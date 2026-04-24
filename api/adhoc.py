import json
import logging
import os
import re
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

import yaml
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from openai import OpenAI
from pydantic import BaseModel

from api.db import query
from api.validation import validate_user_input, validate_generated_sql

load_dotenv()

router = APIRouter()

_client: OpenAI | None = None

def _llm() -> OpenAI:
    global _client
    if _client is None:
        key = os.getenv("OPENROUTER_API_KEY", "")
        if not key or key == "your_openrouter_api_key_here":
            raise HTTPException(status_code=503, detail="OPENROUTER_API_KEY not configured in .env")
        _client = OpenAI(
            api_key=key,
            base_url="https://openrouter.ai/api/v1",
        )
    return _client


MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4.1")

_SCHEMA_PATH = Path(__file__).parent.parent / "database" / "schema.yaml"


def _load_schema() -> str:
    """Read schema.yaml and render it as a compact text block for the LLM prompt."""
    with open(_SCHEMA_PATH, encoding="utf-8") as f:
        doc = yaml.safe_load(f)

    lines: list[str] = []
    lines.append(f"Database: {doc['database']} ({doc['engine']})")
    lines.append(doc.get("description", "").strip())
    lines.append("")

    if doc.get("notes"):
        lines.append("IMPORTANT NOTES:")
        for note in doc["notes"]:
            lines.append(f"  - {note}")
        lines.append("")

    for source_name, source in doc.get("sources", {}).items():
        lines.append(f"{source_name} — {source.get('description', '')}")
        for table_name, table in source.get("tables", {}).items():
            col_parts = []
            for col_name, meta in table.get("columns", {}).items():
                if not isinstance(meta, dict):
                    col_parts.append(col_name)
                    continue
                part = col_name
                if meta.get("pk"):
                    part += " PK"
                if meta.get("fk"):
                    part += f" FK→{meta['fk']}"
                if meta.get("values"):
                    part += f" [{' | '.join(str(v) for v in meta['values'])}]"
                col_parts.append(part)
            lines.append(f"  {table_name}({', '.join(col_parts)})")
            if table.get("description"):
                lines.append(f"    -- {table['description']}")
        lines.append("")

    return "\n".join(lines).strip()


# Load once at import time; uvicorn reload will re-import the module.
SCHEMA = _load_schema()

SQL_SYSTEM = f"""You are a SQLite expert for IISofBC, a non-profit immigration services organisation.
Given a user's plain-English question, produce a valid SQLite SELECT query and, if the result
would suit a chart, a chart specification.

SECURITY RULES — HIGHEST PRIORITY:
You operate on a READ-ONLY analytics system. If the user's request involves any of the
following — in any phrasing, direct or indirect — you MUST refuse and return a blocked response:
  DROP, DELETE, INSERT, UPDATE, ALTER, CREATE, TRUNCATE, ATTACH, PRAGMA, VACUUM,
  or any other operation that modifies, deletes, or restructures data or schema.

This includes natural-language phrasings such as:
  "drop the table", "delete all records", "remove the data", "wipe the database",
  "add a new row", "update the values", "change the schema", "create a table".

When a destructive request is detected, respond with ONLY this JSON and nothing else:
{{
  "blocked": true,
  "reason": "<one of the labels below>"
}}

Use the most specific matching label:
  "DROP (table/index deletion)"
  "DELETE (row deletion)"
  "INSERT (data modification)"
  "UPDATE (data modification)"
  "ALTER (schema modification)"
  "CREATE (schema modification)"
  "TRUNCATE (table wipe)"

QUERY RULES (for legitimate read-only questions):
- Only write SELECT statements.
- Use SQLite functions: strftime('%Y', col) for year, etc.
- Limit results to 200 rows unless the user asks for more.
- Respond with ONLY valid JSON in this exact shape (no markdown fences, no extra text):
{{
  "sql": "<sqlite SELECT statement>",
  "chart": {{
    "type": "bar|line|pie|grouped_bar|area",
    "title": "Human-readable title",
    "x_axis": "column_name",
    "y_axis": "column_name or [list, of, columns]"
  }}
}}
- Set "chart" to null if the result is a single scalar or a plain lookup (e.g. a list of names).

DATABASE SCHEMA:
{SCHEMA}
"""

SUMMARY_SYSTEM = """You are a helpful data analyst for IISofBC, a non-profit immigration services organisation.
Given a SQL query, its results (as JSON), and the original user question, write a concise
2-4 sentence plain-English summary of what the data shows. Focus on the key insight.
Do NOT repeat the SQL. Do NOT use markdown. Just write natural sentences."""


def _extract_json(text: str) -> dict:
    """Strip markdown code fences if the model wrapped the JSON anyway."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


class HistoryTurn(BaseModel):
    query: str
    sql:   str


class AdhocRequest(BaseModel):
    query:   str
    history: list[HistoryTurn] = []


@router.post("/adhoc")
def adhoc_query(req: AdhocRequest):
    user_q = req.query.strip()

    # ── Layer 1: gate-check raw user input (pre-LLM) ───────────────────────
    try:
        validate_user_input(user_q)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    client = _llm()

    # ── Step 1: generate SQL + chart spec ──────────────────────────────────
    # Prepend conversation history so the LLM understands follow-up questions.
    # Each prior turn becomes a user message (the question) followed by an
    # assistant message (the SQL JSON it produced), giving the model full context.
    messages: list[dict] = [{"role": "system", "content": SQL_SYSTEM}]
    for turn in req.history:
        messages.append({"role": "user",      "content": turn.query})
        messages.append({"role": "assistant",  "content": json.dumps({"sql": turn.sql})})
    messages.append({"role": "user", "content": user_q})

    sql_resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0,
        max_tokens=800,
    )
    raw = sql_resp.choices[0].message.content or ""

    try:
        plan = _extract_json(raw)
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(status_code=502, detail=f"LLM returned invalid JSON: {exc}\n\n{raw}")

    # ── LLM self-reported block (destructive request detected by the model) ──
    if plan.get("blocked"):
        reason = plan.get("reason", "restricted operation")
        logger.warning("LLM self-blocked request — reason: %s | query: '%s'", reason, user_q[:120])
        raise HTTPException(
            status_code=400,
            detail=(
                f"This request was blocked because the AI attempted a restricted operation: "
                f"{reason}. Only read-only SELECT queries are permitted on this system."
            ),
        )

    sql       = plan.get("sql", "").strip()
    chart_raw = plan.get("chart")

    # ── Layer 2: validate LLM-generated SQL before execution ───────────────
    # Returns the cleaned SQL (trailing semicolon stripped) on success.
    try:
        sql = validate_generated_sql(sql)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # ── Step 2: execute SQL ─────────────────────────────────────────────────
    try:
        rows = query(sql)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"SQL execution error: {exc}\n\nSQL: {sql}")

    # ── Step 3: summarise ───────────────────────────────────────────────────
    preview = json.dumps(rows[:20], default=str)   # send at most 20 rows to the LLM
    summary_resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SUMMARY_SYSTEM},
            {"role": "user",   "content": (
                f"Question: {user_q}\n\n"
                f"SQL: {sql}\n\n"
                f"Results ({len(rows)} rows, showing first 20): {preview}"
            )},
        ],
        temperature=0.3,
        max_tokens=300,
    )
    summary = (summary_resp.choices[0].message.content or "").strip()

    # ── Build chart spec ────────────────────────────────────────────────────
    chart = None
    if chart_raw and isinstance(chart_raw, dict) and rows:
        chart = {
            "type":    chart_raw.get("type", "bar"),
            "title":   chart_raw.get("title", ""),
            "x_axis":  chart_raw.get("x_axis", ""),
            "y_axis":  chart_raw.get("y_axis", ""),
        }

    return {
        "query":         user_q,
        "generated_sql": sql,
        "summary":       summary,
        "data":          rows,
        "chart":         chart,
        "row_count":     len(rows),
        "generated_at":  datetime.now().isoformat(),
    }

import logging
import os
import re
from pathlib import Path

import yaml
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()

router  = APIRouter()
logger  = logging.getLogger(__name__)
MODEL   = os.getenv("OPENROUTER_MODEL", "openai/gpt-4.1")

_KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"

# ── Load and index the knowledge base at startup ───────────────────────────────

def _load_knowledge() -> list[dict]:
    """Read every YAML file in the knowledge/ directory and return a flat list of documents."""
    docs = []
    for path in sorted(_KNOWLEDGE_DIR.glob("*.yaml")):
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        category = data.get("category", path.stem)
        for doc in data.get("documents", []):
            docs.append({
                "id":       doc.get("id", ""),
                "title":    doc.get("title", ""),
                "category": category,
                "tags":     doc.get("tags", []),
                "content":  doc.get("content", "").strip(),
                "forms":    doc.get("forms", []),
                "portal":   doc.get("portal", ""),
            })
    logger.info("Knowledge base loaded: %d documents from %s", len(docs), _KNOWLEDGE_DIR)
    return docs


KNOWLEDGE: list[dict] = _load_knowledge()


def _score(doc: dict, query: str) -> int:
    """
    Simple keyword overlap score. Checks the query against the document's
    title, tags, and first 300 characters of content (case-insensitive).
    Weights: title match = 3pts, tag match = 2pts, content match = 1pt.
    """
    q_words = set(re.findall(r"\w+", query.lower()))
    score   = 0

    title_words   = set(re.findall(r"\w+", doc["title"].lower()))
    tag_words     = set(w.lower() for tag in doc["tags"] for w in re.findall(r"\w+", tag))
    content_words = set(re.findall(r"\w+", doc["content"][:300].lower()))

    score += len(q_words & title_words)   * 3
    score += len(q_words & tag_words)     * 2
    score += len(q_words & content_words) * 1
    return score


def _retrieve(query: str, top_k: int = 5) -> list[dict]:
    """Return the top_k most relevant documents for the query."""
    scored = [(doc, _score(doc, query)) for doc in KNOWLEDGE]
    scored.sort(key=lambda x: x[1], reverse=True)
    # Always include docs with score > 0; fall back to top_k regardless
    results = [doc for doc, s in scored if s > 0][:top_k]
    if not results:
        results = [doc for doc, _ in scored[:3]]   # at least 3 docs as context
    return results


def _format_context(docs: list[dict]) -> str:
    parts = []
    for doc in docs:
        block = f"[{doc['category']}] {doc['title']}\n{doc['content']}"
        if doc["forms"]:
            block += f"\nForms: {', '.join(doc['forms'])}"
        if doc["portal"]:
            block += f"\nPortal / Location: {doc['portal']}"
        parts.append(block)
    return "\n\n---\n\n".join(parts)


SYSTEM_PROMPT = """You are the ISSofBC Internal Knowledge Assistant — a helpful, friendly, and accurate
assistant for staff at the Immigrant & Integration Society of BC (ISSofBC), a non-profit
settlement services organisation in Vancouver, BC.

Your job is to answer staff questions about:
  - HR policies (leave, benefits, performance, onboarding, code of conduct)
  - Client services (intake, eligibility, confidentiality, referrals)
  - Programs (SSP, ELT, ERP, YIP, SNP, HAP)
  - Finance (expenses, grants, donations, budgets)
  - IT systems (Newtract, BambooHR, Business Central, Microsoft 365, passwords)
  - Workflows and procedures (step-by-step processes)
  - Forms and portal locations

RULES:
- Answer based ONLY on the knowledge base context provided. Do not invent policies or procedures.
- If the answer is in the context, be specific — include form numbers, portal paths, contacts, and deadlines.
- If the question cannot be answered from the context, say so clearly and suggest who to contact
  (e.g. "I don't have that information — please contact hr@issofbc.org for HR questions").
- Be concise but complete. Use bullet points or numbered steps for procedures.
- Always end your answer with the relevant source document title(s) in this format:
  Source: [Document Title 1], [Document Title 2]
- Never fabricate phone numbers, email addresses, URLs, or form numbers.
- Maintain a warm, professional, supportive tone — staff may be asking about sensitive matters.
"""


class ChatMessage(BaseModel):
    role:    str   # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    query:   str
    history: list[ChatMessage] = []


@router.post("/chatbot")
def chatbot(req: ChatRequest):
    query = req.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="query must not be empty")

    key = os.getenv("OPENROUTER_API_KEY", "")
    if not key or key == "your_openrouter_api_key_here":
        raise HTTPException(status_code=503, detail="OPENROUTER_API_KEY not configured in .env")

    client = OpenAI(api_key=key, base_url="https://openrouter.ai/api/v1")

    # Retrieve relevant knowledge docs
    relevant_docs = _retrieve(query)
    context       = _format_context(relevant_docs)

    # Build message list: system → history → injected context + user question
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for msg in req.history:
        messages.append({"role": msg.role, "content": msg.content})

    # Inject retrieved context into the final user turn
    messages.append({
        "role": "user",
        "content": (
            f"KNOWLEDGE BASE CONTEXT (use this to answer):\n\n{context}\n\n"
            f"---\n\nMY QUESTION: {query}"
        ),
    })

    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.2,
        max_tokens=700,
    )

    answer = (resp.choices[0].message.content or "").strip()

    return {
        "answer":  answer,
        "sources": [{"title": d["title"], "category": d["category"]} for d in relevant_docs],
    }

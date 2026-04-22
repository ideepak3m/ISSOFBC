import re
import logging

logger = logging.getLogger(__name__)

# ── Shared operation label table ───────────────────────────────────────────────
# Used by both the input gate (natural-language scan) and the SQL output guard.
# Every blocked response uses the same message built from these labels.

def _blocked_message(label: str) -> str:
    return (
        f"This request was blocked because the AI attempted a restricted operation: "
        f"{label}. Only read-only SELECT queries are permitted on this system."
    )


# ── Layer 1a: direct SQL typed by the user ─────────────────────────────────────
_SQL_START_PATTERNS = [
    r"^\s*SELECT\b",
    r"^\s*WITH\b",
    r"^\s*INSERT\b",
    r"^\s*UPDATE\b",
    r"^\s*DELETE\b",
    r"^\s*DROP\b",
    r"^\s*ALTER\b",
    r"^\s*CREATE\b",
    r"^\s*TRUNCATE\b",
    r"^\s*ATTACH\b",
    r"^\s*DETACH\b",
    r"^\s*PRAGMA\b",
]

# ── Layer 1b: SQL comment injection markers ────────────────────────────────────
_SQL_COMMENT_PATTERNS = [r"--", r"/\*"]

# ── Layer 1c: natural-language destructive intent ──────────────────────────────
# Patterns are specific enough to avoid false positives on legitimate analytics
# questions (e.g. "drop in enrolments", "show deleted records", "update on hiring").
# Each tuple is (regex, operation_label).
_DESTRUCTIVE_INTENT_PATTERNS = [
    # DROP
    (r"\bdrop\s+(the\s+|a\s+|that\s+|this\s+|our\s+)?(table|database|db|index|view|schema|org)\b",
     "DROP (table/index deletion)"),
    # DELETE rows
    (r"\bdelete\s+(all\s+)?(the\s+)?(records?|rows?|data|entries|everything|users?|clients?|beneficiar)",
     "DELETE (row deletion)"),
    (r"\berase\s+(all\s+)?(the\s+)?(records?|rows?|data|entries)\b",
     "DELETE (row deletion)"),
    (r"\bremove\s+all\s+(the\s+)?(records?|rows?|data|entries)\b",
     "DELETE (row deletion)"),
    (r"\bpurge\s+(all\s+)?(the\s+)?(records?|rows?|data|entries|table)\b",
     "DELETE (row deletion)"),
    # TRUNCATE
    (r"\btruncate\s+(the\s+|a\s+|that\s+)?(table|database|db|data)?\b",
     "TRUNCATE (table wipe)"),
    (r"\bwipe\s+(out\s+)?(all\s+)?(the\s+)?(data|table|records?|database|db)\b",
     "TRUNCATE (table wipe)"),
    # INSERT
    (r"\binsert\s+(new\s+|a\s+)?(data|records?|rows?|entries?|values?)\b",
     "INSERT (data modification)"),
    (r"\badd\s+(a\s+|new\s+)?(record|row|entry|data)\s+(to|into)\b",
     "INSERT (data modification)"),
    # UPDATE
    (r"\bupdate\s+(the\s+|all\s+|every\s+)?(records?|rows?|data|table|values?|entries)\b",
     "UPDATE (data modification)"),
    (r"\bmodify\s+(the\s+|all\s+)?(records?|rows?|data|entries)\b",
     "UPDATE (data modification)"),
    # ALTER schema
    (r"\balter\s+(the\s+|a\s+)?(table|database|schema|column|structure)\b",
     "ALTER (schema modification)"),
    (r"\brename\s+(the\s+|a\s+)?(table|column|database)\b",
     "ALTER (schema modification)"),
    # CREATE
    (r"\bcreate\s+(a\s+|new\s+|the\s+)?(table|database|index|view|schema)\b",
     "CREATE (schema modification)"),
]

# ── Layer 1d: prompt injection phrases ────────────────────────────────────────
_PROMPT_INJECTION_PHRASES = [
    "ignore all previous instructions",
    "ignore your instructions",
    "disregard your instructions",
    "forget your instructions",
    "from now on you are",
    "your new instructions are",
    "you are now a",
    "act as a different",
    "override your instructions",
    "pretend you are",
    "you have no restrictions",
    "jailbreak",
]

# ── Layer 2: dangerous keywords in LLM-generated SQL ──────────────────────────
_DANGEROUS_SQL_WITH_LABELS = [
    (r"\bDROP\b",          "DROP (table/index deletion)"),
    (r"\bDELETE\b",        "DELETE (row deletion)"),
    (r"\bINSERT\b",        "INSERT (data modification)"),
    (r"\bUPDATE\b",        "UPDATE (data modification)"),
    (r"\bALTER\b",         "ALTER (schema modification)"),
    (r"\bCREATE\b",        "CREATE (schema modification)"),
    (r"\bTRUNCATE\b",      "TRUNCATE (table wipe)"),
    (r"\bREPLACE\b",       "REPLACE (data modification)"),
    (r"\bUPSERT\b",        "UPSERT (data modification)"),
    (r"\bATTACH\b",        "ATTACH (database file access)"),
    (r"\bDETACH\b",        "DETACH (database operation)"),
    (r"\bPRAGMA\b",        "PRAGMA (runtime configuration)"),
    (r"\bVACUUM\b",        "VACUUM (database maintenance)"),
    (r"\bANALYZE\b",       "ANALYZE (database maintenance)"),
    (r"\bREINDEX\b",       "REINDEX (database maintenance)"),
    (r"\bSELECT\s+INTO\b", "SELECT INTO (table creation)"),
    (r"sqlite_master",     "sqlite_master (schema enumeration)"),
    (r"sqlite_temp_master","sqlite_temp_master (schema enumeration)"),
]


# ── Public validators ──────────────────────────────────────────────────────────

def validate_user_input(query: str) -> None:
    """
    Gate-check the raw user input before the LLM is ever called.
    Raises ValueError with a user-facing message on rejection.

    Checks (in order):
      1a. Input starts with a raw SQL keyword
      1b. SQL comment injection markers (-- or /*)
      1c. Natural-language phrases signalling destructive intent
      1d. Known prompt injection phrases
    """
    if not query or not query.strip():
        raise ValueError("Query must not be empty.")

    stripped = query.strip()

    # 1a — direct SQL
    for pattern in _SQL_START_PATTERNS:
        if re.match(pattern, stripped, re.IGNORECASE):
            logger.warning("Direct SQL input blocked: '%s'", stripped[:120])
            raise ValueError(
                "Please ask your question in plain English. "
                "Direct SQL commands are not accepted."
            )

    # 1b — SQL comment injection
    for pattern in _SQL_COMMENT_PATTERNS:
        if re.search(pattern, stripped):
            logger.warning("SQL comment injection blocked: '%s'", stripped[:120])
            raise ValueError(
                "Your question contains characters that are not permitted. "
                "Please rephrase and try again."
            )

    # 1c — natural-language destructive intent
    for pattern, label in _DESTRUCTIVE_INTENT_PATTERNS:
        if re.search(pattern, stripped, re.IGNORECASE):
            logger.warning("Destructive intent blocked (%s): '%s'", label, stripped[:120])
            raise ValueError(_blocked_message(label))

    # 1d — prompt injection
    lowered = stripped.lower()
    for phrase in _PROMPT_INJECTION_PHRASES:
        if phrase in lowered:
            logger.warning("Prompt injection blocked: '%s'", stripped[:120])
            raise ValueError(
                "Your question contains content that cannot be processed. "
                "Please ask a genuine data question."
            )


def validate_generated_sql(sql: str) -> str:
    """
    Validate the SQL produced by the LLM before it is executed.
    Returns the cleaned SQL (trailing semicolon stripped) on success.
    Raises ValueError with the standardised blocked message on rejection.

    Checks (in order):
      1. Non-empty
      2. Dangerous DDL/DML/SQLite keywords (checked before semicolon so a
         stacked query like "SELECT 1; DROP TABLE x" names the real operation)
      3. Semicolons remaining after trailing-semicolon strip (stacked queries)
      4. First word must be SELECT or WITH
    """
    if not sql or not sql.strip():
        logger.error("LLM returned empty SQL.")
        raise ValueError("The AI did not return a valid SQL query. Please try rephrasing.")

    # Strip trailing semicolon — LLMs routinely append one to valid single statements.
    stripped = sql.strip().rstrip(";").strip()

    for pattern, label in _DANGEROUS_SQL_WITH_LABELS:
        if re.search(pattern, stripped, re.IGNORECASE):
            logger.error("Blocked — %s in LLM SQL: '%s'", label, stripped[:120])
            raise ValueError(_blocked_message(label))

    if ";" in stripped:
        logger.error("Stacked query (semicolon) in LLM SQL: '%s'", stripped[:120])
        raise ValueError(_blocked_message("stacked query (multiple statements via semicolon)"))

    first_word = stripped.split()[0].upper() if stripped else ""
    if first_word not in ("SELECT", "WITH"):
        logger.error("LLM returned non-SELECT SQL (%s): '%s'", first_word, stripped[:120])
        raise ValueError(_blocked_message(f"{first_word} statement (non-SELECT query)"))

    return stripped

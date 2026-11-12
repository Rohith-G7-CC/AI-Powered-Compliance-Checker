import json
from src.llm.llm_router import chat_completion_json


# =====================================================
# SYSTEM PROMPT
# =====================================================
SYSTEM_PROMPT = """
You are a senior regulatory compliance expert.

Your task is to analyze a contract's extracted clauses and determine
which regulatory compliance clauses are MISSING or INSUFFICIENT.

You must reason based on:
- Clause text
- Clause type
- Risk severity and explanation
- Regulatory expectations (GDPR, HIPAA)

Rules:
- If a topic is explicitly and clearly covered, DO NOT mark it missing
- If coverage is vague, weak, or incomplete, mark it as missing
- Only report genuinely required missing clauses

Return ONLY valid JSON.
"""


# =====================================================
# USER PROMPT TEMPLATE
# =====================================================
USER_PROMPT = """
REGULATORY EXPECTATIONS:
{regulations}

EXTRACTED CONTRACT CLAUSES (with risk analysis):
{clauses}

TASK:
Identify which regulatory compliance clauses are missing or insufficient.

Return a JSON array in the following format ONLY:

[
  {{
    "required_clause": "<Clause Name>",
    "regulation": "<GDPR or HIPAA>",
    "reason": "<Why this clause is missing or insufficient>"
  }}
]

Do NOT include clauses that are already sufficiently covered.
Do NOT add explanations outside JSON.
"""


# =====================================================
# CORE FUNCTION
# =====================================================
def detect_missing_clauses_from_contract(assessed_clauses, regulations):
    compact_clauses = []
    for clause in assessed_clauses:
        compact_clauses.append({
            "clause_id": clause.get("clause_id"),
            "clause_heading": clause.get("clause_heading"),
            "clause_type": clause.get("clause_type"),
            "clause_text": clause.get("clause_text"),
            "risk": clause.get("risk", {})
        })

    prompt = USER_PROMPT.format(
        regulations=json.dumps(regulations, indent=2),
        clauses=json.dumps(compact_clauses, indent=2)
    )

    response = chat_completion_json(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=prompt,
        temperature=0.0
    )

    # If router wrapped list → extract safely
    if isinstance(response, dict) and "data" in response:
        return response["data"]

    # If LLM directly returned list
    if isinstance(response, list):
        return response

    # Fallback safety
    try:
        response = chat_completion_json(...)
    except Exception:
        return []


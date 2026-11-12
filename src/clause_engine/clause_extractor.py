# src/clause_engine/clause_extractor.py

import json
from dotenv import load_dotenv

from src.llm.llm_router import chat_completion_json

load_dotenv()

# =====================================================
# PROMPTS
# =====================================================
SYSTEM_PROMPT = """
You are a senior legal analyst AI. 
Your task is to extract ALL meaningful legal clauses from a contract.
Output MUST be a valid JSON array.

Each clause object must contain:
- clause_id (string)
- clause_heading (string or null)
- clause_text (full clause text)
- clause_type (categorize into: Confidentiality, Termination, Indemnity, Liability, Payment, Data Protection, IP, SLA, Assignment, Governing Law, Dispute Resolution, Other)
- rationale (1 sentence why this classification is correct)
"""

USER_PROMPT = """
Extract all clauses from the following contract text:

<CONTRACT_TEXT>
{contract}
</CONTRACT_TEXT>

Return ONLY a JSON array of objects with the exact schema described.
DO NOT add commentary or text outside JSON.
"""

# =====================================================
# CORE FUNCTION (REFactored)
# =====================================================
def extract_clauses(contract_text: str):
    prompt = USER_PROMPT.format(contract=contract_text)

    response = chat_completion_json(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=prompt,
        temperature=0.0
    )

    clauses = response["data"]
    llm_used = response["_llm_used"]
    

    # Ensure clause_id + audit metadata
    for idx, clause in enumerate(clauses, start=1):
        clause.setdefault("clause_id", str(idx))
        clause["_llm_used"] = llm_used

    return clauses


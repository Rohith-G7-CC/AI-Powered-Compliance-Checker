# src/contract_modification/amendment_generator.py

from dotenv import load_dotenv
from src.llm.llm_router import chat_completion

load_dotenv()

# =====================================================
# PROMPTS
# =====================================================
SYSTEM_PROMPT_AMEND = """
You are a senior contract and compliance lawyer.

Rewrite ONLY the clause provided to resolve the identified HIGH RISK.
Do NOT add new obligations beyond what is necessary to fix the risk.
Do NOT introduce new clauses, headings, or definitions.
Preserve the original structure, numbering, and legal tone.

Return ONLY the rewritten clause text.
"""



SYSTEM_PROMPT_NEW = """
You are a senior compliance lawyer.
Draft a legally sound contract clause.
"""

# =====================================================
# AMEND EXISTING CLAUSE (REFactored)
# =====================================================
def generate_amendment(original_clause, reason, regulation=None):
    user_prompt = f"""
Original Clause:
{original_clause}

Issue:
{reason}

Regulatory Context:
{regulation if regulation else "General Compliance"}
"""

    result = chat_completion(
        system_prompt=SYSTEM_PROMPT_AMEND,
        user_prompt=user_prompt,
        temperature=0.0
    )

    # Plain text expected (do NOT force JSON here)
    amended_clause = result["content"].strip()

    return amended_clause


# =====================================================
# GENERATE NEW COMPLIANCE CLAUSE
# =====================================================
def generate_compliance_clause(clause_name, regulation):
    user_prompt = f"""
Draft a '{clause_name}' clause required under {regulation}.
The clause must be clear, enforceable, and enterprise-ready.
"""

    result = chat_completion(
        system_prompt=SYSTEM_PROMPT_NEW,
        user_prompt=user_prompt,
        temperature=0.0
    )

    return result["content"].strip()

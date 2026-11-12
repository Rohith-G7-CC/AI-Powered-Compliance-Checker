# src/risk_engine/risk_engine.py

import json
from dotenv import load_dotenv

from src.llm.llm_router import chat_completion_json

load_dotenv()

# =====================================================
# PROMPTS (UNCHANGED)
# =====================================================
SYSTEM_PROMPT = """
You are a Senior Regulatory Compliance Officer specializing in contract law.
Your task is to evaluate LEGAL RISK for each contract clause.

You MUST output ONLY valid JSON in the following structure:

{
  "risk_level": "low" | "medium" | "high",
  "risk_score": number (0-100),
  "risk_factors": [ list of key concerns ],
  "missing_controls": [ list of missing protections ],
  "regulation_violations": [ list of violated or implicated regulations ],
  "explanation": "short summary written for compliance analysts"
}

Rules:
- Base risk on the meaning of the clause, not keywords.
- Evaluate confidentiality, liability, indemnity, data protection, IP, and regulatory exposure.
- Consider GDPR, HIPAA, SOC2, ISO27001, and general contract law.
- Be strict. If uncertain, classify as medium risk.
"""

USER_PROMPT_TEMPLATE = """
Evaluate the legal and regulatory risk of the following clause:

<CLAUSE_TEXT>
{clause}
</CLAUSE_TEXT>

Return ONLY the JSON object described in the system prompt.
"""

# =====================================================
# CORE LLM CALL (REFactored)
# =====================================================
def assess_clause_with_llm(clause_text: str):
    prompt = USER_PROMPT_TEMPLATE.format(clause=clause_text)

    risk = chat_completion_json(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=prompt,
        temperature=0.0
    )

    # Standardize on "severity" for downstream pipeline
    if isinstance(risk, dict):
        risk_level = risk.get("risk_level")

        if risk_level in ["low", "medium", "high"]:
            risk["severity"] = risk_level
        else:
            risk["severity"] = "medium"  # safe fallback

        # 🔴 ADD THIS LINE (CRITICAL)
        risk["risk_reason"] = risk.get("explanation", "").strip()

    return risk


# =====================================================
# BATCH RISK ASSESSMENT (UNCHANGED API)
# =====================================================
def assess_clauses(clauses):
    """
    clauses → list of clause dicts from clause_extractor
    Attaches LLM risk output to each clause
    """
    assessed = []

    for c in clauses:
        text = c.get("clause_text", "")
        clause_id = c.get("clause_id")

        print(f"\nEvaluating risk for clause: {clause_id} ...")

        risk = assess_clause_with_llm(text)

        # Attach risk + audit metadata
        c["risk"] = risk
        assessed.append(c)

    return assessed


# =====================================================
# STANDALONE TEST (OPTIONAL)
# =====================================================
if __name__ == "__main__":
    INPUT_FILE = "extracted_clauses.json"
    OUTPUT_FILE = "clauses_with_llm_risk.json"

    print(f"\nLoading clauses from: {INPUT_FILE}")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        clauses_list = json.load(f)

    print("\nRunning LLM-based risk assessment...")
    assessed = assess_clauses(clauses_list)

    print(f"\nSaving risk-evaluated clauses to: {OUTPUT_FILE}")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(assessed, f, indent=2, ensure_ascii=False)

    print("\nRisk analysis saved successfully.")

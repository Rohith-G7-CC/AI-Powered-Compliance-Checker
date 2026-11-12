from typing import List, Dict


# ---------------------------------------------------------
# Helper: Normalize clause types for comparison
# ---------------------------------------------------------
def _normalize(text: str) -> str:
    return text.lower().strip()


# ---------------------------------------------------------
# Core Compliance Check Function
# ---------------------------------------------------------
def check_compliance(
    clauses: List[Dict],
    regulations: Dict,
    live_gdpr_updates: Dict = None,
    live_hipaa_updates: Dict = None
):

    compliance_issues = []

    # Extract clause types and texts
    clause_types = {_normalize(c.get("clause_type", "")) for c in clauses}
    clause_texts = [_normalize(c.get("clause_text", "")) for c in clauses]

    # -----------------------------------------------------
    # 1. Baseline Regulatory Compliance Check
    # -----------------------------------------------------
    for regulation_name, rules in regulations.items():
        required_clauses = rules.get("required_clauses", [])

        for required in required_clauses:
            if _normalize(required) not in clause_types:
                compliance_issues.append({
                    "regulation": regulation_name,
                    "issue_type": "missing_clause",
                    "required_clause": required,
                    "severity": "high",
                    "source": "baseline_regulation"
                })

    # -----------------------------------------------------
    # 2. Weak / Risky Clause Detection (from Milestone 2)
    # -----------------------------------------------------
    for c in clauses:
        risk = c.get("risk", {})
        risk_level = risk.get("risk_level")

        if risk_level == "high":
            compliance_issues.append({
                "regulation": "General",
                "issue_type": "high_risk_clause",
                "clause_id": c.get("clause_id"),
                "clause_type": c.get("clause_type"),
                "severity": "high",
                "explanation": risk.get("explanation"),
                "source": "risk_engine"
            })

    # -----------------------------------------------------
    # 3. Live GDPR Update Awareness
    # -----------------------------------------------------
    if live_gdpr_updates and live_gdpr_updates.get("has_new_updates"):
        for entry in live_gdpr_updates.get("new_entries", []):
            compliance_issues.append({
                "regulation": "GDPR",
                "issue_type": "regulatory_update",
                "severity": "medium",
                "title": entry.get("title"),
                "summary": entry.get("summary"),
                "source": "gdpr_live_tracker"
            })

    # -----------------------------------------------------
    # 4. Live HIPAA Update Awareness
    # -----------------------------------------------------
    if live_hipaa_updates and live_hipaa_updates.get("has_new_updates"):
        for entry in live_hipaa_updates.get("new_entries", []):
            compliance_issues.append({
                "regulation": "HIPAA",
                "issue_type": "regulatory_update",
                "severity": "medium",
                "title": entry.get("title"),
                "summary": entry.get("summary"),
                "source": "hipaa_live_tracker"
            })

    # -----------------------------------------------------
    # Final Structured Output
    # -----------------------------------------------------
    compliance_report = {
        "total_clauses_analyzed": len(clauses),
        "total_issues_detected": len(compliance_issues),
        "issues": compliance_issues
    }

    return compliance_report


# ---------------------------------------------------------
# Standalone Test Execution
# ---------------------------------------------------------
if __name__ == "__main__":
    print("This module is intended to be used inside Milestone 3 pipeline.")

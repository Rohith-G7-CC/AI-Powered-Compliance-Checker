# src/contract_modification/gap_analyzer.py

def identify_high_risk_clauses(clauses):
    high = []

    for c in clauses:
        risk = c.get("risk", {})

        severity = (
            risk.get("severity")      # Version-2 style
            or risk.get("risk_level") # Version-1 / actual engine output
            or ""
        )

        if isinstance(severity, str) and severity.lower() in ("high", "critical"):
            high.append(c)

    return high


def extract_missing_clauses(compliance_report):
    missing = []

    for issue in compliance_report.get("issues", []):
        if issue.get("issue_type") == "missing_clause":
            missing.append({
                "regulation": issue.get("regulation"),
                "required_clause": issue.get("required_clause")
            })

    return missing

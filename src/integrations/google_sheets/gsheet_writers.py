# src/integrations/google_sheets/gsheet_writers.py

from datetime import datetime
from src.integrations.google_sheets.gsheet_client import get_spreadsheet


# =========================
# Contracts Overview Writer
# =========================
def write_contract_overview(data: dict):
    """
    Expected keys in data:
    - contract_id
    - contract_name
    - client_name
    - jurisdiction
    - domain
    - regulations_checked (comma-separated string or list)
    - overall_status (COMPLIANT / NON-COMPLIANT)
    """

    spreadsheet = get_spreadsheet()
    worksheet = spreadsheet.worksheet("Contracts_Overview")

    regulations = data.get("regulations_checked")
    if isinstance(regulations, list):
        regulations = ", ".join(regulations)

    row = [
        data.get("contract_id"),
        data.get("contract_name"),
        data.get("client_name"),
        data.get("jurisdiction"),
        data.get("domain"),
        regulations,
        data.get("overall_status"),
        datetime.utcnow().isoformat()
    ]

    worksheet.append_row(row)


# =========================
# Compliance Issues Writer
# =========================
def write_compliance_issues(contract_id: str, issues: list):
    """
    Writes each compliance issue as a separate row.

    issues: list of issue dictionaries from compliance report
    """

    if not issues:
        return

    spreadsheet = get_spreadsheet()
    worksheet = spreadsheet.worksheet("Compliance_Issues")

    rows = []

    for issue in issues:
        issue_type = issue.get("issue_type")

        # Reference depends on issue type
        if issue_type == "missing_clause":
            reference = issue.get("required_clause")
        elif issue_type == "high_risk_clause":
            reference = issue.get("clause_id")
        else:
            reference = "N/A"

        row = [
            contract_id,
            issue.get("regulation"),
            issue_type,
            reference,
            issue.get("severity"),
            issue.get("explanation", ""),
            issue.get("source")
        ]

        rows.append(row)

    worksheet.append_rows(rows)


# =========================
# Actions Audit Writer
# =========================
def write_action_audit(
    action_type: str,
    contract_id: str,
    target: str,
    status: str,
    triggered_by: str = "System"
):
    """
    Logs actions performed by the system.

    action_type: e.g. 'Clause Amended', 'Clause Inserted', 'Slack Alert Sent'
    target: clause_id, regulation, or '-' if not applicable
    status: Completed / Failed / Pending
    """

    spreadsheet = get_spreadsheet()
    worksheet = spreadsheet.worksheet("Actions_Audit")

    row = [
        datetime.utcnow().isoformat(),
        contract_id,
        action_type,
        target,
        status,
        triggered_by
    ]

    worksheet.append_row(row)
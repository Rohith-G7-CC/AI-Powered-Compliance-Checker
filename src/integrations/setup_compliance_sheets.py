# src/integrations/setup_compliance_sheets.py

import gspread
from oauth2client.service_account import ServiceAccountCredentials


# =========================
# CONFIGURATION
# =========================
SERVICE_ACCOUNT_FILE = "credentials/service_account.json"
SPREADSHEET_NAME = "AI_Contract_Compliance_Dashboard"

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]


# =========================
# AUTH
# =========================
def get_client():
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        SERVICE_ACCOUNT_FILE, SCOPE
    )
    return gspread.authorize(creds)


# =========================
# UTILITY
# =========================
def create_sheet_if_not_exists(spreadsheet, title, headers):
    try:
        worksheet = spreadsheet.worksheet(title)
        print(f"✔ Sheet exists: {title}")
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title=title,
            rows="1000",
            cols=str(len(headers))
        )
        worksheet.append_row(headers)
        print(f"🆕 Created sheet: {title}")
    return worksheet


# =========================
# MAIN
# =========================
def initialize_compliance_sheets():
    client = get_client()

    try:
        spreadsheet = client.open(SPREADSHEET_NAME)
        print("✔ Spreadsheet exists")
    except gspread.exceptions.SpreadsheetNotFound:
        spreadsheet = client.create(SPREADSHEET_NAME)
        print("🆕 Created spreadsheet")

    # Sheet 1: Contracts Overview
    create_sheet_if_not_exists(
        spreadsheet,
        "Contracts_Overview",
        [
            "contract_id",
            "contract_name",
            "client_name",
            "jurisdiction",
            "domain",
            "regulations_checked",
            "overall_status",
            "last_run_timestamp"
        ]
    )

    # Sheet 2: Compliance Issues
    create_sheet_if_not_exists(
        spreadsheet,
        "Compliance_Issues",
        [
            "contract_id",
            "regulation",
            "issue_type",
            "reference",
            "severity",
            "explanation",
            "source"
        ]
    )

    # Sheet 3: Actions Audit
    create_sheet_if_not_exists(
        spreadsheet,
        "Actions_Audit",
        [
            "timestamp",
            "contract_id",
            "action_type",
            "target",
            "status",
            "triggered_by"
        ]
    )

    print("\n✅ Google Sheets structure initialized successfully")


if __name__ == "__main__":
    initialize_compliance_sheets()

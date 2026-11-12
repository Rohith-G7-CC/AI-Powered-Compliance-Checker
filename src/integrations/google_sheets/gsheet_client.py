# src/integrations/google_sheets/gsheet_client.py

import gspread
from oauth2client.service_account import ServiceAccountCredentials

# =========================
# CONFIG
# =========================
SERVICE_ACCOUNT_FILE = "credentials/service_account.json"
SPREADSHEET_NAME = "AI_Contract_Compliance_Dashboard"

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]


# =========================
# CLIENT FACTORY
# =========================
def get_spreadsheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        SERVICE_ACCOUNT_FILE, SCOPE
    )
    client = gspread.authorize(creds)
    return client.open(SPREADSHEET_NAME)

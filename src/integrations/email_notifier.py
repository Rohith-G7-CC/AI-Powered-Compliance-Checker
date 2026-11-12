# src/integrations/email_notifier.py

import smtplib
from email.message import EmailMessage
from datetime import datetime
import ssl

import os
from dotenv import load_dotenv
load_dotenv()

# ==============================
# SMTP CONFIG (ENV SAFE)
# ==============================
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

SMTP_USERNAME = os.getenv("SENDER_EMAIL")
SMTP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")

FROM_EMAIL = os.getenv("SENDER_EMAIL")
TO_EMAILS = os.getenv("SENDER_EMAIL")


# ==============================
# EMAIL SENDER (LOW LEVEL)
# ==============================
def send_email(subject: str, body: str):
    msg = EmailMessage()
    msg["From"] = FROM_EMAIL
    msg["To"] = TO_EMAILS
    msg["Subject"] = subject
    msg.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls(context=context)
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)


def format_summary_email(pipeline_result: dict) -> str:
    return f"""
Hello,

The compliance analysis for the contract has been completed.

Contract Name: {pipeline_result.get("contract_name")}
Contract ID: {pipeline_result.get("contract_id")}

Summary:
• Total Clauses Extracted: {pipeline_result.get("total_clauses_extracted")}
• Total Risks Detected: {pipeline_result.get("total_risks_detected")}
• Amendments Applied: {"YES" if pipeline_result.get("amendments_done") else "NO"}

Severity Level: {pipeline_result.get("severity")}
Regulations Checked: {pipeline_result.get("regulation")}

Timestamp: {pipeline_result.get("timestamp")}
Audit ID: {pipeline_result.get("audit_id")}

This is an automated compliance notification.
"""



# ==============================
# DECISION ENGINE (CORE LOGIC)
# ==============================
def notify_once(pipeline_result: dict):
    timestamp = datetime.utcnow().isoformat() + "Z"

    # 1. COMPLIANCE ALERT (HIGH / CRITICAL)
    if pipeline_result.get("severity") in ["HIGH", "CRITICAL"]:
        send_email(
            subject=f"[Compliance Alert] {pipeline_result.get('severity')} Risk – {pipeline_result.get('contract_name')}",
            body=format_summary_email(pipeline_result)
        )
        return  # 🟡 STOP HERE


    # 2. CONTRACT UPDATED (AUTO-AMENDMENT)
    if pipeline_result.get("contract_updated") is True:
        send_email(
            subject=f"[Contract Updated] Compliance Changes Applied – {pipeline_result.get('contract_name')}",
            body=format_summary_email(pipeline_result)
        )
        return  # 🟢 STOP HERE


    # 5️⃣ NOTHING TO SEND
    return


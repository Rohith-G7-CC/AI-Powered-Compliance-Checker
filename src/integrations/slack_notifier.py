# src/integrations/slack_notifier.py

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# -------------------------------------------------------------------
# Supported Slack Event Types
# -------------------------------------------------------------------
ALLOWED_EVENTS = {
    "COMPLIANCE_ALERT",
    "HIGH_RISK_CLAUSE",
    "REGULATORY_UPDATE",
    "AUTO_CONTRACT_UPDATE",
    "PIPELINE_FAILURE",
    "COMPLIANCE_SUMMARY"
}

ALLOWED_SEVERITIES = {"CRITICAL", "HIGH", "INFO"}

# -------------------------------------------------------------------
# Core Slack Sender
# -------------------------------------------------------------------
def send_slack_message(payload: dict) -> None:
    if not SLACK_WEBHOOK_URL:
        print("❌ Slack webhook URL not configured")
        return

    try:
        response = requests.post(
            SLACK_WEBHOOK_URL,
            json=payload,
            timeout=10
        )

        if response.status_code != 200:
            print("❌ Slack notification failed:", response.text)
        else:
            print("✅ Slack notification sent")

    except Exception as e:
        print("❌ Slack notification exception:", str(e))


# -------------------------------------------------------------------
# Message Formatter (SINGLE SOURCE OF TRUTH)
# -------------------------------------------------------------------
def format_slack_message(event: dict) -> dict:
    """
    Converts a structured event into a clean Slack message.
    Slack is for humans → keep it readable.
    """

    header = f"*{event['event_type']}* | Severity: *{event['severity']}*"
    lines = [header]

    if event.get("summary"):
        lines.append(f"*Summary:* {event['summary']}")

    contract = event.get("contract")
    if contract:
        lines.append(f"*Contract:* {contract.get('name', 'N/A')}")
        if contract.get("jurisdiction"):
            lines.append(f"*Jurisdiction:* {contract['jurisdiction']}")

    details = event.get("details", {})
    for key, value in details.items():
        lines.append(f"*{key.replace('_', ' ').title()}:* {value}")

    if event.get("action_required"):
        lines.append(f"*Action Required:* {event['action_required']}")

    if event.get("source_module"):
        lines.append(f"_Source: {event['source_module']}_")

    return {
        "text": "\n".join(lines)
    }


# -------------------------------------------------------------------
# Public Notifier (USED BY ALL MODULES)
# -------------------------------------------------------------------
def notify_slack(event: dict) -> None:
    """
    Generic Slack notifier.
    All modules should send events using this function.
    """

    # Validate event type
    if event.get("event_type") not in ALLOWED_EVENTS:
        print("⚠️ Invalid Slack event type:", event.get("event_type"))
        return

    # Normalize + validate severity
    severity = event.get("severity", "").upper()
    if severity not in ALLOWED_SEVERITIES:
        return  # Ignore LOW / MEDIUM noise

    event["severity"] = severity

    # Add timestamp if missing
    event.setdefault(
        "timestamp",
        datetime.utcnow().isoformat()
    )

    payload = format_slack_message(event)
    send_slack_message(payload)


# -------------------------------------------------------------------
# Convenience Wrapper (OPTIONAL – for Risk Engine)
# -------------------------------------------------------------------
def notify_if_high_risk(contract_name: str, compliance_report: dict) -> None:
    high_risk_issues = [
        issue for issue in compliance_report.get("issues", [])
        if issue.get("severity", "").lower() == "high"
    ]

    if not high_risk_issues:
        return

    event = {
        "event_type": "COMPLIANCE_ALERT",
        "severity": "HIGH",
        "contract": {
            "name": contract_name
        },
        "summary": "High-risk compliance issues detected",
        "details": {
            "high_risk_issue_count": len(high_risk_issues)
        },
        "action_required": "Immediate legal review required",
        "source_module": "Risk Analysis Engine"
    }

    notify_slack(event)

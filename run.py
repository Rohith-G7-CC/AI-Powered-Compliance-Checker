# run.py

import os
import json
import argparse
from dotenv import load_dotenv
from datetime import datetime

# --------------------------------------------------
# Utils
# --------------------------------------------------
from src.utils.pdf_extract import extract_pdf
from src.utils.cleaner import normalize_text, chunk_text
from src.utils.annotate_csv import convert_m2_json_to_csv

from src.clause_engine.clause_extractor import extract_clauses
from src.risk_engine.risk_engine import assess_clauses

from src.regulatory.gdpr_live_tracker import detect_gdpr_changes
from src.regulatory.hipaa_live_tracker import detect_hipaa_changes

from src.contract_modification.gap_analyzer import identify_high_risk_clauses
from src.contract_modification.amendment_generator import generate_amendment
from src.utils.pdf_writer import write_contract_pdf

from src.integrations.email_notifier import notify_once
from src.integrations.slack_notifier import notify_slack
from src.integrations.google_sheets.gsheet_writers import (
    write_contract_overview,
    write_compliance_issues,
    write_action_audit
)

# --------------------------------------------------
# Environment Setup
# --------------------------------------------------
load_dotenv()

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./results")
os.makedirs(OUTPUT_DIR, exist_ok=True)

MAX_LENGTH = 45000  # Chunk threshold


# ==================================================
# MAIN PIPELINE
# ==================================================

def safe_notify_slack(payload):
    try:
        notify_slack(payload)
    except Exception as e:
        print("⚠️ Slack notification failed:", e)


import re

def apply_amendments_to_original_text(original_text, amendments):
    updated_text = original_text

    for clause_id, amended_clause in amendments.items():
        pattern = rf"(^|\n){re.escape(clause_id)}\.?\s+.*?(?=\n\d+(?:\.\d+)*\.?\s|\Z)"

        updated_text, count = re.subn(
            pattern,
            f"\n{amended_clause.strip()}",
            updated_text,
            flags=re.DOTALL
        )

        if count == 0:
            print(f"⚠️ Clause {clause_id} NOT replaced (pattern mismatch)")
        else:
            print(f"✅ Clause {clause_id} replaced successfully")

    return updated_text


def run_pipeline(pdf_path, progress_callback=None):
    try:
        print("\n==============================")
        print(" AI-POWERED CONTRACT COMPLIANCE PIPELINE ")
        print("==============================\n")

        def update_progress(percent, message):
            if progress_callback:
                progress_callback(percent, message)

        # --------------------------------------------------
        # STEP 1: PDF → TEXT
        # --------------------------------------------------
        print("Step 1: Extracting text from PDF")
        update_progress(10, "Extracting text from PDF")
        raw_text = extract_pdf(pdf_path)

        # --------------------------------------------------
        # STEP 2: CLEAN TEXT
        # --------------------------------------------------
        print("Step 2: Normalizing contract text")
        clean_text = normalize_text(raw_text)
        original_header = clean_text.split("\n\n")[0].strip()

        # --------------------------------------------------
        # STEP 3: CLAUSE EXTRACTION
        # --------------------------------------------------
        print("Step 3: Extracting clauses")
        if len(clean_text) > MAX_LENGTH:
            print("Large contract detected → chunking enabled")
            chunks = chunk_text(clean_text, max_tokens=1500)
            clauses = []

            for idx, chunk in enumerate(chunks):
                print(f" - Processing chunk {idx + 1}/{len(chunks)}")
                extracted = extract_clauses(chunk)
                for c in extracted:
                    c["clause_id"] = f"chunk{idx}_{c.get('clause_id', 'c')}"
                clauses.extend(extracted)
        else:
            update_progress(30, "Extracting Clauses")
            clauses = extract_clauses(clean_text)

        print(f"Total clauses extracted: {len(clauses)}")

        # --------------------------------------------------
        # STEP 4: RISK ANALYSIS
        # --------------------------------------------------
        print("Step 4: Performing LLM-based risk assessment")
        update_progress(50, "Analysing Risks")
        assessed_clauses = assess_clauses(clauses)

        base_name = os.path.basename(pdf_path).replace(".pdf", "")
        m2_json = os.path.join(OUTPUT_DIR, f"{base_name}_m2_output.json")

        with open(m2_json, "w", encoding="utf-8") as f:
            json.dump(assessed_clauses, f, indent=2, ensure_ascii=False)

        print("Milestone 2 JSON saved:", m2_json)

        m2_csv = os.path.join(OUTPUT_DIR, f"{base_name}_m2_annotations.csv")
        convert_m2_json_to_csv(m2_json, m2_csv)

        # --------------------------------------------------
        # STEP 5: LIVE REGULATORY TRACKING
        # --------------------------------------------------
        print("\nStep 5: Fetching live regulatory updates")
        gdpr_updates = detect_gdpr_changes()
        hipaa_updates = detect_hipaa_changes()

        print("GDPR:", gdpr_updates.get("message"))
        print("HIPAA:", hipaa_updates.get("message"))

        if gdpr_updates.get("changed") and gdpr_updates.get("message"):
            safe_notify_slack({
                "event_type": "REGULATORY_UPDATE",
                "severity": "INFO",
                "summary": "GDPR regulatory update detected",
                "details": {
                    "message": gdpr_updates.get("message")
                },
                "action_required": "Review impacted contracts",
                "source_module": "GDPR Live Tracker"
            })

        if hipaa_updates.get("changed") and hipaa_updates.get("message"):
            safe_notify_slack({
                "event_type": "REGULATORY_UPDATE",
                "severity": "INFO",
                "summary": "HIPAA regulatory update detected",
                "details": {
                    "message": hipaa_updates.get("message")
                },
                "action_required": "Review impacted contracts",
                "source_module": "HIPAA Live Tracker"
            })


        # --------------------------------------------------
        # STEP 6: COMPLIANCE GAP ANALYSIS
        # --------------------------------------------------
        print("\nStep 6: Performing compliance gap analysis")

        issues = []

        for clause in assessed_clauses:
            risk = clause.get("risk", {})
            
            severity = risk.get("severity") or risk.get("risk_level")
            if isinstance(severity, str) and severity.lower() in ["high", "critical"]:
                issues.append({
                    "regulation": risk.get("regulation", "General"),
                    "issue_type": "high_risk_clause",
                    "clause_id": clause["clause_id"],
                    "clause_type": risk.get("clause_type", "Unknown"),
                    "severity": severity,
                    "explanation": risk.get("explanation", ""),
                    "source": "risk_engine"
                })

        compliance_report = {
            "total_clauses_analyzed": len(assessed_clauses),
            "total_issues_detected": len(issues),
            "issues": issues
        }

        print("Compliance issues detected:", compliance_report["total_issues_detected"])

        contract_id = base_name.upper()

        overall_status = (
            "NON-COMPLIANT"
            if any(i["severity"] in ["high", "critical"] for i in compliance_report["issues"])
            else "COMPLIANT"
        )

        contract_metadata = {
            "contract_id": contract_id,
            "contract_name": base_name,
            "client_name": "UNKNOWN",
            "jurisdiction": "UNKNOWN",
            "domain": "GENERAL",
            "regulations_checked": list(
                set(i["regulation"] for i in compliance_report["issues"])
            ) or ["General"],
            "overall_status": overall_status
        }


        if any(i["severity"] in ["high", "critical"] for i in compliance_report["issues"]):
            safe_notify_slack({
                "event_type": "COMPLIANCE_ALERT",
                "severity": "HIGH",
                "contract": {
                    "name": base_name,
                    "jurisdiction": contract_metadata["jurisdiction"]
                },
                "summary": "High-risk compliance issues detected",
                "details": {
                    "high_risk_issue_count": sum(
                        1 for i in compliance_report["issues"]
                        if i["severity"].lower() == "high"
                    )
                },
                "action_required": "Immediate legal review required",
                "source_module": "Compliance Gap Analyzer"
            })


        # ---- Google Sheets: Contracts Overview ----
        write_contract_overview(contract_metadata)

        # ---- Google Sheets: Compliance Issues ----
        write_compliance_issues(
            contract_id=contract_id,
            issues=compliance_report["issues"]
        )

        # ---- Google Sheets: Audit Log ----
        write_action_audit(
            action_type="Compliance Check Completed",
            contract_id=contract_id,
            target="-",
            status="Success",
            triggered_by="Risk Engine"
        )


        # --------------------------------------------------
        # STEP 7: AMEND HIGH-RISK CLAUSES
        # --------------------------------------------------
        inserted_clauses = []
        print("\nStep 7: Amending high-risk clauses")
        amendments = {}

        update_progress(70, "Suggesting Improvements")
        high_risk = identify_high_risk_clauses(assessed_clauses)

        if not high_risk:
            print("No high-risk clauses found — no amendments will be generated. (Severity check is case-insensitive)")

        for clause in high_risk:
            risk = clause.get("risk", {})

            # HARD GATE — rewrite ONLY true HIGH risk
            if risk.get("severity") != "high":
                continue

            risk_reason = risk.get("risk_reason") or risk.get("explanation")
            if not risk_reason:
                print(f"⚠️ Skipping clause {clause['clause_id']} — no clear risk reason")
                continue

            cid = clause["clause_id"]
            print(f" - Amending HIGH-RISK clause {cid}")

            amended_body = generate_amendment(
                original_clause=clause["clause_text"],
                reason=risk_reason,
                regulation=risk.get("regulation_violations", "General Compliance")
            )

            # PRESERVE CLAUSE HEADING (number + title)
            heading = clause["clause_text"].split("\n", 1)[0].strip()

            amendments[cid] = f"{heading}\n{amended_body}"


            # Debug: log amendment preview and whether it differs from original
            try:
                amended_preview = amendments[cid].strip().replace('\n', ' ')[:200]
                original_preview = clause["clause_text"].strip().replace('\n', ' ')[:200]
                if amended_preview == original_preview:
                    print(f"Note: Amendment for clause {cid} appears identical to original (first 200 chars).")
                else:
                    print(f"Amendment for clause {cid} created (preview): {amended_preview}")
            except Exception as e:
                print("⚠️ Could not preview amendment:", e)

            write_action_audit(
                action_type="Clause Amended",
                contract_id=contract_id,
                target=cid,
                status="Completed",
                triggered_by="Amendment Engine"
            )

        if not amendments:
            print("Warning: No amendments were created. The rebuilt contract will be identical to the original unless clauses were inserted.")


        update_progress(90, "Rewriting Contract")
        # --------------------------------------------------
        # APPLY AMENDMENTS TO ORIGINAL CONTRACT TEXT
        # --------------------------------------------------
        updated_contract = apply_amendments_to_original_text(
            clean_text,   # full original contract text
            amendments    # only amended clauses
        )

        # --------------------------------------------------
        # STEP 10: SAVE FINAL OUTPUTS
        # --------------------------------------------------
        report_path = os.path.join(
            OUTPUT_DIR, f"{base_name}_m3_compliance_report.json"
        )
        contract_path = os.path.join(
            OUTPUT_DIR, f"{base_name}_updated_contract.txt"
        )
        
        pdf_contract_path = os.path.join(
            OUTPUT_DIR, f"{base_name}_updated_contract.pdf"
        )

        write_contract_pdf(updated_contract, pdf_contract_path)

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump({
                "compliance_report": compliance_report,
                "amended_clauses": list(amendments.keys()),
            }, f, indent=2)

        with open(contract_path, "w", encoding="utf-8") as f:
            f.write(updated_contract)


        # DERIVE OVERALL SEVERITY (ESCALATION LOGIC)
        if any(i["severity"] == "critical" for i in compliance_report["issues"]):
            severity = "CRITICAL"
        elif any(i["severity"] == "high" for i in compliance_report["issues"]):
            severity = "HIGH"
        elif any(i["severity"] == "medium" for i in compliance_report["issues"]):
            severity = "MEDIUM"
        else:
            severity = "LOW"

        final_pipeline_result = {
            "pipeline_status": "SUCCESS",
            "run_id": f"RUN-{contract_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",

            # FOR EMAIL
            "contract_name": base_name,
            "total_clauses_extracted": len(assessed_clauses),
            "total_risks_detected": compliance_report["total_issues_detected"],
            "amendments_done": bool(amendments or inserted_clauses),
            "timestamp": datetime.utcnow().isoformat() + "Z",

            # EXISTING FIELDS (KEEP THEM)
            "contract_id": contract_id,
            "regulation": ", ".join(
                sorted(set(i["regulation"] for i in compliance_report["issues"]))
            ) if compliance_report["issues"] else "NONE",

            "severity": severity,

            "issue_type": (
                "high_risk_clause"
                if compliance_report["issues"]
                else "none"
            ),

            "summary": f"{compliance_report['total_issues_detected']} compliance issues detected",

            "contract_updated": bool(amendments or inserted_clauses),
            "changes_applied": list(amendments.keys()),

            "audit_id": f"AUD-{contract_id}",

            "failed_stage": None,
            "error_summary": None
        }

        try:
            notify_once(final_pipeline_result)
        except Exception as email_err:
            print("⚠️ Email notification failed:", email_err)

        update_progress(100, "Completed")
        print("\n==============================")
        print(" PIPELINE COMPLETED SUCCESSFULLY ")
        print("==============================")
        print("Generated files:")
        print(" -", m2_json)
        print(" -", m2_csv)
        print(" -", report_path)
        print(" -", contract_path)
    
    except Exception as e:

        failure_result = {
            "pipeline_status": "FAILED",
            "run_id": "RUN-ERROR",

            "contract_id": os.path.basename(pdf_path),
            "regulation": "UNKNOWN",
            "severity": "CRITICAL",
            "issue_type": "pipeline_failure",

            "summary": "Pipeline execution failed",
            "contract_updated": False,
            "changes_applied": [],

            "audit_id": "AUD-ERROR",

            "failed_stage": "Pipeline Execution",
            "error_summary": str(e)
        }

        try:
            notify_once(failure_result)
        except Exception as email_err:
            print("⚠️ Email notification failed:", email_err)

        safe_notify_slack({
            "event_type": "PIPELINE_FAILURE",
            "severity": "CRITICAL",
            "summary": "Contract compliance pipeline failed",
            "details": {
                "error": str(e)
            },
            "action_required": "Investigate and rerun pipeline",
            "source_module": "Pipeline Orchestrator"
        })

        raise



# ==================================================
# ENTRY POINT
# ==================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run Full AI-Powered Contract Compliance Pipeline"
    )
    parser.add_argument(
        "--pdf",
        required=True,
        help="Path to contract PDF file"
    )

    args = parser.parse_args()
    run_pipeline(args.pdf)

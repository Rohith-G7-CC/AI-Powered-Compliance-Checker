# app.py

import streamlit as st
import json
import os
from datetime import datetime
from dotenv import load_dotenv
# ----------------------------
# IMPORT YOUR PIPELINE
# ----------------------------
from run import run_pipeline

# Load environment variables from .env
load_dotenv()
RAW_DIR = os.getenv("RAW_DIR", "./raw")
os.makedirs(RAW_DIR, exist_ok=True)
# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(
    page_title="AI Contract Compliance Checker",
    layout="wide"
)


# ----------------------------
# OUTPUT DIRECTORY (SAFE)
# ----------------------------
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./results")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ----------------------------
# CUSTOM CSS (COPIED FROM app4.py STYLE)
# ----------------------------
st.markdown("""
<style>

/* REAL TAB TEXT */
.stTabs [data-baseweb="tab"] p {
    font-size: 1.10rem !important;
    font-weight: 500 !important;
}

/* Active tab */
.stTabs [aria-selected="true"] p {
    font-size: 1.35rem !important;
    font-weight: 600 !important;
    color: white !important;
}

/* Tab box */
.stTabs [data-baseweb="tab"] {
    padding: 14px 26px !important;
    background: #eef1f6;
    border-radius: 12px !important;
    border: 1px solid #d1d9e6;
    transition: all 0.3s ease-in-out;
}

/* Hover */
.stTabs [data-baseweb="tab"]:hover {
    background: linear-gradient(135deg, #4b9fff, #6f42c1) !important;
    transform: translateY(-4px);
    box-shadow: 0px 6px 15px rgba(0,0,0,0.25);
}
.stTabs [data-baseweb="tab"]:hover p {
    color: white !important;
}

/* Active */
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #4b9fff, #1f78ff) !important;
    box-shadow: 0px 6px 18px rgba(75,159,255,0.5);
}

/* Spacing */
.stTabs [data-baseweb="tab-list"] {
    gap: 12px !important;
}

/* Primary Button */
div.stButton > button:first-child {
    background: linear-gradient(135deg, #4b9fff, #6f42c1);
    color: white;
    padding: 12px 25px;
    border-radius: 12px;
    font-size: 1.1rem;
    font-weight: 700;
    border: none;
}

/* Risk Summary Cards */
.risk-card {
    background: #f8f9fc;
    border-radius: 14px;
    padding: 18px 10px;
    text-align: center;
    border: 1px solid #e1e6f0;
}

.risk-label {
    font-size: 1.05rem;
    font-weight: 700;
    margin-bottom: 6px;
}

.risk-value {
    font-size: 2.2rem;
    font-weight: 800;
}

/* Download Card Style */
.download-card {
    border: 1px solid #dce1eb;
    border-radius: 14px;
    padding: 16px 18px;
    margin-bottom: 14px;
    background: #f9fafc;
    transition: all 0.25s ease-in-out;
}

.download-card:hover {
    background: #eef3ff;
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(0,0,0,0.08);
}

.download-title {
    font-size: 1.05rem;
    font-weight: 600;
    margin-bottom: 10px;
}

/* Bigger + Bolder Download Button Text */
.download-card button {
    font-size: 1.15rem !important;
    font-weight: 700 !important;
}

</style>
""", unsafe_allow_html=True)

# ----------------------------
# TITLE
# ----------------------------
st.title("📜 AI-Powered Regulatory Compliance Checker")
st.caption("End-to-End Regulatory Risk, Compliance & Amendment System")

# ----------------------------
# SESSION STATE INIT
# ----------------------------
if "pipeline_done" not in st.session_state:
    st.session_state.pipeline_done = False
if "output_files" not in st.session_state:
    st.session_state.output_files = {}

# ----------------------------
# TABS
# ----------------------------
tabs = st.tabs([
    "📂 Upload & Run",
    "📑 Clause & Risk Analysis",
    "🛠️ Suggestions & Amendments",
    "📊 Compliance Report",
    "🔔 Alerts & Downloads"
])

# ==================================================
# TAB 1 — UPLOAD & RUN
# ==================================================
with tabs[0]:
    st.header("Upload Contract & Run Full Pipeline")

    uploaded_pdf = st.file_uploader(
        "Upload Contract PDF",
        type=["pdf"]
    )

    if uploaded_pdf:
        # Save using original filename
        raw_dir = os.path.join(RAW_DIR)
        os.makedirs(raw_dir, exist_ok=True)

        pdf_path = os.path.join(raw_dir, uploaded_pdf.name)

        with open(pdf_path, "wb") as f:
            f.write(uploaded_pdf.read())

        st.success("PDF uploaded successfully")

        progress_bar = st.progress(0)
        status_text = st.empty()

        def progress_callback(percent, message):
            progress_bar.progress(percent / 100)
            status_text.markdown(
                f"🔄 **{message}** — **{percent}%**"
            )

        run_clicked = st.button("⚡Run Compliance Pipeline")

        if run_clicked and not st.session_state.pipeline_done:
            try:
                with st.spinner("Running compliance pipeline…"):
                    run_pipeline(
                        pdf_path,
                        progress_callback=progress_callback
                    )

                st.session_state.pipeline_done = True
                status_text.success("Pipeline completed successfully")

            except Exception as e:
                st.error("❌ Pipeline failed. Check logs.")



# ==================================================
# TAB 2 — CLAUSES & RISK
# ==================================================
with tabs[1]:
    st.header("Clause Extraction & Risk Analysis")

    if not st.session_state.pipeline_done:
        st.info("Run the pipeline first.")
    else:
        if not os.path.exists(OUTPUT_DIR):
            st.warning("No output directory found.")
        else:
            m2_files = [
                f for f in os.listdir(OUTPUT_DIR)
                if f.endswith("_m2_output.json")
            ]

            if not m2_files:
                st.warning("Milestone 2 output not found.")
            else:
                # Pick the most recent Milestone 2 file
                m2_files.sort(
                    key=lambda x: os.path.getmtime(
                        os.path.join(OUTPUT_DIR, x)
                    ),
                    reverse=True
                )

                m2_path = os.path.join(OUTPUT_DIR, m2_files[0])

                with open(m2_path, "r", encoding="utf-8") as f:
                    clauses = json.load(f)

                # ----------------------------
                # RISK SUMMARY (TOP METRICS)
                # ----------------------------
                total_clauses = len(clauses)
                high_risk = medium_risk = low_risk = 0

                for c in clauses:
                    severity = c.get("risk", {}).get("severity", "").lower()
                    if severity == "high":
                        high_risk += 1
                    elif severity == "medium":
                        medium_risk += 1
                    else:
                        low_risk += 1

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.markdown(f"""
                    <div class="risk-card">
                        <div class="risk-label">📑 Total Clauses</div>
                        <div class="risk-value">{total_clauses}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                    <div class="risk-card">
                        <div class="risk-label">🔴 High Risk</div>
                        <div class="risk-value">{high_risk}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    st.markdown(f"""
                    <div class="risk-card">
                        <div class="risk-label">🟠 Medium Risk</div>
                        <div class="risk-value">{medium_risk}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col4:
                    st.markdown(f"""
                    <div class="risk-card">
                        <div class="risk-label">🟢 Low Risk</div>
                        <div class="risk-value">{low_risk}</div>
                    </div>
                    """, unsafe_allow_html=True)


                st.divider()

                # ----------------------------
                # CLAUSE-BY-CLAUSE DISPLAY
                # ----------------------------
                for c in clauses:
                    st.subheader(f"Clause {c.get('clause_id', 'N/A')}")
                    st.write(c.get("clause_text", "Clause text not available."))

                    risk = c.get("risk", {})
                    if risk:
                        st.json(risk)
                    else:
                        st.warning("Risk analysis not available for this clause.")



# ==================================================
# TAB 3 — SUGGESTIONS & AMENDMENTS
# ==================================================
with tabs[2]:
    st.header("Suggestions & Amendments")

    if not st.session_state.pipeline_done:
        st.info("Run the pipeline first.")
    else:
        if not os.path.exists(OUTPUT_DIR):
            st.warning("No output directory found.")
        else:
            report_files = [
                f for f in os.listdir(OUTPUT_DIR)
                if f.endswith("_m3_compliance_report.json")
            ]

            if not report_files:
                st.warning("Compliance report not found.")
            else:
                # Pick latest report
                report_files.sort(
                    key=lambda x: os.path.getmtime(
                        os.path.join(OUTPUT_DIR, x)
                    ),
                    reverse=True
                )

                report_path = os.path.join(OUTPUT_DIR, report_files[0])

                with open(report_path, "r", encoding="utf-8") as f:
                    report = json.load(f)

                # --------------------------
                # Amended Clauses
                # --------------------------
                st.subheader("🔧 Amended High-Risk Clauses")

                amended = report.get("amended_clauses", [])

                if amended:
                    for cid in amended:
                        st.warning(f"Clause amended: {cid}")
                else:
                    st.success("No clause amendments were required.")

                # --------------------------
                # Inserted Clauses
                # --------------------------
                st.subheader("➕ Newly Inserted Compliance Clauses")

                inserted = report.get("inserted_clauses", [])

                if inserted:
                    for clause in inserted:
                        st.info(clause)
                else:
                    st.success("No new clauses were inserted.")



# ==================================================
# TAB 4 — COMPLIANCE REPORT
# ==================================================
with tabs[3]:
    st.header("Compliance Summary")

    if not st.session_state.pipeline_done:
        st.info("Run the pipeline first.")
    else:
        if not os.path.exists(OUTPUT_DIR):
            st.warning("No output directory found.")
        else:
            report_files = [
                f for f in os.listdir(OUTPUT_DIR)
                if f.endswith("_m3_compliance_report.json")
            ]

            if not report_files:
                st.warning("Compliance report not available.")
            else:
                # Optional: pick the most recent report
                report_files.sort(
                    key=lambda x: os.path.getmtime(
                        os.path.join(OUTPUT_DIR, x)
                    ),
                    reverse=True
                )

                report_path = os.path.join(OUTPUT_DIR, report_files[0])

                with open(report_path, "r", encoding="utf-8") as f:
                    report = json.load(f)

                st.json(report)


# ==================================================
# TAB 5 — ALERTS & DOWNLOADS
# ==================================================
with tabs[4]:
    st.header("Notifications & Output Files")

    if not st.session_state.pipeline_done:
        st.info("Run the pipeline first.")
    else:
        # Always use the same OUTPUT_DIR as run.py
        if not os.path.exists(OUTPUT_DIR):
            st.warning("No output directory found.")
        else:
            files = sorted(
                os.listdir(OUTPUT_DIR),
                key=lambda x: os.path.getmtime(os.path.join(OUTPUT_DIR, x)),
                reverse=True
            )[:4]   # last run outputs

            if not files:
                st.info("Pipeline completed, but no output files generated yet.")
            else:
                # Split files into rows of 2
                for i in range(0, len(files), 2):
                    cols = st.columns(2)

                    for col, f in zip(cols, files[i:i+2]):
                        file_path = os.path.join(OUTPUT_DIR, f)

                        if f.endswith("_updated_contract.txt"):
                            button_label = "⬇️ Updated Contract (TXT)"
                        elif f.endswith("_m3_compliance_report.json"):
                            button_label = "⬇️ Compliance Report (JSON)"
                        elif f.endswith("_updated_contract.pdf"):
                            button_label = "⬇️ Updated Contract (PDF)"
                        elif f.endswith("_m2_annotations.csv"):
                            button_label = "⬇️ Clause Annotations (CSV)"
                        else:
                            # ❌ DO NOTHING — no card, no column content
                            continue

                        # ✅ ONLY render card when file is valid
                        with col:
                            with open(file_path, "rb") as file:
                                st.markdown(
                                    '<div class="download-card">',
                                    unsafe_allow_html=True
                                )

                                st.download_button(
                                    label=button_label,
                                    data=file,
                                    file_name=f,
                                    use_container_width=True
                                )

                                st.markdown(
                                    '</div>',
                                    unsafe_allow_html=True
                                )



# ----------------------------
# FOOTER
# ----------------------------
st.write("---")
st.write("© 2025 AI-Powered Regulatory Compliance Checker")

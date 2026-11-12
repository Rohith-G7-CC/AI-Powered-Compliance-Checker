## 📜 AI-Powered Regulatory Compliance Checker for Contracts

An end-to-end **Generative AI–driven system** that automatically reviews contracts, detects regulatory compliance risks (GDPR, HIPAA), identifies missing clauses, generates legally safe amendments, and provides real-time alerts and audit logs.

---

## 🚀 Project Overview

Manual contract compliance review is time-consuming, error-prone, and difficult to scale.  
This project solves that problem by using **Large Language Models (LLMs)** to:

- Extract legal clauses from contracts
- Analyze regulatory and legal risks
- Detect missing or weak compliance clauses
- Automatically suggest safe amendments
- Track live regulatory updates
- Notify stakeholders via Email, Slack, and Google Sheets
- Generate updated contracts and compliance reports

The system is designed to be **modular, reliable, explainable, and production-ready**.

---

## 🧠 Key Features

- 📂 **PDF Contract Upload**
- 🔍 **Clause Extraction using GenAI**
- ⚠️ **Clause-Level Risk Analysis**
- 📜 **GDPR & HIPAA Compliance Checks**
- ✏️ **Automatic Amendment Generation (High-Risk Only)**
- 🧱 **Safe Contract Rebuilding**
- 📊 **Compliance Reports (JSON, CSV)**
- 📄 **Updated Contract Output (TXT & PDF)**
- 🔔 **Email & Slack Notifications**
- 📈 **Google Sheets Audit Logging**
- 🛡️ **LLM Fail-Safe & Fallback Mechanisms**

---

## 🏗️ System Architecture

```

Streamlit UI
↓
Pipeline Orchestrator (run.py)
↓
PDF Extraction → Text Cleaning → Chunking
↓
Clause Extraction (LLM)
↓
Risk Analysis (LLM)
↓
Compliance Gap Detection
↓
Amendment Generation (High Risk)
↓
Contract Rebuilding
↓
Outputs + Notifications + Audit Logs

```

---

## 🧩 Project Structure

```

.
├── app.py                         # Streamlit UI
├── run.py                         # Main pipeline orchestrator
├── src/
│   ├── clause_engine/
│   │   └── clause_extractor.py
│   ├── risk_engine/
│   │   └── risk_engine.py
│   ├── contract_modification/
│   │   ├── amendment_generator.py
│   │   ├── gap_analyzer.py
│   │   └── contract_rebuilder.py
│   ├── regulatory/
│   │   ├── gdpr_live_tracker.py
│   │   └── hipaa_live_tracker.py
│   ├── llm/
│   │   └── llm_router.py
│   ├── integrations/
│   │   ├── email_notifier.py
│   │   ├── slack_notifier.py
│   │   └── google_sheets/
│   │       ├── gsheet_client.py
│   │       └── gsheet_writers.py
│   └── utils/
│       ├── pdf_extract.py
│       ├── cleaner.py
│       ├── annotate_csv.py
│       └── pdf_writer.py
├── results/                       # Generated outputs
├── data/                          # Regulatory snapshots
├── .env                           # Environment variables
└── README.md

````

---

## 🧠 LLM Strategy

### Primary Model
- Groq – llama-3.3-70b-versatile

### Fallbacks
- OpenRouter (LLaMA 3.1 8B)
- Hard fallback JSON (never crashes)

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/springboardmentor587-star/Compliance-Checker.git
cd Compliance-Checker
````

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables (`.env`)

```env
# LLM Keys
GROQ_API_KEY=your_groq_key
OPENROUTER_API_KEY=your_openrouter_key

# Email
SENDER_EMAIL=your_email@gmail.com
EMAIL_APP_PASSWORD=your_app_password

# Slack
SLACK_WEBHOOK_URL=your_slack_webhook

# Directories
RAW_DIR=./data/raw
OUTPUT_DIR=./data/processed

# Chunking
MAX_CHUNK_TOKENS=1500
CHUNK_OVERLAP=200
```

---

## ▶️ Running the Application

### Start Streamlit UI

```bash
streamlit run app.py
```

Then open:

```
http://localhost:8501
```

---

## 📊 Generated Outputs

| File Type                    | Purpose                    |
| ---------------------------- | -------------------------- |
| `_m2_output.json`            | Clause-level risk analysis |
| `_m2_annotations.csv`        | Clause annotations         |
| `_m3_compliance_report.json` | Compliance summary         |
| `_updated_contract.txt`      | Updated contract           |
| `_updated_contract.pdf`      | Final PDF contract         |

---

## 🔔 Notifications & Integrations

* **Slack** → High-risk issues, regulatory updates, failures
* **Email** → High/Critical severity or contract updates
* **Google Sheets** →

  * Contracts Overview
  * Compliance Issues
  * Audit Logs

---

## 🧪 Reliability & Fail-Safe Design

* Pipeline never crashes on LLM failure
* Safe default outputs
* Severity-based automation
* Full audit trail for compliance

---

## 🌱 Future Enhancements

* Retrieval-Augmented Generation (RAG)
* Support for more regulations (ISO, SOC2, PCI-DSS)
* Multilingual contract analysis
* Human approval workflows
* Continuous monitoring of active contracts
* Cloud deployment with REST APIs


---

## 📄 License

This project is licensed under the **MIT License**.

---


## 👥 Contributors

- **Charan** – Project Lead & Mentor

- **Rohith Vunna** – Student Developer
  
- Open to community contributions 🚀  

Feel free to fork this repository, raise issues, or submit pull requests.


---

⭐ **If you like this project, give it a star on GitHub!**

---

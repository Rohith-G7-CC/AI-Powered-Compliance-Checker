import json
from pathlib import Path

REGULATIONS_FILE = Path("data/regulations/regulations.json")
REGULATIONS_FILE.parent.mkdir(parents=True, exist_ok=True)

DEFAULT_REGULATIONS = {
    "GDPR": {
        "required_clauses": [
            "Data Processing",
            "Data Retention",
            "Breach Notification",
            "Data Subject Rights"
        ]
    },
    "HIPAA": {
        "required_clauses": [
            "PHI Protection",
            "Access Controls",
            "Audit Controls"
        ]
    }
}

def load_regulations():
    if not REGULATIONS_FILE.exists():
        with open(REGULATIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_REGULATIONS, f, indent=2)

    with open(REGULATIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

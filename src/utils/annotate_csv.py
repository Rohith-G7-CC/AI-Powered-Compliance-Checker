# src/utils/annotate_csv.py
import csv
import json
from pathlib import Path

SCHEMA = [
    "clause_id",
    "clause_type",
    "clause_text",
    "risk_score",
    "severity",
]

def convert_m2_json_to_csv(m2_json, out_csv):
    with open(m2_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    rows = []
    for c in data:
        rows.append([
            c.get("clause_id"),
            c.get("clause_type"),
            c.get("clause_text"),
            c.get("risk", {}).get("risk_score"),
            c.get("risk", {}).get("severity")        
            or c.get("risk", {}).get("risk_level")  
            ])

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(SCHEMA)
        writer.writerows(rows)

    print("Saved CSV →", out_csv)


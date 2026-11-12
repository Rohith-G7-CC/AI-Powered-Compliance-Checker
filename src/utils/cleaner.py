# src/utils/cleaner.py
import os
import re
from pathlib import Path
from dotenv import load_dotenv
import json

load_dotenv()
RAW_DIR = os.getenv("RAW_DIR")
PROCESSED_DIR = os.getenv("PROCESSED_DIR")
Path(PROCESSED_DIR).mkdir(parents=True, exist_ok=True)

MAX_CHUNK = int(os.getenv("MAX_CHUNK_TOKENS"))
OVERLAP = int(os.getenv("CHUNK_OVERLAP"))

def normalize_text(text: str) -> str:
    # Remove multiple empty lines
    t = re.sub(r'\r\n', '\n', text)
    t = re.sub(r'\n{2,}', '\n\n', t)
    t = re.sub(r'[ \t]+', ' ', t)
    t = t.strip()
    return t

def chunk_text(text: str, max_tokens=MAX_CHUNK, overlap=OVERLAP):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        j = min(len(words), i + max_tokens)
        chunk = " ".join(words[i:j])
        chunks.append(chunk)
        i = j - overlap if j - overlap > i else j
    return chunks

def process_all():
    for f in Path(RAW_DIR).glob("*.txt"):
        with open(f, "r", encoding="utf-8") as fh:
            raw = fh.read()
        txt = normalize_text(raw)
        chunks = chunk_text(txt)
        out = {
            "source": str(f),
            "chunks": chunks,
            "chunk_count": len(chunks)
        }
        out_fname = Path(PROCESSED_DIR)/ (f.stem + "_processed.json")
        with open(out_fname, "w", encoding="utf-8") as outfh:
            json.dump(out, outfh, indent=2, ensure_ascii=False)
        print("Wrote", out_fname)

if __name__ == "__main__":
    process_all()

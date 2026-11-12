# src/utils/pdf_extract.py
import os
from pathlib import Path
import pdfplumber
from dotenv import load_dotenv

load_dotenv()

RAW_DIR = os.getenv("RAW_DIR", "./data/raw")
Path(RAW_DIR).mkdir(parents=True, exist_ok=True)

def extract_pdf(file_path, out_path=None):
    texts = []
    with pdfplumber.open(file_path) as pdf:
        for p in pdf.pages:
            texts.append(p.extract_text() or "")

    joined = "\n".join(texts)

    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(f"Source: {file_path}\n\n")
            f.write(joined)

    return joined

def main(input_dir="data/raw"):
    # Step 1: Set the input directory (default is "data/raw")
    p = Path(input_dir)
    
    # Step 2: Get a list of all PDF files in the input directory and subdirectories
    files = list(p.glob("**/*.pdf"))
    
    # Step 3: Loop through each PDF file
    for file in files:
        # Generate a unique output filename based on the file name and hash
        fname = f"{file.stem}_{abs(hash(str(file)))}.txt"
        
        # Create the output file path in the RAW_DIR
        out_path = os.path.join(RAW_DIR, fname)
        
        # Print the file being processed
        print("Extracting", file, "->", out_path)
        
        # Call the extract_pdf function to extract text from the PDF
        extract_pdf(str(file), out_path)

if __name__ == "__main__":
    main()

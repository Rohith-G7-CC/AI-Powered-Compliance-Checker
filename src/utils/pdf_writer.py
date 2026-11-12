# src/utils/pdf_writer.py

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import re

def write_contract_pdf(contract_text, output_path):
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    import re

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        alignment=1,   # center
        spaceAfter=18
    )

    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        spaceBefore=14,
        spaceAfter=8
    )

    clause_text = ParagraphStyle(
        "ClauseText",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        spaceAfter=6
    )

    story = []

    for line in contract_text.split("\n"):
        line = line.strip()
        if not line:
            continue

        # Main title
        if re.match(r"^[A-Z0-9 ()\-]+AGREEMENT$", line):
            story.append(Paragraph(line, title_style))

        # Section headings (e.g., "5. DATA PROTECTION & PRIVACY")
        elif re.match(r"^\d+\.\s+[A-Z &]+$", line):
            story.append(Paragraph(line, section_heading))

        # Clause text
        else:
            story.append(Paragraph(line, clause_text))

    doc.build(story)
    print(f"Contract PDF written to {output_path}")


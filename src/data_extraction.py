from docx import Document
from typing import List, Dict

def extract_docx_sections(docx_path: str, section_names: List[str]) -> Dict[str, str]:
    """
    Extracts text from a DOCX by section headings. Only sections in `section_names` are kept.
    Returns a mapping from section name to its full text.
    """
    doc = Document(docx_path)
    sections: Dict[str, str] = {name: "" for name in section_names}
    current_section = None

    for para in doc.paragraphs:
        text = para.text.strip()
        # Check if this paragraph is a section heading
        if text in section_names:
            current_section = text
            continue
        # If inside a section, append text
        if current_section:
            sections[current_section] += text + "\n"

    return sections

import fitz  # PyMuPDF

def extract_pdf_sections(pdf_path: str, section_names: List[str]) -> Dict[str, str]:
    """
    Extracts text from a PDF by looking for section headings.
    Returns a mapping from section name to its text.
    """
    doc = fitz.open(pdf_path)
    sections: Dict[str, str] = {name: "" for name in section_names}
    current_section = None

    # Concatenate all page texts with markers
    full_text = ""
    for page in doc:
        page_text = page.get_text()
        full_text += page_text + "\n"

    # Split into lines and parse
    for line in full_text.splitlines():
        line = line.strip()
        if line in section_names:
            current_section = line
            continue
        if current_section:
            sections[current_section] += line + "\n"
    return sections

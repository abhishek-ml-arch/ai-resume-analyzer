import fitz  # PyMuPDF


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract plain text from PDF bytes. Returns empty string if extraction fails."""
    text = ""
    try:
        pdf = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page in pdf:
            text += page.get_text()
        pdf.close()
    except Exception as e:
        raise ValueError(f"Failed to parse PDF: {str(e)}")
    return text

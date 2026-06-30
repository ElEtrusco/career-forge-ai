
from pypdf import PdfReader
import re


def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    return clean_text(text)


def clean_text(text: str) -> str:
    # eliminar saltos de línea excesivos
    text = re.sub(r"\n+", "\n", text)

    # eliminar espacios duplicados
    text = re.sub(r"\s+", " ", text)

    return text.strip()

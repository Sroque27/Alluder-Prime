"""
extractors.py
-------------
This module handles all text extraction for Alluder.

Supported input types:
1. Raw text (copy & paste)
2. PDF files (via pdfplumber)
3. URLs (via requests + BeautifulSoup)

Each extractor returns CLEAN, PLAIN TEXT that can be fed directly
into the NLP pipeline.
"""

import pdfplumber
import requests
from bs4 import BeautifulSoup
from fastapi import UploadFile


# ---------------------------------------------------------
# 1. Extract from raw text
# ---------------------------------------------------------
def extract_from_text(text: str) -> str:
    """
    Returns the text exactly as provided, but ensures it is stripped
    of leading/trailing whitespace. This keeps the pipeline clean.
    """
    return text.strip()


# ---------------------------------------------------------
# 2. Extract from PDF upload
# ---------------------------------------------------------
async def extract_from_pdf(file: UploadFile) -> str:
    """
    Extracts text from an uploaded PDF file using pdfplumber.

    Steps:
    - Read the uploaded file into memory
    - Open it with pdfplumber
    - Extract text page by page
    - Join all pages into a single string
    """

    # Read the PDF file into bytes
    pdf_bytes = await file.read()

    # pdfplumber requires a file-like object, so wrap the bytes
    import io
    pdf_stream = io.BytesIO(pdf_bytes)

    extracted_text = []

    # Open the PDF safely
    with pdfplumber.open(pdf_stream) as pdf:
        for page in pdf.pages:
            # Extract text from each page
            page_text = page.extract_text()
            if page_text:
                extracted_text.append(page_text)

    # Join all pages with line breaks
    return "\n".join(extracted_text).strip()


# ---------------------------------------------------------
# 3. Extract from URL
# ---------------------------------------------------------
def extract_from_url(url: str) -> str:
    """
    Downloads a webpage and extracts readable text using BeautifulSoup.

    Steps:
    - Send HTTP GET request
    - Parse HTML
    - Remove scripts, styles, and irrelevant tags
    - Extract visible text
    """

    try:
        # Fetch the webpage
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise error for bad status codes
    except Exception as e:
        return f"Error fetching URL: {e}"

    # Parse HTML content
    soup = BeautifulSoup(response.text, "html.parser")

    # Remove script and style tags (they contain no readable text)
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()

    # Extract visible text
    text = soup.get_text(separator="\n")

    # Clean up whitespace
    cleaned = "\n".join(line.strip() for line in text.splitlines() if line.strip())

    return cleaned

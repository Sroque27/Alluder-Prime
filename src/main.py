"""
Alluder Backend Server (FastAPI)
--------------------------------
This file exposes the API endpoints that the Alluder UI interacts with.

Endpoints:
- GET /          → Serve the main UI (index.html)
- POST /analyze/text → Analyze raw text input
- POST /analyze/pdf  → Analyze uploaded PDF files
- POST /analyze/url  → Analyze text extracted from a URL
- GET /health    → Simple health check

This file does NOT perform NLP itself — it delegates to pipeline.py.
"""

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Import your pipeline and extractors
from .pipeline import run_pipeline
from .extractors import extract_from_text, extract_from_pdf, extract_from_url



# ---------------------------------------------------------
# Create the FastAPI application
# ---------------------------------------------------------
app = FastAPI(
    title="Alluder",
    description="A local reading assistant that annotates text with insights.",
)


# ---------------------------------------------------------
# Serve the UI folder (HTML/CSS/JS)
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent      # Directory of this file
UI_DIR = BASE_DIR / "ui"                        # Path to UI folder

# Mount the UI directory so it is accessible at /ui/*
app.mount("/ui", StaticFiles(directory=UI_DIR), name="ui")


# ---------------------------------------------------------
# Root route → loads the main UI page
# ---------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Returns index.html so the user sees the Alluder interface.
    """
    index_file = UI_DIR / "index.html"
    return index_file.read_text(encoding="utf-8")


# ---------------------------------------------------------
# Analyze raw text input
# ---------------------------------------------------------
@app.post("/analyze/text")
async def analyze_text(text: str = Form(...)):
    """
    Accepts plain text from a form submission.
    Runs the NLP pipeline and returns annotations.
    """
    extracted = extract_from_text(text)
    annotations = run_pipeline(extracted)
    return JSONResponse({"original_text": extracted, "annotations": annotations})


# ---------------------------------------------------------
# Analyze uploaded PDF
# ---------------------------------------------------------
@app.post("/analyze/pdf")
async def analyze_pdf(file: UploadFile = File(...)):
    """
    Accepts a PDF file upload.
    Extracts text from the PDF, runs the pipeline, and returns annotations.
    """
    extracted = await extract_from_pdf(file)
    annotations = run_pipeline(extracted)
    return JSONResponse({"original_text": extracted, "annotations": annotations})


# ---------------------------------------------------------
# Analyze text from a URL
# ---------------------------------------------------------
@app.post("/analyze/url")
async def analyze_url(url: str = Form(...)):
    """
    Accepts a URL string.
    Downloads the page, extracts text, runs the pipeline, and returns annotations.
    """
    extracted = extract_from_url(url)
    annotations = run_pipeline(extracted)
    return JSONResponse({"original_text": extracted, "annotations": annotations})


# ---------------------------------------------------------
# Health check endpoint
# ---------------------------------------------------------
@app.get("/health")
async def health():
    """
    Simple endpoint to verify that the server is running.
    """
    return {"status": "ok", "app": "Alluder"}

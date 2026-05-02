"""
Alluder Package
---------------
This file marks the 'src' directory as a Python package.

It also provides convenient imports for core modules so they can be
accessed cleanly throughout the project.
"""

# Re-export commonly used functions for convenience
from .pipeline import run_pipeline
from .extractors import extract_from_text, extract_from_pdf, extract_from_url
from .knowledge import fetch_background_info

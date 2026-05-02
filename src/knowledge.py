"""
knowledge.py
------------
This module provides background knowledge lookup for Alluder.

It currently supports:
1. Wikipedia summaries
2. Wikidata entity lookup (simple version)

The goal is to return short, helpful background information
for named entities detected by the NLP pipeline.

All functions are designed to:
- Fail gracefully (never crash the pipeline)
- Return clean, readable summaries
- Be easy to expand with more knowledge sources later
"""

import wikipedia
import requests


# ---------------------------------------------------------
# Helper: Clean up Wikipedia summaries
# ---------------------------------------------------------
def clean_summary(text: str) -> str:
    """
    Removes unnecessary whitespace and formatting from Wikipedia summaries.
    """
    return " ".join(text.split()).strip()


# ---------------------------------------------------------
# 1. Wikipedia lookup
# ---------------------------------------------------------
def fetch_wikipedia_summary(query: str) -> str:
    """
    Attempts to fetch a short summary from Wikipedia.

    Steps:
    - Search for the query
    - Take the top result
    - Fetch its summary
    - Clean and return it

    Returns:
        A short summary string, or None if lookup fails.
    """
    try:
        # Search Wikipedia for the best match
        results = wikipedia.search(query)

        if not results:
            return None

        # Take the top result
        page_title = results[0]

        # Fetch the summary (first paragraph)
        summary = wikipedia.summary(page_title, sentences=2)

        return clean_summary(summary)

    except Exception:
        # Any error (disambiguation, network, etc.) → return None
        return None


# ---------------------------------------------------------
# 2. Wikidata lookup (simple version)
# ---------------------------------------------------------
def fetch_wikidata_info(query: str) -> str:
    """
    Performs a simple Wikidata lookup using the search API.

    Returns:
        A short description (e.g., "Italian city", "American actor")
        or None if lookup fails.

    This is intentionally lightweight — Wikidata is huge, and
    this keeps things fast and predictable.
    """

    try:
        # Wikidata search API endpoint
        url = "https://www.wikidata.org/w/api.php"

        params = {
            "action": "wbsearchentities",
            "format": "json",
            "language": "en",
            "search": query,
        }

        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        # If no results, return None
        if "search" not in data or not data["search"]:
            return None

        # Take the top result
        top = data["search"][0]

        # Wikidata returns a "description" field (short and useful)
        description = top.get("description")

        return description

    except Exception:
        return None


# ---------------------------------------------------------
# 3. Combined background knowledge lookup
# ---------------------------------------------------------
def fetch_background_info(query: str) -> dict:
    """
    Attempts to fetch background knowledge from multiple sources.

    Returns a dictionary like:
    {
        "wikipedia": "...",
        "wikidata": "..."
    }

    If no information is found, returns None.
    """

    wiki_summary = fetch_wikipedia_summary(query)
    wikidata_desc = fetch_wikidata_info(query)

    # If nothing found, return None
    if not wiki_summary and not wikidata_desc:
        return None

    # Build a structured response
    info = {}

    if wiki_summary:
        info["wikipedia"] = wiki_summary

    if wikidata_desc:
        info["wikidata"] = wikidata_desc

    return info

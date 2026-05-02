"""
annotators.py
-------------
This module contains reusable annotation functions for Alluder.

It separates token-level, entity-level, and pattern-based annotation
logic from the main pipeline, keeping the codebase modular and clean.

Functions included:
- annotate_tokens(doc)
- annotate_entities(doc)
- detect_date_periods(doc)
- detect_abbreviations(doc)
- detect_quotations(text)

These functions are imported and used by pipeline.py.
"""

from typing import List, Dict, Any
from lemminflect import getInflection
from .knowledge import fetch_background_info
import re


# ---------------------------------------------------------
# Token-level annotation
# ---------------------------------------------------------
def annotate_tokens(doc) -> List[Dict[str, Any]]:
    """
    Extracts token-level linguistic information from a spaCy Doc.

    Includes:
    - lemma
    - POS tag
    - dependency role
    - inflection (via lemminflect)
    - foreign-word detection (spaCy POS == "X")
    """
    annotations = []

    for token in doc:
        token_info = {
            "text": token.text,
            "lemma": token.lemma_,
            "pos": token.pos_,
            "tag": token.tag_,
            "dep": token.dep_,
            "is_alpha": token.is_alpha,
            "is_stop": token.is_stop,
        }

        # Inflection lookup (e.g., run → ran, running)
        try:
            inflections = getInflection(token.lemma_, token.tag_)
            if inflections:
                token_info["inflection"] = inflections
        except Exception:
            token_info["inflection"] = []


        # spaCy marks foreign words as POS = "X"
        if token.pos_ == "X":
            token_info["foreign_word"] = True

        annotations.append(token_info)

    return annotations


# ---------------------------------------------------------
# Entity-level annotation
# ---------------------------------------------------------
def annotate_entities(doc) -> List[Dict[str, Any]]:
    """
    Extracts named entities (PERSON, ORG, GPE, DATE, etc.)
    and attaches background knowledge when available.

    Background knowledge comes from:
    - Wikipedia summaries
    - Wikidata descriptions
    """
    entities = []

    for ent in doc.ents:
        ent_info = {
            "text": ent.text,
            "label": ent.label_,
        }

        # Fetch background info (Wikipedia + Wikidata)
        background = fetch_background_info(ent.text)
        if background:
            ent_info["background"] = background

        entities.append(ent_info)

    return entities


# ---------------------------------------------------------
# Date period detection
# ---------------------------------------------------------
def detect_date_periods(doc) -> List[Dict[str, Any]]:
    """
    Identifies DATE and TIME entities as 'date periods'.

    Example:
    - "In 1492" → DATE
    - "During the 18th century" → DATE
    - "At 5 PM" → TIME
    """
    periods = []

    for ent in doc.ents:
        if ent.label_ in ["DATE", "TIME"]:
            periods.append({
                "text": ent.text,
                "type": "date_period"
            })

    return periods


# ---------------------------------------------------------
# Abbreviation detection
# ---------------------------------------------------------
def detect_abbreviations(doc) -> List[Dict[str, Any]]:
    """
    Flags tokens that look like abbreviations.

    Simple heuristic:
    - All uppercase
    - Length > 1

    Examples:
    - NASA
    - FBI
    - NATO
    """
    abbr = []

    for token in doc:
        if token.text.isupper() and len(token.text) > 1:
            abbr.append({
                "text": token.text,
                "type": "abbreviation"
            })

    return abbr


# ---------------------------------------------------------
# Quotation detection
# ---------------------------------------------------------
def detect_quotations(text: str) -> List[Dict[str, Any]]:
    """
    Extracts quoted text using regex.

    Supports:
    - "double quotes"
    - “smart quotes”

    Returns a list of:
    { "text": "...", "type": "quotation" }
    """
    quotes = []

    # Regex captures both "..." and “...”
    pattern = r'"(.*?)"|“(.*?)”'
    matches = re.findall(pattern, text)

    for m in matches:
        # Each match is a tuple; pick the non-empty group
        content = m[0] if m[0] else m[1]

        quotes.append({
            "text": content,
            "type": "quotation"
        })

    return quotes

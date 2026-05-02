"""
Alluder NLP Pipeline
--------------------
This module runs the full text-analysis workflow for Alluder.
It is designed to be modular, readable, and easy to extend.

Pipeline stages:
1. Detect language of the input text
2. Translate to English if needed
3. Run spaCy NLP processing
4. Annotate tokens (POS, lemma, morphology, inflection)
5. Annotate entities (NER + background knowledge)
6. Detect date periods
7. Detect abbreviations
8. Detect quotations
9. Return a structured dictionary of all annotations
"""
import time
import spacy
from langdetect import detect
from googletrans import Translator
from lemminflect import getInflection
from typing import List, Dict, Any

from .annotators import (
    annotate_tokens,
    annotate_entities,
    detect_date_periods,
    detect_abbreviations,
    detect_quotations
)

# Background knowledge lookup (Wikipedia/Wikidata)
from .knowledge import fetch_background_info
from .utils.caching import cached_background_lookup



# ---------------------------------------------------------
# Load spaCy model once at import time (efficient + clean)
# ---------------------------------------------------------
try:
    # Load the small English model (fast + lightweight)
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # If the model isn't installed, give a clear error message
    raise RuntimeError(
        "spaCy model 'en_core_web_sm' is not installed.\n"
        "Install it with: python -m spacy download en_core_web_sm"
    )

# Translator instance (Google Translate API wrapper)
translator = Translator()


# ---------------------------------------------------------
# Detect the language of the input text
# ---------------------------------------------------------
def detect_language(text: str) -> str:
    """
    Uses langdetect to guess the language of the input text.
    Returns a 2‑letter language code (e.g., 'en', 'fr', 'es').
    """
    try:
        return detect(text)
    except:
        # If detection fails, return a safe fallback
        return "unknown"


# ---------------------------------------------------------
# Translate text to English if needed
# ---------------------------------------------------------
def translate_if_needed(text: str, lang: str) -> str:
    """
    If the text is not English, attempt to translate it.
    If translation fails, return the original text.
    """
    if lang == "en":
        return text  # No translation needed

    try:
        result = translator.translate(text, dest="en")
        return result.text
    except:
        # Fallback: return original text unchanged
        return text


# ---------------------------------------------------------
# Token‑level annotation (POS, lemma, morphology, inflection)
# ---------------------------------------------------------
def annotate_tokens(doc) -> List[Dict[str, Any]]:
    """
    Extracts token‑level linguistic information from the spaCy Doc.
    Includes POS, lemma, dependency, and inflection.
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

        # Silence lemminflect warnings by skipping invalid tags
        try:
            if token.tag_ not in (None, "", "X"):
                inflections = getInflection(token.lemma_, token.tag_)
            else:
                inflections = []
        except Exception:
            inflections = []

        if inflections:
            token_info["inflection"] = inflections

        # spaCy marks foreign words as POS = "X"
        if token.pos_ == "X":
            token_info["foreign_word"] = True

        annotations.append(token_info)

    return annotations


# ---------------------------------------------------------
# Entity‑level annotation (NER + background knowledge)
# ---------------------------------------------------------
def annotate_entities(doc) -> List[Dict[str, Any]]:
    """
    Extracts named entities (people, places, dates, etc.)
    and attaches background knowledge when available.
    """
    entities = []

    for ent in doc.ents:
        ent_info = {
            "text": ent.text,       # The entity span
            "label": ent.label_,    # Entity type (PERSON, ORG, GPE, etc.)
        }

        # Fetch Wikipedia/Wikidata background info
        # background = cached_background_lookup(ent.text, fetch_background_info)
        background = fetch_background_info(ent.text)
        if background:
            ent_info["background"] = background

        entities.append(ent_info)

    return entities


# ---------------------------------------------------------
# Detect date periods (simple version using spaCy DATE/TIME)
# ---------------------------------------------------------
def detect_date_periods(doc) -> List[Dict[str, Any]]:
    """
    Identifies DATE and TIME entities as 'date periods'.
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
# Detect abbreviations (simple heuristic: uppercase tokens)
# ---------------------------------------------------------
def detect_abbreviations(doc) -> List[Dict[str, Any]]:
    """
    Flags tokens that look like abbreviations (e.g., NASA, FBI).
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
# Detect quotations using regex
# ---------------------------------------------------------
def detect_quotations(text: str) -> List[Dict[str, Any]]:
    """
    Extracts quoted text using a simple regex pattern.
    Supports "quotes" and “smart quotes”.
    """
    import re

    quotes = []
    pattern = r'"(.*?)"|“(.*?)”'  # Matches both quote styles
    matches = re.findall(pattern, text)

    for m in matches:
        # Each match returns a tuple; pick the non‑empty one
        content = m[0] if m[0] else m[1]
        quotes.append({
            "text": content,
            "type": "quotation"
        })

    return quotes


# ---------------------------------------------------------
# Main pipeline orchestrator
# ---------------------------------------------------------
def run_pipeline(text: str) -> Dict[str, Any]:
    """
    Runs the full Alluder NLP pipeline and returns structured annotations.
    """

    # 1. Detect language
    t0 = time.perf_counter()
    lang = detect_language(text)
    t1 = time.perf_counter()

    # 2. Translate to English if needed
    translated = translate_if_needed(text, lang)
    t2 = time.perf_counter()

    # 3. Run spaCy NLP on the (possibly translated) text
    doc = nlp(translated)
    t3 = time.perf_counter()

    # 4. Token‑level annotations
    token_data = annotate_tokens(doc)
    t4 = time.perf_counter()

    # 5. Entity‑level annotations
    entity_data = annotate_entities(doc)
    t5 = time.perf_counter()

    # 6. Date period detection
    date_periods = detect_date_periods(doc)

    # 7. Abbreviation detection
    abbreviations = detect_abbreviations(doc)

    # 8. Quotation detection (uses original text)
    quotations = detect_quotations(text)
    t6 = time.perf_counter()

    timings = {
        "language_detection": t1 - t0,
        "translation": t2 - t1,
        "spacy": t3 - t2,
        "token_annotation": t4 - t3,
        "entity_enrichment": t5 - t4,
        "patterns": t6 - t5,
        "total": t6 - t0,
    }

    # 9. Return everything in a structured dictionary
    return {
        "language": lang,
        "translated_text": translated,
        #"tokens": token_data,
        "entities": entity_data,
        "date_periods": date_periods,
        "abbreviations": abbreviations,
        "quotations": quotations,
        "timings": timings,
    }

# Simple in-memory cache for background knowledge lookups

CACHE = {}

def cached_background_lookup(query, fetch_fn):
    """
    Returns cached background info if available.
    Otherwise calls fetch_fn(query), stores the result, and returns it.
    """
    if query in CACHE:
        return CACHE[query]

    result = fetch_fn(query)
    CACHE[query] = result
    return result

import json
from bs4 import BeautifulSoup


def extract_json_objects_containing_key(html: str, key: str) -> list[dict]:
    """Extract JSON objects from script tags that contain the specified key."""
    soup = BeautifulSoup(html, "html.parser")
    found = []

    for script in soup.find_all("script", type="application/json"):
        content = script.string
        if not content:
            continue
        try:
            parsed = json.loads(content)
            if json_contains_key(parsed, key):
                found.append(parsed)
        except json.JSONDecodeError:
            pass

    # Deduplicate by string representation
    seen = set()
    unique = []
    for obj in found:
        s = json.dumps(obj, sort_keys=True)
        if s not in seen:
            seen.add(s)
            unique.append(obj)
    return unique


def json_contains_key(obj, key: str) -> bool:
    """Recursively check if a python object (parsed json) contains the string key anywhere."""
    if isinstance(obj, dict):
        if key in obj:
            return True
        return any(json_contains_key(v, key) for v in obj.values())
    if isinstance(obj, list):
        return any(json_contains_key(item, key) for item in obj)
    return False


def deep_find(obj, key: str):
    """Recursively find the first occurrence of a key in nested dict/list."""
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            result = deep_find(v, key)
            if result is not None:
                return result
    elif isinstance(obj, list):
        for item in obj:
            result = deep_find(item, key)
            if result is not None:
                return result
    return None

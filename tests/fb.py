#!/usr/bin/env python3
"""
extract_fb_json.py

Usage:
  # fetch from URL (will use same headers you used in curl)
  python extract_fb_json.py --url "https://www.facebook.com/csgocasescom/"

  # or extract from a local downloaded HTML file (useful for offline testing)
  python extract_fb_json.py --file ./response.html

Output:
  - extracted.json : the JSON object (pretty) that contains the requested key
"""

import argparse
import json
import sys
from typing import List

import requests
from bs4 import BeautifulSoup


DEFAULT_HEADERS = {
    "accept": "text/xhtml,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "sec-fetch-mode": "navigate",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
}


def fetch_url(url: str, headers: dict) -> str:
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.text


def extract_json_objects_containing_key(html: str, key: str) -> List[dict]:
    """Extract JSON objects from script tags that contain the specified key."""
    soup = BeautifulSoup(html, "html.parser")
    found = []

    for script in soup.find_all("script", type="application/json"):
        content = script.string
        if not content:
            continue
        try:
            parsed = json.loads(content)
            if _json_contains_key(parsed, key):
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


def _json_contains_key(obj, key: str) -> bool:
    """Recursively check if a python object (parsed json) contains the string key anywhere."""
    if isinstance(obj, dict):
        if key in obj:
            return True
        return any(_json_contains_key(v, key) for v in obj.values())
    if isinstance(obj, list):
        return any(_json_contains_key(item, key) for item in obj)
    return False


def _deep_find(obj, key: str):
    """Recursively find the first occurrence of a key in nested dict/list."""
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            result = _deep_find(v, key)
            if result is not None:
                return result
    elif isinstance(obj, list):
        for item in obj:
            result = _deep_find(item, key)
            if result is not None:
                return result
    return None


def simplify_and_save(obj: dict, outpath: str):
    """Save pretty JSON and print a short summary."""
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)

    print("Saved extracted JSON to:", outpath)

    # Try to extract summary from timeline_list_feed_units
    tlu = _deep_find(obj, "timeline_list_feed_units")
    if not tlu or not isinstance(tlu, dict):
        return

    edges = tlu.get("edges", [])
    if not edges:
        return

    summary = {"edges_count": len(edges)}

    first_node = edges[0].get("node", {})
    if node_id := first_node.get("id"):
        summary["first_node_id"] = node_id

    message = _deep_find(first_node, "message")
    if message:
        text = message if isinstance(message, str) else message.get("text", "")
        if text:
            summary["first_message_excerpt"] = text[:200].replace("\n", " ")

    print("Summary:", json.dumps(summary, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="URL to fetch (optional)")
    parser.add_argument("--file", help="Local HTML file to read (optional)")
    parser.add_argument("--key", default="timeline_list_feed_units", help="JSON key to search for (default: timeline_list_feed_units)")
    parser.add_argument("--out", default="extracted.json", help="Output filename (default: extracted.json)")
    args = parser.parse_args()

    if not args.url and not args.file:
        parser.error("Provide either --url or --file to read the HTML from.")

    html = ""
    if args.file:
        with open(args.file, "r", encoding="utf-8", errors="ignore") as f:
            html = f.read()
    else:
        html = fetch_url(args.url, DEFAULT_HEADERS)

    matches = extract_json_objects_containing_key(html, args.key)
    if not matches:
        print(f"No JSON object containing key '{args.key}' found in the page.")
        # Try a fallback: save a small slice for manual inspection
        snippet = html[:20000]
        with open("page_snippet.html", "w", encoding="utf-8") as f:
            f.write(snippet)
        print("Wrote page_snippet.html (first 20KB) for inspection.")
        sys.exit(2)

    # pick the first match (you can change logic if you prefer the largest or nth match)
    chosen = matches[0]
    simplify_and_save(chosen, args.out)


if __name__ == "__main__":
    main()

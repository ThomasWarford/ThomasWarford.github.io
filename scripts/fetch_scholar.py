#!/usr/bin/env python3
"""
Fetch publications from Google Scholar and ORCID and update _data/publications.yml.

Usage:
    python3 scripts/fetch_scholar.py
"""

import json
import os
import re
import sys
import urllib.request

SCHOLAR_USER_ID = "zTiHyRcAAAAJ"
ORCID_ID = "0009-0000-6039-2083"
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "_data", "publications.yml")

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def fetch_orcid_dois(orcid_id):
    """Fetch known DOIs from ORCID public API."""
    url = f"https://pub.orcid.org/v3.0/{orcid_id}/works"
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT})
    dois = {}
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for group in data.get("group", []):
                for summary in group.get("work-summary", []):
                    title = summary.get("title", {}).get("title", {}).get("value", "").strip().lower()
                    url_val = summary.get("url", {}).get("value", "")
                    if title and url_val:
                        dois[title] = url_val
    except Exception as e:
        print(f"[Warning] Could not fetch ORCID DOIs: {e}", file=sys.stderr)
    return dois


def fetch_scholar_publications(user_id):
    """Scrape publication entries from Google Scholar profile."""
    url = f"https://scholar.google.co.uk/citations?user={user_id}&hl=en&cstart=0&pagesize=100"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"[Error] Failed to fetch Google Scholar profile: {e}", file=sys.stderr)
        return []

    rows = re.findall(r'<tr class="gsc_a_tr">(.*?)</tr>', html, re.DOTALL)
    publications = []

    for r in rows:
        title_m = re.search(r'<a[^>]*class="gsc_a_at"[^>]*>(.*?)</a>', r)
        title = title_m.group(1).strip() if title_m else ""
        if not title:
            continue

        href_m = re.search(r'<a[^>]*href="([^"]*)"[^>]*class="gsc_a_at"', r)
        if href_m:
            scholar_url = "https://scholar.google.co.uk" + href_m.group(1).replace("&amp;", "&")
        else:
            scholar_url = ""

        grays = re.findall(r'<div class="gs_gray">(.*?)</div>', r)
        authors = grays[0].strip() if len(grays) > 0 else ""
        raw_venue = grays[1].strip() if len(grays) > 1 else ""
        venue = re.sub(r"<[^>]*>", "", raw_venue).strip()
        # Clean trailing comma or year from venue string if present
        venue = re.sub(r",\s*\d{4}\s*$", "", venue).strip()

        year_m = re.search(r'<span class="gsc_a_h[^"]*">(\d+)</span>', r)
        year = int(year_m.group(1)) if year_m else None

        cites_m = re.search(r'class="gsc_a_ac[^"]*">(\d+)<', r)
        citations = int(cites_m.group(1)) if cites_m else 0

        pub = {
            "title": title,
            "authors": authors,
            "venue": venue or "Preprint",
            "year": year,
            "doi": None,
            "scholar_url": scholar_url,
        }
        publications.append(pub)

    return publications


def dump_yaml(data):
    """Clean YAML serialization."""
    try:
        import yaml
        return yaml.dump(data, sort_keys=False, allow_unicode=True)
    except ImportError:
        lines = []
        for item in data:
            doi_val = f'"{item["doi"]}"' if item.get("doi") else "null"
            scholar_val = f'"{item["scholar_url"]}"' if item.get("scholar_url") else "null"
            lines.append(f'- title: "{item["title"]}"')
            lines.append(f'  authors: "{item["authors"]}"')
            lines.append(f'  venue: "{item["venue"]}"')
            lines.append(f'  year: {item["year"] if item.get("year") else "null"}')
            lines.append(f'  doi: {doi_val}')
            lines.append(f'  scholar_url: {scholar_val}')
            lines.append("")
        return "\n".join(lines)


def load_existing():
    """Load existing publications to preserve custom links (e.g. doi, code, pdf)."""
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        import yaml
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or []
            return {p.get("title", "").strip().lower(): p for p in data if isinstance(p, dict)}
    except Exception:
        return {}


def main():
    print(f"Fetching publications for Scholar ID: {SCHOLAR_USER_ID}...")
    scholar_pubs = fetch_scholar_publications(SCHOLAR_USER_ID)
    print(f"Found {len(scholar_pubs)} publications on Google Scholar.")

    print(f"Fetching ORCID metadata for {ORCID_ID}...")
    orcid_dois = fetch_orcid_dois(ORCID_ID)

    existing = load_existing()

    merged = []
    for pub in scholar_pubs:
        key = pub["title"].strip().lower()

        # Check ORCID DOIs
        if key in orcid_dois:
            pub["doi"] = orcid_dois[key]

        # Preserve custom existing fields
        if key in existing:
            old = existing[key]
            for field in ["doi", "code", "arxiv", "pdf", "abstract"]:
                if old.get(field) and not pub.get(field):
                    pub[field] = old[field]

        merged.append(pub)

    # Preserve existing manual order if present; place any brand new items at top
    existing_order = list(existing.keys())

    def sort_key(p):
        key = p["title"].strip().lower()
        if key in existing_order:
            return (1, -existing_order.index(key))
        y = p.get("year")
        return (2, y if y is not None else 0)

    merged.sort(key=sort_key, reverse=True)

    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    yaml_text = dump_yaml(merged)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write(yaml_text)

    print(f"Updated {DATA_FILE} successfully with {len(merged)} publications.")


if __name__ == "__main__":
    main()

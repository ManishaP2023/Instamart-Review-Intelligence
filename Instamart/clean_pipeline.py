"""
Reads output/combined_reviews.json, cleans it, and writes
output/cleaned_reviews.(json|csv).

What "clean" means here:
- strip whitespace / normalize review text
- convert all dates to a standard ISO format (YYYY-MM-DD)
- coerce ratings to a whole number 1-5 (or None if missing/invalid)
- drop rows with no usable text
- de-duplicate exact matches (platform + author + text + date)
- de-duplicate Reddit posts that surfaced under more than one search query
- add a stable record_id, word_count, and year_month column

This step only processes files you already have in output/ — it does not
go fetch anything new. Re-run it any time after a new scrape.
"""

import csv
import json
import os
import re
from datetime import datetime

INPUT_PATH = os.path.join("output", "combined_reviews.json")
OUTPUT_JSON = os.path.join("output", "cleaned_reviews.json")
OUTPUT_CSV = os.path.join("output", "cleaned_reviews.csv")

FIELDNAMES = [
    "record_id", "platform", "author", "rating", "title", "text", "word_count",
    "date", "year_month", "country", "subreddit", "app_version", "thumbs_up",
    "reply_text", "url",
]


def clean_text(text):
    if not text:
        return None
    text = str(text).strip()
    text = re.sub(r"\s+", " ", text)
    return text or None


def parse_date(raw):
    if not raw:
        return None
    raw = str(raw).strip()

    # Try a handful of formats seen across the three sources, in order.
    formats = [
        "%Y-%m-%d %H:%M:%S",       # Play Store
        "%Y-%m-%dT%H:%M:%S%z",     # App Store / ISO
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    # Fall back: some Reddit timestamps come through as unix epoch (int/float)
    try:
        return datetime.utcfromtimestamp(float(raw)).strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        pass

    return None  # couldn't parse — leave blank rather than guess


def clean_rating(raw):
    if raw is None or raw == "":
        return None
    try:
        val = round(float(raw))
    except (ValueError, TypeError):
        return None
    if 1 <= val <= 5:
        return val
    return None


def load_combined():
    if not os.path.exists(INPUT_PATH):
        raise FileNotFoundError(
            f"{INPUT_PATH} not found — run `python main.py` first to scrape and combine raw data."
        )
    with open(INPUT_PATH, encoding="utf-8") as f:
        return json.load(f)


def clean_records(records):
    cleaned = []
    for r in records:
        text = clean_text(r.get("text"))
        title = clean_text(r.get("title"))

        if not text and not title:
            continue  # nothing usable — drop it

        date = parse_date(r.get("date"))
        cleaned.append({
            "platform": r.get("platform"),
            "author": clean_text(r.get("author")),
            "rating": clean_rating(r.get("rating")),
            "title": title,
            "text": text,
            "word_count": len(text.split()) if text else 0,
            "date": date,
            "year_month": date[:7] if date else None,
            "country": r.get("country"),
            "subreddit": r.get("subreddit"),
            "app_version": r.get("app_version"),
            "thumbs_up": r.get("thumbs_up"),
            "reply_text": clean_text(r.get("reply_text")),
            "url": r.get("url"),
        })
    return cleaned


def dedupe(records):
    seen_exact = set()
    seen_reddit_posts = set()
    deduped = []

    for r in records:
        exact_key = (r["platform"], r["author"], r["text"], r["date"])
        if exact_key in seen_exact:
            continue

        if r["platform"] == "reddit" and r["title"]:
            # Same post surfacing under multiple search queries — key on
            # author+title+date since Reddit post ids aren't always present.
            post_key = (r["author"], r["title"], r["date"])
            if post_key in seen_reddit_posts:
                continue
            seen_reddit_posts.add(post_key)

        seen_exact.add(exact_key)
        deduped.append(r)

    return deduped


def add_record_ids(records):
    for i, r in enumerate(records, start=1):
        r_with_id = {"record_id": f"IM-{i:06d}"}
        r_with_id.update(r)
        records[i - 1] = r_with_id
    return records


def write_json(records, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def write_csv(records, path):
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(records)


def main():
    raw = load_combined()
    print(f"Loaded {len(raw)} combined records.")

    cleaned = clean_records(raw)
    print(f"{len(cleaned)} records after dropping empty/blank entries.")

    deduped = dedupe(cleaned)
    print(f"{len(deduped)} records after de-duplication.")

    final = add_record_ids(deduped)

    write_json(final, OUTPUT_JSON)
    write_csv(final, OUTPUT_CSV)

    print(f"\nWrote {OUTPUT_JSON} and {OUTPUT_CSV}")
    print("Next: open dashboard.html in your browser and load the cleaned CSV/JSON.")


if __name__ == "__main__":
    main()

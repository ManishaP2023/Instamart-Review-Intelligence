"""
Runs all three scrapers (Play Store, App Store, Reddit) and writes raw +
combined output into output/.

Usage:
    python main.py
    python main.py --skip-apple
    python main.py --skip-reddit
    python main.py --skip-apple --skip-reddit   # Play Store only
"""

import argparse
import csv
import json
import os

from dotenv import load_dotenv

from scrapers.play_store import scrape_play_store
from scrapers.app_store import scrape_app_store
from scrapers.reddit_scraper import scrape_reddit
from utils.combine import combine_all

OUTPUT_DIR = "output"


def write_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def write_csv(data, path):
    if not data:
        # still create an empty file so downstream steps don't choke on a missing path
        open(path, "w").close()
        return
    fieldnames = sorted({key for row in data for key in row.keys()})
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-play", action="store_true", help="Skip Google Play Store scraping")
    parser.add_argument("--skip-apple", action="store_true", help="Skip Apple App Store scraping")
    parser.add_argument("--skip-reddit", action="store_true", help="Skip Reddit scraping")
    args = parser.parse_args()

    load_dotenv()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    play_raw, app_raw, reddit_raw = [], [], []
    failed_sources = []

    # Each source is wrapped separately so that one source failing outright
    # (network issue, quota exhausted, etc.) doesn't stop the others from
    # being scraped and doesn't prevent combined_reviews.(json|csv) from
    # being written at the end — that file is what clean_pipeline.py needs,
    # and it should always get written if ANY source succeeded.
    if not args.skip_play:
        try:
            play_raw = scrape_play_store()
            write_json(play_raw, os.path.join(OUTPUT_DIR, "play_store_raw.json"))
            write_csv(play_raw, os.path.join(OUTPUT_DIR, "play_store_raw.csv"))
        except Exception as e:
            print(f"[Play Store] Failed: {e}")
            failed_sources.append("play_store")

    if not args.skip_apple:
        try:
            app_raw = scrape_app_store()
            write_json(app_raw, os.path.join(OUTPUT_DIR, "app_store_raw.json"))
            write_csv(app_raw, os.path.join(OUTPUT_DIR, "app_store_raw.csv"))
        except Exception as e:
            print(f"[App Store] Failed: {e}")
            failed_sources.append("app_store")

    if not args.skip_reddit:
        try:
            reddit_raw = scrape_reddit()
            write_json(reddit_raw, os.path.join(OUTPUT_DIR, "reddit_raw.json"))
            write_csv(reddit_raw, os.path.join(OUTPUT_DIR, "reddit_raw.csv"))
        except Exception as e:
            print(f"[Reddit] Failed: {e}")
            failed_sources.append("reddit")

    if failed_sources:
        print(f"\nNote: these sources failed and contributed 0 rows: {', '.join(failed_sources)}")
        print("The other sources still ran — see errors above for what went wrong.")

    combined = combine_all(play_raw, app_raw, reddit_raw)
    write_json(combined, os.path.join(OUTPUT_DIR, "combined_reviews.json"))
    write_csv(combined, os.path.join(OUTPUT_DIR, "combined_reviews.csv"))

    print(f"\nDone. {len(combined)} combined records written to {OUTPUT_DIR}/combined_reviews.(json|csv)")
    print("Next: run `python clean_pipeline.py` to clean and dedupe.")


if __name__ == "__main__":
    main()

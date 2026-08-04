"""
Apple App Store reviews for Instamart, via Apple's public customer-reviews
RSS/JSON feed. No API key needed.

Note: Apple's feed only exposes a limited, recent window of reviews per
country (roughly the most recent ~500, in pages of 50), regardless of how
high APP_STORE_HOW_MANY is set. That's a limit of Apple's feed, not this
script. Full historical review data would require App Store Connect API
access, which only the app's own developer (Swiggy/Bundl Technologies, not
us) can get.
"""

import time
import requests

import config

BASE_URL = "https://itunes.apple.com/{country}/rss/customerreviews/id={app_id}/sortBy=mostRecent/page={page}/json"


def scrape_app_store():
    all_reviews = []

    for country in config.APP_STORE_COUNTRIES:
        print(f"[App Store] Fetching reviews for country={country} ...")

        country_reviews = []
        page = 1
        max_page = 10  # Apple's feed caps out around page 10 (~50 reviews/page)

        while len(country_reviews) < config.APP_STORE_HOW_MANY and page <= max_page:
            url = BASE_URL.format(country=country, app_id=config.APP_STORE_APP_ID, page=page)
            resp = requests.get(url, timeout=15)

            if resp.status_code != 200:
                print(f"[App Store] Request failed for {country} page {page}: HTTP {resp.status_code}")
                break

            try:
                data = resp.json()
            except ValueError:
                break

            entries = data.get("feed", {}).get("entry", [])
            # The first entry on page 1 is app metadata, not a review, when present
            entries = [e for e in entries if "im:rating" in e]

            if not entries:
                break  # no more pages

            for e in entries:
                country_reviews.append({
                    "id": e.get("id", {}).get("label"),
                    "author": e.get("author", {}).get("name", {}).get("label"),
                    "rating": e.get("im:rating", {}).get("label"),
                    "title": e.get("title", {}).get("label"),
                    "text": e.get("content", {}).get("label"),
                    "date": e.get("updated", {}).get("label"),
                    "app_version": e.get("im:version", {}).get("label"),
                    "_country": country,
                })

            page += 1
            time.sleep(1)

        country_reviews = country_reviews[:config.APP_STORE_HOW_MANY]
        print(f"[App Store] Got {len(country_reviews)} reviews for {country}")
        all_reviews.extend(country_reviews)

    return all_reviews

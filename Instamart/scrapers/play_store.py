"""
Google Play Store reviews for Instamart, via the free `google-play-scraper`
library. No API key needed.
"""

import time
from google_play_scraper import reviews, Sort

import config


def scrape_play_store():
    """Fetch Play Store reviews across all configured countries.

    Returns a list of raw dicts (one per review), each tagged with the
    country it was pulled from.
    """
    all_reviews = []

    for country in config.PLAY_STORE_COUNTRIES:
        print(f"[Play Store] Fetching reviews for country={country} ...")

        country_reviews = []
        continuation_token = None
        batch_size = 200  # fetched in batches to avoid overwhelming Google's servers

        while len(country_reviews) < config.PLAY_STORE_HOW_MANY:
            remaining = config.PLAY_STORE_HOW_MANY - len(country_reviews)
            result, continuation_token = reviews(
                config.PLAY_STORE_APP_ID,
                lang=config.PLAY_STORE_LANG,
                country=country,
                sort=Sort.NEWEST,
                count=min(batch_size, remaining),
                continuation_token=continuation_token,
            )

            if not result:
                break  # ran out of reviews for this country

            for r in result:
                r["_country"] = country
            country_reviews.extend(result)

            if continuation_token is None:
                break  # library signals no more pages

            time.sleep(1)  # short pause between batches, be polite to Google's servers

        print(f"[Play Store] Got {len(country_reviews)} reviews for {country}")
        all_reviews.extend(country_reviews)

    return all_reviews

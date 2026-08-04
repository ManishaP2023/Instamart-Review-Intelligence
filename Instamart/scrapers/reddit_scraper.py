"""
Reddit posts/comments mentioning Instamart, via Apify's Reddit scraper
actor. Requires an APIFY_TOKEN (see .env.example).

Root-cause fix (apify_client v3.x):
  - v3 call() returns a Pydantic Run model, not a dict.
  - The Run model uses snake_case attributes (default_dataset_id).
  - call() can return None if the actor run fails or times out — the
    original code crashed with TypeError: 'NoneType' is not subscriptable
    because it tried run["defaultDatasetId"] without a None guard.
  - v3 also exposes run.dataset() directly on the RunClient, which is
    cleaner than fetching by dataset ID — we use that as the primary path.
"""

import os
from apify_client import ApifyClient

import config

ACTOR_ID = "trudax/reddit-scraper-lite"


def scrape_reddit():
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        print("[Reddit] No APIFY_TOKEN found in environment — skipping Reddit scrape.")
        return []

    client = ApifyClient(token)
    all_items = []

    for query in config.REDDIT_QUERIES:
        print(f"[Reddit] Searching for: {query!r} ...")

        run_input = {
            "searches": [query],
            "type": "posts",
            "sort": "relevance",
            "includeComments": config.REDDIT_COMMENTS_MODE != "none",
            "maxItems": config.REDDIT_MAX_ITEMS_PER_QUERY,
        }
        if config.REDDIT_COMMENTS_MODE == "high_engagement":
            run_input["maxComments"] = 20

        # FIX 1: call() in apify_client v3 returns Run | None.
        # Always guard against None (actor failed / timed out).
        run = client.actor(ACTOR_ID).call(run_input=run_input)

        if run is None:
            print(f"[Reddit] Actor run returned None for query {query!r} — "
                  "the run may have failed or timed out. Skipping.")
            continue

        # FIX 2: Extract dataset_id correctly for both v2 (dict) and v3 (Run model).
        # v3 Run is a Pydantic model with snake_case attributes.
        # v2 Run was a plain dict with camelCase keys.
        dataset_id = None
        if isinstance(run, dict):
            # apify_client v2 path (kept for backwards compat)
            dataset_id = run.get("defaultDatasetId")
        else:
            # apify_client v3 path — attribute is snake_case
            dataset_id = getattr(run, "default_dataset_id", None)

        if not dataset_id:
            print(f"[Reddit] Could not find dataset id for query {query!r} — skipping.")
            continue

        # FIX 3: Use client.dataset(id).iterate_items() — works in both v2 and v3.
        # (v3 also supports run.dataset().iterate_items() but that requires
        # holding a RunClient reference, which call() doesn't return directly.)
        query_items = []
        try:
            for item in client.dataset(dataset_id).iterate_items():
                item["_search_query"] = query
                query_items.append(item)
        except Exception as e:
            print(f"[Reddit] Error iterating dataset for query {query!r}: {e}")
            continue

        print(f"[Reddit] Got {len(query_items)} items for {query!r}")
        all_items.extend(query_items)

    return all_items

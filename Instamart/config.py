"""
All app-specific settings live here. Change these to point the scraper
at a different app, market, or scrape volume.
"""

# ---------------------------------------------------------------------------
# Google Play Store
# ---------------------------------------------------------------------------
PLAY_STORE_APP_ID = "in.swiggy.android.instamart"   # Instamart: Groceries & more

# Instamart only operates in India, so unlike a global app there's little
# value in pulling other-country storefronts — reviews outside "in" are
# usually just diaspora users or empty. Add more codes only if you have a
# reason to (e.g. testing a country the app has expanded into).
PLAY_STORE_COUNTRIES = ["in"]

# google-play-scraper needs a language too. Kept in English on purpose:
# most Instamart reviews are written in English even by Indian users, but
# a meaningful slice are in Hindi/other regional languages using Latin
# script or native script. This scraper does NOT translate or do
# language-detection — you'll only reliably capture English-language
# reviews. Treat that as a known gap, not a bug.
PLAY_STORE_LANG = "en"

# Reviews to fetch per (app, country). Keep this low while testing —
# bump it up for a full run.
PLAY_STORE_HOW_MANY = 100

# ---------------------------------------------------------------------------
# Apple App Store
# ---------------------------------------------------------------------------
# Instamart's standalone iOS app ("Instamart: Groceries & more"). Note the
# combined "Swiggy: Food Instamart Dineout" app (id989540920) also carries
# Instamart-relevant reviews mixed with food-delivery ones — that's a
# separate, noisier source and is intentionally NOT included here to avoid
# polluting the dataset with reviews about food orders, not groceries.
APP_STORE_APP_ID = "6738619733"

# Same reasoning as Play Store: India-only app, India-only storefront.
APP_STORE_COUNTRIES = ["in"]

APP_STORE_HOW_MANY = 100

# ---------------------------------------------------------------------------
# Reddit (via Apify)
# ---------------------------------------------------------------------------
# Multiple phrasings, not just "Instamart" — the name alone is also used by
# unrelated apps/brands (e.g. InstaMandi-style grocery clones, "instamart"
# as a generic term). Being specific about "Swiggy Instamart" cuts down on
# false positives.
REDDIT_QUERIES = [
    "Swiggy Instamart",
    "Instamart delivery",
    "Instamart app",
    "Instamart 10 minute grocery",
]

# "none" = fastest/cheapest (posts only)
# "high_engagement" = comments only on the most popular posts
# "all" = every comment on every post (slow, uses much more Apify usage)
REDDIT_COMMENTS_MODE = "high_engagement"

# Safety valve so a popular query doesn't run away with your Apify usage.
# None = no limit (stops only when a search term runs out of results).
REDDIT_MAX_ITEMS_PER_QUERY = 100

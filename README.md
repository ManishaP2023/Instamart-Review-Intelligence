# Instamart-Review-Intelligence

A lightweight research tool that scrapes and analyses user reviews for Swiggy Instamart across Google Play, the App Store, and Reddit — then visualises them in an offline PM dashboard.

Built as part of a product case study on quick-commerce category expansion.

---

## What's in this repo

| File | What it does |
|---|---|
| `dashboard.html` | Offline PM dashboard — open in any browser, no server needed |
| `combined_reviews.json` | Pre-scraped review dataset ready to load |
| `Instamart-RS/` | Python scraper that generated the dataset |

---

## Viewing the dashboard

1. Open the [live dashboard →](https://YOUR-USERNAME.github.io/YOUR-REPO-NAME/dashboard.html)
2. Click **Load JSON** and select `combined_reviews.json`, or click **Load sample data** to explore with placeholder reviews
3. Use the sidebar filters and four tabs to explore themes, sentiment, and PM insights

No login, no server, no data leaves your browser.

---

## Running the scraper yourself

**Requirements:** Python 3.10+, an [Apify](https://apify.com) account (free tier works)

```bash
cd Instamart-RS
pip install -r requirements.txt
cp .env.example .env          # add your APIFY_TOKEN
python main.py
python clean_pipeline.py      # dedupe and clean
```

Output lands in `Instamart-RS/output/`. Swap `combined_reviews.json` in the root with your fresh file and reload the dashboard.

---

## Scraper flags

```bash
python main.py --skip-apple    # Play Store + Reddit only
python main.py --skip-reddit   # Play Store + App Store only
```

---

*For questions or feedback, open an issue.*

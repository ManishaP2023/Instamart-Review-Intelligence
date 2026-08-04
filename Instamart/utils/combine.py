"""
Normalizes raw Play Store / App Store / Reddit records into one shared
schema so they can be analyzed side by side.

Shared columns:
platform, id, author, rating, title, text, date, thumbs_up, app_version,
reply_text, url
"""


def combine_play_store(raw):
    out = []
    for r in raw:
        out.append({
            "platform": "play_store",
            "id": r.get("reviewId"),
            "author": r.get("userName"),
            "rating": r.get("score"),
            "title": None,  # Play Store reviews don't have titles
            "text": r.get("content"),
            "date": str(r.get("at")) if r.get("at") else None,
            "thumbs_up": r.get("thumbsUpCount"),
            "app_version": r.get("reviewCreatedVersion"),
            "reply_text": r.get("replyContent"),
            "url": None,
            "country": r.get("_country"),
        })
    return out


def combine_app_store(raw):
    out = []
    for r in raw:
        out.append({
            "platform": "app_store",
            "id": r.get("id"),
            "author": r.get("author"),
            "rating": r.get("rating"),
            "title": r.get("title"),
            "text": r.get("text"),
            "date": r.get("date"),
            "thumbs_up": None,  # App Store reviews don't expose helpfulness counts
            "app_version": r.get("app_version"),
            "reply_text": None,
            "url": None,
            "country": r.get("_country"),
        })
    return out


def combine_reddit(raw):
    out = []
    for r in raw:
        # Posts have a "title" field; comments generally don't. This is the
        # heuristic the combined file uses to tell them apart — it's a
        # reasonable shortcut, not a guarantee.
        title = r.get("title")
        out.append({
            "platform": "reddit",
            "id": r.get("id"),
            "author": r.get("username") or r.get("author"),
            "rating": None,  # Reddit has no star ratings
            "title": title,
            "text": r.get("body") or r.get("text") or r.get("selftext"),
            "date": r.get("createdAt") or r.get("date"),
            "thumbs_up": r.get("upVotes") or r.get("score"),  # upvote score stands in for "thumbs up"
            "app_version": None,
            "reply_text": None,
            "url": r.get("url"),
            "country": None,  # Reddit doesn't map cleanly to app-store countries
            "subreddit": r.get("communityName") or r.get("subreddit"),
        })
    return out


def combine_all(play_raw, app_raw, reddit_raw):
    combined = []
    combined.extend(combine_play_store(play_raw))
    combined.extend(combine_app_store(app_raw))
    combined.extend(combine_reddit(reddit_raw))
    return combined

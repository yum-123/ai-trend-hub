"""Zenn の RSS フィードから記事を取得するフェッチャー"""
import feedparser


ZENN_FEED_URL = "https://zenn.dev/feed"


def fetch(keywords: list[str], feed_limit: int = 100) -> list[dict]:
    """Zenn のトレンドフィードを取得し、キーワードにマッチする記事を返す。

    Returns:
        list of dict with keys: title, url, tags, likes, published_at, source
    """
    feed = feedparser.parse(ZENN_FEED_URL)
    articles = []
    keywords_lower = [kw.lower() for kw in keywords]

    for entry in feed.entries[:feed_limit]:
        title_lower = entry.get("title", "").lower()
        summary_lower = entry.get("summary", "").lower()
        text = title_lower + " " + summary_lower

        matched = any(kw in text for kw in keywords_lower)
        if not matched:
            continue

        published = entry.get("published", "")[:10] if entry.get("published") else ""

        articles.append({
            "title": entry.get("title", ""),
            "url": entry.get("link", ""),
            "tags": [],
            "likes": 0,
            "published_at": published,
            "source": "Zenn",
        })

    return articles

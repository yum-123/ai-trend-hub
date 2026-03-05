"""Reddit から記事を取得するフェッチャー (認証不要・JSON API 使用)"""
import datetime
import time
import requests


SEARCH_URL = "https://www.reddit.com/search.json"
SUBREDDIT_URL = "https://www.reddit.com/r/{subreddit}/hot.json"

DEFAULT_SUBREDDITS = [
    "MachineLearning",
    "artificial",
    "LocalLLaMA",
    "singularity",
    "ClaudeAI",
    "ChatGPT",
    "OpenAI",
]

HEADERS = {"User-Agent": "ai-trend-hub/1.0"}


def fetch(keywords: list[str], per_keyword: int = 5, subreddits: list[str] | None = None) -> list[dict]:
    """Reddit をキーワード検索し、記事リストを返す。

    Returns:
        list of dict with keys: title, url, tags, likes, published_at, source
    """
    seen_ids = set()
    articles = []

    for keyword in keywords:
        try:
            resp = requests.get(
                SEARCH_URL,
                params={
                    "q": keyword,
                    "sort": "relevance",
                    "t": "week",
                    "limit": per_keyword,
                    "restrict_sr": False,
                },
                headers=HEADERS,
                timeout=10,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"[Reddit] '{keyword}' の取得失敗: {e}")
            continue

        for post in resp.json().get("data", {}).get("children", []):
            d = post["data"]
            if d["id"] in seen_ids:
                continue
            seen_ids.add(d["id"])

            published = datetime.date.fromtimestamp(d["created_utc"]).isoformat()
            articles.append({
                "title": d["title"],
                "url": f"https://www.reddit.com{d['permalink']}",
                "tags": [d["subreddit"]],
                "likes": d["score"],
                "published_at": published,
                "source": "Reddit",
            })

        time.sleep(1)  # Reddit のレート制限対策

    return articles

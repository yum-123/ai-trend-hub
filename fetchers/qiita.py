"""Qiita API v2 から記事を取得するフェッチャー"""
import requests


QIITA_API_BASE = "https://qiita.com/api/v2"


def fetch(keywords: list[str], per_keyword: int = 10) -> list[dict]:
    """キーワードリストで Qiita を検索し、記事リストを返す。

    Returns:
        list of dict with keys: title, url, tags, likes, published_at, source
    """
    seen_ids = set()
    articles = []

    for keyword in keywords:
        try:
            resp = requests.get(
                f"{QIITA_API_BASE}/items",
                params={"query": keyword, "per_page": per_keyword},
                timeout=10,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"[Qiita] '{keyword}' の取得失敗: {e}")
            continue

        for item in resp.json():
            if item["id"] in seen_ids:
                continue
            seen_ids.add(item["id"])
            articles.append({
                "title": item["title"],
                "url": item["url"],
                "tags": [t["name"] for t in item["tags"]],
                "likes": item["likes_count"],
                "published_at": item["created_at"][:10],
                "source": "Qiita",
            })

    return articles

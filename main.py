"""AI トレンドハブ - メインスクリプト

使い方:
    python main.py
"""
import datetime
import json
import pathlib
import yaml
from dotenv import load_dotenv

from fetchers import qiita, zenn, reddit
import scorer

load_dotenv(pathlib.Path.home() / ".config" / "ai-trend-hub" / ".env")


def load_config(path: str = "config.yaml") -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_markdown(articles: list[dict], date: str, keywords: list[str], scored: bool) -> str:
    lines = [
        f"# AI トレンド記事 - {date}",
        "",
        f"**キーワード:** {', '.join(keywords)}",
        f"**取得件数:** {len(articles)} 件",
        "",
        "---",
        "",
    ]

    # スコアリング済みの場合はスコア順フラット表示、そうでなければソース別
    if scored:
        lines.append("## 関連度順")
        lines.append("")
        for item in articles:
            score_label = f"⭐ {item['score']}/10" if "score" in item else ""
            tags = " ".join(f"`{t}`" for t in item["tags"]) if item["tags"] else ""
            likes = f"👍 {item['likes']}" if item["likes"] else ""
            meta = " | ".join(filter(None, [item["published_at"], score_label, item["source"], likes, tags]))
            lines.append(f"- [{item['title']}]({item['url']})")
            if meta:
                lines.append(f"  {meta}")
        lines.append("")
    else:
        by_source: dict[str, list[dict]] = {}
        for article in articles:
            by_source.setdefault(article["source"], []).append(article)

        for source, items in by_source.items():
            lines.append(f"## {source} ({len(items)} 件)")
            lines.append("")
            for item in items:
                tags = " ".join(f"`{t}`" for t in item["tags"]) if item["tags"] else ""
                likes = f"👍 {item['likes']}" if item["likes"] else ""
                meta = " | ".join(filter(None, [item["published_at"], likes, tags]))
                lines.append(f"- [{item['title']}]({item['url']})")
                if meta:
                    lines.append(f"  {meta}")
            lines.append("")

    return "\n".join(lines)


def main():
    config = load_config()
    keywords = config["keywords"]
    today = datetime.date.today().isoformat()

    all_articles: list[dict] = []

    if config["sources"]["qiita"]["enabled"]:
        print("Qiita を取得中...")
        items = qiita.fetch(keywords, config["sources"]["qiita"]["per_keyword"])
        print(f"  → {len(items)} 件取得")
        all_articles.extend(items)

    if config["sources"]["zenn"]["enabled"]:
        print("Zenn を取得中...")
        items = zenn.fetch(keywords, config["sources"]["zenn"]["feed_limit"])
        print(f"  → {len(items)} 件取得")
        all_articles.extend(items)

    if config["sources"]["reddit"]["enabled"]:
        print("Reddit を取得中...")
        reddit_conf = config["sources"]["reddit"]
        items = reddit.fetch(
            keywords,
            per_keyword=reddit_conf["per_keyword"],
            subreddits=reddit_conf.get("subreddits"),
        )
        print(f"  → {len(items)} 件取得")
        all_articles.extend(items)

    print(f"\nスコアリング中... ({len(all_articles)} 件)")
    filtered = scorer.score_articles(all_articles, keywords)
    is_scored = any("score" in a for a in filtered)

    output_dir = pathlib.Path(config["output"]["dir"])
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f"{today}.md"

    md = build_markdown(filtered, today, keywords, scored=is_scored)
    output_path.write_text(md, encoding="utf-8")

    json_path = output_dir / f"{today}.json"
    json_data = {"date": today, "keywords": keywords, "articles": filtered}
    json_path.write_text(json.dumps(json_data, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n完了！ {len(filtered)} 件を {output_path} と {json_path} に保存しました。")


if __name__ == "__main__":
    main()

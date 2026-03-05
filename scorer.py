"""Claude API を使って記事の関連度をスコアリングするモジュール"""
import json
import os
import anthropic


SCORE_THRESHOLD = 5  # これ未満の記事は除外


def score_articles(articles: list[dict], keywords: list[str]) -> list[dict]:
    """記事リストを Claude でスコアリングし、関連度順に並べて返す。

    - API 呼び出しは 1 回（全記事を一括送信）
    - SCORE_THRESHOLD 未満の記事は除外
    - score フィールドを追加して返す
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[Scorer] ANTHROPIC_API_KEY が未設定のためスキップします")
        return articles

    client = anthropic.Anthropic(api_key=api_key)

    # タイトル一覧をナンバリングして渡す
    numbered = "\n".join(f"{i}: {a['title']}" for i, a in enumerate(articles))
    interests = ", ".join(keywords)

    prompt = f"""以下は技術記事のタイトル一覧です。
私の興味: {interests}

各記事について、私の興味との関連度を 0〜10 の整数でスコアリングしてください。
- 10: 非常に関連が高い
- 5: ある程度関連がある
- 0: まったく関係ない

以下の JSON 形式のみで回答してください（説明不要）:
{{"scores": [スコアの配列（記事番号順）]}}

記事一覧:
{numbered}"""

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        text = message.content[0].text.strip()
        # コードブロック(```json ... ```)が含まれる場合に除去
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        result = json.loads(text.strip())
        scores = result["scores"]
    except Exception as e:
        print(f"[Scorer] スコアリング失敗: {e}")
        return articles

    # スコアを付与して閾値でフィルタリング
    scored = []
    for article, score in zip(articles, scores):
        if score >= SCORE_THRESHOLD:
            scored.append({**article, "score": score})

    # スコア降順で返す
    scored.sort(key=lambda a: a["score"], reverse=True)

    removed = len(articles) - len(scored)
    print(f"  → {len(scored)} 件が閾値以上（{removed} 件を除外）")
    return scored

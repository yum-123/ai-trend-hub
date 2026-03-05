"""AI トレンドハブ - Streamlit UI

起動方法:
    .venv/bin/streamlit run app.py
"""
import json
import pathlib

import streamlit as st

OUTPUT_DIR = pathlib.Path("output")

st.set_page_config(page_title="AI トレンドハブ", page_icon="🤖", layout="wide")
st.title("🤖 AI トレンドハブ")


def load_json_files() -> list[str]:
    if not OUTPUT_DIR.exists():
        return []
    return sorted(
        [p.stem for p in OUTPUT_DIR.glob("*.json")],
        reverse=True,
    )


def load_data(date: str) -> dict:
    path = OUTPUT_DIR / f"{date}.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


dates = load_json_files()

if not dates:
    st.warning("output/ に JSON ファイルがありません。まず `python main.py` を実行してください。")
    st.stop()

# --- サイドバー ---
with st.sidebar:
    st.header("フィルター")

    selected_date = st.selectbox("日付", dates)
    data = load_data(selected_date)
    all_articles = data.get("articles", [])

    all_sources = sorted({a["source"] for a in all_articles})
    selected_sources = st.multiselect("ソース", all_sources, default=all_sources)

    min_score = st.slider("最低スコア", min_value=0, max_value=10, value=5)

    st.markdown("---")
    st.caption(f"キーワード: {', '.join(data.get('keywords', []))}")

# --- フィルタリング ---
filtered = [
    a for a in all_articles
    if a["source"] in selected_sources and a.get("score", 0) >= min_score
]
excluded = len(all_articles) - len(filtered)

# --- サマリー ---
col1, col2, col3 = st.columns(3)
col1.metric("表示件数", len(filtered))
col2.metric("除外件数", excluded)
col3.metric("合計取得", len(all_articles))

st.divider()

# --- 記事カード ---
if not filtered:
    st.info("条件に一致する記事がありません。フィルターを緩めてください。")
else:
    for article in filtered:
        score = article.get("score")
        score_stars = "⭐" * score if score else ""
        tags_str = " ".join(f"`{t}`" for t in article.get("tags", []) if t)
        likes = article.get("likes") or 0

        with st.container(border=True):
            title_col, score_col = st.columns([5, 1])
            with title_col:
                st.markdown(f"### [{article['title']}]({article['url']})")
            with score_col:
                if score is not None:
                    st.markdown(f"**⭐ {score}/10**")

            meta_parts = []
            if article.get("published_at"):
                meta_parts.append(f"📅 {article['published_at']}")
            meta_parts.append(f"📰 {article['source']}")
            if likes:
                meta_parts.append(f"👍 {likes}")
            st.caption(" | ".join(meta_parts))

            if tags_str:
                st.markdown(tags_str)

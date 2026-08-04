# AI トレンドハブ

Qiita・Zenn・Reddit から AI 関連記事を自動収集し、Claude API でスコアリングしてまとめるツールです。

## 機能

- Qiita / Zenn / Reddit からキーワードに一致する記事を取得
- Claude API で記事の関連度をスコアリング（1〜10点）
- Markdown と JSON 形式で `output/` ディレクトリに保存
- Streamlit による Web UI でフィルタリング・閲覧

## 必要環境

- Python 3.12 以上（WSL / Linux / macOS）
- Anthropic API キー（スコアリング機能に使用）
- Qiita API トークン（任意）

## セットアップ

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd ai-trend-hub
```

### 2. 仮想環境の作成とパッケージのインストール

WSL (Ubuntu) など Linux 環境では `python` コマンドが存在せず `python3` のみの場合があります。
仮想環境を使うことで `python` コマンドが使えるようになります。

```bash
# 仮想環境を作成（初回のみ）
python3 -m venv .venv

# 仮想環境を有効化
source .venv/bin/activate

# パッケージをインストール（初回のみ）
pip install -r requirements.txt
```

仮想環境が有効になると、プロンプトの先頭に `(.venv)` が表示されます。

> **注意:** 毎回ターミナルを開くたびに `source .venv/bin/activate` を実行する必要があります。

### 3. 環境変数の設定

`~/.config/ai-trend-hub/.env` ファイルを作成し、API キーを設定します。

```bash
mkdir -p ~/.config/ai-trend-hub
cat > ~/.config/ai-trend-hub/.env << 'EOF'
ANTHROPIC_API_KEY=your_anthropic_api_key_here
QIITA_TOKEN=your_qiita_token_here  # 任意
EOF
```

## 実行方法

### 記事の収集・スコアリング

```bash
# 仮想環境を有効化してから実行
source .venv/bin/activate
python main.py
```

実行すると `output/YYYY-MM-DD.md` と `output/YYYY-MM-DD.json` が生成されます。

### Web UI の起動

```bash
source .venv/bin/activate
streamlit run app.py
```

ブラウザで `http://localhost:8501` が自動的に開きます。

## 設定

`config.yaml` で収集対象のキーワードやソースを変更できます。

```yaml
keywords:
  - AI
  - LLM
  - AIエージェント
  # ...

sources:
  qiita:
    enabled: true
    per_keyword: 10   # キーワードごとに取得する記事数
  zenn:
    enabled: true
    feed_limit: 100   # フィードから取得する最大記事数
  reddit:
    enabled: true
    per_keyword: 5
    subreddits:
      - MachineLearning
      # ...

output:
  dir: output
```

## ディレクトリ構成

```
ai-trend-hub/
├── main.py          # 記事収集・スコアリングのメインスクリプト
├── app.py           # Streamlit Web UI
├── scorer.py        # Claude API によるスコアリング
├── config.yaml      # 設定ファイル
├── requirements.txt # 依存パッケージ
├── fetchers/
│   ├── qiita.py     # Qiita フェッチャー
│   ├── zenn.py      # Zenn フェッチャー
│   └── reddit.py    # Reddit フェッチャー
└── output/          # 出力ファイル（自動生成）
```

## デプロイ（Streamlit Community Cloud）

Web UI (`app.py`) は [Streamlit Community Cloud](https://streamlit.io/cloud) で無料公開できます。

### 1. GitHub Actions で記事収集を自動化

`.github/workflows/daily-update.yml` が毎日 07:00 JST に `main.py` を実行し、
`output/` の結果を自動でリポジトリに commit します。

リポジトリの Settings → Secrets and variables → Actions で、以下のシークレットを登録してください。

| シークレット名 | 内容 |
| --- | --- |
| `ANTHROPIC_API_KEY` | Anthropic API キー（スコアリングに使用） |

### 2. Streamlit Community Cloud にデプロイ

1. https://share.streamlit.io にアクセスし、GitHub アカウントでログイン
2. 「New app」から本リポジトリを選択
3. Main file path に `app.py` を指定してデプロイ
4. 「Advanced settings」→「Secrets」に以下を TOML 形式で追加

   ```toml
   ANTHROPIC_API_KEY = "your_anthropic_api_key_here"
   ```

デプロイ後、GitHub Actions が `output/` を更新するたびにアプリも自動的に最新データを反映します。

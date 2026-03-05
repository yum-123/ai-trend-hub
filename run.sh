#!/bin/bash
# AI トレンドハブ - cron 実行用ラッパースクリプト

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$HOME/.config/ai-trend-hub/.env"
LOG_FILE="$PROJECT_DIR/output/run.log"

# .env を読み込む
if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
else
    echo "[ERROR] .env が見つかりません: $ENV_FILE" >> "$LOG_FILE"
    exit 1
fi

cd "$PROJECT_DIR"

echo "=== $(date '+%Y-%m-%d %H:%M:%S') 開始 ===" >> "$LOG_FILE"
"$PROJECT_DIR/.venv/bin/python" main.py >> "$LOG_FILE" 2>&1
echo "=== $(date '+%Y-%m-%d %H:%M:%S') 完了 ===" >> "$LOG_FILE"

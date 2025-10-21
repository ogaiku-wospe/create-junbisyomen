#!/bin/bash
# 準備書面作成支援システム - 起動スクリプト
# 使い方: bash start.sh または ./start.sh

# スクリプトのディレクトリに移動
cd "$(dirname "$0")"

# 依存パッケージの簡易チェック
if ! python3 -c "import openai" 2>/dev/null; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "⚠️  依存パッケージがインストールされていません"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📦 以下のコマンドを実行してください:"
    echo ""
    echo "   bash setup.sh"
    echo ""
    echo "または手動でインストール:"
    echo ""
    echo "   pip3 install -r requirements.txt"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    exit 1
fi

# Python 3で起動
python3 run_phase1_multi.py

#!/bin/bash
# 準備書面作成支援システム - 起動スクリプト（macOS用）
# このファイルをダブルクリックで起動できます

# スクリプトのディレクトリに移動
cd "$(dirname "$0")"

# ターミナルのタイトルを設定
echo -ne "\033]0;準備書面作成支援システム\007"

# ヘッダー表示
clear
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║          📝 準備書面作成支援システム v3.7.2               ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Python 3の確認
if ! command -v python3 &> /dev/null; then
    echo "❌ エラー: Python 3がインストールされていません"
    echo ""
    echo "📥 インストール方法:"
    echo "   1. Homebrewをインストール: https://brew.sh/"
    echo "   2. Python 3をインストール: brew install python@3"
    echo ""
    read -p "Enterキーを押して終了..."
    exit 1
fi

# .envファイルの確認
if [ ! -f ".env" ]; then
    echo "⚠️  警告: .envファイルが見つかりません"
    echo ""
    echo "📋 初回セットアップが必要です:"
    echo "   1. .env.exampleを.envにコピー"
    echo "   2. .envファイルにAPIキーを設定"
    echo ""
    echo "🚀 セットアップスクリプトを実行しますか？ [y/N]"
    read -p "> " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📦 セットアップを開始します..."
        if [ -f "setup.sh" ]; then
            bash setup.sh
        else
            cp .env.example .env
            echo "✅ .envファイルを作成しました"
            echo "⚠️  .envファイルを編集してAPIキーを設定してください"
            echo ""
            read -p "Enterキーを押して続行..."
        fi
    else
        echo "❌ セットアップをキャンセルしました"
        read -p "Enterキーを押して終了..."
        exit 1
    fi
fi

# 依存パッケージの確認
echo "🔍 依存パッケージを確認中..."
if ! python3 -c "import openai" 2>/dev/null; then
    echo "⚠️  依存パッケージがインストールされていません"
    echo ""
    echo "📦 インストールしますか？ [y/N]"
    read -p "> " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📦 依存パッケージをインストール中..."
        pip3 install -r requirements.txt
    else
        echo "❌ インストールをキャンセルしました"
        echo "手動でインストールしてください: pip3 install -r requirements.txt"
        read -p "Enterキーを押して終了..."
        exit 1
    fi
fi

echo ""
echo "✅ システムチェック完了"
echo ""
echo "🚀 起動中..."
echo ""

# メインプログラムを起動
python3 run_phase1_multi.py

# 終了時にウィンドウを閉じる前に待機
EXIT_CODE=$?
echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ 正常終了しました"
else
    echo "❌ エラーで終了しました (終了コード: $EXIT_CODE)"
fi
echo ""
read -p "Enterキーを押してウィンドウを閉じる..."

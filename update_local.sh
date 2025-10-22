#!/bin/bash
# GitHubから最新コードをローカルに反映する自動スクリプト
# 使用方法: bash update_local.sh

set -e  # エラーが発生したら即座に終了

echo "========================================"
echo "GitHub最新版取得スクリプト"
echo "========================================"
echo ""

# カレントディレクトリを確認
CURRENT_DIR=$(pwd)
echo "📂 現在のディレクトリ: $CURRENT_DIR"
echo ""

# Gitリポジトリかどうか確認
if [ ! -d ".git" ]; then
    echo "❌ エラー: このディレクトリはGitリポジトリではありません。"
    echo "   正しいディレクトリで実行してください。"
    exit 1
fi

# リモートの確認
REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")
if [ -z "$REMOTE_URL" ]; then
    echo "❌ エラー: リモートリポジトリが設定されていません。"
    exit 1
fi

echo "🔗 リモートリポジトリ: $REMOTE_URL"
echo ""

# 現在のブランチを確認
CURRENT_BRANCH=$(git branch --show-current)
echo "🌿 現在のブランチ: $CURRENT_BRANCH"
echo ""

# 未コミットの変更を確認
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    echo "⚠️  警告: 未コミットの変更があります。"
    echo ""
    git status --short
    echo ""
    read -p "変更を一時保存してから更新しますか？ (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "💾 変更を一時保存中..."
        git stash
        STASHED=true
    else
        echo "❌ 更新を中止しました。"
        echo "   変更をコミットするか、git stash で一時保存してから再実行してください。"
        exit 1
    fi
fi

# mainブランチに切り替え
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "🔄 mainブランチに切り替え中..."
    git checkout main
fi

# 最新版を取得
echo "⬇️  GitHub から最新版を取得中..."
git fetch origin

echo "🔄 ローカルを最新版に更新中..."
git pull origin main

echo ""
echo "✅ 更新完了！"
echo ""

# スタッシュした変更を復元
if [ "$STASHED" = true ]; then
    echo "♻️  一時保存した変更を復元中..."
    if git stash pop; then
        echo "✅ 変更を復元しました。"
    else
        echo "⚠️  変更の復元中に競合が発生しました。"
        echo "   git status で確認して、手動で解決してください。"
    fi
    echo ""
fi

# 最新のコミット情報を表示
echo "📝 最新のコミット:"
git log --oneline -5
echo ""

# 新しいファイルやディレクトリを確認
echo "📋 プロジェクト構成:"
ls -la | head -20
echo ""

# Python依存関係の更新を提案
if [ -f "requirements.txt" ]; then
    echo "💡 ヒント: 依存関係を更新するには:"
    echo "   pip install -r requirements.txt --upgrade"
    echo ""
fi

# 仮想環境の確認
if [ -d "venv" ]; then
    echo "💡 仮想環境が検出されました。"
    echo "   有効化するには: source venv/bin/activate"
    echo ""
fi

echo "========================================"
echo "🎉 更新が完了しました！"
echo "========================================"
echo ""
echo "次のステップ:"
echo "  1. python3 run_phase1_multi.py でプログラムを起動"
echo "  2. メニュー8「時系列ストーリー組み立て」を試す"
echo ""

#!/bin/bash
# =============================================================================
# ローカルリポジトリ更新スクリプト
# /Users/ogaiku/create-junbisyomen のコードを最新版に更新
# =============================================================================

set -e  # エラーが発生したら即座に終了

# 色付き出力用の定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ローカルリポジトリのパス
LOCAL_REPO_PATH="/Users/ogaiku/create-junbisyomen"

echo "======================================================================"
echo "  ローカルリポジトリ更新スクリプト"
echo "======================================================================"
echo ""

# ディレクトリの存在確認
if [ ! -d "$LOCAL_REPO_PATH" ]; then
    echo -e "${RED}❌ エラー: ディレクトリが見つかりません${NC}"
    echo "   パス: $LOCAL_REPO_PATH"
    echo ""
    echo "【対処方法】"
    echo "  1. ディレクトリが存在するか確認してください"
    echo "  2. パスが正しいか確認してください"
    echo "  3. 必要に応じてこのスクリプトのLOCAL_REPO_PATH変数を修正してください"
    exit 1
fi

echo -e "${BLUE}📂 ローカルリポジトリ: $LOCAL_REPO_PATH${NC}"
echo ""

# ディレクトリに移動
cd "$LOCAL_REPO_PATH" || exit 1

# Gitリポジトリかどうか確認
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ エラー: Gitリポジトリではありません${NC}"
    echo "   $LOCAL_REPO_PATH/.git が見つかりません"
    exit 1
fi

# 現在のブランチを確認
CURRENT_BRANCH=$(git branch --show-current)
echo -e "${BLUE}📍 現在のブランチ: $CURRENT_BRANCH${NC}"
echo ""

# 変更があるか確認
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    echo -e "${YELLOW}⚠️  警告: コミットされていない変更があります${NC}"
    echo ""
    git status --short
    echo ""
    read -p "変更を破棄して更新しますか？ (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}更新をキャンセルしました${NC}"
        exit 0
    fi
    
    echo -e "${YELLOW}🗑️  ローカルの変更を破棄しています...${NC}"
    git reset --hard HEAD
    echo ""
fi

# リモートから最新情報を取得
echo -e "${BLUE}🔄 リモートから最新情報を取得中...${NC}"
git fetch origin

# 現在のコミットハッシュを記録
OLD_COMMIT=$(git rev-parse HEAD)

# リモートブランチの最新コミットハッシュを取得
if git rev-parse "origin/$CURRENT_BRANCH" >/dev/null 2>&1; then
    NEW_COMMIT=$(git rev-parse "origin/$CURRENT_BRANCH")
else
    echo -e "${RED}❌ エラー: リモートブランチ origin/$CURRENT_BRANCH が見つかりません${NC}"
    exit 1
fi

# 更新が必要か確認
if [ "$OLD_COMMIT" = "$NEW_COMMIT" ]; then
    echo -e "${GREEN}✅ 既に最新版です${NC}"
    echo "   コミット: $(git rev-parse --short HEAD)"
    exit 0
fi

# プルして更新
echo -e "${BLUE}⬇️  最新版をプル中...${NC}"
git pull origin "$CURRENT_BRANCH"
echo ""

# 更新内容を表示
echo -e "${GREEN}✅ 更新完了！${NC}"
echo ""
echo "【更新内容】"
git log --oneline --graph --decorate "$OLD_COMMIT..$NEW_COMMIT"
echo ""

# 変更されたファイル一覧
echo "【変更されたファイル】"
git diff --name-status "$OLD_COMMIT" "$NEW_COMMIT"
echo ""

# 現在のコミット情報
echo "【現在の状態】"
echo "  ブランチ: $CURRENT_BRANCH"
echo "  コミット: $(git rev-parse --short HEAD)"
echo "  メッセージ: $(git log -1 --pretty=%B | head -1)"
echo ""

echo -e "${GREEN}======================================================================"
echo "  更新が正常に完了しました"
echo "======================================================================${NC}"

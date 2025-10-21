#!/bin/bash
# =============================================================================
# ローカルリポジトリ更新スクリプト（macOS用 .command ファイル）
# /Users/ogaiku/create-junbisyomen のコードを最新版に更新
# 
# 使い方: このファイルをダブルクリックで実行
# =============================================================================

# スクリプトの実行ディレクトリに移動
cd "$(dirname "$0")" || exit 1

# 同じディレクトリにある update_local_repo.sh を実行
if [ -f "update_local_repo.sh" ]; then
    bash update_local_repo.sh
else
    echo "❌ エラー: update_local_repo.sh が見つかりません"
    echo "   このファイルと同じディレクトリに update_local_repo.sh を配置してください"
    exit 1
fi

# 終了前にユーザー入力を待つ（ウィンドウが自動で閉じないようにする）
echo ""
read -p "Enterキーを押して終了..." -r

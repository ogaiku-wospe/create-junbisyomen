#!/bin/bash

# =============================================================================
# プロジェクトクリーンアップスクリプト
# 不要なファイルとディレクトリを安全に削除します
# =============================================================================

echo "========================================="
echo "プロジェクトクリーンアップスクリプト"
echo "========================================="
echo ""

# 現在のディレクトリを確認
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "作業ディレクトリ: $SCRIPT_DIR"
echo ""

# バックアップディレクトリを作成（念のため）
BACKUP_DIR="$SCRIPT_DIR/cleanup_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "バックアップディレクトリ: $BACKUP_DIR"
echo ""

# 削除対象のリスト
echo "=== 削除対象のファイル/ディレクトリを確認中 ==="
echo ""

# 1. __pycache__ ディレクトリ
if [ -d "$SCRIPT_DIR/__pycache__" ]; then
    echo "✓ 発見: __pycache__/"
    PYCACHE_FOUND=1
else
    echo "✗ 未検出: __pycache__/"
    PYCACHE_FOUND=0
fi

# 2. .pyc ファイル
PYC_FILES=$(find "$SCRIPT_DIR" -name "*.pyc" -not -path "*/venv/*" 2>/dev/null)
if [ -n "$PYC_FILES" ]; then
    echo "✓ 発見: *.pyc ファイル"
    PYCS_FOUND=1
else
    echo "✗ 未検出: *.pyc ファイル"
    PYCS_FOUND=0
fi

# 3. venv ディレクトリ
if [ -d "$SCRIPT_DIR/venv" ]; then
    echo "✓ 発見: venv/"
    VENV_FOUND=1
else
    echo "✗ 未検出: venv/"
    VENV_FOUND=0
fi

# 4. ログファイル
LOG_FILES=$(find "$SCRIPT_DIR" -maxdepth 1 -name "*.log" 2>/dev/null)
if [ -n "$LOG_FILES" ]; then
    echo "✓ 発見: *.log ファイル"
    LOGS_FOUND=1
else
    echo "✗ 未検出: *.log ファイル"
    LOGS_FOUND=0
fi

# 5. 機密ファイル
SENSITIVE_FILES=()
[ -f "$SCRIPT_DIR/credentials.json" ] && SENSITIVE_FILES+=("credentials.json")
[ -f "$SCRIPT_DIR/token.pickle" ] && SENSITIVE_FILES+=("token.pickle")

if [ ${#SENSITIVE_FILES[@]} -gt 0 ]; then
    echo "✓ 発見: 機密ファイル (${SENSITIVE_FILES[*]})"
    SENSITIVE_FOUND=1
else
    echo "✗ 未検出: 機密ファイル"
    SENSITIVE_FOUND=0
fi

# 6. 一時的な状態ファイル
TEMP_STATE_FILES=()
[ -f "$SCRIPT_DIR/current_case.json" ] && TEMP_STATE_FILES+=("current_case.json")
[ -f "$SCRIPT_DIR/database_uploaded.json" ] && TEMP_STATE_FILES+=("database_uploaded.json")

if [ ${#TEMP_STATE_FILES[@]} -gt 0 ]; then
    echo "✓ 発見: 一時状態ファイル (${TEMP_STATE_FILES[*]})"
    TEMP_FOUND=1
else
    echo "✗ 未検出: 一時状態ファイル"
    TEMP_FOUND=0
fi

echo ""
echo "========================================="
echo "削除を実行しますか？"
echo "========================================="
echo ""
echo "注意: 機密ファイルと一時状態ファイルはバックアップされます"
echo ""
read -p "続行するには 'yes' と入力してください: " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo ""
    echo "キャンセルされました。"
    rmdir "$BACKUP_DIR" 2>/dev/null
    exit 0
fi

echo ""
echo "=== クリーンアップを開始 ==="
echo ""

# 機密ファイルと一時状態ファイルをバックアップ
if [ $SENSITIVE_FOUND -eq 1 ] || [ $TEMP_FOUND -eq 1 ]; then
    echo "機密ファイルと一時状態ファイルをバックアップ中..."
    for file in "${SENSITIVE_FILES[@]}" "${TEMP_STATE_FILES[@]}"; do
        if [ -f "$SCRIPT_DIR/$file" ]; then
            cp "$SCRIPT_DIR/$file" "$BACKUP_DIR/"
            echo "  ✓ バックアップ: $file"
        fi
    done
    echo ""
fi

# 1. __pycache__ を削除
if [ $PYCACHE_FOUND -eq 1 ]; then
    echo "削除中: __pycache__/"
    rm -rf "$SCRIPT_DIR/__pycache__"
    echo "  ✓ 完了"
fi

# 2. .pyc ファイルを削除
if [ $PYCS_FOUND -eq 1 ]; then
    echo "削除中: *.pyc ファイル"
    find "$SCRIPT_DIR" -name "*.pyc" -not -path "*/venv/*" -delete
    echo "  ✓ 完了"
fi

# 3. venv を削除
if [ $VENV_FOUND -eq 1 ]; then
    echo "削除中: venv/ (これには時間がかかる場合があります)"
    rm -rf "$SCRIPT_DIR/venv"
    echo "  ✓ 完了"
fi

# 4. ログファイルを削除
if [ $LOGS_FOUND -eq 1 ]; then
    echo "削除中: *.log ファイル"
    find "$SCRIPT_DIR" -maxdepth 1 -name "*.log" -delete
    echo "  ✓ 完了"
fi

# 5. 機密ファイルを削除
if [ $SENSITIVE_FOUND -eq 1 ]; then
    echo "削除中: 機密ファイル"
    for file in "${SENSITIVE_FILES[@]}"; do
        rm -f "$SCRIPT_DIR/$file"
        echo "  ✓ 削除: $file"
    done
fi

# 6. 一時状態ファイルを削除
if [ $TEMP_FOUND -eq 1 ]; then
    echo "削除中: 一時状態ファイル"
    for file in "${TEMP_STATE_FILES[@]}"; do
        rm -f "$SCRIPT_DIR/$file"
        echo "  ✓ 削除: $file"
    done
fi

echo ""
echo "========================================="
echo "クリーンアップ完了！"
echo "========================================="
echo ""
echo "バックアップ保存先: $BACKUP_DIR"
echo ""
echo "次のステップ:"
echo "1. .gitignore ファイルを確認・調整"
echo "2. git status で変更を確認"
echo "3. 必要に応じて git add/commit を実行"
echo ""
echo "仮想環境を再作成するには:"
echo "  python3 -m venv venv"
echo "  source venv/bin/activate  # Linux/Mac"
echo "  venv\\Scripts\\activate     # Windows"
echo "  pip install -r requirements.txt"
echo ""

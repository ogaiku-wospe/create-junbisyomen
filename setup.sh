#!/bin/bash
# 準備書面作成支援システム - 初回セットアップスクリプト
# 使い方: bash setup.sh

set -e  # エラーが発生したら停止

# スクリプトのディレクトリに移動
cd "$(dirname "$0")"

# ヘッダー表示
clear
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║       🔧 準備書面作成支援システム - 初回セットアップ      ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# ステップ1: Python 3の確認
echo "【ステップ 1/5】Python 3の確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ $PYTHON_VERSION がインストールされています"
else
    echo "❌ Python 3がインストールされていません"
    echo ""
    echo "📥 macOSの場合のインストール方法:"
    echo "   1. Homebrewをインストール: https://brew.sh/"
    echo "   2. ターミナルで実行: brew install python@3"
    echo ""
    echo "📥 Linuxの場合のインストール方法:"
    echo "   Ubuntu/Debian: sudo apt-get install python3 python3-pip"
    echo "   CentOS/RHEL: sudo yum install python3 python3-pip"
    exit 1
fi
echo ""

# ステップ2: .envファイルの作成
echo "【ステップ 2/5】環境変数ファイルの作成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f ".env" ]; then
    echo "⚠️  .envファイルが既に存在します"
    read -p "上書きしますか？ [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "⏭️  スキップしました"
    else
        cp .env.example .env
        echo "✅ .envファイルを作成しました"
    fi
else
    cp .env.example .env
    echo "✅ .envファイルを作成しました"
fi
echo ""

# ステップ3: 依存パッケージのインストール
echo "【ステップ 3/5】依存パッケージのインストール"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "requirements.txt" ]; then
    echo "📦 Pythonパッケージをインストール中..."
    pip3 install -r requirements.txt
    echo "✅ インストール完了"
else
    echo "⚠️  requirements.txtが見つかりません"
fi
echo ""

# ステップ4: システムライブラリの確認（macOS）
echo "【ステップ 4/5】システムライブラリの確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 macOSを検出しました"
    
    # Homebrewの確認
    if command -v brew &> /dev/null; then
        echo "✅ Homebrewがインストールされています"
        
        # Tesseract OCRの確認
        if brew list tesseract &> /dev/null; then
            echo "✅ Tesseract OCRがインストールされています"
        else
            echo "⚠️  Tesseract OCRがインストールされていません"
            read -p "インストールしますか？ [y/N] " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                brew install tesseract tesseract-lang
                echo "✅ Tesseract OCRをインストールしました"
            else
                echo "⏭️  スキップしました（手動インストール: brew install tesseract tesseract-lang）"
            fi
        fi
        
        # Popper（PDFライブラリ）の確認
        if brew list poppler &> /dev/null; then
            echo "✅ Poppler（PDFライブラリ）がインストールされています"
        else
            echo "⚠️  Poppler（PDFライブラリ）がインストールされていません"
            read -p "インストールしますか？ [y/N] " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                brew install poppler
                echo "✅ Popplerをインストールしました"
            else
                echo "⏭️  スキップしました（手動インストール: brew install poppler）"
            fi
        fi
    else
        echo "⚠️  Homebrewがインストールされていません"
        echo "📥 インストール方法: https://brew.sh/"
        echo "   ターミナルで実行: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 Linuxを検出しました"
    echo "📝 必要なパッケージ:"
    echo "   - tesseract-ocr"
    echo "   - poppler-utils"
    echo ""
    echo "インストールコマンド例:"
    echo "   Ubuntu/Debian: sudo apt-get install tesseract-ocr tesseract-ocr-jpn poppler-utils"
    echo "   CentOS/RHEL: sudo yum install tesseract poppler-utils"
fi
echo ""

# ステップ5: APIキーの設定ガイド
echo "【ステップ 5/5】APIキーの設定"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 .envファイルに以下のAPIキーを設定してください:"
echo ""
echo "1. OpenAI API キー（必須）"
echo "   取得: https://platform.openai.com/api-keys"
echo "   設定項目: OPENAI_API_KEY=your_api_key_here"
echo ""
echo "2. Anthropic Claude API キー（推奨）"
echo "   取得: https://console.anthropic.com/"
echo "   設定項目: ANTHROPIC_API_KEY=your_api_key_here"
echo "   ※OpenAI Vision拒否時の高品質フォールバック用"
echo ""
echo "3. Google Drive API 認証情報（オプション）"
echo "   取得: https://console.cloud.google.com/"
echo "   ファイル: credentials.json"
echo ""
read -p ".envファイルを今すぐ編集しますか？ [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v nano &> /dev/null; then
        nano .env
    elif command -v vim &> /dev/null; then
        vim .env
    elif command -v vi &> /dev/null; then
        vi .env
    else
        echo "テキストエディタが見つかりません。手動で編集してください: .env"
        if [[ "$OSTYPE" == "darwin"* ]]; then
            open .env
        fi
    fi
fi
echo ""

# 完了メッセージ
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║               ✅ セットアップ完了！                        ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 起動方法:"
echo ""
echo "   【macOS】ダブルクリックで起動:"
echo "     start.command をダブルクリック"
echo ""
echo "   【ターミナルから起動】:"
echo "     bash start.sh"
echo "     または"
echo "     python3 run_phase1_multi.py"
echo ""
echo "📚 詳細なドキュメント:"
echo "   README.md - 基本的な使い方"
echo "   USAGE_GUIDE.md - 詳細な操作ガイド"
echo "   GOOGLE_DRIVE_GUIDE.md - Google Drive連携設定"
echo ""

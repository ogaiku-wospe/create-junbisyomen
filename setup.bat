@echo off
REM 準備書面作成支援システム - 初回セットアップスクリプト（Windows用）
REM このファイルをダブルクリックで実行できます

chcp 65001 > nul
setlocal enabledelayedexpansion

REM カレントディレクトリをスクリプトの場所に移動
cd /d "%~dp0"

REM ヘッダー表示
cls
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║   🔧 Phase1_Evidence Analysis System - 初回セットアップ   ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM ステップ1: Pythonの確認
echo 【ステップ 1/4】Pythonの確認
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Pythonがインストールされていません
    echo.
    echo 📥 インストール方法:
    echo    https://www.python.org/downloads/
    echo    からPython 3をダウンロードしてインストールしてください
    echo    ※インストール時に「Add Python to PATH」にチェックを入れてください
    echo.
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
    echo ✅ !PYTHON_VERSION! がインストールされています
)
echo.

REM ステップ2: .envファイルの作成
echo 【ステップ 2/4】環境変数ファイルの作成
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if exist ".env" (
    echo ⚠️  .envファイルが既に存在します
    set /p OVERWRITE="上書きしますか？ [y/N] "
    if /i "!OVERWRITE!"=="y" (
        copy /y .env.example .env > nul
        echo ✅ .envファイルを作成しました
    ) else (
        echo ⏭️  スキップしました
    )
) else (
    copy .env.example .env > nul
    echo ✅ .envファイルを作成しました
)
echo.

REM ステップ3: 依存パッケージのインストール
echo 【ステップ 3/4】依存パッケージのインストール
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if exist "requirements.txt" (
    echo 📦 Pythonパッケージをインストール中...
    pip install -r requirements.txt
    echo ✅ インストール完了
) else (
    echo ⚠️  requirements.txtが見つかりません
)
echo.

REM ステップ4: APIキーの設定ガイド
echo 【ステップ 4/4】APIキーの設定
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 📝 .envファイルに以下のAPIキーを設定してください:
echo.
echo 1. OpenAI API キー（必須）
echo    取得: https://platform.openai.com/api-keys
echo    設定項目: OPENAI_API_KEY=your_api_key_here
echo.
echo 2. Anthropic Claude API キー（推奨）
echo    取得: https://console.anthropic.com/
echo    設定項目: ANTHROPIC_API_KEY=your_api_key_here
echo    ※OpenAI Vision拒否時の高品質フォールバック用
echo.
echo 3. Google Drive API 認証情報（オプション）
echo    取得: https://console.cloud.google.com/
echo    ファイル: credentials.json
echo.
set /p EDIT_ENV=".envファイルを今すぐ編集しますか？ [y/N] "
if /i "!EDIT_ENV!"=="y" (
    notepad .env
)
echo.

REM 完了メッセージ
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║               ✅ セットアップ完了！                        ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 🚀 起動方法:
echo.
echo    【ダブルクリックで起動】:
echo      start.bat をダブルクリック
echo.
echo    【コマンドプロンプトから起動】:
echo      python run_phase1_multi.py
echo.
echo 📚 詳細なドキュメント:
echo    README.md - 基本的な使い方
echo    USAGE_GUIDE.md - 詳細な操作ガイド
echo    GOOGLE_DRIVE_GUIDE.md - Google Drive連携設定
echo.
pause

@echo off
REM 準備書面作成支援システム - 起動スクリプット（Windows用）
REM このファイルをダブルクリックで起動できます

chcp 65001 > nul
setlocal enabledelayedexpansion

REM カレントディレクトリをスクリプトの場所に移動
cd /d "%~dp0"

REM ヘッダー表示
cls
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║          📝 準備書面作成支援システム v3.7.2               ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Python 3の確認
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ エラー: Pythonがインストールされていません
    echo.
    echo 📥 インストール方法:
    echo    https://www.python.org/downloads/
    echo    からPython 3をダウンロードしてインストールしてください
    echo.
    pause
    exit /b 1
)

REM .envファイルの確認
if not exist ".env" (
    echo ⚠️  警告: .envファイルが見つかりません
    echo.
    echo 📋 初回セットアップが必要です
    echo    .env.exampleを.envにコピーしてAPIキーを設定してください
    echo.
    copy .env.example .env
    echo ✅ .envファイルを作成しました
    echo ⚠️  .envファイルを編集してAPIキーを設定してください
    echo.
    notepad .env
    echo.
    pause
)

REM 依存パッケージの確認
echo 🔍 依存パッケージを確認中...
python -c "import openai" 2>nul
if errorlevel 1 (
    echo ⚠️  依存パッケージがインストールされていません
    echo.
    echo 📦 インストールしますか？ [Y/N]
    set /p INSTALL_DEPS=^> 
    if /i "!INSTALL_DEPS!"=="Y" (
        echo 📦 依存パッケージをインストール中...
        pip install -r requirements.txt
    ) else (
        echo ❌ インストールをキャンセルしました
        echo 手動でインストールしてください: pip install -r requirements.txt
        pause
        exit /b 1
    )
)

echo.
echo ✅ システムチェック完了
echo.
echo 🚀 起動中...
echo.

REM メインプログラムを起動
python run_phase1_multi.py

REM 終了時にウィンドウを閉じる前に待機
if errorlevel 1 (
    echo.
    echo ❌ エラーで終了しました
) else (
    echo.
    echo ✅ 正常終了しました
)
echo.
pause

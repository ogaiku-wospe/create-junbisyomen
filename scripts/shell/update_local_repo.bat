@echo off
REM =============================================================================
REM ローカルリポジトリ更新スクリプト（Windows用）
REM C:\Users\[username]\create-junbisyomen のコードを最新版に更新
REM 
REM 使い方: このファイルをダブルクリックで実行
REM =============================================================================

chcp 65001 > nul
setlocal enabledelayedexpansion

echo ======================================================================
echo   ローカルリポジトリ更新スクリプト
echo ======================================================================
echo.

REM ローカルリポジトリのパス（環境に応じて変更してください）
set "LOCAL_REPO_PATH=C:\Users\%USERNAME%\create-junbisyomen"

echo 📂 ローカルリポジトリ: %LOCAL_REPO_PATH%
echo.

REM ディレクトリの存在確認
if not exist "%LOCAL_REPO_PATH%" (
    echo ❌ エラー: ディレクトリが見つかりません
    echo    パス: %LOCAL_REPO_PATH%
    echo.
    echo 【対処方法】
    echo   1. ディレクトリが存在するか確認してください
    echo   2. パスが正しいか確認してください
    echo   3. 必要に応じてこのスクリプトのLOCAL_REPO_PATH変数を修正してください
    goto :error
)

REM ディレクトリに移動
cd /d "%LOCAL_REPO_PATH%" || goto :error

REM Gitリポジトリかどうか確認
if not exist ".git" (
    echo ❌ エラー: Gitリポジトリではありません
    echo    %LOCAL_REPO_PATH%\.git が見つかりません
    goto :error
)

REM 現在のブランチを確認
for /f "tokens=*" %%a in ('git branch --show-current') do set "CURRENT_BRANCH=%%a"
echo 📍 現在のブランチ: %CURRENT_BRANCH%
echo.

REM 変更があるか確認
git diff-index --quiet HEAD -- 2>nul
if errorlevel 1 (
    echo ⚠️  警告: コミットされていない変更があります
    echo.
    git status --short
    echo.
    set /p "REPLY=変更を破棄して更新しますか？ (y/n): "
    if /i not "!REPLY!"=="y" (
        echo 更新をキャンセルしました
        goto :end
    )
    
    echo 🗑️  ローカルの変更を破棄しています...
    git reset --hard HEAD
    echo.
)

REM リモートから最新情報を取得
echo 🔄 リモートから最新情報を取得中...
git fetch origin

REM 現在のコミットハッシュを記録
for /f "tokens=*" %%a in ('git rev-parse HEAD') do set "OLD_COMMIT=%%a"

REM リモートブランチの最新コミットハッシュを取得
git rev-parse "origin/%CURRENT_BRANCH%" >nul 2>&1
if errorlevel 1 (
    echo ❌ エラー: リモートブランチ origin/%CURRENT_BRANCH% が見つかりません
    goto :error
)
for /f "tokens=*" %%a in ('git rev-parse "origin/%CURRENT_BRANCH%"') do set "NEW_COMMIT=%%a"

REM 更新が必要か確認
if "%OLD_COMMIT%"=="%NEW_COMMIT%" (
    echo ✅ 既に最新版です
    for /f "tokens=*" %%a in ('git rev-parse --short HEAD') do echo    コミット: %%a
    goto :end
)

REM プルして更新
echo ⬇️  最新版をプル中...
git pull origin %CURRENT_BRANCH%
echo.

REM 更新内容を表示
echo ✅ 更新完了！
echo.
echo 【更新内容】
git log --oneline --graph --decorate %OLD_COMMIT:~0,8%..%NEW_COMMIT:~0,8%
echo.

REM 変更されたファイル一覧
echo 【変更されたファイル】
git diff --name-status %OLD_COMMIT:~0,8% %NEW_COMMIT:~0,8%
echo.

REM 現在のコミット情報
echo 【現在の状態】
echo   ブランチ: %CURRENT_BRANCH%
for /f "tokens=*" %%a in ('git rev-parse --short HEAD') do echo   コミット: %%a
for /f "tokens=*" %%a in ('git log -1 --pretty^=%%B') do (
    echo   メッセージ: %%a
    goto :show_complete
)

:show_complete
echo.
echo ======================================================================
echo   更新が正常に完了しました
echo ======================================================================
goto :end

:error
echo.
echo ❌ エラーが発生しました
pause
exit /b 1

:end
echo.
pause

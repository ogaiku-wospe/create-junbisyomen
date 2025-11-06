@echo off
REM =============================================================================
REM プロジェクトクリーンアップスクリプト (Windows版)
REM 不要なファイルとディレクトリを安全に削除します
REM =============================================================================

chcp 65001 >nul
echo =========================================
echo プロジェクトクリーンアップスクリプト
echo =========================================
echo.

REM 現在のディレクトリを確認
set "SCRIPT_DIR=%~dp0"
echo 作業ディレクトリ: %SCRIPT_DIR%
echo.

REM バックアップディレクトリを作成（念のため）
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
for /f "tokens=1-2 delims=/:" %%a in ("%TIME%") do (set mytime=%%a%%b)
set "BACKUP_DIR=%SCRIPT_DIR%cleanup_backup_%mydate%_%mytime%"
mkdir "%BACKUP_DIR%" 2>nul
echo バックアップディレクトリ: %BACKUP_DIR%
echo.

echo === 削除対象のファイル/ディレクトリを確認中 ===
echo.

REM 1. __pycache__ ディレクトリ
if exist "%SCRIPT_DIR%__pycache__\" (
    echo ✓ 発見: __pycache__\
    set PYCACHE_FOUND=1
) else (
    echo ✗ 未検出: __pycache__\
    set PYCACHE_FOUND=0
)

REM 2. venv ディレクトリ
if exist "%SCRIPT_DIR%venv\" (
    echo ✓ 発見: venv\
    set VENV_FOUND=1
) else (
    echo ✗ 未検出: venv\
    set VENV_FOUND=0
)

REM 3. ログファイル
set LOGS_FOUND=0
if exist "%SCRIPT_DIR%*.log" (
    echo ✓ 発見: *.log ファイル
    set LOGS_FOUND=1
) else (
    echo ✗ 未検出: *.log ファイル
)

REM 4. 機密ファイル
set SENSITIVE_FOUND=0
if exist "%SCRIPT_DIR%credentials.json" set SENSITIVE_FOUND=1
if exist "%SCRIPT_DIR%token.pickle" set SENSITIVE_FOUND=1
if %SENSITIVE_FOUND%==1 (
    echo ✓ 発見: 機密ファイル
) else (
    echo ✗ 未検出: 機密ファイル
)

REM 5. 一時的な状態ファイル
set TEMP_FOUND=0
if exist "%SCRIPT_DIR%current_case.json" set TEMP_FOUND=1
if exist "%SCRIPT_DIR%database_uploaded.json" set TEMP_FOUND=1
if %TEMP_FOUND%==1 (
    echo ✓ 発見: 一時状態ファイル
) else (
    echo ✗ 未検出: 一時状態ファイル
)

echo.
echo =========================================
echo 削除を実行しますか？
echo =========================================
echo.
echo 注意: 機密ファイルと一時状態ファイルはバックアップされます
echo.
set /p CONFIRM="続行するには 'yes' と入力してください: "

if not "%CONFIRM%"=="yes" (
    echo.
    echo キャンセルされました。
    rmdir "%BACKUP_DIR%" 2>nul
    exit /b 0
)

echo.
echo === クリーンアップを開始 ===
echo.

REM 機密ファイルと一時状態ファイルをバックアップ
if %SENSITIVE_FOUND%==1 (
    echo 機密ファイルをバックアップ中...
    if exist "%SCRIPT_DIR%credentials.json" (
        copy "%SCRIPT_DIR%credentials.json" "%BACKUP_DIR%\" >nul
        echo   ✓ バックアップ: credentials.json
    )
    if exist "%SCRIPT_DIR%token.pickle" (
        copy "%SCRIPT_DIR%token.pickle" "%BACKUP_DIR%\" >nul
        echo   ✓ バックアップ: token.pickle
    )
    echo.
)

if %TEMP_FOUND%==1 (
    echo 一時状態ファイルをバックアップ中...
    if exist "%SCRIPT_DIR%current_case.json" (
        copy "%SCRIPT_DIR%current_case.json" "%BACKUP_DIR%\" >nul
        echo   ✓ バックアップ: current_case.json
    )
    if exist "%SCRIPT_DIR%database_uploaded.json" (
        copy "%SCRIPT_DIR%database_uploaded.json" "%BACKUP_DIR%\" >nul
        echo   ✓ バックアップ: database_uploaded.json
    )
    echo.
)

REM 1. __pycache__ を削除
if %PYCACHE_FOUND%==1 (
    echo 削除中: __pycache__\
    rmdir /s /q "%SCRIPT_DIR%__pycache__"
    echo   ✓ 完了
)

REM 2. .pyc ファイルを削除
echo 削除中: *.pyc ファイル
del /s /q "%SCRIPT_DIR%*.pyc" >nul 2>&1
echo   ✓ 完了

REM 3. venv を削除
if %VENV_FOUND%==1 (
    echo 削除中: venv\ ^(これには時間がかかる場合があります^)
    rmdir /s /q "%SCRIPT_DIR%venv"
    echo   ✓ 完了
)

REM 4. ログファイルを削除
if %LOGS_FOUND%==1 (
    echo 削除中: *.log ファイル
    del /q "%SCRIPT_DIR%*.log" >nul 2>&1
    echo   ✓ 完了
)

REM 5. 機密ファイルを削除
if %SENSITIVE_FOUND%==1 (
    echo 削除中: 機密ファイル
    if exist "%SCRIPT_DIR%credentials.json" (
        del /q "%SCRIPT_DIR%credentials.json"
        echo   ✓ 削除: credentials.json
    )
    if exist "%SCRIPT_DIR%token.pickle" (
        del /q "%SCRIPT_DIR%token.pickle"
        echo   ✓ 削除: token.pickle
    )
)

REM 6. 一時状態ファイルを削除
if %TEMP_FOUND%==1 (
    echo 削除中: 一時状態ファイル
    if exist "%SCRIPT_DIR%current_case.json" (
        del /q "%SCRIPT_DIR%current_case.json"
        echo   ✓ 削除: current_case.json
    )
    if exist "%SCRIPT_DIR%database_uploaded.json" (
        del /q "%SCRIPT_DIR%database_uploaded.json"
        echo   ✓ 削除: database_uploaded.json
    )
)

echo.
echo =========================================
echo クリーンアップ完了！
echo =========================================
echo.
echo バックアップ保存先: %BACKUP_DIR%
echo.
echo 次のステップ:
echo 1. .gitignore ファイルを確認・調整
echo 2. git status で変更を確認
echo 3. 必要に応じて git add/commit を実行
echo.
echo 仮想環境を再作成するには:
echo   python -m venv venv
echo   venv\Scripts\activate
echo   pip install -r requirements.txt
echo.
pause

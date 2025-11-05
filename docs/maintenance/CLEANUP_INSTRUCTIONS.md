# プロジェクトクリーンアップ手順書

このドキュメントでは、`create-junbisyomen` プロジェクトから不要なファイルを安全に削除し、GitHubリポジトリとして適切な状態にする手順を説明します。

## 📋 概要

以下のファイル/ディレクトリが削除対象です：

### 🗑️ 削除するもの

1. **`__pycache__/`** - Pythonバイトコードキャッシュ
2. **`*.pyc`** - コンパイル済みPythonファイル
3. **`venv/`** - 仮想環境（`requirements.txt`で再構築可能）
4. **`*.log`** - ログファイル（`migration.log`, `phase1_multi.log`）
5. **`credentials.json`** - Google Drive認証情報（機密）
6. **`token.pickle`** - アクセストークン（機密）
7. **`current_case.json`** - 一時的な状態ファイル
8. **`database_uploaded.json`** - 一時的な状態ファイル

### ✅ 保持するもの

- すべての `.py` ソースコードファイル
- `.md` ドキュメントファイル
- `.sh`, `.bat`, `.command` スクリプトファイル
- `requirements.txt`
- **`credentials.json.example`** - 認証情報のテンプレート（重要！）
- `prompts/` ディレクトリ
- `database_schema_v3.json`, `analysis_method_report.json`

---

## 🚀 実行手順

### ステップ1: GitHubから最新版を取得

ローカルのプロジェクトディレクトリで以下のコマンドを実行してください：

```bash
cd /Users/ogaiku/create-junbisyomen
git pull origin main
```

これにより、以下のファイルが自動的にダウンロードされます：

1. **`.gitignore`** - Git管理から除外するファイルのパターン
2. **`cleanup_project.sh`** - Mac/Linux用クリーンアップスクリプト
3. **`cleanup_project.bat`** - Windows用クリーンアップスクリプト
4. **`CLEANUP_INSTRUCTIONS.md`** - この手順書（本ファイル）

> **💡 Tips**: GitHubリポジトリから個別にダウンロードすることもできます：
> - リポジトリURL: https://github.com/ogaiku-wospe/create-junbisyomen
> - 各ファイルのRawボタンから直接ダウンロード可能

### ステップ2: スクリプトに実行権限を付与（Mac/Linuxのみ）

```bash
cd /Users/ogaiku/create-junbisyomen
chmod +x cleanup_project.sh
```

### ステップ3: クリーンアップスクリプトを実行

#### Mac/Linux:
```bash
cd /Users/ogaiku/create-junbisyomen
./cleanup_project.sh
```

#### Windows:
```cmd
cd C:\Users\ogaiku\create-junbisyomen
cleanup_project.bat
```

### ステップ4: 確認プロンプト

スクリプトが削除対象のファイルを検出し、リストを表示します。
続行するには `yes` と入力してください。

### ステップ5: バックアップを確認

機密ファイル（`credentials.json`, `token.pickle`）と一時状態ファイルは、
`cleanup_backup_YYYYMMDD_HHMMSS/` ディレクトリに自動的にバックアップされます。

---

## 📝 クリーンアップ後の作業

### 1. Gitの状態を確認

```bash
git status
```

### 2. `.gitignore` をGitに追加

```bash
git add .gitignore
git commit -m "Add .gitignore to exclude temporary and sensitive files"
```

### 3. 削除されたファイルをGitから削除（必要に応じて）

もし `credentials.json` などが以前にGitで管理されていた場合：

```bash
git rm --cached credentials.json token.pickle current_case.json database_uploaded.json
git commit -m "Remove sensitive and temporary files from Git tracking"
```

### 4. 仮想環境を再構築（必要な場合）

```bash
# 仮想環境を作成
python3 -m venv venv

# 仮想環境を有効化
# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 依存パッケージをインストール
pip install -r requirements.txt
```

---

## 🔒 セキュリティに関する注意事項

### 重要: 機密ファイルの取り扱い

1. **`credentials.json`** と **`token.pickle`** は絶対にGitHubにアップロードしないでください
2. これらのファイルは `.gitignore` で除外されています
3. バックアップディレクトリも `.gitignore` で除外されています

### GitHub履歴から機密情報を削除する場合

もし既に機密ファイルをGitHubにプッシュしてしまった場合は、以下の手順で履歴から削除してください：

```bash
# BFG Repo-Cleanerを使用（推奨）
# https://rtyley.github.io/bfg-repo-cleaner/

# または git filter-branchを使用
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch credentials.json token.pickle" \
  --prune-empty --tag-name-filter cat -- --all

# 強制プッシュ（注意: 共同作業者がいる場合は事前に通知）
git push origin --force --all
```

**注意**: GitHubに機密情報をプッシュした場合は、以下も実施してください：
- Google Cloud Consoleで認証情報を無効化
- 新しい認証情報を生成
- トークンをリフレッシュ

---

## 🔍 トラブルシューティング

### Q: スクリプトが動作しない

**Mac/Linux**:
- 実行権限が付与されているか確認: `ls -l cleanup_project.sh`
- `chmod +x cleanup_project.sh` を実行

**Windows**:
- PowerShellの実行ポリシーを確認
- コマンドプロンプトから実行（PowerShellではなく）

### Q: バックアップを復元したい

バックアップディレクトリ（`cleanup_backup_YYYYMMDD_HHMMSS/`）から必要なファイルをコピーしてください：

```bash
cp cleanup_backup_20240115_143022/credentials.json .
cp cleanup_backup_20240115_143022/token.pickle .
```

### Q: venvを削除したくない

スクリプトを編集して、venv削除の部分をコメントアウトまたは削除してください。

---

## 📊 ディスク容量の節約

クリーンアップにより、以下のディスク容量が解放されます（概算）：

- `venv/`: 50-200 MB（依存パッケージによる）
- `__pycache__/` と `*.pyc`: 1-5 MB
- ログファイル: サイズによる

---

## ✅ チェックリスト

クリーンアップ完了後、以下を確認してください：

- [ ] `.gitignore` ファイルがプロジェクトルートに存在する
- [ ] 機密ファイルがバックアップされている
- [ ] `git status` で不要なファイルが表示されない
- [ ] `.gitignore` がGitにコミットされている
- [ ] 必要に応じて仮想環境を再構築している
- [ ] プロジェクトが正常に動作することを確認

---

## 🆘 サポート

問題が発生した場合は、以下を確認してください：

1. バックアップディレクトリに機密ファイルが保存されているか
2. `git status` で意図しないファイルが削除されていないか
3. 必要なファイル（`.py`, `.md`, `requirements.txt`など）が残っているか

---

**作成日**: 2025年10月22日  
**バージョン**: 1.0

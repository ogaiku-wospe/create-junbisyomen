# 🚀 クイックスタートガイド

準備書面作成支援システムを**5分で**始められます！

> **⚠️ 重要**: 初めて起動する場合、まず **`bash setup.sh`** を実行してください！
> 
> これで依存パッケージが自動インストールされます。

## 📋 目次

1. [最初の起動（3ステップ）](#最初の起動3ステップ)
2. [起動方法（ダブルクリックで簡単！）](#起動方法)
3. [トラブルシューティング](#トラブルシューティング)

---

## 最初の起動（3ステップ）

### ステップ1️⃣: セットアップスクリプトを実行

**⚡ macOS/Linuxの場合（推奨）:**
```bash
# ターミナルで実行
cd create-junbisyomen
bash setup.sh
```

**手動インストールの場合:**
```bash
cd create-junbisyomen
pip3 install -r requirements.txt
cp .env.example .env
```

**Windows:**
```
フォルダを開いて setup.bat をダブルクリック
```

セットアップスクリプトが自動で：
- ✅ Python 3をチェック
- ✅ .envファイルを作成
- ✅ 必要なパッケージをインストール
- ✅ システムライブラリを確認

### ステップ2️⃣: APIキーを設定

`.env` ファイルを開いて、以下を設定：

```bash
# 必須: OpenAI API キー
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# 推奨: Anthropic Claude API キー（高品質フォールバック用）
ANTHROPIC_API_KEY=sk-ant-your-actual-anthropic-key-here
```

**APIキーの取得方法:**
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/

### ステップ3️⃣: 起動！

次のセクションの[起動方法](#起動方法)を参照してください。

---

## 起動方法

### 🍎 macOS

#### 方法1: ダブルクリックで起動（おすすめ！）

1. Finderで `create-junbisyomen` フォルダを開く
2. **`start.command`** をダブルクリック

> 💡 初回起動時に「開発元を確認できません」と表示される場合：
> - `start.command` を右クリック → 「開く」を選択
> - または、ターミナルで `chmod +x start.command` を実行

#### 方法2: ターミナルから起動

```bash
cd create-junbisyomen
bash start.sh
```

#### 方法3: 直接起動

```bash
cd create-junbisyomen
python3 run_phase1_multi.py
```

---

### 🪟 Windows

#### 方法1: ダブルクリックで起動（おすすめ！）

1. エクスプローラーで `create-junbisyomen` フォルダを開く
2. **`start.bat`** をダブルクリック

#### 方法2: コマンドプロンプトから起動

```cmd
cd create-junbisyomen
python run_phase1_multi.py
```

---

### 🐧 Linux

#### 方法1: シェルスクリプトで起動

```bash
cd create-junbisyomen
bash start.sh
```

#### 方法2: 直接起動

```bash
cd create-junbisyomen
python3 run_phase1_multi.py
```

---

## 💡 便利な使い方

### エイリアスを設定（macOS/Linux）

毎回ディレクトリに移動するのが面倒な場合、エイリアスを設定：

```bash
# ~/.bashrc または ~/.zshrc に追加
alias junbi="cd ~/path/to/create-junbisyomen && python3 run_phase1_multi.py"
```

設定後、どこからでも `junbi` コマンドで起動できます！

### Dockに追加（macOS）

1. `start.command` を右クリック
2. 「Dockに追加」を選択
3. Dockから1クリックで起動！

---

## トラブルシューティング

### ❌ "can't open file ... No such file or directory"

**原因**: プロジェクトディレクトリに移動していない

**解決方法**:
```bash
# まずプロジェクトディレクトリに移動
cd ~/path/to/create-junbisyomen

# それから起動
python3 run_phase1_multi.py
```

または、`start.command` / `start.sh` / `start.bat` を使用してください（自動でディレクトリ移動します）

---

### ❌ "Python 3がインストールされていません"

**macOS:**
```bash
# Homebrewをインストール（まだの場合）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Python 3をインストール
brew install python@3
```

**Windows:**
- https://www.python.org/downloads/ からダウンロード
- インストール時に「Add Python to PATH」にチェック

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip
```

---

### ❌ "No module named 'google_auth_oauthlib'" または "No module named 'openai'"

**原因**: 依存パッケージがインストールされていない

**⚡ 推奨解決方法（自動インストール）**:
```bash
cd create-junbisyomen
bash setup.sh
```

**手動インストールの場合**:
```bash
cd create-junbisyomen
pip3 install -r requirements.txt
```

> 💡 **このエラーが出た場合は必ず `setup.sh` を実行してください！**
> 
> `start.sh` や `python3 run_phase1_multi.py` を実行する前に、
> まず `bash setup.sh` で依存パッケージをインストールする必要があります。

---

### ❌ ".envファイルが見つかりません"

**原因**: 環境変数ファイルが作成されていない

**解決方法**:
```bash
cd create-junbisyomen
cp .env.example .env
# .envファイルを編集してAPIキーを設定
```

または `setup.sh` / `setup.bat` を実行してください

---

### ❌ "OpenAI APIキーが設定されていません"

**原因**: `.env` ファイルにAPIキーが設定されていない

**解決方法**:
1. `.env` ファイルを開く
2. `OPENAI_API_KEY=your_key_here` の `your_key_here` を実際のAPIキーに置き換え
3. ファイルを保存

**APIキー取得**: https://platform.openai.com/api-keys

---

## 📚 次のステップ

起動できたら、次のドキュメントも確認してください：

- **README.md** - システム全体の概要
- **USAGE_GUIDE.md** - 詳細な操作ガイド
- **GOOGLE_DRIVE_GUIDE.md** - Google Drive連携設定

---

## 🆘 それでも問題が解決しない場合

GitHub Issuesで質問してください：
https://github.com/ogaiku-wospe/create-junbisyomen/issues

以下の情報を含めると早く解決できます：
- OS（macOS / Windows / Linux）
- Pythonバージョン（`python3 --version`）
- エラーメッセージ全文
- 実行したコマンド

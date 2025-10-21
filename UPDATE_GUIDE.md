# ローカルリポジトリ更新ガイド

このガイドでは、GitHubの最新版コードをローカルのディレクトリ `/Users/ogaiku/create-junbisyomen` に反映する方法を説明します。

## 📋 目次

1. [更新方法（推奨）](#更新方法推奨)
2. [更新スクリプトの使い方](#更新スクリプトの使い方)
3. [手動更新方法](#手動更新方法)
4. [トラブルシューティング](#トラブルシューティング)

---

## 🚀 更新方法（推奨）

### macOS / Linux の場合

```bash
cd /Users/ogaiku/create-junbisyomen
git pull origin fix/evidence-analysis-file-input
```

または、提供されている更新スクリプトを使用:

```bash
# このリポジトリの update_local_repo.sh をローカルにコピー
cp /path/to/webapp/update_local_repo.sh /Users/ogaiku/create-junbisyomen/

# 実行権限を付与
chmod +x /Users/ogaiku/create-junbisyomen/update_local_repo.sh

# 実行
/Users/ogaiku/create-junbisyomen/update_local_repo.sh
```

### macOS (ダブルクリック実行)

```bash
# .command ファイルをローカルにコピー
cp /path/to/webapp/update_local_repo.command /Users/ogaiku/create-junbisyomen/
cp /path/to/webapp/update_local_repo.sh /Users/ogaiku/create-junbisyomen/

# 実行権限を付与
chmod +x /Users/ogaiku/create-junbisyomen/update_local_repo.command
chmod +x /Users/ogaiku/create-junbisyomen/update_local_repo.sh

# ファイルをダブルクリックで実行
```

### Windows の場合

```cmd
cd C:\Users\[username]\create-junbisyomen
git pull origin fix/evidence-analysis-file-input
```

または、提供されている `update_local_repo.bat` をダブルクリックで実行

---

## 📦 更新スクリプトの使い方

### 1. スクリプトのコピー

このリポジトリには3つの更新スクリプトが用意されています:

- **update_local_repo.sh** - macOS/Linux用シェルスクリプト
- **update_local_repo.command** - macOS用（ダブルクリック実行可能）
- **update_local_repo.bat** - Windows用バッチファイル

これらのスクリプトを `/Users/ogaiku/create-junbisyomen` にコピーしてください。

### 2. スクリプトの実行

#### macOS / Linux (ターミナル)

```bash
cd /Users/ogaiku/create-junbisyomen
./update_local_repo.sh
```

#### macOS (ダブルクリック)

1. Finderで `/Users/ogaiku/create-junbisyomen` を開く
2. `update_local_repo.command` をダブルクリック
3. ターミナルウィンドウが開き、自動的に更新が実行されます

#### Windows (ダブルクリック)

1. エクスプローラーで `C:\Users\[username]\create-junbisyomen` を開く
2. `update_local_repo.bat` をダブルクリック
3. コマンドプロンプトウィンドウが開き、自動的に更新が実行されます

### 3. スクリプトの動作

更新スクリプトは以下の処理を実行します:

1. ✅ ローカルリポジトリの存在確認
2. 📍 現在のブランチ確認
3. ⚠️ コミットされていない変更の確認（ある場合は警告）
4. 🔄 リモートから最新情報を取得
5. ⬇️ 最新版をプル
6. 📊 更新内容の表示（変更されたファイル一覧、コミットログ）

---

## 🔧 手動更新方法

スクリプトを使わずに手動で更新する場合:

### Step 1: ローカルリポジトリに移動

```bash
cd /Users/ogaiku/create-junbisyomen
```

### Step 2: 現在の状態を確認

```bash
git status
```

### Step 3: コミットされていない変更がある場合

#### オプション A: 変更を保存してから更新

```bash
git stash                                    # 変更を一時保存
git pull origin fix/evidence-analysis-file-input  # 最新版を取得
git stash pop                                # 保存した変更を復元
```

#### オプション B: 変更を破棄して更新

```bash
git reset --hard HEAD                        # 変更を破棄
git pull origin fix/evidence-analysis-file-input  # 最新版を取得
```

### Step 4: 最新版を取得

```bash
git pull origin fix/evidence-analysis-file-input
```

### Step 5: 更新内容を確認

```bash
git log --oneline --graph --decorate -10     # 最新10件のコミット履歴
git diff HEAD@{1} HEAD                        # 変更差分の確認
```

---

## 🆘 トラブルシューティング

### エラー: "ディレクトリが見つかりません"

**原因**: `/Users/ogaiku/create-junbisyomen` が存在しない

**対処方法**:
```bash
# ディレクトリの存在確認
ls -la /Users/ogaiku/create-junbisyomen

# ディレクトリが存在しない場合は、正しいパスを確認
# または、GitHubからクローン
cd /Users/ogaiku
git clone https://github.com/ogaiku-wospe/create-junbisyomen.git
```

### エラー: "Gitリポジトリではありません"

**原因**: `.git` フォルダが存在しない

**対処方法**:
```bash
# Gitリポジトリとして初期化
cd /Users/ogaiku/create-junbisyomen
git init
git remote add origin https://github.com/ogaiku-wospe/create-junbisyomen.git
git fetch origin
git checkout fix/evidence-analysis-file-input
```

### エラー: "認証に失敗しました"

**原因**: GitHub認証が設定されていない

**対処方法**:
```bash
# GitHubトークンを使用した認証設定
git config --global credential.helper store
git pull origin fix/evidence-analysis-file-input

# プロンプトが表示されたら:
# Username: ogaiku-wospe
# Password: [GitHubトークン]
```

### エラー: "コンフリクトが発生しました"

**原因**: ローカルの変更とリモートの変更が衝突

**対処方法**:
```bash
# オプション 1: ローカルの変更を破棄
git reset --hard origin/fix/evidence-analysis-file-input

# オプション 2: 手動でコンフリクトを解決
git status                    # コンフリクトファイルを確認
# ファイルを編集してコンフリクトマーカー（<<<<<<<, =======, >>>>>>>）を削除
git add [解決したファイル]
git commit -m "Resolve conflicts"
git pull origin fix/evidence-analysis-file-input
```

### 警告: "コミットされていない変更があります"

**原因**: ローカルファイルが編集されている

**対処方法**:

#### オプション A: 変更を保持して更新
```bash
git stash                                    # 変更を一時保存
git pull origin fix/evidence-analysis-file-input
git stash pop                                # 変更を復元
```

#### オプション B: 変更を破棄して更新
```bash
git reset --hard HEAD
git pull origin fix/evidence-analysis-file-input
```

### エラー: "リモートブランチが見つかりません"

**原因**: ブランチ名が間違っているか、リモート情報が古い

**対処方法**:
```bash
# リモートブランチ一覧を確認
git branch -r

# リモート情報を更新
git fetch origin

# 正しいブランチに切り替え
git checkout fix/evidence-analysis-file-input
git pull origin fix/evidence-analysis-file-input
```

---

## 📚 参考情報

### 現在のコミット情報を確認

```bash
cd /Users/ogaiku/create-junbisyomen
git log -1 --oneline
```

### 最新10件のコミット履歴を確認

```bash
git log --oneline --graph --decorate -10
```

### 特定のファイルの変更履歴を確認

```bash
git log --follow -p -- run_phase1_multi.py
```

### ローカルとリモートの差分を確認

```bash
git fetch origin
git diff origin/fix/evidence-analysis-file-input
```

---

## ✅ 更新完了の確認

更新が正常に完了したら、以下を確認してください:

1. **最新のコミットハッシュ**
   ```bash
   git rev-parse --short HEAD
   ```

2. **現在のブランチ**
   ```bash
   git branch --show-current
   ```
   → `fix/evidence-analysis-file-input` と表示されるはずです

3. **ファイルの整合性**
   ```bash
   git status
   ```
   → `nothing to commit, working tree clean` と表示されるはずです

4. **動作確認**
   ```bash
   python3 run_phase1_multi.py
   ```
   または
   ```bash
   ./start.command  # macOS
   ```

---

## 🎯 最新の変更内容（2025年10月21日）

今回の更新で追加された主な機能:

### 1. メニューの再編成
- メニュー項目を1〜9の順番に並び替え
- より直感的なメニュー構成

### 2. 証拠一覧エクスポート機能（新機能）
- **CSV形式**: UTF-8 BOM エンコーディング、Excelで開きやすい
- **Excel形式**: カラフルな書式設定、フィルター機能付き
  - ステータス別の色分け（緑=確定済み、黄=整理済み_未確定、赤=未分類）
  - 分析状態の色分け（緑=分析済み、黄=未分析）
  - ヘッダー行の固定
  - 自動列幅調整

### 3. 例文の統一化
- すべてのユーザー入力例を `tmp_` 形式に統一
- より明確な操作ガイド

---

## 📞 サポート

問題が解決しない場合は、以下の情報を添えてお問い合わせください:

1. エラーメッセージ全文
2. 実行したコマンド
3. `git status` の出力
4. オペレーティングシステム（macOS / Linux / Windows）

---

**最終更新日**: 2025年10月21日

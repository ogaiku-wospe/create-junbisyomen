# GitHubから最新コードをローカルに反映する手順

このガイドでは、GitHubリポジトリの最新版を `/Users/ogaiku/create-junbisyomen` に反映させる方法を説明します。

---

## 🎯 目的

GitHub上の最新コード（mainブランチ）をローカルマシンにダウンロードして、最新機能を使用できるようにします。

---

## 📋 前提条件

- ローカルに `/Users/ogaiku/create-junbisyomen` ディレクトリが存在すること
- Gitがインストールされていること
- インターネット接続があること

---

## 🚀 更新手順

### 方法1: コマンドラインで更新（推奨）

ターミナルを開いて、以下のコマンドを実行してください。

#### Step 1: ローカルディレクトリに移動

```bash
cd /Users/ogaiku/create-junbisyomen
```

#### Step 2: 現在の状態を確認

```bash
# 現在のブランチを確認
git branch

# 変更されているファイルを確認
git status
```

**もし変更があれば**:
- 変更を保存したい場合: `git stash` で一時保存
- 変更を破棄する場合: `git restore .` で元に戻す

#### Step 3: 最新版を取得

```bash
# mainブランチに切り替え
git checkout main

# GitHubから最新版を取得
git pull origin main
```

#### Step 4: 依存関係を更新（必要に応じて）

```bash
# Pythonパッケージを更新
pip install -r requirements.txt

# または仮想環境を使用している場合
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

#### Step 5: 更新内容を確認

```bash
# 最新のコミットを確認
git log --oneline -5

# 新しいファイルを確認
ls -la
```

---

### 方法2: 完全に再クローン（クリーンインストール）

もし問題が発生した場合は、完全に再クローンすることもできます。

```bash
# 古いディレクトリをバックアップ
cd /Users/ogaiku
mv create-junbisyomen create-junbisyomen.backup

# 最新版をクローン
git clone https://github.com/ogaiku-wospe/create-junbisyomen.git
cd create-junbisyomen

# セットアップ
bash setup.sh
```

---

## 📦 最新版（v3.8.0）に含まれる新機能

### 🆕 時系列ストーリー組み立て機能

1. **Claude Sonnet 4統合**
   - 最新のClaude Sonnet 4 (claude-sonnet-4-20250514) を使用
   - 高品質な日本語ナラティブ生成

2. **database.json活用**
   - Phase1で分析された証拠データを完全活用
   - related_facts、legal_significance、temporal_informationを統合

3. **包括的依頼者情報機能**
   - 日付なし、複数事実にわたる全体的な文脈情報を管理
   - カテゴリー別整理（事件の背景、人物関係、全体的な経緯、その他）

4. **Google Drive自動アップロード**
   - エクスポートしたファイルを自動的にGoogle Driveにアップロード
   - 事件フォルダ内の `timeline` サブフォルダに保存
   - ウェブリンクを表示

5. **多様な出力形式**
   - JSON、Markdown、HTML、テキスト形式に対応
   - すべての形式で自動アップロード

---

## 🔧 新しいファイル

更新後、以下の新しいファイルが追加されます:

```
/Users/ogaiku/create-junbisyomen/
├── timeline_builder.py                    # 🆕 時系列ストーリー組み立てコア
├── TIMELINE_STORY_GUIDE.md               # 🆕 詳細な使用ガイド
├── IMPLEMENTATION_SUMMARY_TIMELINE.md    # 🆕 実装サマリー
├── test_timeline_builder.py              # 🆕 テストコード
└── UPDATE_LOCAL_FROM_GITHUB.md           # 🆕 このファイル
```

---

## ✅ 更新後の確認

### 1. プログラムを起動

```bash
cd /Users/ogaiku/create-junbisyomen
python3 run_phase1_multi.py
```

### 2. メニュー8を確認

メインメニューに **「8. 時系列ストーリー組み立て」** が表示されることを確認してください。

### 3. 機能をテスト

```
メインメニュー > 8 を選択
時系列ストーリーメニュー > 各機能を試す
```

---

## 🆘 トラブルシューティング

### エラー: "Your local changes would be overwritten"

**原因**: ローカルに未コミットの変更があります。

**解決策**:
```bash
# 変更を一時保存
git stash

# 最新版を取得
git pull origin main

# 必要なら変更を復元
git stash pop
```

### エラー: "fatal: refusing to merge unrelated histories"

**原因**: Gitの履歴が一致していません。

**解決策**:
```bash
# 強制的に最新版に更新
git fetch origin
git reset --hard origin/main
```

### Pythonパッケージのエラー

**解決策**:
```bash
# 依存関係を再インストール
pip install -r requirements.txt --upgrade

# または仮想環境を再作成
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📞 サポート

問題が解決しない場合は、以下を確認してください:

1. **Gitのバージョン**: `git --version` (2.0以上推奨)
2. **Pythonのバージョン**: `python3 --version` (3.8以上必要)
3. **ネットワーク接続**: `ping github.com`

---

## 📝 定期的な更新のベストプラクティス

### 毎回の作業前に実行

```bash
cd /Users/ogaiku/create-junbisyomen
git checkout main
git pull origin main
```

これで常に最新版で作業できます！

---

## 🎉 まとめ

1. ✅ ローカルディレクトリに移動: `cd /Users/ogaiku/create-junbisyomen`
2. ✅ mainブランチに切り替え: `git checkout main`
3. ✅ 最新版を取得: `git pull origin main`
4. ✅ プログラムを起動: `python3 run_phase1_multi.py`
5. ✅ 新機能を楽しむ: メニュー8「時系列ストーリー組み立て」

---

**Happy Coding! 🚀**

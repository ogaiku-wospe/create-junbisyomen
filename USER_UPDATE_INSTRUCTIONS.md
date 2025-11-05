# ユーザー向け: 最新版への更新手順

## 🎯 概要

インポートエラー（`No module named 'case_manager'`）を修正し、ファイル構造を整理した最新版がリリースされました。

---

## 🚀 更新手順（5分で完了）

### ステップ1: 最新コードを取得

```bash
cd ~/create-junbisyomen-3
git pull origin main
```

**期待される出力:**
```
リモート: Enumerating objects: X, done.
リモート: Counting objects: 100% (X/X), done.
リモート: Compressing objects: 100% (X/X), done.
更新 92e81a7..b6cb520
Fast-forward
 IMPORT_FIX.md         | 157 ++++++++++++++++++++++++++
 README.md             |   2 +
 batch_process.py      |   5 +
 run_phase1.py         |   5 +
 run_phase1_multi.py   |   5 +
 test_imports.py       | 145 ++++++++++++++++++++++++
```

### ステップ2: 仮想環境を再構築

```bash
# 既存の仮想環境を削除
rm -rf venv

# 新しい仮想環境を作成
python3 -m venv venv

# 仮想環境を有効化
source venv/bin/activate

# pipをアップグレード
pip install --upgrade pip

# 依存パッケージをインストール
pip install -r requirements.txt
```

**重要**: `pip install -r requirements.txt`は数分かかる場合があります。

### ステップ3: インポートテストを実行

```bash
python3 test_imports.py
```

**成功時の出力:**
```
======================================================================
  インポートテスト
======================================================================

プロジェクトルート: /Users/ogaiku/create-junbisyomen-3
Pythonバージョン: 3.11.5

モジュールのインポートをテスト中...
----------------------------------------------------------------------
✅ global_config                   のインポート成功 (設定ファイル)
✅ src.case_manager                のインポート成功 (事件管理)
✅ src.evidence_organizer          のインポート成功 (証拠整理)
✅ src.metadata_extractor          のインポート成功 (メタデータ抽出)
✅ src.file_processor              のインポート成功 (ファイル処理)
✅ src.ai_analyzer_complete        のインポート成功 (AI分析)
✅ src.evidence_editor_ai          のインポート成功 (証拠編集)
✅ src.timeline_builder            のインポート成功 (タイムライン構築)
----------------------------------------------------------------------

結果: 8/8 成功

🎉 すべてのモジュールのインポートに成功しました！

次のステップ:
  • マルチ事件対応版を実行: python3 run_phase1_multi.py
  • 単一事件版を実行: python3 run_phase1.py
  • 一括処理を実行: python3 batch_process.py --help
```

### ステップ4: システムを起動

```bash
python3 run_phase1_multi.py
```

または

```bash
python3 run_phase1.py
```

---

## ❓ よくある質問

### Q1: `git pull`で「Already up to date」と表示される

**回答**: すでに最新版です。次のステップ（仮想環境の再構築）に進んでください。

### Q2: `pip install`が失敗する

**回答**: 以下を試してください:

```bash
# pipをアップグレード
pip install --upgrade pip setuptools wheel

# 再度インストール
pip install -r requirements.txt
```

### Q3: test_imports.pyでエラーが出る

**回答**: エラーメッセージを確認してください:

#### `No module named 'google'`の場合:
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

#### `No module named 'PIL'`の場合:
```bash
pip install Pillow pillow-heif
```

#### それ以外のエラー:
[IMPORT_FIX.md](IMPORT_FIX.md)のトラブルシューティングセクションを参照してください。

### Q4: 仮想環境がアクティブになっているか確認したい

```bash
which python3
```

**期待される出力:**
```
/Users/ogaiku/create-junbisyomen-3/venv/bin/python3
```

パスに`venv`が含まれていればOKです。

### Q5: まだ「No module named 'case_manager'」エラーが出る

**確認事項:**

1. 正しいディレクトリにいるか:
```bash
pwd
# 出力: /Users/ogaiku/create-junbisyomen-3
```

2. `src`ディレクトリが存在するか:
```bash
ls -la src/
```

3. 最新コードを取得したか:
```bash
git log --oneline -1
# 出力に "fix: Python path configuration" が含まれているはず
```

---

## 📝 何が変更されたのか？

### 1. インポートエラーの修正

**問題**: ファイル構造を再編成した後、Pythonが`src/`パッケージを見つけられませんでした。

**解決**: すべてのメインスクリプトにプロジェクトルートをPythonパスに追加するコードを追加しました。

```python
# プロジェクトルートをPythonパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
```

### 2. ファイル構造の整理

以前は40以上のMarkdownファイルがルートディレクトリに散在していましたが、現在は整理されています:

```
プロジェクトルート/
├── README.md                 # メインドキュメント
├── QUICKSTART.md             # クイックスタート
├── IMPORT_FIX.md             # インポートエラー修正ガイド（新規）
├── FILE_STRUCTURE.md         # ファイル構造ガイド
├── REORGANIZATION_COMPLETE.md # 再編成の概要
├── test_imports.py           # インポートテストスクリプト（新規）
├── docs/                     # すべてのドキュメント（整理済み）
│   ├── user-guides/
│   ├── setup-guides/
│   ├── feature-guides/
│   ├── architecture/
│   └── ...
├── src/                      # Pythonソースコード
│   ├── __init__.py
│   ├── case_manager.py
│   ├── evidence_organizer.py
│   └── ...
└── scripts/                  # ユーティリティスクリプト
    ├── maintenance/
    ├── analysis/
    ├── setup/
    └── testing/
```

### 3. 新しいツール

- **test_imports.py**: すべての必要なモジュールが正しくインポートできるかを簡単にテスト
- **IMPORT_FIX.md**: インポートエラーのトラブルシューティングガイド

---

## 🆘 それでも解決しない場合

以下の診断情報を収集して開発者に共有してください:

```bash
# 診断スクリプト
echo "========== システム情報 =========="
echo "Pythonバージョン:"
python3 --version

echo -e "\n現在のディレクトリ:"
pwd

echo -e "\n仮想環境:"
which python3

echo -e "\n========== ディレクトリ構造 =========="
ls -la | head -20

echo -e "\n========== src ディレクトリ =========="
ls -la src/

echo -e "\n========== Gitログ（最新） =========="
git log --oneline -3

echo -e "\n========== インストールされているパッケージ =========="
pip list | grep -E "(google|openai|anthropic|Pillow)"

echo -e "\n========== Pythonパス =========="
python3 -c "import sys; print('\n'.join(sys.path[:5]))"

echo -e "\n========== インポートテスト =========="
python3 test_imports.py
```

---

## 📚 関連ドキュメント

- **[IMPORT_FIX.md](IMPORT_FIX.md)** - 詳細なトラブルシューティング
- **[FILE_STRUCTURE.md](FILE_STRUCTURE.md)** - 新しいファイル構造の詳細
- **[REORGANIZATION_COMPLETE.md](REORGANIZATION_COMPLETE.md)** - 再編成の概要
- **[QUICKSTART.md](QUICKSTART.md)** - 初めての方向けクイックスタート
- **[docs/README.md](docs/README.md)** - ドキュメント索引

---

## ✅ 更新完了チェックリスト

更新が正常に完了したことを確認するために、以下をチェックしてください:

- [ ] `git pull origin main` を実行した
- [ ] 仮想環境を再構築した (`rm -rf venv && python3 -m venv venv`)
- [ ] 仮想環境を有効化した (`source venv/bin/activate`)
- [ ] `requirements.txt` をインストールした (`pip install -r requirements.txt`)
- [ ] `test_imports.py` が成功した
- [ ] `run_phase1_multi.py` または `run_phase1.py` が起動する
- [ ] インポートエラーが発生しない

すべてにチェックが入れば、更新完了です！🎉

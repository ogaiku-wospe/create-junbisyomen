# インポートエラー修正ガイド

## 🔧 修正内容

### 問題
```
❌ エラー: モジュールのインポートに失敗しました: No module named 'case_manager'
```

### 原因
ファイル構造を再編成し、Pythonモジュールを`src/`ディレクトリに移動した後、Pythonが`src`パッケージを見つけられない問題がありました。

### 解決策
すべてのメインスクリプト（`run_phase1.py`, `run_phase1_multi.py`, `batch_process.py`）に以下のコードを追加しました:

```python
# プロジェクトルートをPythonパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
```

これにより、Pythonは`src/`ディレクトリからモジュールを正しくインポートできるようになります。

---

## 🚀 使用方法（ユーザー側の対応）

### 1. 最新コードを取得

```bash
cd ~/create-junbisyomen-3
git pull origin main
```

### 2. 仮想環境を再構築（推奨）

```bash
# 既存の仮想環境を削除
rm -rf venv

# 新しい仮想環境を作成
python3 -m venv venv

# 仮想環境を有効化
source venv/bin/activate

# 依存パッケージをインストール
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. インポートテストを実行

```bash
# テストスクリプトで確認
python3 test_imports.py
```

成功すると以下のように表示されます:
```
✅ global_config のインポート成功
✅ src.case_manager のインポート成功
✅ src.evidence_organizer のインポート成功
✅ src.metadata_extractor のインポート成功
✅ src.file_processor のインポート成功
✅ src.ai_analyzer_complete のインポート成功
✅ src.evidence_editor_ai のインポート成功
✅ src.timeline_builder のインポート成功

🎉 すべてのモジュールのインポートに成功しました！
```

### 4. システムを実行

```bash
# マルチ事件対応版を実行
python3 run_phase1_multi.py

# または、単一事件版を実行
python3 run_phase1.py
```

---

## 🔍 トラブルシューティング

### エラー1: `No module named 'google'`

**原因**: Google APIクライアントライブラリがインストールされていません。

**解決**:
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

または:
```bash
pip install -r requirements.txt
```

### エラー2: `No module named 'src.case_manager'`

**原因**: プロジェクトルートディレクトリから実行していない可能性があります。

**解決**:
```bash
# 正しいディレクトリに移動
cd ~/create-junbisyomen-3

# 現在のディレクトリを確認
pwd
# 出力: /Users/ogaiku/create-junbisyomen-3

# src ディレクトリが存在することを確認
ls -la src/
```

### エラー3: `ModuleNotFoundError: No module named 'PIL'`

**原因**: Pillowライブラリがインストールされていません。

**解決**:
```bash
pip install Pillow pillow-heif
```

### エラー4: 仮想環境がアクティブになっていない

**確認**:
```bash
which python3
# 出力例: /Users/ogaiku/create-junbisyomen-3/venv/bin/python3
```

**解決**:
```bash
source venv/bin/activate
```

---

## 📝 変更されたファイル

以下のファイルにPythonパス設定コードを追加しました:

1. `run_phase1_multi.py` - マルチ事件対応版メインスクリプト
2. `run_phase1.py` - 単一事件版メインスクリプト
3. `batch_process.py` - 一括処理スクリプト

---

## ✅ 確認事項チェックリスト

実行前に以下を確認してください:

- [ ] 最新コードを`git pull`で取得した
- [ ] 正しいディレクトリ（`~/create-junbisyomen-3`）にいる
- [ ] 仮想環境がアクティブになっている
- [ ] `requirements.txt`のパッケージがすべてインストールされている
- [ ] `src/`ディレクトリと`src/__init__.py`が存在する
- [ ] `.env`ファイルが設定されている
- [ ] `test_imports.py`が成功する

---

## 🆘 それでも解決しない場合

以下の情報を共有してください:

```bash
# 1. Pythonバージョン
python3 --version

# 2. 現在のディレクトリ
pwd

# 3. ディレクトリ構造
ls -la

# 4. src ディレクトリの内容
ls -la src/

# 5. インストールされているパッケージ
pip list | grep -E "(google|openai|anthropic)"

# 6. Pythonパス
python3 -c "import sys; print('\n'.join(sys.path))"

# 7. エラーメッセージの全文
python3 run_phase1_multi.py
```

---

## 📚 関連ドキュメント

- [FILE_STRUCTURE.md](FILE_STRUCTURE.md) - 新しいファイル構造の詳細
- [REORGANIZATION_COMPLETE.md](REORGANIZATION_COMPLETE.md) - 再編成の概要
- [docs/setup-guides/](docs/setup-guides/) - セットアップガイド

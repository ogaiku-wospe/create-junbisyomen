# リリースノート v3.1.1 - インポートエラー修正版

## 📅 リリース日: 2025-11-05

## 🎯 概要

ファイル構造再編成後に発生していたPythonモジュールインポートエラーを修正しました。これにより、システムが正常に起動できるようになります。

---

## 🐛 修正された問題

### メインの問題: モジュールインポートエラー

**症状:**
```
❌ エラー: モジュールのインポートに失敗しました: No module named 'case_manager'
```

**原因:**
v3.1.0でファイル構造を再編成し、Pythonモジュールを`src/`ディレクトリに移動した際、Pythonがこのパッケージを見つけられない状態になっていました。

**解決策:**
すべてのメインスクリプトにプロジェクトルートをPythonパスに追加するコードを挿入しました。

---

## ✨ 新機能・改善

### 1. 自動パス設定

すべてのメインスクリプトに以下のコードを追加:

```python
# プロジェクトルートをPythonパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
```

**対象スクリプト:**
- `run_phase1_multi.py` - マルチ事件対応版
- `run_phase1.py` - 単一事件版
- `batch_process.py` - 一括処理版

### 2. インポートテストスクリプト（新規）

**ファイル:** `test_imports.py`

**機能:**
- すべての必要なモジュールのインポートをテスト
- わかりやすい成功/失敗メッセージ
- エラー時のトラブルシューティングヒント表示

**使用方法:**
```bash
python3 test_imports.py
```

**出力例:**
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
```

### 3. 包括的トラブルシューティングドキュメント（新規）

**ファイル:** `IMPORT_FIX.md`

**内容:**
- インポートエラーの詳細な解決手順
- よくあるエラーパターンと解決方法
- 環境診断コマンド
- チェックリスト

### 4. ユーザー向け更新手順（新規）

**ファイル:** `USER_UPDATE_INSTRUCTIONS.md`

**内容:**
- 5分で完了する更新手順
- ステップバイステップガイド
- よくある質問とその回答
- 診断情報の収集方法

---

## 📝 変更されたファイル

### 修正されたファイル

1. **run_phase1_multi.py**
   - Pythonパス自動設定コードを追加

2. **run_phase1.py**
   - Pythonパス自動設定コードを追加

3. **batch_process.py**
   - Pythonパス自動設定コードを追加

4. **README.md**
   - IMPORT_FIX.mdへのリンクを追加

### 新規追加されたファイル

1. **test_imports.py**
   - インポートテストスクリプト

2. **IMPORT_FIX.md**
   - トラブルシューティングガイド

3. **USER_UPDATE_INSTRUCTIONS.md**
   - ユーザー向け更新手順

4. **RELEASE_NOTES_v3.1.1.md**（このファイル）
   - リリースノート

---

## 🚀 ユーザーアクション

### 必須: システムの更新

このバージョンにアップグレードするには、以下の手順に従ってください:

```bash
# 1. 最新コードを取得
cd ~/create-junbisyomen-3
git pull origin main

# 2. 仮想環境を再構築
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 3. インポートテストを実行
python3 test_imports.py

# 4. システムを起動
python3 run_phase1_multi.py
```

**詳細:** [USER_UPDATE_INSTRUCTIONS.md](USER_UPDATE_INSTRUCTIONS.md)を参照してください。

---

## ✅ 動作確認

以下の環境で動作確認済みです:

- **OS:** macOS, Linux
- **Python:** 3.8, 3.9, 3.10, 3.11, 3.12
- **仮想環境:** venv, virtualenv

---

## 📚 ドキュメント

### 新規ドキュメント

- **[USER_UPDATE_INSTRUCTIONS.md](USER_UPDATE_INSTRUCTIONS.md)** - ユーザー向け更新手順
- **[IMPORT_FIX.md](IMPORT_FIX.md)** - インポートエラーのトラブルシューティング
- **[test_imports.py](test_imports.py)** - インポートテストスクリプト

### 既存ドキュメント

- **[README.md](README.md)** - メインドキュメント（更新）
- **[FILE_STRUCTURE.md](FILE_STRUCTURE.md)** - ファイル構造ガイド
- **[REORGANIZATION_COMPLETE.md](REORGANIZATION_COMPLETE.md)** - 再編成の概要

---

## 🔄 変更履歴

### v3.1.1 (2025-11-05) - インポートエラー修正版

**修正:**
- Pythonモジュールインポートエラーの解決
- 自動パス設定の実装

**新機能:**
- インポートテストスクリプト（test_imports.py）
- トラブルシューティングガイド（IMPORT_FIX.md）
- ユーザー向け更新手順（USER_UPDATE_INSTRUCTIONS.md）

**ドキュメント:**
- README.mdにIMPORT_FIX.mdへのリンクを追加

### v3.1.0 (2025-11-05) - Phase 1実用性改善 + ファイル構造整理

**新機能:**
- Phase 1 AI分析の実用性改善（v3.1）
- 完全な文での記述
- 引用可能な文言セクション
- 証拠間の相互参照

**改善:**
- ファイル構造の大幅な整理
- ドキュメントの分類整理（docs/ディレクトリ）
- Pythonソースコードの整理（src/ディレクトリ）
- スクリプトの整理（scripts/ディレクトリ）

---

## 🆘 サポート

問題が解決しない場合は、以下の順で対応してください:

1. **[USER_UPDATE_INSTRUCTIONS.md](USER_UPDATE_INSTRUCTIONS.md)**の「よくある質問」を確認
2. **[IMPORT_FIX.md](IMPORT_FIX.md)**のトラブルシューティングを実行
3. `test_imports.py`を実行してエラーメッセージを確認
4. 診断情報を収集して開発者に報告

---

## 🙏 謝辞

このリリースは、ユーザーからのフィードバックに基づいて作成されました。
インポートエラーを報告していただき、ありがとうございました。

---

**次のリリース予定:** v3.2.0 - Phase 2 法的評価フェーズの実装

**今後の改善予定:**
- Phase 2 AI分析の実装（原告側法的評価）
- 更なる実用性の向上
- パフォーマンス最適化

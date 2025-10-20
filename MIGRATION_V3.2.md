# v3.2.0 移行ガイド: database.jsonをGoogle Driveで管理

## 📋 概要

v3.2.0から、database.jsonは完全にGoogle Driveで管理されるようになりました。ローカルファイルは不要です。

### 🎯 主な変更点

1. **Google Drive完全管理**: database.jsonは事件フォルダ内で管理
2. **ローカルファイル廃止**: ローカルdatabase.jsonは不要
3. **マルチデバイス対応**: 複数デバイスで同じデータベースにアクセス
4. **自動同期**: Google Driveの自動バックアップ機能を活用

## 🚀 移行手順

### ステップ1: 最新コードを取得

```bash
cd /Users/ogaiku/create-junbisyomen
git pull origin main
```

### ステップ2: ローカルdatabase.jsonをバックアップして削除

```bash
python3 cleanup_local_database.py
```

このスクリプトは以下を実行します:
- ローカルdatabase.jsonを`local_backup/`にバックアップ
- ローカルファイルを削除
- 確認プロンプトを表示

**実行例:**
```
==================================================================
  ローカルdatabase.jsonクリーンアップ
==================================================================

📁 検出: database.json
   サイズ: 45678 bytes
   最終更新: 2025-10-20 12:34:56

📦 バックアップ先: local_backup/database_20251020_123456.json

ローカルdatabase.jsonを削除しますか？ (y/n): y

✅ バックアップ完了: local_backup/database_20251020_123456.json
✅ ローカルdatabase.json削除完了

==================================================================
  クリーンアップ完了
==================================================================

📝 今後について:
  - database.jsonはGoogle Driveで管理されます
  - ローカルファイルは不要になりました
  - バックアップは local_backup/ に保存されています
```

### ステップ3: システムを起動

```bash
python3 run_phase1_multi.py
```

初回起動時、Google Drive上に自動的にdatabase.jsonが作成されます。

### ステップ4: 動作確認（オプション）

```bash
python3 test_gdrive_database.py
```

テストスクリプトで以下を確認:
- Google Driveからの読み込み
- データベース構造の検証
- 証拠統計の表示

## 📊 新しいデータフロー

### v3.1.0以前（ローカル管理）

```
システム起動
    ↓
ローカルdatabase.json読み込み
    ↓
証拠分析・整理
    ↓
ローカルdatabase.json保存
    ↓
（Google Driveとの同期なし）
```

### v3.2.0以降（Google Drive管理）

```
システム起動
    ↓
Google Drive認証
    ↓
database.json読み込み（Google Driveから）
    ↓
証拠分析・整理
    ↓
database.json保存（Google Driveへ）
    ↓
✅ 自動的に他のデバイスでも利用可能
```

## 🔧 技術詳細

### GDriveDatabaseManager クラス

新しく追加された`gdrive_database_manager.py`モジュール:

```python
from gdrive_database_manager import GDriveDatabaseManager, create_database_manager

# マネージャー作成
db_manager = create_database_manager(case_manager, case_info)

# データベース読み込み
database = db_manager.load_database()

# データベース保存
db_manager.save_database(database)

# 証拠操作
evidence = db_manager.get_evidence_by_id("ko001")
all_pending = db_manager.get_all_evidence(status='pending')
next_number = db_manager.get_next_evidence_number('ko')
```

### 主要メソッド

| メソッド | 説明 |
|---------|------|
| `load_database()` | Google Driveから読み込み |
| `save_database(database)` | Google Driveへ保存 |
| `get_evidence_by_id(id)` | 証拠IDで検索 |
| `get_all_evidence(status)` | 全証拠取得（フィルタ可） |
| `add_evidence(data)` | 証拠追加 |
| `update_evidence(id, updates)` | 証拠更新 |
| `delete_evidence(id)` | 証拠削除 |
| `get_next_evidence_number(side)` | 次の証拠番号取得 |
| `get_next_temp_number()` | 次の仮番号取得 |

### 変更されたファイル

1. **gdrive_database_manager.py** (新規)
   - Google Drive上のdatabase.json管理クラス

2. **evidence_organizer.py**
   - `db_manager`を初期化に追加
   - `_load_database_from_gdrive()`を`db_manager.load_database()`に置き換え
   - `_save_database_to_gdrive()`を`db_manager.save_database()`に置き換え

3. **run_phase1_multi.py**
   - `db_manager`を初期化に追加（事件選択後）
   - `load_database()`を`db_manager.load_database()`に置き換え
   - `save_database()`を`db_manager.save_database()`に置き換え

4. **cleanup_local_database.py** (新規)
   - ローカルdatabase.jsonのバックアップ&削除ツール

5. **test_gdrive_database.py** (新規)
   - 動作確認用テストスクリプト

## 💡 利点

### 1. マルチデバイス対応
- 自宅のPC、職場のPC、ノートPCで同じデータベースにアクセス
- リアルタイムで最新データを参照

### 2. 自動バックアップ
- Google Driveの版管理機能を活用
- ファイルが破損してもGoogleが自動で復元

### 3. ストレージ管理
- ローカルディスクの容量を節約
- 大規模な証拠データベースでも問題なし

### 4. セキュリティ
- Google Driveの強固なセキュリティ
- 暗号化通信で安全にアクセス

## ⚠️ 注意事項

### インターネット接続が必要
- database.jsonの読み書きにはインターネット接続が必要
- オフラインでは動作しません

### 初回起動時の認証
- Google Drive APIの認証が必要
- `credentials.json`が必要（初回のみ）

### パフォーマンス
- ローカルファイルよりわずかに遅い（ネットワーク経由）
- 通常の使用では問題ないレベル

## 🔙 ロールバック方法

v3.1.0に戻す場合:

```bash
# 古いバージョンをチェックアウト
git checkout a9978ae

# または特定のコミットに戻す
git revert HEAD

# バックアップから復元
cp local_backup/database_*.json database.json
```

## 📞 トラブルシューティング

### Q1: "database.json検索エラー"が表示される

**原因**: Google Drive APIの認証に失敗

**解決策**:
1. `credentials.json`が存在することを確認
2. `token.json`を削除して再認証: `rm token.json`
3. システムを再起動

### Q2: データが表示されない

**原因**: 異なる事件フォルダを参照している可能性

**解決策**:
1. メニューで「6. 事件を切り替え」を選択
2. 正しい事件を選択
3. データベースを確認

### Q3: 保存エラーが発生する

**原因**: Google Driveの容量不足または権限不足

**解決策**:
1. Google Driveの容量を確認
2. 共有ドライブの書き込み権限を確認
3. ネットワーク接続を確認

### Q4: ローカルdatabase.jsonとの不整合

**原因**: 移行前のローカルファイルが残っている

**解決策**:
1. `cleanup_local_database.py`を実行
2. `local_backup/`フォルダを確認
3. 必要に応じてGoogle Drive上のdatabase.jsonを手動更新

## 📚 関連ドキュメント

- [README.md](README.md) - システム概要
- [README_MULTI_CASE.md](README_MULTI_CASE.md) - マルチ事件対応ガイド
- [USAGE_GUIDE.md](USAGE_GUIDE.md) - 詳細な使用方法

## 🎯 今後の予定

- [ ] オフラインモードのサポート（キャッシュ機能）
- [ ] database.jsonの差分同期
- [ ] 複数ユーザーの同時編集対応
- [ ] 変更履歴の可視化

---

**バージョン**: 3.2.0  
**リリース日**: 2025年10月20日  
**互換性**: v3.1.0以降のシステムで動作

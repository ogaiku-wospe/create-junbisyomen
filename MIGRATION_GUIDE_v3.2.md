# v3.2.0 移行ガイド - database.jsonのGoogle Drive管理

## 📋 概要

v3.2.0から、database.jsonをGoogle Driveで管理するようになりました。これにより以下のメリットがあります:

- ✅ **複数デバイスで同期**: Mac、Windows、Linuxから同じデータベースにアクセス
- ✅ **自動バックアップ**: Google Driveの自動バックアップ機能を利用
- ✅ **ローカルストレージ不要**: ディスク容量を節約
- ✅ **リアルタイム更新**: 最新データに常にアクセス

## 🔄 移行手順

### ステップ1: 最新版を取得

```bash
cd /Users/ogaiku/create-junbisyomen
git pull origin main
```

### ステップ2: ローカルdatabase.jsonをバックアップして削除

```bash
python3 cleanup_local_database.py
```

このスクリプトは:
- ローカルdatabase.jsonを `local_backup/` フォルダにバックアップ
- ローカルファイルを削除
- 確認プロンプトを表示

### ステップ3: システムを起動

```bash
python3 run_phase1_multi.py
```

初回起動時:
1. 事件を選択または新規作成
2. Google Drive上の事件フォルダ内にdatabase.jsonが自動作成されます
3. 以降、全ての読み書きはGoogle Driveで直接実行されます

## 🎯 新しい動作

### データベースの場所

**以前（v3.1.x）:**
```
/Users/ogaiku/create-junbisyomen/database.json  ← ローカル
```

**現在（v3.2.0）:**
```
Google Drive/
└── 共有ドライブ/
    └── meiyokison_名誉毀損事件/
        └── database.json  ← Google Drive上
```

### 読み込み・保存の動作

**以前:**
1. ローカルdatabase.jsonを読み込み
2. Google Driveにバックアップ（オプション）

**現在:**
1. Google Driveから直接読み込み
2. Google Driveに直接保存
3. ローカルキャッシュなし

## 🔍 技術詳細

### 新規ファイル

#### `gdrive_database_manager.py`

Google Drive上のdatabase.jsonを管理するヘルパークラス:

```python
from gdrive_database_manager import GDriveDatabaseManager, create_database_manager

# 初期化
db_manager = create_database_manager(case_manager, case_info)

# 読み込み
database = db_manager.load_database()

# 保存
db_manager.save_database(database)

# 証拠の取得
evidence = db_manager.get_evidence_by_id('ko001')

# 証拠の追加
db_manager.add_evidence(evidence_data)
```

主なメソッド:
- `load_database()`: Google Driveからdatabase.jsonを読み込み
- `save_database(database)`: Google Driveにdatabase.jsonを保存
- `get_evidence_by_id(evidence_id)`: IDで証拠を取得
- `get_all_evidence(status)`: 全証拠を取得（ステータスでフィルタ可能）
- `add_evidence(evidence_data)`: 証拠を追加
- `update_evidence(evidence_id, updates)`: 証拠を更新
- `delete_evidence(evidence_id)`: 証拠を削除
- `get_next_evidence_number(side)`: 次の証拠番号を取得
- `get_next_temp_number()`: 次の仮番号を取得

### 変更されたファイル

#### `evidence_organizer.py`

- `GDriveDatabaseManager`をインポート
- 初期化時に`self.db_manager`を作成
- `_load_database_from_gdrive()`と`_save_database_to_gdrive()`をシンプル化

#### `run_phase1_multi.py`

- `GDriveDatabaseManager`をインポート
- `self.db_manager`フィールドを追加
- 事件選択/作成時に`db_manager`を初期化
- `load_database()`と`save_database()`をシンプル化

## ⚠️ 重要な注意事項

### 1. インターネット接続が必要

database.jsonの読み書きにはインターネット接続が必要です。オフライン環境では使用できません。

### 2. Google Drive APIの制限

Google Drive APIには以下の制限があります:
- 1ユーザーあたり1日1,000リクエスト
- 読み取り: 1秒あたり10リクエスト
- 書き込み: 1秒あたり10リクエスト

通常の使用では問題ありませんが、大量の証拠を一度に処理する場合は注意してください。

### 3. 同時編集の制御

複数デバイスから同時に同じdatabase.jsonを編集すると、最後の保存が上書きされます。
複数デバイスで作業する場合は、時間をずらして使用することを推奨します。

### 4. バックアップの重要性

Google Driveに依存するため、以下のバックアップを推奨します:

```bash
# 定期的にエクスポート
python3 run_phase1_multi.py
# メニューで「5. database.jsonの状態確認」を選択
```

## 🐛 トラブルシューティング

### Q1: `❌ Google Drive認証が必要です`

**原因**: credentials.jsonが見つからない、またはtokenが期限切れ

**解決策**:
```bash
# tokenを削除して再認証
rm token.pickle
python3 run_phase1_multi.py
```

### Q2: `❌ database.json読み込みエラー`

**原因**: Google Drive上のdatabase.jsonが破損している

**解決策**:
1. ローカルバックアップから復元:
```bash
# local_backup/ にバックアップがあるか確認
ls local_backup/

# 最新のバックアップを確認
python3 -c "
import json
with open('local_backup/database_YYYYMMDD_HHMMSS.json') as f:
    data = json.load(f)
    print('✅ バックアップファイルは正常です')
"
```

2. 手動でGoogle Driveにアップロード

### Q3: `⚠️ データベースマネージャーの初期化に失敗`

**原因**: 事件フォルダIDが正しくない、またはGoogle Drive認証エラー

**解決策**:
1. global_config.pyのSHARED_DRIVE_ROOT_IDを確認
2. Google Drive APIが有効化されているか確認
3. credentials.jsonが正しく配置されているか確認

### Q4: ローカルとGoogle Driveのデータが異なる

**原因**: 古いローカルdatabase.jsonが残っている

**解決策**:
```bash
# ローカルdatabase.jsonを削除
rm database.json

# システムを再起動
python3 run_phase1_multi.py
```

## 📊 パフォーマンスへの影響

### 読み込み時間

- **ローカル（v3.1.x）**: 〜10ms
- **Google Drive（v3.2.0）**: 〜200-500ms

database.jsonのサイズが大きくなると、Google Driveからの読み込みに時間がかかる場合があります。

### 対策

将来的に以下の最適化を検討:
- [ ] ローカルキャッシュの実装（オプション）
- [ ] 差分更新の実装
- [ ] バッチ処理の最適化

## 🔮 今後の予定

### v3.3.0（予定）
- [ ] ローカルキャッシュのオプション実装
- [ ] オフラインモードのサポート
- [ ] 同時編集の競合解決機能

### v3.4.0（予定）
- [ ] database.jsonの自動バックアップ（ローカル）
- [ ] エクスポート/インポート機能の強化

## 📞 サポート

問題が発生した場合:
1. このガイドのトラブルシューティングを確認
2. [GitHub Issues](https://github.com/ogaiku-wospe/create-junbisyomen/issues) を検索
3. 新しいIssueを作成

---

**バージョン**: 3.2.0  
**最終更新**: 2025年10月20日

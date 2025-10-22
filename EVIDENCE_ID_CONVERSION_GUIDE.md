# 証拠ID変換ガイド

database.json内の証拠IDを一括変換するツールです。

---

## 🎯 目的

Google Drive上のdatabase.jsonに記録されている証拠IDを変換します。

**変換内容**: `tmp_` → `tmp_ko_`

**例**:
- `tmp_001` → `tmp_ko_001`
- `tmp_015` → `tmp_ko_015`
- `tmp_021` → `tmp_ko_021`

---

## 🚀 使用方法

### 方法1: Pythonスクリプト直接実行（推奨）

```bash
cd /home/user/webapp
python3 convert_evidence_ids.py
```

### 方法2: シェルスクリプト実行

```bash
cd /home/user/webapp
bash convert_ids.sh
```

---

## 📋 実行の流れ

### Step 1: 事件の確認

```
======================================================================
  証拠ID変換ツール
  database.json: tmp_ → tmp_ko_
======================================================================

📁 事件: test_損害賠償請求事件 (test_case_001)
```

### Step 2: データベース読み込み

```
======================================================================
  Google DriveからDatabase.jsonを読み込み中...
======================================================================
✅ 読み込み成功: 21件の証拠
```

### Step 3: バックアップ作成

```
💾 バックアップ作成: /home/user/webapp/local_storage/test_case_001/backups/database_backup_20251022_150000.json
```

### Step 4: 確認プロンプト

```
変換内容: tmp_ → tmp_ko_
この操作を実行すると、Google Drive上のdatabase.jsonが更新されます。

続行しますか？ (y/n):
```

**`y` を入力して続行**

### Step 5: 証拠ID変換

```
======================================================================
  証拠IDを変換中: tmp_ → tmp_ko_
======================================================================
  ✓ tmp_001              → tmp_ko_001
  ✓ tmp_002              → tmp_ko_002
  ✓ tmp_003              → tmp_ko_003
  ...
  ✓ tmp_021              → tmp_ko_021

✅ 変換完了: 21件
```

### Step 6: プレビュー表示

```
======================================================================
  変換後のプレビュー
======================================================================
  1. tmp_ko_001           甲tmp_ko_001              tmp_001_甲10_2021年8-10月_IMG_6482.HEIC
  2. tmp_ko_002           甲tmp_ko_002              tmp_002_甲9_2021年8-10月_IMG_0357.PNG
  ...
 10. tmp_ko_010           甲tmp_ko_010              tmp_010_甲3.png

... 他 11 件

総件数: 21件
```

### Step 7: 最終確認

```
======================================================================
Google Driveに保存しますか？ (y/n):
```

**`y` を入力して保存**

### Step 8: 完了

```
======================================================================
  Google Driveにアップロード中...
======================================================================
✅ アップロード成功

======================================================================
  ✅ 変換完了！
======================================================================

変換件数: 21件
バックアップ: /home/user/webapp/local_storage/test_case_001/backups/database_backup_20251022_150000.json

次回からは以下の形式で入力してください:
  例: tmp_ko_001-021
```

---

## 🔒 安全機能

### 1. 自動バックアップ

変換前に必ずローカルにバックアップを作成します。

**保存場所**: `{LOCAL_STORAGE_DIR}/{case_id}/backups/database_backup_YYYYMMDD_HHMMSS.json`

### 2. 二段階確認

- 変換実行前に確認
- Google Drive保存前に確認

### 3. プレビュー表示

保存前に変換結果を確認できます。

---

## 📊 変換される項目

### 1. evidence_id

```json
{
  "evidence_id": "tmp_001"  →  "evidence_id": "tmp_ko_001"
}
```

### 2. evidence_number

```json
{
  "evidence_number": "甲tmp_001"  →  "evidence_number": "甲tmp_ko_001"
}
```

### 3. metadata.last_updated

変換実行時刻に自動更新されます。

---

## ⚠️ 注意事項

### 1. 事件選択が必要

実行前に `run_phase1_multi.py` で事件を選択しておいてください。

```bash
python3 run_phase1_multi.py
# メニューから事件を選択
```

### 2. 既存のtmp_ko_は無視

既に `tmp_ko_` で始まる証拠IDは変換されません（重複変換を防止）。

### 3. Google Drive接続が必要

- インターネット接続が必要です
- Google Drive APIの認証が完了している必要があります

---

## 🆘 トラブルシューティング

### エラー: "事件が選択されていません"

**解決策**:
```bash
python3 run_phase1_multi.py
# メニュー10で事件を選択
# その後、再度変換スクリプトを実行
```

### エラー: "database.jsonの読み込みに失敗"

**原因**: Google Drive接続の問題

**解決策**:
1. インターネット接続を確認
2. Google Drive認証を再実行
3. `run_phase1_multi.py` でdatabase.jsonの状態を確認

### エラー: "アップロード失敗"

**解決策**:
1. バックアップは保存されているので安心
2. Google Drive接続を確認
3. 再度スクリプトを実行
4. バックアップから手動で復元も可能

---

## 🔄 バックアップからの復元

もし問題が発生した場合は、バックアップから復元できます。

### 手動復元方法

1. バックアップファイルを確認
```bash
ls -la /home/user/webapp/local_storage/{case_id}/backups/
```

2. バックアップをコピー
```bash
cp /home/user/webapp/local_storage/{case_id}/backups/database_backup_YYYYMMDD_HHMMSS.json /tmp/database_restore.json
```

3. Google Driveに手動アップロード
   - Google Driveのウェブインターフェースから事件フォルダにアップロード
   - またはGDriveDatabaseManagerを使用

---

## 📝 実行後の確認

### 1. プログラムで確認

```bash
python3 run_phase1_multi.py
# メニュー9: database.jsonの状態確認
```

### 2. 証拠番号で実行

```bash
python3 run_phase1_multi.py
# メニュー2: 証拠分析
# 甲号証を選択
# 証拠番号入力: tmp_ko_001-021  ← 新しい形式で入力
```

---

## ✅ 成功の確認

変換が成功すると:

1. ✅ Google Drive上のdatabase.jsonが更新される
2. ✅ 証拠IDが `tmp_ko_001`, `tmp_ko_002`, ... に変更される
3. ✅ 証拠番号が `甲tmp_ko_001`, `甲tmp_ko_002`, ... に変更される
4. ✅ バックアップがローカルに保存される

次回からは `tmp_ko_001-021` の形式で証拠を指定できます！

---

## 🎉 まとめ

```bash
# 実行
cd /home/user/webapp
python3 convert_evidence_ids.py

# 確認
python3 run_phase1_multi.py
# メニュー2 → 甲号証 → tmp_ko_001-021
```

これで証拠IDが統一され、使いやすくなります！

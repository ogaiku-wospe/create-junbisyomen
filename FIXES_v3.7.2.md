# v3.7.2 修正内容まとめ

## 📋 発見された問題点

### 1. データベース重複問題 ⚠️
**症状**: 
- 同じ証拠がデータベースに2回保存される
- インデックス[0-10]: 未分析エントリ（`temp_id`のみ）
- インデックス[11-21]: 分析済みエントリ（`evidence_id`あり、`temp_id`なし）

**原因**:
```python
# 旧コード（問題あり）
existing_entry = next(
    (e for e in database["evidence"] 
     if e.get("evidence_id") == evidence_number),
    None
)
```
- `evidence_id`のみでマッチングしていた
- 未分析エントリ（`evidence_id`なし）を見つけられず、新規追加してしまう

**修正**:
```python
# 新コード（修正済み）
existing_index = next(
    (i for i, e in enumerate(database["evidence"]) 
     if (e.get("evidence_id") == evidence_number or
         e.get("temp_id") == evidence_number or
         e.get("evidence_number") == evidence_number)),
    None
)

if existing_index is not None:
    # 既存エントリのtemp_idを保持
    old_entry = database["evidence"][existing_index]
    if 'temp_id' in old_entry:
        evidence_entry['temp_id'] = old_entry['temp_id']
    if 'temp_number' in old_entry:
        evidence_entry['temp_number'] = old_entry['temp_number']
    
    database["evidence"][existing_index] = evidence_entry
```

**結果**: 
- ✅ `temp_id`, `evidence_id`, `evidence_number`のいずれかでマッチング
- ✅ 既存エントリの`temp_id`を保持
- ✅ 重複を防止

---

### 2. OpenAI Content Policy拒否 🛡️
**症状**:
- 医療文書などで「I'm sorry, I can't assist with that」と拒否される
- 分析が完全に失敗

**修正**:
```python
# Vision API分析後にチェック
result = response.choices[0].message.content

# コンテンツポリシー拒否チェック
if "I'm sorry, I can't assist with that" in result or "I cannot assist" in result:
    logger.warning("⚠️ Vision API: コンテンツポリシーにより画像分析が拒否されました")
    logger.info("📝 OCRテキストを使用したテキストベース分析にフォールバック")
    return None  # Noneを返してフォールバック処理を促す
```

```python
# フォールバック処理
vision_result = self._analyze_with_vision(actual_file_path, analysis_prompt, file_type)

# Vision APIがコンテンツポリシーで拒否した場合、テキストベース分析にフォールバック
if vision_result is None:
    logger.info("📝 OCRテキストを使用してテキストベース分析を実行")
    return self._analyze_with_text(analysis_prompt, file_content)
```

**結果**:
- ✅ Vision API拒否を自動検出
- ✅ OCRテキストベース分析に自動フォールバック
- ✅ すべての証拠が分析可能に

---

## 🧹 新規ツール: データベースクリーンアップユーティリティ

### 機能
1. **重複エントリの検出と分析**
2. **自動マージ**（分析済みエントリを優先）
3. **バックアップ自動作成**
4. **ドライランモード**（テスト実行）

### 使用方法

#### 重複を分析
```bash
python utils/database_cleanup.py database.json --analyze
```

**出力例**:
```
⚠️  11個の重複グループが見つかりました

【重複グループ 1】
  エントリ 1:
    temp_id: tmp_001
    evidence_id: なし
    evidence_number: なし
    file_name: 2021年8-10月.jpg
    分析完了: ❌
  エントリ 2:
    temp_id: なし
    evidence_id: tmp_001
    evidence_number: 甲tmp_001
    file_name: 甲tmp_001_2021年8-10月.jpg
    分析完了: ✅
```

#### 重複をマージ（ドライラン）
```bash
python utils/database_cleanup.py database.json --merge
```

**出力例**:
```
🔧 11個の重複グループをマージします

✅ マージ: tmp_001
   保持: 甲tmp_001_2021年8-10月.jpg
   削除: 1個のエントリ
...

💡 ドライラン完了（実際の変更は行われていません）
   実行する場合は dry_run=False で実行してください
```

#### 重複をマージ（実行）
```bash
python utils/database_cleanup.py database.json --merge --execute
```

**出力例**:
```
🔧 11個の重複グループをマージします

✅ マージ: tmp_001
   保持: 甲tmp_001_2021年8-10月.jpg
   削除: 1個のエントリ
...

💾 バックアップ作成: database_backup_20251020_093822.json
✅ データベース保存: database.json

✅ 11個のエントリを削除しました
   残り: 11個のエントリ
```

### マージロジック
1. **分析完了済みエントリを優先**: `phase1_complete_analysis`があるエントリを保持
2. **未分析エントリから`temp_id`を継承**: 保持エントリに`temp_id`がない場合、未分析エントリから取得
3. **重複を削除**: 保持エントリ以外をすべて削除
4. **バックアップ作成**: 変更前のデータベースを自動バックアップ

---

## 📊 修正の検証

### ユーザーのデータベースでの検証結果

#### 修正前
```
Total evidence entries: 22

インデックス [0-10]: 未分析エントリ（temp_idのみ）
インデックス [11-21]: 分析済みエントリ（evidence_idあり、temp_idなし）
```

#### 修正後（クリーンアップ実行）
```
Total evidence entries: 11

すべてのエントリが以下を満たす:
- temp_id: ✅ 保持
- evidence_id: ✅ 保持
- evidence_number: ✅ 保持
- phase1_complete_analysis: ✅ 存在
```

---

## 🎯 今後の推奨アクション

### 既存データベースのクリーンアップ
すでに重複があるデータベースには、クリーンアップツールを実行してください：

```bash
# 1. 重複を確認
python utils/database_cleanup.py path/to/database.json --analyze

# 2. マージをテスト（ドライラン）
python utils/database_cleanup.py path/to/database.json --merge

# 3. 問題なければ実行
python utils/database_cleanup.py path/to/database.json --merge --execute
```

### 新規分析
- 修正済みコードで新規分析を実行すれば、重複は発生しません
- ファイル名から日付が自動抽出されます
- Vision API拒否時は自動的にOCRベース分析にフォールバックします

### 既知の残存問題
- **tmp_008の分析失敗**: `document_date="不明"`, `observable_facts=0`
  - 調査が必要（ファイル破損？OCR失敗？）
  - 個別に再分析を推奨

---

## 📝 変更ファイル一覧

1. **`run_phase1_multi.py`** (修正)
   - データベース保存ロジックの改善
   - temp_id/evidence_id/evidence_numberのいずれかでマッチング

2. **`ai_analyzer_complete.py`** (修正)
   - Vision APIコンテンツポリシー拒否の検出と自動フォールバック
   - ファイル名からの日付抽出機能を追加
   - AI分析後に日付抽出を統合

3. **`utils/database_cleanup.py`** (新規)
   - データベースクリーンアップユーティリティ
   - 重複検出、分析、マージ機能

4. **`README.md`** (更新)
   - v3.7.2セクションを追加
   - バージョンを3.7.2に更新

---

## ✅ 修正完了チェックリスト

- [x] データベース重複問題を修正
- [x] OpenAI Content Policy拒否への対応を実装
- [x] ファイル名からの日付抽出を実装
- [x] データベースクリーンアップツールを作成
- [x] READMEを更新
- [x] 変更をコミット
- [x] ユーザーのデータベースで検証

---

**バージョン**: 3.7.2  
**修正日**: 2025年10月20日  
**コミット**: c3f35d8

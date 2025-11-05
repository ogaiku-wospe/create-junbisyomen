# 証拠ステータス表示問題の修正

## 🐛 問題の説明

**症状**: 証拠が「整理済み_未確定」フォルダにあるのに、証拠一覧で「未分類」として表示される

**原因**: 証拠の`status`フィールドを整理状態として誤って使用していた

### 2つの異なる「status」概念

1. **分析状態** (`status`フィールド): 
   - `"completed"`: 分析完了
   - `"pending"`: 分析中
   - `"error"`: エラー
   
2. **整理状態** (フォルダ位置による):
   - `"確定済み"`: 甲号証/乙号証フォルダ内
   - `"整理済み_未確定"`: tmp_xxx形式のID
   - `"未分類"`: その他

**問題**: コードが`status`フィールドを整理状態として扱っていた

---

## ✅ 修正内容

### 修正1: `show_evidence_list()` メソッド

**修正前**:
```python
for evidence in filtered_evidence:
    status = evidence.get('status', '未分類')  # ❌ 分析状態を取得
    if status == '確定済み':
        confirmed_evidence.append(evidence)
```

**修正後**:
```python
for evidence in filtered_evidence:
    evidence_id = evidence.get('evidence_id', '')
    evidence_number = evidence.get('evidence_number', '')
    
    # 整理状態を判定 ✅
    if evidence_number and not evidence_number.startswith('甲tmp') and not evidence_number.startswith('乙tmp'):
        confirmed_evidence.append(evidence)  # 確定済み
    elif evidence_id.startswith('tmp_'):
        pending_evidence.append(evidence)  # 整理済み_未確定
    else:
        unclassified_evidence.append(evidence)  # 未分類
```

### 修正2: CSVエクスポート (`_export_to_csv()`)

**修正前**:
```python
status_order.get(x.get('status', '未分類'), 99)  # ❌
```

**修正後**:
```python
def get_organization_status(evidence):
    """証拠の整理状態を判定"""
    evidence_id = evidence.get('evidence_id', '')
    evidence_number = evidence.get('evidence_number', '')
    
    if evidence_number and not evidence_number.startswith('甲tmp') and not evidence_number.startswith('乙tmp'):
        return '確定済み'
    elif evidence_id.startswith('tmp_'):
        return '整理済み_未確定'
    else:
        return '未分類'

status_order.get(get_organization_status(x), 99)  # ✅
```

### 修正3: Excelエクスポート (`_export_to_excel()`)

CSVエクスポートと同じ修正を適用。

---

## 📊 整理状態の判定ロジック

### 確定済み

**条件**: 
- `evidence_number`が存在
- `evidence_number`が`"甲tmp"`や`"乙tmp"`で始まらない

**例**:
- `evidence_number: "甲1"` → 確定済み ✅
- `evidence_number: "乙5"` → 確定済み ✅
- `evidence_number: "甲tmp_001"` → 確定済みではない ❌

### 整理済み_未確定

**条件**:
- `evidence_id`が`"tmp_"`で始まる

**例**:
- `evidence_id: "tmp_001"` → 整理済み_未確定 ✅
- `evidence_id: "tmp_ko_015"` → 整理済み_未確定 ✅
- `evidence_id: "ko_001"` → 整理済み_未確定ではない ❌

### 未分類

**条件**:
- 上記のどちらにも当てはまらない

---

## 🧪 テスト

### テストケース1: 整理済み_未確定の証拠

**database.json**:
```json
{
  "evidence_id": "tmp_ko_001",
  "evidence_number": "甲tmp_ko_001",
  "status": "completed"
}
```

**期待される表示**:
```
【整理済み_未確定】
----------------------------------------------------------------------
  tmp_ko_001 | 2021-08-15 | ✅ 分析済み     | example.pdf
```

### テストケース2: 確定済みの証拠

**database.json**:
```json
{
  "evidence_id": "ko_001",
  "evidence_number": "甲1",
  "status": "completed"
}
```

**期待される表示**:
```
【確定済み（甲号証）】
----------------------------------------------------------------------
  ko_001     | 2021-08-15 | ✅ 分析済み     | example.pdf
```

### テストケース3: 未分類の証拠

**database.json**:
```json
{
  "evidence_id": "unknown_001",
  "evidence_number": "",
  "status": "pending"
}
```

**期待される表示**:
```
【未分類】
----------------------------------------------------------------------
  unknown_001 | example.pdf
```

---

## ✅ 修正後の動作

1. ✅ 証拠一覧（メニュー5）が正しく表示される
2. ✅ CSVエクスポートで正しい整理状態が記録される
3. ✅ Excelエクスポートで正しい整理状態が記録される
4. ✅ `tmp_`で始まる証拠IDは「整理済み_未確定」として表示される

---

## 🚀 更新方法

```bash
cd /Users/ogaiku/create-junbisyomen
git pull origin main
python3 run_phase1_multi.py
```

メニュー5で証拠一覧を確認してください。

---

## 📝 今後の注意点

### データベース設計

将来的には、整理状態を明示的なフィールドとして追加することを検討:

```json
{
  "evidence_id": "tmp_ko_001",
  "evidence_number": "甲tmp_ko_001",
  "analysis_status": "completed",  // 分析状態
  "organization_status": "整理済み_未確定",  // 整理状態
  "folder_location": "整理済み_未確定",  // フォルダ位置
  "status": "completed"  // 後方互換性のため維持
}
```

これにより、判定ロジックが不要になり、コードがシンプルになります。

---

## 🔗 関連ファイル

- `run_phase1_multi.py`: メイン修正箇所
  - `show_evidence_list()` (Line 1461)
  - `_export_to_csv()` (Line 1618)
  - `_export_to_excel()` (Line 1698)

---

修正完了！🎉

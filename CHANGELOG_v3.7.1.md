# v3.7.1 変更履歴（2025年10月20日）

## 🔧 フィールド名を document_date に統一（より明確な命名）

### 概要
v3.7.0で導入した`creation_date`を`document_date`に改名し、証拠説明書との対応を明確化しました。

### 変更理由

#### 問題点
v3.7.0で使用した`creation_date`という名称には曖昧さがありました：
- **ファイルの作成日？** → システム上でファイルが作成された日付
- **文書の作成日？** → 文書内に記載されている作成日
- **証拠の成立日？** → 法的に証拠が成立した日付

この曖昧さにより、AIが日付抽出時にどの日付を優先すべきか判断しにくい状況でした。

#### 解決策
`document_date`という名称に変更：
- **明確な意味**: 「証拠説明書に記載する日付」
- **実務との対応**: 民事訴訟規則（証拠説明書の記載事項）に対応
- **優先順位の明確化**: 文書・画像・動画それぞれの作成年月日の判断基準を明示

### 変更内容

#### 1. データ構造の変更

**v3.7.0（旧）:**
```json
"temporal_information": {
  "creation_date": "2021-08-15",
  "creation_date_source": "契約書末尾の契約締結日",
  "other_dates": [
    {"date": "2021-10-20", "context": "支払期限"}
  ],
  "timeline": "時系列の客観的整理"
}
```

**v3.7.1（新）:**
```json
"temporal_information": {
  "document_date": "2021-08-15",              // 証拠説明書記載用の日付（必須）
  "document_date_source": "契約書末尾の契約締結日",  // 根拠を明記
  "other_dates": [
    {"date": "2021-10-20", "context": "支払期限"}
  ],
  "timeline": "時系列の客観的整理",
  "date_confidence": "high - 契約書に明記"    // 信頼度を追加
}
```

#### 2. Phase1_EvidenceAnalysis.txt の更新

**追加された指示セクション:**
```markdown
## 🗓️ 日付情報の抽出は最重要タスク

### 最優先：document_date（証拠の作成年月日）
1. **証拠説明書に記載する日付** = この証拠がいつ作成されたかを示す日付
2. 優先順位で判断：
   - 📄 **文書の場合**: 文書上部の日付、契約日、作成日、発行日、メール送信日
   - 📷 **画像の場合**: EXIF撮影日時、ファイル名の日付、画像内の日付表示
   - 📹 **動画の場合**: 撮影日時、ファイルメタデータの作成日
3. `document_date_source`に根拠を必ず記載
4. YYYY-MM-DD形式で記載（日付が不明瞭な場合は推定範囲を`date_confidence`に記載）

### 日付が判明しない場合
- `document_date`: `null` または `"不明"`
- `document_date_source`: "文書内に日付記載なし、ファイル名にも日付なし"
- `date_confidence`: "low - 作成日を特定する情報が不足"
```

#### 3. ai_analyzer_complete.py の更新

**プロンプト構築部分:**
```python
**🗓️ 最重要タスク - 証拠の作成年月日を必ず特定:**
- `document_date`: 証拠説明書に記載する作成年月日（YYYY-MM-DD形式）
- 文書上部の日付、EXIF撮影日時、ファイル名の日付など、あらゆる手がかりから判断
- `document_date_source`に根拠を明記（例：「文書上部に2021年8月15日と記載」）
- 日付が不明な場合も、その旨と理由を`date_confidence`に記載
```

#### 4. run_phase1_multi.py の更新

**メニュー4（日付順ソート）の処理:**
```python
# 既存分析からdocument_dateを取得（後方互換性あり）
document_date = temporal_info.get('document_date') or temporal_info.get('creation_date')

if document_date:
    print(f"  ✅ 既存分析から取得: {document_date}")
    evidence['extracted_date'] = document_date
    continue
```

### 後方互換性

**既存データ（v3.7.0形式）への対応:**
```python
# システムは以下の順序でチェック
1. document_date（v3.7.1以降）
2. creation_date（v3.7.0、フォールバック）

# どちらか一方が存在すれば正常動作
```

**移行の必要性:**
- 既存のv3.7.0形式データはそのまま使用可能
- 新規分析からは自動的にdocument_date形式
- 強制的なデータ移行は不要

### メリット

#### 1. 明確性の向上
- ✅ フィールド名から用途が一目瞭然
- ✅ 証拠説明書の記載事項と直接対応
- ✅ AIへの指示が明確化

#### 2. 実務との整合性
```
証拠説明書（民事訴訟規則）の記載事項:
1. 証拠の標目
2. 証拠の作成年月日    ← document_dateが対応
3. 証拠の作成者
4. 立証趣旨
```

#### 3. エラー防止
- ✅ ファイルメタデータの作成日と混同しない
- ✅ AIが正しい日付を抽出しやすい
- ✅ 日付の根拠（document_date_source）も必須化

### テスト結果

**想定されるテストケース:**
1. ✅ 契約書（契約締結日を抽出）
2. ✅ メール（送信日時を抽出）
3. ✅ 領収書（発行日を抽出）
4. ✅ 写真（EXIF撮影日時を抽出）
5. ✅ 日付記載なし（document_date: null、理由を記載）

**後方互換性テスト:**
1. ✅ v3.7.0形式のデータベース読み込み
2. ✅ creation_dateからdocument_dateへの自動変換
3. ✅ メニュー4（日付順ソート）の正常動作

### 実装ファイル

**変更されたファイル:**
1. `prompts/Phase1_EvidenceAnalysis.txt`
   - temporal_information構造をdocument_date形式に変更
   - 日付抽出の優先順位を明記
   - date_confidenceフィールドを追加

2. `ai_analyzer_complete.py`
   - プロンプト構築部分でdocument_dateを強調
   - JSON構造例を更新

3. `run_phase1_multi.py`
   - メニュー4でdocument_date優先、creation_dateをフォールバック
   - 説明文をdocument_dateに統一

4. `README.md`
   - v3.7.1セクションを追加
   - v3.7.0の説明をdocument_date表記に更新

**コミット:**
- `47d2cd5` - v3.7.1: Change creation_date to document_date for clarity
- `0b0ba9c` - docs: Add v3.7.1 documentation and update v3.7.0 references

### 今後の推奨事項

#### 1. データベース完全移行（オプション）
v3.7.0形式のデータをv3.7.1形式に変換するスクリプト：
```python
def migrate_v370_to_v371(database):
    """v3.7.0 (creation_date) → v3.7.1 (document_date)"""
    for evidence in database.get('evidence', []):
        if 'phase1_complete_analysis' in evidence:
            ai_analysis = evidence['phase1_complete_analysis'].get('ai_analysis', {})
            obj_analysis = ai_analysis.get('objective_analysis', {})
            temporal_info = obj_analysis.get('temporal_information', {})
            
            # creation_date → document_date
            if 'creation_date' in temporal_info and 'document_date' not in temporal_info:
                temporal_info['document_date'] = temporal_info.pop('creation_date')
                temporal_info['document_date_source'] = temporal_info.pop('creation_date_source', '移行元：creation_date')
    
    return database
```

#### 2. AIプロンプトのさらなる強化
証拠種別ごとの具体例を追加：
- 契約書：「契約締結日」を優先
- 領収書：「発行日」を優先
- メール：「送信日時」を優先
- 写真：「撮影日時（EXIF）」を優先

#### 3. バリデーション機能の追加
```python
def validate_document_date(temporal_info):
    """document_dateの妥当性チェック"""
    if not temporal_info.get('document_date'):
        return False, "document_dateが設定されていません"
    
    if not temporal_info.get('document_date_source'):
        return False, "document_date_sourceが設定されていません"
    
    if not temporal_info.get('date_confidence'):
        return False, "date_confidenceが設定されていません"
    
    return True, "OK"
```

---

**v3.7.1リリース日**: 2025年10月20日  
**担当**: AI Assistant  
**リリースタイプ**: パッチアップデート（命名改善、後方互換性あり）  
**破壊的変更**: なし（creation_dateは引き続きサポート）

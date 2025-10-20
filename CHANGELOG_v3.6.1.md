# v3.6.1 変更履歴（2025年10月20日）

## 📅 通常の証拠分析での日付抽出機能を強化

### 概要
v3.6.0で定義された`objective_analysis.temporal_information`構造を、実際にAIが確実に記入するよう改善しました。

### 問題点
- v3.6.0では`temporal_information`の**データ構造のみ定義**
- AIが実際にこのフィールドを埋めるための**明示的指示が不足**
- 結果：通常の証拠分析（メニュー2/3）で日付情報が抽出されないケースが多発
- 回避策：メニュー8で別途日付抽出処理が必要だった

### 修正内容

#### 1. Phase1_EvidenceAnalysis.txt の強化

**変更箇所：重要情報の抽出（line 62-66）**
```diff
- 4. **重要情報の抽出**
-    - 日付（複数ある場合はすべて）
+ 4. **重要情報の抽出（特に日付情報は必須）**
+    - **日付（最優先）**: 複数ある場合はすべて抽出し、各日付の意味（契約日、作成日、有効期限等）も記録
```

**変更箇所：temporal_information構造（line 151-155）**
```diff
  "temporal_information": {
-   "dates_mentioned": ["文書に記載されている日付1", "日付2", ...],
-   "date_context": "各日付の文脈（契約日、作成日、有効期限等）",
-   "timeline": "時系列の客観的整理"
+   "dates_mentioned": ["文書に記載されている日付1（YYYY-MM-DD形式推奨）", "日付2", ...],
+   "date_context": "各日付の文脈（契約日、作成日、有効期限、発行日、署名日等）を明確に記載",
+   "timeline": "時系列の客観的整理（複数の日付がある場合、時系列順に並べる）",
+   "primary_date": "証拠の代表日付（最も重要な日付、例：契約日、発行日）をYYYY-MM-DD形式で記載"
  }
```

**新規追加：日付情報の重要性を強調（line 207-212）**
```markdown
## 🗓️ 日付情報の抽出は特に重要
**temporal_informationフィールドは必ず詳細に記入してください:**
1. 文書や画像から読み取れる全ての日付を`dates_mentioned`に記載
2. 各日付の意味・文脈を`date_context`に明確に記述
3. 最も重要な日付を`primary_date`にYYYY-MM-DD形式で記載
4. 日付が全く記載されていない場合のみ空配列`[]`とし、その旨を`date_context`に明記
```

#### 2. ai_analyzer_complete.py の強化

**変更箇所：分析指示（line 201-206）**
```diff
  **重要:** 
  - 証拠に記載されている事実のみを記録
  - 法的評価や主観的解釈は一切含めない
  - 訴訟の当事者や事件の詳細は知らない前提で分析
  - あなたは中立的な記録者として振る舞う
+ - **日付情報（temporal_information）は必ず詳細に抽出してください**
```

**変更箇所：JSON構造をobjective_analysis形式に更新（line 224-260）**
- 旧形式の`legal_significance`構造を削除
- 新形式の`objective_analysis`構造に置き換え
- `temporal_information`に`primary_date`フィールドを追加

### 期待される効果

#### 1. ワークフローの簡素化
**従来（v3.6.0まで）:**
```
tmp証拠を分析（メニュー2/3）
  ↓
日付情報は抽出されない
  ↓
別途日付抽出（メニュー8）が必要
  ↓
date_extractionフィールドに記録
  ↓
日付順ソート
```

**新方式（v3.6.1以降）:**
```
tmp証拠を分析（メニュー2/3）
  ↓
日付情報も同時に抽出（temporal_informationに記録）
  ↓
既に日付情報があるのでメニュー8は不要
  ↓
temporal_information.primary_dateで直接ソート可能
```

#### 2. データの一貫性向上
- 日付情報が確実にdatabase.jsonに記録される
- `date_extraction`と`temporal_information`の二重管理が不要に
- 単一のデータソースで証拠ソートが可能

#### 3. ユーザビリティ向上
- 通常分析後、即座に日付順ソートが可能
- 追加の日付抽出処理が不要
- database.jsonを見れば日付情報が一目瞭然

### データ構造の変更

```json
// v3.6.1以降のtemporal_information構造
{
  "objective_analysis": {
    "temporal_information": {
      "dates_mentioned": ["2021-08-15", "2021-10-20"],
      "date_context": "2021-08-15は契約日、2021-10-20は支払期限",
      "timeline": "2021年8月15日に契約締結、同年10月20日が支払期限として設定された",
      "primary_date": "2021-08-15"  // 🆕 追加：証拠の代表日付
    }
  }
}
```

### 実装ファイル

**変更されたファイル:**
1. `prompts/Phase1_EvidenceAnalysis.txt` - プロンプトの強化
2. `ai_analyzer_complete.py` - プロンプト構築ロジックの更新
3. `README.md` - v3.6.1ドキュメントの追加

**コミット:**
- `0f6e575` - v3.6.1: Enhanced date extraction in regular evidence analysis
- `9c050ff` - docs: Add v3.6.1 documentation for enhanced date extraction

### 今後の課題

1. **既存データの移行**
   - 旧形式（legal_significance）で分析済みの証拠を新形式（objective_analysis）に変換するツールの作成
   - 既存の`date_extraction`データを`temporal_information`にマージ

2. **ソート機能の最適化**
   - メニュー8を`temporal_information.primary_date`優先に変更
   - `date_extraction`フィールドはフォールバックとして保持

3. **テストとバリデーション**
   - 実際の証拠でv3.6.1のプロンプトをテスト
   - 日付抽出率の検証
   - エッジケース（日付なし、複数日付）の動作確認

### 関連Issue・PR

- 関連する質問: 「証拠分析の段階でdatabase.jsonに日付情報は記載されないのですか」
- 修正前の状態: `temporal_information`構造は定義済みだが、AIが実際に記入する指示が不足
- 修正後の状態: プロンプトで明示的に日付抽出を指示、`primary_date`フィールドも追加

---

**v3.6.1リリース日**: 2025年10月20日  
**担当**: AI Assistant  
**リリースタイプ**: マイナーアップデート（機能強化）

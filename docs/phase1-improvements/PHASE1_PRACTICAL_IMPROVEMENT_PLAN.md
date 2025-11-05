# Phase 1 AI分析の実用性向上計画

## 🎯 改善目標

**主目的**: Phase 1のAI分析出力を、準備書面作成時に**そのまま使える**レベルに改善する

**重要制約**: 完全な客観性と中立性を維持（法的評価は一切含めない）

---

## 📊 現状分析

### 現在のプロンプトの強み
1. ✅ **客観性の徹底**: Phase 1 = 中立的記録という原則が明確
2. ✅ **完全言語化レベル4**: 原文参照不要という高い目標設定
3. ✅ **包括的な分析項目**: 画像・文書の詳細分析要件が網羅的
4. ✅ **時間情報重視**: document_dateの重要性が強調されている

### 実用性の課題（準備書面作成時の観点から）

#### 問題点1: 出力が「羅列」になりやすい
**現状**:
```json
"observable_facts": [
  "証拠から観察できる客観的事実1",
  "客観的事実2",
  "客観的事実3"
]
```

**課題**:
- 事実が箇条書きで羅列されるだけで、文脈や関連性が不明
- 準備書面に引用する際、追加で文章化・構造化する必要がある
- **どの事実が重要か、どの順序で記述すべきか**の判断が必要

**理想**:
```json
"observable_facts": {
  "structured_facts": [
    {
      "fact_id": "fact_001",
      "category": "document_basic_info",
      "fact_statement": "本証拠は、2021年8月15日付で甲野太郎氏から乙山花子氏宛に送付された契約解除通知書である。",
      "source_location": "文書上部のタイトルおよび日付欄",
      "confidence": "high",
      "related_facts": ["fact_002", "fact_003"]
    },
    {
      "fact_id": "fact_002",
      "category": "content_substance",
      "fact_statement": "通知書には、令和3年7月1日付で締結された売買契約（契約番号：ABC-2021-0701）を、同年8月31日をもって解除する旨が記載されている。",
      "source_location": "本文第1段落",
      "confidence": "high",
      "related_facts": ["fact_001", "fact_004"]
    }
  ],
  "fact_summary": "本証拠は契約解除通知書であり、2021年8月15日付で発行され、同年7月1日締結の売買契約を同年8月31日に解除する旨が記載されている。",
  "chronological_sequence": ["契約締結(2021-07-01)", "通知発行(2021-08-15)", "解除予定日(2021-08-31)"]
}
```

#### 問題点2: 当事者情報が断片的
**現状**:
```json
"parties_mentioned": {
  "individuals": ["甲野太郎", "乙山花子"],
  "organizations": ["ABC株式会社"],
  "roles_described": "文書内で各当事者の記述"
}
```

**課題**:
- 名前の羅列だけで、**文書内での役割や立場**が明確でない
- 準備書面で「誰が何をした」を記述する際、情報が不十分
- 連絡先、肩書き、関係性などの情報が散逸

**理想**:
```json
"parties_mentioned": {
  "detailed_parties": [
    {
      "party_id": "party_001",
      "name": "甲野太郎",
      "type": "individual",
      "role_in_document": "通知書の発信者",
      "attributes": {
        "address": "東京都千代田区○○1-2-3",
        "title": "契約当事者（売主）",
        "contact": "記載なし"
      },
      "actions_described": [
        "契約解除通知の発送",
        "違約金の請求"
      ],
      "first_appearance": "文書上部の差出人欄"
    },
    {
      "party_id": "party_002",
      "name": "乙山花子",
      "type": "individual",
      "role_in_document": "通知書の受信者",
      "attributes": {
        "address": "大阪府大阪市○○1-2-3",
        "title": "契約当事者（買主）",
        "contact": "記載なし"
      },
      "actions_described": [
        "契約違反（支払遅延）"
      ],
      "first_appearance": "文書上部の宛先欄"
    }
  ],
  "relationships": [
    {
      "from": "party_001",
      "to": "party_002",
      "relationship": "売買契約における売主と買主",
      "basis": "本文第1段落の記載"
    }
  ],
  "party_summary": "甲野太郎（売主・発信者）から乙山花子（買主・受信者）への通知"
}
```

#### 問題点3: 金額情報の文脈不足
**現状**:
```json
"financial_information": {
  "amounts": ["500,000円", "50,000円"],
  "currency": "JPY",
  "amount_context": "各金額の文脈"
}
```

**課題**:
- 金額の羅列だけで、**何の金額か、支払済みか未払いか**が不明確
- 準備書面で主張する際、追加の文脈補足が必要

**理想**:
```json
"financial_information": {
  "detailed_amounts": [
    {
      "amount_id": "amt_001",
      "amount_value": 500000,
      "amount_display": "500,000円",
      "currency": "JPY",
      "amount_type": "contract_price",
      "description": "売買契約における売買代金の総額",
      "payment_status": "partially_paid",
      "payment_details": "300,000円は既払い、残200,000円は未払い",
      "due_date": "2021-07-31",
      "source_location": "本文第2段落、契約書第5条",
      "related_parties": ["party_001", "party_002"],
      "confidence": "high"
    },
    {
      "amount_id": "amt_002",
      "amount_value": 50000,
      "amount_display": "50,000円",
      "currency": "JPY",
      "amount_type": "penalty",
      "description": "契約違反による違約金",
      "payment_status": "unpaid_claimed",
      "due_date": "2021-08-31",
      "source_location": "本文第3段落",
      "related_parties": ["party_001", "party_002"],
      "confidence": "high"
    }
  ],
  "total_claimed": 250000,
  "total_paid": 300000,
  "financial_summary": "売買代金500,000円のうち300,000円既払い、残額200,000円および違約金50,000円（計250,000円）が未払い"
}
```

#### 問題点4: 時系列情報が分散している
**現状**:
```json
"temporal_information": {
  "document_date": "2021-08-15",
  "other_dates": [
    {"date": "2021-07-01", "context": "契約締結日"},
    {"date": "2021-08-31", "context": "解除予定日"}
  ],
  "timeline": "時系列の客観的整理"
}
```

**課題**:
- `timeline`フィールドが文字列なので、プログラムで処理しにくい
- 準備書面の「事実経緯」セクション作成時に、追加の構造化が必要
- 証拠間の時系列比較が困難

**理想**:
```json
"temporal_information": {
  "document_date": "2021-08-15",
  "document_date_source": "文書上部に「令和3年8月15日」と明記",
  "date_confidence": "high",
  "all_dates_structured": [
    {
      "date_id": "date_001",
      "date": "2021-07-01",
      "date_type": "contract_signing",
      "description": "売買契約の締結日",
      "participants": ["party_001", "party_002"],
      "source_location": "本文第1段落「令和3年7月1日付で締結された」",
      "confidence": "high"
    },
    {
      "date_id": "date_002",
      "date": "2021-07-31",
      "date_type": "payment_deadline",
      "description": "売買代金の支払期限",
      "participants": ["party_002"],
      "source_location": "本文第2段落「支払期限である同年7月31日」",
      "confidence": "high"
    },
    {
      "date_id": "date_003",
      "date": "2021-08-15",
      "date_type": "document_creation",
      "description": "本通知書の作成・発送日",
      "participants": ["party_001"],
      "source_location": "文書上部の日付欄",
      "confidence": "high"
    },
    {
      "date_id": "date_004",
      "date": "2021-08-31",
      "date_type": "contract_termination",
      "description": "契約解除の効力発生予定日",
      "participants": ["party_001", "party_002"],
      "source_location": "本文第1段落「同年8月31日をもって解除する」",
      "confidence": "high"
    }
  ],
  "chronological_summary": "2021年7月1日に契約締結、同年7月31日が支払期限、8月15日に解除通知発送、8月31日に解除予定",
  "timeline_visualization": [
    {"date": "2021-07-01", "event": "契約締結", "event_type": "contract_signing"},
    {"date": "2021-07-31", "event": "支払期限", "event_type": "deadline"},
    {"date": "2021-08-15", "event": "解除通知発送（本証拠）", "event_type": "notice"},
    {"date": "2021-08-31", "event": "解除予定", "event_type": "termination"}
  ]
}
```

#### 問題点5: document_stateの実用性不足
**現状**:
```json
"document_state": {
  "completeness": "完全",
  "modifications": "訂正なし",
  "annotations": "手書きメモあり",
  "preservation_state": "良好"
}
```

**課題**:
- 概略的な記述で、**実際に何がどこにあるか**が不明
- 準備書面で証拠の真正性や完全性を論じる際、詳細が不足

**理想**:
```json
"document_state": {
  "completeness": {
    "status": "complete",
    "description": "全4ページが揃っている",
    "missing_parts": null,
    "page_count": 4
  },
  "modifications": {
    "has_modifications": false,
    "details": []
  },
  "annotations": {
    "has_annotations": true,
    "details": [
      {
        "annotation_id": "anno_001",
        "type": "handwritten_note",
        "location": "第2ページ右上余白",
        "content": "「至急対応」との手書きメモ",
        "ink_color": "青色",
        "estimated_date": "文書作成後に追記されたと推定"
      }
    ]
  },
  "preservation_state": {
    "overall_condition": "good",
    "details": "紙質・印字ともに鮮明、汚損・破損なし",
    "authenticity_indicators": [
      "社印の押印あり（第4ページ右下）",
      "連続ページ番号あり（各ページ下部）",
      "一貫したフォーマット"
    ]
  },
  "physical_characteristics": {
    "format": "A4縦用紙、横書き",
    "printing_method": "レーザープリンター出力と推定",
    "paper_quality": "一般的なコピー用紙"
  }
}
```

---

## 🎯 改善方針

### 基本原則
1. **完全な客観性の維持**: 法的評価や主観的解釈は一切含めない
2. **構造化の徹底**: 準備書面作成時のプログラム処理を想定した構造
3. **即引用可能性**: AI出力を最小限の編集で準備書面に転用できる
4. **文脈の明示**: 各情報の出典と関連性を明確化

### 具体的改善項目

#### 改善1: observable_factsの構造化
- **現状**: 配列による箇条書き
- **改善後**: 各事実にID、カテゴリ、完全な文としての記述、出典を付与
- **効果**: 準備書面の「証拠の内容」セクションに直接引用可能

#### 改善2: parties_mentionedの詳細化
- **現状**: 名前の羅列
- **改善後**: 各当事者の役割、属性、行為、関係性を構造化
- **効果**: 準備書面の「関係者」セクションや事実記載に直接使用可能

#### 改善3: financial_informationの文脈化
- **現状**: 金額の羅列
- **改善後**: 各金額の種類、支払状況、期日、関連当事者を明記
- **効果**: 請求の根拠や損害額の主張に直接使用可能

#### 改善4: temporal_informationの時系列構造化
- **現状**: 部分的な構造化
- **改善後**: 全日付を時系列配列化、各日付にイベント情報を付与
- **効果**: 準備書面の「事実経緯」タイムライン作成が自動化可能

#### 改善5: document_stateの詳細化
- **現状**: 概略的な記述
- **改善後**: 各要素（完全性、訂正、注釈、保存状態）を詳細に構造化
- **効果**: 証拠の真正性・信用性の主張に使用可能

#### 改善6: extracted_dataの実用化
- **現状**: 概念的な羅列
- **改善後**: 各項目（条件、義務、権利、例外）を文書内の記載と紐付け
- **効果**: 契約解釈や権利義務の主張に直接使用可能

#### 改善7: 新セクション追加 - quotable_statements
- **目的**: 準備書面で引用すべき重要文言を完全抽出
- **内容**: 
  ```json
  "quotable_statements": [
    {
      "quote_id": "quote_001",
      "statement": "「本契約は、令和3年8月31日をもって解除します。」",
      "location": "本文第1段落第3文",
      "context": "契約解除の意思表示",
      "verbatim": true,
      "language": "japanese",
      "emphasis": "none"
    }
  ]
  ```

#### 改善8: 新セクション追加 - cross_reference_potential
- **目的**: 他の証拠との照合ポイントを示唆（客観的事実として）
- **内容**:
  ```json
  "cross_reference_potential": [
    {
      "reference_id": "ref_001",
      "this_evidence_element": "契約番号：ABC-2021-0701",
      "potential_related_evidence": "元となる契約書（存在すれば）",
      "matching_criteria": "契約番号の一致",
      "objective_note": "本証拠に記載されている契約番号を持つ他の証拠が存在する場合、相互参照が可能"
    }
  ]
  ```

---

## 📋 実装計画

### ステップ1: プロンプト改善
**ファイル**: `prompts/Phase1_EvidenceAnalysis.txt`

**追加・変更内容**:
1. 出力形式の詳細化（上記の構造化フィールドを追加）
2. 各フィールドの記述例を具体的に提示
3. 「準備書面に引用できる文として記述する」ことを明示
4. 文脈と出典を常に明記するよう指示

### ステップ2: スキーマ更新
**ファイル**: `database_schema_v3.json`

**追加・変更内容**:
1. `objective_analysis`内の各フィールドを詳細化
2. 新セクション`quotable_statements`を追加
3. 新セクション`cross_reference_potential`を追加
4. 各フィールドのJSON型定義を詳細化

### ステップ3: AI分析エンジン更新
**ファイル**: `ai_analyzer_complete.py`

**追加・変更内容**:
1. プロンプト構築ロジックの調整（新フィールドの説明追加）
2. 分析結果の検証ロジック追加（必須フィールドのチェック）
3. 品質評価基準の更新（構造化度合いを評価）

### ステップ4: テストとドキュメント
1. サンプル証拠で改善版を試行
2. 出力結果の実用性を検証
3. 使用例ドキュメントの作成

---

## 🎯 期待される効果

### Phase 2（法的分析）での効果
- AIが構造化されたデータから法的意義を抽出しやすくなる
- 証拠間の関連性分析が自動化可能
- タイムライン自動生成が可能

### 準備書面作成での効果
- 証拠説明書の「内容」欄に直接転記可能
- 事実経緯セクションの自動生成が可能
- 主張セクションの根拠として引用が容易

### データベース活用での効果
- 複数証拠からの情報統合が容易
- 金額の集計・分析が自動化
- 時系列の可視化が可能

---

## 📝 注意事項

### 客観性の維持
- 全ての改善は「観察可能な事実の構造化」に限定
- 「～と推認される」「～の可能性がある」などの推測は含めない
- ただし、「文書の記載から推定できる客観的情報」は記録可（例：「印刷方法はレーザープリンターと推定」）

### 過度な構造化の回避
- 構造化のために情報を捏造しない
- 文書に記載がない項目は`null`または`"記載なし"`とする
- 推測が必要な場合は、`estimated: true`フラグを付与

### 実用性とのバランス
- AIの出力が長大になりすぎないよう配慮
- 重要度の高い情報を優先的に構造化
- 準備書面作成時の典型的なニーズに焦点

---

## 🚀 次のステップ

1. ✅ **改善計画の策定**（本ドキュメント）
2. 🔄 **プロンプトの改善版作成**
3. 🔄 **スキーマの更新**
4. 🔄 **サンプル証拠での試行**
5. 🔄 **実用性の検証とフィードバック**
6. 🔄 **本番環境への適用**

---

**作成日**: 2025-11-05
**バージョン**: 1.0
**ステータス**: 改善計画策定完了 → プロンプト改善着手

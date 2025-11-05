# Phase 1 実用版（v3.1）使用ガイド

## 📋 目次

1. [改善の概要](#改善の概要)
2. [新機能と改善点](#新機能と改善点)
3. [準備書面作成での活用方法](#準備書面作成での活用方法)
4. [具体例：契約解除通知書の分析](#具体例契約解除通知書の分析)
5. [AI（ChatGPT/Claude）での使用方法](#aichatgptclaudeでの使用方法)
6. [移行ガイド](#移行ガイド)

---

## 改善の概要

### v3.1の目的
**Phase 1のAI分析出力を、準備書面作成時に直接引用・活用できる実用的な形式に改善**

### 基本原則（変更なし）
- ✅ 完全な客観性と中立性を維持
- ✅ 法的評価や主観的解釈は一切含めない
- ✅ Phase 1 = 客観的事実記録、Phase 2 = 法的分析（将来）

### 実用性の向上
- 📝 **完全な文で記述**: 箇条書きではなく、準備書面に引用できる完全な文
- 🔗 **出典の明記**: 各情報の出典位置を具体的に記載
- 🏗️ **構造化の徹底**: プログラムでの処理を容易にする詳細な構造化
- 💬 **文脈の提供**: 各情報の意味・関連性を客観的に説明
- 📌 **引用文の完全抽出**: 重要な文言を一字一句そのまま抽出

---

## 新機能と改善点

### 1. observable_facts の構造化

#### ❌ 旧版（v3.0）
```json
"observable_facts": [
  "契約解除の通知",
  "2021年8月15日付",
  "甲野太郎から乙山花子へ"
]
```

**問題点**:
- 箇条書きで文脈が不明
- 準備書面に引用する際、追加の文章化が必要
- 出典情報がない

#### ✅ 新版（v3.1）
```json
"observable_facts": {
  "structured_facts": [
    {
      "fact_id": "fact_001",
      "category": "document_basic_info",
      "fact_statement": "本証拠は、2021年8月15日付で甲野太郎氏から乙山花子氏宛に送付された契約解除通知書である。",
      "source_location": "文書上部のタイトル欄および日付欄",
      "confidence": "high",
      "related_facts": ["fact_002", "fact_003"],
      "tags": ["contract", "date", "party", "notice"]
    },
    {
      "fact_id": "fact_002",
      "category": "content_substance",
      "fact_statement": "通知書には、令和3年7月1日付で締結された売買契約（契約番号：ABC-2021-0701）を、同年8月31日をもって解除する旨が記載されている。",
      "source_location": "本文第1段落",
      "confidence": "high",
      "related_facts": ["fact_001", "fact_004"],
      "tags": ["contract", "termination", "date"]
    }
  ],
  "fact_summary": "本証拠は契約解除通知書であり、2021年8月15日付で甲野太郎氏から乙山花子氏に送付され、同年7月1日締結の売買契約を同年8月31日に解除する旨が記載されている。",
  "fact_count": 8
}
```

**改善点**:
- ✅ 各事実が完全な文として記述
- ✅ 出典位置を明記
- ✅ カテゴリとタグで分類
- ✅ 事実間の関連性を記録
- ✅ 準備書面にそのまま引用可能

---

### 2. temporal_information の時系列構造化

#### ❌ 旧版（v3.0）
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

**問題点**:
- `timeline`が文字列なのでプログラム処理が困難
- 各日付の詳細情報が不足
- 準備書面の「事実経緯」セクション作成に追加作業が必要

#### ✅ 新版（v3.1）
```json
"temporal_information": {
  "document_date": "2021-08-15",
  "document_date_source": "文書上部に「令和3年8月15日」と明記",
  "date_confidence": "high",
  "date_confidence_reason": "文書上部に明示的な日付記載あり",
  
  "all_dates_structured": [
    {
      "date_id": "date_001",
      "date": "2021-07-01",
      "date_type": "contract_signing",
      "description": "甲野太郎氏と乙山花子氏との間で売買契約が締結された日である。",
      "participants": ["party_001", "party_002"],
      "source_location": "本文第1段落「令和3年7月1日付で締結された」",
      "confidence": "high"
    },
    {
      "date_id": "date_002",
      "date": "2021-07-31",
      "date_type": "payment_deadline",
      "description": "売買代金の支払期限であった日である。",
      "participants": ["party_002"],
      "source_location": "本文第2段落「支払期限である同年7月31日」",
      "confidence": "high"
    },
    {
      "date_id": "date_003",
      "date": "2021-08-15",
      "date_type": "document_creation",
      "description": "本通知書の作成・発送日である。",
      "participants": ["party_001"],
      "source_location": "文書上部の日付欄",
      "confidence": "high"
    },
    {
      "date_id": "date_004",
      "date": "2021-08-31",
      "date_type": "contract_termination",
      "description": "契約解除の効力が発生する予定日である。",
      "participants": ["party_001", "party_002"],
      "source_location": "本文第1段落「同年8月31日をもって解除する」",
      "confidence": "high"
    }
  ],
  
  "chronological_summary": "2021年7月1日に売買契約が締結され、同年7月31日が支払期限であったところ、8月15日に契約解除通知が発送され、8月31日に契約解除の効力が発生する予定である。",
  
  "timeline_visualization": [
    {"date": "2021-07-01", "event": "契約締結", "event_type": "contract_signing", "participants": ["party_001", "party_002"]},
    {"date": "2021-07-31", "event": "支払期限", "event_type": "deadline", "participants": ["party_002"]},
    {"date": "2021-08-15", "event": "解除通知発送（本証拠）", "event_type": "notice", "participants": ["party_001"]},
    {"date": "2021-08-31", "event": "解除予定", "event_type": "termination", "participants": ["party_001", "party_002"]}
  ]
}
```

**改善点**:
- ✅ 全ての日付を時系列配列化
- ✅ 各日付に詳細な説明文を付与
- ✅ タイムライン可視化データを提供
- ✅ プログラムでの自動処理が可能
- ✅ 準備書面の「事実経緯」セクションに直接使用可能

---

### 3. parties_mentioned の詳細化

#### ❌ 旧版（v3.0）
```json
"parties_mentioned": {
  "individuals": ["甲野太郎", "乙山花子"],
  "organizations": ["ABC株式会社"],
  "roles_described": "文書内で各当事者の記述"
}
```

**問題点**:
- 名前の羅列だけで役割が不明
- 連絡先、住所、肩書きなどの情報が散逸
- 当事者間の関係性が不明確

#### ✅ 新版（v3.1）
```json
"parties_mentioned": {
  "detailed_parties": [
    {
      "party_id": "party_001",
      "name": "甲野太郎",
      "type": "individual",
      "role_in_document": "通知書の発信者（売主）",
      "attributes": {
        "address": "東京都千代田区丸の内1-2-3",
        "title": "契約当事者（売主）",
        "contact": "記載なし"
      },
      "actions_described": [
        "契約解除通知の発送を行った",
        "違約金50,000円の支払を請求した"
      ],
      "statements_made": [
        "「本契約は、令和3年8月31日をもって解除します。」",
        "「違約金として50,000円をお支払いください。」"
      ],
      "first_appearance": "文書上部の差出人欄"
    },
    {
      "party_id": "party_002",
      "name": "乙山花子",
      "type": "individual",
      "role_in_document": "通知書の受信者（買主）",
      "attributes": {
        "address": "大阪府大阪市北区梅田1-2-3",
        "title": "契約当事者（買主）",
        "contact": "記載なし"
      },
      "actions_described": [
        "売買代金の支払を遅延した"
      ],
      "statements_made": [],
      "first_appearance": "文書上部の宛先欄"
    }
  ],
  "relationships": [
    {
      "relationship_id": "rel_001",
      "from_party": "party_001",
      "to_party": "party_002",
      "relationship_type": "売買契約における売主と買主",
      "relationship_description": "甲野太郎氏（売主）と乙山花子氏（買主）は、令和3年7月1日付で売買契約を締結した当事者である。",
      "basis": "本文第1段落の記載「令和3年7月1日付で締結された売買契約」"
    }
  ],
  "party_summary": "甲野太郎氏（売主・発信者）から乙山花子氏（買主・受信者）への契約解除通知である。"
}
```

**改善点**:
- ✅ 各当事者の詳細情報を構造化
- ✅ 役割、住所、肩書きを明記
- ✅ 文書内での行為を完全な文で記述
- ✅ 当事者間の関係性を明確化
- ✅ 準備書面の「当事者」セクションに直接使用可能

---

### 4. financial_information の文脈化

#### ❌ 旧版（v3.0）
```json
"financial_information": {
  "amounts": ["500,000円", "50,000円"],
  "currency": "JPY",
  "amount_context": "各金額の文脈"
}
```

**問題点**:
- 金額の羅列だけで意味が不明
- 支払済みか未払いかが不明
- 準備書面で主張する際の文脈が不足

#### ✅ 新版（v3.1）
```json
"financial_information": {
  "detailed_amounts": [
    {
      "amount_id": "amt_001",
      "amount_value": 500000,
      "amount_display": "500,000円",
      "currency": "JPY",
      "amount_type": "contract_price",
      "description": "売買契約における売買代金の総額である。",
      "payment_status": "partially_paid",
      "payment_details": "300,000円は既に支払われているが、残額200,000円は未払いである。",
      "due_date": "2021-07-31",
      "source_location": "本文第2段落、契約書第5条の記載",
      "related_parties": ["party_001", "party_002"],
      "confidence": "high"
    },
    {
      "amount_id": "amt_002",
      "amount_value": 50000,
      "amount_display": "50,000円",
      "currency": "JPY",
      "amount_type": "penalty",
      "description": "契約違反による違約金である。",
      "payment_status": "unpaid_claimed",
      "payment_details": "甲野太郎氏が乙山花子氏に対して請求している金額である。",
      "due_date": "2021-08-31",
      "source_location": "本文第3段落",
      "related_parties": ["party_001", "party_002"],
      "confidence": "high"
    }
  ],
  "financial_calculations": {
    "total_claimed": 250000,
    "total_paid": 300000,
    "total_unpaid": 250000,
    "breakdown": "売買代金未払分200,000円 + 違約金50,000円 = 250,000円"
  },
  "financial_summary": "売買代金500,000円のうち300,000円は既に支払われているが、残額200,000円および違約金50,000円（合計250,000円）が未払いである。"
}
```

**改善点**:
- ✅ 各金額の詳細情報を構造化
- ✅ 支払状況を明確化
- ✅ 金額の集計データを提供
- ✅ 準備書面の「請求金額」セクションに直接使用可能

---

### 5. 新セクション：quotable_statements

**目的**: 準備書面で引用すべき重要文言を一字一句そのまま抽出

```json
"quotable_statements": [
  {
    "quote_id": "quote_001",
    "statement": "「本契約は、令和3年8月31日をもって解除します。」",
    "location": "本文第1段落第3文",
    "context": "契約解除の意思表示",
    "verbatim": true,
    "language": "japanese",
    "emphasis": "none",
    "speaker": "party_001"
  },
  {
    "quote_id": "quote_002",
    "statement": "「支払期限である令和3年7月31日を経過しても、残金200,000円のお支払がございません。」",
    "location": "本文第2段落第2文",
    "context": "支払遅延の指摘",
    "verbatim": true,
    "language": "japanese",
    "emphasis": "none",
    "speaker": "party_001"
  }
]
```

**活用方法**:
- 準備書面の「証拠の内容」セクションで直接引用
- 主張の根拠として文言を正確に引用
- 相手方の主張との矛盾を指摘する際に使用

---

### 6. 新セクション：cross_reference_potential

**目的**: 他の証拠との照合ポイントを客観的に示唆

```json
"cross_reference_potential": [
  {
    "reference_id": "ref_001",
    "this_evidence_element": "契約番号：ABC-2021-0701",
    "potential_related_evidence": "元となる売買契約書",
    "matching_criteria": "契約番号の一致",
    "objective_note": "本証拠に記載されている契約番号「ABC-2021-0701」を持つ他の証拠（売買契約書）が存在する場合、相互参照が可能である。"
  },
  {
    "reference_id": "ref_002",
    "this_evidence_element": "支払済金額：300,000円",
    "potential_related_evidence": "振込明細書、領収書",
    "matching_criteria": "金額および支払日付の一致",
    "objective_note": "本証拠に記載されている「既払い金額300,000円」を裏付ける振込明細書や領収書が存在する場合、支払事実の証明に使用できる。"
  }
]
```

**活用方法**:
- Phase 2での証拠間の関連性分析に使用
- 準備書面作成時の証拠の組み合わせを検討
- 証拠の相互補完関係を把握

---

## 準備書面作成での活用方法

### 1. 証拠説明書の「作成年月日」欄

**database.json から抽出**:
```json
"temporal_information": {
  "document_date": "2021-08-15",
  "document_date_source": "文書上部に「令和3年8月15日」と明記"
}
```

**証拠説明書に記入**:
```
作成年月日: 令和3年8月15日
```

---

### 2. 証拠説明書の「内容」欄

**database.json から抽出**:
```json
"observable_facts": {
  "fact_summary": "本証拠は契約解除通知書であり、2021年8月15日付で甲野太郎氏から乙山花子氏に送付され、同年7月1日締結の売買契約を同年8月31日に解除する旨が記載されている。"
}
```

**証拠説明書に記入**:
```
内容: 本証拠は、甲野太郎から乙山花子に対する契約解除通知書である。
      令和3年7月1日締結の売買契約（契約番号：ABC-2021-0701）を、
      同年8月31日をもって解除する旨が記載されている。
```

---

### 3. 準備書面の「事実経緯」セクション

**database.json から抽出**:
```json
"temporal_information": {
  "chronological_summary": "2021年7月1日に売買契約が締結され、同年7月31日が支払期限であったところ、8月15日に契約解除通知が発送され、8月31日に契約解除の効力が発生する予定である。",
  "timeline_visualization": [...]
}
```

**準備書面に記載**:
```
第2 事実経緯

1. 令和3年7月1日、原告と被告は、○○の売買契約を締結した（甲1号証）。

2. 同年7月31日が売買代金の支払期限であった（甲1号証）。

3. 同年8月15日、原告は被告に対し、契約解除通知を発送した（甲2号証）。

4. 契約解除の効力は、同年8月31日に発生する予定であった（甲2号証）。
```

---

### 4. 準備書面の「証拠の内容」セクション

**database.json から抽出**:
```json
"quotable_statements": [
  {
    "quote_id": "quote_001",
    "statement": "「本契約は、令和3年8月31日をもって解除します。」",
    "location": "本文第1段落第3文",
    "context": "契約解除の意思表示"
  }
]
```

**準備書面に記載**:
```
第3 証拠の内容

1. 甲2号証の内容

   (1) 甲2号証は、原告から被告に対する契約解除通知書である。
   
   (2) 同通知書には、「本契約は、令和3年8月31日をもって解除します。」
       と明記されており、原告の契約解除の意思表示が明確である。
   
   (3) また、「支払期限である令和3年7月31日を経過しても、残金200,000円の
       お支払がございません。」と記載されており、被告の支払遅延が
       契約解除の原因であることが示されている。
```

---

### 5. 準備書面の「主張」セクション

**database.json から抽出**:
```json
"financial_information": {
  "financial_summary": "売買代金500,000円のうち300,000円は既に支払われているが、残額200,000円および違約金50,000円（合計250,000円）が未払いである。"
}
```

**準備書面に記載**:
```
第4 請求の根拠

1. 売買代金残額 200,000円

   売買契約に基づく売買代金は500,000円であり、このうち300,000円は
   既に支払われているが、残額200,000円は支払期限（令和3年7月31日）を
   経過しても支払われていない（甲2号証）。

2. 違約金 50,000円

   被告の支払遅延により、原告は契約を解除せざるを得なかった。
   契約書第10条に基づく違約金50,000円を請求する（甲2号証）。

3. 請求金額合計

   上記1および2の合計 250,000円を請求する。
```

---

## 具体例：契約解除通知書の分析

### サンプル証拠（甲2号証）

```
                         契約解除通知書

                                        令和3年8月15日

乙山花子 様

                              東京都千代田区丸の内1-2-3
                              甲野太郎

拝啓 時下ますますご清祥のこととお慶び申し上げます。

さて、令和3年7月1日付で締結されました売買契約（契約番号：ABC-2021-0701）
につきまして、下記の理由により、本契約を令和3年8月31日をもって解除
いたします。

                           記

1. 支払期限である令和3年7月31日を経過しても、残金200,000円のお支払が
   ございません。

2. 契約書第8条第2項に基づき、上記支払遅延を理由として、本契約を解除
   いたします。

3. 契約書第10条に基づき、違約金として50,000円を令和3年8月31日までに
   お支払いください。

                                                          以上

                                        甲野太郎 ㊞
```

### v3.1での分析結果（抜粋）

```json
{
  "evidence_id": "ko002",
  "verbalization_level": 4,
  "confidence_score": 0.95,
  
  "objective_analysis": {
    "document_type": "契約解除通知書",
    
    "observable_facts": {
      "structured_facts": [
        {
          "fact_id": "fact_001",
          "category": "document_basic_info",
          "fact_statement": "本証拠は、2021年8月15日付で甲野太郎氏から乙山花子氏宛に送付された契約解除通知書である。",
          "source_location": "文書上部のタイトル欄および日付欄",
          "confidence": "high",
          "related_facts": ["fact_002", "fact_003"],
          "tags": ["contract", "date", "party", "notice"]
        },
        {
          "fact_id": "fact_002",
          "category": "content_substance",
          "fact_statement": "通知書には、令和3年7月1日付で締結された売買契約（契約番号：ABC-2021-0701）を、同年8月31日をもって解除する旨が記載されている。",
          "source_location": "本文第1段落",
          "confidence": "high",
          "related_facts": ["fact_001", "fact_004"],
          "tags": ["contract", "termination", "date"]
        },
        {
          "fact_id": "fact_003",
          "category": "content_substance",
          "fact_statement": "支払期限である令和3年7月31日を経過しても、残金200,000円の支払がないことが契約解除の理由として記載されている。",
          "source_location": "記書き第1項",
          "confidence": "high",
          "related_facts": ["fact_002", "fact_005"],
          "tags": ["payment", "deadline", "breach", "amount"]
        },
        {
          "fact_id": "fact_004",
          "category": "content_substance",
          "fact_statement": "契約書第8条第2項に基づき、支払遅延を理由として契約を解除する旨が記載されている。",
          "source_location": "記書き第2項",
          "confidence": "high",
          "related_facts": ["fact_002", "fact_003"],
          "tags": ["contract", "termination", "legal_basis"]
        },
        {
          "fact_id": "fact_005",
          "category": "content_substance",
          "fact_statement": "契約書第10条に基づき、違約金として50,000円を令和3年8月31日までに支払うよう請求されている。",
          "source_location": "記書き第3項",
          "confidence": "high",
          "related_facts": ["fact_003", "fact_004"],
          "tags": ["penalty", "amount", "deadline", "claim"]
        }
      ],
      "fact_summary": "本証拠は、甲野太郎氏から乙山花子氏に対する契約解除通知書であり、2021年8月15日付で発送され、同年7月1日締結の売買契約を支払遅延を理由として同年8月31日に解除し、違約金50,000円を請求する内容である。",
      "fact_count": 5
    },
    
    "temporal_information": {
      "document_date": "2021-08-15",
      "document_date_source": "文書上部に「令和3年8月15日」と明記",
      "date_confidence": "high",
      "date_confidence_reason": "文書上部に明示的な日付記載あり",
      
      "all_dates_structured": [
        {
          "date_id": "date_001",
          "date": "2021-07-01",
          "date_type": "contract_signing",
          "description": "甲野太郎氏と乙山花子氏との間で売買契約が締結された日である。",
          "participants": ["party_001", "party_002"],
          "source_location": "本文第1段落「令和3年7月1日付で締結されました売買契約」",
          "confidence": "high"
        },
        {
          "date_id": "date_002",
          "date": "2021-07-31",
          "date_type": "payment_deadline",
          "description": "売買代金の支払期限であった日である。",
          "participants": ["party_002"],
          "source_location": "記書き第1項「支払期限である令和3年7月31日」",
          "confidence": "high"
        },
        {
          "date_id": "date_003",
          "date": "2021-08-15",
          "date_type": "document_creation",
          "description": "本契約解除通知書の作成・発送日である。",
          "participants": ["party_001"],
          "source_location": "文書上部の日付欄",
          "confidence": "high"
        },
        {
          "date_id": "date_004",
          "date": "2021-08-31",
          "date_type": "contract_termination",
          "description": "契約解除の効力が発生する予定日である。",
          "participants": ["party_001", "party_002"],
          "source_location": "本文第1段落「令和3年8月31日をもって解除いたします」",
          "confidence": "high"
        },
        {
          "date_id": "date_005",
          "date": "2021-08-31",
          "date_type": "payment_deadline",
          "description": "違約金50,000円の支払期限である。",
          "participants": ["party_002"],
          "source_location": "記書き第3項「令和3年8月31日までにお支払いください」",
          "confidence": "high"
        }
      ],
      
      "chronological_summary": "2021年7月1日に売買契約が締結され、同年7月31日が支払期限であったところ、8月15日に契約解除通知が発送され、8月31日に契約解除の効力が発生するとともに違約金の支払期限となっている。",
      
      "timeline_visualization": [
        {"date": "2021-07-01", "event": "契約締結", "event_type": "contract_signing", "participants": ["party_001", "party_002"]},
        {"date": "2021-07-31", "event": "支払期限", "event_type": "deadline", "participants": ["party_002"]},
        {"date": "2021-08-15", "event": "解除通知発送（本証拠）", "event_type": "notice", "participants": ["party_001"]},
        {"date": "2021-08-31", "event": "解除予定・違約金支払期限", "event_type": "termination", "participants": ["party_001", "party_002"]}
      ]
    },
    
    "parties_mentioned": {
      "detailed_parties": [
        {
          "party_id": "party_001",
          "name": "甲野太郎",
          "type": "individual",
          "role_in_document": "通知書の発信者（売主）",
          "attributes": {
            "address": "東京都千代田区丸の内1-2-3",
            "title": "契約当事者（売主）",
            "contact": "記載なし"
          },
          "actions_described": [
            "契約解除通知の発送を行った",
            "違約金50,000円の支払を請求した"
          ],
          "statements_made": [
            "「本契約を令和3年8月31日をもって解除いたします。」",
            "「違約金として50,000円を令和3年8月31日までにお支払いください。」"
          ],
          "first_appearance": "文書上部の差出人欄"
        },
        {
          "party_id": "party_002",
          "name": "乙山花子",
          "type": "individual",
          "role_in_document": "通知書の受信者（買主）",
          "attributes": {
            "address": "記載なし（宛先欄には住所なし）",
            "title": "契約当事者（買主）",
            "contact": "記載なし"
          },
          "actions_described": [
            "売買代金の支払を遅延した（残金200,000円未払い）"
          ],
          "statements_made": [],
          "first_appearance": "文書上部の宛先欄"
        }
      ],
      "relationships": [
        {
          "relationship_id": "rel_001",
          "from_party": "party_001",
          "to_party": "party_002",
          "relationship_type": "売買契約における売主と買主",
          "relationship_description": "甲野太郎氏（売主）と乙山花子氏（買主）は、令和3年7月1日付で売買契約を締結した当事者である。",
          "basis": "本文第1段落の記載「令和3年7月1日付で締結されました売買契約」"
        }
      ],
      "party_summary": "甲野太郎氏（売主・発信者）から乙山花子氏（買主・受信者）への契約解除通知である。"
    },
    
    "financial_information": {
      "detailed_amounts": [
        {
          "amount_id": "amt_001",
          "amount_value": 200000,
          "amount_display": "200,000円",
          "currency": "JPY",
          "amount_type": "contract_price_unpaid",
          "description": "売買契約における売買代金の未払残額である。",
          "payment_status": "unpaid",
          "payment_details": "支払期限（令和3年7月31日）を経過しても支払われていない。",
          "due_date": "2021-07-31",
          "source_location": "記書き第1項「残金200,000円のお支払がございません」",
          "related_parties": ["party_001", "party_002"],
          "confidence": "high"
        },
        {
          "amount_id": "amt_002",
          "amount_value": 50000,
          "amount_display": "50,000円",
          "currency": "JPY",
          "amount_type": "penalty",
          "description": "契約書第10条に基づく違約金である。",
          "payment_status": "unpaid_claimed",
          "payment_details": "甲野太郎氏が乙山花子氏に対して請求している金額である。",
          "due_date": "2021-08-31",
          "source_location": "記書き第3項「違約金として50,000円を令和3年8月31日までにお支払いください」",
          "related_parties": ["party_001", "party_002"],
          "confidence": "high"
        }
      ],
      "financial_calculations": {
        "total_claimed": 250000,
        "total_paid": 0,
        "total_unpaid": 250000,
        "breakdown": "売買代金未払分200,000円 + 違約金50,000円 = 250,000円"
      },
      "financial_summary": "売買代金の未払残額200,000円および違約金50,000円（合計250,000円）が請求されている。"
    },
    
    "quotable_statements": [
      {
        "quote_id": "quote_001",
        "statement": "「令和3年7月1日付で締結されました売買契約（契約番号：ABC-2021-0701）につきまして、下記の理由により、本契約を令和3年8月31日をもって解除いたします。」",
        "location": "本文第1段落",
        "context": "契約解除の意思表示",
        "verbatim": true,
        "language": "japanese",
        "emphasis": "none",
        "speaker": "party_001"
      },
      {
        "quote_id": "quote_002",
        "statement": "「支払期限である令和3年7月31日を経過しても、残金200,000円のお支払がございません。」",
        "location": "記書き第1項",
        "context": "支払遅延の指摘",
        "verbatim": true,
        "language": "japanese",
        "emphasis": "none",
        "speaker": "party_001"
      },
      {
        "quote_id": "quote_003",
        "statement": "「契約書第8条第2項に基づき、上記支払遅延を理由として、本契約を解除いたします。」",
        "location": "記書き第2項",
        "context": "解除の法的根拠",
        "verbatim": true,
        "language": "japanese",
        "emphasis": "none",
        "speaker": "party_001"
      },
      {
        "quote_id": "quote_004",
        "statement": "「契約書第10条に基づき、違約金として50,000円を令和3年8月31日までにお支払いください。」",
        "location": "記書き第3項",
        "context": "違約金の請求",
        "verbatim": true,
        "language": "japanese",
        "emphasis": "none",
        "speaker": "party_001"
      }
    ],
    
    "cross_reference_potential": [
      {
        "reference_id": "ref_001",
        "this_evidence_element": "契約番号：ABC-2021-0701",
        "potential_related_evidence": "元となる売買契約書",
        "matching_criteria": "契約番号の一致",
        "objective_note": "本証拠に記載されている契約番号「ABC-2021-0701」を持つ他の証拠（売買契約書）が存在する場合、契約内容の詳細を確認できる。"
      },
      {
        "reference_id": "ref_002",
        "this_evidence_element": "契約書第8条第2項（解除条項）",
        "potential_related_evidence": "売買契約書の第8条",
        "matching_criteria": "条項番号の一致",
        "objective_note": "本証拠で言及されている「契約書第8条第2項」の実際の条文を、売買契約書で確認できる。"
      },
      {
        "reference_id": "ref_003",
        "this_evidence_element": "契約書第10条（違約金条項）",
        "potential_related_evidence": "売買契約書の第10条",
        "matching_criteria": "条項番号の一致",
        "objective_note": "本証拠で言及されている「契約書第10条」の違約金額の根拠を、売買契約書で確認できる。"
      },
      {
        "reference_id": "ref_004",
        "this_evidence_element": "支払済金額（残金200,000円という記載から推測される）",
        "potential_related_evidence": "振込明細書、領収書",
        "matching_criteria": "支払金額および支払日付の一致",
        "objective_note": "本証拠に「残金200,000円」という記載があることから、売買代金の一部は既に支払われたと推測される。その支払を証明する振込明細書や領収書が存在する可能性がある。"
      }
    ]
  }
}
```

---

## AI（ChatGPT/Claude）での使用方法

### Phase 2での活用（将来）

**プロンプト例**:
```
あなたは訴訟代理人です。以下のdatabase.json（Phase 1の客観的分析結果）を読み、
原告の立場から法的分析を行い、準備書面の草案を作成してください。

【database.json】
{
  // Phase 1の分析結果を貼り付け
}

【指示】
1. 証拠間の関連性を分析してください
2. 時系列を整理し、事実経緯を構築してください
3. 原告の主張に有利な証拠を特定してください
4. 準備書面の「第2 事実経緯」「第3 証拠の内容」「第4 主張」セクションの草案を作成してください
```

### 準備書面の自動生成

**プロンプト例**:
```
以下のdatabase.jsonから、証拠説明書の「内容」欄に記載すべき文章を生成してください。

【database.json】
{
  "evidence_id": "ko002",
  "objective_analysis": {
    "observable_facts": {
      "fact_summary": "..."
    },
    "temporal_information": {
      "document_date": "2021-08-15",
      ...
    }
  }
}

【出力形式】
簡潔で正確な証拠説明（2-3文程度）
```

---

## 移行ガイド

### v3.0 → v3.1への移行

#### 1. プロンプトファイルの更新

**旧版**:
```
prompts/Phase1_EvidenceAnalysis.txt
```

**新版**:
```
prompts/Phase1_EvidenceAnalysis_v2_Practical.txt
```

#### 2. スキーマファイルの更新

**旧版**:
```
database_schema_v3.json
```

**新版**:
```
database_schema_v3.1_practical.json
```

#### 3. 既存データの互換性

v3.1は v3.0の上位互換です。既存のdatabase.jsonも引き続き使用できます。

**v3.0の出力**:
```json
"observable_facts": ["事実1", "事実2"]
```

**v3.1での読み取り**:
- AIがv3.0形式を検出した場合、自動的にv3.1形式に変換して出力
- 既存データの再分析は不要（ただし、推奨）

#### 4. 新規証拠の分析

**ai_analyzer_complete.py** の更新:
```python
# プロンプトファイルのパスを新版に変更
LOCAL_PROMPT_PATH = "prompts/Phase1_EvidenceAnalysis_v2_Practical.txt"
```

#### 5. 段階的移行

1. **ステップ1**: 新版プロンプトとスキーマを配置
2. **ステップ2**: 新規証拠の分析で新版を試行
3. **ステップ3**: 出力品質を確認
4. **ステップ4**: 既存証拠の再分析（任意）
5. **ステップ5**: 旧版ファイルのアーカイブ

---

## まとめ

### v3.1の主な改善

1. ✅ **observable_facts**: 完全な文での記述、出典明記、構造化
2. ✅ **temporal_information**: 時系列の完全構造化、タイムライン可視化
3. ✅ **parties_mentioned**: 当事者情報の詳細化、関係性の明確化
4. ✅ **financial_information**: 金額情報の文脈化、支払状況の明記
5. ✅ **quotable_statements**: 重要文言の完全抽出（新規）
6. ✅ **cross_reference_potential**: 証拠間照合の示唆（新規）

### 期待される効果

- 📝 準備書面作成時の作業効率が大幅に向上
- 🤖 Phase 2でのAI活用が容易に
- 🔗 証拠間の関連性分析が自動化可能
- 📊 タイムライン自動生成が可能
- ✍️ 証拠説明書・準備書面への直接引用が可能

### 客観性の維持

- ✅ 全ての改善は「観察可能な事実の構造化」に限定
- ✅ 法的評価や主観的解釈は一切含まない
- ✅ Phase 1の基本原則（中立性）は完全に維持

---

**作成日**: 2025-11-05  
**バージョン**: v3.1 実用版  
**ステータス**: 完成・実装準備完了

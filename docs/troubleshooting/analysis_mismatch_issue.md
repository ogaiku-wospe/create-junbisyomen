# 証拠分析結果の不一致問題 - トラブルシューティング

## 📋 問題の概要

ユーザーから報告された問題：
```
「tmp_ko_004の内容が全然違うように思えます」
```

実際のPDF内容：
```
=配達証明=

差出人: 〒997-0028 山形県鶴岡市山王町９ー２９
        弁護士法人ｍａｍｏｒｉ 弁護士 日比野 大

受取人: 〒063-0804 北海道札幌市西区二十四軒四条４－２－１２
        ブランシャール琴似ＳＴＡＴＩＯＮ ３０２号
        石村 まゆか 様
```

---

## 🔍 診断結果

### データベースの状態確認

```json
{
  "metadata": {
    "total_evidence_count": 13,
    "completed_count": 13  // ← 13件完了と表示されている
  }
}
```

しかし、実際の証拠データを確認すると：

```
全証拠の分析状況:
1. tmp_ko_001  ❌ 未分析
2. tmp_ko_002  ❌ 未分析
3. tmp_ko_003  ❌ 未分析
4. tmp_ko_004  ❌ 未分析  ← 問題の証拠
...
13. tmp_ko_013 ❌ 未分析

分析済み: 0件 / 未分析: 13件
```

### 🎯 結論

**AI分析がまだ実行されていません。**

`completed_count: 13`は「証拠整理が13件完了した」という意味で、「AI分析が13件完了した」という意味ではありません。

---

## 🔎 混同の原因

### Phase 1 システムには2つの段階があります

#### ステップ1: 証拠整理（Evidence Organization）
- ✅ ファイルのリネーム
- ✅ フォルダ間の移動
- ✅ メタデータ抽出（ファイルサイズ、ハッシュ値など）
- ✅ database.jsonへの登録

**状態**: `completed_count`がカウントアップ

#### ステップ2: AI分析（AI Analysis）
- ❌ ファイル内容の抽出
- ❌ GPT-4o Vision / Claude による分析
- ❌ 客観的事実の抽出
- ❌ 法的重要性の評価

**状態**: `analyzed_content`と`ai_analysis`がdatabase.jsonに追加

---

## 📊 database.jsonの構造比較

### 証拠整理後（現在の状態）

```json
{
  "evidence_id": "tmp_ko_004",
  "evidence_number": "甲tmp_ko_004",
  "original_filename": "tmp_ko_004_10.pdf",
  "complete_metadata": {
    "basic": { ... },
    "hashes": { ... }
  }
  // ← analyzed_content と ai_analysis が存在しない
}
```

### AI分析後（期待される状態）

```json
{
  "evidence_id": "tmp_ko_004",
  "evidence_number": "甲tmp_ko_004",
  "original_filename": "tmp_ko_004_10.pdf",
  "complete_metadata": { ... },
  
  // ✅ 以下が追加される
  "analyzed_content": {
    "content_summary": "配達証明書。弁護士法人ｍａｍｏｒｉの弁護士日比野大から石村まゆかへ送付された郵便物の配達記録。",
    "content_type": "legal_document",
    "text_content": "=配達証明=\n差出人: 〒997-0028...",
    "document_structure": {
      "total_pages": 3,
      "has_text": true,
      "has_images": false
    }
  },
  
  "ai_analysis": {
    "document_type": "配達証明",
    "analysis_summary": "この証拠は、弁護士法人ｍａｍｏｒｉから被告に対して送付された郵便物の配達証明書である。",
    "observable_facts": {
      "structured_facts": [
        {
          "fact_id": "fact_001",
          "category": "document_basic_info",
          "fact_statement": "これは配達証明書である。",
          "source_location": "文書上部のタイトル"
        },
        {
          "fact_id": "fact_002",
          "category": "party_information",
          "fact_statement": "差出人は弁護士法人ｍａｍｏｒｉの弁護士日比野大である。",
          "source_location": "差出人欄"
        },
        {
          "fact_id": "fact_003",
          "category": "party_information",
          "fact_statement": "受取人は北海道札幌市西区二十四軒四条４－２－１２ ブランシャール琴似ＳＴＡＴＩＯＮ ３０２号の石村まゆかである。",
          "source_location": "受取人欄"
        }
      ]
    },
    "parties_mentioned": {
      "detailed_parties": [
        {
          "party_name": "弁護士法人ｍａｍｏｒｉ",
          "role": "差出人",
          "representation": "弁護士 日比野 大"
        },
        {
          "party_name": "石村まゆか",
          "role": "受取人",
          "address": "〒063-0804 北海道札幌市西区二十四軒四条４－２－１２"
        }
      ]
    },
    "verbalization_level": 4,
    "confidence_score": 95.0
  }
}
```

---

## ✅ 解決方法

### ステップ1: システムを起動

```bash
python3 run_phase1_multi.py
```

### ステップ2: AI分析を実行

メニューから以下を選択：

```
2. 証拠分析
↓
1. 甲号証
↓
001-013  ← 全件分析する場合
または
004     ← tmp_ko_004だけ分析する場合
```

### ステップ3: 分析完了を待つ

- 1件あたり30秒〜2分程度
- 13件全体で約5〜20分

### ステップ4: 結果を確認

```
5. 証拠分析一覧を表示
```

---

## 🎯 AI分析実行後の期待される結果

### tmp_ko_004の分析結果

**文書タイプ**: 配達証明

**客観的事実**:
1. これは配達証明書である
2. 差出人は弁護士法人ｍａｍｏｒｉの弁護士日比野大である
3. 差出人の住所は〒997-0028 山形県鶴岡市山王町９ー２９である
4. 受取人は石村まゆかである
5. 受取人の住所は〒063-0804 北海道札幌市西区二十四軒四条４－２－１２ ブランシャール琴似ＳＴＡＴＩＯＮ ３０２号である

**関係者**:
- 差出人: 弁護士法人ｍａｍｏｒｉ（代理人: 弁護士 日比野 大）
- 受取人: 石村まゆか

**言語化レベル**: 4（完全言語化）

**信頼度スコア**: 95.0

---

## 🔧 トラブルシューティング

### Q1: AI分析を実行したのに結果が反映されない

**確認事項**:
1. 分析処理が正常に完了したか確認
2. エラーメッセージが表示されていないか確認
3. database.jsonが最新版か確認（Google Driveから再ダウンロード）

### Q2: 分析結果が期待と異なる

**原因の可能性**:
1. PDFの画質が低い（OCRエラー）
2. Vision APIがポリシー違反と誤判定
3. 複数ページのPDFで一部ページのみ分析

**対処方法**:
1. Claude Visionフォールバックを有効化（`.env`で設定）
2. 画像の解像度を上げる
3. 再分析を実行

### Q3: completed_countの意味

`completed_count`は以下のいずれかを指します：
- 証拠整理が完了した件数
- または AI分析が完了した件数

正確な状態は、各証拠の`analyzed_content`と`ai_analysis`フィールドの有無で判断してください。

---

## 📚 関連ドキュメント

- [診断スクリプトの使い方](../user-guides/diagnostic_tools.md)
- [AI分析の仕組み](../architecture/ai_analysis_workflow.md)
- [database.jsonの構造](../architecture/database_schema_v3.1_practical.json)

---

## 🆘 サポート

上記の手順で解決しない場合は、以下の情報を収集してください：

```bash
# 診断スクリプトを実行
python3 scripts/analysis/diagnose_analysis_issues.py /path/to/database.json

# エラーログを確認
tail -50 phase1_multi.log
```

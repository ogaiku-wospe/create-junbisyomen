# AI分析エンジン リファクタリング計画

## 🎯 目的

1. **OpenAI API完全削除** - ChatGPT APIは不要
2. **Claude Vision API専用化** - より確実な分析
3. **段階的分析の実装** - 各ステップで結果を検証

## ✅ 完了した作業（Part 1）

### コミット: 27a91d3

- ✅ `import openai` 削除
- ✅ OpenAI client初期化削除 (`self.client`)
- ✅ Anthropic Claude APIを必須化
- ✅ 中間結果保存用の `self.intermediate_results` 追加
- ✅ ドキュメント文字列更新

**結果**: 130行削除、41行追加

## 🔄 残りの作業

### Part 2: OpenAI API呼び出しを完全削除

**対象ファイル**: `src/ai_analyzer_complete.py`

#### 削除が必要な箇所

1. **`_analyze_with_vision` メソッド内** (現在529行以降に死コードあり)
   - lines 531-720: OpenAI API結果処理コード全体
   - OpenAIコンテンツポリシー拒否チェック
   - OpenAI→Claude Vision→Claude Textのフォールバックチェーン

2. **`_analyze_with_text` メソッド内** (line 1121付近)
   - OpenAI API呼び出し
   - GPT-4 Turboモデル使用箇所

3. **他のファイル**:
   - `src/evidence_editor_ai.py` (lines 213, 279)

#### 置き換え方法

```python
# 旧: OpenAI API呼び出し
response = self.client.chat.completions.create(
    model=OPENAI_MODEL,
    messages=[...],
    max_tokens=OPENAI_MAX_TOKENS
)
result = response.choices[0].message.content

# 新: Claude APIのみ
result = self._analyze_with_claude_stepwise(...)
```

### Part 3: 段階的分析メソッドの実装

#### 新メソッド: `_analyze_with_claude_stepwise`

```python
def _analyze_with_claude_stepwise(self, 
                                   image_paths: List[str],
                                   prompt: str,
                                   file_type: str,
                                   pdf_text: str = "") -> Dict:
    """
    Claude Vision APIで段階的分析
    
    ステップ1: 各ページを個別に分析
    ステップ2: ページ間の一貫性をチェック
    ステップ3: 全体を統合分析
    ステップ4: JSON形式で結果を返す
    
    各ステップで中間結果を self.intermediate_results に保存
    """
    logger.info(f"📊 段階的分析開始: {len(image_paths)}ページ")
    
    # ステップ1: ページ単位分析
    page_results = []
    for i, image_path in enumerate(image_paths, 1):
        logger.info(f"  📄 ページ{i}分析中...")
        
        # ページ単独で分析
        page_prompt = f"""
Analyze page {i} of {len(image_paths)} from this legal document.

Extract:
1. OCR text from this page only
2. Key information (names, addresses, dates, amounts)
3. Document type indicators (contract, notice, certificate, etc.)

Return as JSON.
"""
        
        page_result = self._analyze_single_page_with_claude(image_path, page_prompt)
        page_results.append({
            'page': i,
            'result': page_result,
            'image_path': image_path
        })
        
        # 中間結果を保存
        self.intermediate_results[f'page_{i}'] = page_result
        logger.info(f"  ✅ ページ{i}分析完了")
    
    # ステップ2: ページ間一貫性チェック
    logger.info(f"  🔍 ページ間一貫性チェック...")
    consistency_check = self._check_page_consistency(page_results, pdf_text)
    self.intermediate_results['consistency_check'] = consistency_check
    
    if not consistency_check['is_consistent']:
        logger.warning(f"  ⚠️ ページ間の不整合を検出: {consistency_check['issues']}")
    else:
        logger.info(f"  ✅ ページ間の一貫性確認")
    
    # ステップ3: 全体統合分析
    logger.info(f"  📋 全体統合分析中...")
    
    # 全ページの情報を統合したプロンプト
    combined_prompt = self._build_combined_prompt(prompt, page_results, consistency_check)
    
    # 全画像と統合プロンプトでClaude Vision APIを呼び出し
    final_result = self._analyze_with_claude_multi_page(image_paths, combined_prompt)
    
    # ステップ4: JSON形式で返す
    self.intermediate_results['final_result'] = final_result
    
    logger.info(f"  ✅ 段階的分析完了")
    return final_result
```

#### 新メソッド: `_analyze_single_page_with_claude`

```python
def _analyze_single_page_with_claude(self, image_path: str, prompt: str) -> Dict:
    """
    単一ページをClaude Vision APIで分析
    """
    # 画像をBase64エンコード
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    mime_type = self._get_mime_type(image_path)
    
    # Claude Vision API呼び出し
    try:
        response = self.anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,  # ページ単位なので短め
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": mime_type,
                            "data": image_data
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }]
        )
        
        result_text = response.content[0].text
        
        # JSON解析
        return self._parse_json_safely(result_text)
        
    except Exception as e:
        logger.error(f"Claude Vision API呼び出し失敗: {e}")
        return {'error': str(e)}
```

#### 新メソッド: `_check_page_consistency`

```python
def _check_page_consistency(self, page_results: List[Dict], pdf_text: str = "") -> Dict:
    """
    ページ間の一貫性をチェック
    
    確認項目:
    1. 同じ文書か（文書タイプ、差出人、受取人など）
    2. ページ番号の連続性
    3. PDFテキスト抽出との一致率
    """
    import re
    
    consistency = {
        'is_consistent': True,
        'issues': [],
        'document_type': None,
        'sender': None,
        'recipient': None
    }
    
    # ページ1から文書タイプを取得
    if len(page_results) > 0:
        page1 = page_results[0]['result']
        consistency['document_type'] = page1.get('document_type')
        consistency['sender'] = page1.get('sender')
        consistency['recipient'] = page1.get('recipient')
    
    # 各ページの文書タイプを確認
    for page_result in page_results[1:]:
        page_doc_type = page_result['result'].get('document_type')
        if page_doc_type and page_doc_type != consistency['document_type']:
            consistency['is_consistent'] = False
            consistency['issues'].append(
                f"ページ{page_result['page']}の文書タイプが異なる: "
                f"{consistency['document_type']} vs {page_doc_type}"
            )
    
    # PDFテキスト抽出との一致確認
    if pdf_text:
        # ページ1のOCRテキストとPDF抽出テキストを比較
        page1_ocr = page_results[0]['result'].get('ocr_text', '')
        
        # キーワード一致率
        patterns = [
            r'\d{3}-?\d{4}',  # 郵便番号
            r'\d{2,4}年\d{1,2}月\d{1,2}日',  # 日付
        ]
        
        pdf_keywords = set()
        for pattern in patterns:
            pdf_keywords.update(re.findall(pattern, pdf_text))
        
        ocr_keywords = set()
        for pattern in patterns:
            ocr_keywords.update(re.findall(pattern, page1_ocr))
        
        if pdf_keywords and len(pdf_keywords & ocr_keywords) / len(pdf_keywords) < 0.5:
            consistency['issues'].append(
                f"ページ1のOCRテキストとPDF抽出の一致率が低い"
            )
    
    return consistency
```

#### 新メソッド: `_build_combined_prompt`

```python
def _build_combined_prompt(self, 
                           original_prompt: str,
                           page_results: List[Dict],
                           consistency_check: Dict) -> str:
    """
    ページ単位の分析結果を統合したプロンプトを構築
    """
    # ページ単位の情報をまとめる
    pages_summary = []
    for page_result in page_results:
        page_num = page_result['page']
        result = page_result['result']
        
        summary = f"""
Page {page_num}:
- Document type: {result.get('document_type', 'Unknown')}
- Key entities: {result.get('key_entities', [])}
- OCR text (first 200 chars): {result.get('ocr_text', '')[:200]}
"""
        pages_summary.append(summary)
    
    # 統合プロンプト
    combined_prompt = f"""
CONTEXT: This document has {len(page_results)} pages. Each page has been pre-analyzed.

PAGE-BY-PAGE SUMMARY:
{''.join(pages_summary)}

CONSISTENCY CHECK:
- Document consistency: {'✅ Consistent' if consistency_check['is_consistent'] else '⚠️ Inconsistent'}
- Issues: {', '.join(consistency_check['issues']) if consistency_check['issues'] else 'None'}

TASK:
Based on the above page-level analysis, now perform a comprehensive analysis of the entire document.

{original_prompt}

IMPORTANT:
- Use the page-level OCR text provided above
- Ensure the analysis is consistent across all pages
- If there are inconsistencies, explain them in the analysis
"""
    
    return combined_prompt
```

### Part 4: JSON解析エラーハンドリング強化

既に実装済みの `_parse_json_safely` メソッドを活用し、段階的分析の各ステップで使用する。

```python
def _parse_json_safely(self, text: str) -> Dict:
    """
    JSON解析を安全に行う（既存メソッドを改善）
    """
    # 既存の修復ロジックを使用
    # さらに改善: 複数の修復戦略を試す
    pass
```

## 📊 期待される効果

### Before（現在）

```
OpenAI API呼び出し
  ↓ 拒否される
Claude Vision API（全ページ一括）
  ↓ JSON解析エラー
失敗
```

### After（改善後）

```
ステップ1: ページ1分析 → 成功 ✅
ステップ1: ページ2分析 → 成功 ✅
ステップ1: ページ3分析 → 成功 ✅
ステップ2: 一貫性チェック → 問題なし ✅
ステップ3: 全体統合分析 → 成功 ✅
ステップ4: JSON形式化 → 成功 ✅
```

## 🔧 実装手順

1. **Part 2を完了** - OpenAI APIコード全削除
2. **Part 3を実装** - 段階的分析メソッド追加
3. **テスト** - tmp_ko_004で動作確認
4. **コミット＆プッシュ** - PR更新

## 📝 ユーザー様へのメッセージ

現在、OpenAI APIの削除作業を進めています（Part 1完了）。

残りの作業は大きいため、以下の選択肢があります：

### オプション1: 完全実装（推奨、時間がかかる）
- OpenAI API完全削除
- 段階的分析メソッド実装
- 全機能テスト

### オプション2: 最小限の修正（速い）
- OpenAI APIコールを全てClaude APIに置き換え
- 段階的分析は後回し
- 動作するシステムを優先

どちらを希望されますか？

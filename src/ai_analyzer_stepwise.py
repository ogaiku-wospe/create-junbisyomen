"""
段階的AI分析エンジン
JSONを一度に生成せず、ステップごとに局所的・持続的に生成することで確実性と正確性を向上
"""

import os
import json
import logging
import base64
from typing import Dict, List, Optional, Any
import anthropic

from global_config import *

logger = logging.getLogger(__name__)


class StepwiseAnalyzer:
    """段階的分析クラス - JSONを局所的・持続的に生成"""
    
    def __init__(self, anthropic_client: anthropic.Anthropic):
        """初期化"""
        self.anthropic_client = anthropic_client
        self.intermediate_results = {}
        
        logger.info("✅ StepwiseAnalyzer初期化完了")
    
    def analyze_evidence_stepwise(self,
                                   evidence_id: str,
                                   image_paths: List[str],
                                   pdf_text: str = "") -> Dict:
        """
        証拠を段階的に分析してJSONを局所的に生成
        
        ステップ1: メタデータ抽出 (証拠の基本情報)
        ステップ2: OCRテキスト抽出 (全ページのテキスト)
        ステップ3: 文書内容分析 (文書タイプ、当事者など)
        ステップ4: 法的意義抽出 (法的評価)
        ステップ5: 関連事実抽出 (事実関係)
        ステップ6: 最終統合 (全体をまとめる)
        
        各ステップでJSONの一部を生成し、最後に統合
        """
        logger.info(f"🎯 段階的分析開始: {evidence_id} ({len(image_paths)}ページ)")
        
        # 中間結果をクリア
        self.intermediate_results = {
            'evidence_id': evidence_id,
            'page_count': len(image_paths),
            'pdf_text_preview': pdf_text[:200] if pdf_text else ""
        }
        
        # ステップ1: メタデータ抽出
        logger.info("📊 [1/6] メタデータ抽出")
        metadata_json = self._step1_extract_metadata(image_paths[0], evidence_id)
        self.intermediate_results['step1_metadata'] = metadata_json
        logger.info(f"   ✅ メタデータ抽出完了: {len(json.dumps(metadata_json))}文字")
        
        # ステップ2: OCRテキスト抽出（全ページ）
        logger.info("📄 [2/6] OCRテキスト抽出")
        ocr_json = self._step2_extract_ocr_text(image_paths)
        self.intermediate_results['step2_ocr'] = ocr_json
        total_ocr_chars = sum(len(page.get('text', '')) for page in ocr_json.get('pages', []))
        logger.info(f"   ✅ OCRテキスト抽出完了: {total_ocr_chars}文字（{len(ocr_json.get('pages', []))}ページ）")
        
        # ステップ3: 文書内容分析
        logger.info("📋 [3/6] 文書内容分析")
        content_json = self._step3_analyze_content(image_paths, ocr_json, pdf_text)
        self.intermediate_results['step3_content'] = content_json
        logger.info(f"   ✅ 文書内容分析完了: 文書タイプ={content_json.get('document_type')}")
        
        # ステップ4: 法的意義抽出
        logger.info("⚖️ [4/6] 法的意義抽出")
        legal_json = self._step4_extract_legal_significance(content_json, ocr_json)
        self.intermediate_results['step4_legal'] = legal_json
        logger.info(f"   ✅ 法的意義抽出完了")
        
        # ステップ5: 関連事実抽出
        logger.info("🔍 [5/6] 関連事実抽出")
        facts_json = self._step5_extract_related_facts(content_json, ocr_json, legal_json)
        self.intermediate_results['step5_facts'] = facts_json
        logger.info(f"   ✅ 関連事実抽出完了")
        
        # ステップ6: 最終統合
        logger.info("🔗 [6/6] 最終統合")
        final_json = self._step6_final_integration(
            metadata_json, ocr_json, content_json, legal_json, facts_json
        )
        self.intermediate_results['step6_final'] = final_json
        logger.info(f"   ✅ 最終統合完了")
        
        logger.info(f"🎉 段階的分析完了: {evidence_id}")
        
        return final_json
    
    def _step1_extract_metadata(self, first_image_path: str, evidence_id: str) -> Dict:
        """
        ステップ1: メタデータ抽出
        - 文書の基本情報のみを抽出
        - JSONは小さく局所的に生成
        """
        prompt = f"""
Analyze the FIRST PAGE of this evidence document and extract ONLY basic metadata.

TASK: Extract the following information as JSON:
{{
  "evidence_id": "{evidence_id}",
  "document_basic_info": "Brief description in Japanese (1 sentence, max 50 chars)",
  "file_info": "File type and page count",
  "page_count": <number>
}}

IMPORTANT:
- Keep the JSON small and focused
- Only extract what you can see on the FIRST PAGE
- Use Japanese for descriptions
- Do NOT include OCR text yet (that comes in Step 2)
- Do NOT analyze content deeply (that comes in Step 3)

Return ONLY the JSON, no other text.
"""
        
        result = self._call_claude_vision(first_image_path, prompt, max_tokens=500)
        return self._parse_json_from_response(result)
    
    def _step2_extract_ocr_text(self, image_paths: List[str]) -> Dict:
        """
        ステップ2: OCRテキスト抽出（全ページ）
        - 各ページからテキストのみを抽出
        - 分析はせず、テキストのみ
        """
        pages_ocr = []
        
        for i, image_path in enumerate(image_paths, 1):
            logger.info(f"   📄 ページ{i}のOCR実行中...")
            
            prompt = f"""
Perform high-accuracy OCR text extraction from this page.

TASK: Extract ALL text precisely, return as JSON:
{{
  "page": {i},
  "text": "All text from this page, character-by-character, in original language",
  "char_count": <number of characters>
}}

CRITICAL OCR REQUIREMENTS:
✅ Extract EVERY character visible on the page
✅ Preserve ALL formatting: line breaks, spacing, indentation
✅ Include ALL punctuation, symbols, and special characters
✅ For Japanese text:
  - Preserve kanji, hiragana, katakana exactly as shown
  - Include postal codes (〒xxx-xxxx format)
  - Include phone numbers, dates, addresses
  - Maintain vertical/horizontal text layout distinctions
✅ For stamps/seals: Include any readable text within stamps
✅ For headers/footers: Include all header and footer text
✅ For tables: Preserve table structure with appropriate spacing

❌ Do NOT translate any text
❌ Do NOT summarize or paraphrase
❌ Do NOT skip any portion of the text
❌ Do NOT add interpretations or analysis

QUALITY CHECK: Ensure char_count matches actual extracted characters.

Return ONLY the JSON, no other text.
"""
            
            result = self._call_claude_vision(image_path, prompt, max_tokens=4096)
            page_json = self._parse_json_from_response(result)
            pages_ocr.append(page_json)
            
            logger.info(f"   ✅ ページ{i}完了: {page_json.get('char_count', 0)}文字")
        
        # 全ページのテキストを統合
        full_text = '\n\n=== ページ区切り ===\n\n'.join(
            page.get('text', '') for page in pages_ocr
        )
        
        return {
            "pages": pages_ocr,
            "full_text": full_text,
            "total_chars": sum(page.get('char_count', 0) for page in pages_ocr)
        }
    
    def _step3_analyze_content(self, image_paths: List[str], ocr_json: Dict, pdf_text: str) -> Dict:
        """
        ステップ3: 文書内容分析
        - OCRテキストを使って文書の内容を分析
        - 文書タイプ、当事者、日付など
        """
        # OCRテキストを取得
        full_ocr_text = ocr_json.get('full_text', '')
        
        prompt = f"""
Analyze this legal document based on the extracted OCR text.

OCR TEXT:
{full_ocr_text[:3000]}
{"..." if len(full_ocr_text) > 3000 else ""}

TASK: Analyze and return as JSON:
{{
  "document_type": "Document type in Japanese (配達証明, 通知書, 契約書, etc.)",
  "sender": {{
    "name": "Sender name",
    "address": "Sender address",
    "organization": "Organization if applicable"
  }},
  "recipient": {{
    "name": "Recipient name",
    "address": "Recipient address"
  }},
  "date": "Document date if found (YYYY-MM-DD or original format)",
  "subject": "Main subject or purpose in Japanese",
  "key_entities": ["List", "of", "important", "names", "organizations"]
}}

IMPORTANT:
- Base analysis ONLY on the OCR text provided
- Use Japanese for descriptions
- Extract factual information only
- If information is not found, use null or empty string

Return ONLY the JSON, no other text.
"""
        
        # 1ページ目の画像も参照（視覚的確認用）
        result = self._call_claude_vision(image_paths[0], prompt, max_tokens=1500)
        return self._parse_json_from_response(result)
    
    def _step4_extract_legal_significance(self, content_json: Dict, ocr_json: Dict) -> Dict:
        """
        ステップ4: 法的意義抽出
        - 文書の法的な意味を分析
        - 証拠能力、証明事項など
        """
        doc_type = content_json.get('document_type', '')
        subject = content_json.get('subject', '')
        
        prompt = f"""
Analyze the legal significance of this document.

DOCUMENT INFO:
- Type: {doc_type}
- Subject: {subject}
- Sender: {content_json.get('sender', {}).get('name', '')}
- Recipient: {content_json.get('recipient', {}).get('name', '')}

TASK: Extract legal significance as JSON:
{{
  "legal_document_type": "Legal classification in Japanese",
  "evidential_value": "What this document can prove",
  "legal_implications": "Legal implications in Japanese",
  "proof_points": ["Point 1", "Point 2", "Point 3"]
}}

IMPORTANT:
- Focus on legal significance only
- Use Japanese for descriptions
- Be specific about what can be legally proven

Return ONLY the JSON, no other text.
"""
        
        result = self._call_claude_text(prompt, max_tokens=1500)
        return self._parse_json_from_response(result)
    
    def _step5_extract_related_facts(self, content_json: Dict, ocr_json: Dict, legal_json: Dict) -> Dict:
        """
        ステップ5: 関連事実抽出
        - 文書に含まれる事実関係を抽出
        """
        full_text = ocr_json.get('full_text', '')
        
        prompt = f"""
Extract factual information from this legal document.

OCR TEXT (excerpt):
{full_text[:2000]}

DOCUMENT CONTEXT:
- Type: {content_json.get('document_type', '')}
- Parties: {content_json.get('sender', {}).get('name', '')} → {content_json.get('recipient', {}).get('name', '')}

TASK: Extract facts as JSON:
{{
  "chronology": [
    {{"date": "YYYY-MM-DD", "event": "What happened in Japanese"}}
  ],
  "amounts": [
    {{"type": "金額種類", "amount": "金額", "currency": "JPY"}}
  ],
  "claims": [
    "Claim or assertion in Japanese"
  ],
  "supporting_facts": [
    "Supporting fact in Japanese"
  ]
}}

IMPORTANT:
- Extract factual information only
- Use Japanese for descriptions
- Include dates if found
- Be specific and concrete

Return ONLY the JSON, no other text.
"""
        
        result = self._call_claude_text(prompt, max_tokens=2000)
        return self._parse_json_from_response(result)
    
    def _step6_final_integration(self,
                                  metadata_json: Dict,
                                  ocr_json: Dict,
                                  content_json: Dict,
                                  legal_json: Dict,
                                  facts_json: Dict) -> Dict:
        """
        ステップ6: 最終統合
        - 各ステップの結果を統合して最終JSONを生成
        """
        # 証拠の説明を生成
        description = self._generate_description(content_json, ocr_json)
        
        # 完全性スコアを計算
        completeness = self._calculate_completeness(
            metadata_json, ocr_json, content_json, legal_json, facts_json
        )
        
        # 最終JSONを構築
        final_json = {
            "evidence_id": metadata_json.get('evidence_id', ''),
            "verbalization_level": 4,
            "confidence_score": completeness,
            
            "evidence_metadata": {
                "証拠の基本情報": metadata_json.get('document_basic_info', ''),
                "ファイル情報": metadata_json.get('file_info', ''),
                "ページ数": metadata_json.get('page_count', 0)
            },
            
            "full_content": {
                "OCRテキスト": ocr_json.get('full_text', ''),
                "総文字数": ocr_json.get('total_chars', 0),
                "ページ別テキスト": ocr_json.get('pages', [])
            },
            
            "証拠の説明": description,
            
            "文書の内容": {
                "文書種別": content_json.get('document_type', ''),
                "差出人": content_json.get('sender', {}),
                "受取人": content_json.get('recipient', {}),
                "日付": content_json.get('date', ''),
                "件名": content_json.get('subject', ''),
                "重要な固有名詞": content_json.get('key_entities', [])
            },
            
            "legal_significance": {
                "法的文書種別": legal_json.get('legal_document_type', ''),
                "証拠能力": legal_json.get('evidential_value', ''),
                "法的含意": legal_json.get('legal_implications', ''),
                "証明事項": legal_json.get('proof_points', [])
            },
            
            "related_facts": {
                "時系列": facts_json.get('chronology', []),
                "金額情報": facts_json.get('amounts', []),
                "主張内容": facts_json.get('claims', []),
                "裏付け事実": facts_json.get('supporting_facts', [])
            },
            
            "usage_suggestions": {
                "提出タイミング": self._suggest_timing(content_json, legal_json),
                "他の証拠との関連": self._suggest_relations(content_json, facts_json),
                "注意点": self._suggest_notes(content_json, legal_json)
            },
            
            "完全性スコア": completeness
        }
        
        return final_json
    
    def _call_claude_vision(self, image_path: str, prompt: str, max_tokens: int = 2048) -> str:
        """Claude Vision APIを呼び出し"""
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        mime_type = 'image/jpeg'
        if image_path.endswith('.png'):
            mime_type = 'image/png'
        
        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=max_tokens,
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
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Claude Vision API呼び出し失敗: {e}")
            return "{}"
    
    def _call_claude_text(self, prompt: str, max_tokens: int = 2048) -> str:
        """Claude Text APIを呼び出し"""
        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=max_tokens,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Claude Text API呼び出し失敗: {e}")
            return "{}"
    
    def _parse_json_from_response(self, response: str) -> Dict:
        """APIレスポンスからJSONを抽出してパース"""
        try:
            # ```json ``` で囲まれている場合
            if '```json' in response:
                json_str = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                json_str = response.split('```')[1].split('```')[0].strip()
            else:
                json_str = response.strip()
            
            return json.loads(json_str)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析エラー: {e}")
            logger.debug(f"レスポンス: {response[:500]}")
            return {}
        except Exception as e:
            logger.error(f"JSON抽出エラー: {e}")
            return {}
    
    def _generate_description(self, content_json: Dict, ocr_json: Dict) -> str:
        """証拠の説明を生成"""
        doc_type = content_json.get('document_type', '文書')
        sender = content_json.get('sender', {}).get('name', '不明')
        recipient = content_json.get('recipient', {}).get('name', '不明')
        subject = content_json.get('subject', '')
        
        description = f"{doc_type}。{sender}から{recipient}への文書。"
        if subject:
            description += f"件名：{subject}。"
        
        return description
    
    def _calculate_completeness(self, *args) -> float:
        """完全性スコアを計算"""
        # 各ステップの結果が揃っているかチェック
        total_steps = len(args)
        completed_steps = sum(1 for arg in args if arg and isinstance(arg, dict) and len(arg) > 0)
        
        return round(completed_steps / total_steps, 2)
    
    def _suggest_timing(self, content_json: Dict, legal_json: Dict) -> str:
        """提出タイミングの提案"""
        return "事実関係の主張時、または相手方の主張への反論時に使用可能"
    
    def _suggest_relations(self, content_json: Dict, facts_json: Dict) -> str:
        """他の証拠との関連の提案"""
        return "時系列で前後する証拠と組み合わせることで、事実の連続性を示せる"
    
    def _suggest_notes(self, content_json: Dict, legal_json: Dict) -> str:
        """注意点の提案"""
        doc_type = content_json.get('document_type', '')
        if '配達証明' in doc_type:
            return "配達証明書は送達の事実を証明するが、文書内容の真実性は別途立証が必要"
        else:
            return "文書の真正性（作成者が本当に作成したか）を確認する必要がある"

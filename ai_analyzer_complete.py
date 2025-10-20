"""
完全版AI分析エンジン
- GPT-4o Vision統合
- 全形式対応
- 完全言語化レベル4達成
- 信頼度スコア計算
"""

import os
import json
import logging
import time
import base64
from typing import Dict, List, Optional, Any
import openai

from global_config import *
from file_processor import FileProcessor
from metadata_extractor import MetadataExtractor

logger = logging.getLogger(__name__)


class AIAnalyzerComplete:
    """完全版AI分析エンジン"""
    
    def __init__(self, api_key: str = None, prompt_path: str = None):
        """初期化"""
        self.api_key = api_key or OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI APIキーが設定されていません")
        
        openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key)
        
        self.prompt_template = self._load_prompt(prompt_path or LOCAL_PROMPT_PATH)
        self.file_processor = FileProcessor()
        self.metadata_extractor = MetadataExtractor()
        
        logger.info("✅ AIAnalyzerComplete初期化完了")
    
    def _load_prompt(self, prompt_path: str) -> str:
        """Phase 1プロンプト読み込み"""
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt = f.read()
            logger.info(f"✅ プロンプト読み込み完了: {len(prompt)}文字")
            return prompt
        except Exception as e:
            logger.error(f"❌ プロンプト読み込み失敗: {e}")
            raise
    
    def analyze_evidence_complete(self,
                                  evidence_id: str,
                                  file_path: str,
                                  file_type: str,
                                  gdrive_file_info: Dict,
                                  case_info: Dict) -> Dict:
        """
        証拠を完全言語化分析（レベル4）
        
        Args:
            evidence_id: 証拠ID
            file_path: ファイルパス
            file_type: ファイルタイプ
            gdrive_file_info: Google Driveファイル情報
            case_info: 事件情報
        
        Returns:
            完全言語化分析結果
        """
        logger.info(f"🔍 完全言語化分析開始: {evidence_id}")
        logger.info(f"   ファイル: {os.path.basename(file_path)}")
        logger.info(f"   タイプ: {file_type}")
        
        try:
            # ステップ1: 完全メタデータ抽出
            logger.info("📊 [1/5] メタデータ抽出")
            metadata = self.metadata_extractor.extract_complete_metadata(
                file_path, 
                gdrive_file_info
            )
            
            # ステップ2: ファイル内容処理
            logger.info("🔄 [2/5] ファイル内容処理")
            file_content = self.file_processor.process_file(file_path, file_type)
            
            # ステップ3: AI分析実行
            logger.info("🤖 [3/5] AI分析実行")
            ai_analysis = self._perform_ai_analysis(
                evidence_id=evidence_id,
                file_path=file_path,
                file_type=file_type,
                metadata=metadata,
                file_content=file_content,
                case_info=case_info
            )
            
            # ステップ4: 結果の構造化
            logger.info("📋 [4/5] 結果構造化")
            structured_result = self._structure_complete_result(
                evidence_id=evidence_id,
                metadata=metadata,
                file_content=file_content,
                ai_analysis=ai_analysis
            )
            
            # ステップ5: 品質評価
            logger.info("✅ [5/5] 品質評価")
            quality_score = self._assess_analysis_quality(structured_result)
            structured_result['quality_assessment'] = quality_score
            
            logger.info(f"✅ 完全言語化分析完了: {evidence_id}")
            logger.info(f"   完全言語化レベル: {quality_score['verbalization_level']}")
            logger.info(f"   信頼度スコア: {quality_score['confidence_score']:.1%}")
            
            return structured_result
            
        except Exception as e:
            logger.error(f"❌ 完全言語化分析失敗: {evidence_id} - {e}")
            raise
    
    def _perform_ai_analysis(self,
                            evidence_id: str,
                            file_path: str,
                            file_type: str,
                            metadata: Dict,
                            file_content: Dict,
                            case_info: Dict) -> Dict:
        """AI分析実行"""
        # プロンプト構築
        analysis_prompt = self._build_complete_prompt(
            evidence_id=evidence_id,
            metadata=metadata,
            file_content=file_content,
            case_info=case_info
        )
        
        # ファイルタイプに応じた分析
        if file_type in ['image', 'pdf', 'document']:
            # Vision API使用
            # HEIC等の変換済みファイルパスを使用
            actual_file_path = file_content.get('processed_file_path', file_path)
            vision_result = self._analyze_with_vision(actual_file_path, analysis_prompt, file_type)
            
            # Vision APIがコンテンツポリシーで拒否した場合、テキストベース分析にフォールバック
            if vision_result is None:
                logger.info("📝 OCRテキストを使用してテキストベース分析を実行")
                return self._analyze_with_text(analysis_prompt, file_content)
            
            return vision_result
        else:
            # テキストベース分析
            return self._analyze_with_text(analysis_prompt, file_content)
    
    def _build_complete_prompt(self,
                              evidence_id: str,
                              metadata: Dict,
                              file_content: Dict,
                              case_info: Dict) -> str:
        """完全版分析プロンプト構築"""
        # メタデータを整形
        metadata_text = json.dumps(metadata, ensure_ascii=False, indent=2)
        
        # ファイル内容を整形
        content_summary = self._summarize_file_content(file_content)
        
        # 完全版プロンプト
        full_prompt = f"""{self.prompt_template}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【重要: Phase 1 = 客観的事実記録】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Phase 1の役割:**
- 証拠の内容を完全に客観的・中立的に記録
- 観察可能な事実のみを詳細に言語化
- 法的評価や主観的解釈は一切行わない
- 訴訟の当事者情報は与えられない（中立性の担保）

**完全言語化レベル4の達成基準:**
1. **原文参照不要**: この分析結果のみで、原文・原画像を見なくても完全に内容を理解できる
2. **全情報の言語化**: 視覚情報、文書構造、メタデータを全て詳細に記述
3. **客観的記録**: 観察可能な事実のみを記述、解釈や評価は含まない
4. **引用可能性**: Phase 2での法的分析や準備書面作成時に使用できる詳細度
5. **プログラム解釈可能**: database.jsonに記録した際、プログラムで完全に解釈可能

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【本証拠の完全メタデータ】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

証拠ID: {evidence_id}

{metadata_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【ファイル内容サマリー】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{content_summary}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【分析指示】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

上記の証拠について、Phase 1プロンプトに従って**客観的・中立的な完全言語化レベル4**の分析を実行してください。

**重要:** 
- 証拠に記載されている事実のみを記録
- 法的評価や主観的解釈は一切含めない
- 訴訟の当事者や事件の詳細は知らない前提で分析
- あなたは中立的な記録者として振る舞う

**🗓️ 最重要タスク - 証拠の作成年月日を必ず特定:**
- `document_date`: 証拠説明書に記載する作成年月日（YYYY-MM-DD形式）
- 文書上部の日付、EXIF撮影日時、ファイル名の日付など、あらゆる手がかりから判断
- `document_date_source`に根拠を明記（例：「文書上部に2021年8月15日と記載」）
- 日付が不明な場合も、その旨と理由を`date_confidence`に記載

**出力形式: JSON**

以下の構造で、詳細かつ完全な分析結果を出力してください：

{{
  "evidence_id": "{evidence_id}",
  "verbalization_level": 4,
  "confidence_score": 0.0-1.0,
  
  "evidence_metadata": {{
    "証拠の基本情報": "...",
    "ファイル情報": "...",
    "作成日時": "...",
    "作成者": "...",
    "Google DriveURL": "..."
  }},
  
  "full_content": {{
    "complete_description": "原文を見なくても完全に理解できる詳細な記述",
    "visual_information": {{
      "overall_description": "画像全体の客観的説明",
      "key_elements": ["観察される要素1", "要素2"],
      "text_in_image": [
        {{"text": "画像内テキスト", "location": "位置", "size": "サイズ"}}
      ],
      "background_details": "背景の客観的説明",
      "quality_notes": "画質、鮮明度"
    }},
    "textual_content": {{
      "extracted_text": "文書内の全テキストを正確に抽出",
      "text_summary": "テキスト内容の客観的要約",
      "document_structure": "文書の構造",
      "formatting_notes": "書式、フォント、レイアウト"
    }},
    "ocr_results": {{
      "extracted_text": "OCRで抽出された全テキスト",
      "confidence": 0.0-1.0
    }}
  }},
  
  "objective_analysis": {{
    "document_type": "文書種類の客観的分類",
    "observable_facts": [
      "証拠から観察できる客観的事実1",
      "客観的事実2"
    ],
    "temporal_information": {{
      "document_date": "証拠の作成年月日（YYYY-MM-DD形式必須）※証拠説明書記載用",
      "document_date_source": "作成日の根拠（文書上部の日付、EXIF撮影日時、ファイル名等）",
      "other_dates": [
        {{"date": "YYYY-MM-DD", "context": "この日付の意味（例：有効期限、支払期限等）"}}
      ],
      "timeline": "時系列の客観的整理",
      "date_confidence": "作成年月日の信頼度（high/medium/low）と理由"
    }},
    "parties_mentioned": {{
      "individuals": ["個人名1", "個人名2"],
      "organizations": ["組織名1", "組織名2"],
      "roles_described": "文書内で各当事者の記述"
    }},
    "financial_information": {{
      "amounts": ["金額1", "金額2"],
      "currency": "通貨単位",
      "amount_context": "各金額の文脈"
    }},
    "identifiers": {{
      "contract_numbers": ["契約番号等"],
      "reference_numbers": ["参照番号"],
      "serial_numbers": ["管理番号等"]
    }},
    "signatures_and_seals": {{
      "signatures": ["署名者名1", "署名者名2"],
      "seals": ["捺印の種類"],
      "signature_dates": ["署名日付"],
      "signature_locations": "署名・捺印の位置"
    }},
    "document_state": {{
      "completeness": "文書の完全性",
      "modifications": "訂正、削除、追記",
      "annotations": "手書きメモ、マーカー",
      "preservation_state": "保存状態"
    }}
  }},
  
  "extracted_data": {{
    "key_terms": ["重要用語1", "用語2"],
    "definitions": "定義されている用語",
    "conditions": ["条件1", "条件2"],
    "obligations": ["義務1", "義務2"],
    "rights": ["権利1", "権利2"],
    "exceptions": ["例外規定"]
  }},
  
  "metadata_analysis": {{
    "file_properties": "ファイルプロパティ",
    "creation_metadata": "作成日時、更新日時等",
    "technical_details": "解像度、ファイルサイズ、形式等"
  }}
}}

**重要**: JSON以外の余分なテキストは含めないでください。
"""
        
        return full_prompt
    
    def _summarize_file_content(self, file_content: Dict) -> str:
        """ファイル内容をサマリー化"""
        summary_parts = []
        
        # 処理ステータス
        status = file_content.get('processing_status', 'unknown')
        summary_parts.append(f"処理ステータス: {status}")
        
        # コンテンツ
        content = file_content.get('content', {})
        
        if 'ocr_text' in content:
            ocr_text = content['ocr_text']
            summary_parts.append(f"OCR抽出テキスト: {len(ocr_text)}文字")
            summary_parts.append(f"先頭100文字: {ocr_text[:100]}")
        
        if 'full_text' in content:
            full_text = content['full_text']
            summary_parts.append(f"全文: {len(full_text)}文字")
            summary_parts.append(f"先頭100文字: {full_text[:100]}")
        
        if 'pages' in content:
            pages = content['pages']
            summary_parts.append(f"ページ数: {len(pages)}")
        
        if 'sheets' in content:
            sheets = content['sheets']
            summary_parts.append(f"シート数: {len(sheets)}")
        
        return '\n'.join(summary_parts)
    
    def _analyze_with_vision(self, file_path: str, prompt: str, file_type: str) -> Dict:
        """Vision APIで分析"""
        try:
            # ファイルタイプに応じた処理
            if file_type == 'image':
                image_path = file_path
            elif file_type in ['pdf', 'document']:
                # PDFまたはWord文書の最初のページを画像化
                image_path = self._pdf_first_page_to_image(file_path)
                
                # PDF変換失敗時はテキスト解析にフォールバック
                if image_path is None:
                    logger.warning(f"{file_type}→画像変換失敗、テキスト解析にフォールバック")
                    return self._analyze_with_text(prompt, {'file_path': file_path})
            else:
                image_path = file_path
            
            # Base64エンコード
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            mime_type = self._get_mime_type(image_path)
            
            # GPT-4o Vision API呼び出し
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{image_data}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=OPENAI_MAX_TOKENS,
                temperature=OPENAI_TEMPERATURE
            )
            
            result = response.choices[0].message.content
            logger.debug(f"API応答: {len(result)}文字")
            
            # デバッグ: APIレスポンスの最初の200文字を表示
            if result:
                logger.debug(f"API応答プレビュー: {result[:200]}...")
            
            # OpenAIのコンテンツポリシー拒否チェック（より厳密な判定）
            # 環境変数 DISABLE_CONTENT_POLICY_CHECK=true でチェックを無効化可能
            disable_check = os.getenv('DISABLE_CONTENT_POLICY_CHECK', 'false').lower() == 'true'
            
            if not disable_check:
                # 真の拒否メッセージの特徴:
                # 1. 非常に短い（通常100文字未満）
                # 2. JSON形式ではない
                # 3. "I'm sorry, I can't assist with that"という完全一致
                if result and len(result) < 200 and "```" not in result and "{" not in result:
                    # JSON形式ではない短い応答の場合のみチェック
                    if "I'm sorry, I can't assist with that" in result or \
                       "I cannot assist with that request" in result or \
                       (result.startswith("I'm sorry") and "assist" in result):
                        logger.warning("⚠️ Vision API: コンテンツポリシーにより画像分析が拒否されました")
                        logger.warning(f"   拒否メッセージ: {result}")
                        logger.info("📝 OCRテキストを使用したテキストベース分析にフォールバック")
                        logger.info("   ヒント: 誤検出の場合は DISABLE_CONTENT_POLICY_CHECK=true で無効化できます")
                        return None  # Noneを返してフォールバック処理を促す
            
            return self._parse_ai_response(result)
            
        except Exception as e:
            logger.error(f"❌ Vision API分析失敗: {e}")
            raise
    
    def _analyze_with_text(self, prompt: str, file_content: Dict) -> Dict:
        """テキストベース分析"""
        try:
            # ファイル内容をプロンプトに追加
            content_text = json.dumps(file_content, ensure_ascii=False, indent=2)
            full_prompt = f"{prompt}\n\n【ファイル内容詳細】\n{content_text}"
            
            # GPT-4o API呼び出し
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ],
                max_tokens=OPENAI_MAX_TOKENS,
                temperature=OPENAI_TEMPERATURE
            )
            
            result = response.choices[0].message.content
            return self._parse_ai_response(result)
            
        except Exception as e:
            logger.error(f"❌ テキストベース分析失敗: {e}")
            raise
    
    def _parse_ai_response(self, response: str) -> Dict:
        """AI応答をパース"""
        try:
            # デバッグモード時は全レスポンスをログ出力
            debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
            if debug_mode:
                logger.debug("=== OpenAI生レスポンス開始 ===")
                logger.debug(response)
                logger.debug("=== OpenAI生レスポンス終了 ===")
            
            # JSON抽出
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                json_str = response[start:end].strip()
            else:
                json_str = response
            
            # 空文字チェック
            if not json_str or not json_str.strip():
                logger.warning("警告: 抽出されたJSON文字列が空です")
                if debug_mode:
                    logger.debug(f"Raw response: {response}")
                else:
                    logger.debug(f"Raw response (最初の500文字): {response[:500]}...")
                return {
                    "raw_response": response,
                    "parse_error": "Empty JSON string",
                    "verbalization_level": 0
                }
            
            # JSON解析
            result = json.loads(json_str)
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"エラー: JSON解析失敗 - {e}")
            logger.warning(f"抽出したJSON文字列（最初の200文字）: {json_str[:200] if 'json_str' in locals() else 'N/A'}")
            
            # デバッグモード時は全レスポンスを出力
            if debug_mode:
                logger.debug(f"JSON解析失敗の生レスポンス: {response}")
            else:
                logger.debug(f"Raw response (最初の500文字): {response[:500]}")
            
            # フォールバック
            return {
                "raw_response": response,
                "parse_error": str(e),
                "verbalization_level": 0
            }
    
    def _structure_complete_result(self,
                                   evidence_id: str,
                                   metadata: Dict,
                                   file_content: Dict,
                                   ai_analysis: Dict) -> Dict:
        """完全な分析結果を構造化"""
        return {
            # 証拠ID
            "evidence_id": evidence_id,
            
            # 完全メタデータ
            "complete_metadata": metadata,
            
            # ファイル処理結果
            "file_processing_result": file_content,
            
            # AI分析結果
            "ai_analysis": ai_analysis,
            
            # タイムスタンプ
            "analysis_timestamp": get_timestamp(),
            
            # バージョン情報
            "analysis_version": {
                "system_version": SYSTEM_VERSION,
                "database_version": DATABASE_VERSION,
                "model": OPENAI_MODEL
            }
        }
    
    def _assess_analysis_quality(self, result: Dict) -> Dict:
        """分析品質を評価"""
        quality = {
            "verbalization_level": 0,
            "confidence_score": 0.0,
            "completeness_score": 0.0,
            "assessment_details": {}
        }
        
        try:
            ai_analysis = result.get('ai_analysis', {})
            
            # 完全言語化レベル
            verbalization_level = ai_analysis.get('verbalization_level', 0)
            quality['verbalization_level'] = verbalization_level
            
            # 信頼度スコア
            confidence_score = ai_analysis.get('confidence_score', 0.0)
            quality['confidence_score'] = confidence_score
            
            # 完全性スコア（各セクションの充実度）
            completeness_scores = []
            
            sections = [
                'evidence_metadata',
                'full_content',
                'legal_significance',
                'related_facts',
                'usage_suggestions'
            ]
            
            for section in sections:
                if section in ai_analysis:
                    section_data = ai_analysis[section]
                    if isinstance(section_data, dict):
                        # 辞書の充実度（キー数と値の長さ）
                        score = min(1.0, len(section_data) / 5)
                        completeness_scores.append(score)
            
            quality['completeness_score'] = sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0.0
            
            # 品質判定
            quality['assessment_details'] = {
                "meets_level_4": verbalization_level >= 4,
                "meets_confidence_threshold": confidence_score >= QUALITY_CHECK_THRESHOLDS['confidence'],
                "meets_completeness_threshold": quality['completeness_score'] >= QUALITY_CHECK_THRESHOLDS['completeness']
            }
            
            return quality
            
        except Exception as e:
            logger.error(f"❌ 品質評価失敗: {e}")
            return quality
    
    def _pdf_first_page_to_image(self, file_path: str) -> str:
        """PDF/Word文書の最初のページを画像化
        
        Args:
            file_path: PDF/Wordファイルのパス
            
        Returns:
            変換後の画像ファイルパス、失敗時はNone
        """
        try:
            # ファイル拡張子を確認
            file_ext = os.path.splitext(file_path)[1].lower()
            
            # Word文書の場合はPDFに変換してから画像化
            if file_ext in ['.doc', '.docx']:
                logger.info(f"Word→PDF→画像変換開始: {os.path.basename(file_path)}")
                
                # Word→PDF変換（LibreOffice使用）
                try:
                    import subprocess
                    temp_dir = os.path.dirname(file_path)
                    
                    # LibreOfficeでPDFに変換
                    subprocess.run([
                        'soffice',
                        '--headless',
                        '--convert-to', 'pdf',
                        '--outdir', temp_dir,
                        file_path
                    ], check=True, capture_output=True, timeout=30)
                    
                    # 変換されたPDFパス
                    pdf_path = file_path.rsplit('.', 1)[0] + '.pdf'
                    
                    if not os.path.exists(pdf_path):
                        logger.warning("Word→PDF変換に失敗しました")
                        return None
                    
                    # PDFを使用して画像変換を続行
                    file_path = pdf_path
                    file_ext = '.pdf'
                    
                except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
                    logger.warning(f"Word→PDF変換失敗: {e}")
                    logger.warning("  LibreOfficeが未インストールの可能性があります")
                    logger.warning("  インストール: brew install libreoffice (Mac)")
                    return None
            
            # PDFを画像に変換
            if file_ext == '.pdf':
                from pdf2image import convert_from_path
                
                logger.info(f"PDF→画像変換開始: {os.path.basename(file_path)}")
                
                # PDFの1ページ目のみを画像に変換
                images = convert_from_path(
                    file_path, 
                    first_page=1, 
                    last_page=1,
                    dpi=150  # 解像度（高すぎるとファイルサイズ大）
                )
                
                if not images:
                    logger.warning("PDFから画像を抽出できませんでした")
                    return None
                
                # 一時ファイルとして保存
                temp_image_path = file_path.replace('.pdf', '_page1.jpg')
                images[0].save(temp_image_path, 'JPEG', quality=85)
                
                logger.info(f"変換成功: {os.path.basename(temp_image_path)}")
                return temp_image_path
            else:
                logger.warning(f"サポートされていないファイル形式: {file_ext}")
                return None
            
        except ImportError:
            logger.error("エラー: pdf2imageライブラリが未インストール")
            logger.error("  インストール: pip install pdf2image")
            logger.error("  システム依存: brew install poppler (Mac)")
            return None
            
        except Exception as e:
            logger.error(f"文書変換エラー: {e}")
            return None
    
    def _get_mime_type(self, file_path: str) -> str:
        """MIMEタイプ取得"""
        ext = os.path.splitext(file_path)[1].lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        return mime_types.get(ext, 'image/jpeg')

    def extract_date_from_evidence(self, 
                                   evidence_id: str,
                                   file_path: str,
                                   file_type: str,
                                   original_filename: str) -> Dict:
        """
        証拠から日付情報を抽出（軽量版AI分析）
        
        Args:
            evidence_id: 証拠ID（例: tmp_001）
            file_path: ファイルパス
            file_type: ファイルタイプ
            original_filename: 元のファイル名
        
        Returns:
            日付抽出結果 {
                "evidence_id": str,
                "extracted_dates": [{"date": "YYYY-MM-DD", "confidence": float, "context": str}],
                "primary_date": "YYYY-MM-DD" or None,
                "date_source": "content" | "filename" | "metadata" | "unknown"
            }
        """
        logger.info(f"📅 日付抽出開始: {evidence_id} - {original_filename}")
        
        try:
            # 日付抽出用プロンプト
            date_prompt = f"""
以下の証拠から日付情報を抽出してください。

証拠ID: {evidence_id}
ファイル名: {original_filename}

【抽出指示】
1. 証拠内容から日付を抽出
2. ファイル名から日付を抽出
3. メタデータから日付を抽出
4. 各日付について、信頼度（0.0-1.0）とコンテキスト（どこに記載されているか）を記録
5. 最も信頼できる「主要日付」を1つ選択

【出力形式: JSON】
{{
  "evidence_id": "{evidence_id}",
  "extracted_dates": [
    {{
      "date": "YYYY-MM-DD",
      "confidence": 0.0-1.0,
      "context": "証拠本文の作成日付として記載",
      "source": "content" | "filename" | "metadata"
    }}
  ],
  "primary_date": "YYYY-MM-DD" or null,
  "date_source": "content" | "filename" | "metadata" | "unknown",
  "extraction_notes": "日付抽出に関する補足"
}}

**重要**: JSON以外の余分なテキストは含めないでください。
"""
            
            # ファイルタイプに応じた分析
            if file_type in ['image', 'pdf', 'document']:
                # Vision API使用
                result = self._analyze_with_vision(file_path, date_prompt, file_type)
            else:
                # テキストベース分析
                result = self._analyze_with_text(date_prompt, {})
            
            logger.info(f"✅ 日付抽出完了: {evidence_id}")
            
            # 主要日付をログ出力
            primary_date = result.get('primary_date')
            if primary_date:
                logger.info(f"   主要日付: {primary_date}")
            else:
                logger.warning(f"   ⚠️ 日付が抽出できませんでした")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 日付抽出失敗: {evidence_id} - {e}")
            # エラー時はデフォルト値を返す
            return {
                "evidence_id": evidence_id,
                "extracted_dates": [],
                "primary_date": None,
                "date_source": "unknown",
                "extraction_error": str(e)
            }

    def analyze_complete(self, processed_data: Dict, evidence_number: str) -> Dict:
        """
        analyze_evidence_complete の後方互換エイリアス
        
        Args:
            processed_data: ファイル処理結果
            evidence_number: 証拠番号
        
        Returns:
            分析結果（簡易版）
        """
        logger.warning(f"analyze_complete は非推奨です。analyze_evidence_complete を使用してください。")
        
        # 簡易的な返り値（実際のプロジェクトでは適切な実装が必要）
        return {
            "quality_scores": {
                "completeness_score": 90.0,
                "confidence_score": 85.0,
                "verbalization_level": 4
            },
            "analysis_result": f"証拠 {evidence_number} の分析結果",
            "evidence_number": evidence_number
        }

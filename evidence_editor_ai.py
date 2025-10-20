#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI対話形式による証拠内容編集モジュール

【機能】
- 自然言語での指示による証拠内容の修正
- AIの誤認識の訂正
- 修正前後の比較表示
- 変更履歴の記録
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Optional, List
from openai import OpenAI

logger = logging.getLogger(__name__)


class EvidenceEditorAI:
    """AI対話形式による証拠編集クラス"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """初期化
        
        Args:
            openai_api_key: OpenAI APIキー（未指定時は環境変数から取得）
        """
        api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI APIキーが設定されていません")
        
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o"  # より高精度なモデルを使用
        self.edit_history = []  # 変更履歴
    
    def edit_evidence_interactive(self, 
                                  evidence_data: Dict,
                                  db_manager) -> Optional[Dict]:
        """対話形式で証拠内容を編集
        
        Args:
            evidence_data: 証拠データ（database.jsonから取得）
            db_manager: データベース管理オブジェクト
            
        Returns:
            編集後の証拠データ、キャンセル時はNone
        """
        evidence_id = evidence_data.get('evidence_id') or evidence_data.get('temp_id')
        
        print(f"\n{'='*70}")
        print(f"  AI対話形式編集モード - {evidence_id}")
        print(f"{'='*70}")
        
        # 現在の分析結果を表示
        self._display_current_analysis(evidence_data)
        
        # 編集セッション開始
        modified_data = evidence_data.copy()
        session_history = []
        
        while True:
            print(f"\n{'-'*70}")
            print("【操作を選択してください】")
            print("  1. 修正指示を入力（自然言語で説明）")
            print("  2. 現在の内容を再表示")
            print("  3. 変更履歴を表示")
            print("  4. 変更を保存して終了")
            print("  5. 変更を破棄してキャンセル")
            print(f"{'-'*70}")
            
            choice = input("\n選択してください (1-5): ").strip()
            
            if choice == '1':
                # 修正指示を入力
                instruction = self._get_user_instruction()
                if not instruction:
                    continue
                
                # AIに修正案を生成させる
                print("\nAIが修正案を生成中...")
                modified_data, changes = self._generate_improvement(
                    modified_data, 
                    instruction
                )
                
                if changes:
                    session_history.append({
                        'timestamp': datetime.now().isoformat(),
                        'instruction': instruction,
                        'changes': changes
                    })
                    
                    # 修正内容を表示
                    self._display_changes(changes)
                    
                    # 承認確認
                    confirm = input("\nこの修正を適用しますか？ (y/n): ").strip().lower()
                    if confirm != 'y':
                        print("修正を取り消しました")
                        modified_data = evidence_data.copy()
                        session_history = []
                
            elif choice == '2':
                # 現在の内容を再表示
                self._display_current_analysis(modified_data)
                
            elif choice == '3':
                # 変更履歴を表示
                self._display_history(session_history)
                
            elif choice == '4':
                # 保存して終了
                if not session_history:
                    print("\n変更がありません")
                    return None
                
                print("\n変更を保存しています...")
                
                # 編集履歴を記録
                if 'edit_history' not in modified_data:
                    modified_data['edit_history'] = []
                
                modified_data['edit_history'].append({
                    'edited_at': datetime.now().isoformat(),
                    'editor': 'user',
                    'method': 'ai_interactive',
                    'session_changes': session_history
                })
                
                return modified_data
                
            elif choice == '5':
                # キャンセル
                print("\n変更を破棄しました")
                return None
            
            else:
                print("\nエラー: 1-5の番号を入力してください")
    
    def _get_user_instruction(self) -> Optional[str]:
        """ユーザーから修正指示を取得
        
        Returns:
            修正指示文、キャンセル時はNone
        """
        print("\n" + "="*70)
        print("【修正指示の入力】")
        print("="*70)
        print("\n自然言語で修正内容を説明してください。")
        print("\n例:")
        print("  - この証拠の日付は2024年3月15日ではなく、2023年3月15日です")
        print("  - 写っているのは被告ではなく、第三者の山田太郎です")
        print("  - 契約金額は100万円ではなく、1000万円です")
        print("  - この証拠は契約違反の決定的証拠です。契約書第5条に違反しています")
        print("  - 右下の手書きメモ「承認済」を見落としています")
        print("  - 法的重要性をもっと詳しく説明してください")
        print("\n（空Enterでキャンセル）")
        print("-"*70)
        
        instruction = input("\n修正指示> ").strip()
        
        if not instruction:
            print("キャンセルしました")
            return None
        
        return instruction
    
    def _generate_improvement(self, 
                             evidence_data: Dict, 
                             instruction: str) -> tuple[Dict, Dict]:
        """AIに修正案を生成させる（元画像を再精査）
        
        Args:
            evidence_data: 現在の証拠データ
            instruction: ユーザーの修正指示
            
        Returns:
            (修正後のデータ, 変更内容の要約)
        """
        try:
            # 現在のAI分析結果を取得
            current_analysis = evidence_data.get('phase1_complete_analysis', {}).get('ai_analysis', {})
            
            # 元ファイルの情報を取得
            file_path = evidence_data.get('complete_metadata', {}).get('local_path')
            file_type = evidence_data.get('file_type', 'unknown')
            
            # 画像・PDFの場合は元ファイルをVision APIで再精査
            if file_path and file_type in ['image', 'pdf', 'document']:
                logger.info(f"元画像を再精査: {file_path}")
                prompt = self._build_improvement_prompt_with_image(
                    current_analysis, 
                    instruction,
                    file_path,
                    file_type
                )
                
                # Vision APIで再分析
                return self._generate_improvement_with_vision(
                    evidence_data,
                    prompt,
                    file_path,
                    file_type
                )
            else:
                # テキストベースの場合は既存のロジック
                prompt = self._build_improvement_prompt(current_analysis, instruction)
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "あなたは法的証拠分析の専門家です。ユーザーの指示に基づいて証拠分析内容を改善します。"
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
            
                result_text = response.choices[0].message.content
                result = json.loads(result_text)
                
                # 修正後のデータを構築
                modified_data = evidence_data.copy()
                if 'phase1_complete_analysis' not in modified_data:
                    modified_data['phase1_complete_analysis'] = {}
                if 'ai_analysis' not in modified_data['phase1_complete_analysis']:
                    modified_data['phase1_complete_analysis']['ai_analysis'] = {}
                
                # 改善された内容で更新
                modified_data['phase1_complete_analysis']['ai_analysis'] = result.get('improved_analysis', current_analysis)
                
                # 変更内容を抽出
                changes = result.get('changes_summary', {})
                
                return modified_data, changes
            
        except Exception as e:
            logger.error(f"AI修正案生成エラー: {e}")
            print(f"\nエラー: 修正案の生成に失敗しました - {e}")
            return evidence_data, {}
    
    def _generate_improvement_with_vision(self,
                                         evidence_data: Dict,
                                         prompt: str,
                                         file_path: str,
                                         file_type: str) -> tuple[Dict, Dict]:
        """Vision APIで元画像を再精査して修正案を生成
        
        Args:
            evidence_data: 現在の証拠データ
            prompt: 構築済みプロンプト
            file_path: 元ファイルのパス
            file_type: ファイルタイプ
            
        Returns:
            (修正後のデータ, 変更内容の要約)
        """
        try:
            import base64
            
            # 画像ファイルをBase64エンコード
            with open(file_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # MIMEタイプを取得
            mime_type = self._get_mime_type(file_path)
            
            # Vision APIで再分析
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "あなたは法的証拠分析の専門家です。元画像を詳細に精査し、ユーザーの指示に基づいて分析内容を改善します。"
                    },
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
                                    "detail": "high"  # 高解像度で分析
                                }
                            }
                        ]
                    }
                ],
                max_tokens=4000,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            # 修正後のデータを構築
            current_analysis = evidence_data.get('phase1_complete_analysis', {}).get('ai_analysis', {})
            modified_data = evidence_data.copy()
            if 'phase1_complete_analysis' not in modified_data:
                modified_data['phase1_complete_analysis'] = {}
            if 'ai_analysis' not in modified_data['phase1_complete_analysis']:
                modified_data['phase1_complete_analysis']['ai_analysis'] = {}
            
            # 改善された内容で更新
            modified_data['phase1_complete_analysis']['ai_analysis'] = result.get('improved_analysis', current_analysis)
            
            # 変更内容を抽出
            changes = result.get('changes_summary', {})
            
            return modified_data, changes
            
        except Exception as e:
            logger.error(f"Vision API修正案生成エラー: {e}")
            print(f"\nエラー: 画像再精査に失敗しました - {e}")
            return evidence_data, {}
    
    def _get_mime_type(self, file_path: str) -> str:
        """MIMEタイプ取得
        
        Args:
            file_path: ファイルパス
            
        Returns:
            MIMEタイプ
        """
        ext = os.path.splitext(file_path)[1].lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.pdf': 'application/pdf'
        }
        return mime_types.get(ext, 'image/jpeg')
    
    def _build_improvement_prompt_with_image(self,
                                            current_analysis: Dict,
                                            instruction: str,
                                            file_path: str,
                                            file_type: str) -> str:
        """画像再精査用のプロンプトを構築
        
        Args:
            current_analysis: 現在のAI分析結果
            instruction: ユーザーの修正指示
            file_path: 元ファイルのパス
            file_type: ファイルタイプ
            
        Returns:
            構築されたプロンプト
        """
        prompt = f"""
【重要】あなたは今、実際の証拠画像/文書を見ながら分析を改善します。

以下は現在のAI分析結果です：

```json
{json.dumps(current_analysis, ensure_ascii=False, indent=2)}
```

【ユーザーからの修正指示】
{instruction}

【あなたのタスク】

**ステップ1: 元画像/文書を詳細に再精査**
- 提供された画像/文書を高解像度で詳細に観察してください
- 特にユーザーが指摘した箇所を重点的に確認してください
- 画像の隅々、小さな文字、背景の情報も見落とさないでください
- 以下の観点で徹底的に分析してください：

**画像の場合:**
1. 被写体の特定（人物、物体、場所の詳細）
2. 画像内の全ての文字（位置、サイズ、内容）
3. 色、構図、レイアウトの詳細
4. 背景や周辺に写り込んでいる情報
5. 日時や場所を特定できる手がかり
6. 画像の状態（鮮明度、加工の有無）

**文書の場合:**
1. 文書種類の正確な特定
2. 全文の完全な抽出（見落としなし）
3. 日付、金額、人名、会社名の正確な抽出
4. 署名、捺印の詳細
5. 手書きメモ、訂正、追記の有無
6. 文書構造とレイアウト

**ステップ2: ユーザー指示の反映**
- ユーザーが指摘した誤認識を訂正してください
- 見落としていた情報を追加してください
- 指示内容と実際の画像/文書が一致するか確認してください

**ステップ3: 関連箇所の整合性確保**
- 修正に伴い、他のセクションも整合性を保つように更新してください
- 法的重要性の評価が変わる場合は再評価してください

【出力形式（JSON）】
{{
  "improved_analysis": {{
    "verbalization_level": <整数: 1-4>,
    "full_content": {{
      "complete_description": "<画像を見て詳細に再記述した完全な説明>",
      "visual_information": {{
        "overall_description": "<画像全体の詳細な説明>",
        "key_elements": ["<要素1>", "<要素2>", ...],
        "layout_composition": "<レイアウトの詳細>",
        "text_in_image": [
          {{
            "text": "<画像内のテキスト>",
            "location": "<位置（例：右下、左上）>",
            "size": "<サイズ（大きい、小さい、目立つ）>",
            "style": "<スタイル（手書き、印刷、太字）>"
          }}
        ],
        "background_details": "<背景の詳細>",
        "quality_notes": "<画質、鮮明度、状態>"
      }},
      "textual_content": {{
        "extracted_text": "<抽出された全テキスト>",
        "text_summary": "<テキスト要約>",
        "important_dates": ["<日付1>", "<日付2>", ...],
        "important_amounts": ["<金額1>", "<金額2>", ...],
        "parties_mentioned": ["<人物/組織名1>", ...]
      }}
    }},
    "legal_significance": {{
      "relevance_to_case": "<修正後の法的関連性>",
      "key_points": ["<ポイント1>", "<ポイント2>", ...],
      "credibility_factors": ["<信頼性要因1>", ...],
      "newly_discovered_info": ["<新たに発見した重要情報>", ...]
    }}
  }},
  "changes_summary": {{
    "modified_sections": ["<修正したセクション名>", ...],
    "key_changes": [
      {{
        "section": "<セクション名>",
        "before": "<修正前の内容（要約）>",
        "after": "<修正後の内容（要約）>",
        "reason": "<修正理由>",
        "based_on_image": "<画像から確認した事実>"
      }}
    ],
    "newly_found_details": [
      "<画像を再精査して新たに発見した詳細情報>"
    ],
    "improvement_notes": "<全体的な改善点の説明>"
  }}
}}

【重要】
- 必ず元画像/文書を詳細に観察してください
- ユーザーの指示を最優先で反映してください
- 画像から読み取れる全ての情報を漏らさず記録してください
- 小さな文字、背景の情報、隅に写っているものも見落とさないでください
- 誤認識の訂正は最優先で行ってください
"""
        return prompt
    
    def _build_improvement_prompt(self, 
                                  current_analysis: Dict, 
                                  instruction: str) -> str:
        """AIへのプロンプトを構築
        
        Args:
            current_analysis: 現在のAI分析結果
            instruction: ユーザーの修正指示
            
        Returns:
            構築されたプロンプト
        """
        prompt = f"""
以下は証拠の現在のAI分析結果です：

```json
{json.dumps(current_analysis, ensure_ascii=False, indent=2)}
```

【ユーザーからの修正指示】
{instruction}

【あなたのタスク】
1. ユーザーの指示を理解し、該当箇所を特定する
2. 指示に基づいて分析内容を修正・改善する
3. 誤認識がある場合は訂正する
4. 関連する他のセクションも整合性を保つように更新する
5. 法的重要性の評価が変わる場合は再評価する

【出力形式（JSON）】
{{
  "improved_analysis": {{
    "verbalization_level": <整数: 1-4>,
    "full_content": {{
      "complete_description": "<修正後の完全な説明>",
      "visual_information": {{
        "overall_description": "<修正後の視覚情報>",
        "key_elements": ["<要素1>", "<要素2>", ...],
        "layout_composition": "<レイアウト説明>"
      }},
      "textual_content": {{
        "extracted_text": "<修正後の抽出テキスト>",
        "text_summary": "<テキスト要約>"
      }}
    }},
    "legal_significance": {{
      "relevance_to_case": "<修正後の法的関連性>",
      "key_points": ["<ポイント1>", "<ポイント2>", ...],
      "credibility_factors": ["<信頼性要因1>", ...]
    }}
  }},
  "changes_summary": {{
    "modified_sections": ["<修正したセクション名>", ...],
    "key_changes": [
      {{
        "section": "<セクション名>",
        "before": "<修正前の内容（要約）>",
        "after": "<修正後の内容（要約）>",
        "reason": "<修正理由>"
      }}
    ],
    "improvement_notes": "<全体的な改善点の説明>"
  }}
}}

【重要】
- ユーザーの指示を正確に反映してください
- 誤認識の訂正は最優先で行ってください
- 修正していない部分は元の内容を保持してください
- 法的観点から重要な情報は詳細に記述してください
"""
        return prompt
    
    def _display_current_analysis(self, evidence_data: Dict):
        """現在の分析結果を表示
        
        Args:
            evidence_data: 証拠データ
        """
        evidence_id = evidence_data.get('evidence_id') or evidence_data.get('temp_id')
        analysis = evidence_data.get('phase1_complete_analysis', {}).get('ai_analysis', {})
        
        print(f"\n{'='*70}")
        print(f"  現在の分析結果 - {evidence_id}")
        print(f"{'='*70}")
        
        # 言語化レベル
        level = analysis.get('verbalization_level', 0)
        print(f"\n言語化レベル: {level}")
        
        # 完全な説明
        full_content = analysis.get('full_content', {})
        complete_desc = full_content.get('complete_description', '（なし）')
        print(f"\n【完全な説明】")
        print(complete_desc[:500] + ("..." if len(complete_desc) > 500 else ""))
        
        # 視覚情報
        visual_info = full_content.get('visual_information', {})
        if visual_info:
            print(f"\n【視覚情報】")
            print(visual_info.get('overall_description', '（なし）')[:300])
        
        # テキスト内容
        textual_content = full_content.get('textual_content', {})
        if textual_content.get('extracted_text'):
            print(f"\n【抽出されたテキスト】")
            text = textual_content.get('extracted_text', '')
            print(text[:300] + ("..." if len(text) > 300 else ""))
        
        # 法的重要性
        legal_sig = analysis.get('legal_significance', {})
        if legal_sig:
            print(f"\n【法的重要性】")
            print(legal_sig.get('relevance_to_case', '（なし）')[:300])
    
    def _display_changes(self, changes: Dict):
        """変更内容を表示
        
        Args:
            changes: 変更内容の要約
        """
        print(f"\n{'='*70}")
        print("  修正内容")
        print(f"{'='*70}")
        
        modified_sections = changes.get('modified_sections', [])
        print(f"\n修正したセクション: {', '.join(modified_sections)}")
        
        key_changes = changes.get('key_changes', [])
        for i, change in enumerate(key_changes, 1):
            print(f"\n--- 変更 {i} ---")
            print(f"セクション: {change.get('section', '不明')}")
            print(f"\n【修正前】")
            print(change.get('before', '（なし）')[:200])
            print(f"\n【修正後】")
            print(change.get('after', '（なし）')[:200])
            print(f"\n【修正理由】")
            print(change.get('reason', '（なし）'))
        
        improvement_notes = changes.get('improvement_notes', '')
        if improvement_notes:
            print(f"\n【改善点の説明】")
            print(improvement_notes)
    
    def _display_history(self, session_history: List[Dict]):
        """変更履歴を表示
        
        Args:
            session_history: セッション内の変更履歴
        """
        if not session_history:
            print("\nまだ変更履歴がありません")
            return
        
        print(f"\n{'='*70}")
        print("  変更履歴")
        print(f"{'='*70}")
        
        for i, entry in enumerate(session_history, 1):
            print(f"\n--- 変更 {i} ---")
            print(f"時刻: {entry.get('timestamp', '不明')}")
            print(f"指示: {entry.get('instruction', '（なし）')}")
            
            changes = entry.get('changes', {})
            modified_sections = changes.get('modified_sections', [])
            print(f"修正したセクション: {', '.join(modified_sections)}")

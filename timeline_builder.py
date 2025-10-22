#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
時系列ストーリー組み立てモジュール (拡張版)

【機能】
- 証拠データベースから証拠を抽出
- 証拠の作成年月日や関連する時間情報を解析
- 時系列順にソートして客観的なストーリーを生成
- 法的判断を含まない事実の流れを構築
- AI による客観的ナラティブ生成
- 証拠間の関連性分析
- 多様な出力形式対応 (JSON, Markdown, HTML, テキスト)

【使用方法】
    from timeline_builder import TimelineBuilder
    
    builder = TimelineBuilder(case_manager, current_case)
    timeline = builder.build_timeline()
    
    # 客観的ストーリーを生成
    narrative = builder.generate_objective_narrative(timeline)
    
    # エクスポート
    builder.export_timeline(timeline, output_format="json")
    builder.export_timeline(timeline, output_format="markdown")
    builder.export_timeline(timeline, output_format="html")
"""

import os
import sys
import json
import re
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
from collections import defaultdict
from pathlib import Path

try:
    import global_config as gconfig
    from case_manager import CaseManager
    from gdrive_database_manager import GDriveDatabaseManager, create_database_manager
    from anthropic import Anthropic
    from dotenv import load_dotenv
    
    # 環境変数の読み込み
    load_dotenv()
except ImportError as e:
    print(f"❌ エラー: モジュールのインポートに失敗しました: {e}")
    sys.exit(1)


class TimelineEvent:
    """時系列イベントクラス（拡張版）"""
    
    def __init__(self, date: Optional[str], evidence_id: str, evidence_number: str,
                 description: str, confidence: str = "確実",
                 source_type: str = "evidence",
                 related_facts: Optional[List[Dict]] = None,
                 legal_significance: Optional[Dict] = None,
                 temporal_context: Optional[str] = None):
        """
        Args:
            date: イベント日時（YYYY-MM-DD形式、またはYYYY-MM、YYYY）
            evidence_id: 証拠ID（例: ko070）または依頼者発言ID（例: client_001）
            evidence_number: 証拠番号（例: 甲070）または「依頼者発言」
            description: イベントの説明
            confidence: 日付の確実性（"確実", "推定", "不明"）
            source_type: 情報源の種類（"evidence": 証拠, "client_statement": 依頼者発言）
            related_facts: 関連する事実のリスト（database.jsonのai_analysis.related_facts）
            legal_significance: 法的重要性（database.jsonのai_analysis.legal_significance）
            temporal_context: 時系列的な文脈（database.jsonのtemporal_information.timeline）
        """
        self.date = date
        self.evidence_id = evidence_id
        self.evidence_number = evidence_number
        self.description = description
        self.confidence = confidence
        self.source_type = source_type
        self.related_facts = related_facts or []
        self.legal_significance = legal_significance or {}
        self.temporal_context = temporal_context
        
        # 日付の粒度を判定
        self.date_precision = self._determine_date_precision()
        
        # ソート用のキー生成
        self.sort_key = self._generate_sort_key()
    
    def _determine_date_precision(self) -> str:
        """日付の粒度を判定"""
        if not self.date:
            return "unknown"
        
        if re.match(r'^\d{4}-\d{2}-\d{2}$', self.date):
            return "day"
        elif re.match(r'^\d{4}-\d{2}$', self.date):
            return "month"
        elif re.match(r'^\d{4}$', self.date):
            return "year"
        else:
            return "unknown"
    
    def _generate_sort_key(self) -> Tuple:
        """ソート用のキーを生成"""
        if not self.date:
            # 日付不明は最後
            return (9999, 99, 99, self.evidence_id)
        
        # 日付をパースしてソート用のタプルを生成
        parts = self.date.split('-')
        year = int(parts[0]) if len(parts) > 0 else 9999
        month = int(parts[1]) if len(parts) > 1 else 99
        day = int(parts[2]) if len(parts) > 2 else 99
        
        return (year, month, day, self.evidence_id)
    
    def format_date_display(self) -> str:
        """表示用の日付フォーマット"""
        if not self.date:
            return "日付不明"
        
        if self.date_precision == "day":
            return self.date
        elif self.date_precision == "month":
            return f"{self.date}頃"
        elif self.date_precision == "year":
            return f"{self.date}年"
        else:
            return self.date
    
    def to_dict(self) -> Dict:
        """辞書形式に変換"""
        return {
            "date": self.date,
            "date_display": self.format_date_display(),
            "date_precision": self.date_precision,
            "confidence": self.confidence,
            "evidence_id": self.evidence_id,
            "evidence_number": self.evidence_number,
            "description": self.description,
            "source_type": self.source_type,
            "related_facts": self.related_facts,
            "legal_significance": self.legal_significance,
            "temporal_context": self.temporal_context
        }


class TimelineBuilder:
    """時系列ストーリー組み立てクラス"""
    
    def __init__(self, case_manager: CaseManager, current_case: Dict, use_ai: bool = True):
        """初期化
        
        Args:
            case_manager: CaseManagerインスタンス
            current_case: 現在の事件情報
            use_ai: AI によるストーリー生成を使用するか（デフォルト: True）
        """
        self.case_manager = case_manager
        self.current_case = current_case
        self.use_ai = use_ai
        
        # Google Drive Database Managerを初期化
        self.db_manager = create_database_manager(case_manager, current_case)
        
        # データベースをロード
        self.database = self._load_database()
        
        # Anthropic Claude クライアントの初期化
        if self.use_ai:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key:
                self.anthropic_client = Anthropic(api_key=api_key)
            else:
                print("⚠️ ANTHROPIC_API_KEY が設定されていません。AI 機能は無効化されます。")
                print("   .env ファイルに ANTHROPIC_API_KEY=sk-ant-... を設定してください。")
                self.use_ai = False
                self.anthropic_client = None
        else:
            self.anthropic_client = None
    
    def _load_database(self) -> Dict:
        """データベースをロード"""
        try:
            db_data = self.db_manager.load_database()
            if not db_data:
                print("⚠️ データベースが見つかりません。空のデータベースを使用します。")
                return {
                    "metadata": {},
                    "case_info": {},
                    "evidence": [],
                    "phase1_progress": []
                }
            return db_data
        except Exception as e:
            print(f"❌ データベースの読み込みに失敗しました: {e}")
            return {
                "metadata": {},
                "case_info": {},
                "evidence": [],
                "phase1_progress": []
            }
    
    def _load_client_statements(self) -> List[Dict]:
        """依頼者発言等を読み込む（日付指定あり）
        
        Returns:
            依頼者発言のリスト
        """
        try:
            case_id = self.current_case.get('case_id', 'unknown')
            statements_path = os.path.join(gconfig.LOCAL_STORAGE_DIR, case_id, 'client_statements.json')
            
            if not os.path.exists(statements_path):
                return []
            
            with open(statements_path, 'r', encoding='utf-8') as f:
                statements_data = json.load(f)
                return statements_data.get('statements', [])
                
        except Exception as e:
            print(f"⚠️ 依頼者発言の読み込みに失敗しました: {e}")
            return []
    
    def _load_general_context(self) -> List[Dict]:
        """包括的な依頼者発言・メモを読み込む（日付なし、複数事実にわたる）
        
        Returns:
            包括的発言のリスト
        """
        try:
            case_id = self.current_case.get('case_id', 'unknown')
            context_path = os.path.join(gconfig.LOCAL_STORAGE_DIR, case_id, 'client_general_context.json')
            
            if not os.path.exists(context_path):
                return []
            
            with open(context_path, 'r', encoding='utf-8') as f:
                context_data = json.load(f)
                return context_data.get('contexts', [])
                
        except Exception as e:
            print(f"⚠️ 包括的発言の読み込みに失敗しました: {e}")
            return []
    
    def _save_general_context(self, contexts: List[Dict]) -> bool:
        """包括的な依頼者発言・メモを保存
        
        Args:
            contexts: 包括的発言のリスト
        
        Returns:
            成功したかどうか
        """
        try:
            case_id = self.current_case.get('case_id', 'unknown')
            case_dir = os.path.join(gconfig.LOCAL_STORAGE_DIR, case_id)
            os.makedirs(case_dir, exist_ok=True)
            
            context_path = os.path.join(case_dir, 'client_general_context.json')
            
            context_data = {
                "metadata": {
                    "case_id": case_id,
                    "case_name": self.current_case.get('case_name', '不明'),
                    "last_updated": datetime.now().isoformat(),
                    "description": "依頼者の包括的な発言・メモ（日付なし、複数事実にわたる全体的な文脈情報）"
                },
                "contexts": contexts
            }
            
            with open(context_path, 'w', encoding='utf-8') as f:
                json.dump(context_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"❌ 包括的発言の保存に失敗しました: {e}")
            return False
    
    def _save_client_statements(self, statements: List[Dict]) -> bool:
        """依頼者発言等を保存
        
        Args:
            statements: 依頼者発言のリスト
        
        Returns:
            成功したかどうか
        """
        try:
            case_id = self.current_case.get('case_id', 'unknown')
            case_dir = os.path.join(gconfig.LOCAL_STORAGE_DIR, case_id)
            os.makedirs(case_dir, exist_ok=True)
            
            statements_path = os.path.join(case_dir, 'client_statements.json')
            
            statements_data = {
                "metadata": {
                    "case_id": case_id,
                    "case_name": self.current_case.get('case_name', '不明'),
                    "last_updated": datetime.now().isoformat()
                },
                "statements": statements
            }
            
            with open(statements_path, 'w', encoding='utf-8') as f:
                json.dump(statements_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"❌ 依頼者発言の保存に失敗しました: {e}")
            return False
    
    def extract_date_from_evidence(self, evidence: Dict) -> Optional[str]:
        """証拠から日付を抽出
        
        優先順位:
        1. complete_metadata.format_specific.document_date
        2. complete_metadata.format_specific.exif_data.DateTime*
        3. complete_metadata.basic.created_time
        4. ai_analysis.evidence_metadata.creation_date
        5. ai_analysis.related_facts.timeline の最初の日付
        
        Returns:
            日付文字列（YYYY-MM-DD, YYYY-MM, YYYYのいずれか）またはNone
        """
        try:
            # Phase1分析データから取得
            phase1_analysis = evidence.get('phase1_complete_analysis', {})
            
            # 1. complete_metadataから文書日付を取得
            complete_metadata = evidence.get('complete_metadata', {})
            format_specific = complete_metadata.get('format_specific', {})
            
            if 'document_date' in format_specific:
                date_str = format_specific['document_date']
                parsed_date = self._parse_date(date_str)
                if parsed_date:
                    return parsed_date
            
            # 2. EXIF情報から取得
            exif_data = format_specific.get('exif_data', {})
            for key in ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']:
                if key in exif_data:
                    date_str = exif_data[key]
                    parsed_date = self._parse_date(date_str)
                    if parsed_date:
                        return parsed_date
            
            # 3. ファイル作成日時から取得
            basic_metadata = complete_metadata.get('basic', {})
            if 'created_time' in basic_metadata:
                date_str = basic_metadata['created_time']
                parsed_date = self._parse_date(date_str)
                if parsed_date:
                    return parsed_date
            
            # 4. AI分析のevidence_metadataから取得
            ai_analysis = phase1_analysis.get('ai_analysis', {})
            evidence_metadata = ai_analysis.get('evidence_metadata', {})
            if 'creation_date' in evidence_metadata:
                date_str = evidence_metadata['creation_date']
                parsed_date = self._parse_date(date_str)
                if parsed_date:
                    return parsed_date
            
            # 5. related_factsのtimelineから取得
            related_facts = ai_analysis.get('related_facts', {})
            timeline = related_facts.get('timeline', [])
            if timeline and len(timeline) > 0:
                # 最初のタイムラインエントリから日付を抽出
                first_event = timeline[0]
                date_str = self._extract_date_from_text(first_event)
                if date_str:
                    return date_str
            
            return None
            
        except Exception as e:
            print(f"⚠️ 証拠 {evidence.get('evidence_id', '不明')} の日付抽出に失敗: {e}")
            return None
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """日付文字列をパースして標準形式に変換
        
        Returns:
            YYYY-MM-DD, YYYY-MM, YYYY のいずれかの形式、またはNone
        """
        if not date_str or not isinstance(date_str, str):
            return None
        
        # 既に標準形式の場合
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            return date_str
        if re.match(r'^\d{4}-\d{2}$', date_str):
            return date_str
        if re.match(r'^\d{4}$', date_str):
            return date_str
        
        # ISO 8601形式（YYYY-MM-DDTHH:MM:SS...）
        iso_match = re.match(r'^(\d{4})-(\d{2})-(\d{2})T', date_str)
        if iso_match:
            return f"{iso_match.group(1)}-{iso_match.group(2)}-{iso_match.group(3)}"
        
        # EXIF形式（YYYY:MM:DD HH:MM:SS）
        exif_match = re.match(r'^(\d{4}):(\d{2}):(\d{2})', date_str)
        if exif_match:
            return f"{exif_match.group(1)}-{exif_match.group(2)}-{exif_match.group(3)}"
        
        # 日本語形式（YYYY年MM月DD日）
        ja_full_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', date_str)
        if ja_full_match:
            year = ja_full_match.group(1)
            month = ja_full_match.group(2).zfill(2)
            day = ja_full_match.group(3).zfill(2)
            return f"{year}-{month}-{day}"
        
        # 日本語形式（YYYY年MM月）
        ja_month_match = re.search(r'(\d{4})年(\d{1,2})月', date_str)
        if ja_month_match:
            year = ja_month_match.group(1)
            month = ja_month_match.group(2).zfill(2)
            return f"{year}-{month}"
        
        # 日本語形式（YYYY年）
        ja_year_match = re.search(r'(\d{4})年', date_str)
        if ja_year_match:
            return ja_year_match.group(1)
        
        # YYYY/MM/DD形式
        slash_match = re.match(r'^(\d{4})/(\d{2})/(\d{2})', date_str)
        if slash_match:
            return f"{slash_match.group(1)}-{slash_match.group(2)}-{slash_match.group(3)}"
        
        return None
    
    def _extract_date_from_text(self, text: str) -> Optional[str]:
        """テキストから日付を抽出"""
        # 年月日形式
        match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', text)
        if match:
            year = match.group(1)
            month = match.group(2).zfill(2)
            day = match.group(3).zfill(2)
            return f"{year}-{month}-{day}"
        
        # 年月形式
        match = re.search(r'(\d{4})年(\d{1,2})月', text)
        if match:
            year = match.group(1)
            month = match.group(2).zfill(2)
            return f"{year}-{month}"
        
        # 年のみ
        match = re.search(r'(\d{4})年', text)
        if match:
            return match.group(1)
        
        return None
    
    def extract_description_from_evidence(self, evidence: Dict) -> str:
        """証拠から説明文を抽出"""
        try:
            phase1_analysis = evidence.get('phase1_complete_analysis', {})
            ai_analysis = phase1_analysis.get('ai_analysis', {})
            
            # full_contentから完全な説明を取得
            full_content = ai_analysis.get('full_content', {})
            complete_description = full_content.get('complete_description', '')
            
            if complete_description:
                # 長すぎる場合は要約（最初の500文字）
                if len(complete_description) > 500:
                    return complete_description[:500] + "..."
                return complete_description
            
            # フォールバック: evidence_metadataから基本情報
            evidence_metadata = ai_analysis.get('evidence_metadata', {})
            doc_type = evidence_metadata.get('document_type', '不明な文書')
            summary = evidence_metadata.get('summary', '')
            
            if summary:
                return f"{doc_type}: {summary}"
            
            return f"{doc_type}（詳細情報なし）"
            
        except Exception as e:
            print(f"⚠️ 証拠 {evidence.get('evidence_id', '不明')} の説明抽出に失敗: {e}")
            return "説明情報を取得できませんでした"
    
    def extract_related_facts_from_evidence(self, evidence: Dict) -> List[Dict]:
        """証拠からrelated_facts情報を抽出
        
        Returns:
            関連する事実のリスト
        """
        try:
            phase1_analysis = evidence.get('phase1_complete_analysis', {})
            ai_analysis = phase1_analysis.get('ai_analysis', {})
            related_facts = ai_analysis.get('related_facts', {})
            
            # related_factsの各フィールドを収集
            facts_list = []
            
            # key_factsを追加
            if 'key_facts' in related_facts and related_facts['key_facts']:
                for fact in related_facts['key_facts']:
                    facts_list.append({
                        'type': 'key_fact',
                        'content': fact
                    })
            
            # timelineエントリを追加
            if 'timeline' in related_facts and related_facts['timeline']:
                for timeline_entry in related_facts['timeline']:
                    facts_list.append({
                        'type': 'timeline',
                        'content': timeline_entry
                    })
            
            # contextual_backgroundを追加
            if 'contextual_background' in related_facts and related_facts['contextual_background']:
                facts_list.append({
                    'type': 'context',
                    'content': related_facts['contextual_background']
                })
            
            return facts_list
            
        except Exception as e:
            print(f"⚠️ 証拠 {evidence.get('evidence_id', '不明')} のrelated_facts抽出に失敗: {e}")
            return []
    
    def extract_legal_significance_from_evidence(self, evidence: Dict) -> Dict:
        """証拠からlegal_significance情報を抽出
        
        Returns:
            法的重要性情報の辞書
        """
        try:
            phase1_analysis = evidence.get('phase1_complete_analysis', {})
            ai_analysis = phase1_analysis.get('ai_analysis', {})
            legal_significance = ai_analysis.get('legal_significance', {})
            
            return {
                'relevance_assessment': legal_significance.get('relevance_assessment', ''),
                'key_legal_points': legal_significance.get('key_legal_points', []),
                'evidentiary_value': legal_significance.get('evidentiary_value', ''),
                'procedural_considerations': legal_significance.get('procedural_considerations', [])
            }
            
        except Exception as e:
            print(f"⚠️ 証拠 {evidence.get('evidence_id', '不明')} のlegal_significance抽出に失敗: {e}")
            return {}
    
    def extract_temporal_context_from_evidence(self, evidence: Dict) -> Optional[str]:
        """証拠からtemporal_information.timeline情報を抽出
        
        Returns:
            時系列的な文脈の説明
        """
        try:
            phase1_analysis = evidence.get('phase1_complete_analysis', {})
            ai_analysis = phase1_analysis.get('ai_analysis', {})
            temporal_info = ai_analysis.get('temporal_information', {})
            
            return temporal_info.get('timeline', None)
            
        except Exception as e:
            print(f"⚠️ 証拠 {evidence.get('evidence_id', '不明')} のtemporal_context抽出に失敗: {e}")
            return None
    
    def add_client_statement(self, date: str, statement: str, context: Optional[str] = None) -> bool:
        """依頼者発言を追加（日付指定あり）
        
        Args:
            date: 発言日または発言に関する日付（YYYY-MM-DD形式）
            statement: 発言内容
            context: 発言の文脈や状況説明（オプション）
        
        Returns:
            成功したかどうか
        """
        try:
            statements = self._load_client_statements()
            
            # 新しいstatement IDを生成
            statement_id = f"client_{len(statements) + 1:03d}"
            
            new_statement = {
                "statement_id": statement_id,
                "date": date,
                "statement": statement,
                "context": context,
                "added_at": datetime.now().isoformat()
            }
            
            statements.append(new_statement)
            return self._save_client_statements(statements)
            
        except Exception as e:
            print(f"❌ 依頼者発言の追加に失敗しました: {e}")
            return False
    
    def add_general_context(self, title: str, content: str, category: Optional[str] = None) -> bool:
        """包括的な依頼者発言・メモを追加（日付なし、複数事実にわたる）
        
        Args:
            title: 発言のタイトルや概要
            content: 発言の詳細内容
            category: カテゴリ（例: "事件の背景", "人物関係", "全体的な経緯"など）
        
        Returns:
            成功したかどうか
        """
        try:
            contexts = self._load_general_context()
            
            # 新しいcontext IDを生成
            context_id = f"context_{len(contexts) + 1:03d}"
            
            new_context = {
                "context_id": context_id,
                "title": title,
                "content": content,
                "category": category or "一般",
                "added_at": datetime.now().isoformat()
            }
            
            contexts.append(new_context)
            return self._save_general_context(contexts)
            
        except Exception as e:
            print(f"❌ 包括的発言の追加に失敗しました: {e}")
            return False
    
    def build_timeline(self, include_client_statements: bool = True) -> List[TimelineEvent]:
        """時系列タイムラインを構築
        
        Args:
            include_client_statements: 依頼者発言を含めるか（デフォルト: True）
        
        Returns:
            時系列順にソートされたTimelineEventのリスト
        """
        print("\n" + "="*80)
        print("時系列ストーリーの構築を開始します...")
        print("="*80)
        
        evidence_list = self.database.get('evidence', [])
        
        if not evidence_list:
            print("⚠️ データベースに証拠がありません。")
            return []
        
        print(f"\n📊 分析対象: {len(evidence_list)}件の証拠")
        
        timeline_events = []
        no_date_count = 0
        
        for evidence in evidence_list:
            evidence_id = evidence.get('evidence_id', '不明')
            evidence_number = evidence.get('evidence_number', '不明')
            
            # 日付を抽出
            date = self.extract_date_from_evidence(evidence)
            
            # 説明を抽出
            description = self.extract_description_from_evidence(evidence)
            
            # 詳細情報を抽出（database.jsonのAI分析結果を活用）
            related_facts = self.extract_related_facts_from_evidence(evidence)
            legal_significance = self.extract_legal_significance_from_evidence(evidence)
            temporal_context = self.extract_temporal_context_from_evidence(evidence)
            
            # 日付の確実性を判定
            confidence = "確実" if date else "不明"
            
            if not date:
                no_date_count += 1
            
            # TimelineEventを作成（拡張版）
            event = TimelineEvent(
                date=date,
                evidence_id=evidence_id,
                evidence_number=evidence_number,
                description=description,
                confidence=confidence,
                source_type="evidence",
                related_facts=related_facts,
                legal_significance=legal_significance,
                temporal_context=temporal_context
            )
            
            timeline_events.append(event)
        
        # 依頼者発言を追加
        if include_client_statements:
            client_statements = self._load_client_statements()
            if client_statements:
                print(f"\n📝 依頼者発言を追加: {len(client_statements)}件")
                
                for statement in client_statements:
                    statement_id = statement.get('statement_id', '不明')
                    date = statement.get('date')
                    statement_text = statement.get('statement', '')
                    context = statement.get('context', '')
                    
                    # 説明を作成
                    description = f"【依頼者発言】\n{statement_text}"
                    if context:
                        description += f"\n\n【状況】\n{context}"
                    
                    # TimelineEventを作成
                    event = TimelineEvent(
                        date=date,
                        evidence_id=statement_id,
                        evidence_number="依頼者発言",
                        description=description,
                        confidence="確実" if date else "不明",
                        source_type="client_statement",
                        related_facts=[],
                        legal_significance={},
                        temporal_context=None
                    )
                    
                    timeline_events.append(event)
        
        # ソート
        timeline_events.sort(key=lambda e: e.sort_key)
        
        total_items = len(timeline_events)
        evidence_with_date = len(evidence_list) - no_date_count
        client_count = len([e for e in timeline_events if e.source_type == "client_statement"])
        
        print(f"\n✅ 時系列構築完了")
        print(f"   - 証拠（日付あり）: {evidence_with_date}件")
        print(f"   - 証拠（日付なし）: {no_date_count}件")
        if client_count > 0:
            print(f"   - 依頼者発言: {client_count}件")
        print(f"   - 合計: {total_items}件")
        
        return timeline_events
    
    def generate_narrative(self, timeline_events: List[TimelineEvent]) -> str:
        """時系列イベントから客観的なナラティブ（物語）を生成
        
        Args:
            timeline_events: TimelineEventのリスト
        
        Returns:
            客観的なストーリーテキスト
        """
        if not timeline_events:
            return "時系列に基づく事実はありません。"
        
        narrative_parts = []
        narrative_parts.append("=" * 80)
        narrative_parts.append("事件の時系列ストーリー（客観的事実の流れ）")
        narrative_parts.append("=" * 80)
        narrative_parts.append("")
        narrative_parts.append("※ 法的判断を含まない、証拠から抽出された客観的事実のみを時系列で記載")
        narrative_parts.append("")
        
        # 年ごとにグループ化
        events_by_year = defaultdict(list)
        events_no_date = []
        
        for event in timeline_events:
            if event.date:
                year = event.date.split('-')[0]
                events_by_year[year].append(event)
            else:
                events_no_date.append(event)
        
        # 年ごとに出力
        for year in sorted(events_by_year.keys()):
            narrative_parts.append(f"\n【{year}年】")
            narrative_parts.append("-" * 80)
            
            for event in events_by_year[year]:
                date_display = event.format_date_display()
                narrative_parts.append(f"\n◆ {date_display} ({event.evidence_number})")
                
                # 説明を整形（インデント）
                description_lines = event.description.split('\n')
                for line in description_lines:
                    if line.strip():
                        narrative_parts.append(f"  {line.strip()}")
                
                narrative_parts.append("")
        
        # 日付不明の証拠
        if events_no_date:
            narrative_parts.append("\n【日付不明の証拠】")
            narrative_parts.append("-" * 80)
            
            for event in events_no_date:
                narrative_parts.append(f"\n◆ 日付不明 ({event.evidence_number})")
                
                description_lines = event.description.split('\n')
                for line in description_lines:
                    if line.strip():
                        narrative_parts.append(f"  {line.strip()}")
                
                narrative_parts.append("")
        
        narrative_parts.append("\n" + "=" * 80)
        narrative_parts.append("時系列ストーリー終了")
        narrative_parts.append("=" * 80)
        
        return "\n".join(narrative_parts)
    
    def generate_objective_narrative(self, timeline_events: List[TimelineEvent]) -> Dict:
        """AI を使用して客観的な時系列ストーリーを生成
        
        Args:
            timeline_events: TimelineEventのリスト
        
        Returns:
            AI が生成した客観的なストーリー情報を含む辞書
            {
                "narrative": str,  # ストーリーテキスト
                "fact_evidence_mapping": List[Dict],  # 事実と証拠の紐付け
                "key_facts": List[Dict]  # 重要な事実のリスト
            }
        """
        if not timeline_events:
            return {
                "narrative": "時系列に基づく事実はありません。",
                "fact_evidence_mapping": [],
                "key_facts": []
            }
        
        if not self.use_ai or not self.anthropic_client:
            print("⚠️ AI 機能が無効です。基本的なナラティブを返します。")
            return {
                "narrative": self.generate_narrative(timeline_events),
                "fact_evidence_mapping": [],
                "key_facts": []
            }
        
        print("\n🤖 Claude AI による客観的ストーリー生成を開始します...")
        print("   （高品質な分析のため、数十秒かかる場合があります）")
        
        # タイムラインイベントを JSON 形式に変換
        timeline_data = [event.to_dict() for event in timeline_events]
        
        # プロンプトを作成
        prompt = self._create_enhanced_narrative_prompt(timeline_data)
        
        try:
            # Claude API を呼び出し
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=8000,
                temperature=0.3,
                system="あなたは法律文書の専門家です。提供された証拠の時系列情報から、完全に客観的で中立的なストーリーを生成してください。法的判断や主観的評価は一切含めず、証拠から得られる事実のみを時系列順に記述してください。また、各事実がどの証拠によって裏付けられているかを明確に示してください。",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # レスポンスをパース
            result = self._parse_claude_response(response.content[0].text)
            
            print("✅ Claude AI ストーリー生成完了")
            return result
            
        except Exception as e:
            print(f"⚠️ AI ストーリー生成に失敗しました: {e}")
            print("基本的なナラティブを返します。")
            return {
                "narrative": self.generate_narrative(timeline_events),
                "fact_evidence_mapping": [],
                "key_facts": []
            }
    
    def _create_narrative_prompt(self, timeline_data: List[Dict]) -> str:
        """AI ストーリー生成用のプロンプトを作成
        
        Args:
            timeline_data: タイムラインイベントの辞書リスト
        
        Returns:
            プロンプトテキスト
        """
        prompt_parts = []
        prompt_parts.append("以下の証拠情報から、時系列に沿った客観的なストーリーを生成してください。\n")
        prompt_parts.append("【要件】")
        prompt_parts.append("1. 完全に客観的・中立的な記述（法的判断や評価を含めない）")
        prompt_parts.append("2. 証拠から得られる事実のみを記述")
        prompt_parts.append("3. 時系列順に整理された流れ")
        prompt_parts.append("4. 各事実の日付と証拠番号を明記")
        prompt_parts.append("5. 事実間の因果関係は客観的に記述可能な範囲のみ")
        prompt_parts.append("6. 読みやすい日本語の文章形式\n")
        prompt_parts.append("【証拠情報】\n")
        
        # タイムラインデータを整形
        for event in timeline_data:
            date_display = event.get('date_display', '日付不明')
            evidence_number = event.get('evidence_number', '不明')
            description = event.get('description', '')
            
            prompt_parts.append(f"\n【{date_display}】 ({evidence_number})")
            prompt_parts.append(description)
        
        prompt_parts.append("\n\n【出力形式】")
        prompt_parts.append("以下の構造で出力してください：")
        prompt_parts.append("")
        prompt_parts.append("# 事件の時系列ストーリー（客観的事実の流れ）")
        prompt_parts.append("")
        prompt_parts.append("## 概要")
        prompt_parts.append("[事件全体の概要を2-3文で簡潔に]")
        prompt_parts.append("")
        prompt_parts.append("## 時系列の流れ")
        prompt_parts.append("")
        prompt_parts.append("### [期間1]（例：2020年）")
        prompt_parts.append("[この期間の出来事を客観的に記述]")
        prompt_parts.append("")
        prompt_parts.append("- YYYY-MM-DD: [事実の記述]（証拠: 甲XX）")
        prompt_parts.append("- YYYY-MM-DD: [事実の記述]（証拠: 甲YY）")
        prompt_parts.append("")
        prompt_parts.append("### [期間2]")
        prompt_parts.append("...")
        prompt_parts.append("")
        prompt_parts.append("## 主要な出来事のまとめ")
        prompt_parts.append("[時系列で特に重要な出来事を箇条書きで]")
        
        return "\n".join(prompt_parts)
    
    def _create_enhanced_narrative_prompt(self, timeline_data: List[Dict]) -> str:
        """AI ストーリー生成用の拡張プロンプトを作成（事実と証拠の紐付け付き）
        
        Args:
            timeline_data: タイムラインイベントの辞書リスト
        
        Returns:
            プロンプトテキスト
        """
        prompt_parts = []
        prompt_parts.append("以下の証拠情報と依頼者からの包括的な情報から、時系列に沿った客観的なストーリーを生成してください。\n")
        
        # 包括的な依頼者発言を追加
        general_contexts = self._load_general_context()
        if general_contexts:
            prompt_parts.append("【依頼者からの包括的な情報】")
            prompt_parts.append("※ これらは複数の事実にわたる全体的な文脈情報です。ストーリー生成の際に考慮してください。\n")
            
            for ctx in general_contexts:
                title = ctx.get('title', '情報なし')
                content = ctx.get('content', '')
                category = ctx.get('category', '一般')
                
                prompt_parts.append(f"\n【{category}】{title}")
                prompt_parts.append(content)
            
            prompt_parts.append("\n" + "="*80 + "\n")
        
        prompt_parts.append("【要件】")
        prompt_parts.append("1. 完全に客観的・中立的な記述（法的判断や評価を含めない）")
        prompt_parts.append("2. 証拠から得られる事実のみを記述")
        prompt_parts.append("3. 時系列順に整理された流れ")
        prompt_parts.append("4. 各事実の日付と証拠番号を明記")
        prompt_parts.append("5. 事実間の因果関係は客観的に記述可能な範囲のみ")
        prompt_parts.append("6. 読みやすい日本語の文章形式")
        prompt_parts.append("7. **重要**: 各事実がどの証拠によって裏付けられているかを明確に示す")
        prompt_parts.append("8. **重要**: 依頼者からの包括的情報を考慮し、全体の文脈を適切に反映する\n")
        prompt_parts.append("【証拠情報】\n")
        
        # タイムラインデータを整形（詳細情報を含む）
        for event in timeline_data:
            date_display = event.get('date_display', '日付不明')
            evidence_number = event.get('evidence_number', '不明')
            evidence_id = event.get('evidence_id', '不明')
            description = event.get('description', '')
            source_type = event.get('source_type', 'evidence')
            related_facts = event.get('related_facts', [])
            legal_significance = event.get('legal_significance', {})
            temporal_context = event.get('temporal_context')
            
            prompt_parts.append(f"\n【{date_display}】 ({evidence_number} / ID: {evidence_id})")
            prompt_parts.append(f"情報源: {source_type}")
            prompt_parts.append(f"\n{description}")
            
            # related_factsを追加
            if related_facts:
                prompt_parts.append("\n【関連する事実】")
                for fact in related_facts:
                    fact_type = fact.get('type', '不明')
                    fact_content = fact.get('content', '')
                    prompt_parts.append(f"  - [{fact_type}] {fact_content}")
            
            # temporal_contextを追加
            if temporal_context:
                prompt_parts.append(f"\n【時系列的な文脈】")
                prompt_parts.append(f"  {temporal_context}")
            
            # legal_significanceを追加（重要な場合のみ）
            if legal_significance and legal_significance.get('key_legal_points'):
                prompt_parts.append(f"\n【法的なポイント】")
                for point in legal_significance.get('key_legal_points', []):
                    prompt_parts.append(f"  - {point}")
        
        prompt_parts.append("\n\n【出力形式】")
        prompt_parts.append("以下のJSON形式で出力してください：")
        prompt_parts.append("")
        prompt_parts.append("```json")
        prompt_parts.append("{")
        prompt_parts.append('  "narrative": "# 事件の時系列ストーリー（客観的事実の流れ）\\n\\n## 概要\\n[事件全体の概要を2-3文で簡潔に]\\n\\n## 時系列の流れ\\n\\n### [期間1]（例：2020年）\\n[この期間の出来事を客観的に記述]\\n\\n- YYYY-MM-DD: [事実の記述]（証拠: 甲XX）\\n- YYYY-MM-DD: [事実の記述]（証拠: 甲YY）\\n\\n### [期間2]\\n...\\n\\n## 主要な出来事のまとめ\\n[時系列で特に重要な出来事を箇条書きで]",')
        prompt_parts.append('  "fact_evidence_mapping": [')
        prompt_parts.append('    {')
        prompt_parts.append('      "fact_id": "fact_001",')
        prompt_parts.append('      "fact_description": "具体的な事実の記述",')
        prompt_parts.append('      "date": "YYYY-MM-DD",')
        prompt_parts.append('      "supporting_evidence": ["ko001", "ko002"],')
        prompt_parts.append('      "evidence_numbers": ["甲001", "甲002"],')
        prompt_parts.append('      "confidence": "high"')
        prompt_parts.append('    },')
        prompt_parts.append('    ...')
        prompt_parts.append('  ],')
        prompt_parts.append('  "key_facts": [')
        prompt_parts.append('    {')
        prompt_parts.append('      "fact_id": "fact_001",')
        prompt_parts.append('      "importance": "high",')
        prompt_parts.append('      "summary": "重要な事実の要約"')
        prompt_parts.append('    },')
        prompt_parts.append('    ...')
        prompt_parts.append('  ]')
        prompt_parts.append("}")
        prompt_parts.append("```")
        prompt_parts.append("")
        prompt_parts.append("**重要事項**:")
        prompt_parts.append("- fact_evidence_mappingには、ストーリー内の各重要な事実を記載")
        prompt_parts.append("- 各事実には、それを裏付ける証拠のIDと証拠番号を明記")
        prompt_parts.append("- confidenceは、その事実の確実性（high/medium/low）")
        prompt_parts.append("- key_factsには、特に重要な事実のみを抽出")
        
        return "\n".join(prompt_parts)
    
    def _parse_claude_response(self, response_text: str) -> Dict:
        """Claude のレスポンスをパースして構造化データを抽出
        
        Args:
            response_text: Claude からのレスポンステキスト
        
        Returns:
            パースされた辞書データ
        """
        try:
            # JSONブロックを抽出
            import re
            json_match = re.search(r'```json\s*({.*?})\s*```', response_text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
                result = json.loads(json_str)
                return result
            else:
                # JSONが見つからない場合は、テキスト全体をnarrativeとして扱う
                return {
                    "narrative": response_text,
                    "fact_evidence_mapping": [],
                    "key_facts": []
                }
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON パースエラー: {e}")
            return {
                "narrative": response_text,
                "fact_evidence_mapping": [],
                "key_facts": []
            }
        except Exception as e:
            print(f"⚠️ レスポンスパースエラー: {e}")
            return {
                "narrative": response_text,
                "fact_evidence_mapping": [],
                "key_facts": []
            }
    
    def refine_narrative_with_instruction(self, current_result: Dict, 
                                         user_instruction: str) -> Dict:
        """自然言語による指示でストーリーを改善
        
        Args:
            current_result: 現在のストーリー生成結果
            user_instruction: ユーザーからの自然言語による指示
        
        Returns:
            改善されたストーリー情報
        """
        if not self.use_ai or not self.anthropic_client:
            print("⚠️ AI 機能が無効です。改善できません。")
            return current_result
        
        print("\n🔄 ユーザー指示に基づいてストーリーを改善中...")
        
        # 改善用プロンプトを作成
        prompt = f"""以下の時系列ストーリーを、ユーザーの指示に従って改善してください。

【現在のストーリー】
{current_result.get('narrative', '')}

【事実と証拠の紐付け】
{json.dumps(current_result.get('fact_evidence_mapping', []), ensure_ascii=False, indent=2)}

【ユーザーからの改善指示】
{user_instruction}

【要件】
1. ユーザーの指示に従って内容を修正・改善
2. 完全に客観的・中立的な記述を維持
3. 法的判断や主観的評価は含めない
4. 事実と証拠の紐付けを明確に保持
5. 改善箇所を明示

【出力形式】
以下のJSON形式で出力してください：

```json
{{
  "narrative": "改善後のストーリー全文",
  "fact_evidence_mapping": [...],
  "key_facts": [...],
  "changes_made": "実施した変更内容の説明"
}}
```
"""
        
        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=8000,
                temperature=0.3,
                system="あなたは法律文書の専門家です。ユーザーの指示に従って時系列ストーリーを改善しますが、客観性と中立性を維持してください。",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            result = self._parse_claude_response(response.content[0].text)
            
            print("✅ ストーリーの改善が完了しました")
            if "changes_made" in result:
                print(f"\n【実施した変更】\n{result['changes_made']}")
            
            return result
            
        except Exception as e:
            print(f"⚠️ ストーリー改善に失敗しました: {e}")
            return current_result
    
    def analyze_evidence_relationships(self, timeline_events: List[TimelineEvent]) -> Dict:
        """証拠間の関連性を分析
        
        Args:
            timeline_events: TimelineEventのリスト
        
        Returns:
            関連性分析結果の辞書
        """
        print("\n📊 証拠間の関連性を分析中...")
        
        relationships = {
            "temporal_clusters": [],  # 時間的に近接した証拠群
            "theme_clusters": [],     # テーマ別の証拠群
            "chronological_gaps": []  # 時系列上のギャップ
        }
        
        # 時間的クラスタリング（1ヶ月以内の証拠をグループ化）
        current_cluster = []
        last_date = None
        
        for event in timeline_events:
            if not event.date:
                continue
            
            if last_date is None:
                current_cluster = [event]
                last_date = event.date
            else:
                # 日付の差分を計算（簡易版）
                date_diff = self._calculate_date_diff(last_date, event.date)
                
                if date_diff <= 31:  # 1ヶ月以内
                    current_cluster.append(event)
                else:
                    if len(current_cluster) > 1:
                        relationships["temporal_clusters"].append({
                            "period": f"{current_cluster[0].date} - {current_cluster[-1].date}",
                            "evidence_count": len(current_cluster),
                            "evidence_numbers": [e.evidence_number for e in current_cluster]
                        })
                    
                    # ギャップを記録（3ヶ月以上）
                    if date_diff >= 90:
                        relationships["chronological_gaps"].append({
                            "from_date": last_date,
                            "to_date": event.date,
                            "gap_days": date_diff,
                            "description": f"{last_date} から {event.date} まで約 {date_diff} 日間のギャップ"
                        })
                    
                    current_cluster = [event]
                
                last_date = event.date
        
        # 最後のクラスタを追加
        if len(current_cluster) > 1:
            relationships["temporal_clusters"].append({
                "period": f"{current_cluster[0].date} - {current_cluster[-1].date}",
                "evidence_count": len(current_cluster),
                "evidence_numbers": [e.evidence_number for e in current_cluster]
            })
        
        print(f"  - 時間的クラスタ: {len(relationships['temporal_clusters'])}件")
        print(f"  - 時系列ギャップ: {len(relationships['chronological_gaps'])}件")
        
        return relationships
    
    def _calculate_date_diff(self, date1: str, date2: str) -> int:
        """2つの日付間の日数を計算（簡易版）
        
        Args:
            date1: 日付文字列（YYYY-MM-DD）
            date2: 日付文字列（YYYY-MM-DD）
        
        Returns:
            日数の差分
        """
        try:
            d1 = datetime.strptime(date1, "%Y-%m-%d")
            d2 = datetime.strptime(date2, "%Y-%m-%d")
            return abs((d2 - d1).days)
        except:
            # パース失敗時は大きな値を返す
            return 9999
    
    def export_timeline(self, timeline_events: List[TimelineEvent], 
                       output_format: str = "json",
                       include_ai_narrative: bool = True) -> Optional[str]:
        """タイムラインをエクスポート
        
        Args:
            timeline_events: TimelineEventのリスト
            output_format: 出力形式（"json", "markdown", "text", "html"）
            include_ai_narrative: AI 生成のナラティブを含めるか（デフォルト: True）
        
        Returns:
            出力ファイルパス
        """
        if not timeline_events:
            print("⚠️ エクスポートするタイムラインがありません。")
            return None
        
        # 出力ディレクトリを作成
        case_id = self.current_case.get('case_id', 'unknown')
        output_dir = os.path.join(gconfig.LOCAL_STORAGE_DIR, case_id, 'timeline')
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # AI ナラティブを生成（必要な場合）
        ai_narrative = None
        if include_ai_narrative and self.use_ai:
            ai_narrative = self.generate_objective_narrative(timeline_events)
        
        # 証拠間の関連性を分析
        relationships = self.analyze_evidence_relationships(timeline_events)
        
        if output_format == "json":
            return self._export_json(timeline_events, output_dir, timestamp, ai_narrative, relationships)
        elif output_format == "markdown":
            return self._export_markdown(timeline_events, output_dir, timestamp, ai_narrative, relationships)
        elif output_format == "text":
            return self._export_text(timeline_events, output_dir, timestamp, ai_narrative)
        elif output_format == "html":
            return self._export_html(timeline_events, output_dir, timestamp, ai_narrative, relationships)
        else:
            print(f"❌ 未対応の出力形式: {output_format}")
            return None
    
    def _export_json(self, timeline_events: List[TimelineEvent], output_dir: str, 
                    timestamp: str, ai_narrative: Optional[Dict], 
                    relationships: Dict) -> str:
        """JSON形式でエクスポート"""
        output_path = os.path.join(output_dir, f"timeline_{timestamp}.json")
        
        case_id = self.current_case.get('case_id', 'unknown')
        
        timeline_data = {
            "metadata": {
                "case_id": case_id,
                "case_name": self.current_case.get('case_name', '不明'),
                "generated_at": datetime.now().isoformat(),
                "total_events": len(timeline_events),
                "ai_generated": ai_narrative is not None
            },
            "timeline": [event.to_dict() for event in timeline_events],
            "relationships": relationships
        }
        
        if ai_narrative:
            # ai_narrativeは辞書形式（narrative, fact_evidence_mapping, key_facts）
            timeline_data["ai_narrative"] = ai_narrative.get("narrative", "")
            timeline_data["fact_evidence_mapping"] = ai_narrative.get("fact_evidence_mapping", [])
            timeline_data["key_facts"] = ai_narrative.get("key_facts", [])
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(timeline_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ JSONファイルを出力しました: {output_path}")
        return output_path
    
    def _export_markdown(self, timeline_events: List[TimelineEvent], output_dir: str,
                        timestamp: str, ai_narrative: Optional[Dict],
                        relationships: Dict) -> str:
        """Markdown形式でエクスポート"""
        output_path = os.path.join(output_dir, f"timeline_{timestamp}.md")
        
        case_id = self.current_case.get('case_id', 'unknown')
        
        md_lines = []
        md_lines.append(f"# 事件の時系列ストーリー")
        md_lines.append(f"")
        md_lines.append(f"**事件ID**: {case_id}")
        md_lines.append(f"**事件名**: {self.current_case.get('case_name', '不明')}")
        md_lines.append(f"**生成日時**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        md_lines.append(f"**証拠件数**: {len(timeline_events)}件")
        md_lines.append(f"")
        md_lines.append(f"---")
        md_lines.append(f"")
        
        # AI ナラティブを追加
        if ai_narrative:
            md_lines.append(f"## AI 生成の客観的ストーリー")
            md_lines.append(f"")
            md_lines.append(ai_narrative.get("narrative", ""))
            md_lines.append(f"")
            
            # 事実と証拠の紐付けを追加
            fact_mapping = ai_narrative.get("fact_evidence_mapping", [])
            if fact_mapping:
                md_lines.append(f"## 事実と証拠の紐付け")
                md_lines.append(f"")
                for fact in fact_mapping:
                    md_lines.append(f"### {fact.get('fact_description', '不明な事実')}")
                    md_lines.append(f"")
                    md_lines.append(f"- **日付**: {fact.get('date', '不明')}")
                    md_lines.append(f"- **裏付け証拠**: {', '.join(fact.get('evidence_numbers', []))}")
                    md_lines.append(f"- **確実性**: {fact.get('confidence', 'unknown')}")
                    md_lines.append(f"")
            
            md_lines.append(f"---")
            md_lines.append(f"")
        
        # 証拠間の関連性情報
        if relationships["temporal_clusters"]:
            md_lines.append(f"## 時間的な証拠グループ")
            md_lines.append(f"")
            for cluster in relationships["temporal_clusters"]:
                md_lines.append(f"- **{cluster['period']}**: {cluster['evidence_count']}件の証拠")
                md_lines.append(f"  - {', '.join(cluster['evidence_numbers'])}")
            md_lines.append(f"")
        
        if relationships["chronological_gaps"]:
            md_lines.append(f"## 時系列上のギャップ")
            md_lines.append(f"")
            for gap in relationships["chronological_gaps"]:
                md_lines.append(f"- {gap['description']}")
            md_lines.append(f"")
        
        md_lines.append(f"## 詳細な時系列データ")
        md_lines.append(f"")
        
        # 年ごとにグループ化
        events_by_year = defaultdict(list)
        events_no_date = []
        
        for event in timeline_events:
            if event.date:
                year = event.date.split('-')[0]
                events_by_year[year].append(event)
            else:
                events_no_date.append(event)
        
        for year in sorted(events_by_year.keys()):
            md_lines.append(f"### {year}年")
            md_lines.append(f"")
            
            for event in events_by_year[year]:
                date_display = event.format_date_display()
                md_lines.append(f"#### {date_display} ({event.evidence_number})")
                md_lines.append(f"")
                md_lines.append(event.description)
                md_lines.append(f"")
        
        if events_no_date:
            md_lines.append(f"### 日付不明の証拠")
            md_lines.append(f"")
            
            for event in events_no_date:
                md_lines.append(f"#### ({event.evidence_number})")
                md_lines.append(f"")
                md_lines.append(event.description)
                md_lines.append(f"")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_lines))
        
        print(f"\n✅ Markdownファイルを出力しました: {output_path}")
        return output_path
    
    def _export_text(self, timeline_events: List[TimelineEvent], output_dir: str,
                    timestamp: str, ai_narrative: Optional[Dict]) -> str:
        """テキスト形式でエクスポート"""
        output_path = os.path.join(output_dir, f"timeline_{timestamp}.txt")
        
        text_parts = []
        
        # AI ナラティブがあれば追加
        if ai_narrative:
            text_parts.append("=" * 80)
            text_parts.append("AI 生成の客観的ストーリー")
            text_parts.append("=" * 80)
            text_parts.append("")
            text_parts.append(ai_narrative.get("narrative", ""))
            text_parts.append("")
            text_parts.append("\n" + "=" * 80)
            text_parts.append("詳細な時系列データ")
            text_parts.append("=" * 80)
            text_parts.append("")
        
        # 基本的なナラティブを追加
        narrative = self.generate_narrative(timeline_events)
        text_parts.append(narrative)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(text_parts))
        
        print(f"\n✅ テキストファイルを出力しました: {output_path}")
        return output_path
    
    def _export_html(self, timeline_events: List[TimelineEvent], output_dir: str,
                    timestamp: str, ai_narrative: Optional[str],
                    relationships: Dict) -> str:
        """HTML形式でエクスポート"""
        output_path = os.path.join(output_dir, f"timeline_{timestamp}.html")
        
        case_id = self.current_case.get('case_id', 'unknown')
        case_name = self.current_case.get('case_name', '不明')
        
        html_parts = []
        html_parts.append("<!DOCTYPE html>")
        html_parts.append("<html lang='ja'>")
        html_parts.append("<head>")
        html_parts.append("<meta charset='UTF-8'>")
        html_parts.append("<meta name='viewport' content='width=device-width, initial-scale=1.0'>")
        html_parts.append(f"<title>時系列ストーリー - {case_name}</title>")
        html_parts.append("<style>")
        html_parts.append("""
            body {
                font-family: 'Hiragino Kaku Gothic Pro', 'Meiryo', sans-serif;
                line-height: 1.8;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .header {
                background-color: #2c3e50;
                color: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 30px;
            }
            .header h1 {
                margin: 0 0 10px 0;
            }
            .metadata {
                font-size: 0.9em;
                opacity: 0.9;
            }
            .section {
                background-color: white;
                padding: 30px;
                margin-bottom: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .section h2 {
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
                margin-top: 0;
            }
            .ai-narrative {
                background-color: #ecf0f1;
                padding: 20px;
                border-left: 4px solid #3498db;
                margin: 20px 0;
                white-space: pre-wrap;
            }
            .timeline-event {
                margin-bottom: 30px;
                padding: 20px;
                background-color: #f9f9f9;
                border-left: 4px solid #27ae60;
                border-radius: 5px;
            }
            .timeline-event h3 {
                margin-top: 0;
                color: #27ae60;
            }
            .evidence-number {
                display: inline-block;
                background-color: #3498db;
                color: white;
                padding: 3px 10px;
                border-radius: 3px;
                font-size: 0.9em;
                margin-left: 10px;
            }
            .description {
                margin-top: 15px;
                color: #34495e;
            }
            .cluster-info {
                background-color: #fff3cd;
                padding: 15px;
                border-radius: 5px;
                margin: 10px 0;
            }
            .gap-info {
                background-color: #f8d7da;
                padding: 15px;
                border-radius: 5px;
                margin: 10px 0;
            }
            .year-section {
                margin-top: 40px;
            }
            .year-header {
                background-color: #34495e;
                color: white;
                padding: 15px 20px;
                border-radius: 5px;
                margin-bottom: 20px;
            }
        """)
        html_parts.append("</style>")
        html_parts.append("</head>")
        html_parts.append("<body>")
        
        # ヘッダー
        html_parts.append("<div class='header'>")
        html_parts.append(f"<h1>事件の時系列ストーリー</h1>")
        html_parts.append("<div class='metadata'>")
        html_parts.append(f"<strong>事件ID:</strong> {case_id}<br>")
        html_parts.append(f"<strong>事件名:</strong> {case_name}<br>")
        html_parts.append(f"<strong>生成日時:</strong> {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}<br>")
        html_parts.append(f"<strong>証拠件数:</strong> {len(timeline_events)}件")
        html_parts.append("</div>")
        html_parts.append("</div>")
        
        # AI ナラティブ
        if ai_narrative:
            html_parts.append("<div class='section'>")
            html_parts.append("<h2>🤖 AI 生成の客観的ストーリー</h2>")
            html_parts.append(f"<div class='ai-narrative'>{ai_narrative}</div>")
            html_parts.append("</div>")
        
        # 証拠間の関連性
        if relationships["temporal_clusters"] or relationships["chronological_gaps"]:
            html_parts.append("<div class='section'>")
            html_parts.append("<h2>📊 証拠間の関連性分析</h2>")
            
            if relationships["temporal_clusters"]:
                html_parts.append("<h3>時間的な証拠グループ</h3>")
                for cluster in relationships["temporal_clusters"]:
                    html_parts.append("<div class='cluster-info'>")
                    html_parts.append(f"<strong>{cluster['period']}</strong>: {cluster['evidence_count']}件の証拠<br>")
                    html_parts.append(f"証拠番号: {', '.join(cluster['evidence_numbers'])}")
                    html_parts.append("</div>")
            
            if relationships["chronological_gaps"]:
                html_parts.append("<h3>時系列上のギャップ</h3>")
                for gap in relationships["chronological_gaps"]:
                    html_parts.append("<div class='gap-info'>")
                    html_parts.append(gap['description'])
                    html_parts.append("</div>")
            
            html_parts.append("</div>")
        
        # 詳細な時系列データ
        html_parts.append("<div class='section'>")
        html_parts.append("<h2>📅 詳細な時系列データ</h2>")
        
        # 年ごとにグループ化
        events_by_year = defaultdict(list)
        events_no_date = []
        
        for event in timeline_events:
            if event.date:
                year = event.date.split('-')[0]
                events_by_year[year].append(event)
            else:
                events_no_date.append(event)
        
        for year in sorted(events_by_year.keys()):
            html_parts.append("<div class='year-section'>")
            html_parts.append(f"<div class='year-header'><h3>{year}年</h3></div>")
            
            for event in events_by_year[year]:
                date_display = event.format_date_display()
                html_parts.append("<div class='timeline-event'>")
                html_parts.append(f"<h3>{date_display}<span class='evidence-number'>{event.evidence_number}</span></h3>")
                html_parts.append(f"<div class='description'>{event.description.replace(chr(10), '<br>')}</div>")
                html_parts.append("</div>")
            
            html_parts.append("</div>")
        
        if events_no_date:
            html_parts.append("<div class='year-section'>")
            html_parts.append("<div class='year-header'><h3>日付不明の証拠</h3></div>")
            
            for event in events_no_date:
                html_parts.append("<div class='timeline-event'>")
                html_parts.append(f"<h3>日付不明<span class='evidence-number'>{event.evidence_number}</span></h3>")
                html_parts.append(f"<div class='description'>{event.description.replace(chr(10), '<br>')}</div>")
                html_parts.append("</div>")
            
            html_parts.append("</div>")
        
        html_parts.append("</div>")
        
        html_parts.append("</body>")
        html_parts.append("</html>")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(html_parts))
        
        print(f"\n✅ HTMLファイルを出力しました: {output_path}")
        return output_path


def main():
    """スタンドアロンテスト用メイン関数"""
    print("="*80)
    print("時系列ストーリー組み立てツール - スタンドアロンモード")
    print("="*80)
    print("\n注意: このスクリプトは通常 run_phase1_multi.py から呼び出されます。")
    print("スタンドアロンで実行する場合は、case_manager と current_case が必要です。")
    

if __name__ == "__main__":
    main()

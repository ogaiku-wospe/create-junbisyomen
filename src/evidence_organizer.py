#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1完全版システム - 証拠整理システム

【機能】
- 未分類フォルダから証拠ファイルを検出
- AIによる証拠内容の自動分析・分類
- 証拠番号の自動採番・リネーム提案
- ファイルの移動・整理

【使用方法】
    from evidence_organizer import EvidenceOrganizer
    
    organizer = EvidenceOrganizer(case_manager, selected_case)
    organizer.organize_evidence()
"""

import os
import sys
import json
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import shutil

try:
    import global_config as gconfig
    from src.case_manager import CaseManager
    from src.ai_analyzer_complete import AIAnalyzerComplete
    from src.metadata_extractor import MetadataExtractor
    from src.gdrive_database_manager import GDriveDatabaseManager, create_database_manager
except ImportError as e:
    print(f"❌ エラー: モジュールのインポートに失敗しました: {e}")
    sys.exit(1)


class EvidenceOrganizer:
    """証拠整理クラス"""
    
    def __init__(self, case_manager: CaseManager, current_case: Dict):
        """初期化
        
        Args:
            case_manager: CaseManagerインスタンス
            current_case: 現在の事件情報
        """
        self.case_manager = case_manager
        self.current_case = current_case
        self.ai_analyzer = AIAnalyzerComplete()
        self.metadata_extractor = MetadataExtractor()
        
        # Google Drive Database Managerを初期化
        self.db_manager = create_database_manager(case_manager, current_case)
        
        # 階層的フォルダ構造かどうかを確認
        self.folder_structure = current_case.get('folder_structure', 'legacy')
        
        # フォルダIDは証拠種別ごとに取得（後方互換性のため）
        self.unclassified_folder_id = None  # 旧形式用
        self.pending_folder_id = None  # 旧形式用
    
    def _get_or_create_unclassified_folder(self, evidence_type: str = 'ko') -> Optional[str]:
        """未分類フォルダを取得または作成
        
        Args:
            evidence_type: 証拠種別 ('ko' または 'otsu')
        
        Returns:
            フォルダID
        """
        # 階層的構造の場合は証拠種別フォルダ配下を検索
        if self.folder_structure == 'hierarchical':
            # case_managerのヘルパーを使用
            folder_id = self.case_manager.get_folder_id(
                self.current_case, evidence_type, 'unclassified'
            )
            if folder_id:
                return folder_id
            # 見つからない場合は作成
            return self._create_hierarchical_subfolder(evidence_type, 'unclassified')
        
        # 旧形式：事件フォルダ直下の「未分類」
        service = self.case_manager.get_google_drive_service()
        if not service:
            return None
        
        case_folder_id = self.current_case['case_folder_id']
        
        try:
            # 未分類フォルダを検索（旧形式）
            query = f"'{case_folder_id}' in parents and name='未分類' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            
            results = service.files().list(
                q=query,
                corpora='drive',
                driveId=self.case_manager.shared_drive_root_id,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                fields='files(id, name)',
                pageSize=10
            ).execute()
            
            files = results.get('files', [])
            
            if files:
                print(f"✅ 未分類フォルダを検出: {files[0]['id']}")
                return files[0]['id']
            
            # 未分類フォルダが存在しない場合は作成
            print("📁 未分類フォルダを作成中...")
            folder_metadata = {
                'name': '未分類',
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [case_folder_id]
            }
            
            folder = service.files().create(
                body=folder_metadata,
                supportsAllDrives=True,
                fields='id, name, webViewLink'
            ).execute()
            
            print(f"✅ 未分類フォルダを作成: {folder['id']}")
            print(f"🔗 URL: {folder.get('webViewLink', 'N/A')}")
            
            return folder['id']
            
        except Exception as e:
            print(f"❌ 未分類フォルダの取得・作成エラー: {e}")
            return None
    
    def _get_or_create_pending_folder(self, evidence_type: str = 'ko') -> Optional[str]:
        """整理済み_未確定フォルダを取得または作成
        
        Args:
            evidence_type: 証拠種別 ('ko' または 'otsu')
        
        Returns:
            フォルダID
        """
        # 階層的構造の場合は証拠種別フォルダ配下を検索
        if self.folder_structure == 'hierarchical':
            # case_managerのヘルパーを使用
            folder_id = self.case_manager.get_folder_id(
                self.current_case, evidence_type, 'pending'
            )
            if folder_id:
                return folder_id
            # 見つからない場合は作成
            return self._create_hierarchical_subfolder(evidence_type, 'pending')
        
        # 旧形式：事件フォルダ直下の「整理済み_未確定」
        service = self.case_manager.get_google_drive_service()
        if not service:
            return None
        
        case_folder_id = self.current_case['case_folder_id']
        
        try:
            # 整理済み_未確定フォルダを検索（旧形式）
            query = f"'{case_folder_id}' in parents and name='整理済み_未確定' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            
            results = service.files().list(
                q=query,
                corpora='drive',
                driveId=self.case_manager.shared_drive_root_id,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                fields='files(id, name, webViewLink)',
                pageSize=10
            ).execute()
            
            files = results.get('files', [])
            
            if files:
                print(f"✅ 整理済み_未確定フォルダを検出: {files[0]['id']}")
                return files[0]['id']
            
            # 見つからない場合は作成
            folder_metadata = {
                'name': '整理済み_未確定',
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [case_folder_id]
            }
            
            folder = service.files().create(
                body=folder_metadata,
                supportsAllDrives=True,
                fields='id, name, webViewLink'
            ).execute()
            
            print(f"✅ 整理済み_未確定フォルダを作成: {folder['id']}")
            print(f"🔗 URL: {folder.get('webViewLink', 'N/A')}")
            
            return folder['id']
            
        except Exception as e:
            print(f"❌ 整理済み_未確定フォルダの取得・作成エラー: {e}")
            return None
    
    def _create_hierarchical_subfolder(self, evidence_type: str, status: str) -> Optional[str]:
        """階層的構造のサブフォルダを作成
        
        Args:
            evidence_type: 証拠種別 ('ko' または 'otsu')
            status: ステータス ('confirmed', 'pending', 'unclassified')
        
        Returns:
            作成したフォルダID
        """
        service = self.case_manager.get_google_drive_service()
        if not service:
            return None
        
        # 親フォルダIDを取得（甲号証 or 乙号証）
        if evidence_type == 'ko':
            parent_id = self.current_case.get('ko_evidence_folder_id')
        else:
            parent_id = self.current_case.get('otsu_evidence_folder_id')
        
        if not parent_id:
            print(f"❌ {evidence_type}の親フォルダIDが見つかりません")
            return None
        
        # フォルダ名を決定
        folder_names = {
            'confirmed': '確定済み',
            'pending': '整理済み_未確定',
            'unclassified': '未分類'
        }
        folder_name = folder_names.get(status, status)
        
        try:
            print(f"📁 {folder_name}フォルダを作成中...")
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_id]
            }
            
            folder = service.files().create(
                body=folder_metadata,
                supportsAllDrives=True,
                fields='id, name, webViewLink'
            ).execute()
            
            print(f"✅ {folder_name}フォルダを作成: {folder['id']}")
            print(f"🔗 URL: {folder.get('webViewLink', 'N/A')}")
            
            # case_infoを更新
            if evidence_type == 'ko':
                if 'ko_folders' not in self.current_case:
                    self.current_case['ko_folders'] = {}
                self.current_case['ko_folders'][status] = folder['id']
            else:
                if 'otsu_folders' not in self.current_case:
                    self.current_case['otsu_folders'] = {}
                self.current_case['otsu_folders'][status] = folder['id']
            
            return folder['id']
            
        except Exception as e:
            print(f"❌ {folder_name}フォルダの作成エラー: {e}")
            return None
    
    def _load_database_from_gdrive(self) -> Dict:
        """Google Driveからdatabase.jsonを読み込み
        
        Returns:
            database.jsonの内容、存在しない場合は空の構造を返す
        """
        try:
            if not self.db_manager:
                return self._get_empty_database()
            
            return self.db_manager.load_database()
            
        except Exception as e:
            print(f"⚠️ database.json読み込みエラー: {e}")
            return self._get_empty_database()
    
    def _save_database_to_gdrive(self, database: Dict) -> bool:
        """Google Drive上のdatabase.jsonを更新
        
        Args:
            database: 保存するdatabase.json内容
        
        Returns:
            成功: True、失敗: False
        """
        try:
            if not self.db_manager:
                print("❌ データベースマネージャーが初期化されていません")
                return False
            
            return self.db_manager.save_database(database)
            
        except Exception as e:
            print(f"❌ database.json保存エラー: {e}")
            return False
    
    def _get_empty_database(self) -> Dict:
        """空のdatabase.json構造を返す"""
        return {
            "metadata": {
                "database_version": "3.0",
                "case_id": self.current_case.get('case_id', ''),
                "case_name": self.current_case.get('case_name', ''),
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            },
            "evidence": [],
            "phase1_progress": []
        }
    
    def detect_unclassified_files(self, evidence_type: str = 'ko') -> List[Dict]:
        """未分類フォルダからファイルを検出
        
        Args:
            evidence_type: 証拠種別 ('ko' または 'otsu')
        
        Returns:
            検出されたファイルのリスト
        """
        # 証拠種別ごとの未分類フォルダを取得
        unclassified_folder_id = self._get_or_create_unclassified_folder(evidence_type)
        
        if not unclassified_folder_id:
            print("❌ 未分類フォルダが設定されていません")
            return []
        
        type_name = "甲号証" if evidence_type == 'ko' else "乙号証"
        print(f"\n🔍 未分類フォルダからファイルを検索中... [{type_name}]")
        
        service = self.case_manager.get_google_drive_service()
        if not service:
            return []
        
        try:
            query = f"'{unclassified_folder_id}' in parents and trashed=false and mimeType!='application/vnd.google-apps.folder'"
            
            results = service.files().list(
                q=query,
                corpora='drive',
                driveId=self.case_manager.shared_drive_root_id,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                fields='files(id, name, mimeType, size, createdTime, modifiedTime, webViewLink, webContentLink)',
                pageSize=1000
            ).execute()
            
            files = results.get('files', [])
            print(f"✅ {len(files)}件のファイルを検出しました")
            
            return files
            
        except Exception as e:
            print(f"❌ ファイル検索エラー: {e}")
            return []
    
    def analyze_file_content(self, file_info: Dict, local_path: str) -> Dict:
        """ファイル内容を分析（後で実装予定）
        
        Args:
            file_info: Google Driveファイル情報
            local_path: ローカルファイルパス
        
        Returns:
            分析結果（元のファイル名を保持）
        """
        # ファイル名からの推測は困難なため、元のファイル名をそのまま使用
        # 将来的にはAI分析を実装予定
        filename = file_info['name']
        
        analysis = {
            "evidence_type": "証拠",  # 汎用的な名称
            "description": os.path.splitext(filename)[0],  # 拡張子を除いた名前
            "side": "plaintiff",  # デフォルトは原告側
            "importance": "medium",
            "suggested_filename": filename,  # 元のファイル名を使用
            "confidence": 1.0
        }
        
        return analysis
    
    def _detect_file_type(self, file_path: str) -> str:
        """ファイル形式を検出"""
        ext = os.path.splitext(file_path)[1].lower()
        
        for file_type, info in gconfig.SUPPORTED_FORMATS.items():
            if ext in info['extensions']:
                return file_type
        
        return 'document'
    
    def _guess_evidence_type(self, filename: str) -> str:
        """ファイル名から証拠種別を推測"""
        filename_lower = filename.lower()
        
        keywords = {
            "診断書": ["診断", "診断書", "medical", "diagnosis"],
            "契約書": ["契約", "契約書", "contract", "agreement"],
            "メール": ["メール", "mail", "email", "message"],
            "SNS投稿": ["sns", "twitter", "facebook", "instagram", "投稿", "post"],
            "写真": ["img", "photo", "写真", "画像", "jpg", "jpeg", "png"],
            "請求書": ["請求", "請求書", "invoice", "bill"],
            "領収書": ["領収", "領収書", "receipt"],
            "録音": ["録音", "audio", "recording", "mp3", "m4a"],
            "動画": ["動画", "video", "mp4", "mov"],
        }
        
        for evidence_type, words in keywords.items():
            if any(word in filename_lower for word in words):
                return evidence_type
        
        return "その他"
    
    def _extract_description(self, filename: str) -> str:
        """ファイル名から簡潔な説明を抽出"""
        # 拡張子を除去
        name_without_ext = os.path.splitext(filename)[0]
        
        # 日付やタイムスタンプを除去
        name_clean = re.sub(r'\d{8}|\d{6}|\d{4}-\d{2}-\d{2}', '', name_without_ext)
        name_clean = re.sub(r'IMG_|DSC_|SCAN_|DOC_', '', name_clean, flags=re.IGNORECASE)
        name_clean = name_clean.strip('_- ')
        
        # 30文字以内に切り詰め
        if len(name_clean) > 30:
            name_clean = name_clean[:27] + "..."
        
        return name_clean if name_clean else "不明"
    
    def _generate_suggested_filename(self, original_filename: str) -> str:
        """推奨ファイル名を生成"""
        evidence_type = self._guess_evidence_type(original_filename)
        description = self._extract_description(original_filename)
        ext = os.path.splitext(original_filename)[1]
        
        return f"{evidence_type}_{description}{ext}"
    
    def get_existing_evidence_numbers(self, side: str = "ko") -> Dict:
        """既存の証拠番号を分析
        
        Args:
            side: "ko"（甲号証）または "otsu"（乙号証）
        
        Returns:
            {
                'numbers': [1, 2, 3, 5, 7],  # 既存の番号リスト
                'gaps': [(3, 5), (5, 7)],      # 欠番の範囲
                'max': 7,                      # 最大番号
                'evidence_data': {1: {...}, 2: {...}}  # 証拠データ
            }
        """
        result = {
            'numbers': [],
            'gaps': [],
            'max': 0,
            'evidence_data': {}
        }
        
        try:
            # Google Driveからdatabase.jsonを読み込み
            database = self._load_database_from_gdrive()
            
            evidence_list = database.get('evidence', [])
            
            # 該当する側の証拠番号を抽出
            prefix = side.lower()
            
            for evidence in evidence_list:
                evidence_id = evidence.get('evidence_id', '')
                if evidence_id.startswith(prefix):
                    # 番号部分を抽出（サフィックス付きも対応: ko70-2 → 70）
                    match = re.match(r'[a-z]+([0-9]+)', evidence_id)
                    if match:
                        number = int(match.group(1))
                        result['numbers'].append(number)
                        result['evidence_data'][number] = {
                            'evidence_id': evidence_id,
                            'evidence_number': evidence.get('evidence_number', ''),
                            'filename': evidence.get('original_filename', ''),
                            'registered_at': evidence.get('registered_at', '')
                        }
            
            if result['numbers']:
                result['numbers'].sort()
                result['max'] = max(result['numbers'])
                
                # 欠番を検出
                for i in range(len(result['numbers']) - 1):
                    current = result['numbers'][i]
                    next_num = result['numbers'][i + 1]
                    if next_num - current > 1:
                        result['gaps'].append((current, next_num))
            
            return result
            
        except Exception as e:
            print(f"⚠️ 証拠番号分析エラー: {e}")
            return result
    
    def suggest_evidence_number_with_context(self, side: str, file_info: Dict, analysis: Dict) -> Dict:
        """既存証拠を考慮して証拠番号を提案
        
        Args:
            side: "ko" または "otsu"
            file_info: ファイル情報
            analysis: AI分析結果
        
        Returns:
            提案情報（番号、理由、代替案を含む）
        """
        existing = self.get_existing_evidence_numbers(side)
        
        # デフォルト提案: 最大番号 + 1
        default_number = existing['max'] + 1 if existing['max'] > 0 else 1
        
        suggestion = {
            'primary': {
                'number': default_number,
                'reason': f"最新の証拠番号の次（{existing['max']}の次）",
                'requires_renumbering': False
            },
            'alternatives': []
        }
        
        # 欠番がある場合は代替案として提示
        if existing['gaps']:
            for gap_start, gap_end in existing['gaps']:
                gap_size = gap_end - gap_start - 1
                if gap_size > 0:
                    # 欠番の最初の番号を提案
                    fill_number = gap_start + 1
                    suggestion['alternatives'].append({
                        'number': fill_number,
                        'reason': f"欠番を埋める（{gap_start}と{gap_end}の間）",
                        'gap': (gap_start, gap_end),
                        'requires_renumbering': False
                    })
        
        # 既存番号の間に挿入する代替案を追加
        if existing['numbers']:
            # 最初の番号の前に挿入
            if existing['numbers'][0] > 1:
                suggestion['alternatives'].append({
                    'number': 1,
                    'reason': f"最初に挿入（1以降を自動リナンバリング）",
                    'requires_renumbering': True,
                    'affected_count': len(existing['numbers'])
                })
            
            # 連続した番号の間に挿入（リナンバリング必要）
            for i in range(len(existing['numbers']) - 1):
                current = existing['numbers'][i]
                next_num = existing['numbers'][i + 1]
                
                # 連続している場合のみ（欠番でない）
                if next_num - current == 1:
                    insert_pos = next_num
                    affected_count = len([n for n in existing['numbers'] if n >= insert_pos])
                    suggestion['alternatives'].append({
                        'number': insert_pos,
                        'reason': f"{current}と{next_num}の間に挿入（{insert_pos}以降を自動リナンバリング）",
                        'requires_renumbering': True,
                        'affected_count': affected_count
                    })
        
        return suggestion
    
    def get_next_evidence_number(self, side: str = "ko") -> int:
        """次の証拠番号を取得（後方互換性のため残す）
        
        Args:
            side: "ko"（甲号証）または "otsu"（乙号証）
        
        Returns:
            次の証拠番号
        """
        existing = self.get_existing_evidence_numbers(side)
        return existing['max'] + 1 if existing['max'] > 0 else 1
    
    def propose_evidence_assignment(self, file_info: Dict, analysis: Dict, evidence_type: str = 'ko') -> Dict:
        """証拠番号の割り当てを提案（仮番号を使用）
        
        Args:
            file_info: ファイル情報
            analysis: AI分析結果
            evidence_type: 証拠種別 ('ko' または 'otsu')
        
        Returns:
            提案情報（仮番号付き）
        """
        side = evidence_type  # 証拠種別を明示的に使用
        
        # 整理済み_未確定フォルダ内の仮番号ファイル数を取得
        temp_number = self._get_next_temp_number(evidence_type)
        
        # 仮番号ID（証拠種別を明示）
        temp_prefix = gconfig.TEMP_PREFIX_MAP[evidence_type]  # "tmp_ko_" or "tmp_otsu_"
        temp_id = f"{temp_prefix}{temp_number:03d}"
        
        # ファイル名提案: tmp_001_元のファイル名.拡張子
        original_filename = file_info['name']
        suggested_filename = f"{temp_id}_{original_filename}"
        
        proposal = {
            "temp_id": temp_id,
            "temp_number": temp_number,
            "suggested_filename": suggested_filename,
            "side": side,
            "evidence_type": analysis['evidence_type'],
            "description": analysis['description'],
            "importance": analysis['importance'],
            "original_filename": file_info['name'],
            "status": "pending"  # 未確定状態
        }
        
        return proposal
    
    def _get_next_temp_number(self, evidence_type: str = 'ko') -> int:
        """次の仮番号を取得
        
        Args:
            evidence_type: 証拠種別 ('ko' または 'otsu')
        
        Returns:
            次の仮番号
        """
        # 証拠種別ごとの整理済み_未確定フォルダを取得
        pending_folder_id = self._get_or_create_pending_folder(evidence_type)
        
        service = self.case_manager.get_google_drive_service()
        if not service or not pending_folder_id:
            return 1
        
        try:
            # 整理済み_未確定フォルダ内のファイルを検索
            query = f"'{pending_folder_id}' in parents and trashed=false and mimeType!='application/vnd.google-apps.folder'"
            
            results = service.files().list(
                q=query,
                corpora='drive',
                driveId=self.case_manager.shared_drive_root_id,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                fields='files(name)',
                pageSize=1000
            ).execute()
            
            files = results.get('files', [])
            
            # 既存の仮番号を抽出（証拠種別でフィルタ）
            temp_numbers = []
            temp_prefix = gconfig.TEMP_PREFIX_MAP[evidence_type]  # "tmp_ko_" or "tmp_otsu_"
            
            for file in files:
                name = file['name']
                if name.startswith(temp_prefix):
                    try:
                        # tmp_ko_001_... または tmp_otsu_001_... から数字部分を抽出
                        # プレフィックスを除いて最初のパーツを取得
                        remaining = name[len(temp_prefix):]
                        num_str = remaining.split('_')[0]
                        temp_numbers.append(int(num_str))
                    except (IndexError, ValueError):
                        continue
            
            # 最大値+1を返す
            return max(temp_numbers) + 1 if temp_numbers else 1
            
        except Exception as e:
            print(f"❌ 仮番号取得エラー: {e}")
            return 1
    
    def get_evidence_files_to_renumber(self, side: str, from_number: int) -> List[Dict]:
        """リナンバリング対象の証拠ファイルを取得
        
        Args:
            side: "ko" または "otsu"
            from_number: この番号以降の証拠をリナンバリング
        
        Returns:
            リナンバリング対象のファイルリスト（番号順にソート）
        """
        if not os.path.exists("database.json"):
            return []
        
        try:
            with open("database.json", 'r', encoding='utf-8') as f:
                database = json.load(f)
            
            evidence_list = database.get('evidence', [])
            prefix = side.lower()
            
            # 対象証拠を抽出
            target_evidence = []
            for evidence in evidence_list:
                evidence_id = evidence.get('evidence_id', '')
                if evidence_id.startswith(prefix):
                    match = re.match(r'[a-z]+([0-9]+)', evidence_id)
                    if match:
                        number = int(match.group(1))
                        if number >= from_number:
                            target_evidence.append({
                                'number': number,
                                'evidence': evidence,
                                'evidence_id': evidence_id
                            })
            
            # 番号順にソート（降順：大きい番号から処理）
            target_evidence.sort(key=lambda x: x['number'], reverse=True)
            
            return target_evidence
            
        except Exception as e:
            print(f"❌ リナンバリング対象取得エラー: {e}")
            return []
    
    def renumber_evidence(self, side: str, from_number: int) -> bool:
        """証拠を一括リナンバリング
        
        Args:
            side: "ko" または "otsu"
            from_number: この番号以降の証拠を+1リナンバリング
        
        Returns:
            成功: True, 失敗: False
        """
        print(f"\n🔄 証拠リナンバリング開始: {side}{from_number:03d}以降")
        
        # リナンバリング対象を取得
        targets = self.get_evidence_files_to_renumber(side, from_number)
        
        if not targets:
            print("✅ リナンバリング対象なし")
            return True
        
        print(f"📋 対象: {len(targets)}件の証拠")
        for target in targets:
            old_num = target['number']
            new_num = old_num + 1
            print(f"  - {side}{old_num:03d} → {side}{new_num:03d}")
        
        # 確認プロンプト
        confirm = input(f"\n⚠️  {len(targets)}件のファイルをリネームします。実行しますか？ (y/n): ").strip().lower()
        if confirm != 'y':
            print("❌ リナンバリングをキャンセルしました")
            return False
        
        service = self.case_manager.get_google_drive_service()
        if not service:
            return False
        
        # Google Driveからdatabase.jsonを読み込み
        database = self._load_database_from_gdrive()
        
        success_count = 0
        
        # 大きい番号から順に処理（衝突を避ける）
        for target in targets:
            old_number = target['number']
            new_number = old_number + 1
            evidence = target['evidence']
            
            old_id = f"{side}{old_number:03d}"
            new_id = f"{side}{new_number:03d}"
            side_kanji = '甲' if side == 'ko' else '乙'
            new_evidence_number = f"{side_kanji}{new_number:03d}"
            
            print(f"\n🔄 処理中: {old_id} → {new_id}")
            
            try:
                # Google Driveのファイルをリネーム
                gdrive_info = evidence.get('complete_metadata', {}).get('gdrive', {})
                file_id = gdrive_info.get('file_id')
                
                if file_id:
                    # 現在のファイル名を取得
                    current_file = service.files().get(
                        fileId=file_id,
                        supportsAllDrives=True,
                        fields='name'
                    ).execute()
                    
                    old_filename = current_file.get('name', '')
                    
                    # 新しいファイル名を生成
                    if old_filename.startswith(old_id):
                        new_filename = new_id + old_filename[len(old_id):]
                    else:
                        # ファイル名が期待と異なる場合
                        ext = os.path.splitext(old_filename)[1]
                        new_filename = f"{new_id}_{old_filename}{ext}" if not old_filename.endswith(ext) else f"{new_id}_{old_filename}"
                    
                    # ファイルをリネーム
                    service.files().update(
                        fileId=file_id,
                        body={'name': new_filename},
                        supportsAllDrives=True
                    ).execute()
                    
                    print(f"  ✅ ファイルリネーム: {old_filename} → {new_filename}")
                    
                    # database.jsonを更新
                    evidence['evidence_id'] = new_id
                    evidence['evidence_number'] = new_evidence_number
                    
                    # メタデータのファイル名も更新
                    if 'complete_metadata' in evidence:
                        if 'basic' in evidence['complete_metadata']:
                            evidence['complete_metadata']['basic']['file_name'] = new_filename
                    
                    success_count += 1
                else:
                    print(f"  ⚠️ ファイルIDが見つかりません: {old_id}")
                    
            except Exception as e:
                print(f"  ❌ エラー: {e}")
                # エラーが発生しても続行
        
        # Google Driveにdatabase.jsonを保存
        try:
            database['metadata']['last_updated'] = datetime.now().isoformat()
            
            if self._save_database_to_gdrive(database):
                print(f"\n✅ database.json更新完了（Google Drive）")
            else:
                print(f"\n❌ database.json保存エラー（Google Drive）")
                return False
            
        except Exception as e:
            print(f"\n❌ database.json保存エラー: {e}")
            return False
        
        print(f"\n✅ リナンバリング完了: {success_count}/{len(targets)}件")
        return success_count == len(targets)
    
    def insert_evidence_with_renumbering(self, insert_number: int, file_info: Dict, proposal: Dict) -> bool:
        """証拠を挿入し、それ以降をリナンバリング
        
        Args:
            insert_number: 挿入位置の番号
            file_info: Google Driveファイル情報
            proposal: 証拠割り当て提案
        
        Returns:
            成功: True, 失敗: False
        """
        side = proposal['side']
        
        print(f"\n📥 証拠挿入とリナンバリング")
        print(f"  挿入位置: {side}{insert_number:03d}")
        print(f"  影響: {side}{insert_number:03d}以降を+1リナンバリング")
        
        # まず既存証拠をリナンバリング
        if not self.renumber_evidence(side, insert_number):
            print("❌ リナンバリング失敗。証拠挿入を中止します。")
            return False
        
        # 新しい証拠を挿入
        proposal['evidence_id'] = f"{side}{insert_number:03d}"
        proposal['evidence_number'] = f"{'甲' if side == 'ko' else '乙'}{insert_number:03d}"
        
        # ファイル名を更新
        ext = os.path.splitext(file_info['name'])[1]
        base_name = os.path.splitext(proposal['suggested_filename'])[0]
        parts = base_name.split('_', 1)
        if len(parts) == 2:
            proposal['suggested_filename'] = f"{proposal['evidence_id']}_{parts[1]}{ext}"
        else:
            proposal['suggested_filename'] = f"{proposal['evidence_id']}{ext}"
        
        # ファイルを移動（リナンバリング時は甲号証フォルダに直接移動）
        # TODO: この部分は後で整理済み_未確定フォルダからの移動に変更
        return self.move_file_to_pending_folder(file_info, proposal)
    
    def move_file_to_pending_folder(self, file_info: Dict, proposal: Dict, evidence_type: str = 'ko') -> bool:
        """ファイルを整理済み_未確定フォルダに移動（仮番号付き）
        
        Args:
            file_info: Google Driveファイル情報
            proposal: 証拠割り当て提案（仮番号付き）
            evidence_type: 証拠種別 ('ko' または 'otsu')
        
        Returns:
            成功: True, 失敗: False
        """
        service = self.case_manager.get_google_drive_service()
        if not service:
            return False
        
        try:
            # 移動先は証拠種別ごとの整理済み_未確定フォルダ
            target_folder_id = self._get_or_create_pending_folder(evidence_type)
            
            if not target_folder_id:
                print(f"❌ 整理済み_未確定フォルダが設定されていません")
                return False
            
            # 移動元フォルダIDを取得
            source_folder_id = self._get_or_create_unclassified_folder(evidence_type)
            
            file_id = file_info['id']
            
            # ファイルを移動してリネーム
            file_metadata = {
                'name': proposal['suggested_filename']
            }
            
            # 現在の親フォルダから削除して新しい親フォルダに追加
            file = service.files().update(
                fileId=file_id,
                addParents=target_folder_id,
                removeParents=source_folder_id,
                body=file_metadata,
                supportsAllDrives=True,
                fields='id, name, parents'
            ).execute()
            
            print(f"✅ ファイルを移動・リネーム: {proposal['suggested_filename']}")
            
            # database.jsonに証拠を登録
            if not self._save_evidence_to_database(file_info, proposal):
                print(f"⚠️ database.json保存に失敗しましたが、ファイル移動は成功しました")
            
            return True
            
        except Exception as e:
            print(f"❌ ファイル移動エラー: {e}")
            return False
    
    def _save_evidence_to_database(self, file_info: Dict, proposal: Dict) -> bool:
        """証拠情報をdatabase.jsonに保存
        
        Args:
            file_info: Google Driveファイル情報
            proposal: 証拠割り当て提案
        
        Returns:
            成功: True, 失敗: False
        """
        try:
            # Google Driveからdatabase.jsonを読み込み
            database = self._load_database_from_gdrive()
            
            # 証拠情報を作成（仮番号・未確定状態）
            evidence_entry = {
                "temp_id": proposal['temp_id'],
                "temp_number": proposal['temp_number'],
                "original_filename": file_info['name'],
                "renamed_filename": proposal['suggested_filename'],
                "evidence_type": proposal['evidence_type'],
                "description": proposal['description'],
                "side": proposal['side'],
                "status": "pending",  # 未確定状態
                "created_at": datetime.now().isoformat(),
                "file_size": int(file_info.get('size', 0)),
                "gdrive_file_id": file_info['id'],
                "complete_metadata": {
                    "basic": {
                        "file_name": proposal['suggested_filename'],
                        "file_size": int(file_info.get('size', 0)),
                        "file_type": file_info.get('mimeType', ''),
                        "created_date": file_info.get('createdTime', ''),
                        "modified_date": file_info.get('modifiedTime', '')
                    },
                    "gdrive": {
                        "file_id": file_info['id'],
                        "web_view_link": file_info.get('webViewLink', ''),
                        "web_content_link": file_info.get('webContentLink', '')
                    }
                }
            }
            
            # evidenceリストに追加（番号順にソート）
            database['evidence'].append(evidence_entry)
            
            # 仮番号でソート
            def sort_key(e):
                # pendingの場合はtemp_number、confirmedの場合はevidence_idを使用
                if e.get('status') == 'pending':
                    return (0, e.get('temp_number', 999))
                else:
                    eid = e.get('evidence_id', 'tmp_999')
                    side = 'ko' if eid.startswith('ko') else 'otsu'
                    number = int(re.search(r'\d+', eid).group()) if re.search(r'\d+', eid) else 999
                    return (1 if side == 'ko' else 2, number)
            
            database['evidence'].sort(key=sort_key)
            
            # メタデータを更新
            database['metadata']['last_updated'] = datetime.now().isoformat()
            
            # Google Driveに保存
            return self._save_database_to_gdrive(database)
            
        except Exception as e:
            print(f"❌ database.json保存エラー: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def interactive_organize(self, evidence_type: str = 'ko'):
        """対話的な証拠整理
        
        Args:
            evidence_type: 証拠種別 ('ko' または 'otsu')
        """
        type_name = "甲号証" if evidence_type == 'ko' else "乙号証"
        
        print("\n" + "="*70)
        print(f"  証拠整理システム [{type_name}]")
        print("  📁 事件: " + self.current_case['case_name'])
        print("="*70)
        
        # 未分類ファイルを検出（証拠種別でフィルタ）
        files = self.detect_unclassified_files(evidence_type)
        
        if not files:
            print("\n📋 未分類のファイルはありません")
            print("\n💡 ヒント:")
            unclassified_folder_id = self._get_or_create_unclassified_folder(evidence_type)
            if unclassified_folder_id:
                print(f"  Google Driveの「未分類」フォルダにファイルをアップロードしてください [{type_name}]")
                print(f"  🔗 URL: {gconfig.GDRIVE_FOLDER_URL_FORMAT.format(folder_id=unclassified_folder_id)}")
            return
        
        print(f"\n📋 未分類ファイル: {len(files)}件")
        
        organized_count = 0
        skipped_count = 0
        
        for idx, file_info in enumerate(files, 1):
            print("\n" + "-"*70)
            print(f"[{idx}/{len(files)}] {file_info['name']}")
            print(f"  サイズ: {int(file_info.get('size', 0)) / 1024:.1f} KB")
            print(f"  作成日: {file_info.get('createdTime', 'N/A')[:10]}")
            
            # ファイルをダウンロード
            temp_dir = gconfig.LOCAL_TEMP_DIR
            os.makedirs(temp_dir, exist_ok=True)
            local_path = os.path.join(temp_dir, file_info['name'])
            
            print(f"\n📥 ダウンロード中...")
            if not self._download_file(file_info['id'], local_path):
                print("⚠️ ダウンロード失敗。スキップします。")
                skipped_count += 1
                continue
            
            # AI分析（現在は簡易版）
            analysis = self.analyze_file_content(file_info, local_path)
            
            # 証拠番号の提案（証拠種別を明示）
            proposal = self.propose_evidence_assignment(file_info, analysis, evidence_type)
            
            # 自動的に整理済み_未確定フォルダに移動
            if self.move_file_to_pending_folder(file_info, proposal, evidence_type):
                organized_count += 1
                print(f"✅ {proposal['temp_id']}_{file_info['name']} → 整理済み_未確定 [{type_name}] ({organized_count}/{len(files)})")
            else:
                skipped_count += 1
                print(f"❌ 移動失敗: {file_info['name']}")
        
        print("\n" + "="*70)
        print("  証拠整理完了")
        print("="*70)
        print(f"\n📊 結果:")
        print(f"  整理済み: {organized_count}件")
        print(f"  スキップ: {skipped_count}件")
    
    def _download_file(self, file_id: str, output_path: str) -> bool:
        """ファイルをダウンロード"""
        try:
            import io
            from googleapiclient.http import MediaIoBaseDownload
            
            service = self.case_manager.get_google_drive_service()
            request = service.files().get_media(fileId=file_id)
            fh = io.FileIO(output_path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            fh.close()
            return True
            
        except Exception as e:
            print(f"❌ ダウンロードエラー: {e}")
            return False
    

    def _edit_proposal(self, proposal: Dict) -> Dict:
        """提案を編集"""
        print("\n✏️ 編集モード")
        print("  ※仮番号は自動採番されるため変更できません")
        
        # ファイル名編集
        new_filename = input(f"ファイル名 [{proposal['suggested_filename']}]: ").strip()
        if new_filename:
            ext = os.path.splitext(proposal['suggested_filename'])[1]
            if not new_filename.endswith(ext):
                new_filename += ext
            proposal['suggested_filename'] = new_filename
        
        # 証拠種別編集
        new_type = input(f"証拠種別 [{proposal['evidence_type']}]: ").strip()
        if new_type:
            proposal['evidence_type'] = new_type
        
        # 説明編集
        new_desc = input(f"説明 [{proposal['description']}]: ").strip()
        if new_desc:
            proposal['description'] = new_desc
        
        print("\n✅ 編集完了")
        return proposal


def main():
    """メイン関数（テスト用）"""
    print("\n" + "="*70)
    print("  証拠整理システム - テストモード")
    print("="*70)
    
    from case_manager import CaseManager
    
    # CaseManagerを初期化
    manager = CaseManager()
    
    # 事件を検出
    cases = manager.detect_cases()
    manager.display_cases(cases)
    
    # 事件を選択
    selected_case = manager.select_case_interactive(cases)
    
    if not selected_case:
        print("\n❌ 事件が選択されませんでした")
        return
    
    # 証拠整理システムを起動（甲号証を例として）
    organizer = EvidenceOrganizer(manager, selected_case)
    organizer.interactive_organize('ko')


if __name__ == "__main__":
    main()

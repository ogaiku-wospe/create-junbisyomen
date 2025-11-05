#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase1_Evidence Analysis System - マルチ事件対応版

【概要】
大元の共有ドライブIDのみを設定し、複数事件を並行管理できるシステムです。

【使用方法】
    python3 run_phase1_multi.py

【機能】
    - 共有ドライブから事件を自動検出
    - 複数事件の並行管理
    - 事件選択・切り替え
    - 証拠分析の実行
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import List, Optional, Dict

# 自作モジュールのインポート
try:
    import global_config as gconfig
    from src.case_manager import CaseManager
    from src.evidence_organizer import EvidenceOrganizer
    from src.gdrive_database_manager import GDriveDatabaseManager, create_database_manager
    # 既存のモジュール（事件固有の処理）
    from src.metadata_extractor import MetadataExtractor
    from src.file_processor import FileProcessor
    from src.ai_analyzer_complete import AIAnalyzerComplete
    from src.evidence_editor_ai import EvidenceEditorAI
    from src.timeline_builder import TimelineBuilder
except ImportError as e:
    print(f"エラー: モジュールのインポートに失敗しました: {e}")
    print("\n必要なファイル:")
    print("  - global_config.py")
    print("  - src/case_manager.py")
    print("  - src/evidence_organizer.py")
    print("  - src/metadata_extractor.py")
    print("  - src/file_processor.py")
    print("  - src/ai_analyzer_complete.py")
    print("  - src/evidence_editor_ai.py")
    sys.exit(1)

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('phase1_multi.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class Phase1MultiRunner:
    """Phase 1マルチ事件対応実行クラス"""
    
    def __init__(self):
        """初期化"""
        self.case_manager = CaseManager()
        self.current_case = None
        self.db_manager = None  # 事件選択後に初期化
        self.metadata_extractor = MetadataExtractor()
        self.file_processor = FileProcessor()
        self.ai_analyzer = AIAnalyzerComplete()
        self.evidence_editor = EvidenceEditorAI()
    
    def select_case(self) -> bool:
        """事件を選択または新規作成
        
        Returns:
            選択成功: True, キャンセル: False
        """
        print("\n" + "="*70)
        print("  Phase1_Evidence Analysis System - 事件選択")
        print("="*70)
        
        # 事件を検出
        cases = self.case_manager.detect_cases()
        
        if not cases:
            print("\n事件が見つかりませんでした。")
            print("\n【選択してください】")
            print("  1. 新規事件を作成")
            print("  2. 終了")
            
            choice = input("\n選択してください (1-2): ").strip()
            
            if choice == '1':
                # 新規事件作成
                return self._create_new_case()
            else:
                print("\n❌ 終了します")
                return False
        
        # 事件一覧を表示
        print("\n【検出された事件】")
        self.case_manager.display_cases(cases)
        
        print("\n【選択してください】")
        print(f"  1-{len(cases)}. 既存事件を選択")
        print(f"  {len(cases)+1}. 新規事件を作成")
        print(f"  0. 終了")
        
        # 事件を選択
        selected_case = self.case_manager.select_case_interactive(cases, allow_new=True)
        
        if selected_case == "new":
            # 新規事件作成
            return self._create_new_case()
        elif not selected_case:
            print("\n❌ 事件が選択されませんでした")
            return False
        
        self.current_case = selected_case
        
        # データベースマネージャーを初期化
        self.db_manager = create_database_manager(self.case_manager, selected_case)
        if not self.db_manager:
            logger.warning(" データベースマネージャーの初期化に失敗しました")
        
        # 事件設定ファイルを生成
        self.case_manager.generate_case_config(selected_case, "current_case.json")
        
        return True
    
    def _create_new_case(self) -> bool:
        """新規事件を作成
        
        Returns:
            作成成功: True, キャンセル: False
        """
        print("\n" + "="*70)
        print("  新規事件の作成")
        print("="*70)
        
        try:
            # 事件情報を入力
            print("\n事件情報を入力してください")
            
            case_id = input("\n事件ID（例: 2025_001）: ").strip()
            if not case_id:
                print("エラー: 事件IDは必須です")
                return False
            
            case_name = input("事件名（例: 損害賠償請求事件）: ").strip()
            if not case_name:
                print("エラー: 事件名は必須です")
                return False
            
            case_number = input("事件番号（例: 令和7年(ワ)第1号）[省略可]: ").strip()
            court = input("裁判所（例: 東京地方裁判所）[省略可]: ").strip()
            plaintiff = input("原告（例: 山田太郎）[省略可]: ").strip()
            defendant = input("被告（例: 株式会社〇〇）[省略可]: ").strip()
            
            # 確認
            print("\n入力内容の確認:")
            print(f"  事件ID: {case_id}")
            print(f"  事件名: {case_name}")
            if case_number:
                print(f"  事件番号: {case_number}")
            if court:
                print(f"  裁判所: {court}")
            if plaintiff:
                print(f"  原告: {plaintiff}")
            if defendant:
                print(f"  被告: {defendant}")
            
            confirm = input("\nこの内容で作成しますか？ (y/n): ").strip().lower()
            if confirm != 'y':
                print("エラー: キャンセルしました")
                return False
            
            # フォルダ作成
            print("\nフォルダを作成中...")
            
            service = self.case_manager.get_google_drive_service()
            if not service:
                print("エラー: Google Drive認証に失敗しました")
                return False
            
            # 事件フォルダを作成
            case_folder_name = f"{case_id}_{case_name}"
            
            folder_metadata = {
                'name': case_folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [self.case_manager.shared_drive_root_id]
            }
            
            case_folder = service.files().create(
                body=folder_metadata,
                supportsAllDrives=True,
                fields='id, name, webViewLink'
            ).execute()
            
            case_folder_id = case_folder['id']
            print(f"  ✅ 事件フォルダ作成: {case_folder_name}")
            
            # 階層的フォルダ構造を作成
            if gconfig.USE_HIERARCHICAL_FOLDERS:
                print(f"  📁 階層的フォルダ構造を作成中...")
                
                # 甲号証ルートフォルダを作成
                ko_folder_metadata = {
                    'name': '甲号証',
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [case_folder_id]
                }
                
                ko_folder = service.files().create(
                    body=ko_folder_metadata,
                    supportsAllDrives=True,
                    fields='id, name'
                ).execute()
                
                ko_folder_id = ko_folder['id']
                print(f"    ✅ 甲号証フォルダ作成")
                
                # 甲号証配下にサブフォルダを作成
                ko_subfolders = {}
                for status_key, folder_name in [('confirmed', '確定済み'), ('pending', '整理済み_未確定'), ('unclassified', '未分類')]:
                    subfolder = service.files().create(
                        body={
                            'name': folder_name,
                            'mimeType': 'application/vnd.google-apps.folder',
                            'parents': [ko_folder_id]
                        },
                        supportsAllDrives=True,
                        fields='id, name'
                    ).execute()
                    ko_subfolders[status_key] = subfolder['id']
                    print(f"      ✅ 甲号証/{folder_name}")
                
                # 乙号証ルートフォルダを作成
                otsu_folder_metadata = {
                    'name': '乙号証',
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [case_folder_id]
                }
                
                otsu_folder = service.files().create(
                    body=otsu_folder_metadata,
                    supportsAllDrives=True,
                    fields='id, name'
                ).execute()
                
                otsu_folder_id = otsu_folder['id']
                print(f"    ✅ 乙号証フォルダ作成")
                
                # 乙号証配下にサブフォルダを作成
                otsu_subfolders = {}
                for status_key, folder_name in [('confirmed', '確定済み'), ('pending', '整理済み_未確定'), ('unclassified', '未分類')]:
                    subfolder = service.files().create(
                        body={
                            'name': folder_name,
                            'mimeType': 'application/vnd.google-apps.folder',
                            'parents': [otsu_folder_id]
                        },
                        supportsAllDrives=True,
                        fields='id, name'
                    ).execute()
                    otsu_subfolders[status_key] = subfolder['id']
                    print(f"      ✅ 乙号証/{folder_name}")
            else:
                # 旧形式のフラットな構造（後方互換性のため残す）
                ko_folder = service.files().create(
                    body={
                        'name': '甲号証',
                        'mimeType': 'application/vnd.google-apps.folder',
                        'parents': [case_folder_id]
                    },
                    supportsAllDrives=True,
                    fields='id, name'
                ).execute()
                
                otsu_folder = service.files().create(
                    body={
                        'name': '乙号証',
                        'mimeType': 'application/vnd.google-apps.folder',
                        'parents': [case_folder_id]
                    },
                    supportsAllDrives=True,
                    fields='id, name'
                ).execute()
                
                # 未分類・整理済み_未確定フォルダ（事件フォルダ直下）
                service.files().create(
                    body={
                        'name': '未分類',
                        'mimeType': 'application/vnd.google-apps.folder',
                        'parents': [case_folder_id]
                    },
                    supportsAllDrives=True,
                    fields='id, name'
                ).execute()
                
                service.files().create(
                    body={
                        'name': '整理済み_未確定',
                        'mimeType': 'application/vnd.google-apps.folder',
                        'parents': [case_folder_id]
                    },
                    supportsAllDrives=True,
                    fields='id, name'
                ).execute()
                
                print(f"  ✅ 旧形式フォルダ構造作成完了")
            
            # 事件情報を一時設定（database作成のため）
            temp_case_info = {
                'case_id': case_id,
                'case_name': case_name,
                'case_folder_id': case_folder_id
            }
            
            # データベースマネージャーを初期化してdatabase.jsonを作成
            temp_db_manager = create_database_manager(self.case_manager, temp_case_info)
            if temp_db_manager:
                # 空のdatabase.jsonがGoogle Driveに作成される
                database = temp_db_manager.load_database()
                # case_infoを追加
                database['case_info'] = {
                    "case_name": case_name,
                    "case_number": case_number or "",
                    "court": court or "",
                    "plaintiff": plaintiff or "",
                    "defendant": defendant or "",
                    "case_summary": ""
                }
                temp_db_manager.save_database(database)
                print(f"  ✅ database.json作成（Google Drive）")
            else:
                print(f"  ❌ database.json作成に失敗")
                return False
            
            # 事件情報を設定
            self.current_case = {
                'case_id': case_id,
                'case_name': case_name,
                'case_folder_id': case_folder_id,
                'ko_evidence_folder_id': ko_folder['id'],
                'otsu_evidence_folder_id': otsu_folder['id'],
                'case_folder_url': case_folder.get('webViewLink', '')
            }
            
            # 階層的構造の場合はサブフォルダ情報を追加
            if gconfig.USE_HIERARCHICAL_FOLDERS:
                self.current_case['folder_structure'] = 'hierarchical'
                self.current_case['ko_folders'] = ko_subfolders
                self.current_case['otsu_folders'] = otsu_subfolders
            else:
                self.current_case['folder_structure'] = 'legacy'
            
            # データベースマネージャーを初期化
            self.db_manager = create_database_manager(self.case_manager, self.current_case)
            if not self.db_manager:
                logger.warning(" データベースマネージャーの初期化に失敗しました")
            
            # 事件設定ファイルを生成
            self.case_manager.generate_case_config(self.current_case, "current_case.json")
            
            print("\n✅ 新規事件を作成しました")
            print(f" フォルダURL: {case_folder.get('webViewLink', 'N/A')}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ エラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _upload_database_to_gdrive(self, local_path: str, case_folder_id: str) -> Optional[str]:
        """database.jsonをGoogle Driveにアップロード
        
        Args:
            local_path: ローカルのdatabase.jsonパス
            case_folder_id: 事件フォルダID
        
        Returns:
            アップロードされたファイルID（失敗時はNone）
        """
        try:
            service = self.case_manager.get_google_drive_service()
            if not service:
                return None
            
            from googleapiclient.http import MediaFileUpload
            
            file_metadata = {
                'name': 'database.json',
                'parents': [case_folder_id],
                'mimeType': 'application/json'
            }
            
            media = MediaFileUpload(local_path, mimetype='application/json', resumable=True)
            
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                supportsAllDrives=True,
                fields='id, name'
            ).execute()
            
            logger.info(f" database.jsonをGoogle Driveにアップロード: {file['id']}")
            return file['id']
            
        except Exception as e:
            logger.error(f" database.jsonアップロード失敗: {e}")
            return None
    
    def _download_database_from_gdrive(self, case_folder_id: str) -> Optional[Dict]:
        """Google Driveからdatabase.jsonをダウンロード
        
        Args:
            case_folder_id: 事件フォルダID
        
        Returns:
            database.jsonの内容（Dict）、見つからない場合はNone
        """
        try:
            service = self.case_manager.get_google_drive_service()
            if not service:
                return None
            
            # database.jsonを検索
            query = f"name='database.json' and '{case_folder_id}' in parents and trashed=false"
            results = service.files().list(
                q=query,
                corpora='drive',
                driveId=self.case_manager.shared_drive_root_id,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                fields='files(id, name)',
                pageSize=1
            ).execute()
            
            files = results.get('files', [])
            if not files:
                logger.warning(" Google Driveにdatabase.jsonが見つかりません")
                return None
            
            file_id = files[0]['id']
            
            # ファイルをダウンロード
            import io
            from googleapiclient.http import MediaIoBaseDownload
            
            request = service.files().get_media(fileId=file_id, supportsAllDrives=True)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            fh.seek(0)
            database = json.loads(fh.read().decode('utf-8'))
            
            logger.info(f" database.jsonをGoogle Driveからダウンロード")
            return database
            
        except Exception as e:
            logger.error(f" database.jsonダウンロード失敗: {e}")
            return None
    
    def _update_database_on_gdrive(self, database: Dict, case_folder_id: str) -> bool:
        """Google Drive上のdatabase.jsonを更新
        
        Args:
            database: 更新するdatabase.json内容
            case_folder_id: 事件フォルダID
        
        Returns:
            成功: True、失敗: False
        """
        try:
            service = self.case_manager.get_google_drive_service()
            if not service:
                return False
            
            # 既存のdatabase.jsonを検索
            query = f"name='database.json' and '{case_folder_id}' in parents and trashed=false"
            results = service.files().list(
                q=query,
                corpora='drive',
                driveId=self.case_manager.shared_drive_root_id,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                fields='files(id, name)',
                pageSize=1
            ).execute()
            
            files = results.get('files', [])
            
            # 一時ファイルに保存
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as tmp:
                json.dump(database, tmp, ensure_ascii=False, indent=2)
                tmp_path = tmp.name
            
            from googleapiclient.http import MediaFileUpload
            media = MediaFileUpload(tmp_path, mimetype='application/json', resumable=True)
            
            if files:
                # 既存ファイルを更新
                file_id = files[0]['id']
                service.files().update(
                    fileId=file_id,
                    media_body=media,
                    supportsAllDrives=True
                ).execute()
                logger.info(f" Google Drive上のdatabase.jsonを更新")
            else:
                # 新規作成
                file_metadata = {
                    'name': 'database.json',
                    'parents': [case_folder_id],
                    'mimeType': 'application/json'
                }
                service.files().create(
                    body=file_metadata,
                    media_body=media,
                    supportsAllDrives=True
                ).execute()
                logger.info(f" database.jsonをGoogle Driveに新規作成")
            
            # 一時ファイルを削除
            os.remove(tmp_path)
            return True
            
        except Exception as e:
            logger.error(f" database.json更新失敗: {e}")
            return False
    
    def load_database(self) -> dict:
        """database.jsonの読み込み（Google Driveのみ）"""
        if not self.current_case:
            raise ValueError("事件が選択されていません")
        
        if not self.db_manager:
            raise ValueError("データベースマネージャーが初期化されていません")
        
        # Google Driveから読み込み
        return self.db_manager.load_database()
    
    def save_database(self, database: dict):
        """database.jsonの保存（Google Driveのみ）"""
        if not self.current_case:
            raise ValueError("事件が選択されていません")
        
        if not self.db_manager:
            raise ValueError("データベースマネージャーが初期化されていません")
        
        # メタデータ更新
        database["metadata"]["last_updated"] = datetime.now().isoformat()
        database["metadata"]["total_evidence_count"] = len(database["evidence"])
        database["metadata"]["completed_count"] = len([
            e for e in database["evidence"] if e.get("status") == "completed"
        ])
        
        # Google Driveに保存
        if self.db_manager.save_database(database):
            logger.info(f" Google Driveにdatabase.jsonを保存しました")
        else:
            logger.error(f" Google Drive保存失敗")
            raise Exception("database.jsonの保存に失敗しました")
    
    def display_main_menu(self):
        """メインメニュー表示"""
        if not self.current_case:
            print("\n❌ エラー: 事件が選択されていません")
            return
        
        print("\n" + "="*70)
        print(f"  Phase1_Evidence Analysis System - 証拠管理")
        print(f"  事件: {self.current_case['case_name']}")
        print("="*70)
        print("\n【証拠の整理・分析】")
        print("  1. 証拠整理 (未分類フォルダ → 整理済み_未確定)")
        print("  2. 証拠分析 (番号指定: tmp_001 / 範囲指定: tmp_001-011)")
        print("  3. AI対話形式で分析内容を改善")
        print("\n【証拠の確定・管理】")
        print("  4. 日付順に並び替えて確定 (整理済み_未確定 → 甲号証/乙号証)")
        print("\n【証拠の閲覧・ストーリー生成】")
        print("  5. 証拠分析一覧を表示")
        print("  6. 証拠一覧をエクスポート（CSV/Excel）")
        print("  7. 時系列ストーリーの生成（証拠を時系列で整理）")
        print("  8. 依頼者発言・メモの管理")
        print("\n【システム管理】")
        print("  9. database.jsonの状態確認")
        print("  10. 事件を切り替え")
        print("  0. 終了")
        print("-"*70)
    
    def select_evidence_type(self) -> Optional[str]:
        """証拠種別を選択
        
        Returns:
            'ko': 甲号証, 'otsu': 乙号証, None: キャンセル
        """
        print("\n証拠種別を選択してください:")
        print("  1. 甲号証（こちらの証拠）")
        print("  2. 乙号証（相手方の証拠）")
        print("  3. キャンセル")
        
        choice = input("\n> ").strip()
        
        if choice == '1':
            return 'ko'
        elif choice == '2':
            return 'otsu'
        else:
            return None
    
    def get_evidence_number_input(self, evidence_type: str = 'ko') -> Optional[List[str]]:
        """証拠番号の入力取得
        
        Args:
            evidence_type: 'ko' または 'otsu'
        
        Examples:
            tmp_070-073  -> ['tmp_070', 'tmp_071', 'tmp_072', 'tmp_073']
            tmp_001-005  -> ['tmp_001', 'tmp_002', 'tmp_003', 'tmp_004', 'tmp_005']
            tmp_001-011  -> ['tmp_001', 'tmp_002', ..., 'tmp_011']
        """
        print("\n証拠番号の入力")
        print("  単一指定: tmp_001, tmp_020")
        print("  範囲指定: tmp_001-011, tmp_020-030")
        print("  キャンセル: 空Enter")
        user_input = input("\n> ").strip()
        
        if not user_input:
            return None
        
        # 範囲指定の処理（例: tmp_001-011, tmp_020-030）
        if '-' in user_input and user_input.count('-') == 1:
            try:
                # 範囲の開始と終了を分離
                start_str, end_str = user_input.split('-')
                
                # 開始番号から prefix と数字部分を分離
                # 例: "tmp_001" -> prefix="tmp_", start_num="001"
                # 例: "tmp_020" -> prefix="tmp_", start_num="020"
                import re
                match = re.match(r'^(.+?)(\d+)$', start_str)
                if not match:
                    logger.error("範囲指定の形式が正しくありません（開始番号）")
                    print("\nエラー: 範囲指定の形式が正しくありません")
                    print("  正しい例: tmp_001-011, tmp_020-030")
                    print(f"  入力値: {user_input}")
                    return None
                
                prefix = match.group(1)  # "tmp_" or "ko"
                start_num_str = match.group(2)  # "001" or "70"
                
                # 数値変換
                start_num = int(start_num_str)
                end_num = int(end_str)
                
                if start_num > end_num:
                    logger.error("開始番号は終了番号以下でなければなりません")
                    print(f"\nエラー: 開始番号({start_num})が終了番号({end_num})より大きいです")
                    return None
                
                # 範囲が大きすぎないかチェック
                range_size = end_num - start_num + 1
                if range_size > 100:
                    print(f"\nエラー: 範囲が大きすぎます({range_size}件)")
                    print("  一度に処理できるのは100件までです")
                    return None
                
                # ゼロ埋めの桁数を判定（開始番号の桁数を維持）
                width = len(start_num_str)
                
                # 範囲内の証拠番号リストを生成
                # 例: tmp_001, tmp_002, ..., tmp_011
                return [f"{prefix}{i:0{width}d}" for i in range(start_num, end_num + 1)]
                
            except ValueError as e:
                logger.error(f"範囲指定の形式が正しくありません: {e}")
                print("\nエラー: 範囲指定の形式が正しくありません")
                print("  正しい例: tmp_001-011, tmp_020-030")
                print(f"  詳細: {e}")
                return None
        else:
            # 単一証拠番号
            return [user_input]
    
    def search_evidence_files_from_gdrive(self) -> List[Dict]:
        """Google Driveから証拠ファイルを検索
        
        Returns:
            検出された証拠ファイルのリスト
        """
        if not self.current_case or not self.current_case.get('ko_evidence_folder_id'):
            logger.error(" 甲号証フォルダIDが設定されていません")
            return []
        
        print("\nGoogle Driveから証拠ファイルを検索中...")
        
        service = self.case_manager.get_google_drive_service()
        if not service:
            logger.error(" Google Drive認証に失敗しました")
            return []
        
        try:
            ko_folder_id = self.current_case['ko_evidence_folder_id']
            query = f"'{ko_folder_id}' in parents and trashed=false and mimeType!='application/vnd.google-apps.folder'"
            
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
            print(f"完了: {len(files)}件の証拠ファイルを検出しました")
            
            return files
            
        except Exception as e:
            logger.error(f" Google Drive検索エラー: {e}")
            return []
    
    def _get_gdrive_info_from_database(self, evidence_number: str, evidence_type: str = 'ko') -> Optional[Dict]:
        """database.jsonから証拠のGoogle Drive情報を取得
        
        Args:
            evidence_number: 証拠番号（例: tmp_001, tmp_020）
            evidence_type: 証拠種別 ('ko' または 'otsu')
        
        Returns:
            Google Driveファイル情報（見つからない場合はNone）
        """
        try:
            database = self.load_database()
            
            # 証拠番号を正規化（甲001 → ko001で統一）
            normalized_number = evidence_number
            if evidence_number.startswith('甲'):
                normalized_number = f"ko{evidence_number[1:]}"
            elif evidence_number.startswith('乙'):
                normalized_number = f"otsu{evidence_number[1:]}"
            
            # データベースから証拠を検索
            # 1. evidence_id で検索（確定済み証拠: ko001, ko002...）
            # 2. temp_id で検索（整理済み_未確定: tmp_001, tmp_002...）
            for evidence in database.get('evidence', []):
                # 確定済み証拠の検索
                if evidence.get('evidence_id') == normalized_number:
                    # Google DriveファイルIDを取得（複数の場所をチェック）
                    gdrive_file_id = evidence.get('gdrive_file_id')
                    
                    # gdrive_file_idがない場合、complete_metadata.gdrive.file_idをチェック
                    if not gdrive_file_id:
                        metadata = evidence.get('complete_metadata', {})
                        gdrive_info = metadata.get('gdrive', {})
                        gdrive_file_id = gdrive_info.get('file_id')
                    
                    if not gdrive_file_id:
                        logger.warning(f" 証拠 {evidence_number} のGoogle DriveファイルIDが見つかりません")
                        return None
                    
                    # Google Drive APIでファイル情報を取得
                    service = self.case_manager.get_google_drive_service()
                    if not service:
                        logger.error(" Google Drive認証に失敗しました")
                        return None
                    
                    file_info = service.files().get(
                        fileId=gdrive_file_id,
                        supportsAllDrives=True,
                        fields='id, name, mimeType, size, createdTime, modifiedTime, webViewLink, webContentLink'
                    ).execute()
                    
                    return file_info
                
                # 未確定証拠の検索（temp_id: tmp_001, tmp_002...）
                if evidence.get('temp_id') == evidence_number:
                    # Google DriveファイルIDを取得（複数の場所をチェック）
                    gdrive_file_id = evidence.get('gdrive_file_id')
                    
                    # gdrive_file_idがない場合、complete_metadata.gdrive.file_idをチェック
                    if not gdrive_file_id:
                        metadata = evidence.get('complete_metadata', {})
                        gdrive_info = metadata.get('gdrive', {})
                        gdrive_file_id = gdrive_info.get('file_id')
                    
                    if not gdrive_file_id:
                        logger.warning(f" 証拠 {evidence_number} のGoogle DriveファイルIDが見つかりません")
                        return None
                    
                    # Google Drive APIでファイル情報を取得
                    service = self.case_manager.get_google_drive_service()
                    if not service:
                        logger.error(" Google Drive認証に失敗しました")
                        return None
                    
                    file_info = service.files().get(
                        fileId=gdrive_file_id,
                        supportsAllDrives=True,
                        fields='id, name, mimeType, size, createdTime, modifiedTime, webViewLink, webContentLink'
                    ).execute()
                    
                    return file_info
            
            logger.warning(f" 証拠 {evidence_number} がdatabase.jsonに見つかりません")
            return None
            
        except Exception as e:
            logger.error(f" database.json読み込みエラー: {e}")
            return None
    
    def process_evidence(self, evidence_number: str, gdrive_file_info: Dict = None, evidence_type: str = 'ko') -> bool:
        """証拠の処理（完全版）
        
        Args:
            evidence_number: 証拠番号（例: tmp_001）
            gdrive_file_info: Google Driveファイル情報（オプション）
            evidence_type: 証拠種別 ('ko' または 'otsu')
            
        Returns:
            処理成功: True, 失敗: False
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"  証拠 {evidence_number} の処理開始")
        logger.info(f"{'='*70}")
        
        try:
            # 1. ファイルパスの取得（Google Driveから）
            if gdrive_file_info:
                logger.info(f"ファイル: {gdrive_file_info['name']}")
                logger.info(f"🔗 URL: {gdrive_file_info.get('webViewLink', 'N/A')}")
                
                # Google Driveからダウンロード
                file_path = self._download_file_from_gdrive(gdrive_file_info)
                if not file_path:
                    logger.error(" ファイルのダウンロードに失敗しました")
                    return False
            else:
                # ローカルファイルパスを使用
                logger.warning(" Google Drive情報がありません。ローカルファイルを指定してください。")
                print("\n" + "="*70)
                print(f"  証拠 {evidence_number} のファイルパスを入力してください")
                print("="*70)
                print("\n例:")
                print("  /home/user/webapp/evidence_files/tmp_020.pdf")
                print("  /tmp/sample.pdf")
                print("\nキャンセル: 空Enter")
                
                file_path_input = input("\nファイルパス > ").strip()
                
                if not file_path_input:
                    logger.warning(" ユーザーがキャンセルしました")
                    print("\n❌ キャンセルしました")
                    return False
                
                file_path = file_path_input
                
                if not os.path.exists(file_path):
                    logger.error(f" ファイルが見つかりません: {file_path}")
                    print(f"\n❌ エラー: ファイルが見つかりません")
                    print(f"  パス: {file_path}")
                    print("\n指定されたファイルパスが正しいか確認してください")
                    return False
                
                logger.info(f"✅ ローカルファイルを使用: {file_path}")
            
            # 2. メタデータ抽出
            logger.info(f"メタデータを抽出中...")
            metadata = self.metadata_extractor.extract_complete_metadata(
                file_path,
                gdrive_file_info=gdrive_file_info
            )
            logger.info(f"  - ファイルハッシュ(SHA-256): {metadata['hashes']['sha256'][:16]}...")
            logger.info(f"  - ファイルサイズ: {metadata['basic']['file_size_human']}")
            
            # 3. ファイル処理
            logger.info(f"ファイルを処理中...")
            file_type = self._detect_file_type(file_path)
            processed_data = self.file_processor.process_file(file_path, file_type)
            logger.info(f"  - ファイル形式: {processed_data['file_type']}")
            
            # 4. AI分析（GPT-4o Vision）
            logger.info(f"AI分析を実行中（GPT-4o Vision）...")
            analysis_result = self.ai_analyzer.analyze_evidence_complete(
                evidence_id=evidence_number,
                file_path=file_path,
                file_type=file_type,
                gdrive_file_info=gdrive_file_info,
                case_info=self.current_case
            )
            
            # 5. 品質評価
            quality = analysis_result.get('quality_assessment', {})
            logger.info(f"品質評価:")
            logger.info(f"  - 完全性スコア: {quality.get('completeness_score', 0):.1%}")
            logger.info(f"  - 信頼度スコア: {quality.get('confidence_score', 0):.1%}")
            logger.info(f"  - 言語化レベル: {quality.get('verbalization_level', 0)}")
            
            # 6. database.jsonに追加
            logger.info(f"database.jsonに保存中...")
            database = self.load_database()
            
            evidence_entry = {
                "evidence_id": evidence_number,
                "evidence_number": f"甲{evidence_number.lstrip('ko')}",
                "original_filename": gdrive_file_info['name'] if gdrive_file_info else os.path.basename(file_path),
                "complete_metadata": metadata,
                "phase1_complete_analysis": analysis_result,
                "status": "completed",
                "processed_at": datetime.now().isoformat()
            }
            
            # 既存のエントリを更新、または新規追加
            # temp_id, evidence_id, evidence_number のいずれかでマッチング
            existing_index = next(
                (i for i, e in enumerate(database["evidence"]) 
                 if (e.get("evidence_id") == evidence_number or
                     e.get("temp_id") == evidence_number or
                     e.get("evidence_number") == evidence_number)),
                None
            )
            
            if existing_index is not None:
                # 既存エントリのtemp_idを保持
                old_entry = database["evidence"][existing_index]
                if 'temp_id' in old_entry:
                    evidence_entry['temp_id'] = old_entry['temp_id']
                if 'temp_number' in old_entry:
                    evidence_entry['temp_number'] = old_entry['temp_number']
                
                database["evidence"][existing_index] = evidence_entry
                logger.info(f"  ✅ 既存エントリを更新しました（temp_id: {old_entry.get('temp_id')}）")
            else:
                database["evidence"].append(evidence_entry)
                logger.info(f"  ✅ 新規エントリを追加しました")
            
            self.save_database(database)
            
            logger.info(f"\n✅ 証拠 {evidence_number} の処理が完了しました！")
            return True
            
        except Exception as e:
            logger.error(f" エラーが発生しました: {e}", exc_info=True)
            return False
    
    def _download_file_from_gdrive(self, file_info: Dict) -> Optional[str]:
        """Google Driveからファイルをダウンロード"""
        try:
            import io
            from googleapiclient.http import MediaIoBaseDownload
            
            service = self.case_manager.get_google_drive_service()
            file_id = file_info['id']
            file_name = file_info['name']
            
            # 一時ディレクトリにダウンロード
            temp_dir = gconfig.LOCAL_TEMP_DIR
            os.makedirs(temp_dir, exist_ok=True)
            
            output_path = os.path.join(temp_dir, file_name)
            
            request = service.files().get_media(fileId=file_id)
            fh = io.FileIO(output_path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    logger.info(f"  ダウンロード進捗: {int(status.progress() * 100)}%")
            
            fh.close()
            logger.info(f"  ✅ ダウンロード完了: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f" ダウンロードエラー: {e}")
            return None
    
    def _detect_file_type(self, file_path: str) -> str:
        """ファイル形式を検出"""
        ext = os.path.splitext(file_path)[1].lower()
        
        for file_type, info in gconfig.SUPPORTED_FORMATS.items():
            if ext in info['extensions']:
                return file_type
        
        return 'document'  # デフォルト
    
    def finalize_pending_evidence(self):
        """整理済み_未確定の証拠を並び替えて確定"""
        print("\n" + "="*70)
        print("  証拠の並び替え・確定")
        print("="*70)
        
        # database.jsonから未確定証拠を取得
        database = self.load_database()
        pending_evidence = [e for e in database.get('evidence', []) if e.get('status') == 'pending']
        
        if not pending_evidence:
            print("\n未確定の証拠はありません")
            return
        
        print(f"\n未確定証拠: {len(pending_evidence)}件")
        print("\n現在の順序:")
        for idx, evidence in enumerate(pending_evidence, 1):
            print(f"  [{idx}] {evidence['temp_id']} - {evidence['original_filename']}")
            print(f"      種別: {evidence['evidence_type']}, 説明: {evidence['description']}")
        
        print("\n操作を選択してください:")
        print("  1: この順序で確定 (甲001, 甲002...)")
        print("  2: 順序を変更")
        print("  0: キャンセル")
        
        while True:
            choice = input("\n> ").strip()
            if choice in ['0', '1', '2']:
                break
            print("エラー: 0, 1, 2 のいずれかを入力してください")
        
        if choice == '0':
            print("エラー: キャンセルしました")
            return
        
        elif choice == '2':
            # 順序変更
            print("\n順序を変更します")
            print("   例: 1,3,2,4 → 1番目,3番目,2番目,4番目の順")
            new_order_input = input(f"新しい順序を入力 (1-{len(pending_evidence)}をカンマ区切り): ").strip()
            
            try:
                new_order = [int(x.strip()) for x in new_order_input.split(',')]
                if len(new_order) != len(pending_evidence) or set(new_order) != set(range(1, len(pending_evidence) + 1)):
                    print("エラー: 無効な順序です")
                    return
                
                # 並び替え
                pending_evidence = [pending_evidence[i-1] for i in new_order]
                
                print("\n✅ 並び替え後:")
                for idx, evidence in enumerate(pending_evidence, 1):
                    print(f"  [{idx}] {evidence['temp_id']} - {evidence['original_filename']}")
                
            except ValueError:
                print("エラー: 入力エラー")
                return
        
        # 確定確認
        confirm = input(f"\nこの順序で確定しますか？ (y/n): ").strip().lower()
        if confirm != 'y':
            print("エラー: キャンセルしました")
            return
        
        # 確定処理
        print("\n📥 証拠を確定中...")
        service = self.case_manager.get_google_drive_service()
        if not service:
            print("エラー: Google Drive認証に失敗しました")
            return
        
        success_count = 0
        ko_folder_id = self.current_case['ko_evidence_folder_id']
        
        # 整理済み_未確定フォルダIDを取得
        from evidence_organizer import EvidenceOrganizer
        organizer = EvidenceOrganizer(self.case_manager, self.current_case)
        pending_folder_id = organizer.pending_folder_id
        
        for idx, evidence in enumerate(pending_evidence, 1):
            ko_number = idx
            ko_id = f"ko{ko_number:03d}"
            ko_number_kanji = f"甲{ko_number:03d}"
            
            print(f"\n[{idx}/{len(pending_evidence)}] {evidence['temp_id']} → {ko_id}")
            
            try:
                # ファイルを取得
                file_id = evidence['gdrive_file_id']
                
                # 新しいファイル名を生成
                old_filename = evidence['renamed_filename']
                # tmp_XXX_ の部分を koXXX_ に置換
                new_filename = old_filename.replace(evidence['temp_id'], ko_id)
                
                # ファイルを移動してリネーム
                file = service.files().update(
                    fileId=file_id,
                    addParents=ko_folder_id,
                    removeParents=pending_folder_id,
                    body={'name': new_filename},
                    supportsAllDrives=True,
                    fields='id, name'
                ).execute()
                
                print(f"  ✅ {new_filename}")
                
                # database.jsonの証拠情報を更新
                evidence['evidence_id'] = ko_id
                evidence['evidence_number'] = ko_number_kanji
                evidence['renamed_filename'] = new_filename
                evidence['status'] = 'completed'
                evidence['confirmed_at'] = datetime.now().isoformat()
                
                success_count += 1
                
            except Exception as e:
                print(f"  ❌ エラー: {e}")
        
        # database.jsonを保存
        self.save_database(database)
        
        print("\n" + "="*70)
        print(f"完了: 確定完了: {success_count}/{len(pending_evidence)}件")
        print("="*70)
    
    def analyze_and_sort_pending_evidence(self, evidence_type: str = 'ko'):
        """未確定証拠をAI分析→日付抽出→自動ソート→確定
        
        Args:
            evidence_type: 証拠種別 ('ko' または 'otsu')
        """
        type_name = "甲号証" if evidence_type == 'ko' else "乙号証"
        type_folder = "甲号証" if evidence_type == 'ko' else "乙号証"
        
        print("\n" + "="*70)
        print(f"  未確定証拠の分析・日付抽出・自動ソート [{type_name}]")
        print("="*70)
        
        # database.jsonから未確定証拠を取得（証拠種別でフィルター）
        database = self.load_database()
        pending_evidence = [
            e for e in database.get('evidence', []) 
            if e.get('status') == 'pending' and e.get('evidence_type', 'ko') == evidence_type
        ]
        
        if not pending_evidence:
            print(f"\n{type_name}の未確定証拠はありません")
            return
        
        print(f"\n{type_name}の未確定証拠: {len(pending_evidence)}件")
        print("\n現在の順序:")
        for idx, evidence in enumerate(pending_evidence, 1):
            print(f"  [{idx}] {evidence['temp_id']} - {evidence['original_filename']}")
        
        prefix = "ko" if evidence_type == 'ko' else "otsu"
        print("\n【処理内容】")
        print("  1. 各証拠から作成年月日を取得（既に分析済みならdocument_dateを使用）")
        print("  2. 作成年月日順に自動ソート（古い順）")
        print(f"  3. ソート後の順序で確定番号（{prefix}001, {prefix}002, {prefix}003...）を割り当て")
        print(f"  4. 整理済み_未確定 → {type_folder} フォルダへ移動")
        
        confirm = input("\n処理を開始しますか？ (y/n): ").strip().lower()
        if confirm != 'y':
            print("エラー: キャンセルしました")
            return
        
        # ステップ1: 作成年月日の取得
        print("\n" + "="*70)
        print("  [1/3] 作成年月日の取得中...")
        print("="*70)
        
        service = self.case_manager.get_google_drive_service()
        if not service:
            print("エラー: Google Drive認証に失敗しました")
            return
        
        for idx, evidence in enumerate(pending_evidence, 1):
            print(f"\n[{idx}/{len(pending_evidence)}] {evidence['temp_id']} - {evidence['original_filename']}")
            
            # まず、既存のAI分析からdocument_dateを取得
            document_date = None
            if 'phase1_complete_analysis' in evidence:
                ai_analysis = evidence['phase1_complete_analysis'].get('ai_analysis', {})
                obj_analysis = ai_analysis.get('objective_analysis', {})
                temporal_info = obj_analysis.get('temporal_information', {})
                # v3.6.2以降: document_date、v3.6.1以前: creation_date（後方互換性）
                document_date = temporal_info.get('document_date') or temporal_info.get('creation_date')
                
                if document_date:
                    print(f"  ✅ 既存分析から取得: {document_date}")
                    evidence['extracted_date'] = document_date
                    continue
            
            # 既存分析がない場合のみ、別途日付抽出を実行
            print(f"  ⚠️ 未分析のため日付抽出を実行...")
            
            try:
                # Google Driveからファイルをダウンロード
                gdrive_file_id = evidence.get('gdrive_file_id')
                if not gdrive_file_id:
                    print(f"  ⚠️ Google DriveファイルIDが見つかりません")
                    evidence['extracted_date'] = None
                    continue
                
                # ファイル情報を取得
                file_info = service.files().get(
                    fileId=gdrive_file_id,
                    supportsAllDrives=True,
                    fields='id, name, mimeType'
                ).execute()
                
                # ファイルをダウンロード
                file_path = self._download_file_from_gdrive(file_info)
                if not file_path:
                    print(f"  ⚠️ ファイルのダウンロードに失敗しました")
                    evidence['extracted_date'] = None
                    continue
                
                # ファイルタイプを検出
                file_type = self._detect_file_type(file_path)
                
                # 日付抽出（軽量版）
                date_result = self.ai_analyzer.extract_date_from_evidence(
                    evidence_id=evidence['temp_id'],
                    file_path=file_path,
                    file_type=file_type,
                    original_filename=evidence['original_filename']
                )
                
                # 結果を証拠情報に追加
                evidence['date_extraction'] = date_result
                evidence['extracted_date'] = date_result.get('primary_date')
                
                if evidence['extracted_date']:
                    print(f"  📅 抽出日付: {evidence['extracted_date']}")
                else:
                    print(f"  ⚠️ 日付が抽出できませんでした")
                
            except Exception as e:
                print(f"  ❌ エラー: {e}")
                evidence['extracted_date'] = None
        
        # ステップ2: 作成年月日順にソート
        print("\n" + "="*70)
        print("  [2/3] 作成年月日順にソート中...")
        print("="*70)
        
        # 日付が取得できたものと取得できなかったものに分離
        with_date = [e for e in pending_evidence if e.get('extracted_date')]
        without_date = [e for e in pending_evidence if not e.get('extracted_date')]
        
        # 作成年月日順にソート（古い順）
        with_date.sort(key=lambda e: e['extracted_date'])
        
        # ソート後の順序（日付あり→日付なし）
        sorted_evidence = with_date + without_date
        
        print(f"\n✅ ソート完了:")
        print(f"  - 日付取得成功: {len(with_date)}件")
        print(f"  - 日付取得失敗: {len(without_date)}件")
        
        print("\nソート後の順序:")
        for idx, evidence in enumerate(sorted_evidence, 1):
            date_str = evidence.get('extracted_date', '日付なし')
            print(f"  [{idx}] {evidence['temp_id']} - {evidence['original_filename']} ({date_str})")
        
        # ステップ3: 確定番号割り当て・移動
        print("\n" + "="*70)
        print("  [3/3] 確定番号を割り当て中...")
        print("="*70)
        
        confirm_finalize = input("\nこの順序で確定しますか？ (y/n): ").strip().lower()
        if confirm_finalize != 'y':
            print("エラー: キャンセルしました（日付抽出結果はdatabase.jsonに保存されました）")
            self.save_database(database)
            return
        
        success_count = 0
        ko_folder_id = self.current_case['ko_evidence_folder_id']
        
        # 整理済み_未確定フォルダIDを取得
        from evidence_organizer import EvidenceOrganizer
        organizer = EvidenceOrganizer(self.case_manager, self.current_case)
        pending_folder_id = organizer.pending_folder_id
        
        for idx, evidence in enumerate(sorted_evidence, 1):
            ko_number = idx
            ko_id = f"ko{ko_number:03d}"
            ko_number_kanji = f"甲{ko_number:03d}"
            
            print(f"\n[{idx}/{len(sorted_evidence)}] {evidence['temp_id']} → {ko_id}")
            date_str = evidence.get('extracted_date', '日付なし')
            print(f"  日付: {date_str}")
            
            try:
                # ファイルを取得
                file_id = evidence['gdrive_file_id']
                
                # 新しいファイル名を生成
                old_filename = evidence['renamed_filename']
                # tmp_XXX_ の部分を koXXX_ に置換
                new_filename = old_filename.replace(evidence['temp_id'], ko_id)
                
                # ファイルを移動してリネーム
                file = service.files().update(
                    fileId=file_id,
                    addParents=ko_folder_id,
                    removeParents=pending_folder_id,
                    body={'name': new_filename},
                    supportsAllDrives=True,
                    fields='id, name'
                ).execute()
                
                print(f"  ✅ {new_filename}")
                
                # database.jsonの証拠情報を更新
                evidence['evidence_id'] = ko_id
                evidence['evidence_number'] = ko_number_kanji
                evidence['renamed_filename'] = new_filename
                evidence['status'] = 'completed'
                evidence['confirmed_at'] = datetime.now().isoformat()
                evidence['sorted_by_date'] = True  # 日付ソートで確定したことを記録
                
                success_count += 1
                
            except Exception as e:
                print(f"  ❌ エラー: {e}")
        
        # database.jsonを保存
        self.save_database(database)
        
        print("\n" + "="*70)
        print(f"完了: 確定完了: {success_count}/{len(sorted_evidence)}件")
        print(f"日付順ソート: {len(with_date)}件")
        print("="*70)
    
    def show_database_status(self):
        """database.jsonの状態表示"""
        database = self.load_database()
        
        print("\n" + "="*70)
        print("  database.json 状態確認")
        print("="*70)
        
        print(f"\n事件情報:")
        metadata = database.get('metadata', {})
        print(f"  事件ID: {metadata.get('case_id', 'N/A')}")
        print(f"  事件名: {metadata.get('case_name', 'N/A')}")
        print(f"  データベースバージョン: {metadata.get('database_version', database.get('version', 'N/A'))}")
        print(f"  最終更新: {metadata.get('last_updated', 'N/A')}")
        
        print(f"\n証拠統計:")
        print(f"  総証拠数: {len(database['evidence'])}件")
        
        completed = [e for e in database['evidence'] if e.get('status') == 'completed']
        print(f"  完了: {len(completed)}件")
        
        pending = [e for e in database['evidence'] if e.get('status') == 'pending']
        print(f"  未確定: {len(pending)}件")
        
        in_progress = [e for e in database['evidence'] if e.get('status') == 'in_progress']
        print(f"  処理中: {len(in_progress)}件")
        
        if database['evidence']:
            print(f"\n証拠一覧 (最大20件):")
            for evidence in database['evidence'][:20]:
                status = evidence.get('status', 'unknown')
                if status == 'completed':
                    status_text = "[完了]"
                    evidence_id = evidence.get('evidence_number', evidence.get('evidence_id', 'N/A'))
                elif status == 'pending':
                    status_text = "[未確定]"
                    evidence_id = evidence.get('temp_id', 'N/A')
                else:
                    status_text = "[不明]"
                    evidence_id = 'N/A'
                
                print(f"  {status_text} {evidence_id} - {evidence.get('original_filename', 'N/A')}")
            
            if len(database['evidence']) > 20:
                print(f"  ... 他 {len(database['evidence']) - 20}件")
        
        print("\n" + "="*70)
    
    def edit_evidence_with_ai(self, evidence_type: str = 'ko'):
        """AI対話形式で証拠内容を編集
        
        Args:
            evidence_type: 証拠種別 ('ko' または 'otsu')
        """
        if not self.current_case:
            raise ValueError("事件が選択されていません")
        
        type_name = "甲号証" if evidence_type == 'ko' else "乙号証"
        print("\n" + "="*70)
        print(f"  AI対話形式で証拠内容を改善 [{type_name}]")
        print("="*70)
        
        # 証拠番号を入力
        evidence_numbers = self.get_evidence_number_input(evidence_type)
        if not evidence_numbers:
            print("\nキャンセルしました")
            return
        
        # 1件ずつ処理
        for evidence_number in evidence_numbers:
            print(f"\n処理中: {evidence_number}")
            
            # データベースから証拠データを取得
            database = self.db_manager.load_database()
            evidence_data = None
            
            for evidence in database.get('evidence', []):
                # evidence_id または temp_id で検索
                if (evidence.get('evidence_id') == evidence_number or 
                    evidence.get('temp_id') == evidence_number or
                    evidence.get('evidence_number') == evidence_number):
                    evidence_data = evidence
                    break
            
            if not evidence_data:
                print(f"\nエラー: 証拠 {evidence_number} が見つかりません")
                continue
            
            # AI分析結果が存在するか確認
            if 'phase1_complete_analysis' not in evidence_data:
                print(f"\nエラー: {evidence_number} はまだAI分析されていません")
                print("  先にメニュー「2」または「3」で分析を実行してください")
                continue
            
            # AI対話形式で編集
            modified_data = self.evidence_editor.edit_evidence_interactive(
                evidence_data,
                self.db_manager
            )
            
            # 編集がキャンセルされた場合
            if modified_data is None:
                print(f"\n{evidence_number} の編集をキャンセルしました")
                continue
            
            # データベースを更新
            print(f"\n{evidence_number} をデータベースに保存中...")
            
            for i, evidence in enumerate(database['evidence']):
                if (evidence.get('evidence_id') == evidence_number or 
                    evidence.get('temp_id') == evidence_number or
                    evidence.get('evidence_number') == evidence_number):
                    database['evidence'][i] = modified_data
                    break
            
            # 保存
            self.db_manager.save_database(database)
            print(f"✅ {evidence_number} の変更を保存しました")
    
    def _get_evidence_display_data(self, evidence: Dict) -> Dict:
        """証拠データから表示用情報を抽出（データ構造の違いを吸収）
        
        Args:
            evidence: 証拠データ
            
        Returns:
            表示用データ（file_name, creation_date, analysis_status）
        """
        # ファイル名の取得（複数の場所を試行）
        file_name = (
            evidence.get('file_name') or
            evidence.get('original_filename') or
            evidence.get('complete_metadata', {}).get('basic', {}).get('file_name') or
            '不明'
        )
        
        # 分析結果の取得（データ構造の違いを吸収）
        phase1_analysis = evidence.get('phase1_complete_analysis', {})
        
        # 新しい構造: phase1_complete_analysis.ai_analysis.full_content.complete_description
        ai_analysis = phase1_analysis.get('ai_analysis', {})
        
        # 作成日の取得（優先順位：AI分析結果 > PDFメタデータ > ファイルシステム）
        # 1. AI分析結果から文書の作成日を取得（最優先）
        document_date = None
        if ai_analysis:
            objective_analysis = ai_analysis.get('objective_analysis', {})
            temporal_info = objective_analysis.get('temporal_information', {})
            document_date = temporal_info.get('document_date')
        
        # 2. 旧構造のフォールバック
        if not document_date:
            document_date = (
                phase1_analysis.get('objective_analysis', {}).get('temporal_information', {}).get('document_date') or
                evidence.get('temporal_information', {}).get('document_date')
            )
        
        # 3. PDFメタデータから取得（フォールバック）
        if not document_date:
            pdf_date = evidence.get('complete_metadata', {}).get('format_specific', {}).get('document_info', {}).get('CreationDate', '')
            if pdf_date and len(pdf_date) >= 10:
                # "D:20220103..." -> "2022-01-03" に変換
                if pdf_date.startswith('D:'):
                    pdf_date = pdf_date[2:]
                if len(pdf_date) >= 8:
                    document_date = f"{pdf_date[:4]}-{pdf_date[4:6]}-{pdf_date[6:8]}"
        
        # 4. ファイルシステム上の作成日（最終フォールバック）
        if not document_date:
            fs_date = evidence.get('complete_metadata', {}).get('basic', {}).get('created_time', '')
            if fs_date:
                document_date = fs_date[:10]  # YYYY-MM-DD部分のみ
        
        creation_date = document_date or '不明'
        if ai_analysis:
            full_content = ai_analysis.get('full_content', {})
            complete_description = full_content.get('complete_description')
        else:
            # 旧構造: phase1_complete_analysis.complete_description または full_content.complete_description
            complete_description = (
                phase1_analysis.get('complete_description') or
                phase1_analysis.get('full_content', {}).get('complete_description') or
                evidence.get('full_content', {}).get('complete_description')
            )
        
        analysis_status = "✅ 分析済み" if complete_description else "⚠️  未分析"
        
        return {
            'file_name': file_name,
            'creation_date': creation_date,
            'analysis_status': analysis_status,
            'complete_description': complete_description
        }
    
    def _get_evidence_export_data(self, evidence: Dict) -> Dict:
        """証拠データからエクスポート用詳細情報を抽出（データ構造の違いを吸収）
        
        Args:
            evidence: 証拠データ
            
        Returns:
            エクスポート用データ（基本情報+分析詳細）
        """
        # 基本情報を取得
        display_data = self._get_evidence_display_data(evidence)
        
        # 分析詳細の取得（データ構造の違いを吸収）
        phase1_analysis = evidence.get('phase1_complete_analysis', {})
        ai_analysis = phase1_analysis.get('ai_analysis', {})
        
        if ai_analysis:
            # 新しい構造: phase1_complete_analysis.ai_analysis.objective_analysis
            objective_analysis = ai_analysis.get('objective_analysis', {})
            document_type = objective_analysis.get('document_type', '')
            
            # author, recipientの取得
            parties = objective_analysis.get('parties_mentioned', {})
            organizations = parties.get('organizations', [])
            author = organizations[0] if organizations else ''
            recipient = organizations[1] if len(organizations) > 1 else ''
        else:
            # 旧構造: phase1_complete_analysis直下またはfull_content内
            old_analysis = phase1_analysis or evidence.get('full_content', {})
            document_type = old_analysis.get('document_type', '')
            author = old_analysis.get('author', '')
            recipient = old_analysis.get('recipient', '')
        
        return {
            **display_data,
            'document_type': document_type,
            'author': author,
            'recipient': recipient
        }
    
    def show_evidence_list(self, evidence_type: str = 'ko'):
        """証拠分析一覧を表示
        
        Args:
            evidence_type: 証拠種別 ('ko' または 'otsu')
        """
        type_name = "甲号証" if evidence_type == 'ko' else "乙号証"
        
        print("\n" + "="*70)
        print(f"  証拠分析一覧 [{type_name}]")
        print("="*70)
        
        # データベースを読み込み
        database = self.db_manager.load_database()
        evidence_list = database.get('evidence', [])
        
        if not evidence_list:
            print("\n⚠️  証拠が登録されていません")
            return
        
        # 証拠種別でフィルター
        filtered_evidence = [
            e for e in evidence_list 
            if e.get('evidence_type', 'ko') == evidence_type
        ]
        
        if not filtered_evidence:
            print(f"\n⚠️  {type_name}の証拠が登録されていません")
            return
        
        # ステータス別に分類
        confirmed_evidence = []      # 確定済み（甲号証/乙号証）
        pending_evidence = []        # 整理済み_未確定
        unclassified_evidence = []   # 未分類
        
        for evidence in filtered_evidence:
            evidence_id = evidence.get('evidence_id', '')
            evidence_number = evidence.get('evidence_number', '')
            
            # 整理状態を判定（優先順位が重要）
            # 1. 整理済み_未確定: evidence_idが "tmp_" で始まる（最優先）
            if evidence_id.startswith('tmp_'):
                pending_evidence.append(evidence)
            # 2. 確定済み: evidence_numberが "甲1" や "乙2" のような形式
            #    （"甲tmp" や "乙tmp" で始まらない、かつ証拠番号が存在する）
            elif evidence_number and not evidence_number.startswith('甲tmp') and not evidence_number.startswith('乙tmp'):
                confirmed_evidence.append(evidence)
            # 3. 未分類: その他
            else:
                unclassified_evidence.append(evidence)
        
        # 確定済み証拠の表示
        if confirmed_evidence:
            print(f"\n【確定済み（{type_name}）】")
            print("-"*70)
            for evidence in sorted(confirmed_evidence, key=lambda x: x.get('evidence_id', '')):
                evidence_id = evidence.get('evidence_id', '不明')
                temp_id = evidence.get('temp_id', '')
                
                # データ構造の違いを吸収して表示用データを取得
                display_data = self._get_evidence_display_data(evidence)
                
                print(f"  {evidence_id:10} | {display_data['creation_date']:12} | {display_data['analysis_status']:12} | {display_data['file_name']}")
                if temp_id:
                    print(f"             (元ID: {temp_id})")
        
        # 整理済み_未確定証拠の表示
        if pending_evidence:
            print("\n【整理済み_未確定】")
            print("-"*70)
            for evidence in sorted(pending_evidence, key=lambda x: x.get('temp_id', '')):
                temp_id = evidence.get('temp_id', '不明')
                
                # データ構造の違いを吸収して表示用データを取得
                display_data = self._get_evidence_display_data(evidence)
                
                print(f"  {temp_id:10} | {display_data['creation_date']:12} | {display_data['analysis_status']:12} | {display_data['file_name']}")
        
        # 未分類証拠の表示
        if unclassified_evidence:
            print("\n【未分類】")
            print("-"*70)
            for evidence in unclassified_evidence:
                file_name = evidence.get('file_name', '不明')
                temp_id = evidence.get('temp_id', '')
                evidence_id = evidence.get('evidence_id', '')
                display_id = evidence_id or temp_id or '不明'
                
                print(f"  {display_id:10} | {file_name}")
        
        # サマリー表示
        print("\n" + "="*70)
        print(f"  {type_name}の合計: {len(filtered_evidence)}件")
        print(f"    確定済み: {len(confirmed_evidence)}件")
        print(f"    整理済み_未確定: {len(pending_evidence)}件")
        print(f"    未分類: {len(unclassified_evidence)}件")
        print("="*70)
    
    def export_evidence_list(self, evidence_type: str = 'ko'):
        """証拠一覧をCSV/Excel形式でエクスポート
        
        Args:
            evidence_type: 証拠種別 ('ko' または 'otsu')
        """
        type_name = "甲号証" if evidence_type == 'ko' else "乙号証"
        
        print("\n" + "="*70)
        print(f"  証拠一覧エクスポート [{type_name}]")
        print("="*70)
        
        # データベースを読み込み
        database = self.db_manager.load_database()
        evidence_list = database.get('evidence', [])
        
        if not evidence_list:
            print("\n⚠️  証拠が登録されていません")
            return
        
        # 証拠種別でフィルター
        filtered_evidence = [
            e for e in evidence_list 
            if e.get('evidence_type', 'ko') == evidence_type
        ]
        
        if not filtered_evidence:
            print(f"\n⚠️  {type_name}の証拠が登録されていません")
            return
        
        # 出力形式を選択
        print("\n出力形式を選択してください:")
        print("  1. CSV形式")
        print("  2. Excel形式 (.xlsx)")
        print("  3. キャンセル")
        
        format_choice = input("\n> ").strip()
        
        if format_choice == '3' or not format_choice:
            print("キャンセルしました")
            return
        
        # 出力ファイル名を生成
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        case_name = self.current_case.get('case_name', 'unknown').replace(' ', '_').replace('/', '_')
        type_suffix = "ko" if evidence_type == 'ko' else "otsu"
        
        if format_choice == '1':
            # CSV形式
            filename = f"evidence_list_{case_name}_{type_suffix}_{timestamp}.csv"
            self._export_to_csv(filtered_evidence, filename, evidence_type)
        elif format_choice == '2':
            # Excel形式
            filename = f"evidence_list_{case_name}_{type_suffix}_{timestamp}.xlsx"
            self._export_to_excel(filtered_evidence, filename, evidence_type)
        else:
            print("無効な選択です")
            return
    
    def _export_to_csv(self, evidence_list: List[Dict], filename: str, evidence_type: str = 'ko'):
        """CSV形式でエクスポート
        
        Args:
            evidence_list: 証拠リスト
            filename: 出力ファイル名
            evidence_type: 証拠種別 ('ko' または 'otsu')
        """
        import csv
        
        try:
            output_path = os.path.join(os.getcwd(), filename)
            
            with open(output_path, 'w', encoding='utf-8-sig', newline='') as csvfile:
                fieldnames = [
                    '証拠種別', 'ステータス', '証拠番号', '仮番号', '作成日', 
                    '分析状態', 'ファイル名', '文書種別', '作成者',
                    '宛先', '要約', 'Google DriveファイルID'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                
                # ステータスでソート（確定済み→整理済み_未確定→未分類）
                def get_organization_status(evidence):
                    """証拠の整理状態を判定"""
                    evidence_id = evidence.get('evidence_id', '')
                    evidence_number = evidence.get('evidence_number', '')
                    
                    if evidence_number and not evidence_number.startswith('甲tmp') and not evidence_number.startswith('乙tmp'):
                        return '確定済み'
                    elif evidence_id.startswith('tmp_'):
                        return '整理済み_未確定'
                    else:
                        return '未分類'
                
                status_order = {'確定済み': 1, '整理済み_未確定': 2, '未分類': 3}
                sorted_evidence = sorted(
                    evidence_list, 
                    key=lambda x: (
                        status_order.get(get_organization_status(x), 99),
                        x.get('evidence_id', ''),
                        x.get('temp_id', '')
                    )
                )
                
                type_name = "甲号証" if evidence_type == 'ko' else "乙号証"
                
                for evidence in sorted_evidence:
                    status = get_organization_status(evidence)
                    evidence_id = evidence.get('evidence_id', '')
                    temp_id = evidence.get('temp_id', '')
                    
                    # データ構造の違いを吸収してエクスポート用データを取得
                    export_data = self._get_evidence_export_data(evidence)
                    
                    gdrive_file_id = evidence.get('gdrive_file_id', '') or evidence.get('complete_metadata', {}).get('gdrive', {}).get('file_id', '')
                    
                    # 分析状態
                    analysis_status = "分析済み" if export_data['complete_description'] else "未分析"
                    
                    summary = export_data['complete_description'] or ''
                    writer.writerow({
                        '証拠種別': type_name,
                        'ステータス': status,
                        '証拠番号': evidence_id,
                        '仮番号': temp_id,
                        '作成日': export_data['creation_date'],
                        '分析状態': analysis_status,
                        'ファイル名': export_data['file_name'],
                        '文書種別': export_data['document_type'],
                        '作成者': export_data['author'],
                        '宛先': export_data['recipient'],
                        '要約': summary[:100] + '...' if len(summary) > 100 else summary,
                        'Google DriveファイルID': gdrive_file_id
                    })
            
            print(f"\n✅ CSV形式でエクスポートしました")
            print(f"   ファイル: {output_path}")
            print(f"   件数: {len(evidence_list)}件")
            
        except Exception as e:
            print(f"\n❌ エクスポートに失敗しました: {e}")
            import traceback
            traceback.print_exc()
    
    def _export_to_excel(self, evidence_list: List[Dict], filename: str, evidence_type: str = 'ko'):
        """Excel形式でエクスポート
        
        Args:
            evidence_list: 証拠リスト
            filename: 出力ファイル名
            evidence_type: 証拠種別 ('ko' または 'otsu')
        """
        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        except ImportError:
            print("\n⚠️  openpyxlがインストールされていません")
            print("以下のコマンドでインストールしてください:")
            print("  pip3 install openpyxl")
            print("\nまたは:")
            print("  pip3 install --break-system-packages openpyxl")
            return
        
        try:
            type_name = "甲号証" if evidence_type == 'ko' else "乙号証"
            output_path = os.path.join(os.getcwd(), filename)
            
            # ワークブックとシートを作成
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = f"{type_name}一覧"
            
            # ヘッダー行のスタイル
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            header_font = Font(color="FFFFFF", bold=True, size=11)
            header_alignment = Alignment(horizontal="center", vertical="center")
            border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            # ヘッダー行
            headers = [
                '証拠種別', 'ステータス', '証拠番号', '仮番号', '作成日', 
                '分析状態', 'ファイル名', '文書種別', '作成者',
                '宛先', '要約'
            ]
            
            for col_idx, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col_idx, value=header)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = header_alignment
                cell.border = border
            
            # 列幅を設定
            column_widths = {
                'A': 12,  # 証拠種別
                'B': 15,  # ステータス
                'C': 12,  # 証拠番号
                'D': 12,  # 仮番号
                'E': 12,  # 作成日
                'F': 12,  # 分析状態
                'G': 40,  # ファイル名
                'H': 15,  # 文書種別
                'I': 20,  # 作成者
                'J': 20,  # 宛先
                'K': 60   # 要約
            }
            
            for col, width in column_widths.items():
                ws.column_dimensions[col].width = width
            
            # ステータスでソート
            def get_organization_status(evidence):
                """証拠の整理状態を判定"""
                evidence_id = evidence.get('evidence_id', '')
                evidence_number = evidence.get('evidence_number', '')
                
                if evidence_number and not evidence_number.startswith('甲tmp') and not evidence_number.startswith('乙tmp'):
                    return '確定済み'
                elif evidence_id.startswith('tmp_'):
                    return '整理済み_未確定'
                else:
                    return '未分類'
            
            status_order = {'確定済み': 1, '整理済み_未確定': 2, '未分類': 3}
            sorted_evidence = sorted(
                evidence_list, 
                key=lambda x: (
                    status_order.get(get_organization_status(x), 99),
                    x.get('evidence_id', ''),
                    x.get('temp_id', '')
                )
            )
            
            # データ行
            for row_idx, evidence in enumerate(sorted_evidence, 2):
                status = get_organization_status(evidence)
                evidence_id = evidence.get('evidence_id', '')
                temp_id = evidence.get('temp_id', '')
                
                # データ構造の違いを吸収してエクスポート用データを取得
                export_data = self._get_evidence_export_data(evidence)
                
                summary = export_data['complete_description'] or ''
                
                # 分析状態
                analysis_status = "分析済み" if export_data['complete_description'] else "未分析"
                
                # セルに値を設定
                row_data = [
                    type_name,                      # 証拠種別
                    status,                         # ステータス
                    evidence_id,                    # 証拠番号
                    temp_id,                        # 仮番号
                    export_data['creation_date'],   # 作成日
                    analysis_status,                # 分析状態
                    export_data['file_name'],       # ファイル名
                    export_data['document_type'],   # 文書種別
                    export_data['author'],          # 作成者
                    export_data['recipient'],       # 宛先
                    summary                         # 要約
                ]
                
                for col_idx, value in enumerate(row_data, 1):
                    cell = ws.cell(row=row_idx, column=col_idx, value=value)
                    cell.border = border
                    cell.alignment = Alignment(vertical="top", wrap_text=True)
                    
                    # ステータスに応じて背景色を設定
                    if col_idx == 2:  # ステータス列（証拠種別の次）
                        if status == '確定済み':
                            cell.fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
                        elif status == '整理済み_未確定':
                            cell.fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
                        else:
                            cell.fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
                    
                    # 分析状態に応じて背景色を設定
                    if col_idx == 6:  # 分析状態列（証拠種別が追加されたので6列目）
                        if analysis_status == "分析済み":
                            cell.fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
                        else:
                            cell.fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
            
            # フリーズペイン（ヘッダー行を固定）
            ws.freeze_panes = "A2"
            
            # ファイルを保存
            wb.save(output_path)
            
            print(f"\n✅ Excel形式でエクスポートしました")
            print(f"   ファイル: {output_path}")
            print(f"   件数: {len(evidence_list)}件")
            
        except Exception as e:
            print(f"\n❌ エクスポートに失敗しました: {e}")
            import traceback
            traceback.print_exc()
    
    def generate_timeline_story(self):
        """時系列ストーリーの生成（拡張版）
        
        証拠を時系列順に並べて、客観的な事実の流れを生成します。
        法的判断は含まず、証拠から抽出された事実のみを時系列で整理します。
        AI機能を使用すると、より読みやすい客観的なストーリーが生成されます。
        """
        print("\n" + "="*70)
        print("  時系列ストーリーの生成（拡張版）")
        print("="*70)
        print("\n証拠を時系列順に整理して、客観的な事実の流れを生成します。")
        print("法的判断は含まず、証拠から抽出された事実のみを記載します。")
        
        # AI機能の使用確認
        print("\n【AI機能の選択】")
        print("  1. AI生成の客観的ストーリー（推奨：読みやすい）")
        print("  2. 基本的なストーリー（AI不使用）")
        print("  0. キャンセル")
        
        ai_choice = input("\n選択 (0-2): ").strip()
        
        if ai_choice == '0':
            print("\nキャンセルしました")
            return
        
        use_ai = (ai_choice == '1')
        
        try:
            # TimelineBuilderを初期化
            print("\n証拠データベースを読み込み中...")
            builder = TimelineBuilder(self.case_manager, self.current_case, use_ai=use_ai)
            
            # タイムラインを構築
            print("証拠データベースを分析中...")
            timeline_events = builder.build_timeline()
            
            if not timeline_events:
                print("\n⚠️ タイムラインを構築できませんでした。")
                print("証拠が登録されていないか、証拠に日付情報がありません。")
                return
            
            # ナラティブ（物語）を生成
            narrative_result = None
            if use_ai:
                print("\n🤖 Claude AIによる客観的ストーリーを生成中...")
                print("（高品質な分析のため、数十秒かかる場合があります）")
                narrative_result = builder.generate_objective_narrative(timeline_events)
                narrative_text = narrative_result.get("narrative", "") if isinstance(narrative_result, dict) else narrative_result
            else:
                print("\n時系列ストーリーを生成中...")
                narrative_text = builder.generate_narrative(timeline_events)
            
            # 画面に表示
            print("\n" + "="*70)
            print("【生成された時系列ストーリー】")
            print("="*70)
            print("\n" + narrative_text)
            
            # 事実と証拠の紐付けを表示（AI使用時のみ）
            if use_ai and isinstance(narrative_result, dict):
                fact_mapping = narrative_result.get("fact_evidence_mapping", [])
                if fact_mapping:
                    print("\n" + "="*70)
                    print("【事実と証拠の紐付け】")
                    print("="*70)
                    for i, fact in enumerate(fact_mapping[:5], 1):  # 最初の5件のみ表示
                        print(f"\n{i}. {fact.get('fact_description', '不明な事実')}")
                        print(f"   日付: {fact.get('date', '不明')}")
                        print(f"   裏付け証拠: {', '.join(fact.get('evidence_numbers', []))}")
                        print(f"   確実性: {fact.get('confidence', 'unknown')}")
                    
                    if len(fact_mapping) > 5:
                        print(f"\n   ... 他 {len(fact_mapping) - 5}件の事実（詳細はエクスポートファイルを参照）")
            
            # 自然言語による改善オプション（AI使用時のみ）
            if use_ai and isinstance(narrative_result, dict):
                print("\n" + "="*70)
                print("【ストーリーの改善】")
                print("自然言語で改善指示を入力できます（例：「もっと詳しく」「簡潔に」）")
                print("改善しない場合は空Enterを押してください。")
                print("="*70)
                
                user_instruction = input("\n改善指示: ").strip()
                
                if user_instruction:
                    print("\n🔄 ストーリーを改善中...")
                    improved_result = builder.refine_narrative_with_instruction(narrative_result, user_instruction)
                    
                    # 改善後のストーリーを表示
                    improved_narrative = improved_result.get("narrative", "")
                    print("\n" + "="*70)
                    print("【改善後の時系列ストーリー】")
                    print("="*70)
                    print("\n" + improved_narrative)
                    
                    # 改善結果を使用するか確認
                    use_improved = input("\n改善後のストーリーを使用しますか？ (y/n): ").strip().lower()
                    if use_improved == 'y':
                        narrative_result = improved_result
                        narrative_text = improved_narrative
                        print("✅ 改善後のストーリーを採用しました")
                    else:
                        print("元のストーリーを使用します")
            
            # エクスポート形式を選択
            print("\n" + "="*70)
            print("エクスポート形式を選択してください:")
            print("  1. JSON形式（プログラムで処理可能）")
            print("  2. Markdown形式（読みやすい）")
            print("  3. テキスト形式（シンプル）")
            print("  4. HTML形式（ブラウザで閲覧可能）")
            print("  5. すべての形式")
            print("  0. エクスポートしない")
            
            choice = input("\n選択 (0-5): ").strip()
            
            export_formats = []
            if choice == '1':
                export_formats = ['json']
            elif choice == '2':
                export_formats = ['markdown']
            elif choice == '3':
                export_formats = ['text']
            elif choice == '4':
                export_formats = ['html']
            elif choice == '5':
                export_formats = ['json', 'markdown', 'text', 'html']
            elif choice == '0':
                print("\nエクスポートをスキップしました")
                return
            else:
                print("\n無効な選択です")
                return
            
            # エクスポート
            print("\nファイルをエクスポート中...")
            for format_type in export_formats:
                output_path = builder.export_timeline(
                    timeline_events, 
                    output_format=format_type,
                    include_ai_narrative=use_ai
                )
                if output_path:
                    print(f"  ✅ {format_type.upper()}: {output_path}")
            
            print("\n✅ 時系列ストーリーの生成が完了しました！")
            
            # 証拠間の関連性分析を表示
            if use_ai:
                print("\n📊 証拠間の関連性分析:")
                relationships = builder.analyze_evidence_relationships(timeline_events)
                
                if relationships["temporal_clusters"]:
                    print("\n【時間的に近接した証拠グループ】")
                    for i, cluster in enumerate(relationships["temporal_clusters"], 1):
                        print(f"  {i}. {cluster['period']}: {cluster['evidence_count']}件")
                        print(f"     証拠: {', '.join(cluster['evidence_numbers'])}")
                
                if relationships["chronological_gaps"]:
                    print("\n【時系列上のギャップ】")
                    for gap in relationships["chronological_gaps"]:
                        print(f"  - {gap['description']}")
            
        except Exception as e:
            print(f"\n❌ エラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
    
    def manage_client_statements(self):
        """依頼者発言・メモの管理"""
        from timeline_builder import TimelineBuilder
        
        print("\n" + "="*70)
        print("  依頼者発言・メモの管理")
        print("="*70)
        print("\n依頼者からのヒアリング内容、発言、メモなどを記録します。")
        print("これらは時系列ストーリー生成時に証拠と統合されます。")
        
        # TimelineBuilderを初期化
        builder = TimelineBuilder(self.case_manager, self.current_case, use_ai=False)
        
        while True:
            print("\n" + "-"*70)
            print("【依頼者情報管理メニュー】")
            print("\n【日付指定あり（特定の出来事）】")
            print("  1. 依頼者発言を追加")
            print("  2. 登録済み発言を表示")
            print("  3. ファイルから一括インポート（テキスト形式）")
            print("\n【包括的情報（日付なし、複数事実にわたる）】🆕")
            print("  4. 包括的な発言・メモを追加")
            print("  5. 登録済み包括的発言を表示")
            print("\n  0. メインメニューに戻る")
            print("-"*70)
            
            choice = input("\n選択 (0-5): ").strip()
            
            if choice == '1':
                # 依頼者発言を追加
                print("\n【依頼者発言の追加】")
                print("発言または出来事に関する日付を入力してください（YYYY-MM-DD形式）")
                print("例: 2023-05-15")
                date = input("日付: ").strip()
                
                if not date:
                    print("❌ 日付を入力してください")
                    continue
                
                print("\n発言内容またはメモを入力してください（複数行可、終了は空行）")
                statement_lines = []
                while True:
                    line = input()
                    if not line:
                        break
                    statement_lines.append(line)
                
                statement = "\n".join(statement_lines)
                
                if not statement:
                    print("❌ 発言内容を入力してください")
                    continue
                
                print("\n状況説明や背景情報を入力してください（省略可、終了は空行）")
                context_lines = []
                while True:
                    line = input()
                    if not line:
                        break
                    context_lines.append(line)
                
                context = "\n".join(context_lines) if context_lines else None
                
                # 発言を追加
                if builder.add_client_statement(date, statement, context):
                    print("\n✅ 依頼者発言を追加しました")
                else:
                    print("\n❌ 発言の追加に失敗しました")
            
            elif choice == '2':
                # 登録済み発言を表示
                statements = builder._load_client_statements()
                
                if not statements:
                    print("\n登録されている発言はありません")
                    continue
                
                print(f"\n【登録済み発言一覧】（{len(statements)}件）")
                print("-"*70)
                
                for i, stmt in enumerate(statements, 1):
                    print(f"\n{i}. ID: {stmt.get('statement_id', '不明')}")
                    print(f"   日付: {stmt.get('date', '不明')}")
                    print(f"   発言: {stmt.get('statement', '')[:100]}...")
                    if stmt.get('context'):
                        print(f"   状況: {stmt.get('context', '')[:100]}...")
                    print(f"   登録日時: {stmt.get('added_at', '不明')}")
            
            elif choice == '3':
                # ファイルから一括インポート
                print("\n【ファイルから一括インポート】")
                print("テキストファイルのパスを入力してください")
                print("フォーマット例:")
                print("  [2023-05-15]")
                print("  依頼者の発言内容")
                print("  複数行可能")
                print("  ")
                print("  [2023-06-20]")
                print("  別の発言...")
                
                file_path = input("\nファイルパス: ").strip()
                
                if not file_path or not os.path.exists(file_path):
                    print("❌ ファイルが見つかりません")
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 簡単なパース: [YYYY-MM-DD] で区切る
                    import re
                    entries = re.split(r'\[(\d{4}-\d{2}-\d{2})\]', content)
                    
                    added_count = 0
                    for i in range(1, len(entries), 2):
                        if i + 1 < len(entries):
                            date = entries[i].strip()
                            statement = entries[i + 1].strip()
                            
                            if date and statement:
                                if builder.add_client_statement(date, statement, None):
                                    added_count += 1
                    
                    print(f"\n✅ {added_count}件の発言を追加しました")
                    
                except Exception as e:
                    print(f"\n❌ インポートに失敗しました: {e}")
            
            elif choice == '4':
                # 包括的な発言・メモを追加
                print("\n【包括的な発言・メモの追加】")
                print("※ 日付指定なし、複数の事実にわたる全体的な情報を記録します")
                print("※ AIが時系列ストーリー生成時に全体の文脈として活用します\n")
                
                print("タイトルまたは概要を入力してください")
                print("例: 事件の全体的な経緯、当事者間の関係性、背景情報")
                title = input("タイトル: ").strip()
                
                if not title:
                    print("❌ タイトルを入力してください")
                    continue
                
                print("\nカテゴリを選択してください")
                print("  1. 事件の背景")
                print("  2. 人物関係")
                print("  3. 全体的な経緯")
                print("  4. その他")
                cat_choice = input("選択 (1-4): ").strip()
                
                category_map = {
                    '1': '事件の背景',
                    '2': '人物関係',
                    '3': '全体的な経緯',
                    '4': 'その他'
                }
                category = category_map.get(cat_choice, 'その他')
                
                print(f"\n{title} の詳細内容を入力してください（複数行可、終了は空行）")
                content_lines = []
                while True:
                    line = input()
                    if not line:
                        break
                    content_lines.append(line)
                
                content = "\n".join(content_lines)
                
                if not content:
                    print("❌ 内容を入力してください")
                    continue
                
                # 包括的発言を追加
                if builder.add_general_context(title, content, category):
                    print("\n✅ 包括的な発言・メモを追加しました")
                    print("   時系列ストーリー生成時にAIが自動的に考慮します")
                else:
                    print("\n❌ 追加に失敗しました")
            
            elif choice == '5':
                # 登録済み包括的発言を表示
                contexts = builder._load_general_context()
                
                if not contexts:
                    print("\n登録されている包括的発言はありません")
                    continue
                
                print(f"\n【登録済み包括的発言一覧】（{len(contexts)}件）")
                print("-"*70)
                
                for i, ctx in enumerate(contexts, 1):
                    print(f"\n{i}. ID: {ctx.get('context_id', '不明')}")
                    print(f"   タイトル: {ctx.get('title', '不明')}")
                    print(f"   カテゴリ: {ctx.get('category', '不明')}")
                    print(f"   内容: {ctx.get('content', '')[:150]}...")
                    print(f"   登録日時: {ctx.get('added_at', '不明')}")
            
            elif choice == '0':
                # メインメニューに戻る
                break
            
            else:
                print("\n❌ 無効な選択です")
    
    def run(self):
        """メイン実行ループ"""
        # 最初に事件を選択
        if not self.select_case():
            print("\n❌ 事件が選択されていないため終了します")
            return
        
        # メインループ
        while True:
            self.display_main_menu()
            choice = input("\n選択 (0-9): ").strip()
            
            if choice == '1':
                # 証拠整理（未分類フォルダから整理済み_未確定へ）
                try:
                    # 証拠種別を選択
                    evidence_type = self.select_evidence_type()
                    if evidence_type:
                        organizer = EvidenceOrganizer(self.case_manager, self.current_case)
                        organizer.interactive_organize(evidence_type=evidence_type)
                except Exception as e:
                    print(f"\n❌ エラーが発生しました: {str(e)}")
                    import traceback
                    traceback.print_exc()
                        
            elif choice == '2':
                # 証拠分析（番号指定・範囲指定に対応）
                # 証拠種別を選択
                evidence_type = self.select_evidence_type()
                if evidence_type:
                    evidence_numbers = self.get_evidence_number_input(evidence_type)
                    if evidence_numbers:
                        # 複数件の場合は確認
                        if len(evidence_numbers) > 1:
                            type_name = "甲号証" if evidence_type == 'ko' else "乙号証"
                            print(f"\n処理対象 [{type_name}]: {', '.join(evidence_numbers)}")
                            confirm = input("処理を開始しますか？ (y/n): ").strip().lower()
                            if confirm != 'y':
                                continue
                        
                        # 分析実行
                        for evidence_number in evidence_numbers:
                            gdrive_file_info = self._get_gdrive_info_from_database(evidence_number, evidence_type)
                            self.process_evidence(evidence_number, gdrive_file_info, evidence_type)
                        
            elif choice == '3':
                # AI対話形式で分析内容を改善
                try:
                    # 証拠種別を選択
                    evidence_type = self.select_evidence_type()
                    if evidence_type:
                        self.edit_evidence_with_ai(evidence_type)
                except Exception as e:
                    print(f"\nエラー: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    
            elif choice == '4':
                # 日付順に並び替えて確定（整理済み_未確定 → 甲号証/乙号証）
                try:
                    # 証拠種別を選択
                    evidence_type = self.select_evidence_type()
                    if evidence_type:
                        self.analyze_and_sort_pending_evidence(evidence_type)
                except Exception as e:
                    print(f"\nエラー: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    
            elif choice == '5':
                # 証拠分析一覧を表示
                try:
                    # 証拠種別を選択
                    evidence_type = self.select_evidence_type()
                    if evidence_type:
                        self.show_evidence_list(evidence_type)
                except Exception as e:
                    print(f"\nエラー: {str(e)}")
                    import traceback
                    traceback.print_exc()
            
            elif choice == '6':
                # 証拠一覧をエクスポート
                try:
                    # 証拠種別を選択
                    evidence_type = self.select_evidence_type()
                    if evidence_type:
                        self.export_evidence_list(evidence_type)
                except Exception as e:
                    print(f"\nエラー: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    
            elif choice == '7':
                # 時系列ストーリーの生成
                try:
                    self.generate_timeline_story()
                except Exception as e:
                    print(f"\nエラー: {str(e)}")
                    import traceback
                    traceback.print_exc()
                
            elif choice == '8':
                # 依頼者発言・メモの管理
                try:
                    self.manage_client_statements()
                except Exception as e:
                    print(f"\nエラー: {str(e)}")
                    import traceback
                    traceback.print_exc()
                
            elif choice == '9':
                # database.jsonの状態確認
                self.show_database_status()
                
            elif choice == '10':
                # 事件を切り替え
                if self.select_case():
                    print("\n✅ 事件を切り替えました")
                    
            elif choice == '0':
                # 終了
                print("\nPhase1_Evidence Analysis Systemを終了します")
                break
                
            else:
                print("\nエラー: 無効な選択です。0-10を入力してください。")
            
            input("\nEnterキーを押して続行...")


def main():
    """メイン関数"""
    print("\n" + "="*70)
    print("  Phase1_Evidence Analysis System（マルチ事件対応版）起動中...")
    print("="*70)
    
    # 環境チェック
    if not os.getenv('OPENAI_API_KEY'):
        print("\n❌ エラー: OPENAI_API_KEYが設定されていません")
        print("\n設定方法:")
        print("  export OPENAI_API_KEY='sk-your-api-key'")
        print("\nまたは .env ファイルに記載:")
        print("  OPENAI_API_KEY=sk-your-api-key")
        return
    
    # Google認証チェック
    if not os.path.exists('credentials.json'):
        print("\n⚠️ 警告: credentials.jsonが見つかりません")
        print("Google Drive API機能が使用できません")
        print("\nGoogle Cloud Consoleから credentials.json をダウンロードしてください")
        response = input("\n続行しますか？ (y/n): ").strip().lower()
        if response != 'y':
            return
    
    # global_config.py チェック
    if not hasattr(gconfig, 'SHARED_DRIVE_ROOT_ID') or not gconfig.SHARED_DRIVE_ROOT_ID:
        print("\n❌ エラー: global_config.py で SHARED_DRIVE_ROOT_ID が設定されていません")
        print("\nglobal_config.py を開いて、大元の共有ドライブIDを設定してください:")
        print("  SHARED_DRIVE_ROOT_ID = 'your-shared-drive-id'")
        return
    
    print(f"\n✅ 共有ドライブID: {gconfig.SHARED_DRIVE_ROOT_ID}")
    
    # 実行
    runner = Phase1MultiRunner()
    runner.run()


if __name__ == "__main__":
    main()

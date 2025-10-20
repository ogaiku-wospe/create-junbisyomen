#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1完全版システム - マルチ事件対応版

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
    from case_manager import CaseManager
    from evidence_organizer import EvidenceOrganizer
    from gdrive_database_manager import GDriveDatabaseManager, create_database_manager
    # 既存のモジュール（事件固有の処理）
    from metadata_extractor import MetadataExtractor
    from file_processor import FileProcessor
    from ai_analyzer_complete import AIAnalyzerComplete
except ImportError as e:
    print(f"❌ エラー: モジュールのインポートに失敗しました: {e}")
    print("\n必要なファイル:")
    print("  - global_config.py")
    print("  - case_manager.py")
    print("  - evidence_organizer.py")
    print("  - metadata_extractor.py")
    print("  - file_processor.py")
    print("  - ai_analyzer_complete.py")
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
    
    def select_case(self) -> bool:
        """事件を選択または新規作成
        
        Returns:
            選択成功: True, キャンセル: False
        """
        print("\n" + "="*70)
        print("  Phase 1完全版システム - 事件選択")
        print("="*70)
        
        # 事件を検出
        cases = self.case_manager.detect_cases()
        
        if not cases:
            print("\n📋 事件が見つかりませんでした。")
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
            logger.warning("⚠️ データベースマネージャーの初期化に失敗しました")
        
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
            print("\n📝 事件情報を入力してください")
            
            case_id = input("\n事件ID（例: 2025_001）: ").strip()
            if not case_id:
                print("❌ 事件IDは必須です")
                return False
            
            case_name = input("事件名（例: 損害賠償請求事件）: ").strip()
            if not case_name:
                print("❌ 事件名は必須です")
                return False
            
            case_number = input("事件番号（例: 令和7年(ワ)第1号）[省略可]: ").strip()
            court = input("裁判所（例: 東京地方裁判所）[省略可]: ").strip()
            plaintiff = input("原告（例: 山田太郎）[省略可]: ").strip()
            defendant = input("被告（例: 株式会社〇〇）[省略可]: ").strip()
            
            # 確認
            print("\n📋 入力内容の確認:")
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
                print("❌ キャンセルしました")
                return False
            
            # フォルダ作成
            print("\n📁 フォルダを作成中...")
            
            service = self.case_manager.get_google_drive_service()
            if not service:
                print("❌ Google Drive認証に失敗しました")
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
            
            # 甲号証フォルダを作成
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
            
            print(f"  ✅ 甲号証フォルダ作成")
            
            # 乙号証フォルダを作成
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
            
            print(f"  ✅ 乙号証フォルダ作成")
            
            # 未分類フォルダを作成
            unclassified_folder_metadata = {
                'name': '未分類',
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [case_folder_id]
            }
            
            unclassified_folder = service.files().create(
                body=unclassified_folder_metadata,
                supportsAllDrives=True,
                fields='id, name'
            ).execute()
            
            print(f"  ✅ 未分類フォルダ作成")
            
            # 整理済み_未確定フォルダを作成
            pending_folder_metadata = {
                'name': '整理済み_未確定',
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [case_folder_id]
            }
            
            pending_folder = service.files().create(
                body=pending_folder_metadata,
                supportsAllDrives=True,
                fields='id, name'
            ).execute()
            
            print(f"  ✅ 整理済み_未確定フォルダ作成")
            
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
            
            # データベースマネージャーを初期化
            self.db_manager = create_database_manager(self.case_manager, self.current_case)
            if not self.db_manager:
                logger.warning("⚠️ データベースマネージャーの初期化に失敗しました")
            
            # 事件設定ファイルを生成
            self.case_manager.generate_case_config(self.current_case, "current_case.json")
            
            print("\n✅ 新規事件を作成しました")
            print(f"📁 フォルダURL: {case_folder.get('webViewLink', 'N/A')}")
            
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
            
            logger.info(f"✅ database.jsonをGoogle Driveにアップロード: {file['id']}")
            return file['id']
            
        except Exception as e:
            logger.error(f"❌ database.jsonアップロード失敗: {e}")
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
                logger.warning("⚠️ Google Driveにdatabase.jsonが見つかりません")
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
            
            logger.info(f"✅ database.jsonをGoogle Driveからダウンロード")
            return database
            
        except Exception as e:
            logger.error(f"❌ database.jsonダウンロード失敗: {e}")
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
                logger.info(f"✅ Google Drive上のdatabase.jsonを更新")
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
                logger.info(f"✅ database.jsonをGoogle Driveに新規作成")
            
            # 一時ファイルを削除
            os.remove(tmp_path)
            return True
            
        except Exception as e:
            logger.error(f"❌ database.json更新失敗: {e}")
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
            logger.info(f"✅ Google Driveにdatabase.jsonを保存しました")
        else:
            logger.error(f"❌ Google Drive保存失敗")
            raise Exception("database.jsonの保存に失敗しました")
    
    def display_main_menu(self):
        """メインメニュー表示"""
        if not self.current_case:
            print("\n❌ エラー: 事件が選択されていません")
            return
        
        print("\n" + "="*70)
        print(f"  Phase 1完全版システム - 証拠管理")
        print(f"  📁 事件: {self.current_case['case_name']}")
        print("="*70)
        print("\n【実行モード】")
        print("  1. 🆕 証拠整理（未分類フォルダから自動整理）")
        print("  2. 証拠番号を指定して分析（例: ko70）")
        print("  3. 範囲指定して分析（例: ko70-73）")
        print("  4. Google Driveから自動検出して分析")
        print("  5. database.jsonの状態確認")
        print("  6. 事件を切り替え")
        print("  7. 📋 並び替え・確定（整理済み_未確定 → 甲号証）")
        print("  8. 終了")
        print("-"*70)
    
    def get_evidence_number_input(self) -> Optional[List[str]]:
        """証拠番号の入力取得
        
        Examples:
            ko70-73      -> ['ko70', 'ko71', 'ko72', 'ko73']
            ko001-005    -> ['ko001', 'ko002', 'ko003', 'ko004', 'ko005']
            tmp_001-011  -> ['tmp_001', 'tmp_002', ..., 'tmp_011']
        """
        user_input = input("\n証拠番号を入力してください（例: ko70 または ko70-73, tmp_001-011）: ").strip()
        
        if not user_input:
            return None
        
        # 範囲指定の処理（例: ko70-73, tmp_001-011）
        if '-' in user_input and user_input.count('-') == 1:
            try:
                # 範囲の開始と終了を分離
                start_str, end_str = user_input.split('-')
                
                # 開始番号から prefix と数字部分を分離
                # 例: "tmp_001" -> prefix="tmp_", start_num="001"
                # 例: "ko70" -> prefix="ko", start_num="70"
                import re
                match = re.match(r'^(.+?)(\d+)$', start_str)
                if not match:
                    logger.error("❌ 範囲指定の形式が正しくありません（開始番号）")
                    return None
                
                prefix = match.group(1)  # "tmp_" or "ko"
                start_num_str = match.group(2)  # "001" or "70"
                
                # 数値変換
                start_num = int(start_num_str)
                end_num = int(end_str)
                
                if start_num > end_num:
                    logger.error("❌ 開始番号は終了番号以下でなければなりません")
                    return None
                
                # ゼロ埋めの桁数を判定（開始番号の桁数を維持）
                width = len(start_num_str)
                
                # 範囲内の証拠番号リストを生成
                # 例: tmp_001, tmp_002, ..., tmp_011
                return [f"{prefix}{i:0{width}d}" for i in range(start_num, end_num + 1)]
                
            except ValueError as e:
                logger.error(f"❌ 範囲指定の形式が正しくありません: {e}")
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
            logger.error("❌ 甲号証フォルダIDが設定されていません")
            return []
        
        print("\n🔍 Google Driveから証拠ファイルを検索中...")
        
        service = self.case_manager.get_google_drive_service()
        if not service:
            logger.error("❌ Google Drive認証に失敗しました")
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
            print(f"✅ {len(files)}件の証拠ファイルを検出しました")
            
            return files
            
        except Exception as e:
            logger.error(f"❌ Google Drive検索エラー: {e}")
            return []
    
    def _get_gdrive_info_from_database(self, evidence_number: str) -> Optional[Dict]:
        """database.jsonから証拠のGoogle Drive情報を取得
        
        Args:
            evidence_number: 証拠番号（例: ko001, 甲001）
        
        Returns:
            Google Driveファイル情報（見つからない場合はNone）
        """
        try:
            database = self.load_database()
            
            # 証拠番号を正規化（ko001, 甲001 → ko001で統一）
            if evidence_number.startswith('甲'):
                evidence_number = f"ko{evidence_number[1:]}"
            elif evidence_number.startswith('乙'):
                evidence_number = f"otsu{evidence_number[1:]}"
            
            # データベースから証拠を検索
            for evidence in database.get('evidence', []):
                if evidence.get('evidence_id') == evidence_number:
                    # Google DriveファイルIDを取得
                    gdrive_file_id = evidence.get('gdrive_file_id')
                    if not gdrive_file_id:
                        logger.warning(f"⚠️ 証拠 {evidence_number} のGoogle DriveファイルIDが見つかりません")
                        return None
                    
                    # Google Drive APIでファイル情報を取得
                    service = self.case_manager.get_google_drive_service()
                    if not service:
                        logger.error("❌ Google Drive認証に失敗しました")
                        return None
                    
                    file_info = service.files().get(
                        fileId=gdrive_file_id,
                        supportsAllDrives=True,
                        fields='id, name, mimeType, size, createdTime, modifiedTime, webViewLink, webContentLink'
                    ).execute()
                    
                    return file_info
            
            logger.warning(f"⚠️ 証拠 {evidence_number} がdatabase.jsonに見つかりません")
            return None
            
        except Exception as e:
            logger.error(f"❌ database.json読み込みエラー: {e}")
            return None
    
    def process_evidence(self, evidence_number: str, gdrive_file_info: Dict = None) -> bool:
        """証拠の処理（完全版）
        
        Args:
            evidence_number: 証拠番号（例: ko70）
            gdrive_file_info: Google Driveファイル情報（オプション）
            
        Returns:
            処理成功: True, 失敗: False
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"  証拠 {evidence_number} の処理開始")
        logger.info(f"{'='*70}")
        
        try:
            # 1. ファイルパスの取得（Google Driveから）
            if gdrive_file_info:
                logger.info(f"📁 ファイル: {gdrive_file_info['name']}")
                logger.info(f"🔗 URL: {gdrive_file_info.get('webViewLink', 'N/A')}")
                
                # Google Driveからダウンロード
                file_path = self._download_file_from_gdrive(gdrive_file_info)
                if not file_path:
                    logger.error("❌ ファイルのダウンロードに失敗しました")
                    return False
            else:
                # ローカルファイルパスを使用
                logger.warning("⚠️ Google Drive情報がありません。ローカルファイルを探します。")
                file_path = f"/tmp/{evidence_number}_sample.pdf"
                if not os.path.exists(file_path):
                    logger.error(f"❌ ファイルが見つかりません: {file_path}")
                    return False
            
            # 2. メタデータ抽出
            logger.info(f"📊 メタデータを抽出中...")
            metadata = self.metadata_extractor.extract_complete_metadata(
                file_path,
                gdrive_file_info=gdrive_file_info
            )
            logger.info(f"  - ファイルハッシュ(SHA-256): {metadata['hashes']['sha256'][:16]}...")
            logger.info(f"  - ファイルサイズ: {metadata['basic']['file_size_human']}")
            
            # 3. ファイル処理
            logger.info(f"🔧 ファイルを処理中...")
            file_type = self._detect_file_type(file_path)
            processed_data = self.file_processor.process_file(file_path, file_type)
            logger.info(f"  - ファイル形式: {processed_data['file_type']}")
            
            # 4. AI分析（GPT-4o Vision）
            logger.info(f"🤖 AI分析を実行中（GPT-4o Vision）...")
            analysis_result = self.ai_analyzer.analyze_evidence_complete(
                evidence_id=evidence_number,
                file_path=file_path,
                file_type=file_type,
                gdrive_file_info=gdrive_file_info,
                case_info=self.current_case
            )
            
            # 5. 品質評価
            quality = analysis_result.get('quality_assessment', {})
            logger.info(f"📈 品質評価:")
            logger.info(f"  - 完全性スコア: {quality.get('completeness_score', 0):.1%}")
            logger.info(f"  - 信頼度スコア: {quality.get('confidence_score', 0):.1%}")
            logger.info(f"  - 言語化レベル: {quality.get('verbalization_level', 0)}")
            
            # 6. database.jsonに追加
            logger.info(f"💾 database.jsonに保存中...")
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
            existing_index = next(
                (i for i, e in enumerate(database["evidence"]) 
                 if e.get("evidence_id") == evidence_number),
                None
            )
            
            if existing_index is not None:
                database["evidence"][existing_index] = evidence_entry
                logger.info(f"  ✅ 既存エントリを更新しました")
            else:
                database["evidence"].append(evidence_entry)
                logger.info(f"  ✅ 新規エントリを追加しました")
            
            self.save_database(database)
            
            logger.info(f"\n✅ 証拠 {evidence_number} の処理が完了しました！")
            return True
            
        except Exception as e:
            logger.error(f"❌ エラーが発生しました: {e}", exc_info=True)
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
            logger.error(f"❌ ダウンロードエラー: {e}")
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
            print("\n📋 未確定の証拠はありません")
            return
        
        print(f"\n📋 未確定証拠: {len(pending_evidence)}件")
        print("\n現在の順序:")
        for idx, evidence in enumerate(pending_evidence, 1):
            print(f"  [{idx}] {evidence['temp_id']} - {evidence['original_filename']}")
            print(f"      種別: {evidence['evidence_type']}, 説明: {evidence['description']}")
        
        print("\n【操作】")
        print("  1. この順序で確定（甲001, 甲002...）")
        print("  2. 順序を変更")
        print("  0. キャンセル")
        
        choice = input("\n選択してください (1-2, 0): ").strip()
        
        if choice == '0':
            print("❌ キャンセルしました")
            return
        
        elif choice == '2':
            # 順序変更
            print("\n📝 順序を変更します")
            print("   例: 1,3,2,4 → 1番目,3番目,2番目,4番目の順")
            new_order_input = input(f"新しい順序を入力 (1-{len(pending_evidence)}をカンマ区切り): ").strip()
            
            try:
                new_order = [int(x.strip()) for x in new_order_input.split(',')]
                if len(new_order) != len(pending_evidence) or set(new_order) != set(range(1, len(pending_evidence) + 1)):
                    print("❌ 無効な順序です")
                    return
                
                # 並び替え
                pending_evidence = [pending_evidence[i-1] for i in new_order]
                
                print("\n✅ 並び替え後:")
                for idx, evidence in enumerate(pending_evidence, 1):
                    print(f"  [{idx}] {evidence['temp_id']} - {evidence['original_filename']}")
                
            except ValueError:
                print("❌ 入力エラー")
                return
        
        # 確定確認
        confirm = input(f"\nこの順序で確定しますか？ (y/n): ").strip().lower()
        if confirm != 'y':
            print("❌ キャンセルしました")
            return
        
        # 確定処理
        print("\n📥 証拠を確定中...")
        service = self.case_manager.get_google_drive_service()
        if not service:
            print("❌ Google Drive認証に失敗しました")
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
                # tmp_001_ の部分を ko001_ に置換
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
        print(f"✅ 確定完了: {success_count}/{len(pending_evidence)}件")
        print("="*70)
    
    def show_database_status(self):
        """database.jsonの状態表示"""
        database = self.load_database()
        
        print("\n" + "="*70)
        print("  database.json 状態確認")
        print("="*70)
        
        print(f"\n📁 事件情報:")
        metadata = database.get('metadata', {})
        print(f"  - 事件ID: {metadata.get('case_id', 'N/A')}")
        print(f"  - 事件名: {metadata.get('case_name', 'N/A')}")
        print(f"  - データベースバージョン: {metadata.get('database_version', database.get('version', 'N/A'))}")
        print(f"  - 最終更新: {metadata.get('last_updated', 'N/A')}")
        
        print(f"\n📊 証拠統計:")
        print(f"  - 総証拠数: {len(database['evidence'])}")
        
        completed = [e for e in database['evidence'] if e.get('status') == 'completed']
        print(f"  - 完了: {len(completed)}")
        
        pending = [e for e in database['evidence'] if e.get('status') == 'pending']
        print(f"  - 未確定: {len(pending)}")
        
        in_progress = [e for e in database['evidence'] if e.get('status') == 'in_progress']
        print(f"  - 処理中: {len(in_progress)}")
        
        if database['evidence']:
            print(f"\n📝 証拠一覧:")
            for evidence in database['evidence'][:20]:  # 最大20件表示
                status = evidence.get('status', 'unknown')
                if status == 'completed':
                    status_icon = "✅"
                    evidence_id = evidence.get('evidence_number', evidence.get('evidence_id', 'N/A'))
                elif status == 'pending':
                    status_icon = "⏳"
                    evidence_id = evidence.get('temp_id', 'N/A')
                else:
                    status_icon = "❓"
                    evidence_id = 'N/A'
                
                print(f"  {status_icon} {evidence_id} - {evidence.get('original_filename', 'N/A')}")
            
            if len(database['evidence']) > 20:
                print(f"  ... 他 {len(database['evidence']) - 20}件")
        
        print("\n" + "="*70)
    
    def run(self):
        """メイン実行ループ"""
        # 最初に事件を選択
        if not self.select_case():
            print("\n❌ 事件が選択されていないため終了します")
            return
        
        # メインループ
        while True:
            self.display_main_menu()
            choice = input("\n選択してください (1-7): ").strip()
            
            if choice == '1':
                # 🆕 証拠整理（未分類フォルダから自動整理）
                try:
                    organizer = EvidenceOrganizer(self.case_manager, self.current_case)
                    organizer.interactive_organize()
                except Exception as e:
                    print(f"\n❌ エラーが発生しました: {str(e)}")
                    import traceback
                    traceback.print_exc()
                        
            elif choice == '2':
                # 証拠番号を指定して分析
                evidence_numbers = self.get_evidence_number_input()
                if evidence_numbers:
                    for evidence_number in evidence_numbers:
                        gdrive_file_info = self._get_gdrive_info_from_database(evidence_number)
                        self.process_evidence(evidence_number, gdrive_file_info)
                        
            elif choice == '3':
                # 範囲指定して分析
                evidence_numbers = self.get_evidence_number_input()
                if evidence_numbers:
                    print(f"\n📋 処理対象: {', '.join(evidence_numbers)}")
                    confirm = input("処理を開始しますか？ (y/n): ").strip().lower()
                    if confirm == 'y':
                        for evidence_number in evidence_numbers:
                            gdrive_file_info = self._get_gdrive_info_from_database(evidence_number)
                            self.process_evidence(evidence_number, gdrive_file_info)
                            
            elif choice == '4':
                # Google Driveから自動検出して分析
                files = self.search_evidence_files_from_gdrive()
                if files:
                    print(f"\n📋 検出されたファイル: {len(files)}件")
                    for idx, file_info in enumerate(files[:10], 1):
                        print(f"  {idx}. {file_info['name']}")
                    
                    if len(files) > 10:
                        print(f"  ... 他 {len(files) - 10}件")
                    
                    print("\n⚠️ 自動分析機能は実装中です")
                    
            elif choice == '5':
                # database.jsonの状態確認
                self.show_database_status()
                
            elif choice == '6':
                # 事件を切り替え
                if self.select_case():
                    print("\n✅ 事件を切り替えました")
                    
            elif choice == '7':
                # 並び替え・確定
                self.finalize_pending_evidence()
                    
            elif choice == '8':
                # 終了
                print("\n👋 Phase 1完全版システムを終了します")
                break
                
            else:
                print("\n❌ 無効な選択です。1-8の番号を入力してください。")
            
            input("\nEnterキーを押して続行...")


def main():
    """メイン関数"""
    print("\n" + "="*70)
    print("  Phase 1完全版システム（マルチ事件対応版）起動中...")
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

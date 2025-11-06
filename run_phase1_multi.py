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

# プロジェクトルートをPythonパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

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
        print("  7. CSV編集内容をdatabase.jsonに反映")
        print("  8. 時系列ストーリーの生成（証拠を時系列で整理）")
        print("  9. 依頼者発言・メモの管理")
        print("\n【システム管理】")
        print("  10. database.jsonの状態確認")
        print("  11. 事件を切り替え")
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
        """証拠番号の入力取得（改善版）
        
        Args:
            evidence_type: 'ko' または 'otsu'
        
        Examples:
            ユーザー入力: 001      -> ['tmp_ko_001'] （甲号証の場合）
            ユーザー入力: 070-073  -> ['tmp_ko_070', 'tmp_ko_071', 'tmp_ko_072', 'tmp_ko_073']
            ユーザー入力: 001-011  -> ['tmp_ko_001', 'tmp_ko_002', ..., 'tmp_ko_011']
        """
        # 証拠種別に応じたプレフィックスを取得
        prefix = gconfig.TEMP_PREFIX_MAP.get(evidence_type, 'tmp_ko_')
        evidence_type_name = gconfig.EVIDENCE_TYPE_DISPLAY_NAMES.get(evidence_type, '甲号証')
        
        print(f"\n証拠番号の入力（{evidence_type_name}）")
        print(f"  単一指定: 001, 020")
        print(f"  範囲指定: 001-011, 020-030")
        print(f"  ※ 自動的に '{prefix}' が付加されます")
        print(f"  キャンセル: 空Enter")
        user_input = input("\n> ").strip()
        
        if not user_input:
            return None
        
        # 範囲指定の処理（例: 001-011, 020-030）
        if '-' in user_input and user_input.count('-') == 1:
            try:
                # 範囲の開始と終了を分離
                start_str, end_str = user_input.split('-')
                
                # 数値変換（数字のみを想定）
                start_num = int(start_str)
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
                width = len(start_str)
                
                # 範囲内の証拠番号リストを生成（プレフィックスを自動付加）
                # 例: tmp_ko_001, tmp_ko_002, ..., tmp_ko_011
                evidence_numbers = [f"{prefix}{i:0{width}d}" for i in range(start_num, end_num + 1)]
                
                print(f"\n✅ 生成された証拠番号: {evidence_numbers[0]} 〜 {evidence_numbers[-1]} ({len(evidence_numbers)}件)")
                return evidence_numbers
                
            except ValueError as e:
                logger.error(f"範囲指定の形式が正しくありません: {e}")
                print("\nエラー: 範囲指定の形式が正しくありません")
                print("  正しい例: 001-011, 020-030（数字のみ）")
                print(f"  詳細: {e}")
                return None
        else:
            # 単一証拠番号（数字のみの入力を想定）
            try:
                # 数字部分のみかチェック
                num = int(user_input)
                width = len(user_input)
                evidence_number = f"{prefix}{num:0{width}d}"
                print(f"\n✅ 生成された証拠番号: {evidence_number}")
                return [evidence_number]
            except ValueError:
                # 数字でない場合はそのまま返す（後方互換性）
                logger.warning(f"旧形式の証拠番号入力: {user_input}")
                print(f"\n⚠️ 旧形式の証拠番号として処理: {user_input}")
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
        
        # エクスポートモード選択
        print("\nエクスポートモードを選択してください:")
        print("  1. 標準モード（主要フィールドのみ、編集しやすい）")
        print("  2. 拡張モード（AI分析・OCR結果を個別列に展開、自然言語編集可能）← 推奨")
        print("  3. 完全モード（database.json全データをJSON列で出力、上級者向け）")
        print("  4. キャンセル")
        
        mode_choice = input("\n> ").strip()
        
        if mode_choice == '4' or not mode_choice:
            print("キャンセルしました")
            return
        
        extended_mode = (mode_choice == '2')
        full_data = (mode_choice == '3')
        
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
        
        if extended_mode:
            mode_suffix = "_extended"
        elif full_data:
            mode_suffix = "_full"
        else:
            mode_suffix = ""
        
        if format_choice == '1':
            # CSV形式
            filename = f"evidence_list_{case_name}_{type_suffix}{mode_suffix}_{timestamp}.csv"
            self._export_to_csv(filtered_evidence, filename, evidence_type, full_data=full_data, extended_mode=extended_mode)
        elif format_choice == '2':
            # Excel形式
            filename = f"evidence_list_{case_name}_{type_suffix}{mode_suffix}_{timestamp}.xlsx"
            self._export_to_excel(filtered_evidence, filename, evidence_type, full_data=full_data, extended_mode=extended_mode)
        else:
            print("無効な選択です")
            return
    
    def _apply_extended_fields(self, evidence: Dict, extended_data: Dict):
        """拡張モードの自然言語フィールドをdatabase.json構造に反映
        
        Args:
            evidence: 更新対象の証拠オブジェクト
            extended_data: CSVから読み込んだ拡張フィールドの辞書
        """
        # complete_metadata構造を確保
        if 'complete_metadata' not in evidence:
            evidence['complete_metadata'] = {}
        metadata = evidence['complete_metadata']
        
        if 'basic' not in metadata:
            metadata['basic'] = {}
        basic = metadata['basic']
        
        if 'format_specs' not in metadata:
            metadata['format_specs'] = {}
        format_spec = metadata['format_specs']
        
        # phase1_complete_analysis構造を確保
        if 'phase1_complete_analysis' not in evidence:
            evidence['phase1_complete_analysis'] = {}
        analysis = evidence['phase1_complete_analysis']
        
        if 'ai_analysis' not in analysis:
            analysis['ai_analysis'] = {}
        ai_analysis = analysis['ai_analysis']
        
        if 'file_processing_result' not in analysis:
            analysis['file_processing_result'] = {}
        if 'content' not in analysis['file_processing_result']:
            analysis['file_processing_result']['content'] = {}
        file_content = analysis['file_processing_result']['content']
        
        # メタデータフィールド
        if 'ファイル名' in extended_data:
            basic['file_name'] = extended_data['ファイル名']
            evidence['original_filename'] = extended_data['ファイル名']
        
        if 'ファイルサイズ' in extended_data:
            basic['file_size_human'] = extended_data['ファイルサイズ']
        
        if 'ページ数' in extended_data:
            try:
                format_spec['page_count'] = int(extended_data['ページ数']) if extended_data['ページ数'] else 0
            except (ValueError, TypeError):
                pass
        
        # 証拠メタデータ
        if 'evidence_metadata' not in ai_analysis:
            ai_analysis['evidence_metadata'] = {}
        ev_meta = ai_analysis['evidence_metadata']
        
        if '証拠種別_詳細' in extended_data:
            ev_meta['evidence_type'] = extended_data['証拠種別_詳細']
        
        if 'フォーマット説明' in extended_data:
            ev_meta['format_description'] = extended_data['フォーマット説明']
        
        # 客観的分析
        if 'objective_analysis' not in ai_analysis:
            ai_analysis['objective_analysis'] = {}
        obj = ai_analysis['objective_analysis']
        
        if '文書種別' in extended_data:
            obj['document_type'] = extended_data['文書種別']
        
        # 時間情報
        if 'temporal_information' not in obj:
            obj['temporal_information'] = {}
        temporal = obj['temporal_information']
        
        if '作成日' in extended_data:
            temporal['document_date'] = extended_data['作成日']
        
        if '時間的コンテキスト' in extended_data:
            temporal['temporal_context'] = extended_data['時間的コンテキスト']
        
        # 関係者情報
        if 'parties_mentioned' not in obj:
            obj['parties_mentioned'] = {}
        parties = obj['parties_mentioned']
        
        # 組織情報（最大3件）
        if 'organizations' not in parties:
            parties['organizations'] = []
        organizations = parties['organizations']
        
        for i in range(3):
            prefix = f'組織{i+1}_'
            name = extended_data.get(f'{prefix}名称', '').strip()
            role = extended_data.get(f'{prefix}役割', '').strip()
            context = extended_data.get(f'{prefix}コンテキスト', '').strip()
            
            if name or role or context:
                org_dict = {}
                if name:
                    org_dict['name'] = name
                if role:
                    org_dict['role'] = role
                if context:
                    org_dict['context'] = context
                
                # インデックスに応じて追加または更新
                if i < len(organizations):
                    if isinstance(organizations[i], dict):
                        organizations[i].update(org_dict)
                    else:
                        organizations[i] = org_dict
                else:
                    organizations.append(org_dict)
        
        # 個人情報（最大2件）
        if 'individuals' not in parties:
            parties['individuals'] = []
        individuals = parties['individuals']
        
        for i in range(2):
            prefix = f'個人{i+1}_'
            name = extended_data.get(f'{prefix}名前', '').strip()
            role = extended_data.get(f'{prefix}役割', '').strip()
            context = extended_data.get(f'{prefix}コンテキスト', '').strip()
            
            if name or role or context:
                ind_dict = {}
                if name:
                    ind_dict['name'] = name
                if role:
                    ind_dict['role'] = role
                if context:
                    ind_dict['context'] = context
                
                if i < len(individuals):
                    if isinstance(individuals[i], dict):
                        individuals[i].update(ind_dict)
                    else:
                        individuals[i] = ind_dict
                else:
                    individuals.append(ind_dict)
        
        # 視覚要素
        if 'visual_elements' not in obj:
            obj['visual_elements'] = {}
        visual = obj['visual_elements']
        
        if 'レイアウト説明' in extended_data:
            visual['layout_description'] = extended_data['レイアウト説明']
        
        if 'テキスト内容要約' in extended_data:
            visual['text_content_summary'] = extended_data['テキスト内容要約']
        
        if '注目すべき特徴' in extended_data:
            visual['notable_features'] = extended_data['注目すべき特徴']
        
        # 完全内容
        if 'full_content' not in ai_analysis:
            ai_analysis['full_content'] = {}
        full_content = ai_analysis['full_content']
        
        if '完全な説明' in extended_data:
            full_content['complete_description'] = extended_data['完全な説明']
        
        if '詳細内容' in extended_data:
            full_content['detailed_content'] = extended_data['詳細内容']
        
        # 法的重要性
        if 'legal_significance' not in ai_analysis:
            ai_analysis['legal_significance'] = {}
        legal = ai_analysis['legal_significance']
        
        if '客観的事実' in extended_data:
            legal['objective_facts'] = extended_data['客観的事実']
        
        if '文脈上の重要性' in extended_data:
            legal['contextual_importance'] = extended_data['文脈上の重要性']
        
        # 証明可能な事実（最大5件）
        if 'provable_facts' not in legal:
            legal['provable_facts'] = []
        provable_facts = legal['provable_facts']
        
        for i in range(1, 6):
            fact = extended_data.get(f'証明可能な事実{i}', '').strip()
            if fact:
                if i-1 < len(provable_facts):
                    provable_facts[i-1] = fact
                else:
                    provable_facts.append(fact)
        
        # 使用提案
        if 'usage_suggestions' not in ai_analysis:
            ai_analysis['usage_suggestions'] = {}
        usage = ai_analysis['usage_suggestions']
        
        if '推奨される使用方法' in extended_data:
            usage['recommended_usage'] = extended_data['推奨される使用方法']
        
        # OCR結果
        if 'ocr' not in file_content:
            file_content['ocr'] = {}
        
        if 'OCRテキスト' in extended_data:
            file_content['ocr']['text'] = extended_data['OCRテキスト']
        
        # 品質スコア
        if '完全言語化レベル' in extended_data:
            try:
                ai_analysis['verbalization_level'] = int(extended_data['完全言語化レベル']) if extended_data['完全言語化レベル'] else 0
            except (ValueError, TypeError):
                pass
        
        if '信頼度スコア' in extended_data:
            score_str = extended_data['信頼度スコア'].strip().rstrip('%')
            try:
                ai_analysis['confidence_score'] = float(score_str) / 100.0 if score_str else 0.0
            except (ValueError, TypeError):
                pass
    
    def _extract_extended_fields(self, evidence: Dict) -> Dict:
        """拡張モード用に自然言語フィールドを抽出
        
        Args:
            evidence: 証拠データ
            
        Returns:
            拡張フィールドの辞書
        """
        extended = {}
        
        # メタデータ
        metadata = evidence.get('complete_metadata', {})
        basic = metadata.get('basic', {})
        format_spec = metadata.get('format_specific', {})
        
        extended['ファイル名'] = basic.get('file_name', '')
        extended['ファイルサイズ'] = basic.get('file_size_human', '')
        extended['ページ数'] = format_spec.get('page_count', '') if isinstance(format_spec, dict) else ''
        
        # AI分析結果
        analysis = evidence.get('phase1_complete_analysis', {})
        ai_analysis = analysis.get('ai_analysis', {})
        
        # 証拠メタデータ
        ev_meta = ai_analysis.get('evidence_metadata', {})
        extended['証拠種別_詳細'] = ev_meta.get('evidence_type', '')
        extended['フォーマット説明'] = ev_meta.get('format_description', '')
        
        # 客観的分析
        obj = ai_analysis.get('objective_analysis', {})
        extended['文書種別'] = obj.get('document_type', '')
        
        # 時間情報
        temporal = obj.get('temporal_information', {})
        extended['作成日'] = temporal.get('document_date', '')
        extended['時間的コンテキスト'] = temporal.get('temporal_context', '')
        
        # 関係者情報
        parties = obj.get('parties_mentioned', {})
        organizations = parties.get('organizations', [])
        individuals = parties.get('individuals', [])
        
        # 組織（最大3件）
        for i in range(3):
            prefix = f'組織{i+1}_'
            if i < len(organizations):
                org = organizations[i]
                if isinstance(org, dict):
                    extended[f'{prefix}名称'] = org.get('name', '')
                    extended[f'{prefix}役割'] = org.get('role', '')
                    extended[f'{prefix}コンテキスト'] = org.get('context', '')
                else:
                    extended[f'{prefix}名称'] = ''
                    extended[f'{prefix}役割'] = ''
                    extended[f'{prefix}コンテキスト'] = ''
            else:
                extended[f'{prefix}名称'] = ''
                extended[f'{prefix}役割'] = ''
                extended[f'{prefix}コンテキスト'] = ''
        
        # 個人（最大2件）
        for i in range(2):
            prefix = f'個人{i+1}_'
            if i < len(individuals):
                person = individuals[i]
                if isinstance(person, dict):
                    extended[f'{prefix}名前'] = person.get('name', '')
                    extended[f'{prefix}役割'] = person.get('role', '')
                    extended[f'{prefix}コンテキスト'] = person.get('context', '')
                else:
                    extended[f'{prefix}名前'] = ''
                    extended[f'{prefix}役割'] = ''
                    extended[f'{prefix}コンテキスト'] = ''
            else:
                extended[f'{prefix}名前'] = ''
                extended[f'{prefix}役割'] = ''
                extended[f'{prefix}コンテキスト'] = ''
        
        # 視覚要素
        visual = obj.get('visual_elements', {})
        extended['レイアウト説明'] = visual.get('layout_description', '')
        extended['テキスト内容要約'] = visual.get('text_content_summary', '')
        notable_features = visual.get('notable_features', [])
        extended['注目すべき特徴'] = ', '.join(notable_features) if isinstance(notable_features, list) else str(notable_features)
        
        # 完全内容
        full_content = ai_analysis.get('full_content', {})
        extended['完全な説明'] = full_content.get('complete_description', '')
        extended['詳細内容'] = full_content.get('detailed_content', '')
        
        # 法的重要性
        legal = ai_analysis.get('legal_significance', {})
        extended['客観的事実'] = legal.get('objective_facts', '')
        extended['文脈上の重要性'] = legal.get('contextual_importance', '')
        
        # 関連事実（最大5件）
        # 複数の可能なパスを試行
        provable_facts = []
        
        # パス1: related_facts.provable_facts
        related = ai_analysis.get('related_facts', {})
        provable_facts = related.get('provable_facts', [])
        
        # パス2: legal_significance.provable_facts（別の可能な場所）
        if not provable_facts:
            provable_facts = legal.get('provable_facts', [])
        
        for i in range(5):
            if i < len(provable_facts):
                fact = provable_facts[i]
                extended[f'証明可能な事実{i+1}'] = fact if isinstance(fact, str) else ''
            else:
                extended[f'証明可能な事実{i+1}'] = ''
        
        # 使用提案
        usage = ai_analysis.get('usage_suggestions', {})
        extended['推奨される使用方法'] = usage.get('recommended_usage', '')
        
        # OCR結果（実際に読み取られた文字列を取得）
        ocr_text = ''
        
        # パス1: ai_analysis.full_content.ocr_results.extracted_text（Vision APIのOCR結果）← 最優先
        ocr_results = full_content.get('ocr_results', {})
        ocr_text = ocr_results.get('extracted_text', '')
        
        # パス2: ai_analysis.full_content.textual_content.extracted_text（代替パス）
        if not ocr_text or ocr_text.strip() == '':
            textual_content = full_content.get('textual_content', {})
            ocr_text = textual_content.get('extracted_text', '')
        
        # パス3: file_processing_result.content.total_text（PDF直接抽出）
        if not ocr_text or ocr_text.strip() == '':
            file_content = analysis.get('file_processing_result', {}).get('content', {})
            total_text = file_content.get('total_text', '')
            # 制御文字のみでないか確認
            if total_text and not (len(total_text) > 0 and '\u0001' in total_text[:20]):
                ocr_text = total_text
        
        # パス4: file_processing_result.content.pages（各ページのテキストを結合）
        if not ocr_text or ocr_text.strip() == '':
            file_content = analysis.get('file_processing_result', {}).get('content', {})
            pages = file_content.get('pages', [])
            if pages:
                page_texts = []
                for page in pages:
                    page_text = page.get('text', '')
                    # 制御文字のみの場合はスキップ
                    if page_text and not all(c in '\u0001\n ' for c in page_text[:50]):
                        page_texts.append(f"--- ページ{page.get('page_number', 0)} ---\n{page_text}")
                if page_texts:
                    ocr_text = '\n\n'.join(page_texts)
        
        # パス5以降: 旧形式の様々なパス
        if not ocr_text or ocr_text.strip() == '':
            file_content = analysis.get('file_processing_result', {}).get('content', {})
            ocr_text = file_content.get('text', '') or \
                      analysis.get('file_processing_result', {}).get('ocr_text', '') or \
                      evidence.get('complete_metadata', {}).get('ocr_text', '')
        
        extended['OCRテキスト'] = ocr_text
        
        # 品質スコア
        extended['完全言語化レベル'] = ai_analysis.get('verbalization_level', 0)
        extended['信頼度スコア'] = f"{ai_analysis.get('confidence_score', 0.0):.1%}"
        
        return extended
    
    def _export_to_csv(self, evidence_list: List[Dict], filename: str, evidence_type: str = 'ko', full_data: bool = False, extended_mode: bool = False):
        """CSV形式でエクスポート
        
        Args:
            evidence_list: 証拠リスト
            filename: 出力ファイル名
            evidence_type: 証拠種別 ('ko' または 'otsu')
            full_data: True の場合、database.jsonの全データをJSON列として出力
            extended_mode: True の場合、自然言語フィールドを個別列に展開（拡張モード）
        """
        import csv
        
        try:
            output_path = os.path.join(os.getcwd(), filename)
            
            with open(output_path, 'w', encoding='utf-8-sig', newline='') as csvfile:
                if extended_mode:
                    # 拡張モード: 自然言語フィールドを個別列に展開
                    fieldnames = [
                        # 基本情報
                        '証拠種別', 'ステータス', '証拠番号', '仮番号', '分析状態',
                        'Google DriveファイルID',
                        
                        # メタデータ
                        'ファイル名', 'ファイルサイズ', 'ページ数',
                        
                        # 証拠メタデータ
                        '証拠種別_詳細', 'フォーマット説明',
                        
                        # 客観的分析
                        '文書種別', '作成日', '時間的コンテキスト',
                        
                        # 関係者情報（最大5組織、5個人）
                        '組織1_名称', '組織1_役割', '組織1_コンテキスト',
                        '組織2_名称', '組織2_役割', '組織2_コンテキスト',
                        '組織3_名称', '組織3_役割', '組織3_コンテキスト',
                        '個人1_名前', '個人1_役割', '個人1_コンテキスト',
                        '個人2_名前', '個人2_役割', '個人2_コンテキスト',
                        
                        # 視覚要素
                        'レイアウト説明', 'テキスト内容要約', '注目すべき特徴',
                        
                        # 完全内容
                        '完全な説明', '詳細内容',
                        
                        # 法的重要性
                        '客観的事実', '文脈上の重要性',
                        
                        # 関連事実（最大10件）
                        '証明可能な事実1', '証明可能な事実2', '証明可能な事実3',
                        '証明可能な事実4', '証明可能な事実5',
                        
                        # 使用提案
                        '推奨される使用方法',
                        
                        # OCR結果
                        'OCRテキスト',
                        
                        # 品質スコア
                        '完全言語化レベル', '信頼度スコア'
                    ]
                elif full_data:
                    # 全データモード: 主要フィールド + JSON列
                    fieldnames = [
                        '証拠種別', 'ステータス', '証拠番号', '仮番号', '作成日', 
                        '分析状態', 'ファイル名', '文書種別', '作成者',
                        '宛先', '要約', 'Google DriveファイルID',
                        'complete_metadata_json', 'phase1_complete_analysis_json'
                    ]
                else:
                    # 簡易モード: 主要フィールドのみ
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
                    
                    # 拡張モードの場合、自然言語フィールドを個別列に展開
                    if extended_mode:
                        # 拡張モード専用の基本情報
                        row_data = {
                            '証拠種別': type_name,
                            'ステータス': status,
                            '証拠番号': evidence_id,
                            '仮番号': temp_id,
                            '分析状態': analysis_status,
                            'Google DriveファイルID': gdrive_file_id
                        }
                        # 拡張フィールドを追加
                        extended_data = self._extract_extended_fields(evidence)
                        row_data.update(extended_data)
                    
                    # 全データモードの場合、標準フィールド + JSON列
                    elif full_data:
                        row_data = {
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
                        }
                        # complete_metadataをJSON文字列として出力
                        complete_metadata = evidence.get('complete_metadata', {})
                        row_data['complete_metadata_json'] = json.dumps(complete_metadata, ensure_ascii=False) if complete_metadata else ''
                        
                        # phase1_complete_analysisをJSON文字列として出力
                        phase1_analysis = evidence.get('phase1_complete_analysis', {})
                        row_data['phase1_complete_analysis_json'] = json.dumps(phase1_analysis, ensure_ascii=False) if phase1_analysis else ''
                    
                    # 標準モード
                    else:
                        row_data = {
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
                        }
                    
                    writer.writerow(row_data)
            
            print(f"\n✅ CSV形式でエクスポートしました")
            print(f"   ファイル: {output_path}")
            print(f"   件数: {len(evidence_list)}件")
            
            # Google Driveへのアップロードを確認
            upload_choice = input("\nGoogle Driveにもアップロードしますか？ (y/n): ").strip().lower()
            if upload_choice == 'y':
                gdrive_url = self._upload_export_file_to_gdrive(output_path, filename)
                if gdrive_url:
                    print(f"\n✅ Google Driveにアップロードしました")
                    print(f"   URL: {gdrive_url}")
            
        except Exception as e:
            print(f"\n❌ エクスポートに失敗しました: {e}")
            import traceback
            traceback.print_exc()
    
    def _upload_export_file_to_gdrive(self, local_path: str, filename: str) -> Optional[str]:
        """エクスポートファイルをGoogle Driveにアップロード
        
        Args:
            local_path: ローカルファイルパス
            filename: ファイル名
        
        Returns:
            Google DriveのURL（失敗時はNone）
        """
        try:
            service = self.case_manager.get_google_drive_service()
            if not service:
                print("❌ Google Driveサービスに接続できません")
                return None
            
            from googleapiclient.http import MediaFileUpload
            
            # エクスポートフォルダIDを取得
            database = self.db_manager.load_database()
            export_folder_id = database.get('metadata', {}).get('export_folder_id')
            
            # エクスポートフォルダIDがない場合は事件フォルダIDにフォールバック
            if not export_folder_id:
                case_folder_id = database.get('metadata', {}).get('case_folder_id')
                if not case_folder_id:
                    print("❌ 事件フォルダIDが見つかりません")
                    return None
                print("⚠️  エクスポートフォルダIDが見つかりません。事件フォルダに保存します。")
                target_folder_id = case_folder_id
            else:
                target_folder_id = export_folder_id
            
            # ファイルタイプを判定
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext == '.csv':
                mime_type = 'text/csv'
            elif file_ext == '.xlsx':
                mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            else:
                mime_type = 'application/octet-stream'
            
            file_metadata = {
                'name': filename,
                'parents': [target_folder_id],
                'mimeType': mime_type
            }
            
            media = MediaFileUpload(local_path, mimetype=mime_type, resumable=True)
            
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                supportsAllDrives=True,
                fields='id, name, webViewLink'
            ).execute()
            
            return file.get('webViewLink', f"https://drive.google.com/file/d/{file['id']}/view")
            
        except Exception as e:
            print(f"❌ Google Driveへのアップロード失敗: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _download_file_from_gdrive_url(self, gdrive_url: str, output_path: str) -> bool:
        """Google Drive URLからファイルをダウンロード
        
        Args:
            gdrive_url: Google DriveのURL
                - https://drive.google.com/file/d/FILE_ID/view
                - https://docs.google.com/spreadsheets/d/FILE_ID/edit
            output_path: ダウンロード先パス
        
        Returns:
            成功時True、失敗時False
        """
        try:
            # URLからファイルIDを抽出
            import re
            
            # パターン1: https://drive.google.com/file/d/FILE_ID/view
            match = re.search(r'/file/d/([a-zA-Z0-9_-]+)', gdrive_url)
            if not match:
                # パターン2: https://docs.google.com/spreadsheets/d/FILE_ID/edit
                match = re.search(r'/spreadsheets/d/([a-zA-Z0-9_-]+)', gdrive_url)
            if not match:
                # パターン3: https://drive.google.com/open?id=FILE_ID
                match = re.search(r'[?&]id=([a-zA-Z0-9_-]+)', gdrive_url)
            if not match:
                # パターン4: 汎用的な /d/ パターン
                match = re.search(r'/d/([a-zA-Z0-9_-]+)', gdrive_url)
            
            if not match:
                print(f"❌ 無効なGoogle Drive URL: {gdrive_url}")
                return False
            
            file_id = match.group(1)
            print(f"📥 ファイルID: {file_id}")
            
            service = self.case_manager.get_google_drive_service()
            if not service:
                print("❌ Google Driveサービスに接続できません")
                return False
            
            # ファイル情報を取得してMIMEタイプを確認
            import io
            from googleapiclient.http import MediaIoBaseDownload
            
            file_metadata = service.files().get(
                fileId=file_id,
                fields='mimeType, name',
                supportsAllDrives=True
            ).execute()
            
            mime_type = file_metadata.get('mimeType', '')
            file_name = file_metadata.get('name', 'unknown')
            
            print(f"   ファイル名: {file_name}")
            print(f"   ファイルタイプ: {mime_type}")
            
            # Google Spreadsheetsの場合はExcel形式でエクスポート
            if mime_type == 'application/vnd.google-apps.spreadsheet':
                print("   📊 Google Spreadsheetsを検出 → Excel形式でエクスポート中...")
                
                # Excel形式でエクスポート
                request = service.files().export_media(
                    fileId=file_id,
                    mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        print(f"   ダウンロード進行中: {int(status.progress() * 100)}%")
                
                # ファイルに書き込み
                with open(output_path, 'wb') as f:
                    f.write(fh.getvalue())
                
                print(f"✅ ダウンロード完了: {output_path}")
            else:
                # 通常のファイルダウンロード
                request = service.files().get_media(fileId=file_id, supportsAllDrives=True)
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        print(f"   ダウンロード進行中: {int(status.progress() * 100)}%")
                
                # ファイルに書き込み
                with open(output_path, 'wb') as f:
                    f.write(fh.getvalue())
                
                print(f"✅ ダウンロード完了: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Google Driveからのダウンロード失敗: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def import_csv_updates(self):
        """CSV編集内容をdatabase.jsonに反映"""
        print("\n" + "="*70)
        print("  CSV編集内容をdatabase.jsonに反映")
        print("="*70)
        print("\n編集したCSVファイルから証拠情報を更新します")
        print("編集可能な項目:")
        print("  標準モード: 作成日、ファイル名、文書種別、作成者、宛先")
        print("  拡張モード: 自然言語フィールド（OCR、AI分析、視覚情報など）")
        print("  完全モード: database.jsonの全データ（JSON列）")
        print("※ステータス、証拠番号などの識別子は編集できません")
        
        # ファイルパスまたはGoogle Drive URLの入力
        print("\n編集したCSV/Excelファイルを指定してください:")
        print("  1. ローカルファイルパス（絶対パスまたは相対パス、拡張子: .csv, .xlsx）")
        print("  2. Google Drive ファイルURL（https://drive.google.com/file/d/.../view）")
        print("  3. Google Spreadsheets URL（https://docs.google.com/spreadsheets/d/.../edit）")
        file_input = input("\nファイルパスまたはURL: ").strip()
        
        if not file_input:
            print("キャンセルしました")
            return
        
        # Google Drive URLかどうかを判定
        is_gdrive_url = file_input.startswith('http') and ('drive.google.com' in file_input or 'docs.google.com' in file_input)
        
        if is_gdrive_url:
            # Google Drive URLからダウンロード
            print("\n📥 Google Driveからダウンロード中...")
            
            # 一時ファイルパスを生成
            import tempfile
            temp_dir = tempfile.gettempdir()
            
            # Google SpreadsheetsのURLかどうかを判定
            import re
            is_spreadsheet = bool(re.search(r'/spreadsheets/d/', file_input))
            
            if is_spreadsheet:
                # Google Spreadsheetsの場合は自動的にExcel形式
                print("   📊 Google Spreadsheetsを検出 → Excel形式として処理します")
                file_ext = '.xlsx'
            else:
                # 通常のGoogle Driveファイルの場合はユーザーに確認
                print("\nファイル形式を選択してください:")
                print("  1. CSV形式 (.csv)")
                print("  2. Excel形式 (.xlsx)")
                format_choice = input("\n> ").strip()
                
                if format_choice == '1':
                    file_ext = '.csv'
                elif format_choice == '2':
                    file_ext = '.xlsx'
                else:
                    print("❌ 無効な選択です")
                    return
            
            temp_filename = f"imported_evidence{file_ext}"
            file_path = os.path.join(temp_dir, temp_filename)
            
            # Google Driveからダウンロード
            if not self._download_file_from_gdrive_url(file_input, file_path):
                print("❌ ダウンロードに失敗しました")
                return
        else:
            # ローカルファイルパス
            file_path = file_input
            
            # ファイルの存在確認
            if not os.path.exists(file_path):
                print(f"\n❌ ファイルが見つかりません: {file_path}")
                return
        
        try:
            import csv
            
            # ファイル拡張子で判定
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.xlsx':
                # Excelファイルを読み込み
                print("\nExcelファイルを読み込んでいます...")
                csv_data = []
                
                import openpyxl
                wb = openpyxl.load_workbook(file_path)
                ws = wb.active
                
                # ヘッダー行を取得
                headers = []
                for cell in ws[1]:
                    headers.append(cell.value if cell.value else '')
                
                # データ行を読み込み
                for row in ws.iter_rows(min_row=2, values_only=True):
                    row_dict = {}
                    for i, value in enumerate(row):
                        if i < len(headers):
                            row_dict[headers[i]] = str(value) if value is not None else ''
                    csv_data.append(row_dict)
            
            elif file_ext == '.csv':
                # CSVファイルを読み込み
                print("\nCSVファイルを読み込んでいます...")
                csv_data = []
                
                with open(file_path, 'r', encoding='utf-8-sig') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        csv_data.append(row)
            
            else:
                print(f"\n❌ サポートされていないファイル形式です: {file_ext}")
                print("   対応形式: .csv, .xlsx")
                return
            
            if not csv_data:
                print("\n❌ CSVファイルにデータがありません")
                return
            
            print(f"✅ {len(csv_data)}件のレコードを読み込みました")
            
            # データベースを読み込み
            database = self.db_manager.load_database()
            evidence_list = database.get('evidence', [])
            
            if not evidence_list:
                print("\n❌ データベースに証拠が登録されていません")
                return
            
            # 証拠番号でインデックスを作成（高速検索用）
            evidence_index = {}
            for evidence in evidence_list:
                evidence_id = evidence.get('evidence_id', '')
                if evidence_id:
                    evidence_index[evidence_id] = evidence
            
            # CSVモードを判定（完全/拡張/標準）
            first_row = csv_data[0] if csv_data else {}
            has_json_columns = 'complete_metadata_json' in first_row or 'phase1_complete_analysis_json' in first_row
            has_extended_columns = 'OCRテキスト' in first_row or '完全な説明' in first_row or 'レイアウト説明' in first_row
            
            if has_json_columns:
                csv_mode = 'full'
                print("\n✅ 完全モードCSV検出: JSON列からdatabase.jsonの全データを読み取ります")
            elif has_extended_columns:
                csv_mode = 'extended'
                print("\n✅ 拡張モードCSV検出: 自然言語フィールドを個別に更新します")
            else:
                csv_mode = 'standard'
                print("\n✅ 標準モードCSV検出: 主要フィールドのみを更新します")
            
            # 更新内容のプレビュー
            updates = []
            
            for row in csv_data:
                evidence_id = row.get('証拠番号', '').strip()
                
                if not evidence_id:
                    continue
                
                if evidence_id not in evidence_index:
                    print(f"\n⚠️  証拠番号 {evidence_id} がデータベースに見つかりません（スキップ）")
                    continue
                
                evidence = evidence_index[evidence_id]
                
                # 変更箇所を検出
                changes = {}
                csv_update_data = {}
                
                if csv_mode == 'full':
                    # 完全モード: JSON列から全データを読み取る
                    csv_metadata_json = row.get('complete_metadata_json', '').strip()
                    csv_analysis_json = row.get('phase1_complete_analysis_json', '').strip()
                    
                    # JSON文字列をパース
                    if csv_metadata_json:
                        try:
                            csv_metadata = json.loads(csv_metadata_json)
                            current_metadata = evidence.get('complete_metadata', {})
                            
                            # 変更検出（簡易比較）
                            if csv_metadata != current_metadata:
                                changes['complete_metadata'] = ('変更あり', '変更あり')
                                csv_update_data['complete_metadata'] = csv_metadata
                        except json.JSONDecodeError as e:
                            print(f"\n⚠️  {evidence_id}: complete_metadata_jsonの解析エラー: {e}")
                    
                    if csv_analysis_json:
                        try:
                            csv_analysis = json.loads(csv_analysis_json)
                            current_analysis = evidence.get('phase1_complete_analysis', {})
                            
                            # 変更検出（簡易比較）
                            if csv_analysis != current_analysis:
                                changes['phase1_complete_analysis'] = ('変更あり', '変更あり')
                                csv_update_data['phase1_complete_analysis'] = csv_analysis
                        except json.JSONDecodeError as e:
                            print(f"\n⚠️  {evidence_id}: phase1_complete_analysis_jsonの解析エラー: {e}")
                
                elif csv_mode == 'extended':
                    # 拡張モード: 自然言語フィールドを個別に更新
                    current_extended = self._extract_extended_fields(evidence)
                    
                    # 拡張フィールドのリスト
                    extended_fields = [
                        'ファイル名', 'ファイルサイズ', 'ページ数',
                        '証拠種別_詳細', 'フォーマット説明',
                        '文書種別', '作成日', '時間的コンテキスト',
                        '組織1_名称', '組織1_役割', '組織1_コンテキスト',
                        '組織2_名称', '組織2_役割', '組織2_コンテキスト',
                        '組織3_名称', '組織3_役割', '組織3_コンテキスト',
                        '個人1_名前', '個人1_役割', '個人1_コンテキスト',
                        '個人2_名前', '個人2_役割', '個人2_コンテキスト',
                        'レイアウト説明', 'テキスト内容要約', '注目すべき特徴',
                        '完全な説明', '詳細内容',
                        '客観的事実', '文脈上の重要性',
                        '証明可能な事実1', '証明可能な事実2', '証明可能な事実3',
                        '証明可能な事実4', '証明可能な事実5',
                        '推奨される使用方法',
                        'OCRテキスト',
                        '完全言語化レベル', '信頼度スコア'
                    ]
                    
                    # CSVから拡張フィールドを読み取り、変更を検出
                    csv_extended_data = {}
                    for field in extended_fields:
                        csv_value = row.get(field, '').strip()
                        current_value = str(current_extended.get(field, '')).strip()
                        
                        # 値が変更されている場合（型変換のみの変更は無視）
                        if csv_value != current_value:
                            # 数値型変換のみの変更を無視（例: 2 → 2.0）
                            is_numeric_conversion_only = False
                            try:
                                # 両方が数値に変換可能で、値が等しい場合は型変換のみとみなす
                                if csv_value and current_value:
                                    csv_num = float(csv_value)
                                    current_num = float(current_value)
                                    if csv_num == current_num:
                                        is_numeric_conversion_only = True
                            except (ValueError, TypeError):
                                pass
                            
                            # 型変換のみの変更でなければ、変更として記録
                            if not is_numeric_conversion_only:
                                changes[field] = (current_value[:50] + '...' if len(current_value) > 50 else current_value,
                                                csv_value[:50] + '...' if len(csv_value) > 50 else csv_value)
                                csv_extended_data[field] = csv_value
                    
                    if csv_extended_data:
                        csv_update_data['extended_fields'] = csv_extended_data
                
                else:
                    # 標準モード: 主要フィールドのみ更新
                    current_data = self._get_evidence_export_data(evidence)
                    
                    csv_file_name = row.get('ファイル名', '').strip()
                    csv_creation_date = row.get('作成日', '').strip()
                    csv_document_type = row.get('文書種別', '').strip()
                    csv_author = row.get('作成者', '').strip()
                    csv_recipient = row.get('宛先', '').strip()
                    
                    if csv_file_name and csv_file_name != current_data['file_name']:
                        changes['file_name'] = (current_data['file_name'], csv_file_name)
                        csv_update_data['file_name'] = csv_file_name
                    
                    if csv_creation_date and csv_creation_date != current_data['creation_date']:
                        changes['creation_date'] = (current_data['creation_date'], csv_creation_date)
                        csv_update_data['creation_date'] = csv_creation_date
                    
                    if csv_document_type and csv_document_type != current_data['document_type']:
                        changes['document_type'] = (current_data['document_type'], csv_document_type)
                        csv_update_data['document_type'] = csv_document_type
                    
                    if csv_author and csv_author != current_data['author']:
                        changes['author'] = (current_data['author'], csv_author)
                        csv_update_data['author'] = csv_author
                    
                    if csv_recipient and csv_recipient != current_data['recipient']:
                        changes['recipient'] = (current_data['recipient'], csv_recipient)
                        csv_update_data['recipient'] = csv_recipient
                
                if changes:
                    updates.append({
                        'evidence_id': evidence_id,
                        'evidence': evidence,
                        'changes': changes,
                        'csv_data': csv_update_data,
                        'csv_mode': csv_mode
                    })
            
            if not updates:
                print("\n✅ 変更箇所がありません。database.jsonは更新されませんでした。")
                return
            
            # 変更内容のプレビュー表示
            print(f"\n【更新プレビュー】 {len(updates)}件の証拠に変更があります")
            print("-"*70)
            
            for i, update in enumerate(updates, 1):
                evidence_id = update['evidence_id']
                changes = update['changes']
                mode = update.get('csv_mode', 'standard')
                
                print(f"\n{i}. 証拠番号: {evidence_id}")
                
                if mode == 'full':
                    # 完全モード: JSON全体の変更
                    if 'complete_metadata' in changes:
                        print(f"   complete_metadata: 変更あり")
                    if 'phase1_complete_analysis' in changes:
                        print(f"   phase1_complete_analysis: 変更あり")
                
                elif mode == 'extended':
                    # 拡張モード: 主要な変更を表示（最大5件）
                    displayed_count = 0
                    for field_name, (old_val, new_val) in changes.items():
                        if displayed_count < 5:
                            print(f"   {field_name}: {old_val} → {new_val}")
                            displayed_count += 1
                    
                    if len(changes) > 5:
                        print(f"   ... 他 {len(changes) - 5} 件のフィールドが変更されました")
                
                else:
                    # 標準モード: 個別フィールド
                    if 'file_name' in changes:
                        old, new = changes['file_name']
                        print(f"   ファイル名: {old} → {new}")
                    
                    if 'creation_date' in changes:
                        old, new = changes['creation_date']
                        print(f"   作成日: {old} → {new}")
                    
                    if 'document_type' in changes:
                        old, new = changes['document_type']
                        print(f"   文書種別: {old} → {new}")
                    
                    if 'author' in changes:
                        old, new = changes['author']
                        print(f"   作成者: {old} → {new}")
                    
                    if 'recipient' in changes:
                        old, new = changes['recipient']
                        print(f"   宛先: {old} → {new}")
            
            # 確認
            print("\n" + "-"*70)
            print("この内容でdatabase.jsonを更新しますか？")
            confirm = input("続行する場合は 'yes' と入力: ").strip().lower()
            
            if confirm != 'yes':
                print("\nキャンセルしました")
                return
            
            # データベースを更新
            print("\nデータベースを更新中...")
            
            for update in updates:
                evidence = update['evidence']
                csv_data = update['csv_data']
                mode = update.get('csv_mode', 'standard')
                
                if mode == 'full':
                    # 完全モード: JSON列から全データを直接反映
                    if 'complete_metadata' in csv_data:
                        evidence['complete_metadata'] = csv_data['complete_metadata']
                    
                    if 'phase1_complete_analysis' in csv_data:
                        evidence['phase1_complete_analysis'] = csv_data['phase1_complete_analysis']
                
                elif mode == 'extended':
                    # 拡張モード: 自然言語フィールドを個別に反映
                    extended_fields = csv_data.get('extended_fields', {})
                    if extended_fields:
                        self._apply_extended_fields(evidence, extended_fields)
                
                else:
                    # 標準モード: 主要フィールドのみ更新
                    # ファイル名の更新
                    if 'file_name' in csv_data:
                        evidence['original_filename'] = csv_data['file_name']
                        if 'complete_metadata' not in evidence:
                            evidence['complete_metadata'] = {}
                        if 'basic' not in evidence['complete_metadata']:
                            evidence['complete_metadata']['basic'] = {}
                        evidence['complete_metadata']['basic']['file_name'] = csv_data['file_name']
                    
                    # 作成日の更新（AI分析結果内に格納）
                    if 'creation_date' in csv_data:
                        phase1_analysis = evidence.get('phase1_complete_analysis', {})
                        ai_analysis = phase1_analysis.get('ai_analysis', {})
                        
                        if ai_analysis:
                            # 新しい構造: phase1_complete_analysis.ai_analysis.objective_analysis.temporal_information.document_date
                            if 'objective_analysis' not in ai_analysis:
                                ai_analysis['objective_analysis'] = {}
                            if 'temporal_information' not in ai_analysis['objective_analysis']:
                                ai_analysis['objective_analysis']['temporal_information'] = {}
                            ai_analysis['objective_analysis']['temporal_information']['document_date'] = csv_data['creation_date']
                        else:
                            # 旧構造用のフォールバック
                            if 'temporal_information' not in evidence:
                                evidence['temporal_information'] = {}
                            evidence['temporal_information']['document_date'] = csv_data['creation_date']
                    
                    # 文書種別の更新
                    if 'document_type' in csv_data:
                        phase1_analysis = evidence.get('phase1_complete_analysis', {})
                        ai_analysis = phase1_analysis.get('ai_analysis', {})
                        
                        if ai_analysis:
                            if 'objective_analysis' not in ai_analysis:
                                ai_analysis['objective_analysis'] = {}
                            ai_analysis['objective_analysis']['document_type'] = csv_data['document_type']
                        else:
                            # 旧構造用のフォールバック
                            phase1_analysis['document_type'] = csv_data['document_type']
                    
                    # 作成者・宛先の更新
                    if 'author' in csv_data or 'recipient' in csv_data:
                        phase1_analysis = evidence.get('phase1_complete_analysis', {})
                        ai_analysis = phase1_analysis.get('ai_analysis', {})
                        
                        if ai_analysis:
                            if 'objective_analysis' not in ai_analysis:
                                ai_analysis['objective_analysis'] = {}
                            if 'parties_mentioned' not in ai_analysis['objective_analysis']:
                                ai_analysis['objective_analysis']['parties_mentioned'] = {}
                            if 'organizations' not in ai_analysis['objective_analysis']['parties_mentioned']:
                                ai_analysis['objective_analysis']['parties_mentioned']['organizations'] = []
                            
                            organizations = ai_analysis['objective_analysis']['parties_mentioned']['organizations']
                            
                            # 作成者（organizations[0]）
                            if 'author' in csv_data:
                                if len(organizations) == 0:
                                    organizations.append(csv_data['author'])
                                else:
                                    organizations[0] = csv_data['author']
                            
                            # 宛先（organizations[1]）
                            if 'recipient' in csv_data:
                                if len(organizations) <= 1:
                                    organizations.append(csv_data['recipient'])
                                else:
                                    organizations[1] = csv_data['recipient']
                        else:
                            # 旧構造用のフォールバック
                            if 'author' in csv_data:
                                phase1_analysis['author'] = csv_data['author']
                            if 'recipient' in csv_data:
                                phase1_analysis['recipient'] = csv_data['recipient']
            
            # データベースを保存（Google Driveに同期）
            print("Google Driveに同期中...")
            self.save_database(database)
            
            print(f"\n✅ {len(updates)}件の証拠を更新し、Google Driveに同期しました！")
            
        except Exception as e:
            print(f"\n❌ エラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
    
    def _export_to_excel(self, evidence_list: List[Dict], filename: str, evidence_type: str = 'ko', full_data: bool = False, extended_mode: bool = False):
        """Excel形式でエクスポート
        
        Args:
            evidence_list: 証拠リスト
            filename: 出力ファイル名
            evidence_type: 証拠種別 ('ko' または 'otsu')
            full_data: True の場合、database.jsonの全データをJSON列として出力
            extended_mode: True の場合、自然言語フィールドを個別列に展開（拡張モード）
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
            if extended_mode:
                # 拡張モード: 自然言語フィールドを個別列に展開（CSV と同じ）
                headers = [
                    '証拠種別', 'ステータス', '証拠番号', '仮番号', '分析状態',
                    'Google DriveファイルID',
                    'ファイル名', 'ファイルサイズ', 'ページ数',
                    '証拠種別_詳細', 'フォーマット説明',
                    '文書種別', '作成日', '時間的コンテキスト',
                    '組織1_名称', '組織1_役割', '組織1_コンテキスト',
                    '組織2_名称', '組織2_役割', '組織2_コンテキスト',
                    '組織3_名称', '組織3_役割', '組織3_コンテキスト',
                    '個人1_名前', '個人1_役割', '個人1_コンテキスト',
                    '個人2_名前', '個人2_役割', '個人2_コンテキスト',
                    'レイアウト説明', 'テキスト内容要約', '注目すべき特徴',
                    '完全な説明', '詳細内容',
                    '客観的事実', '文脈上の重要性',
                    '証明可能な事実1', '証明可能な事実2', '証明可能な事実3',
                    '証明可能な事実4', '証明可能な事実5',
                    '推奨される使用方法',
                    'OCRテキスト',
                    '完全言語化レベル', '信頼度スコア'
                ]
            elif full_data:
                headers = [
                    '証拠種別', 'ステータス', '証拠番号', '仮番号', '作成日', 
                    '分析状態', 'ファイル名', '文書種別', '作成者',
                    '宛先', '要約', 'Google DriveファイルID',
                    'complete_metadata_json', 'phase1_complete_analysis_json'
                ]
            else:
                headers = [
                    '証拠種別', 'ステータス', '証拠番号', '仮番号', '作成日', 
                    '分析状態', 'ファイル名', '文書種別', '作成者',
                    '宛先', '要約', 'Google DriveファイルID'
                ]
            
            for col_idx, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col_idx, value=header)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = header_alignment
                cell.border = border
            
            # 列幅を設定
            if extended_mode:
                # 拡張モード: 全列にデフォルト列幅を設定
                for col_idx in range(1, len(headers) + 1):
                    col_letter = openpyxl.utils.get_column_letter(col_idx)
                    # 基本列は狭め、説明列は広めに設定
                    if col_idx <= 6:  # 基本情報
                        ws.column_dimensions[col_letter].width = 15
                    elif '説明' in headers[col_idx-1] or '内容' in headers[col_idx-1] or 'テキスト' in headers[col_idx-1]:
                        ws.column_dimensions[col_letter].width = 60
                    elif '事実' in headers[col_idx-1]:
                        ws.column_dimensions[col_letter].width = 50
                    else:
                        ws.column_dimensions[col_letter].width = 25
            elif full_data:
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
                    'K': 60,  # 要約
                    'L': 35,  # Google DriveファイルID
                    'M': 80,  # complete_metadata_json
                    'N': 80   # phase1_complete_analysis_json
                }
                for col, width in column_widths.items():
                    ws.column_dimensions[col].width = width
            else:
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
                    'K': 60,  # 要約
                    'L': 35   # Google DriveファイルID
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
                
                # Google Drive ファイルID
                gdrive_file_id = evidence.get('gdrive_file_id', '') or evidence.get('complete_metadata', {}).get('gdrive', {}).get('file_id', '')
                
                summary = export_data['complete_description'] or ''
                
                # 分析状態
                analysis_status = "分析済み" if export_data['complete_description'] else "未分析"
                
                # セルに値を設定
                if extended_mode:
                    # 拡張モード: 自然言語フィールドを個別列に展開
                    extended_data = self._extract_extended_fields(evidence)
                    
                    # 基本情報（最初の6列）
                    row_data = [
                        type_name,          # 証拠種別
                        status,             # ステータス
                        evidence_id,        # 証拠番号
                        temp_id,            # 仮番号
                        analysis_status,    # 分析状態
                        gdrive_file_id      # Google DriveファイルID
                    ]
                    
                    # 拡張フィールドを順番に追加（ヘッダーと同じ順序）
                    extended_field_order = [
                        'ファイル名', 'ファイルサイズ', 'ページ数',
                        '証拠種別_詳細', 'フォーマット説明',
                        '文書種別', '作成日', '時間的コンテキスト',
                        '組織1_名称', '組織1_役割', '組織1_コンテキスト',
                        '組織2_名称', '組織2_役割', '組織2_コンテキスト',
                        '組織3_名称', '組織3_役割', '組織3_コンテキスト',
                        '個人1_名前', '個人1_役割', '個人1_コンテキスト',
                        '個人2_名前', '個人2_役割', '個人2_コンテキスト',
                        'レイアウト説明', 'テキスト内容要約', '注目すべき特徴',
                        '完全な説明', '詳細内容',
                        '客観的事実', '文脈上の重要性',
                        '証明可能な事実1', '証明可能な事実2', '証明可能な事実3',
                        '証明可能な事実4', '証明可能な事実5',
                        '推奨される使用方法',
                        'OCRテキスト',
                        '完全言語化レベル', '信頼度スコア'
                    ]
                    
                    for field_name in extended_field_order:
                        row_data.append(extended_data.get(field_name, ''))
                
                elif full_data:
                    # 全データモード: 標準フィールド + JSON列
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
                        summary,                        # 要約
                        gdrive_file_id                  # Google DriveファイルID
                    ]
                    
                    # JSON列を追加
                    complete_metadata = evidence.get('complete_metadata', {})
                    row_data.append(json.dumps(complete_metadata, ensure_ascii=False) if complete_metadata else '')
                    
                    phase1_analysis = evidence.get('phase1_complete_analysis', {})
                    row_data.append(json.dumps(phase1_analysis, ensure_ascii=False) if phase1_analysis else '')
                
                else:
                    # 標準モード: 主要フィールドのみ
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
                        summary,                        # 要約
                        gdrive_file_id                  # Google DriveファイルID
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
                    # 拡張モードは5列目、標準・全データモードは6列目
                    analysis_status_col = 5 if extended_mode else 6
                    if col_idx == analysis_status_col:
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
            
            # Google Driveへのアップロードを確認
            upload_choice = input("\nGoogle Driveにもアップロードしますか？ (y/n): ").strip().lower()
            if upload_choice == 'y':
                gdrive_url = self._upload_export_file_to_gdrive(output_path, filename)
                if gdrive_url:
                    print(f"\n✅ Google Driveにアップロードしました")
                    print(f"   URL: {gdrive_url}")
            
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
                # CSV編集内容をdatabase.jsonに反映
                try:
                    self.import_csv_updates()
                except Exception as e:
                    print(f"\nエラー: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    
            elif choice == '8':
                # 時系列ストーリーの生成
                try:
                    self.generate_timeline_story()
                except Exception as e:
                    print(f"\nエラー: {str(e)}")
                    import traceback
                    traceback.print_exc()
                
            elif choice == '9':
                # 依頼者発言・メモの管理
                try:
                    self.manage_client_statements()
                except Exception as e:
                    print(f"\nエラー: {str(e)}")
                    import traceback
                    traceback.print_exc()
                
            elif choice == '10':
                # database.jsonの状態確認
                self.show_database_status()
                
            elif choice == '11':
                # 事件を切り替え
                if self.select_case():
                    print("\n✅ 事件を切り替えました")
                    
            elif choice == '0':
                # 終了
                print("\nPhase1_Evidence Analysis Systemを終了します")
                break
                
            else:
                print("\nエラー: 無効な選択です。0-11を入力してください。")
            
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

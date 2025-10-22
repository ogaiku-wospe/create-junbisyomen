#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1完全版システム - 事件マネージャー

【機能】
- 共有ドライブから事件フォルダを自動検出
- 複数事件の並行管理
- 事件情報のキャッシュ
- 事件の選択・切り替え

【使用方法】
    from case_manager import CaseManager
    
    manager = CaseManager()
    cases = manager.detect_cases()
    selected_case = manager.select_case_interactive(cases)
"""

import os
import sys
import json
import pickle
import logging
from typing import List, Dict, Optional
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# ロギング設定
logger = logging.getLogger(__name__)

# グローバル設定を読み込み
try:
    import global_config as gconfig
except ImportError:
    print("❌ global_config.py が見つかりません")
    sys.exit(1)

# Google Drive APIのスコープ（読み書きフルアクセス）
SCOPES = ['https://www.googleapis.com/auth/drive']


class CaseManager:
    """事件管理クラス"""
    
    def __init__(self, shared_drive_root_id: str = None):
        """初期化
        
        Args:
            shared_drive_root_id: 共有ドライブのルートID
                                 指定しない場合は global_config から読み込み
        """
        self.shared_drive_root_id = shared_drive_root_id or gconfig.SHARED_DRIVE_ROOT_ID
        
        if not self.shared_drive_root_id:
            raise ValueError("共有ドライブIDが設定されていません。global_config.py で SHARED_DRIVE_ROOT_ID を設定してください。")
        
        self.service = None
        self.cache_file = os.path.expanduser("~/.phase1_cases_cache.json")
        self.cache_expiry_hours = 24
    
    def get_google_drive_service(self):
        """Google Drive APIサービスを取得（サービスアカウントとOAuth両対応）"""
        if self.service:
            return self.service
        
        if not os.path.exists('credentials.json'):
            print("\n❌ エラー: credentials.jsonが見つかりません")
            print("Google Cloud Consoleからcredentials.jsonをダウンロードしてください")
            return None
        
        # credentials.jsonの形式を確認
        with open('credentials.json', 'r') as f:
            creds_data = json.load(f)
        
        # サービスアカウント形式の場合
        if 'type' in creds_data and creds_data['type'] == 'service_account':
            print("🔐 サービスアカウント認証を使用")
            creds = service_account.Credentials.from_service_account_file(
                'credentials.json', scopes=SCOPES)
            self.service = build('drive', 'v3', credentials=creds)
            return self.service
        
        # OAuth 2.0（デスクトップアプリ）形式の場合
        creds = None
        
        # token.pickleがあれば読み込み
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # 認証が無効または存在しない場合
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            # 認証情報を保存
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('drive', 'v3', credentials=creds)
        return self.service
    
    def detect_cases(self, use_cache: bool = True) -> List[Dict]:
        """共有ドライブから事件フォルダを自動検出
        
        Args:
            use_cache: キャッシュを使用するか
        
        Returns:
            事件情報のリスト
        """
        # キャッシュをチェック
        if use_cache:
            cached_cases = self._load_cache()
            if cached_cases:
                print("✅ キャッシュから事件情報を読み込みました")
                return cached_cases
        
        print("🔍 共有ドライブから事件フォルダを検索中...")
        
        service = self.get_google_drive_service()
        if not service:
            print("❌ Google Drive認証に失敗しました")
            return []
        
        cases = []
        
        try:
            # 共有ドライブ配下のフォルダを一覧取得
            query = f"'{self.shared_drive_root_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
            
            results = service.files().list(
                q=query,
                corpora='drive',
                driveId=self.shared_drive_root_id,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                fields='files(id, name, createdTime, modifiedTime)',
                pageSize=100
            ).execute()
            
            folders = results.get('files', [])
            
            print(f"📁 {len(folders)}個のフォルダを検出しました")
            
            # 各フォルダが事件フォルダかチェック
            for folder in folders:
                folder_name = folder['name']
                case_info = self._analyze_case_folder(service, folder)
                if case_info:
                    cases.append(case_info)
                    print(f"  ✅ 事件フォルダ検出: {case_info['case_name']}")
                else:
                    print(f"  ⏭️  スキップ: {folder_name} (事件フォルダの条件を満たしていません)")
            
            # キャッシュに保存
            self._save_cache(cases)
            
            print(f"\n✅ {len(cases)}件の事件を検出しました\n")
            
        except Exception as e:
            print(f"❌ 事件検出エラー: {e}")
        
        return cases
    
    def _analyze_case_folder(self, service, folder: Dict) -> Optional[Dict]:
        """フォルダが事件フォルダか分析
        
        Args:
            service: Google Drive APIサービス
            folder: フォルダ情報
        
        Returns:
            事件情報（事件フォルダでない場合はNone）
        """
        folder_id = folder['id']
        folder_name = folder['name']
        
        try:
            # フォルダ配下のファイル・フォルダを取得
            query = f"'{folder_id}' in parents and trashed=false"
            results = service.files().list(
                q=query,
                corpora='drive',
                driveId=self.shared_drive_root_id,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                fields='files(id, name, mimeType)',
                pageSize=100
            ).execute()
            
            items = results.get('files', [])
            item_names = [item['name'] for item in items]
            
            # 事件フォルダの条件チェック（デバッグ情報付き）
            matched_indicators = [
                indicator for indicator in gconfig.CASE_FOLDER_INDICATORS
                if indicator in item_names
            ]
            is_case_folder = len(matched_indicators) > 0
            
            if not is_case_folder:
                # デバッグ: 条件を満たしていない理由を表示
                if os.environ.get('DEBUG_CASE_DETECTION'):
                    print(f"      ❌ {folder_name}: 事件フォルダ判定ファイルが見つかりません")
                    print(f"         検出されたファイル: {', '.join(item_names[:5])}{'...' if len(item_names) > 5 else ''}")
                    print(f"         必要なファイル: {', '.join(gconfig.CASE_FOLDER_INDICATORS)}")
                return None
            
            # 事件情報を構築
            case_info = {
                'case_folder_id': folder_id,
                'case_folder_name': folder_name,
                'case_id': self._extract_case_id(folder_name),
                'case_name': self._extract_case_name(folder_name),
                'created_time': folder.get('createdTime'),
                'modified_time': folder.get('modifiedTime'),
                'ko_evidence_folder_id': None,
                'otsu_evidence_folder_id': None,
                'database_folder_id': None,
                'evidence_count': 0,
                'completed_count': 0,
                # 階層的フォルダ構成用
                'folder_structure': None,  # 'hierarchical' or 'legacy'
                'ko_folders': {},  # {'confirmed': id, 'pending': id, 'unclassified': id}
                'otsu_folders': {},  # {'confirmed': id, 'pending': id, 'unclassified': id}
                'legacy_folders': {}  # {'unclassified': id, 'pending': id} for legacy structure
            }
            
            # フォルダ構造を分析（階層的 or 旧形式）
            folder_structure_info = self._analyze_folder_structure(service, folder_id, items)
            case_info.update(folder_structure_info)
            
            # 証拠数をカウント（階層的構造の場合は確定済みフォルダのみ）
            if case_info['folder_structure'] == 'hierarchical':
                ko_confirmed_id = case_info['ko_folders'].get('confirmed')
                if ko_confirmed_id:
                    case_info['evidence_count'] = self._count_files_in_folder(
                        service, ko_confirmed_id
                    )
            elif case_info['ko_evidence_folder_id']:
                # 旧形式の場合は甲号証フォルダ直下
                case_info['evidence_count'] = self._count_files_in_folder(
                    service, case_info['ko_evidence_folder_id']
                )
            
            # config.json を読み込み（存在する場合）
            config_file = next(
                (item for item in items if item['name'] == 'config.json'),
                None
            )
            if config_file:
                config_data = self._download_json_file(service, config_file['id'])
                if config_data:
                    case_info.update(config_data)
            
            # database.json を読み込み（存在する場合）
            database_file = next(
                (item for item in items if item['name'] == 'database.json'),
                None
            )
            if database_file:
                database_data = self._download_json_file(service, database_file['id'])
                if database_data:
                    evidence_list = database_data.get('evidence', [])
                    case_info['evidence_count'] = len(evidence_list)
                    case_info['completed_count'] = len([
                        e for e in evidence_list 
                        if e.get('status') == 'completed'
                    ])
                    case_info['last_updated'] = database_data.get('metadata', {}).get('last_updated')
            
            return case_info
            
        except Exception as e:
            print(f"  ⚠️ フォルダ分析エラー ({folder_name}): {e}")
            return None
    
    def _analyze_folder_structure(self, service, case_folder_id: str, items: List[Dict]) -> Dict:
        """事件フォルダの構造を分析（階層的 or 旧形式）
        
        Args:
            service: Google Drive APIサービス
            case_folder_id: 事件フォルダID
            items: 事件フォルダ直下のアイテムリスト
        
        Returns:
            フォルダ構造情報
        """
        result = {
            'folder_structure': 'legacy',  # デフォルトは旧形式
            'ko_evidence_folder_id': None,
            'otsu_evidence_folder_id': None,
            'database_folder_id': None,
            'ko_folders': {},
            'otsu_folders': {},
            'legacy_folders': {}
        }
        
        # 各フォルダを検索
        ko_root_folder = None
        otsu_root_folder = None
        
        for item in items:
            if item['mimeType'] != 'application/vnd.google-apps.folder':
                continue
            
            name = item['name']
            item_id = item['id']
            
            if name == '甲号証':
                ko_root_folder = item
                result['ko_evidence_folder_id'] = item_id
            elif name == '乙号証':
                otsu_root_folder = item
                result['otsu_evidence_folder_id'] = item_id
            elif name == '未分類':
                result['legacy_folders']['unclassified'] = item_id
            elif name == '整理済み_未確定':
                result['legacy_folders']['pending'] = item_id
            elif name == gconfig.DATABASE_FOLDER_NAME:
                result['database_folder_id'] = item_id
        
        # 階層的構造をチェック
        # 甲号証フォルダ配下を調べる
        if ko_root_folder:
            ko_subfolders = self._get_subfolders(service, ko_root_folder['id'])
            ko_has_subfolders = any(
                sf['name'] in ['確定済み', '整理済み_未確定', '未分類']
                for sf in ko_subfolders
            )
            
            if ko_has_subfolders:
                # 階層的構造を検出
                result['folder_structure'] = 'hierarchical'
                for sf in ko_subfolders:
                    if sf['name'] == '確定済み':
                        result['ko_folders']['confirmed'] = sf['id']
                    elif sf['name'] == '整理済み_未確定':
                        result['ko_folders']['pending'] = sf['id']
                    elif sf['name'] == '未分類':
                        result['ko_folders']['unclassified'] = sf['id']
        
        # 乙号証フォルダ配下を調べる
        if otsu_root_folder:
            otsu_subfolders = self._get_subfolders(service, otsu_root_folder['id'])
            otsu_has_subfolders = any(
                sf['name'] in ['確定済み', '整理済み_未確定', '未分類']
                for sf in otsu_subfolders
            )
            
            if otsu_has_subfolders:
                # 階層的構造を検出
                result['folder_structure'] = 'hierarchical'
                for sf in otsu_subfolders:
                    if sf['name'] == '確定済み':
                        result['otsu_folders']['confirmed'] = sf['id']
                    elif sf['name'] == '整理済み_未確定':
                        result['otsu_folders']['pending'] = sf['id']
                    elif sf['name'] == '未分類':
                        result['otsu_folders']['unclassified'] = sf['id']
        
        return result
    
    def _get_subfolders(self, service, folder_id: str) -> List[Dict]:
        """フォルダ配下のサブフォルダを取得
        
        Args:
            service: Google Drive APIサービス
            folder_id: 親フォルダID
        
        Returns:
            サブフォルダのリスト
        """
        try:
            query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
            
            results = service.files().list(
                q=query,
                corpora='drive',
                driveId=self.shared_drive_root_id,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                fields='files(id, name)',
                pageSize=100
            ).execute()
            
            return results.get('files', [])
        except Exception as e:
            logger.warning(f"サブフォルダ取得エラー ({folder_id}): {e}")
            return []
    
    def _extract_case_id(self, folder_name: str) -> str:
        """フォルダ名から事件IDを抽出"""
        # フォルダ名が "{case_id}_{case_name}" 形式の場合
        if '_' in folder_name:
            return folder_name.split('_')[0]
        return folder_name
    
    def _extract_case_name(self, folder_name: str) -> str:
        """フォルダ名から事件名を抽出"""
        # フォルダ名が "{case_id}_{case_name}" 形式の場合
        if '_' in folder_name:
            parts = folder_name.split('_', 1)
            return parts[1] if len(parts) > 1 else folder_name
        return folder_name
    
    def _count_files_in_folder(self, service, folder_id: str) -> int:
        """フォルダ内のファイル数をカウント"""
        try:
            query = f"'{folder_id}' in parents and trashed=false and mimeType!='application/vnd.google-apps.folder'"
            results = service.files().list(
                q=query,
                corpora='drive',
                driveId=self.shared_drive_root_id,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                fields='files(id)',
                pageSize=1000
            ).execute()
            
            return len(results.get('files', []))
        except:
            return 0
    
    def _download_json_file(self, service, file_id: str) -> Optional[Dict]:
        """JSONファイルをダウンロードして解析"""
        try:
            import io
            from googleapiclient.http import MediaIoBaseDownload
            
            request = service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            fh.seek(0)
            return json.load(fh)
        except:
            return None
    
    def _load_cache(self) -> Optional[List[Dict]]:
        """キャッシュから事件情報を読み込み"""
        if not os.path.exists(self.cache_file):
            return None
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            
            # キャッシュの有効期限チェック
            cached_time = datetime.fromisoformat(cache.get('cached_at', ''))
            now = datetime.now()
            hours_diff = (now - cached_time).total_seconds() / 3600
            
            if hours_diff > self.cache_expiry_hours:
                return None
            
            return cache.get('cases', [])
        except:
            return None
    
    def _save_cache(self, cases: List[Dict]):
        """事件情報をキャッシュに保存"""
        try:
            cache = {
                'cached_at': datetime.now().isoformat(),
                'shared_drive_root_id': self.shared_drive_root_id,
                'cases': cases
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ キャッシュ保存エラー: {e}")
    
    def display_cases(self, cases: List[Dict]):
        """事件一覧を表示"""
        print("\n" + "="*70)
        print("  Phase 1完全版システム - 事件一覧")
        print("="*70)
        
        if not cases:
            print("\n❌ 事件が見つかりませんでした。")
            print("\n💡 ヒント:")
            print("  1. global_config.py で SHARED_DRIVE_ROOT_ID が正しく設定されているか確認")
            print("  2. 共有ドライブ配下に事件フォルダが存在するか確認")
            print("  3. 事件フォルダ内に '甲号証' フォルダが存在するか確認")
            return
        
        print(f"\n📋 検出された事件: {len(cases)}件\n")
        
        for idx, case in enumerate(cases, 1):
            print(f"[{idx}] {case['case_name']}")
            print(f"    📁 フォルダ: {case['case_folder_name']}")
            print(f"    🆔 事件ID: {case['case_id']}")
            
            if case.get('ko_evidence_folder_id'):
                print(f"    📊 甲号証: {case['evidence_count']}件")
                if case.get('completed_count'):
                    print(f"    ✅ 完了: {case['completed_count']}件")
            
            if case.get('last_updated'):
                print(f"    🕐 最終更新: {case['last_updated'][:19]}")
            
            print(f"    🔗 URL: {gconfig.GDRIVE_FOLDER_URL_FORMAT.format(folder_id=case['case_folder_id'])}")
            print()
    
    def select_case_interactive(self, cases: List[Dict], allow_new: bool = False) -> Optional[Dict]:
        """対話的に事件を選択
        
        Args:
            cases: 事件情報のリスト
            allow_new: 新規作成オプションを表示するか
        
        Returns:
            選択された事件情報（キャンセルの場合はNone、新規作成の場合は"new"）
        """
        if not cases:
            return None
        
        if len(cases) == 1 and not allow_new:
            print(f"✅ 事件を自動選択: {cases[0]['case_name']}")
            return cases[0]
        
        while True:
            try:
                if allow_new:
                    prompt = f"\n事件を選択 (1-{len(cases)}, {len(cases)+1}=新規作成, 0=終了, r=再読み込み): "
                else:
                    prompt = f"\n事件を選択 (1-{len(cases)}, 0=終了, r=再読み込み): "
                
                choice = input(prompt).strip().lower()
                
                if choice == '0':
                    return None
                
                if choice == 'r':
                    # キャッシュをクリアして再検出
                    if os.path.exists(self.cache_file):
                        os.remove(self.cache_file)
                    new_cases = self.detect_cases(use_cache=False)
                    self.display_cases(new_cases)
                    return self.select_case_interactive(new_cases, allow_new=allow_new)
                
                idx = int(choice) - 1
                
                # 新規作成オプション
                if allow_new and idx == len(cases):
                    return "new"
                
                if 0 <= idx < len(cases):
                    selected = cases[idx]
                    print(f"\n✅ 選択: {selected['case_name']}")
                    return selected
                else:
                    max_num = len(cases) + 1 if allow_new else len(cases)
                    print(f"❌ 1-{max_num} の番号を入力してください。")
            except ValueError:
                print("❌ 数字を入力してください。")
            except KeyboardInterrupt:
                print("\n\n❌ キャンセルしました")
                return None
    
    def get_folder_id(self, case_info: Dict, evidence_type: str, status: str) -> Optional[str]:
        """証拠種別とステータスに応じた適切なフォルダIDを取得
        
        Args:
            case_info: 事件情報
            evidence_type: 証拠種別 ('ko' または 'otsu')
            status: ステータス ('confirmed', 'pending', 'unclassified')
        
        Returns:
            フォルダID（見つからない場合はNone）
        """
        folder_structure = case_info.get('folder_structure', 'legacy')
        
        if folder_structure == 'hierarchical':
            # 階層的構造の場合
            if evidence_type == 'ko':
                return case_info.get('ko_folders', {}).get(status)
            elif evidence_type == 'otsu':
                return case_info.get('otsu_folders', {}).get(status)
        else:
            # 旧形式の場合
            if status == 'confirmed':
                # 確定済み = 甲号証/乙号証フォルダ直下
                if evidence_type == 'ko':
                    return case_info.get('ko_evidence_folder_id')
                elif evidence_type == 'otsu':
                    return case_info.get('otsu_evidence_folder_id')
            else:
                # pending/unclassified = 事件フォルダ直下（証拠種別は混在）
                return case_info.get('legacy_folders', {}).get(status)
        
        return None
    
    def generate_case_config(self, case_info: Dict, output_path: str = "case_config.json") -> bool:
        """事件専用の設定ファイルを生成
        
        Args:
            case_info: 事件情報
            output_path: 出力先パス
        
        Returns:
            成功したかどうか
        """
        try:
            config = {
                "case_id": case_info['case_id'],
                "case_name": case_info['case_name'],
                "case_folder_id": case_info['case_folder_id'],
                "ko_evidence_folder_id": case_info.get('ko_evidence_folder_id'),
                "otsu_evidence_folder_id": case_info.get('otsu_evidence_folder_id'),
                "database_folder_id": case_info.get('database_folder_id'),
                "shared_drive_root_id": self.shared_drive_root_id,
                "created_at": datetime.now().isoformat(),
                "last_selected_at": datetime.now().isoformat()
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 事件設定ファイルを作成: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ 設定ファイル作成エラー: {e}")
            return False


def main():
    """メイン関数（テスト用）"""
    print("\n" + "="*70)
    print("  Phase 1完全版システム - 事件マネージャー（テストモード）")
    print("="*70)
    
    manager = CaseManager()
    
    # 事件を検出
    cases = manager.detect_cases()
    
    # 事件一覧を表示
    manager.display_cases(cases)
    
    # 事件を選択
    selected_case = manager.select_case_interactive(cases)
    
    if selected_case:
        print("\n" + "="*70)
        print("  選択された事件の詳細")
        print("="*70)
        print(json.dumps(selected_case, ensure_ascii=False, indent=2))
        
        # 設定ファイルを生成
        manager.generate_case_config(selected_case)


if __name__ == "__main__":
    main()

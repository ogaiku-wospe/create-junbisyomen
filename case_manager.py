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
from typing import List, Dict, Optional
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# グローバル設定を読み込み
try:
    import global_config as gconfig
except ImportError:
    print("❌ global_config.py が見つかりません")
    sys.exit(1)

# Google Drive APIのスコープ
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


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
        """Google Drive APIサービスを取得"""
        if self.service:
            return self.service
        
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
                if not os.path.exists('credentials.json'):
                    print("\n❌ エラー: credentials.jsonが見つかりません")
                    print("Google Cloud Consoleからcredentials.jsonをダウンロードしてください")
                    return None
                
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
                case_info = self._analyze_case_folder(service, folder)
                if case_info:
                    cases.append(case_info)
                    print(f"  ✅ 事件フォルダ検出: {case_info['case_name']}")
            
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
            
            # 事件フォルダの条件チェック
            is_case_folder = any(
                indicator in item_names 
                for indicator in gconfig.CASE_FOLDER_INDICATORS
            )
            
            if not is_case_folder:
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
                'completed_count': 0
            }
            
            # 証拠フォルダを検索
            for item in items:
                if item['mimeType'] == 'application/vnd.google-apps.folder':
                    if item['name'] == gconfig.EVIDENCE_FOLDER_NAME_KO:
                        case_info['ko_evidence_folder_id'] = item['id']
                        # 証拠数をカウント
                        case_info['evidence_count'] = self._count_files_in_folder(
                            service, item['id']
                        )
                    elif item['name'] == gconfig.EVIDENCE_FOLDER_NAME_OTSU:
                        case_info['otsu_evidence_folder_id'] = item['id']
                    elif item['name'] == gconfig.DATABASE_FOLDER_NAME:
                        case_info['database_folder_id'] = item['id']
            
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
    
    def select_case_interactive(self, cases: List[Dict]) -> Optional[Dict]:
        """対話的に事件を選択
        
        Args:
            cases: 事件情報のリスト
        
        Returns:
            選択された事件情報（キャンセルの場合はNone）
        """
        if not cases:
            return None
        
        if len(cases) == 1:
            print(f"✅ 事件を自動選択: {cases[0]['case_name']}")
            return cases[0]
        
        while True:
            try:
                choice = input(f"\n事件を選択 (1-{len(cases)}, 0=終了, r=再読み込み): ").strip().lower()
                
                if choice == '0':
                    return None
                
                if choice == 'r':
                    # キャッシュをクリアして再検出
                    if os.path.exists(self.cache_file):
                        os.remove(self.cache_file)
                    new_cases = self.detect_cases(use_cache=False)
                    self.display_cases(new_cases)
                    return self.select_case_interactive(new_cases)
                
                idx = int(choice) - 1
                if 0 <= idx < len(cases):
                    selected = cases[idx]
                    print(f"\n✅ 選択: {selected['case_name']}")
                    return selected
                else:
                    print(f"❌ 1-{len(cases)} の番号を入力してください。")
            except ValueError:
                print("❌ 数字を入力してください。")
            except KeyboardInterrupt:
                print("\n\n❌ キャンセルしました")
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

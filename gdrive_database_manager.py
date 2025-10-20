"""
Google Drive Database Manager

database.jsonをGoogle Driveで管理するためのヘルパークラス
ローカルキャッシュを使用せず、全ての操作をGoogle Drive上で直接実行します。
"""

import os
import json
import logging
from typing import Dict, Optional, List
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

logger = logging.getLogger(__name__)


class GDriveDatabaseManager:
    """Google Drive上のdatabase.jsonを管理"""
    
    DATABASE_FILENAME = "database.json"
    
    def __init__(self, service, case_folder_id: str):
        """
        Args:
            service: Google Drive APIサービスインスタンス
            case_folder_id: 事件フォルダのID
        """
        self.service = service
        self.case_folder_id = case_folder_id
        self._database_file_id: Optional[str] = None
        
    def _find_database_file(self) -> Optional[str]:
        """事件フォルダ内のdatabase.jsonを検索
        
        Returns:
            ファイルID（見つからない場合はNone）
        """
        try:
            query = f"name='{self.DATABASE_FILENAME}' and '{self.case_folder_id}' in parents and trashed=false"
            
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)',
                supportsAllDrives=True,
                includeItemsFromAllDrives=True
            ).execute()
            
            files = results.get('files', [])
            
            if files:
                self._database_file_id = files[0]['id']
                logger.info(f"✅ database.json検出: {self._database_file_id}")
                return self._database_file_id
            else:
                logger.info("📄 database.jsonが存在しません（新規作成が必要）")
                return None
                
        except Exception as e:
            logger.error(f"❌ database.json検索エラー: {e}")
            return None
    
    def load_database(self) -> Dict:
        """Google Driveからdatabase.jsonを読み込み
        
        Returns:
            データベース辞書（存在しない場合は初期構造を返す）
        """
        try:
            # ファイルIDを取得
            file_id = self._database_file_id or self._find_database_file()
            
            if not file_id:
                logger.info("📝 新規database.jsonを作成します")
                return self._create_initial_database()
            
            # Google Driveからダウンロード
            request = self.service.files().get_media(
                fileId=file_id,
                supportsAllDrives=True
            )
            
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            # JSONをパース
            fh.seek(0)
            content = fh.read().decode('utf-8')
            
            if not content or content.strip() == '':
                logger.warning("⚠️ database.jsonが空です。初期構造を返します")
                return self._create_initial_database()
            
            database = json.loads(content)
            logger.info("✅ database.json読み込み成功")
            return database
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON解析エラー: {e}")
            return self._create_initial_database()
        except Exception as e:
            logger.error(f"❌ database.json読み込みエラー: {e}")
            return self._create_initial_database()
    
    def save_database(self, database: Dict) -> bool:
        """database.jsonをGoogle Driveに保存
        
        Args:
            database: 保存するデータベース辞書
            
        Returns:
            成功: True, 失敗: False
        """
        try:
            # タイムスタンプを更新
            if 'metadata' not in database:
                database['metadata'] = {}
            database['metadata']['last_updated'] = datetime.now().isoformat()
            
            # 一時ファイルに書き込み
            temp_path = f"/tmp/{self.DATABASE_FILENAME}"
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(database, f, ensure_ascii=False, indent=2)
            
            # ファイルIDを取得
            file_id = self._database_file_id or self._find_database_file()
            
            media = MediaFileUpload(
                temp_path,
                mimetype='application/json',
                resumable=True
            )
            
            if file_id:
                # 既存ファイルを更新
                self.service.files().update(
                    fileId=file_id,
                    media_body=media,
                    supportsAllDrives=True
                ).execute()
                logger.info("✅ database.json更新成功")
            else:
                # 新規ファイルを作成
                file_metadata = {
                    'name': self.DATABASE_FILENAME,
                    'parents': [self.case_folder_id],
                    'mimeType': 'application/json'
                }
                
                file = self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id',
                    supportsAllDrives=True
                ).execute()
                
                self._database_file_id = file.get('id')
                logger.info(f"✅ database.json作成成功: {self._database_file_id}")
            
            # 一時ファイルを削除
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ database.json保存エラー: {e}")
            return False
    
    def get_evidence_by_id(self, evidence_id: str) -> Optional[Dict]:
        """証拠IDで証拠情報を取得
        
        Args:
            evidence_id: 証拠ID (例: "ko001", "tmp_001")
            
        Returns:
            証拠情報辞書（見つからない場合はNone）
        """
        database = self.load_database()
        evidence_list = database.get('evidence', [])
        
        for evidence in evidence_list:
            if evidence.get('evidence_id') == evidence_id:
                return evidence
            # temp_idもチェック
            if evidence.get('temp_id') == evidence_id:
                return evidence
        
        return None
    
    def get_all_evidence(self, status: Optional[str] = None) -> List[Dict]:
        """全証拠を取得
        
        Args:
            status: フィルタするステータス ('pending', 'completed', None=全て)
            
        Returns:
            証拠情報のリスト
        """
        database = self.load_database()
        evidence_list = database.get('evidence', [])
        
        if status:
            return [e for e in evidence_list if e.get('status') == status]
        
        return evidence_list
    
    def add_evidence(self, evidence_data: Dict) -> bool:
        """証拠を追加
        
        Args:
            evidence_data: 追加する証拠データ
            
        Returns:
            成功: True, 失敗: False
        """
        try:
            database = self.load_database()
            
            if 'evidence' not in database:
                database['evidence'] = []
            
            database['evidence'].append(evidence_data)
            
            return self.save_database(database)
            
        except Exception as e:
            logger.error(f"❌ 証拠追加エラー: {e}")
            return False
    
    def update_evidence(self, evidence_id: str, updates: Dict) -> bool:
        """証拠情報を更新
        
        Args:
            evidence_id: 証拠ID (evidence_id または temp_id)
            updates: 更新する内容
            
        Returns:
            成功: True, 失敗: False
        """
        try:
            database = self.load_database()
            evidence_list = database.get('evidence', [])
            
            updated = False
            for evidence in evidence_list:
                if evidence.get('evidence_id') == evidence_id or evidence.get('temp_id') == evidence_id:
                    evidence.update(updates)
                    updated = True
                    break
            
            if not updated:
                logger.warning(f"⚠️ 証拠が見つかりません: {evidence_id}")
                return False
            
            return self.save_database(database)
            
        except Exception as e:
            logger.error(f"❌ 証拠更新エラー: {e}")
            return False
    
    def delete_evidence(self, evidence_id: str) -> bool:
        """証拠を削除
        
        Args:
            evidence_id: 証拠ID
            
        Returns:
            成功: True, 失敗: False
        """
        try:
            database = self.load_database()
            evidence_list = database.get('evidence', [])
            
            original_count = len(evidence_list)
            database['evidence'] = [
                e for e in evidence_list 
                if e.get('evidence_id') != evidence_id and e.get('temp_id') != evidence_id
            ]
            
            if len(database['evidence']) == original_count:
                logger.warning(f"⚠️ 証拠が見つかりません: {evidence_id}")
                return False
            
            return self.save_database(database)
            
        except Exception as e:
            logger.error(f"❌ 証拠削除エラー: {e}")
            return False
    
    def _create_initial_database(self) -> Dict:
        """初期database.json構造を作成
        
        Returns:
            初期データベース辞書
        """
        return {
            "version": "3.0",
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "case_folder_id": self.case_folder_id,
                "storage_type": "google_drive"
            },
            "evidence": []
        }
    
    def get_next_evidence_number(self, side: str) -> int:
        """次の証拠番号を取得
        
        Args:
            side: 'ko' または 'otsu'
            
        Returns:
            次の証拠番号（例: 1, 2, 3...）
        """
        database = self.load_database()
        evidence_list = database.get('evidence', [])
        
        # 確定済み証拠のみをカウント
        prefix = side.lower()
        max_number = 0
        
        for evidence in evidence_list:
            if evidence.get('status') == 'completed':
                evidence_id = evidence.get('evidence_id', '')
                if evidence_id.startswith(prefix):
                    import re
                    match = re.match(r'[a-z]+([0-9]+)', evidence_id)
                    if match:
                        number = int(match.group(1))
                        max_number = max(max_number, number)
        
        return max_number + 1
    
    def get_next_temp_number(self) -> int:
        """次の仮番号を取得
        
        Returns:
            次の仮番号（例: 1, 2, 3...）
        """
        database = self.load_database()
        evidence_list = database.get('evidence', [])
        
        max_number = 0
        
        for evidence in evidence_list:
            temp_id = evidence.get('temp_id', '')
            if temp_id.startswith('tmp_'):
                try:
                    number = int(temp_id.replace('tmp_', ''))
                    max_number = max(max_number, number)
                except ValueError:
                    continue
        
        return max_number + 1


def create_database_manager(case_manager, case_info: Dict) -> Optional[GDriveDatabaseManager]:
    """GDriveDatabaseManagerインスタンスを作成
    
    Args:
        case_manager: CaseManagerインスタンス
        case_info: 事件情報辞書
        
    Returns:
        GDriveDatabaseManagerインスタンス（失敗時はNone）
    """
    try:
        service = case_manager.get_google_drive_service()
        if not service:
            logger.error("❌ Google Drive認証が必要です")
            return None
        
        case_folder_id = case_info.get('case_folder_id')
        if not case_folder_id:
            logger.error("❌ 事件フォルダIDが見つかりません")
            return None
        
        return GDriveDatabaseManager(service, case_folder_id)
        
    except Exception as e:
        logger.error(f"❌ GDriveDatabaseManager作成エラー: {e}")
        return None

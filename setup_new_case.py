#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1完全版システム - 自動フォルダ作成セットアップ

【使用方法】
    python3 setup_new_case_auto.py

【機能】
    - 共有ドライブIDのみ指定
    - 事件フォルダと証拠フォルダを自動作成
    - config.pyとdatabase.jsonを自動生成
"""

import os
import json
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle


# Google Drive APIのスコープ
SCOPES = ['https://www.googleapis.com/auth/drive.file']


def print_banner():
    """バナーを表示"""
    print("\n" + "="*70)
    print("  Phase 1完全版システム - 自動セットアップ")
    print("  ✨ フォルダ自動作成モード")
    print("="*70)
    print("\n共有ドライブIDを指定すると、自動的にフォルダを作成します！\n")


def get_google_drive_service():
    """Google Drive APIサービスを取得"""
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
    
    return build('drive', 'v3', credentials=creds)


def create_folder(service, folder_name, parent_folder_id=None, is_shared_drive=False):
    """Google Driveにフォルダを作成
    
    Args:
        service: Google Drive APIサービス
        folder_name: 作成するフォルダ名
        parent_folder_id: 親フォルダのID（共有ドライブIDまたは事件フォルダID）
        is_shared_drive: 共有ドライブかどうか
    
    Returns:
        作成されたフォルダのID
    """
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    
    if parent_folder_id:
        file_metadata['parents'] = [parent_folder_id]
    
    try:
        if is_shared_drive and parent_folder_id:
            # 共有ドライブの場合
            folder = service.files().create(
                body=file_metadata,
                supportsAllDrives=True,
                fields='id, name, webViewLink'
            ).execute()
        else:
            # 個人ドライブの場合
            folder = service.files().create(
                body=file_metadata,
                fields='id, name, webViewLink'
            ).execute()
        
        print(f"  ✅ フォルダ作成: {folder_name}")
        print(f"     ID: {folder.get('id')}")
        print(f"     URL: {folder.get('webViewLink', 'N/A')}")
        
        return folder.get('id')
        
    except Exception as e:
        print(f"  ❌ フォルダ作成失敗: {e}")
        return None


def input_with_default(prompt, default=""):
    """デフォルト値付き入力"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ").strip()


def get_case_info():
    """事件情報を取得"""
    print("━"*70)
    print("  ステップ1: 事件情報の入力")
    print("━"*70)
    
    case_info = {}
    
    print("\n【基本情報】")
    case_info['case_id'] = input_with_default(
        "事件ID（英数字）",
        "case_" + datetime.now().strftime("%Y%m%d")
    )
    
    case_info['case_name'] = input_with_default(
        "事件名（例: 損害賠償請求事件）",
        ""
    )
    
    case_info['case_number'] = input_with_default(
        "事件番号（例: 令和7年(ワ)第1234号）",
        "未定"
    )
    
    print("\n【当事者情報】")
    case_info['plaintiff'] = input_with_default("原告名", "")
    case_info['defendant'] = input_with_default("被告名", "")
    case_info['court'] = input_with_default("管轄裁判所", "東京地方裁判所")
    
    print("\n【証拠番号設定】")
    case_info['evidence_prefix_ko'] = input_with_default(
        "甲号証の接頭辞（例: ko）", "ko"
    )
    case_info['evidence_prefix_otsu'] = input_with_default(
        "乙号証の接頭辞（例: otsu）", "otsu"
    )
    
    return case_info


def get_drive_settings():
    """Google Drive設定を取得"""
    print("\n" + "━"*70)
    print("  ステップ2: Google Drive設定")
    print("━"*70)
    
    print("\n💡 フォルダIDの取得方法:")
    print("  1. Google Driveでフォルダを開く")
    print("  2. ブラウザのURLを確認")
    print("     例: https://drive.google.com/drive/folders/1abc...xyz")
    print("  3. 'folders/' の後の文字列がフォルダID\n")
    
    drive_settings = {}
    
    use_shared_drive = input_with_default(
        "共有ドライブを使用しますか？ (y/n)", "n"
    ).lower() == 'y'
    
    if use_shared_drive:
        drive_settings['shared_drive_id'] = input_with_default(
            "共有ドライブID（ここだけ手動で指定）", ""
        )
        drive_settings['is_shared_drive'] = True
    else:
        drive_settings['shared_drive_id'] = None
        drive_settings['is_shared_drive'] = False
    
    create_otsu = input_with_default(
        "乙号証フォルダも作成しますか？ (y/n)", "y"
    ).lower() == 'y'
    drive_settings['create_otsu'] = create_otsu
    
    return drive_settings


def create_folder_structure(service, case_info, drive_settings):
    """フォルダ構造を自動作成"""
    print("\n" + "━"*70)
    print("  ステップ3: フォルダ自動作成")
    print("━"*70)
    
    folder_ids = {}
    
    # 親フォルダID（共有ドライブまたは個人Drive）
    parent_id = drive_settings.get('shared_drive_id')
    is_shared = drive_settings.get('is_shared_drive', False)
    
    print(f"\n📁 フォルダ作成を開始します...")
    print(f"   親フォルダ: {'共有ドライブ' if is_shared else '個人Drive'}")
    if parent_id:
        print(f"   ID: {parent_id}\n")
    
    # 1. 事件フォルダを作成
    case_folder_name = f"{case_info['case_id']}_{case_info['case_name']}"
    print(f"[1/3] 事件フォルダを作成中...")
    case_folder_id = create_folder(
        service, 
        case_folder_name, 
        parent_id,
        is_shared
    )
    
    if not case_folder_id:
        print("\n❌ 事件フォルダの作成に失敗しました")
        return None
    
    folder_ids['case_folder_id'] = case_folder_id
    
    # 2. 甲号証フォルダを作成
    print(f"\n[2/3] 甲号証フォルダを作成中...")
    ko_folder_id = create_folder(
        service,
        "甲号証",
        case_folder_id,
        is_shared
    )
    
    if not ko_folder_id:
        print("\n❌ 甲号証フォルダの作成に失敗しました")
        return None
    
    folder_ids['ko_evidence_folder_id'] = ko_folder_id
    
    # 3. 乙号証フォルダを作成（オプション）
    if drive_settings.get('create_otsu'):
        print(f"\n[3/3] 乙号証フォルダを作成中...")
        otsu_folder_id = create_folder(
            service,
            "乙号証",
            case_folder_id,
            is_shared
        )
        folder_ids['otsu_evidence_folder_id'] = otsu_folder_id
    else:
        folder_ids['otsu_evidence_folder_id'] = None
        print(f"\n[3/3] 乙号証フォルダはスキップしました")
    
    print("\n✅ すべてのフォルダが作成されました！\n")
    
    return folder_ids


def confirm_settings(case_info, drive_settings, folder_ids):
    """設定内容を確認"""
    print("\n" + "="*70)
    print("  設定内容の確認")
    print("="*70)
    
    print("\n【事件情報】")
    print(f"  - 事件ID: {case_info['case_id']}")
    print(f"  - 事件名: {case_info['case_name']}")
    print(f"  - 事件番号: {case_info['case_number']}")
    print(f"  - 原告: {case_info['plaintiff']}")
    print(f"  - 被告: {case_info['defendant']}")
    print(f"  - 管轄: {case_info['court']}")
    
    print("\n【Google Drive】")
    print(f"  - 共有ドライブ: {'使用' if drive_settings['is_shared_drive'] else '個人Drive'}")
    if drive_settings.get('shared_drive_id'):
        print(f"  - 共有ドライブID: {drive_settings['shared_drive_id']}")
    print(f"  - 事件フォルダID: {folder_ids['case_folder_id']}")
    print(f"  - 甲号証フォルダID: {folder_ids['ko_evidence_folder_id']}")
    if folder_ids.get('otsu_evidence_folder_id'):
        print(f"  - 乙号証フォルダID: {folder_ids['otsu_evidence_folder_id']}")
    
    print("\n" + "="*70)
    
    confirm = input_with_default("\nconfig.pyを作成しますか？ (y/n)", "y")
    return confirm.lower() == 'y'


def generate_config_file(case_info, drive_settings, folder_ids, output_path="config.py"):
    """config.pyを生成"""
    
    # 既存のconfig.pyをバックアップ
    if os.path.exists(output_path):
        backup_path = f"config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        os.rename(output_path, backup_path)
        print(f"\n📦 既存のconfig.pyをバックアップ: {backup_path}")
    
    shared_drive_id = drive_settings.get('shared_drive_id')
    
    config_content = f'''"""
Phase 1 完全自動化システム - 設定ファイル
事件: {case_info['case_name']}
作成日: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
自動セットアップで作成
"""

import os
from datetime import datetime

# ================================
# バージョン情報
# ================================

SYSTEM_VERSION = "3.0.0"
SYSTEM_NAME = "Phase 1 Complete Automation System"
DATABASE_VERSION = "3.0"

# ================================
# 事件情報
# ================================

CASE_ID = "{case_info['case_id']}"
CASE_NAME = "{case_info['case_name']}"
CASE_NUMBER = "{case_info['case_number']}"

PLAINTIFF = "{case_info['plaintiff']}"
DEFENDANT = "{case_info['defendant']}"
COURT = "{case_info['court']}"

EVIDENCE_PREFIX_KO = "{case_info['evidence_prefix_ko']}"
EVIDENCE_PREFIX_OTSU = "{case_info['evidence_prefix_otsu']}"

# ================================
# Google Drive設定（自動作成済み）
# ================================

SHARED_DRIVE_ID = {f'"{shared_drive_id}"' if shared_drive_id else 'None'}
CASE_FOLDER_ID = "{folder_ids['case_folder_id']}"
KO_EVIDENCE_FOLDER_ID = "{folder_ids['ko_evidence_folder_id']}"
OTSU_EVIDENCE_FOLDER_ID = {f'"{folder_ids.get("otsu_evidence_folder_id")}"' if folder_ids.get('otsu_evidence_folder_id') else 'None'}

DATABASE_FOLDER_ID = None
TEMP_FOLDER_ID = None
LOGS_FOLDER_ID = None

GDRIVE_FILE_URL_FORMAT = "https://drive.google.com/file/d/{{file_id}}/view"
GDRIVE_FOLDER_URL_FORMAT = "https://drive.google.com/drive/folders/{{folder_id}}"
GDRIVE_DOWNLOAD_URL_FORMAT = "https://drive.google.com/uc?id={{file_id}}&export=download"

# ================================
# OpenAI API設定
# ================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-4o"
OPENAI_MAX_TOKENS = 16000
OPENAI_TEMPERATURE = 0.1

# ================================
# ファイル形式対応設定
# ================================

SUPPORTED_FORMATS = {{
    'image': {{
        'extensions': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.heic', '.heif', '.tiff', '.tif'],
        'mime_types': ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp', 'image/heic', 'image/heif', 'image/tiff']
    }},
    'document': {{
        'extensions': ['.pdf', '.docx', '.doc', '.odt', '.rtf', '.txt'],
        'mime_types': ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword']
    }},
    'spreadsheet': {{
        'extensions': ['.xlsx', '.xls', '.csv', '.ods'],
        'mime_types': ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel', 'text/csv']
    }},
    'web': {{
        'extensions': ['.html', '.htm', '.mhtml', '.mht'],
        'mime_types': ['text/html', 'application/xhtml+xml', 'message/rfc822']
    }},
    'video': {{
        'extensions': ['.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm', '.m4v'],
        'mime_types': ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska', 'video/webm']
    }},
    'audio': {{
        'extensions': ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac', '.wma'],
        'mime_types': ['audio/mpeg', 'audio/wav', 'audio/x-m4a', 'audio/aac', 'audio/ogg', 'audio/flac']
    }}
}}

# ================================
# 品質保証設定
# ================================

QUALITY_THRESHOLDS = {{
    'completeness_score': 90.0,
    'confidence_score': 80.0,
    'verbalization_level': 4,
    'metadata_coverage': 95.0
}}

# ================================
# その他の設定
# ================================

LOG_LEVEL = "INFO"
DATABASE_OUTPUT_PATH = "database.json"
TIMEZONE = "Asia/Tokyo"
TEMP_DIR = "/tmp/phase1_temp"

# ================================
# タイムスタンプ用関数
# ================================

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f+09:00")
'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"\n✅ config.pyを作成しました: {output_path}")


def generate_database_file(case_info, output_path="database.json"):
    """database.jsonを初期化"""
    
    if os.path.exists(output_path):
        backup_path = f"database_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.rename(output_path, backup_path)
        print(f"📦 既存のdatabase.jsonをバックアップ: {backup_path}")
    
    database = {
        "case_info": {
            "case_id": case_info['case_id'],
            "case_name": case_info['case_name'],
            "case_number": case_info['case_number'],
            "plaintiff": case_info['plaintiff'],
            "defendant": case_info['defendant'],
            "court": case_info['court']
        },
        "evidence": [],
        "metadata": {
            "version": "3.0",
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "total_evidence_count": 0,
            "completed_count": 0
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, ensure_ascii=False, indent=2)
    
    print(f"✅ database.jsonを初期化しました: {output_path}")


def print_next_steps(folder_ids):
    """次のステップを表示"""
    print("\n" + "="*70)
    print("  🎉 セットアップ完了！")
    print("="*70)
    
    print("\n✅ 作成されたファイル:")
    print("  - config.py: 事件専用設定")
    print("  - database.json: データベース")
    
    print("\n📁 作成されたGoogle Driveフォルダ:")
    print(f"  - 事件フォルダ: https://drive.google.com/drive/folders/{folder_ids['case_folder_id']}")
    print(f"  - 甲号証フォルダ: https://drive.google.com/drive/folders/{folder_ids['ko_evidence_folder_id']}")
    if folder_ids.get('otsu_evidence_folder_id'):
        print(f"  - 乙号証フォルダ: https://drive.google.com/drive/folders/{folder_ids['otsu_evidence_folder_id']}")
    
    print("\n📋 次のステップ:")
    print("  1. OpenAI APIキーを設定:")
    print("     export OPENAI_API_KEY='sk-proj-your-key'")
    print()
    print("  2. 証拠ファイルを甲号証フォルダにアップロード")
    print()
    print("  3. システムを実行:")
    print("     python3 run_phase1.py")
    
    print("\n" + "="*70 + "\n")


def main():
    """メイン関数"""
    print_banner()
    
    # Google Drive APIサービス取得
    print("🔐 Google Drive認証中...")
    service = get_google_drive_service()
    
    if not service:
        print("\n❌ Google Drive認証に失敗しました")
        print("credentials.jsonを確認してください")
        return
    
    print("✅ Google Drive認証成功\n")
    
    # 事件情報の取得
    case_info = get_case_info()
    
    # Drive設定の取得
    drive_settings = get_drive_settings()
    
    # フォルダ構造を自動作成
    folder_ids = create_folder_structure(service, case_info, drive_settings)
    
    if not folder_ids:
        print("\n❌ フォルダ作成に失敗しました")
        return
    
    # 設定内容の確認
    if not confirm_settings(case_info, drive_settings, folder_ids):
        print("\n❌ セットアップをキャンセルしました")
        return
    
    # ファイルの生成
    print("\n" + "━"*70)
    print("  ファイルを生成中...")
    print("━"*70)
    
    generate_config_file(case_info, drive_settings, folder_ids)
    generate_database_file(case_info)
    
    # 次のステップを表示
    print_next_steps(folder_ids)


if __name__ == "__main__":
    main()
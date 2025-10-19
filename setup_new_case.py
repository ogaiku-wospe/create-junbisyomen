#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1完全版システム - 新規事件セットアップスクリプト

【使用方法】
    python3 setup_new_case.py

【機能】
    - 対話形式で事件情報を入力
    - config.pyを自動生成
    - database.jsonを初期化
    - 設定の妥当性を検証

【作成されるファイル】
    - config.py: 事件専用設定ファイル
    - database.json: 初期化されたデータベース
"""

import os
import json
from datetime import datetime


def print_banner():
    """バナーを表示"""
    print("\n" + "="*70)
    print("  Phase 1完全版システム - 新規事件セットアップウィザード")
    print("="*70)
    print("\nこのウィザードは、新しい事件用の設定ファイルを作成します。")
    print("質問に答えて、事件情報を入力してください。\n")


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
        "事件ID（英数字、任意）",
        "case_" + datetime.now().strftime("%Y%m%d")
    )
    
    case_info['case_name'] = input_with_default(
        "事件名（例: 損害賠償請求事件）",
        ""
    )
    
    case_info['case_number'] = input_with_default(
        "事件番号（例: 令和6年(ワ)第1234号）",
        "未定"
    )
    
    print("\n【当事者情報】")
    case_info['plaintiff'] = input_with_default(
        "原告名",
        ""
    )
    
    case_info['defendant'] = input_with_default(
        "被告名",
        ""
    )
    
    case_info['court'] = input_with_default(
        "管轄裁判所",
        "東京地方裁判所"
    )
    
    print("\n【証拠番号設定】")
    case_info['evidence_prefix_ko'] = input_with_default(
        "甲号証の接頭辞（例: ko, kou, k）",
        "ko"
    )
    
    case_info['evidence_prefix_otsu'] = input_with_default(
        "乙号証の接頭辞（例: otsu, otsu, o）",
        "otsu"
    )
    
    return case_info


def get_gdrive_info():
    """Google Drive情報を取得"""
    print("\n" + "━"*70)
    print("  ステップ2: Google Drive設定")
    print("━"*70)
    
    print("\n💡 Google DriveフォルダIDの取得方法:")
    print("  1. Google Driveでフォルダを開く")
    print("  2. ブラウザのURLを確認")
    print("     例: https://drive.google.com/drive/folders/1abc...xyz")
    print("  3. 'folders/' の後の文字列がフォルダID")
    print()
    
    gdrive_info = {}
    
    use_shared_drive = input_with_default(
        "共有ドライブを使用しますか？ (y/n)",
        "n"
    ).lower() == 'y'
    
    if use_shared_drive:
        gdrive_info['shared_drive_id'] = input_with_default(
            "共有ドライブID",
            ""
        )
    else:
        gdrive_info['shared_drive_id'] = None
    
    gdrive_info['case_folder_id'] = input_with_default(
        "事件フォルダID（必須）",
        ""
    )
    
    gdrive_info['ko_evidence_folder_id'] = input_with_default(
        "甲号証フォルダID（必須）",
        ""
    )
    
    use_otsu = input_with_default(
        "乙号証フォルダを設定しますか？ (y/n)",
        "n"
    ).lower() == 'y'
    
    if use_otsu:
        gdrive_info['otsu_evidence_folder_id'] = input_with_default(
            "乙号証フォルダID",
            ""
        )
    else:
        gdrive_info['otsu_evidence_folder_id'] = None
    
    return gdrive_info


def get_openai_info():
    """OpenAI設定を取得"""
    print("\n" + "━"*70)
    print("  ステップ3: OpenAI API設定")
    print("━"*70)
    
    openai_info = {}
    
    api_key = os.getenv("OPENAI_API_KEY", "")
    if api_key:
        print(f"\n✅ 環境変数にOpenAI APIキーが設定されています")
        print(f"   キー: {api_key[:20]}...")
    else:
        print("\n⚠️ 環境変数にOpenAI APIキーが設定されていません")
        print("   セットアップ後に環境変数を設定してください:")
        print("   export OPENAI_API_KEY='sk-proj-your-key'")
    
    openai_info['model'] = input_with_default(
        "\n使用するモデル",
        "gpt-4o"
    )
    
    return openai_info


def confirm_settings(case_info, gdrive_info, openai_info):
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
    print(f"  - 共有ドライブID: {gdrive_info['shared_drive_id'] or '（個人Drive）'}")
    print(f"  - 事件フォルダID: {gdrive_info['case_folder_id']}")
    print(f"  - 甲号証フォルダID: {gdrive_info['ko_evidence_folder_id']}")
    print(f"  - 乙号証フォルダID: {gdrive_info['otsu_evidence_folder_id'] or '（未設定）'}")
    
    print("\n【OpenAI API】")
    print(f"  - モデル: {openai_info['model']}")
    print(f"  - APIキー: {'設定済み' if os.getenv('OPENAI_API_KEY') else '未設定'}")
    
    print("\n" + "="*70)
    
    confirm = input_with_default("\nこの内容で設定ファイルを作成しますか？ (y/n)", "y")
    return confirm.lower() == 'y'


def generate_config_file(case_info, gdrive_info, openai_info, output_path="config.py"):
    """config.pyを生成"""
    
    # 既存のconfig.pyをバックアップ
    if os.path.exists(output_path):
        backup_path = f"config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        os.rename(output_path, backup_path)
        print(f"\n📦 既存のconfig.pyをバックアップしました: {backup_path}")
    
    config_content = f'''"""
Phase 1 完全自動化システム - 設定ファイル
事件: {case_info['case_name']}
作成日: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
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
# Google Drive設定
# ================================

SHARED_DRIVE_ID = {f'"{gdrive_info["shared_drive_id"]}"' if gdrive_info['shared_drive_id'] else 'None'}
CASE_FOLDER_ID = "{gdrive_info['case_folder_id']}"
KO_EVIDENCE_FOLDER_ID = "{gdrive_info['ko_evidence_folder_id']}"
OTSU_EVIDENCE_FOLDER_ID = {f'"{gdrive_info["otsu_evidence_folder_id"]}"' if gdrive_info['otsu_evidence_folder_id'] else 'None'}

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
OPENAI_MODEL = "{openai_info['model']}"
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
    'presentation': {{
        'extensions': ['.pptx', '.ppt', '.odp'],
        'mime_types': ['application/vnd.openxmlformats-officedocument.presentationml.presentation', 'application/vnd.ms-powerpoint']
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
    }},
    'archive': {{
        'extensions': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
        'mime_types': ['application/zip', 'application/x-rar-compressed', 'application/x-7z-compressed', 'application/x-tar']
    }},
    'email': {{
        'extensions': ['.eml', '.msg', '.emlx'],
        'mime_types': ['message/rfc822', 'application/vnd.ms-outlook']
    }}
}}

# ================================
# ファイル処理設定
# ================================

IMAGE_MAX_SIZE = (3840, 2160)
IMAGE_COMPRESSION_QUALITY = 90

PDF_MAX_PAGES = 100
PDF_DPI = 300

VIDEO_FRAME_SAMPLE_RATE = 30
VIDEO_MAX_FRAMES = 10

AUDIO_TRANSCRIPTION_MODEL = "whisper-1"

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
# ログ設定
# ================================

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
LOG_FILE = "phase1_complete.log"

# ================================
# 出力設定
# ================================

DATABASE_OUTPUT_PATH = "database.json"
AUTO_BACKUP = True
BACKUP_INTERVAL = 10

# ================================
# Phase 1プロンプト設定
# ================================

PHASE1_PROMPT_PATH = None

PROMPT_TEMPLATE_VARS = {{
    "case_name": CASE_NAME,
    "plaintiff": PLAINTIFF,
    "defendant": DEFENDANT,
    "court": COURT,
    "case_number": CASE_NUMBER
}}

# ================================
# その他の設定
# ================================

TIMEZONE = "Asia/Tokyo"
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TEMP_DIR = "/tmp/phase1_temp"
'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"\n✅ config.pyを作成しました: {output_path}")


def generate_database_file(case_info, output_path="database.json"):
    """database.jsonを初期化"""
    
    # 既存のdatabase.jsonをバックアップ
    if os.path.exists(output_path):
        backup_path = f"database_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.rename(output_path, backup_path)
        print(f"📦 既存のdatabase.jsonをバックアップしました: {backup_path}")
    
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
            "completed_count": 0,
            "in_progress_count": 0
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, ensure_ascii=False, indent=2)
    
    print(f"✅ database.jsonを初期化しました: {output_path}")


def print_next_steps():
    """次のステップを表示"""
    print("\n" + "="*70)
    print("  セットアップ完了！")
    print("="*70)
    
    print("\n✅ 以下のファイルが作成されました:")
    print("  - config.py: 事件専用設定ファイル")
    print("  - database.json: 初期化されたデータベース")
    
    print("\n📋 次のステップ:")
    print("  1. OpenAI APIキーを環境変数に設定（未設定の場合）:")
    print("     export OPENAI_API_KEY='sk-proj-your-key'")
    print()
    print("  2. credentials.jsonを配置:")
    print("     Google Cloud Consoleからダウンロードして配置")
    print()
    print("  3. システムを実行:")
    print("     python3 run_phase1.py")
    print()
    print("  4. 証拠ファイルを分析:")
    print("     メニューで「1」を選択して証拠番号を入力")
    
    print("\n" + "="*70 + "\n")


def main():
    """メイン関数"""
    print_banner()
    
    # 事件情報の取得
    case_info = get_case_info()
    
    # Google Drive情報の取得
    gdrive_info = get_gdrive_info()
    
    # OpenAI情報の取得
    openai_info = get_openai_info()
    
    # 設定内容の確認
    if not confirm_settings(case_info, gdrive_info, openai_info):
        print("\n❌ セットアップをキャンセルしました")
        return
    
    # ファイルの生成
    print("\n" + "━"*70)
    print("  ファイルを生成中...")
    print("━"*70)
    
    generate_config_file(case_info, gdrive_info, openai_info)
    generate_database_file(case_info)
    
    # 次のステップを表示
    print_next_steps()


if __name__ == "__main__":
    main()

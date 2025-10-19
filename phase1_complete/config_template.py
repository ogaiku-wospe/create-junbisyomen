"""
Phase 1 完全自動化システム - 設定ファイル（汎用版テンプレート）

【使用方法】
1. このファイルをコピーして config.py にリネーム
2. 下記の設定を自分の事件に合わせて変更
3. システムを実行
"""

import os
from datetime import datetime

# ================================
# バージョン情報
# ================================

SYSTEM_VERSION = "3.0.0"
SYSTEM_NAME = "Phase 1 Complete Automation System (Generic)"
DATABASE_VERSION = "3.0"

# ================================
# 事件情報（ここを変更）
# ================================

# 【重要】以下を自分の事件に合わせて変更してください

CASE_ID = "meiyokison"  # 事件ID（任意、英数字推奨）例: "traffic_accident", "contract_dispute"
CASE_NAME = "提起前_名誉毀損等損害賠償請求事件"  # 事件名（日本語OK）
CASE_NUMBER = "未定"  # 事件番号（例: "令和6年(ワ)第1234号"）

# 当事者情報
PLAINTIFF = "小原瞳（しろくまクラフト）"  # 原告名
DEFENDANT = "石村まゆか（SUB×MISSION）"  # 被告名
COURT = "東京地方裁判所"  # 管轄裁判所

# 証拠番号の接頭辞
EVIDENCE_PREFIX_KO = "ko"   # 甲号証の接頭辞（例: "ko" → ko1, ko2, ...）
EVIDENCE_PREFIX_OTSU = "otsu"  # 乙号証の接頭辞（例: "otsu" → otsu1, otsu2, ...）

# ================================
# Google Drive設定（ここを変更）
# ================================

# 【重要】Google DriveのフォルダIDを自分の事件用に設定

# Google Drive共有ドライブID（任意、個人Driveの場合は None）
SHARED_DRIVE_ID = "0AO6q4_G7DmYSUk9PVA"  # 例: "0AO6q4_G7DmYSUk9PVA" または None

# 事件フォルダID（事件全体のルートフォルダ）
CASE_FOLDER_ID = "1uux0sGt8j3EUI08nOFkBre_99jR8sN-a"  # 必須

# 証拠フォルダID
KO_EVIDENCE_FOLDER_ID = "1NkwibbiUTzaznJGtF0kvsxFER3t62ZMx"  # 甲号証フォルダ
OTSU_EVIDENCE_FOLDER_ID = None  # 乙号証フォルダ（必要に応じて設定）

# その他のフォルダID（オプション）
DATABASE_FOLDER_ID = None  # database.json保存先
TEMP_FOLDER_ID = None  # 一時ファイル保存先
LOGS_FOLDER_ID = None  # ログファイル保存先

# Google Drive URL形式（通常は変更不要）
GDRIVE_FILE_URL_FORMAT = "https://drive.google.com/file/d/{file_id}/view"
GDRIVE_FOLDER_URL_FORMAT = "https://drive.google.com/drive/folders/{folder_id}"
GDRIVE_DOWNLOAD_URL_FORMAT = "https://drive.google.com/uc?id={file_id}&export=download"

# ================================
# フォルダIDの取得方法
# ================================
"""
Google DriveフォルダIDの取得方法:

1. Google Driveでフォルダを開く
2. ブラウザのURLを確認
   例: https://drive.google.com/drive/folders/1uux0sGt8j3EUI08nOFkBre_99jR8sN-a
3. "folders/" の後の文字列がフォルダID
   → "1uux0sGt8j3EUI08nOFkBre_99jR8sN-a"

共有ドライブの場合:
1. 共有ドライブのトップページを開く
2. URLの "/drive/u/0/folders/" の後の文字列がドライブID
"""

# ================================
# OpenAI API設定
# ================================

# OpenAI APIキー（環境変数から取得、直接書き込み非推奨）
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# 使用するモデル
OPENAI_MODEL = "gpt-4o"  # 推奨: gpt-4o (Vision対応)
# その他のオプション: "gpt-4o-mini", "gpt-4-turbo"

# APIパラメータ
OPENAI_MAX_TOKENS = 16000  # 最大トークン数
OPENAI_TEMPERATURE = 0.1  # 温度（0.0-2.0、低いほど一貫性重視）

# ================================
# ファイル形式対応設定
# ================================

# サポートするファイル形式（通常は変更不要）
SUPPORTED_FORMATS = {
    # 画像形式
    'image': {
        'extensions': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.heic', '.heif', '.tiff', '.tif'],
        'mime_types': ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp', 'image/heic', 'image/heif', 'image/tiff']
    },
    # 文書形式
    'document': {
        'extensions': ['.pdf', '.docx', '.doc', '.odt', '.rtf', '.txt'],
        'mime_types': ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword']
    },
    # スプレッドシート形式
    'spreadsheet': {
        'extensions': ['.xlsx', '.xls', '.csv', '.ods'],
        'mime_types': ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel', 'text/csv']
    },
    # プレゼンテーション形式
    'presentation': {
        'extensions': ['.pptx', '.ppt', '.odp'],
        'mime_types': ['application/vnd.openxmlformats-officedocument.presentationml.presentation', 'application/vnd.ms-powerpoint']
    },
    # ウェブ形式
    'web': {
        'extensions': ['.html', '.htm', '.mhtml', '.mht'],
        'mime_types': ['text/html', 'application/xhtml+xml', 'message/rfc822']
    },
    # 動画形式
    'video': {
        'extensions': ['.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm', '.m4v'],
        'mime_types': ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska', 'video/webm']
    },
    # 音声形式
    'audio': {
        'extensions': ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac', '.wma'],
        'mime_types': ['audio/mpeg', 'audio/wav', 'audio/x-m4a', 'audio/aac', 'audio/ogg', 'audio/flac']
    },
    # アーカイブ形式
    'archive': {
        'extensions': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
        'mime_types': ['application/zip', 'application/x-rar-compressed', 'application/x-7z-compressed', 'application/x-tar']
    },
    # メール形式
    'email': {
        'extensions': ['.eml', '.msg', '.emlx'],
        'mime_types': ['message/rfc822', 'application/vnd.ms-outlook']
    }
}

# ================================
# ファイル処理設定
# ================================

# 画像処理設定
IMAGE_MAX_SIZE = (3840, 2160)  # 最大解像度（4K）
IMAGE_COMPRESSION_QUALITY = 90  # JPEG圧縮品質（1-100）

# PDF処理設定
PDF_MAX_PAGES = 100  # 一度に処理する最大ページ数
PDF_DPI = 300  # PDF→画像変換時のDPI

# 動画処理設定
VIDEO_FRAME_SAMPLE_RATE = 30  # フレームサンプリングレート（秒）
VIDEO_MAX_FRAMES = 10  # 抽出する最大フレーム数

# 音声処理設定
AUDIO_TRANSCRIPTION_MODEL = "whisper-1"  # 音声認識モデル

# ================================
# 品質保証設定
# ================================

# 品質スコアの閾値
QUALITY_THRESHOLDS = {
    'completeness_score': 90.0,  # 完全性スコア（%）
    'confidence_score': 80.0,    # 信頼度スコア（%）
    'verbalization_level': 4,    # 言語化レベル（1-5）
    'metadata_coverage': 95.0    # メタデータカバレッジ（%）
}

# ================================
# ログ設定
# ================================

LOG_LEVEL = "INFO"  # ログレベル: DEBUG, INFO, WARNING, ERROR
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
LOG_FILE = "phase1_complete.log"

# ================================
# 出力設定
# ================================

# database.jsonの保存先
DATABASE_OUTPUT_PATH = "database.json"

# バックアップ設定
AUTO_BACKUP = True  # 自動バックアップを有効化
BACKUP_INTERVAL = 10  # バックアップ間隔（証拠数）

# ================================
# Phase 1プロンプト設定
# ================================

# Phase 1プロンプトファイルのパス（オプション）
PHASE1_PROMPT_PATH = None  # 例: "Phase1_EvidenceAnalysis.txt"

# プロンプトテンプレート変数（事件情報を自動挿入）
PROMPT_TEMPLATE_VARS = {
    "case_name": CASE_NAME,
    "plaintiff": PLAINTIFF,
    "defendant": DEFENDANT,
    "court": COURT,
    "case_number": CASE_NUMBER
}

# ================================
# その他の設定
# ================================

# タイムゾーン
TIMEZONE = "Asia/Tokyo"

# 日付フォーマット
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# 一時ファイルの保存先
TEMP_DIR = "/tmp/phase1_temp"

# ================================
# 設定の検証
# ================================

def validate_config():
    """設定の妥当性を検証"""
    errors = []
    
    # 必須項目のチェック
    if not CASE_NAME:
        errors.append("❌ CASE_NAME が設定されていません")
    
    if not PLAINTIFF:
        errors.append("❌ PLAINTIFF が設定されていません")
    
    if not DEFENDANT:
        errors.append("❌ DEFENDANT が設定されていません")
    
    if not CASE_FOLDER_ID:
        errors.append("❌ CASE_FOLDER_ID が設定されていません")
    
    if not KO_EVIDENCE_FOLDER_ID:
        errors.append("❌ KO_EVIDENCE_FOLDER_ID が設定されていません")
    
    if not OPENAI_API_KEY:
        errors.append("❌ OPENAI_API_KEY が設定されていません（環境変数を確認してください）")
    
    # エラーがあれば表示
    if errors:
        print("\n🔧 設定エラーが見つかりました:\n")
        for error in errors:
            print(f"  {error}")
        print("\n💡 config.py を編集して設定を修正してください\n")
        return False
    else:
        print("✅ 設定の検証が完了しました")
        return True


# ================================
# 設定情報の表示
# ================================

def print_config():
    """現在の設定を表示"""
    print("\n" + "="*60)
    print("  Phase 1完全版システム - 現在の設定")
    print("="*60)
    print(f"\n📋 事件情報:")
    print(f"  - 事件ID: {CASE_ID}")
    print(f"  - 事件名: {CASE_NAME}")
    print(f"  - 事件番号: {CASE_NUMBER}")
    print(f"  - 原告: {PLAINTIFF}")
    print(f"  - 被告: {DEFENDANT}")
    print(f"  - 管轄: {COURT}")
    
    print(f"\n📁 Google Drive:")
    print(f"  - 共有ドライブID: {SHARED_DRIVE_ID or '（個人Drive）'}")
    print(f"  - 事件フォルダID: {CASE_FOLDER_ID}")
    print(f"  - 甲号証フォルダID: {KO_EVIDENCE_FOLDER_ID}")
    print(f"  - 乙号証フォルダID: {OTSU_EVIDENCE_FOLDER_ID or '（未設定）'}")
    
    print(f"\n🤖 OpenAI API:")
    print(f"  - モデル: {OPENAI_MODEL}")
    print(f"  - APIキー: {'設定済み' if OPENAI_API_KEY else '未設定'}")
    
    print(f"\n📊 品質保証:")
    print(f"  - 完全性スコア閾値: {QUALITY_THRESHOLDS['completeness_score']}%")
    print(f"  - 信頼度スコア閾値: {QUALITY_THRESHOLDS['confidence_score']}%")
    print(f"  - 言語化レベル閾値: {QUALITY_THRESHOLDS['verbalization_level']}")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    # 設定ファイルを直接実行した場合は検証と表示
    print_config()
    validate_config()

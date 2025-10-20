"""
Phase 1 完全自動化システム - 設定ファイル（完全版）
"""

import os
from datetime import datetime

# .envファイルを読み込む
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ .envファイルを読み込みました")
except ImportError:
    print("⚠️ python-dotenvが未インストール - .envファイルは読み込まれません")
except Exception as e:
    print(f"⚠️ .envファイルの読み込みに失敗: {e}")

# ================================
# バージョン情報
# ================================

SYSTEM_VERSION = "2.0.0"
SYSTEM_NAME = "Phase 1 Complete Automation System"
DATABASE_VERSION = "3.0"  # 完全版対応

# ================================
# Google Drive設定
# ================================

# 事件情報
CASE_ID = "meiyokison"
CASE_NAME = "提起前_名誉毀損等損害賠償請求事件"
CASE_NUMBER = "未定"

# Google Drive フォルダID
SHARED_DRIVE_ID = "0AO6q4_G7DmYSUk9PVA"
CASE_FOLDER_ID = "1uux0sGt8j3EUI08nOFkBre_99jR8sN-a"
KO_EVIDENCE_FOLDER_ID = "1NkwibbiUTzaznJGtF0kvsxFER3t62ZMx"
OTSU_EVIDENCE_FOLDER_ID = None
DATABASE_FOLDER_ID = None
TEMP_FOLDER_ID = None
LOGS_FOLDER_ID = None

# Google Drive URL形式
GDRIVE_FILE_URL_FORMAT = "https://drive.google.com/file/d/{file_id}/view"
GDRIVE_FOLDER_URL_FORMAT = "https://drive.google.com/drive/folders/{folder_id}"

# ================================
# OpenAI API設定
# ================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-4o"
OPENAI_MAX_TOKENS = 16000
OPENAI_TEMPERATURE = 0.1  # 一貫性重視

# ================================
# ファイル形式対応設定
# ================================

# サポートするファイル形式
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
# 分析設定
# ================================

# 完全言語化レベル（1-5）
VERBALIZATION_LEVEL_TARGET = 4  # レベル4: 完全言語化
VERBALIZATION_LEVEL_MINIMUM = 3  # 最低レベル3

# OCR設定
OCR_ENABLED = True
OCR_LANGUAGES = ['jpn', 'eng', 'chi_sim']  # 日本語、英語、中国語簡体字
OCR_ENGINE = 'tesseract'  # tesseract, google_vision, azure

# メタデータ抽出レベル
METADATA_EXTRACTION_LEVEL = 'full'  # basic, standard, full

# ハッシュアルゴリズム
HASH_ALGORITHM = 'sha256'  # md5, sha1, sha256

# ================================
# 動画・音声処理設定
# ================================

# 動画処理
VIDEO_FRAME_EXTRACTION_INTERVAL = 5  # 秒ごとにフレーム抽出
VIDEO_MAX_FRAMES = 50  # 最大抽出フレーム数
VIDEO_THUMBNAIL_TIMESTAMPS = [0, 0.25, 0.5, 0.75, 1.0]  # サムネイル位置（相対位置）

# 音声処理
AUDIO_TRANSCRIPTION_ENGINE = 'whisper'  # whisper, google_speech, azure_speech
AUDIO_LANGUAGE_AUTO_DETECT = True
AUDIO_SPEAKER_DIARIZATION = True  # 話者分離

# ================================
# URL生成設定
# ================================

# Google Drive URL生成
GENERATE_GDRIVE_URLS = True
GENERATE_DOWNLOAD_URLS = True
URL_EXPIRY_HOURS = 24  # ダウンロードURL有効期限

# ================================
# ローカルパス設定
# ================================

LOCAL_WORK_DIR = "/Users/ogaiku/create-junbisyomen"
LOCAL_TEMP_DIR = "/tmp/phase1_complete_temp"
LOCAL_CACHE_DIR = "/tmp/phase1_cache"
LOCAL_PROMPT_PATH = f"{LOCAL_WORK_DIR}/prompts/Phase1_EvidenceAnalysis.txt"

# ================================
# 証拠番号設定
# ================================

EVIDENCE_PREFIX_OUR = "甲"
EVIDENCE_PREFIX_OPPONENT = "乙"
EVIDENCE_NUMBER_FORMAT = "{prefix}{number:03d}"  # 例: 甲070
EVIDENCE_FILENAME_FORMAT = "{prefix}{number}_{sanitized_name}"

# ================================
# データベース構造設定
# ================================

# database.json構造バージョン3.0の仕様
DATABASE_STRUCTURE_VERSION = {
    "version": "3.0",
    "features": [
        "complete_metadata",
        "gdrive_urls",
        "file_hashes",
        "full_verbalization",
        "multi_format_support",
        "ocr_results",
        "transcription_results",
        "confidence_scores",
        "version_tracking"
    ]
}

# ================================
# ログ設定
# ================================

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_FILE_PATH = f"{LOCAL_TEMP_DIR}/phase1_complete.log"

# ================================
# エラー処理設定
# ================================

MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 5
RETRY_EXPONENTIAL_BACKOFF = True

# API呼び出しタイムアウト
API_TIMEOUT_SECONDS = 300  # 5分
LARGE_FILE_TIMEOUT_SECONDS = 600  # 10分（動画等）

# ================================
# パフォーマンス設定
# ================================

# 並列処理設定（将来実装用）
ENABLE_PARALLEL_PROCESSING = False
MAX_PARALLEL_WORKERS = 3

# キャッシュ設定
ENABLE_CACHING = True
CACHE_EXPIRY_HOURS = 24

# ================================
# タイムスタンプ形式
# ================================

TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%f+09:00"  # ISO 8601形式（ミリ秒含む）
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"

def get_timestamp():
    """現在時刻をISO 8601形式で取得（ミリ秒含む）"""
    return datetime.now().strftime(TIMESTAMP_FORMAT)

def get_date():
    """現在日付を取得"""
    return datetime.now().strftime(DATE_FORMAT)

def get_time():
    """現在時刻を取得"""
    return datetime.now().strftime(TIME_FORMAT)

def get_filename_timestamp():
    """ファイル名用タイムスタンプ"""
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")

# ================================
# ファイルサイズ制限
# ================================

MAX_FILE_SIZE = {
    'image': 50 * 1024 * 1024,      # 50MB
    'document': 100 * 1024 * 1024,   # 100MB
    'video': 500 * 1024 * 1024,      # 500MB
    'audio': 100 * 1024 * 1024,      # 100MB
    'other': 200 * 1024 * 1024       # 200MB
}

# ================================
# 品質保証設定
# ================================

# 分析品質チェック
ENABLE_QUALITY_CHECK = True
QUALITY_CHECK_THRESHOLDS = {
    'completeness': 0.9,        # 完全性: 90%以上
    'verbalization': 0.85,      # 言語化: 85%以上
    'metadata_coverage': 0.95,  # メタデータカバレッジ: 95%以上
    'confidence': 0.8           # 信頼度: 80%以上
}

# ================================
# 画像処理設定
# ================================

IMAGE_MAX_SIZE = (3840, 2160)  # 最大解像度（4K）
IMAGE_COMPRESSION_QUALITY = 90  # JPEG圧縮品質（1-100）

# ================================
# PDF処理設定
# ================================

PDF_MAX_PAGES = 100  # 一度に処理する最大ページ数
PDF_DPI = 300  # PDF→画像変換時のDPI
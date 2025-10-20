"""
Phase 1 完全版システム - グローバル設定ファイル

【概要】
大元の共有ドライブIDのみを設定し、配下の事件フォルダを自動検出します。
複数事件の同時並行管理が可能です。

【使用方法】
1. このファイルで SHARED_DRIVE_ROOT_ID を設定
2. 共有ドライブ配下に事件フォルダを作成
3. run_phase1.py を実行すると事件を自動検出・選択可能
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
# グローバル設定
# ================================

SYSTEM_VERSION = "3.0.0"
SYSTEM_NAME = "Phase 1 Multi-Case Management System"
DATABASE_VERSION = "3.0"

# ================================
# 【重要】大元の共有ドライブID設定
# ================================

# ここに大元の共有ドライブIDを設定してください
# この配下に複数の事件フォルダが配置されることを想定しています
SHARED_DRIVE_ROOT_ID = "0AO6q4_G7DmYSUk9PVA"

# 事件フォルダの命名規則
# 事件フォルダ名の形式: {CASE_ID}_{CASE_NAME}
# 例: "meiyokison_名誉毀損等損害賠償請求事件"
CASE_FOLDER_NAME_FORMAT = "{case_id}_{case_name}"

# 証拠フォルダの標準名
EVIDENCE_FOLDER_NAME_KO = "甲号証"
EVIDENCE_FOLDER_NAME_OTSU = "乙号証"
UNCLASSIFIED_FOLDER_NAME = "未分類"
PENDING_FOLDER_NAME = "整理済み_未確定"  # 仮番号ファイル用
DATABASE_FOLDER_NAME = "database"
TEMP_FOLDER_NAME = "temp"
LOGS_FOLDER_NAME = "logs"

# ================================
# 事件検出設定
# ================================

# 事件フォルダとして認識する条件
# 以下のファイル/フォルダが存在すれば事件フォルダとみなす
CASE_FOLDER_INDICATORS = [
    "甲号証",  # 甲号証フォルダが存在
    "config.json",  # または config.json が存在
    "database.json"  # または database.json が存在
]

# 自動検出を有効化
AUTO_DETECT_CASES = True

# ================================
# OpenAI API設定
# ================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-4o"
OPENAI_MAX_TOKENS = 16000
OPENAI_TEMPERATURE = 0.1  # 一貫性重視

# コンテンツポリシーチェック無効化フラグ
# true: コンテンツポリシーチェックを無効化（誤検出が多い場合に有効化）
# false: コンテンツポリシーチェックを有効化（デフォルト）
DISABLE_CONTENT_POLICY_CHECK = os.getenv("DISABLE_CONTENT_POLICY_CHECK", "true").lower() == "true"

# Anthropic Claude API設定（OpenAI Vision API拒否時のフォールバック用）
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Claude 4.x世代モデル - 最高品質の証拠分析用
ANTHROPIC_MODEL = "claude-sonnet-4-20250514"  # Claude Sonnet 4.x (最高品質)
# フォールバックモデル（多段階フォールバック）
ANTHROPIC_MODEL_FALLBACK_1 = "claude-sonnet-3-7-20250219"  # Claude Sonnet 3.7 (高品質)
ANTHROPIC_MODEL_FALLBACK_2 = "claude-haiku-4-20250514"  # Claude Haiku 4.x (高速・大容量)

# Vision API設定
ANTHROPIC_MAX_TOKENS = 8000  # Sonnet 4.xの出力上限に合わせる
ANTHROPIC_TEMPERATURE = 0.1  # 一貫性重視

# Vision APIフォールバック戦略（4段階）
# 1. OpenAI GPT-4o Vision (プライマリ)
# 2. Claude Sonnet 4.x Vision (最高品質セカンダリ) ← NEW!
# 3. Claude Sonnet 3.7 Vision (高品質ターシャリ) ← NEW!
# 4. Claude Haiku 4.x Vision (高速フォールバック) ← NEW!
# 5. OCRテキストベース分析 (最終手段)
ENABLE_CLAUDE_FALLBACK = os.getenv("ENABLE_CLAUDE_FALLBACK", "true").lower() == "true"

# ================================
# Google Drive URL形式
# ================================

GDRIVE_FILE_URL_FORMAT = "https://drive.google.com/file/d/{file_id}/view"
GDRIVE_FOLDER_URL_FORMAT = "https://drive.google.com/drive/folders/{folder_id}"
GDRIVE_DOWNLOAD_URL_FORMAT = "https://drive.google.com/uc?id={file_id}&export=download"

# ================================
# ファイル形式対応設定
# ================================

SUPPORTED_FORMATS = {
    # 画像形式
    'image': {
        'extensions': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.heic', '.heif', '.tiff', '.tif'],
        'mime_types': ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp', 'image/heic', 'image/heif', 'image/tiff']
    },
    # PDF形式（独立カテゴリ - Vision APIでの処理が必要）
    'pdf': {
        'extensions': ['.pdf'],
        'mime_types': ['application/pdf']
    },
    # 文書形式（Word等）
    'document': {
        'extensions': ['.docx', '.doc', '.odt', '.rtf', '.txt'],
        'mime_types': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword']
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
# 品質保証設定
# ================================

ENABLE_QUALITY_CHECK = True
QUALITY_THRESHOLDS = {
    'completeness_score': 90.0,
    'confidence_score': 80.0,
    'verbalization_level': 4,
    'metadata_coverage': 95.0
}

# エイリアス（後方互換性のため）
QUALITY_CHECK_THRESHOLDS = {
    'completeness': 90.0,
    'confidence': 80.0,
    'verbalization': 4,
    'metadata': 95.0
}

# ================================
# ローカルパス設定
# ================================

LOCAL_WORK_DIR = "/Users/ogaiku/create-junbisyomen"
LOCAL_TEMP_DIR = "/tmp/phase1_complete_temp"
LOCAL_CACHE_DIR = "/tmp/phase1_cache"
LOCAL_PROMPT_PATH = f"{LOCAL_WORK_DIR}/prompts/Phase1_EvidenceAnalysis.txt"

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

API_TIMEOUT_SECONDS = 300  # 5分
LARGE_FILE_TIMEOUT_SECONDS = 600  # 10分（動画等）

# ================================
# パフォーマンス設定
# ================================

ENABLE_PARALLEL_PROCESSING = False
MAX_PARALLEL_WORKERS = 3

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
# 画像処理設定
# ================================

IMAGE_MAX_SIZE = (3840, 2160)  # 最大解像度（4K）
IMAGE_COMPRESSION_QUALITY = 90  # JPEG圧縮品質（1-100）

# ================================
# PDF処理設定
# ================================

PDF_MAX_PAGES = 100  # 一度に処理する最大ページ数
PDF_DPI = 300  # PDF→画像変換時のDPI

# ================================
# 動画・音声処理設定
# ================================

VIDEO_FRAME_EXTRACTION_INTERVAL = 5  # 秒ごとにフレーム抽出
VIDEO_MAX_FRAMES = 50  # 最大抽出フレーム数
VIDEO_THUMBNAIL_TIMESTAMPS = [0, 0.25, 0.5, 0.75, 1.0]  # サムネイル位置（相対位置）

AUDIO_TRANSCRIPTION_ENGINE = 'whisper'  # whisper, google_speech, azure_speech
AUDIO_LANGUAGE_AUTO_DETECT = True
AUDIO_SPEAKER_DIARIZATION = True  # 話者分離

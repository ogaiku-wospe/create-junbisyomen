# Phase 1完全版システム使用ガイド

## 📖 目次

1. [システム概要](#システム概要)
2. [環境セットアップ](#環境セットアップ)
3. [実行方法](#実行方法)
4. [出力形式](#出力形式)
5. [トラブルシューティング](#トラブルシューティング)
6. [FAQ](#faq)

---

## システム概要

Phase 1完全版は、証拠ファイルの**完全自動分析システム**です。

### 主要機能

✅ **完全メタデータ抽出**
- ファイルハッシュ（SHA-256, MD5, SHA-1）
- Google Drive URL（直リンク、ダウンロードリンク、プレビューリンク）
- EXIF情報（画像）、文書プロパティ（PDF/Word）
- ファイルサイズ、作成日時、変更日時

✅ **全形式対応**
- 画像: JPEG, PNG, HEIC, GIF, WebP, TIFF
- 文書: PDF, Word (DOCX/DOC), Excel, PowerPoint
- ウェブ: HTML, MHTML
- 動画: MP4, MOV, AVI, MKV, WebM
- 音声: MP3, WAV, M4A, AAC, FLAC
- メール: EML, MSG
- アーカイブ: ZIP, RAR, 7Z

✅ **GPT-4o Vision統合**
- 196KBの完全言語化プロンプト使用
- 画像・PDF・Wordファイルの完全分析
- レベル4の完全言語化達成

✅ **品質保証**
- 完全性スコア（90%以上目標）
- 信頼度スコア（80%以上目標）
- 言語化レベル評価（レベル4/5）

✅ **database.json v3.0**
- プログラム完全解釈可能
- JSONスキーマ定義
- 原文参照不要

---

## 環境セットアップ

### ステップ1: システム要件

- **OS**: Linux (Ubuntu 20.04+), macOS (10.15+), Windows (WSL2)
- **Python**: 3.8以上
- **メモリ**: 4GB以上推奨
- **ディスク**: 10GB以上の空き容量

### ステップ2: Pythonパッケージのインストール

```bash
# 基本パッケージ
pip install --quiet --no-input \
    google-auth \
    google-auth-oauthlib \
    google-auth-httplib2 \
    google-api-python-client \
    openai \
    pillow \
    python-magic \
    pypdf2 \
    python-docx \
    openpyxl \
    beautifulsoup4 \
    mutagen

# 追加パッケージ（オプション）
pip install --quiet --no-input \
    pdf2image \
    pytesseract \
    pillow-heif
```

### ステップ3: システムライブラリのインストール

#### Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install -y \
    libheif-examples \
    libmagic1 \
    tesseract-ocr \
    tesseract-ocr-jpn \
    poppler-utils
```

#### macOS

```bash
brew install libheif libmagic tesseract tesseract-lang poppler
```

#### Windows (WSL2)

```bash
# WSL2のUbuntuで上記Ubuntu/Debianの手順を実行
```

### ステップ4: Google Drive API認証

1. **Google Cloud Consoleでプロジェクト作成**
   - https://console.cloud.google.com/
   - 新しいプロジェクトを作成

2. **Google Drive APIを有効化**
   - APIとサービス > ライブラリ
   - "Google Drive API" を検索して有効化

3. **OAuth 2.0クライアントIDを作成**
   - APIとサービス > 認証情報
   - 認証情報を作成 > OAuth クライアント ID
   - アプリケーションの種類: デスクトップアプリ
   - credentials.jsonをダウンロード

4. **credentials.jsonを配置**
   ```bash
   cp ~/Downloads/credentials.json /home/user/phase1_complete/
   ```

### ステップ5: OpenAI API設定

```bash
# 環境変数に設定（推奨）
export OPENAI_API_KEY="sk-proj-your-actual-api-key-here"

# または、config.pyを直接編集
# nano /home/user/phase1_complete/config.py
# OPENAI_API_KEY = "sk-proj-your-actual-api-key-here"
```

### ステップ6: インストール確認

```bash
cd /home/user/phase1_complete

# Pythonモジュールの確認
python -c "import google.auth, openai, PIL, pypdf2, docx; print('✅ すべてのモジュールがインストールされています')"

# OpenAI APIキーの確認
python -c "import os; print('✅ OpenAI APIキー:', os.getenv('OPENAI_API_KEY')[:20] + '...')"

# Google認証ファイルの確認
ls -lh credentials.json
```

---

## 実行方法

### 方法1: 対話的実行（初心者向け）

```bash
cd /home/user/phase1_complete
python run_phase1.py
```

**メニュー操作:**

```
==============================================================
  Phase 1完全版システム - 証拠分析
  提起前_名誉毀損等損害賠償請求事件
==============================================================

【実行モード】
  1. 証拠番号を指定して分析（例: ko70）
  2. 範囲指定して分析（例: ko70-73）
  3. 個別ファイルを分析（Google Drive URL指定）
  4. 未処理の証拠を自動検索・分析
  5. database.jsonの状態確認
  6. 終了
--------------------------------------------------------------

選択してください (1-6): 1
証拠番号を入力してください（例: ko70 または ko70-73）: ko70

[処理開始...]
```

### 方法2: コマンドライン実行（上級者向け）

```bash
cd /home/user/phase1_complete

# 単一証拠の分析
python phase1_cli.py ko70 --file /path/to/ko70.pdf

# 複数証拠の一括分析
python phase1_cli.py ko70 ko71 ko72 ko73 --file-dir /path/to/evidence_files/

# 詳細ログ出力
python phase1_cli.py ko70 --file /path/to/ko70.pdf --verbose

# カスタム出力先
python phase1_cli.py ko70 --file /path/to/ko70.pdf --output custom_database.json
```

**コマンドラインオプション:**

| オプション | 説明 | 例 |
|-----------|------|-----|
| `--file` | 証拠ファイルのパス（単一） | `--file /path/to/ko70.pdf` |
| `--file-dir` | 証拠ファイルのディレクトリ（複数） | `--file-dir /path/to/evidence/` |
| `--output` | 出力先database.jsonのパス | `--output custom_db.json` |
| `--verbose` | 詳細ログを出力 | `--verbose` |

### 方法3: Python統合（プログラマー向け）

```python
from run_phase1 import Phase1Runner

# ランナーの初期化
runner = Phase1Runner()

# 単一証拠の処理
success = runner.process_evidence("ko70")
if success:
    print("✅ 処理成功")
else:
    print("❌ 処理失敗")

# database.jsonの状態確認
runner.show_database_status()
```

### 方法4: カスタムワークフロー

```bash
cd /home/user/phase1_complete
python custom_workflow.py
```

**カスタマイズ例:**

```python
# バッチ処理
evidence_list = [
    {"number": "ko70", "file": "/path/to/ko70.pdf"},
    {"number": "ko71", "file": "/path/to/ko71.pdf"},
]
custom_batch_process(evidence_list, "/output/directory/")

# 品質チェック
issues = custom_quality_check("database.json")

# HTMLレポート生成
custom_export_report("database.json", "phase1_report.html")
```

---

## 出力形式

### database.json v3.0 の構造

```json
{
  "case_info": {
    "case_name": "提起前_名誉毀損等損害賠償請求事件",
    "plaintiff": "小原瞳（しろくまクラフト）",
    "defendant": "石村まゆか（SUB×MISSION）",
    "court": "東京地方裁判所"
  },
  "evidence": [
    {
      "evidence_number": "ko70",
      "complete_metadata": {
        "file_hash": {
          "sha256": "abc123def456...",
          "md5": "def456ghi789...",
          "sha1": "ghi789jkl012..."
        },
        "file_size_bytes": 1234567,
        "file_name": "ko70_evidence.pdf",
        "mime_type": "application/pdf",
        "created_at": "2024-01-15T10:30:00",
        "modified_at": "2024-01-15T10:35:00",
        "google_drive_urls": {
          "web_view_link": "https://drive.google.com/file/d/abc123/view",
          "download_link": "https://drive.google.com/uc?id=abc123&export=download",
          "preview_link": "https://drive.google.com/file/d/abc123/preview"
        },
        "exif": {
          "Make": "Apple",
          "Model": "iPhone 14 Pro",
          "DateTime": "2024:01:15 10:30:00",
          "GPSLatitude": null,
          "GPSLongitude": null
        },
        "document_properties": {
          "author": "小原瞳",
          "title": "証拠資料",
          "subject": "名誉毀損事件",
          "keywords": "SNS, 誹謗中傷",
          "created": "2024-01-15T10:30:00",
          "modified": "2024-01-15T10:35:00"
        }
      },
      "phase1_complete_analysis": {
        "evidence_type": "デジタル証拠（スクリーンショット）",
        "content_summary": "【完全な内容要約】\n本証拠は、2024年1月15日にTwitter（現X）で発生した...",
        "detailed_description": {
          "visual_elements": [
            {
              "type": "screenshot",
              "platform": "Twitter (X)",
              "content": "被告による誹謗中傷投稿",
              "timestamp_visible": "2024-01-15 10:25",
              "author": "@ishimura_mayuka"
            }
          ],
          "text_content": {
            "main_text": "「小原瞳は詐欺師だ」という明確な名誉毀損発言",
            "additional_text": "リプライ、いいね数、リツイート数も確認可能"
          },
          "technical_details": {
            "screenshot_device": "iPhone 14 Pro",
            "screenshot_time": "2024-01-15T10:30:00",
            "image_resolution": "1170x2532",
            "image_format": "PNG"
          }
        },
        "quality_scores": {
          "completeness_score": 95.0,
          "confidence_score": 90.0,
          "verbalization_level": 4,
          "metadata_coverage": 98.0
        },
        "legal_relevance": {
          "relevance_score": 95,
          "applicable_laws": [
            "民法第709条（不法行為）",
            "民法第710条（財産以外の損害の賠償）"
          ],
          "evidence_strength": "強",
          "admissibility": "高"
        },
        "technical_authenticity": {
          "hash_verified": true,
          "metadata_intact": true,
          "tampering_likelihood": "低",
          "verification_notes": "EXIF情報とファイルハッシュが一致"
        },
        "analysis_metadata": {
          "analyzed_by": "GPT-4o Vision",
          "analysis_date": "2025-10-19T12:34:56",
          "prompt_version": "v3.0 (196KB)",
          "model_version": "gpt-4o-2024-11-20"
        }
      },
      "status": "completed",
      "processed_at": "2025-10-19T12:34:56"
    }
  ],
  "metadata": {
    "version": "3.0",
    "created_at": "2025-10-19T10:00:00",
    "last_updated": "2025-10-19T14:30:00",
    "total_evidence_count": 1,
    "completed_count": 1,
    "in_progress_count": 0
  }
}
```

### 品質スコアの解釈

| スコア | 範囲 | 意味 |
|-------|------|------|
| **完全性スコア** | 0-100% | メタデータとコンテンツの完全性 |
| - 高 | 90-100% | すべての情報が完全に記録されている |
| - 中 | 70-89% | 一部の情報が不足している |
| - 低 | 0-69% | 重要な情報が欠けている |
| **信頼度スコア** | 0-100% | 分析結果の信頼性 |
| - 高 | 80-100% | 高精度の分析結果 |
| - 中 | 60-79% | 一部に不確実性がある |
| - 低 | 0-59% | 再分析が推奨される |
| **言語化レベル** | 1-5 | 原文参照の必要性 |
| - 5 | 完全 | 原文不要、プログラム完全解釈可能 |
| - 4 | 高 | ほぼ原文不要、一部参照推奨 |
| - 3 | 中 | 原文参照を推奨 |
| - 2 | 低 | 原文参照が必要 |
| - 1 | 最低 | 原文なしでは理解不可 |

---

## トラブルシューティング

### 問題1: モジュールのインポートエラー

**エラーメッセージ:**
```
ModuleNotFoundError: No module named 'google.auth'
```

**解決策:**
```bash
pip install --quiet --no-input google-auth google-auth-oauthlib google-api-python-client
```

---

### 問題2: OpenAI APIエラー

**エラーメッセージ:**
```
openai.error.AuthenticationError: Incorrect API key provided
```

**解決策:**
```bash
# APIキーを確認
echo $OPENAI_API_KEY

# APIキーを再設定
export OPENAI_API_KEY="sk-proj-your-actual-api-key-here"

# 確認
python -c "import os; print(os.getenv('OPENAI_API_KEY')[:20])"
```

---

### 問題3: Google Drive認証エラー

**エラーメッセージ:**
```
FileNotFoundError: credentials.json not found
```

**解決策:**
```bash
# credentials.jsonの配置確認
ls -lh /home/user/phase1_complete/credentials.json

# ない場合はGoogle Cloud Consoleからダウンロード
# https://console.cloud.google.com/

# 配置
cp ~/Downloads/credentials.json /home/user/phase1_complete/
```

---

### 問題4: HEIC画像の処理エラー

**エラーメッセージ:**
```
ValueError: Cannot process HEIC format
```

**解決策:**

**Ubuntu/Debian:**
```bash
sudo apt-get install -y libheif-examples
pip install --quiet --no-input pillow-heif
```

**macOS:**
```bash
brew install libheif
pip install --quiet --no-input pillow-heif
```

---

### 問題5: メモリ不足エラー

**エラーメッセージ:**
```
MemoryError: Unable to allocate array
```

**解決策:**

1. **大容量PDFの処理:**
```python
# config.pyで設定を調整
PDF_MAX_PAGES = 50  # デフォルト100から削減
IMAGE_MAX_SIZE = (1920, 1080)  # デフォルト(3840, 2160)から削減
```

2. **バッチ処理のチャンクサイズ削減:**
```python
# 一度に処理する証拠数を減らす
for chunk in chunks(evidence_list, size=5):  # デフォルト10から削減
    process_chunk(chunk)
```

---

### 問題6: Google Drive API制限

**エラーメッセージ:**
```
google.api_core.exceptions.ResourceExhausted: Quota exceeded
```

**解決策:**

1. **処理間隔を空ける:**
```python
import time
for evidence in evidence_list:
    process_evidence(evidence)
    time.sleep(5)  # 5秒待機
```

2. **Google Cloud ConsoleでQuotaを確認:**
   - https://console.cloud.google.com/
   - APIとサービス > Google Drive API > 割り当て

---

## FAQ

### Q1: ko70-73のような大容量ファイルの処理時間は？

**A:** 処理時間の目安:

| 証拠 | サイズ | 推定時間 |
|------|--------|----------|
| ko70 | 58GB (4ファイル) | 2-3時間 |
| ko71 | 187KB | 5-10分 |
| ko72 | 3.2MB | 10-15分 |
| ko73 | 359KB | 5-10分 |

**注意点:**
- 動画ファイル（ko70）は特に時間がかかります
- OpenAI API呼び出し回数に依存
- ネットワーク速度に依存

---

### Q2: database.json v3.0の容量はどのくらい？

**A:** 1証拠あたり約50-200KB（平均100KB）

- メタデータ: 10-20KB
- AI分析結果: 40-180KB（コンテンツ量に依存）
- 10証拠で約1MB、100証拠で約10MB

---

### Q3: OpenAI APIのコストは？

**A:** GPT-4o Vision使用時の目安:

| ファイルタイプ | トークン数 | コスト（USD） |
|--------------|-----------|--------------|
| 画像（1枚） | 約10,000 | $0.05 |
| PDF（10ページ） | 約30,000 | $0.15 |
| 動画（5分） | 約50,000 | $0.25 |

**ko70-73の推定コスト:**
- ko70（動画4本）: $1.00-2.00
- ko71-73（PDF/画像）: $0.20-0.50
- 合計: **約$1.20-2.50**

---

### Q4: Phase 2との連携方法は？

**A:** database.json v3.0はPhase 2で直接使用可能:

```python
# Phase 2のスクリプトで
import json

with open("database.json", "r") as f:
    database = json.load(f)

for evidence in database["evidence"]:
    # Phase 2の処理
    generate_evidence_list(evidence)
```

原文ファイルへのアクセスは不要、database.jsonだけで完結します。

---

### Q5: エラーが発生した証拠の再処理方法は？

**A:** 個別に再処理が可能:

```bash
# 対話的実行で
python run_phase1.py
# メニュー: 1（証拠番号を指定）
# 証拠番号: ko70

# または CLI で
python phase1_cli.py ko70 --file /path/to/ko70.pdf
```

既存のエントリは自動的に上書きされます。

---

## サポート

### 問題が解決しない場合

1. **ログファイルの確認:**
```bash
cat phase1_complete.log | tail -100
```

2. **詳細ログの有効化:**
```bash
python phase1_cli.py ko70 --file /path/to/ko70.pdf --verbose
```

3. **システム情報の確認:**
```bash
python --version
pip list | grep -E "google|openai|pillow|pypdf"
```

---

## 次のステップ

✅ **Phase 1完了後:**
1. database.json v3.0の品質確認
2. Phase 2（証拠説明書生成）への移行
3. Phase 3（最終文書作成）の準備

✅ **推奨される運用:**
1. 証拠ファイルはGoogle Driveに整理
2. database.jsonは定期的にバックアップ
3. 品質スコアが低い証拠は再分析

---

**最終更新:** 2025-10-19  
**バージョン:** 3.0  
**作成者:** Phase 1完全版システム

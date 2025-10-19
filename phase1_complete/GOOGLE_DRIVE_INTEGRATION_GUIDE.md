# Phase 1完全版システム - Google Drive連携の詳細説明

## 📋 目次

1. [Google Drive連携の概要](#google-drive連携の概要)
2. [入力情報](#入力情報)
3. [出力情報](#出力情報)
4. [認証の仕組み](#認証の仕組み)
5. [データフロー](#データフロー)
6. [フォルダ構造](#フォルダ構造)
7. [セキュリティ](#セキュリティ)

---

## 🔗 Google Drive連携の概要

Phase 1完全版システムは、Google Driveと以下の方法で連携します：

```
┌─────────────────────────────────────────────────────────────┐
│                    Google Drive                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  共有ドライブ または 個人ドライブ                      │  │
│  │  ├── 事件フォルダ/                                    │  │
│  │  │   ├── 甲号証フォルダ/                              │  │
│  │  │   │   ├── ko62.pdf                                │  │
│  │  │   │   ├── ko63.jpg                                │  │
│  │  │   │   └── ko64.docx                               │  │
│  │  │   ├── 乙号証フォルダ/ (オプション)                 │  │
│  │  │   └── database.json (自動保存)                     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          ↕️  API連携
┌─────────────────────────────────────────────────────────────┐
│           Phase 1完全版システム (ローカルPC)                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. 認証 (credentials.json + token.json)            │  │
│  │  2. ファイル検索・ダウンロード                        │  │
│  │  3. メタデータ抽出・AI分析                           │  │
│  │  4. database.json作成                                │  │
│  │  5. database.json自動バックアップ (Google Drive)     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📥 入力情報（Google Drive → システム）

### 1. 設定情報（config.py）

システムが**Google Driveから読み取る**ために必要な情報：

```python
# config.py で設定
SHARED_DRIVE_ID = "0AO6q4_G7DmYSUk9PVA"  # 共有ドライブID（オプション）
CASE_FOLDER_ID = "1uux0sGt8j3EUI08nOFkBre_99jR8sN-a"  # 事件フォルダID
KO_EVIDENCE_FOLDER_ID = "1NkwibbiUTzaznJGtF0kvsxFER3t62ZMx"  # 甲号証フォルダID
OTSU_EVIDENCE_FOLDER_ID = None  # 乙号証フォルダID（オプション）
```

**これらのIDはGoogle DriveのURLから取得します:**

```
例: https://drive.google.com/drive/folders/1NkwibbiUTzaznJGtF0kvsxFER3t62ZMx
                                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                            これがフォルダID
```

### 2. 証拠ファイル

システムが**Google Driveからダウンロード**する証拠ファイル：

| ファイルタイプ | 形式 | 例 |
|--------------|------|-----|
| 画像 | JPEG, PNG, HEIC等 | ko62.jpg |
| 文書 | PDF, Word, Excel | ko63.pdf, ko64.docx |
| ウェブ | HTML, MHTML | ko65.html |
| 動画 | MP4, MOV等 | ko70_video.mp4 |
| 音声 | MP3, WAV等 | ko71_audio.mp3 |

**システムがGoogle Driveから取得する情報:**

```python
{
    "file_id": "1abc...xyz",              # Google DriveのファイルID
    "file_name": "ko62.pdf",              # ファイル名
    "mime_type": "application/pdf",       # MIMEタイプ
    "size": 1234567,                      # ファイルサイズ（バイト）
    "created_time": "2024-01-15T10:30:00", # 作成日時
    "modified_time": "2024-01-15T10:35:00", # 変更日時
    "web_view_link": "https://drive.google.com/file/d/1abc...xyz/view",
    "web_content_link": "https://drive.google.com/uc?id=1abc...xyz&export=download"
}
```

### 3. 既存のdatabase.json（復元用）

Google Driveに保存された既存の`database.json`を読み込んで、進捗を復元します。

---

## 📤 出力情報（システム → Google Drive）

### 1. database.json（自動バックアップ）

システムが**Google Driveに保存**する分析結果：

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
      "evidence_number": "ko62",
      "complete_metadata": {
        "file_hash": { "sha256": "abc123..." },
        "google_drive_urls": {
          "web_view_link": "https://drive.google.com/file/d/xxx/view",
          "download_link": "https://drive.google.com/uc?id=xxx&export=download"
        }
      },
      "phase1_complete_analysis": { /* AI分析結果 */ },
      "status": "completed",
      "processed_at": "2025-10-19T12:34:56"
    }
  ]
}
```

**保存先:**
- `{事件フォルダ}/database.json`
- バックアップ: `{事件フォルダ}/database_backup_YYYYMMDD_HHMMSS.json`

### 2. Google Drive URL記録

各証拠ファイルのGoogle Drive URLを`database.json`に記録：

```json
{
  "google_drive_urls": {
    "file_id": "1abc...xyz",
    "web_view_link": "https://drive.google.com/file/d/1abc...xyz/view",
    "download_link": "https://drive.google.com/uc?id=1abc...xyz&export=download",
    "preview_link": "https://drive.google.com/file/d/1abc...xyz/preview"
  }
}
```

**用途:**
- Phase 2以降で証拠ファイルに直接アクセス
- 証拠説明書に直リンクを記載
- 裁判所提出用のURL生成

---

## 🔐 認証の仕組み

### ステップ1: credentials.json（初回のみ）

Google Cloud Consoleから取得する認証情報：

```
credentials.json
├── client_id: Google APIクライアントID
├── client_secret: クライアントシークレット
└── redirect_uris: リダイレクトURI
```

**取得方法:**
1. Google Cloud Console（https://console.cloud.google.com/）にアクセス
2. プロジェクト作成
3. Google Drive APIを有効化
4. OAuth 2.0クライアントIDを作成（デスクトップアプリ）
5. credentials.jsonをダウンロード

### ステップ2: token.json（自動生成）

初回実行時に自動生成されるアクセストークン：

```
token.json
├── access_token: 短期アクセストークン（1時間有効）
├── refresh_token: 長期リフレッシュトークン
├── token_uri: トークン更新用URI
└── expiry: トークンの有効期限
```

**自動更新:**
- `token.json`は自動的に更新されます
- `refresh_token`を使って`access_token`を自動更新
- ユーザーは再認証不要

### ステップ3: 認証フロー

```
初回実行:
┌─────────────────────┐
│ python3 run_phase1.py│
└──────────┬──────────┘
           │
           ↓ credentials.json読み込み
┌─────────────────────┐
│ ブラウザが自動起動   │
│ Googleログイン画面   │
└──────────┬──────────┘
           │
           ↓ ユーザーがログイン
┌─────────────────────┐
│ 権限の許可           │
│ (Google Drive読み書き)│
└──────────┬──────────┘
           │
           ↓ 認証完了
┌─────────────────────┐
│ token.json自動生成   │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│ システム起動         │
└─────────────────────┘

2回目以降:
┌─────────────────────┐
│ python3 run_phase1.py│
└──────────┬──────────┘
           │
           ↓ token.json読み込み
┌─────────────────────┐
│ 自動ログイン（無音）  │
│ 再認証不要           │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│ システム起動         │
└─────────────────────┘
```

---

## 🔄 データフロー（詳細）

### フロー1: 証拠ファイルの取得

```
1. ユーザーが証拠番号を入力 (例: ko62)
   ↓
2. システムがGoogle Driveで検索
   - フォルダID: KO_EVIDENCE_FOLDER_ID
   - ファイル名: "ko62" で始まるファイル
   ↓
3. ファイル情報を取得
   - ファイルID、名前、サイズ、作成日時等
   ↓
4. ファイルをダウンロード
   - ダウンロード先: /tmp/phase1_temp/ko62.pdf
   ↓
5. メタデータ抽出
   - ファイルハッシュ (SHA-256, MD5, SHA-1)
   - EXIF情報 (画像の場合)
   - 文書プロパティ (PDF/Wordの場合)
   - Google Drive URL
   ↓
6. ファイル処理
   - PDF → 画像抽出
   - 画像 → リサイズ・正規化
   - Word → テキスト抽出
   ↓
7. AI分析 (GPT-4o Vision)
   - 画像・テキストを分析
   - 完全言語化レベル4
   ↓
8. database.jsonに保存
   - ローカル: ./database.json
   - Google Drive: {事件フォルダ}/database.json (自動バックアップ)
```

### フロー2: database.jsonの同期

```
起動時:
┌──────────────────────────────┐
│ ローカルのdatabase.jsonを確認  │
└──────────┬───────────────────┘
           │
           ↓ 存在する？
      ┌────┴────┐
      │ YES     │ NO
      ↓         ↓
┌─────────┐  ┌──────────────────┐
│ 読み込み │  │ Google Driveから  │
│         │  │ database.jsonを   │
│         │  │ ダウンロードして復元│
└────┬────┘  └────┬─────────────┘
     │            │
     └────┬───────┘
          ↓
    ┌──────────┐
    │ 処理実行 │
    └────┬─────┘
         │
         ↓ 証拠を処理
    ┌──────────────────┐
    │ database.jsonを更新│
    └────┬─────────────┘
         │
         ↓ 自動バックアップ
    ┌──────────────────────────┐
    │ Google Driveに自動保存     │
    │ - database.json (最新)     │
    │ - database_backup_*.json   │
    └────────────────────────────┘
```

---

## 📁 フォルダ構造

### Google Drive上の推奨構造

```
共有ドライブ/ (または マイドライブ/)
└── 事件フォルダ/
    ├── 甲号証/
    │   ├── ko62.pdf
    │   ├── ko63.jpg
    │   ├── ko64.docx
    │   ├── ko65.html
    │   ├── ko66.png
    │   ├── ko67.pdf
    │   ├── ko70_video1.mp4
    │   ├── ko70_video2.mp4
    │   ├── ko71.pdf
    │   ├── ko72.jpg
    │   └── ko73.docx
    │
    ├── 乙号証/ (オプション)
    │   ├── otsu1.pdf
    │   └── otsu2.jpg
    │
    ├── database.json ← システムが自動保存
    ├── database_backup_20251019_120000.json
    ├── database_backup_20251019_130000.json
    └── database_backup_20251019_140000.json
```

### ローカルPC上の構造

```
~/Documents/phase1_complete_system/
├── config.py                     # Google DriveフォルダID設定
├── credentials.json              # Google認証情報
├── token.json                    # アクセストークン（自動生成）
├── database.json                 # ローカルデータベース
├── phase1_complete.log           # ログファイル
│
├── run_phase1.py                 # 実行スクリプト
├── metadata_extractor.py
├── file_processor.py
├── ai_analyzer_complete.py
└── ...
```

---

## 🔒 セキュリティ

### 1. 認証情報の保護

**credentials.json:**
- ✅ ローカルPCにのみ保存
- ✅ Gitにコミットしない（.gitignoreに追加）
- ✅ 権限: 読み取り専用に設定

**token.json:**
- ✅ 自動生成・自動更新
- ✅ ローカルPCにのみ保存
- ✅ 有効期限: access_tokenは1時間、refresh_tokenは長期

### 2. Google Drive権限

システムが要求する権限：

```
https://www.googleapis.com/auth/drive
```

**できること:**
- ✅ ファイルの読み取り
- ✅ ファイルのダウンロード
- ✅ database.jsonの保存・更新

**できないこと:**
- ❌ ファイルの削除（設定次第で可能だが、推奨しない）
- ❌ 共有設定の変更
- ❌ 他のユーザーへのアクセス権付与

### 3. データの暗号化

**転送時:**
- ✅ HTTPS通信（TLS 1.2以上）
- ✅ Google Drive APIはすべて暗号化通信

**保存時:**
- ✅ Google Drive上のファイルは自動的に暗号化
- ✅ ローカルのdatabase.jsonは平文（必要に応じて暗号化可能）

---

## 🔍 Google Drive操作の詳細

### 操作1: ファイル検索

```python
# 甲号証フォルダ内でko62を検索
query = f"'{KO_EVIDENCE_FOLDER_ID}' in parents and name contains 'ko62'"
results = drive_service.files().list(
    q=query,
    fields="files(id, name, mimeType, size, createdTime, modifiedTime, webViewLink, webContentLink)",
    supportsAllDrives=True
).execute()

# 結果例:
# {
#   "files": [
#     {
#       "id": "1abc...xyz",
#       "name": "ko62.pdf",
#       "mimeType": "application/pdf",
#       "size": "1234567",
#       "createdTime": "2024-01-15T10:30:00.000Z",
#       "modifiedTime": "2024-01-15T10:35:00.000Z",
#       "webViewLink": "https://drive.google.com/file/d/1abc...xyz/view",
#       "webContentLink": "https://drive.google.com/uc?id=1abc...xyz&export=download"
#     }
#   ]
# }
```

### 操作2: ファイルダウンロード

```python
# ファイルIDでダウンロード
file_id = "1abc...xyz"
request = drive_service.files().get_media(fileId=file_id)

# ローカルに保存
with open("/tmp/ko62.pdf", "wb") as f:
    downloader = MediaIoBaseDownload(f, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"ダウンロード進捗: {int(status.progress() * 100)}%")
```

### 操作3: database.json保存

```python
# database.jsonをGoogle Driveに保存
file_metadata = {
    'name': 'database.json',
    'parents': [CASE_FOLDER_ID]
}

media = MediaFileUpload(
    'database.json',
    mimetype='application/json',
    resumable=True
)

# 既存ファイルがあれば更新、なければ新規作成
if existing_file_id:
    drive_service.files().update(
        fileId=existing_file_id,
        media_body=media
    ).execute()
else:
    drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
```

---

## 📊 データの流れ（まとめ）

### 入力データ

| 項目 | 場所 | 内容 |
|------|------|------|
| **設定情報** | config.py | フォルダID、認証情報 |
| **証拠ファイル** | Google Drive | PDF, 画像, 動画, 音声等 |
| **既存DB** | Google Drive | database.json（復元用） |

### 処理データ

| 項目 | 場所 | 内容 |
|------|------|------|
| **ダウンロード** | /tmp/ | 一時的なファイル保存 |
| **メタデータ** | メモリ | ハッシュ、EXIF、URL等 |
| **AI分析** | メモリ | GPT-4o Vision分析結果 |

### 出力データ

| 項目 | 場所 | 内容 |
|------|------|------|
| **database.json** | ローカルPC | 完全分析結果 |
| **database.json** | Google Drive | 自動バックアップ |
| **ログ** | ローカルPC | 処理ログ |

---

## 💡 実装例

### 例1: Google Driveから証拠を検索

```python
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# 認証
creds = Credentials.from_authorized_user_file('token.json')
service = build('drive', 'v3', credentials=creds)

# ko62を検索
query = f"'{KO_EVIDENCE_FOLDER_ID}' in parents and name contains 'ko62'"
results = service.files().list(q=query, fields="files(id, name)").execute()

print(f"検出されたファイル: {results['files']}")
# 出力: [{'id': '1abc...xyz', 'name': 'ko62.pdf'}]
```

### 例2: ファイルをダウンロード

```python
from googleapiclient.http import MediaIoBaseDownload

file_id = "1abc...xyz"
request = service.files().get_media(fileId=file_id)

with open("ko62.pdf", "wb") as f:
    downloader = MediaIoBaseDownload(f, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()

print("✅ ダウンロード完了")
```

### 例3: database.jsonをアップロード

```python
from googleapiclient.http import MediaFileUpload

file_metadata = {'name': 'database.json', 'parents': [CASE_FOLDER_ID]}
media = MediaFileUpload('database.json', mimetype='application/json')

file = service.files().create(
    body=file_metadata,
    media_body=media,
    fields='id'
).execute()

print(f"✅ アップロード完了: {file['id']}")
```

---

## 📝 まとめ

### Google Drive連携の要点

1. **入力:**
   - 設定情報（フォルダID）
   - 証拠ファイル（PDF, 画像, 動画, 音声等）
   - 既存のdatabase.json（復元用）

2. **処理:**
   - ファイル検索・ダウンロード
   - メタデータ抽出・AI分析
   - database.json作成

3. **出力:**
   - database.json（ローカル + Google Drive自動バックアップ）
   - Google Drive URL記録

4. **認証:**
   - credentials.json（初回のみ）
   - token.json（自動生成・自動更新）

5. **セキュリティ:**
   - HTTPS暗号化通信
   - OAuth 2.0認証
   - 最小権限の原則

---

**最終更新:** 2025-10-19  
**バージョン:** 3.2  
**対応:** Google Drive API v3

# システム構造サマリー（2025年10月20日現在）

## 📁 プロジェクト概要

**リポジトリ**: https://github.com/ogaiku-wospe/create-junbisyomen.git  
**ローカルパス**: `/Users/ogaiku/create-junbisyomen`  
**バージョン**: v3.7.2  
**最終コミット**: b903fc1 (fix: Improve content policy rejection detection)

---

## 🏗️ システムアーキテクチャ

### データ保存構造

```
Google Drive (共有ドライブ)
├── [事件フォルダ1]/
│   ├── 甲号証/              ← 確定証拠（ko001, ko002...）
│   ├── 未分類/              ← アップロード直後
│   ├── 整理済み_未確定/     ← 仮番号付き（tmp_001, tmp_002...）
│   ├── database.json        ← **証拠分析データベース（Google Drive上）**
│   └── logs/
├── [事件フォルダ2]/
│   └── ...
└── ...
```

**重要**: 
- ✅ `database.json`は**Google Drive上**に保存される（v3.2.0以降）
- ❌ ローカルに`database.json`は**存在しない**
- ✅ すべての読み書きはGoogle Driveで直接実行
- ✅ 複数デバイスから同じデータベースにアクセス可能

---

## 📂 ディレクトリ構造

```
/home/user/create-junbisyomen/
├── run_phase1_multi.py        ← メインスクリプト（マルチ事件対応・推奨）
├── run_phase1.py              ← 従来版（単一事件）
├── global_config.py           ← グローバル設定（共有ドライブID等）
├── ai_analyzer_complete.py    ← AI分析エンジン
├── evidence_organizer.py      ← 証拠整理
├── evidence_editor_ai.py      ← AI対話式編集
├── case_manager.py            ← 事件管理
├── batch_process.py           ← 一括処理
├── utils/
│   └── database_cleanup.py    ← データベースクリーンアップツール（v3.7.2）
├── prompts/
│   └── Phase1_EvidenceAnalysis.txt  ← AI分析プロンプト
├── README.md                  ← システムドキュメント
├── FIXES_v3.7.2.md           ← v3.7.2修正内容
└── credentials.json           ← Google Drive API認証情報
```

---

## 🔑 重要な設定ファイル

### 1. `global_config.py`

```python
# 大元の共有ドライブID（必須設定）
SHARED_DRIVE_ROOT_ID = "0AO6q4_G7DmYSUk9PVA"

# ローカル作業ディレクトリ
LOCAL_WORK_DIR = "/Users/ogaiku/create-junbisyomen"

# データベースバージョン
DATABASE_VERSION = "3.0"
```

### 2. `.env`（ローカルのみ）

```
OPENAI_API_KEY=sk-proj-your-actual-api-key-here
```

### 3. `credentials.json`（ローカルのみ）

Google Drive API認証情報（OAuth 2.0クライアントID）

---

## 🔄 ワークフロー

### 標準的な証拠処理フロー

```
1. 証拠ファイルをGoogle Drive「未分類」フォルダにアップロード
   ↓
2. メニュー1「証拠整理」実行
   - ファイル名から証拠番号を抽出
   - 「未分類」→「整理済み_未確定」に移動
   - 仮番号（tmp_001, tmp_002...）を付与
   ↓
3. メニュー2「証拠分析」実行
   - tmp_001-010 などの範囲指定
   - AI分析（GPT-4o Vision + OCR）
   - database.jsonに保存（Google Drive上）
   ↓
4. メニュー4「日付順に並び替えて確定」実行
   - document_dateで自動ソート
   - 確定番号（ko001, ko002...）を割り当て
   - 「整理済み_未確定」→「甲号証」に移動
```

---

## 🗄️ database.json 構造（v3.0）

```json
{
  "version": "3.0",
  "metadata": {
    "total_evidence_count": 21,
    "completed_count": 20
  },
  "evidence": [
    {
      "temp_id": "tmp_001",           // 仮番号
      "evidence_id": "tmp_001",       // 証拠ID
      "evidence_number": "甲tmp_001",  // 証拠番号
      "original_filename": "契約書.pdf",
      "renamed_filename": "tmp_001_契約書.pdf",
      "complete_metadata": {          // 完全メタデータ
        "hashes": {
          "sha256": "...",
          "md5": "..."
        },
        "gdrive": {
          "file_id": "...",
          "file_url": "https://drive.google.com/..."
        }
      },
      "phase1_complete_analysis": {   // Phase1分析結果
        "ai_analysis": {
          "verbalization_level": 4,
          "confidence_score": 0.95,
          "objective_analysis": {
            "temporal_information": {
              "document_date": "2021-08-15",  // 作成年月日
              "document_date_source": "契約書末尾"
            }
          }
        }
      }
    }
  ]
}
```

---

## 🐛 v3.7.2で修正された問題

### 1. データベース重複問題
- **問題**: 同じ証拠が2回保存される（未分析版と分析済み版）
- **修正**: マッチングロジックを改善（temp_id/evidence_id/evidence_number）
- **ツール**: `utils/database_cleanup.py`で既存の重複を削除可能

### 2. Vision API Content Policy拒否
- **問題**: 医療文書等が「I'm sorry, I can't assist」で拒否される
- **修正**: 自動的にOCRベースのテキスト分析にフォールバック

---

## 💻 ローカル環境での使用方法

### 初期セットアップ（ローカル）

```bash
# リポジトリクローン
cd /Users/ogaiku
git clone https://github.com/ogaiku-wospe/create-junbisyomen.git
cd create-junbisyomen

# 依存パッケージインストール
pip install -r requirements.txt

# システムライブラリ（macOS）
brew install libheif libmagic tesseract tesseract-lang poppler

# 環境変数設定
cp .env.example .env
nano .env  # OPENAI_API_KEYを設定

# Google Drive API認証
# 1. Google Cloud Consoleでプロジェクト作成
# 2. Google Drive APIを有効化
# 3. OAuth 2.0クライアントID作成
# 4. credentials.jsonをダウンロードして配置
cp ~/Downloads/credentials.json .
```

### システム起動

```bash
cd /Users/ogaiku/create-junbisyomen
python3 run_phase1_multi.py
```

### データベースクリーンアップ（重複削除）

```bash
# 重複を分析
python3 utils/database_cleanup.py [database.json] --analyze

# 重複をマージ（ドライラン）
python3 utils/database_cleanup.py [database.json] --merge

# 重複をマージ（実行）
python3 utils/database_cleanup.py [database.json] --merge --execute
```

**注意**: database.jsonはGoogle Drive上にあるため、一度ローカルにダウンロードしてから処理する必要があります。

---

## 📊 database.jsonの取得方法

### オプション1: Google Drive Web UIから

1. Google Driveで事件フォルダを開く
2. `database.json`を右クリック→ダウンロード
3. `/Users/ogaiku/create-junbisyomen/database.json` に保存

### オプション2: スクリプトで取得（実装が必要）

```python
# 今後実装予定: database_download.py
python3 utils/database_download.py --case meiyokison
```

---

## 🔧 トラブルシューティング

### Q: ローカルにdatabase.jsonがない
**A**: 正常です。v3.2.0からGoogle Drive上で管理されます。

### Q: データベースをクリーンアップしたい
**A**: 
1. Google Driveから`database.json`をダウンロード
2. `utils/database_cleanup.py`でクリーンアップ
3. クリーンアップ後のファイルをGoogle Driveにアップロード

### Q: 事件が検出されない
**A**: 
- `global_config.py`の`SHARED_DRIVE_ROOT_ID`を確認
- 事件フォルダ内に「甲号証」フォルダが存在するか確認

---

## 📚 関連ドキュメント

- [README.md](README.md) - システム全体の説明
- [README_MULTI_CASE.md](README_MULTI_CASE.md) - マルチ事件対応ガイド
- [FIXES_v3.7.2.md](FIXES_v3.7.2.md) - v3.7.2修正内容
- [GOOGLE_DRIVE_GUIDE.md](GOOGLE_DRIVE_GUIDE.md) - Google Drive設定

---

## 🎯 次のステップ

1. ✅ システム構造を理解
2. ⚠️ ローカルにdatabase.jsonは**存在しない**ことを確認
3. 📥 必要に応じてGoogle DriveからダウンロードしてクリーンアップRun
4. 📤 クリーンアップ後、Google Driveに再アップロード
5. 🚀 `run_phase1_multi.py`でシステム起動

---

**更新日**: 2025年10月20日  
**バージョン**: v3.7.2

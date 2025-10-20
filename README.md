# Phase 1 完全版システム - 証拠の完全言語化分析

**✨ v3.2.0 新機能: database.jsonをGoogle Driveで管理！複数デバイスから同じデータベースにアクセスできます。**

**✨ v3.1.0 新機能: マルチ事件対応！大元の共有ドライブIDのみを設定し、複数事件を同時並行で管理できます。**

民事訴訟における証拠ファイルを自動的に分析し、完全言語化（レベル4）を実現するシステムです。

## 🎯 概要

Phase 1完全版システムは、証拠ファイル（画像、PDF、Word、動画、音声など）を自動的に分析し、原文参照不要な詳細記述（完全言語化レベル4）を生成します。

### 主な機能

#### 🆕 v3.2.0 新機能
- ✨ **Google Driveでdatabase.json管理**: ローカルストレージ不要、複数デバイスで同期
- ✨ **自動バックアップ**: Google Drive上で安全に管理
- ✨ **リアルタイム更新**: 複数デバイスから最新データにアクセス

#### 🆕 v3.1.0 新機能（推奨）
- ✨ **マルチ事件対応**: 大元の共有ドライブIDのみ設定で複数事件を並行管理
- ✨ **事件自動検出**: 共有ドライブから事件フォルダを自動検出
- ✨ **簡単切り替え**: メニューから事件を即座に切り替え
- ✨ **進捗一覧**: 複数事件の進捗状況を一目で確認

#### コア機能
- ✅ **全形式対応**: JPEG, PNG, HEIC, PDF, Word, HTML, MP4, MP3など
- ✅ **完全メタデータ抽出**: ファイルハッシュ（SHA-256/MD5/SHA-1）、EXIF情報、Google Drive URL
- ✅ **GPT-4o Vision統合**: 高精度な画像・文書分析
- ✅ **完全言語化レベル4**: 原文参照不要な詳細記述を自動生成
- ✅ **品質保証**: 完全性スコア、信頼度スコア、言語化レベル評価
- ✅ **database.json v3.0**: プログラム完全解釈可能な構造化データ

## 📋 システム要件

- **Python**: 3.8以上
- **OS**: macOS, Linux, Windows (WSL2)
- **メモリ**: 4GB以上推奨
- **ディスク**: 10GB以上の空き容量

### 必須APIキー

- OpenAI API キー（GPT-4o Vision用）
- Google Drive API 認証情報（推奨）

## 🚀 クイックスタート

### 1. リポジトリのクローン

```bash
git clone https://github.com/ogaiku-wospe/create-junbisyomen.git
cd create-junbisyomen
```

### 2. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 3. システムライブラリのインストール（macOS）

```bash
brew install libheif libmagic tesseract tesseract-lang poppler
```

### 4. 環境変数の設定

```bash
# .env ファイルを作成
cp .env.example .env

# エディタで .env を開き、APIキーを設定
nano .env
```

**.env の内容:**
```
OPENAI_API_KEY=sk-proj-your-actual-api-key-here
```

### 5. Google Drive API 認証情報の配置

Google Drive連携を使用する場合：

1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクト作成
2. Google Drive APIを有効化
3. OAuth 2.0クライアントIDを作成（デスクトップアプリ）
4. `credentials.json` をダウンロードして配置

```bash
cp ~/Downloads/credentials.json .
```

## 📖 使用方法

### 🆕 方法1: マルチ事件対応版（推奨）

#### ステップ1: 共有ドライブIDを設定

`global_config.py` を開いて、大元の共有ドライブIDを設定：

```python
# global_config.py
SHARED_DRIVE_ROOT_ID = "your-shared-drive-id-here"  # ← ここに設定
```

#### ステップ2: 共有ドライブに事件フォルダを作成

```
共有ドライブ/
├── meiyokison_名誉毀損事件/
│   └── 甲号証/         # ← 必須
│       ├── ko001.pdf
│       └── ko002.jpg
└── keiyaku_契約違反事件/
    └── 甲号証/         # ← 必須
```

**重要**: 事件フォルダ内に「**甲号証**」フォルダが必要です。

#### ステップ3: システムを起動

```bash
python3 run_phase1_multi.py
```

事件一覧が表示され、選択後に証拠分析を開始できます。

**詳細**: [マルチ事件対応ガイド](README_MULTI_CASE.md)

---

### 方法2: 従来版（単一事件）

#### 新規事件のセットアップ

```bash
python3 setup_new_case.py
```

対話形式で以下を入力：
- 事件名
- 原告・被告名
- 管轄裁判所
- Google DriveフォルダID

#### システムの起動

```bash
python3 run_phase1.py
```

メニューから選択：
1. 証拠番号を指定して分析（例: ko70）
2. 範囲指定して分析（例: ko70-73）
3. 個別ファイルを分析
4. 未処理の証拠を自動検索
5. 進捗確認

#### 一括処理

```bash
# 複数証拠の一括分析
python3 batch_process.py --range ko70-73 --directory /path/to/evidence_files/

# 未処理の証拠を自動処理
python3 batch_process.py --auto --directory /path/to/evidence_files/
```

## 📊 出力形式

分析結果は `database.json` (v3.0形式) に保存されます：

```json
{
  "case_info": {
    "case_name": "事件名",
    "plaintiff": "原告名",
    "defendant": "被告名"
  },
  "evidence": [
    {
      "evidence_number": "ko070",
      "complete_metadata": {
        "hashes": {
          "sha256": "...",
          "md5": "..."
        },
        "gdrive": {
          "file_url": "https://drive.google.com/...",
          "download_url": "..."
        }
      },
      "phase1_complete_analysis": {
        "ai_analysis": {
          "verbalization_level": 4,
          "full_content": {
            "complete_description": "原文参照不要な詳細記述",
            "visual_information": {...},
            "textual_content": {...}
          },
          "legal_significance": {...}
        },
        "quality_assessment": {
          "completeness_score": 0.95,
          "confidence_score": 0.90
        }
      }
    }
  ]
}
```

## 📚 ドキュメント

### 主要ガイド
- **[マルチ事件対応ガイド](README_MULTI_CASE.md)** - 🆕 複数事件の並行管理（推奨）
- [使用ガイド](USAGE_GUIDE.md) - 詳細な使用方法
- [Google Drive連携](GOOGLE_DRIVE_GUIDE.md) - Google Drive設定方法

### 技術文書
- [ファイル整理計画](FILE_ORGANIZATION_PLAN.md) - システム構成とファイル管理

## 🆚 従来版 vs マルチ事件対応版

| 機能 | 従来版 (run_phase1.py) | マルチ事件対応版 (run_phase1_multi.py) |
|------|----------------------|-----------------------------------|
| **設定の簡便性** | 事件ごとに設定ファイル編集 | global_config.pyで一元管理 ✨ |
| **複数事件の管理** | ❌ ディレクトリごとに分離 | ✅ 1つのシステムで管理 ✨ |
| **事件の検出** | ❌ 手動設定 | ✅ 自動検出 ✨ |
| **事件の切り替え** | ❌ ディレクトリ移動が必要 | ✅ メニューから即座に切り替え ✨ |
| **進捗の確認** | ✅ database.json | ✅ 複数事件の進捗を一覧表示 ✨ |
| **推奨度** | ⚠️ 単一事件のみの場合 | ✅ すべてのユースケースで推奨 |

**💡 ヒント**: 新規プロジェクトでは、将来の拡張性を考慮してマルチ事件対応版の使用を推奨します。

## 🔧 高度な設定

### マルチ事件対応版（global_config.py）

```python
# 大元の共有ドライブID（必須）
SHARED_DRIVE_ROOT_ID = "your-shared-drive-id-here"

# 事件フォルダの命名規則
CASE_FOLDER_NAME_FORMAT = "{case_id}_{case_name}"

# 証拠フォルダの標準名
EVIDENCE_FOLDER_NAME_KO = "甲号証"
EVIDENCE_FOLDER_NAME_OTSU = "乙号証"

# 品質保証設定
QUALITY_THRESHOLDS = {
    'completeness_score': 90.0,
    'confidence_score': 80.0,
    'verbalization_level': 4,
    'metadata_coverage': 95.0
}
```

## 🎯 対応ファイル形式

| 分類 | 対応形式 |
|------|---------|
| **画像** | JPEG, PNG, HEIC, GIF, WebP, TIFF |
| **文書** | PDF, Word (DOCX/DOC), Excel, PowerPoint |
| **ウェブ** | HTML, MHTML |
| **動画** | MP4, MOV, AVI, MKV, WebM |
| **音声** | MP3, WAV, M4A, AAC, FLAC |
| **メール** | EML, MSG（準備中） |
| **アーカイブ** | ZIP, RAR, 7Z（準備中） |

## 💰 コスト

OpenAI APIの使用料金（目安）：
- 画像1枚: 約$0.05
- PDF 10ページ: 約$0.15
- 証拠74件の完全分析: 約$60

## ⚠️ 重要な注意事項

### セキュリティ

- **機密情報**: `credentials.json`, `.env`, `database.json` は絶対にGitHubにアップロードしないでください
- **個人情報**: 実際の事件データは `.gitignore` に追加してください
- **APIキー**: OpenAI APIキーは環境変数で管理してください

### 品質チェック

処理後は必ず以下を確認：
- 完全性スコア: 90%以上
- 信頼度スコア: 80%以上
- 言語化レベル: 4以上

スコアが低い場合は再処理を推奨します。

## 🔄 v3.2.0への移行（ローカルdatabase.jsonの削除）

v3.2.0からdatabase.jsonはGoogle Driveで管理されます。ローカルファイルは不要になりました。

### 移行手順

1. **ローカルdatabase.jsonのバックアップと削除**

```bash
python3 cleanup_local_database.py
```

このスクリプトは:
- ローカルdatabase.jsonをバックアップ（`local_backup/`フォルダ）
- ローカルファイルを削除
- 確認プロンプトを表示

2. **システムの起動**

```bash
python3 run_phase1_multi.py
```

初回起動時、Google Drive上にdatabase.jsonが自動作成されます。

### 新しい動作

- ✅ database.jsonは事件フォルダ内に作成されます
- ✅ 全ての読み書きはGoogle Driveで直接実行されます
- ✅ ローカルキャッシュは使用されません
- ✅ 複数デバイスから同じデータベースにアクセスできます

## 🐛 トラブルシューティング

### よくある問題

**Q: `ModuleNotFoundError: No module named 'dotenv'`**
```bash
pip install python-dotenv
```

**Q: `HEIC画像が処理できない`**
```bash
brew install libheif
pip install pillow-heif
```

**Q: `Google Drive APIエラー`**
- `credentials.json` が正しく配置されているか確認
- Google Cloud Consoleで APIが有効化されているか確認

**Q: マルチ事件対応版で事件が検出されない**
- `global_config.py` の `SHARED_DRIVE_ROOT_ID` が正しいか確認
- 事件フォルダ内に「甲号証」フォルダが存在するか確認
- キャッシュをクリア: `rm ~/.phase1_cases_cache.json`

詳細は [マルチ事件対応ガイド](README_MULTI_CASE.md) または [使用ガイド](USAGE_GUIDE.md) を参照してください。

## 🎯 ロードマップ

### v3.1.0（現行版）
- ✅ マルチ事件対応機能
- ✅ 事件自動検出
- ✅ 複数事件の並行管理

### 今後の予定
- [ ] 事件ごとの統計ダッシュボード
- [ ] 複数事件の横断検索
- [ ] 証拠の自動分類
- [ ] Webインターフェース

## 🤝 貢献

バグ報告や機能リクエストは [Issues](https://github.com/ogaiku-wospe/create-junbisyomen/issues) で受け付けています。

## 📄 ライセンス

このプロジェクトは個人利用を目的としています。

## 📞 サポート

問題が発生した場合:
1. [マルチ事件対応ガイド](README_MULTI_CASE.md) または [使用ガイド](USAGE_GUIDE.md) を確認
2. [Issues](https://github.com/ogaiku-wospe/create-junbisyomen/issues) を検索
3. 新しいIssueを作成

---

---

## 🆕 v3.6.0 更新履歴（2025年10月20日）

### 🎯 重大な改善：Phase 1の完全客観化（バイアス排除）

**Phase 1を完全に客観的・中立的な証拠記録システムに変更しました。**

#### 🔴 修正した問題点

**問題**: Phase 1のAI分析に原告側のバイアスが混入していた
- 事件情報（原告・被告）をAIに事前提供
- "relevance_to_case"（本件との関連性）= 原告視点の解釈
- "argument_strategies"（主張戦略）= 原告側の戦略提案
- 結果: 客観的証拠分析ではなく、原告に有利な解釈

#### ✅ 実施した修正

1. **事件情報の完全削除**
   - AIに原告・被告の情報を一切提供しない
   - 訴訟の当事者や事件の詳細を知らない前提で分析
   - 中立的な記録者として振る舞う

2. **データ構造の変更**
   ```
   【削除】
   - legal_significance（法的意義）
   - relevance_to_case（本件との関連性）
   - usage_suggestions（使用方法の提案）
   - argument_strategies（主張戦略）
   
   【追加】
   - objective_analysis（客観的分析）
   - observable_facts（観察可能な事実）
   - temporal_information（時系列情報）
   - parties_mentioned（登場人物の客観的記録）
   - financial_information（金額情報）
   - document_state（文書の状態）
   ```

3. **プロンプトの完全書き換え**
   - Phase 1の役割を「客観的事実記録」に明確化
   - 法的評価や主観的解釈の禁止を明示
   - 観察可能な事実のみを記録するよう指示

4. **編集機能の客観化**
   - 編集時も中立性を維持
   - ユーザー指示に基づく事実の訂正のみ
   - 法的評価の追加は行わない

#### 📊 Phase 1 vs Phase 2 の役割分担

```
【Phase 1: 客観的事実記録】（今回修正）
- 証拠の内容を中立的に完全言語化
- 観察可能な事実のみを記録
- 法的評価は一切含まない
- 訴訟の当事者情報は与えない
→ 誰が見ても同じ結果になる客観的記録

【Phase 2: 法的評価・戦略立案】（今後実装予定）
- Phase 1の客観的記録を元に
- 原告側の立場から法的評価
- 主張戦略を立案
- 準備書面の作成
→ 初めて原告視点の分析を行う
```

#### 🎯 期待される効果

- ✅ 証拠分析の客観性と信頼性の向上
- ✅ 裁判所や相手方にも提示可能な中立的記録
- ✅ Phase 2での法的評価の基礎として活用
- ✅ 証拠の誤認識や偏った解釈の防止
- ✅ システムの透明性と説明可能性の向上

---

## v3.5.0 更新履歴（2025年10月20日）

### 🎉 新機能強化：AI対話形式で証拠内容を改善（元画像再精査機能付き）

**メニュー項目「10. AI対話形式で証拠内容を改善」を大幅強化**

#### ✨ 主要な改善点

1. **元画像の再精査機能**
   - 修正指示を受けた際、AIが元の画像/文書を高解像度で再分析
   - 既存のテキスト情報だけでなく、実際の視覚情報を見ながら修正案を生成
   - 見落としていた情報を発見し、より正確な分析を実現

2. **画像認識の精度向上**
   - 詳細分析プロンプトを大幅に強化
   - 画像内の小さな文字、背景の情報、隅に写っているものも見落とさない
   - 文書の場合は全文抽出、手書きメモ、訂正箇所まで詳細に分析

3. **分析項目の拡充**
   - 画像内テキストの位置・サイズ・スタイルを記録
   - 背景詳細、画質評価を追加
   - 日付・金額・人物名の体系的抽出
   - 新たに発見した情報を明示的に記録

自然言語での指示により、AI分析結果の誤認識を修正したり、内容を改善できます。

#### 使用例：

```
# AIの誤認識を訂正
「この証拠の日付は2024年3月15日ではなく、2023年3月15日です」
「写っているのは被告ではなく、第三者の山田太郎です」
「契約金額は100万円ではなく、1000万円です」

# 内容の追加・強化
「この証拠は契約違反の決定的証拠です。契約書第5条に違反しています」
「右下の手書きメモ「承認済」を見落としています」
「法的重要性をもっと詳しく説明してください」
```

#### 機能詳細：
- ✅ **誤認識の訂正**: 日付、人物、金額などの誤りを自然言語で指摘
- ✅ **内容の補強**: 法的重要性や詳細説明の追加・改善
- ✅ **修正前後の比較**: 変更内容を確認してから保存
- ✅ **変更履歴の記録**: すべての編集履歴をデータベースに保存
- ✅ **承認・却下・再修正**: 満足するまで何度でも修正可能

#### 実行フロー：
1. 証拠番号を入力（例: ko001, tmp_001）
2. 現在のAI分析結果を表示
3. 自然言語で修正指示を入力
4. AIが修正案を生成
5. 修正前後を比較表示
6. 承認・却下・再修正を選択
7. database.jsonに保存

---

## v3.3.0 更新履歴（2025年10月20日）

### 修正されたバグ
1. **証拠番号範囲パースの修正**
   - 問題: `tmp_001-011` が `['tmp_1', 'tmp_2', ..., 'tmp_11']` として解析される
   - 修正: ゼロパディングを保持して `['tmp_001', 'tmp_002', ..., 'tmp_011']` として正しく解析
   - 影響: 範囲指定での一括処理が正常に動作するようになりました

2. **PDF処理のVision API対応**
   - 問題: PDFファイルがVision APIに直接送信され、エラーが発生
   - 修正: `_pdf_first_page_to_image()` メソッドを実装し、PDFの1ページ目を画像に変換
   - フォールバック: PDF変換失敗時はテキスト解析に自動切り替え
   - 必要ライブラリ: `pdf2image`, システム依存: `poppler` (Mac: `brew install poppler`)

3. **データベース検索の拡張**
   - 問題: `temp_id` (例: tmp_001) での検索ができない
   - 修正: `evidence_id` と `temp_id` の両方で検索可能に
   - 影響: 未確定証拠（pending）も検索・処理できるようになりました

### 新機能
4. **デバッグモードの追加**
   - 環境変数 `DEBUG_MODE=true` でOpenAI APIレスポンスの全文をログ出力
   - JSON解析失敗時の詳細なデバッグ情報を提供
   - 使用方法: `export DEBUG_MODE=true` してからスクリプト実行

### ユーザビリティ改善
5. **絵文字使用の削減**
   - 114箇所から41箇所に削減（64%減少）
   - エラーメッセージを「エラー:」などのテキストラベルに変更
   - ログの可読性が向上

6. **エラーメッセージの改善**
   - 具体例を含む詳細なエラーメッセージ
   - 入力検証の強化とフィードバック
   - 範囲指定の制限（最大100件）とわかりやすい警告

7. **システム整合性チェックツール**
   - 新規ファイル: `system_integrity_check.py`
   - 機能: モジュール存在確認、import文の整合性、エラー処理カバレッジ計測
   - クロスプラットフォーム対応（Mac / サンドボックス環境）

### 既知の問題
- **JSON解析失敗**: 一部の証拠（約50%）でOpenAI APIレスポンスのJSON解析が失敗する
  - 原因調査中
  - デバッグモードで詳細ログを確認可能

---

**バージョン**: 3.6.0  
**最終更新**: 2025年10月20日  
**対応Phase**: Phase 1（客観的証拠記録・マルチ事件対応・AI対話式編集・元画像再精査）

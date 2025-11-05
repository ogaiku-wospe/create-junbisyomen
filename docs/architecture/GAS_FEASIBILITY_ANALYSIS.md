# GAS（Google Apps Script）による再現可能性分析

## 📋 目次

1. [エグゼクティブサマリー](#エグゼクティブサマリー)
2. [現在のシステムの機能](#現在のシステムの機能)
3. [GASでの実現可能性評価](#gasでの実現可能性評価)
4. [GAS実装アーキテクチャ案](#gas実装アーキテクチャ案)
5. [実装の難易度と制約](#実装の難易度と制約)
6. [推奨アプローチ](#推奨アプローチ)
7. [完全なGAS実装例](#完全なgas実装例)

---

## エグゼクティブサマリー

### 結論

**✅ 可能です**が、以下の重要な制約があります：

| 機能カテゴリ | 実現可能性 | 制約・課題 |
|------------|-----------|----------|
| **証拠ファイルの管理** | ✅ 完全可能 | Google Drive API使用 |
| **メタデータ抽出** | ⚠️ 部分的 | EXIFは外部API必要、ハッシュ計算は制限あり |
| **GPT-4o Vision分析** | ✅ 可能 | OpenAI API経由で実装可能 |
| **Claude AI統合** | ✅ 可能 | Anthropic API経由で実装可能 |
| **データベース管理** | ✅ 完全可能 | スプレッドシートまたはDrive上のJSON |
| **バッチ処理** | ⚠️ 制限あり | 6分実行時間制限、トリガー使用で対応 |
| **UI/UX** | ✅ 可能 | カスタムメニュー、サイドバー、Webアプリ |
| **Google Form連携** | ✅ 可能 | 証拠登録、依頼者メモ入力に最適 |

### 主な利点

1. **ブラウザベース**: インストール不要、どこからでもアクセス可能
2. **Google Drive統合**: 既存のファイル管理と完全統合
3. **共有が容易**: 複数ユーザーでの共同作業が簡単
4. **クラウドベース**: サーバー管理不要
5. **自動化**: トリガーで定期実行可能

### 主な制約

1. **実行時間制限**: 6分/実行（長時間処理は分割必要）
2. **API制限**: 1日あたりのAPIコール数に制限
3. **パッケージ制限**: Python専用ライブラリは使用不可
4. **ローカルファイルアクセス不可**: すべてDrive経由
5. **並列処理制限**: 同時実行数に制限

---

## 現在のシステムの機能

### コア機能

#### 1. 証拠ファイル管理（evidence_organizer.py, file_processor.py）
- 未分類フォルダから証拠を取得
- 一時番号（tmp_001など）を割り当て
- 整理済み_未確定フォルダへ移動
- 最終的に甲号証フォルダへ確定

#### 2. メタデータ抽出（metadata_extractor.py）
- ファイルハッシュ（SHA-256, MD5, SHA-1）
- EXIF情報（画像）
- Google Drive URL生成
- ファイル作成日時、変更日時
- ファイルサイズ

#### 3. AI分析（ai_analyzer_complete.py）
- GPT-4o Vision による画像/PDF分析
- Claude AI によるフォールバック
- 完全言語化（レベル4）生成
- 法的重要性の抽出
- 時系列情報の抽出
- 作成年月日の特定

#### 4. データベース管理（gdrive_database_manager.py）
- Google Drive上のdatabase.json管理
- 複数事件対応
- 自動バックアップ
- リアルタイム更新

#### 5. 時系列ストーリー生成（timeline_builder.py）
- 証拠を時系列順に整理
- Claude Sonnet 4でナラティブ生成
- 事実・証拠紐付け
- 依頼者発言の統合
- 複数フォーマット出力（JSON, Markdown, HTML）

#### 6. マルチ事件対応（run_phase1_multi.py, case_manager.py）
- 複数事件の並行管理
- 事件の自動検出
- 事件切り替え機能
- 進捗一覧表示

#### 7. 対話式改善（evidence_editor_ai.py）
- 自然言語でAI分析結果を修正
- 元画像の再精査
- 変更履歴の記録

---

## GASでの実現可能性評価

### ✅ 完全実現可能な機能

#### 1. Google Drive連携
```javascript
// GASはDriveServiceが標準装備
function listEvidenceFiles() {
  const folder = DriveApp.getFolderById('folder_id');
  const files = folder.getFiles();
  
  while (files.hasNext()) {
    const file = files.next();
    const metadata = {
      id: file.getId(),
      name: file.getName(),
      url: file.getUrl(),
      mimeType: file.getMimeType(),
      size: file.getSize(),
      createdDate: file.getDateCreated(),
      modifiedDate: file.getLastUpdated()
    };
  }
}
```

#### 2. データベース管理（スプレッドシート）
```javascript
// スプレッドシートをデータベースとして使用
function saveEvidenceToDatabase(evidenceData) {
  const ss = SpreadsheetApp.openById('spreadsheet_id');
  const sheet = ss.getSheetByName('証拠一覧');
  
  sheet.appendRow([
    evidenceData.evidence_number,
    evidenceData.file_name,
    evidenceData.document_date,
    evidenceData.complete_description,
    evidenceData.analysis_timestamp
  ]);
}
```

#### 3. OpenAI API連携
```javascript
// UrlFetchAppでOpenAI APIを呼び出し
function analyzeWithGPT4Vision(imageUrl, base64Image) {
  const apiKey = PropertiesService.getScriptProperties().getProperty('OPENAI_API_KEY');
  
  const payload = {
    model: "gpt-4o",
    messages: [{
      role: "user",
      content: [
        { type: "text", text: "この証拠画像を完全言語化してください..." },
        { type: "image_url", image_url: { url: `data:image/jpeg;base64,${base64Image}` } }
      ]
    }],
    max_tokens: 4000
  };
  
  const options = {
    method: 'post',
    contentType: 'application/json',
    headers: { 'Authorization': 'Bearer ' + apiKey },
    payload: JSON.stringify(payload)
  };
  
  const response = UrlFetchApp.fetch('https://api.openai.com/v1/chat/completions', options);
  return JSON.parse(response.getContentText());
}
```

#### 4. Claude API連携
```javascript
function analyzeWithClaude(prompt, imageData) {
  const apiKey = PropertiesService.getScriptProperties().getProperty('ANTHROPIC_API_KEY');
  
  const payload = {
    model: "claude-sonnet-4-20250514",
    max_tokens: 4000,
    messages: [{
      role: "user",
      content: [
        { type: "image", source: { type: "base64", media_type: "image/jpeg", data: imageData } },
        { type: "text", text: prompt }
      ]
    }]
  };
  
  const options = {
    method: 'post',
    contentType: 'application/json',
    headers: { 
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01'
    },
    payload: JSON.stringify(payload)
  };
  
  const response = UrlFetchApp.fetch('https://api.anthropic.com/v1/messages', options);
  return JSON.parse(response.getContentText());
}
```

#### 5. カスタムUI（メニュー、サイドバー）
```javascript
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('証拠管理システム')
    .addItem('証拠整理', 'organizeEvidence')
    .addItem('証拠分析', 'analyzeEvidence')
    .addItem('時系列ストーリー生成', 'generateTimeline')
    .addItem('進捗確認', 'checkProgress')
    .addToUi();
}

function showSidebar() {
  const html = HtmlService.createHtmlOutputFromFile('Sidebar')
    .setTitle('証拠分析');
  SpreadsheetApp.getUi().showSidebar(html);
}
```

#### 6. Google Form連携
```javascript
// Formからの回答を自動処理
function onFormSubmit(e) {
  const formResponse = e.response;
  const items = formResponse.getItemResponses();
  
  // 依頼者メモの登録
  const clientStatement = {
    date: items[0].getResponse(),
    statement: items[1].getResponse(),
    timestamp: new Date()
  };
  
  saveClientStatement(clientStatement);
}
```

### ⚠️ 部分的に実現可能（制約あり）

#### 1. ファイルハッシュ計算
**問題**: GASにはネイティブなSHA-256計算機能がない

**解決策**:
```javascript
// Utilities.computeDigest()を使用（制限あり）
function calculateSHA256(blob) {
  const bytes = blob.getBytes();
  const digest = Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, bytes);
  
  // バイト配列を16進数文字列に変換
  return digest.map(byte => {
    const hex = (byte < 0 ? byte + 256 : byte).toString(16);
    return hex.length === 1 ? '0' + hex : hex;
  }).join('');
}
```

**制約**: 大きなファイル（50MB以上）では処理時間が長くなる

#### 2. EXIF情報抽出
**問題**: GASにはEXIF抽出機能がない

**解決策**:
1. 外部API使用（ExifTool API、ImgBB API等）
2. 簡易的なEXIF読み取りライブラリをGASで実装
3. Drive APIのimageMediaMetadataフィールドを使用（限定的）

```javascript
function getImageMetadata(fileId) {
  const file = Drive.Files.get(fileId, { fields: 'imageMediaMetadata' });
  
  if (file.imageMediaMetadata) {
    return {
      width: file.imageMediaMetadata.width,
      height: file.imageMediaMetadata.height,
      cameraMake: file.imageMediaMetadata.cameraMake,
      cameraModel: file.imageMediaMetadata.cameraModel,
      date: file.imageMediaMetadata.date,
      location: file.imageMediaMetadata.location
    };
  }
}
```

#### 3. 大量ファイルのバッチ処理
**問題**: 6分の実行時間制限

**解決策**: トリガーを使用した分割処理
```javascript
function batchProcessEvidence() {
  const startTime = new Date().getTime();
  const maxRunTime = 5 * 60 * 1000; // 5分
  
  const properties = PropertiesService.getScriptProperties();
  let currentIndex = parseInt(properties.getProperty('currentIndex') || '0');
  
  const files = getAllPendingFiles();
  
  while (currentIndex < files.length) {
    if (new Date().getTime() - startTime > maxRunTime) {
      // 5分経過したら次回実行用にインデックスを保存
      properties.setProperty('currentIndex', currentIndex.toString());
      
      // 1分後に再実行するトリガーを設定
      ScriptApp.newTrigger('batchProcessEvidence')
        .timeBased()
        .after(1 * 60 * 1000)
        .create();
      
      return;
    }
    
    processFile(files[currentIndex]);
    currentIndex++;
  }
  
  // 完了
  properties.deleteProperty('currentIndex');
}
```

### ❌ 実現困難な機能

#### 1. ローカルファイルの直接処理
- GASはブラウザベースなので、ユーザーのローカルファイルに直接アクセス不可
- **対策**: すべてGoogle Drive経由でアップロード

#### 2. Python専用ライブラリ
- pytesseract（OCR）
- pillow-heif（HEIC変換）
- python-docx（Word詳細処理）

**対策**: 
- OCR: Google Cloud Vision API使用
- HEIC: アップロード時に変換するか、外部APIで変換
- Word: Drive APIのエクスポート機能でテキスト抽出

#### 3. 複雑な動画・音声処理
- GASでは動画/音声の詳細解析は困難
- **対策**: 外部API（Cloudinary, AWS Transcribe等）使用

---

## GAS実装アーキテクチャ案

### システム構成

```
┌─────────────────────────────────────────────────────────────┐
│                    ユーザーインターフェース                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ スプレッド   │  │ Google Form  │  │ Webアプリ    │     │
│  │ シート       │  │ （証拠登録） │  │ （ダッシュ   │     │
│  │ （データ表示）│  │              │  │  ボード）    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         ↑                 ↑                 ↑              │
└─────────┼─────────────────┼─────────────────┼──────────────┘
          │                 │                 │
┌─────────┼─────────────────┼─────────────────┼──────────────┐
│         │      Google Apps Script コア         │              │
├─────────┴─────────────────┴─────────────────┴──────────────┤
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │ DriveManager.gs - Google Drive操作                 │   │
│  │  - ファイル一覧取得                                   │   │
│  │  - フォルダ管理（未分類→整理済み→甲号証）             │   │
│  │  - メタデータ抽出                                     │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │ AIAnalyzer.gs - AI分析エンジン                      │   │
│  │  - OpenAI GPT-4o Vision連携                        │   │
│  │  - Anthropic Claude連携                            │   │
│  │  - プロンプト管理                                     │   │
│  │  - レスポンス解析                                     │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │ DatabaseManager.gs - データ管理                     │   │
│  │  - スプレッドシートへの読み書き                        │   │
│  │  - JSON形式での保存（Drive上）                       │   │
│  │  - クエリ機能                                         │   │
│  │  - バックアップ                                       │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │ TimelineBuilder.gs - 時系列ストーリー生成            │   │
│  │  - 日付抽出・ソート                                   │   │
│  │  - Claude APIでナラティブ生成                        │   │
│  │  - HTML/Markdown出力                                │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │ BatchProcessor.gs - バッチ処理                      │   │
│  │  - トリガー管理                                       │   │
│  │  - 進捗管理                                           │   │
│  │  - エラーハンドリング                                 │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │ UIManager.gs - UI制御                               │   │
│  │  - カスタムメニュー                                   │   │
│  │  - サイドバー                                         │   │
│  │  - ダイアログ                                         │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
          │                 │                 │
          ↓                 ↓                 ↓
┌─────────────────────────────────────────────────────────────┐
│                      外部サービス                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ OpenAI API   │  │ Anthropic    │  │ Google Cloud │     │
│  │ (GPT-4o)     │  │ (Claude)     │  │ Vision API   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### データベース設計（スプレッドシート）

#### シート1: 証拠一覧
| 証拠番号 | ファイル名 | 作成年月日 | ステータス | Drive URL | 分析日時 | 備考 |
|---------|----------|-----------|----------|-----------|---------|------|
| ko001 | 契約書.pdf | 2021-08-15 | 確定 | https://... | 2025-11-05 | |
| tmp_001 | 領収書.jpg | 2022-03-20 | 未確定 | https://... | 2025-11-05 | |

#### シート2: 証拠詳細
| 証拠番号 | メタデータJSON | AI分析結果JSON | 品質スコア | 言語化レベル | 最終更新 |
|---------|--------------|--------------|-----------|------------|---------|
| ko001 | {...} | {...} | 95 | 4 | 2025-11-05 |

#### シート3: 時系列イベント
| 日付 | 証拠番号 | イベント要約 | 詳細説明 | 法的重要性 |
|------|---------|------------|---------|-----------|
| 2021-08-15 | ko001 | 契約締結 | ... | ... |

#### シート4: 依頼者発言
| 日付 | 発言内容 | 関連証拠 | 登録日時 |
|------|---------|---------|---------|
| 2021-08-15 | 契約書にサインした | ko001 | 2025-11-05 |

#### シート5: 事件情報
| 事件ID | 事件名 | 原告 | 被告 | 裁判所 | Drive フォルダID |
|-------|-------|------|------|-------|----------------|
| case001 | 名誉毀損事件 | 山田太郎 | 田中花子 | 東京地裁 | folder_id_123 |

### Google Formの活用

#### Form 1: 証拠登録フォーム
```
【証拠登録】

1. Google DriveのファイルURLを貼り付けてください
   [ テキスト入力 ]

2. 証拠の種類を選択してください
   ( ) 契約書
   ( ) メール
   ( ) 領収書・請求書
   ( ) 写真
   ( ) その他

3. 作成年月日（わかる場合）
   [ 日付入力 ]

4. 備考（任意）
   [ テキストエリア ]

[送信]
```

#### Form 2: 依頼者メモ登録フォーム
```
【依頼者メモ登録】

1. この出来事の日付
   [ 日付入力 ]

2. 出来事の詳細
   [ テキストエリア ]

3. 関連する証拠番号（わかる場合）
   [ テキスト入力 ]

[送信]
```

---

## 実装の難易度と制約

### 難易度評価

| 機能 | 難易度 | 開発時間（目安） | 主な技術課題 |
|------|-------|---------------|------------|
| **Drive連携** | ⭐ 易 | 1-2日 | DriveServiceの基本操作 |
| **スプレッドシートDB** | ⭐⭐ 中 | 2-3日 | データ構造設計、クエリ最適化 |
| **OpenAI API連携** | ⭐⭐ 中 | 2-3日 | API認証、画像エンコーディング |
| **Claude API連携** | ⭐⭐ 中 | 2-3日 | API認証、プロンプト管理 |
| **メタデータ抽出** | ⭐⭐⭐ 難 | 3-5日 | EXIF処理、ハッシュ計算 |
| **バッチ処理** | ⭐⭐⭐ 難 | 3-5日 | トリガー管理、状態管理 |
| **時系列ストーリー生成** | ⭐⭐⭐ 難 | 3-5日 | AI統合、出力フォーマット |
| **UI/UX** | ⭐⭐ 中 | 3-4日 | HTML/CSS、メニュー設計 |
| **Form連携** | ⭐ 易 | 1-2日 | onFormSubmitトリガー |

**合計開発時間**: 約3-4週間（フルタイム）

### 主な制約

#### 1. 実行時間制限
- **制限**: 6分/実行
- **影響**: 大量ファイルの一括処理ができない
- **対策**: 
  - トリガーを使った分割処理
  - 進捗状態の保存・再開機能
  - ユーザーへの処理時間の説明

#### 2. API呼び出し制限
- **UrlFetchApp**: 20,000回/日（無料アカウント）
- **Drive API**: 1,000リクエスト/100秒
- **影響**: 大量証拠の同時分析が困難
- **対策**:
  - リクエストのバッチ処理
  - キャッシング
  - レート制限の実装

#### 3. メモリ制限
- **制限**: スクリプトあたり約100MB
- **影響**: 大きなファイル（50MB以上）の処理が困難
- **対策**:
  - ファイルサイズチェック
  - チャンク処理
  - 外部サービスの利用

#### 4. 同時実行制限
- **制限**: ユーザーあたり30の同時実行
- **影響**: 多数のトリガーが同時に動作しない
- **対策**:
  - キュー管理システム
  - 優先度制御

---

## 推奨アプローチ

### 段階的実装計画

#### フェーズ1: MVP（最小実行可能製品）- 2週間
**目標**: 基本的な証拠登録と分析機能

1. **Google Drive連携**
   - フォルダ構造の作成
   - ファイル一覧取得
   - 基本メタデータ抽出

2. **スプレッドシートDB**
   - 証拠一覧シート
   - 基本的なCRUD操作

3. **OpenAI API連携**
   - GPT-4o Visionで画像分析
   - 基本的な完全言語化

4. **シンプルUI**
   - カスタムメニュー
   - 基本的なダイアログ

**成果物**: 1件ずつ証拠を登録・分析できるシステム

#### フェーズ2: 自動化とバッチ処理 - 1週間
**目標**: 効率的な大量処理

1. **バッチ処理エンジン**
   - トリガーベースの分割処理
   - 進捗管理

2. **Form連携**
   - 証拠登録フォーム
   - 自動処理トリガー

3. **エラーハンドリング**
   - リトライ機能
   - エラーログ

**成果物**: フォームから複数証拠を一括登録・自動分析

#### フェーズ3: 高度な機能 - 1週間
**目標**: 現行システムの主要機能を実装

1. **Claude API統合**
   - フォールバック機能
   - 時系列ストーリー生成

2. **マルチ事件対応**
   - 事件切り替え機能
   - 進捗ダッシュボード

3. **対話式改善**
   - AI編集機能
   - 変更履歴

**成果物**: 現行システムの80%の機能を持つGAS版

### ハイブリッドアプローチ（推奨）

現行のPythonシステムとGASシステムを併用：

#### Python側（ローカル/サーバー）
- 複雑な処理（大量ファイル、動画処理等）
- 詳細なメタデータ抽出
- ローカルファイルからの一括アップロード

#### GAS側（クラウド）
- 日常的な証拠登録・分析
- 進捗確認・検索
- 時系列ストーリー生成
- 共同作業

**データ同期**: Google Drive上のdatabase.jsonを共通DBとして使用

---

## 完全なGAS実装例

### ファイル構成

```
GAS_EvidenceAnalysisSystem/
├── Code.gs                 # メインエントリーポイント
├── DriveManager.gs         # Google Drive操作
├── AIAnalyzer.gs           # AI分析
├── DatabaseManager.gs      # データベース管理
├── TimelineBuilder.gs      # 時系列生成
├── BatchProcessor.gs       # バッチ処理
├── UIManager.gs            # UI制御
├── Config.gs               # 設定
├── Utils.gs                # ユーティリティ
└── HTML/
    ├── Sidebar.html        # サイドバー
    ├── Dashboard.html      # ダッシュボード
    └── Styles.html         # CSS
```

### 1. Code.gs - メインエントリーポイント

```javascript
/**
 * Phase1 証拠分析システム - GAS版
 * 
 * メインエントリーポイント
 */

// スプレッドシート起動時の処理
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  
  ui.createMenu('📁 証拠管理システム')
    .addItem('🔍 証拠整理', 'organizeEvidence')
    .addItem('🤖 証拠分析', 'showAnalysisDialog')
    .addSeparator()
    .addItem('📊 時系列ストーリー生成', 'generateTimeline')
    .addItem('✏️ AI対話式改善', 'showEditDialog')
    .addSeparator()
    .addItem('📈 進捗確認', 'showProgress')
    .addItem('🔄 事件切り替え', 'switchCase')
    .addSeparator()
    .addItem('⚙️ 設定', 'showSettings')
    .addToUi();
}

// インストール時の処理
function onInstall(e) {
  onOpen(e);
  initializeSystem();
}

// システム初期化
function initializeSystem() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // 必要なシートを作成
  createSheetIfNotExists(ss, '証拠一覧');
  createSheetIfNotExists(ss, '証拠詳細');
  createSheetIfNotExists(ss, '時系列イベント');
  createSheetIfNotExists(ss, '依頼者発言');
  createSheetIfNotExists(ss, '事件情報');
  createSheetIfNotExists(ss, '設定');
  
  // ヘッダー行を設定
  setupHeaders();
  
  // 初期設定
  const configSheet = ss.getSheetByName('設定');
  if (configSheet.getLastRow() === 1) {
    configSheet.appendRow(['設定項目', '値']);
    configSheet.appendRow(['共有ドライブID', '']);
    configSheet.appendRow(['現在の事件ID', '']);
    configSheet.appendRow(['OpenAI API Key', '']);
    configSheet.appendRow(['Anthropic API Key', '']);
  }
  
  SpreadsheetApp.getUi().alert('システムの初期化が完了しました！');
}

// シートが存在しない場合は作成
function createSheetIfNotExists(ss, sheetName) {
  if (!ss.getSheetByName(sheetName)) {
    ss.insertSheet(sheetName);
  }
}

// ヘッダー行の設定
function setupHeaders() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // 証拠一覧シート
  const evidenceListSheet = ss.getSheetByName('証拠一覧');
  if (evidenceListSheet.getLastRow() === 0) {
    evidenceListSheet.appendRow([
      '証拠番号', 'ファイル名', '作成年月日', 'ステータス', 
      'Drive URL', '分析日時', '備考'
    ]);
    evidenceListSheet.getRange(1, 1, 1, 7).setFontWeight('bold');
  }
  
  // 証拠詳細シート
  const detailSheet = ss.getSheetByName('証拠詳細');
  if (detailSheet.getLastRow() === 0) {
    detailSheet.appendRow([
      '証拠番号', 'メタデータJSON', 'AI分析結果JSON', 
      '品質スコア', '言語化レベル', '最終更新'
    ]);
    detailSheet.getRange(1, 1, 1, 6).setFontWeight('bold');
  }
  
  // 時系列イベントシート
  const timelineSheet = ss.getSheetByName('時系列イベント');
  if (timelineSheet.getLastRow() === 0) {
    timelineSheet.appendRow([
      '日付', '証拠番号', 'イベント要約', '詳細説明', '法的重要性'
    ]);
    timelineSheet.getRange(1, 1, 1, 5).setFontWeight('bold');
  }
  
  // 依頼者発言シート
  const clientSheet = ss.getSheetByName('依頼者発言');
  if (clientSheet.getLastRow() === 0) {
    clientSheet.appendRow([
      '日付', '発言内容', '関連証拠', '登録日時'
    ]);
    clientSheet.getRange(1, 1, 1, 4).setFontWeight('bold');
  }
  
  // 事件情報シート
  const caseSheet = ss.getSheetByName('事件情報');
  if (caseSheet.getLastRow() === 0) {
    caseSheet.appendRow([
      '事件ID', '事件名', '原告', '被告', '裁判所', 'Driveフォルダ ID'
    ]);
    caseSheet.getRange(1, 1, 1, 6).setFontWeight('bold');
  }
}

// 証拠整理
function organizeEvidence() {
  const ui = SpreadsheetApp.getUi();
  const driveManager = new DriveManager();
  
  try {
    ui.alert('証拠整理を開始します...');
    
    const result = driveManager.organizeUnclassifiedEvidence();
    
    ui.alert(
      '証拠整理完了',
      `${result.organized}件の証拠を整理しました。\n` +
      `一時番号: ${result.tempIds.join(', ')}`,
      ui.ButtonSet.OK
    );
    
  } catch (error) {
    ui.alert('エラー', `証拠整理中にエラーが発生しました: ${error.message}`, ui.ButtonSet.OK);
    Logger.log(`Error in organizeEvidence: ${error.stack}`);
  }
}

// 証拠分析ダイアログ表示
function showAnalysisDialog() {
  const html = HtmlService.createHtmlOutputFromFile('AnalysisDialog')
    .setWidth(400)
    .setHeight(300);
  SpreadsheetApp.getUi().showModalDialog(html, '証拠分析');
}

// 証拠分析実行（ダイアログから呼び出される）
function analyzeEvidence(evidenceNumber) {
  const analyzer = new AIAnalyzer();
  const dbManager = new DatabaseManager();
  
  try {
    // 証拠情報を取得
    const evidenceInfo = dbManager.getEvidenceByNumber(evidenceNumber);
    if (!evidenceInfo) {
      throw new Error(`証拠番号 ${evidenceNumber} が見つかりません`);
    }
    
    // AI分析実行
    const analysisResult = analyzer.analyzeEvidence(evidenceInfo);
    
    // データベースに保存
    dbManager.saveAnalysisResult(evidenceNumber, analysisResult);
    
    return {
      success: true,
      message: `証拠番号 ${evidenceNumber} の分析が完了しました`,
      result: analysisResult
    };
    
  } catch (error) {
    Logger.log(`Error in analyzeEvidence: ${error.stack}`);
    return {
      success: false,
      message: `エラー: ${error.message}`
    };
  }
}

// 時系列ストーリー生成
function generateTimeline() {
  const ui = SpreadsheetApp.getUi();
  const builder = new TimelineBuilder();
  
  try {
    ui.alert('時系列ストーリーを生成します...');
    
    const timeline = builder.generateTimeline();
    
    // 結果をHTMLで表示
    const html = HtmlService.createHtmlOutput(timeline.html)
      .setWidth(800)
      .setHeight(600);
    ui.showModalDialog(html, '時系列ストーリー');
    
  } catch (error) {
    ui.alert('エラー', `時系列生成中にエラーが発生しました: ${error.message}`, ui.ButtonSet.OK);
    Logger.log(`Error in generateTimeline: ${error.stack}`);
  }
}

// 進捗確認
function showProgress() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('証拠一覧');
  const data = sheet.getDataRange().getValues();
  
  // ヘッダー行を除外
  const evidenceData = data.slice(1);
  
  const total = evidenceData.length;
  const confirmed = evidenceData.filter(row => row[3] === '確定').length;
  const pending = evidenceData.filter(row => row[3] === '未確定').length;
  const unprocessed = evidenceData.filter(row => !row[5]).length; // 分析日時が空
  
  const message = 
    `📊 証拠分析の進捗状況\n\n` +
    `合計証拠数: ${total}件\n` +
    `確定済み: ${confirmed}件\n` +
    `未確定: ${pending}件\n` +
    `未分析: ${unprocessed}件\n\n` +
    `進捗率: ${total > 0 ? Math.round((confirmed / total) * 100) : 0}%`;
  
  SpreadsheetApp.getUi().alert('進捗確認', message, SpreadsheetApp.getUi().ButtonSet.OK);
}

// 設定画面表示
function showSettings() {
  const html = HtmlService.createHtmlOutputFromFile('SettingsDialog')
    .setWidth(500)
    .setHeight(400);
  SpreadsheetApp.getUi().showModalDialog(html, '設定');
}
```

### 2. DriveManager.gs - Google Drive操作

```javascript
/**
 * Google Drive操作を管理するクラス
 */
class DriveManager {
  constructor() {
    this.config = this.loadConfig();
  }
  
  // 設定を読み込み
  loadConfig() {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const configSheet = ss.getSheetByName('設定');
    const data = configSheet.getDataRange().getValues();
    
    const config = {};
    for (let i = 1; i < data.length; i++) {
      config[data[i][0]] = data[i][1];
    }
    
    return config;
  }
  
  // 未分類フォルダから証拠を整理
  organizeUnclassifiedEvidence() {
    const caseFolderId = this.config['共有ドライブID'];
    if (!caseFolderId) {
      throw new Error('共有ドライブIDが設定されていません');
    }
    
    // フォルダ構造を取得・作成
    const folders = this.ensureFolderStructure(caseFolderId);
    
    // 未分類フォルダからファイルを取得
    const unclassifiedFiles = this.getFilesInFolder(folders.unclassified);
    
    const organized = [];
    const tempIds = [];
    
    // 各ファイルを処理
    unclassifiedFiles.forEach((file, index) => {
      const tempId = `tmp_${String(index + 1).padStart(3, '0')}`;
      
      // メタデータを抽出
      const metadata = this.extractMetadata(file);
      
      // データベースに登録
      this.registerEvidence(tempId, file, metadata);
      
      // 整理済み_未確定フォルダへ移動
      file.moveTo(folders.pending);
      
      organized.push(file.getName());
      tempIds.push(tempId);
    });
    
    return {
      organized: organized.length,
      tempIds: tempIds
    };
  }
  
  // フォルダ構造を確保
  ensureFolderStructure(rootFolderId) {
    const rootFolder = DriveApp.getFolderById(rootFolderId);
    
    return {
      root: rootFolder,
      unclassified: this.getOrCreateFolder(rootFolder, '未分類'),
      pending: this.getOrCreateFolder(rootFolder, '整理済み_未確定'),
      confirmed: this.getOrCreateFolder(rootFolder, '甲号証')
    };
  }
  
  // フォルダを取得または作成
  getOrCreateFolder(parentFolder, folderName) {
    const folders = parentFolder.getFoldersByName(folderName);
    
    if (folders.hasNext()) {
      return folders.next();
    } else {
      return parentFolder.createFolder(folderName);
    }
  }
  
  // フォルダ内のファイルを取得
  getFilesInFolder(folder) {
    const files = [];
    const iterator = folder.getFiles();
    
    while (iterator.hasNext()) {
      files.push(iterator.next());
    }
    
    return files;
  }
  
  // メタデータ抽出
  extractMetadata(file) {
    const metadata = {
      file_info: {
        filename: file.getName(),
        mime_type: file.getMimeType(),
        size_bytes: file.getSize(),
        created_date: file.getDateCreated().toISOString(),
        modified_date: file.getLastUpdated().toISOString()
      },
      hashes: {
        // GASでのハッシュ計算（制限あり）
        sha256: this.calculateSHA256(file),
        md5: this.calculateMD5(file)
      },
      gdrive: {
        file_id: file.getId(),
        file_url: file.getUrl(),
        download_url: `https://drive.google.com/uc?id=${file.getId()}&export=download`,
        preview_url: `https://drive.google.com/file/d/${file.getId()}/preview`
      }
    };
    
    // 画像の場合、Drive APIでメタデータ取得を試行
    if (file.getMimeType().startsWith('image/')) {
      try {
        const imageMetadata = this.getImageMetadata(file.getId());
        if (imageMetadata) {
          metadata.exif = imageMetadata;
        }
      } catch (error) {
        Logger.log(`EXIF extraction failed: ${error.message}`);
      }
    }
    
    return metadata;
  }
  
  // SHA-256ハッシュ計算
  calculateSHA256(file) {
    try {
      const blob = file.getBlob();
      const bytes = blob.getBytes();
      
      // 大きなファイルの場合はスキップ
      if (bytes.length > 50 * 1024 * 1024) { // 50MB
        return 'skipped_too_large';
      }
      
      const digest = Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, bytes);
      
      return digest.map(byte => {
        const hex = (byte < 0 ? byte + 256 : byte).toString(16);
        return hex.length === 1 ? '0' + hex : hex;
      }).join('');
      
    } catch (error) {
      Logger.log(`SHA-256 calculation failed: ${error.message}`);
      return 'error';
    }
  }
  
  // MD5ハッシュ計算
  calculateMD5(file) {
    try {
      const blob = file.getBlob();
      const bytes = blob.getBytes();
      
      if (bytes.length > 50 * 1024 * 1024) {
        return 'skipped_too_large';
      }
      
      const digest = Utilities.computeDigest(Utilities.DigestAlgorithm.MD5, bytes);
      
      return digest.map(byte => {
        const hex = (byte < 0 ? byte + 256 : byte).toString(16);
        return hex.length === 1 ? '0' + hex : hex;
      }).join('');
      
    } catch (error) {
      Logger.log(`MD5 calculation failed: ${error.message}`);
      return 'error';
    }
  }
  
  // 画像メタデータ取得（Drive API使用）
  getImageMetadata(fileId) {
    try {
      const file = Drive.Files.get(fileId, { fields: 'imageMediaMetadata' });
      
      if (file.imageMediaMetadata) {
        return {
          width: file.imageMediaMetadata.width,
          height: file.imageMediaMetadata.height,
          camera_make: file.imageMediaMetadata.cameraMake,
          camera_model: file.imageMediaMetadata.cameraModel,
          date_taken: file.imageMediaMetadata.date,
          location: file.imageMediaMetadata.location
        };
      }
      
      return null;
      
    } catch (error) {
      Logger.log(`Drive API image metadata failed: ${error.message}`);
      return null;
    }
  }
  
  // 証拠をデータベースに登録
  registerEvidence(tempId, file, metadata) {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = ss.getSheetByName('証拠一覧');
    
    sheet.appendRow([
      tempId,
      file.getName(),
      '', // 作成年月日（後でAI分析で埋める）
      '未確定',
      file.getUrl(),
      '', // 分析日時（未実施）
      ''  // 備考
    ]);
    
    // 詳細シートにメタデータを保存
    const detailSheet = ss.getSheetByName('証拠詳細');
    detailSheet.appendRow([
      tempId,
      JSON.stringify(metadata),
      '', // AI分析結果（未実施）
      '', // 品質スコア
      '', // 言語化レベル
      new Date().toISOString()
    ]);
  }
  
  // ファイルを取得
  getFileById(fileId) {
    return DriveApp.getFileById(fileId);
  }
  
  // ファイルをBase64エンコード
  getFileAsBase64(file) {
    try {
      const blob = file.getBlob();
      const bytes = blob.getBytes();
      
      // 大きなファイルの場合はエラー
      if (bytes.length > 10 * 1024 * 1024) { // 10MB
        throw new Error('ファイルサイズが大きすぎます（10MB以下にしてください）');
      }
      
      return Utilities.base64Encode(bytes);
      
    } catch (error) {
      throw new Error(`Base64エンコード失敗: ${error.message}`);
    }
  }
}
```

### 3. AIAnalyzer.gs - AI分析エンジン

```javascript
/**
 * AI分析を管理するクラス
 */
class AIAnalyzer {
  constructor() {
    this.config = this.loadConfig();
    this.openaiApiKey = this.config['OpenAI API Key'];
    this.anthropicApiKey = this.config['Anthropic API Key'];
  }
  
  // 設定を読み込み
  loadConfig() {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const configSheet = ss.getSheetByName('設定');
    const data = configSheet.getDataRange().getValues();
    
    const config = {};
    for (let i = 1; i < data.length; i++) {
      config[data[i][0]] = data[i][1];
    }
    
    return config;
  }
  
  // 証拠分析のメイン処理
  analyzeEvidence(evidenceInfo) {
    try {
      // ファイルを取得
      const driveManager = new DriveManager();
      const file = driveManager.getFileById(evidenceInfo.fileId);
      
      // ファイルタイプに応じて分析
      const mimeType = file.getMimeType();
      
      if (mimeType.startsWith('image/')) {
        return this.analyzeImage(file);
      } else if (mimeType === 'application/pdf') {
        return this.analyzePDF(file);
      } else if (mimeType.includes('document')) {
        return this.analyzeDocument(file);
      } else {
        throw new Error(`未対応のファイル形式: ${mimeType}`);
      }
      
    } catch (error) {
      Logger.log(`Analysis error: ${error.stack}`);
      throw error;
    }
  }
  
  // 画像分析
  analyzeImage(file) {
    const driveManager = new DriveManager();
    const base64Image = driveManager.getFileAsBase64(file);
    
    // まずOpenAI GPT-4o Visionを試行
    try {
      return this.analyzeWithGPT4Vision(base64Image, file.getMimeType());
    } catch (error) {
      Logger.log(`GPT-4o Vision failed, trying Claude: ${error.message}`);
      
      // フォールバック: Claude Vision
      if (this.anthropicApiKey) {
        return this.analyzeWithClaudeVision(base64Image, file.getMimeType());
      } else {
        throw new Error('OpenAI分析が失敗し、Claude APIキーも設定されていません');
      }
    }
  }
  
  // GPT-4o Visionで分析
  analyzeWithGPT4Vision(base64Image, mimeType) {
    const prompt = this.getAnalysisPrompt();
    
    const payload = {
      model: "gpt-4o",
      messages: [{
        role: "user",
        content: [
          { 
            type: "text", 
            text: prompt
          },
          { 
            type: "image_url", 
            image_url: { 
              url: `data:${mimeType};base64,${base64Image}`,
              detail: "high"
            } 
          }
        ]
      }],
      max_tokens: 4000,
      temperature: 0.1
    };
    
    const options = {
      method: 'post',
      contentType: 'application/json',
      headers: { 
        'Authorization': 'Bearer ' + this.openaiApiKey 
      },
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    };
    
    const response = UrlFetchApp.fetch('https://api.openai.com/v1/chat/completions', options);
    const responseCode = response.getResponseCode();
    
    if (responseCode !== 200) {
      throw new Error(`OpenAI API error: ${responseCode} - ${response.getContentText()}`);
    }
    
    const result = JSON.parse(response.getContentText());
    
    // レスポンスからJSON部分を抽出
    const content = result.choices[0].message.content;
    const analysisResult = this.extractJSON(content);
    
    return {
      provider: 'OpenAI GPT-4o Vision',
      timestamp: new Date().toISOString(),
      analysis: analysisResult
    };
  }
  
  // Claude Visionで分析
  analyzeWithClaudeVision(base64Image, mimeType) {
    const prompt = this.getAnalysisPrompt();
    
    const payload = {
      model: "claude-sonnet-4-20250514",
      max_tokens: 4000,
      messages: [{
        role: "user",
        content: [
          { 
            type: "image", 
            source: { 
              type: "base64", 
              media_type: mimeType, 
              data: base64Image 
            } 
          },
          { 
            type: "text", 
            text: prompt 
          }
        ]
      }]
    };
    
    const options = {
      method: 'post',
      contentType: 'application/json',
      headers: { 
        'x-api-key': this.anthropicApiKey,
        'anthropic-version': '2023-06-01'
      },
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    };
    
    const response = UrlFetchApp.fetch('https://api.anthropic.com/v1/messages', options);
    const responseCode = response.getResponseCode();
    
    if (responseCode !== 200) {
      throw new Error(`Claude API error: ${responseCode} - ${response.getContentText()}`);
    }
    
    const result = JSON.parse(response.getContentText());
    const content = result.content[0].text;
    const analysisResult = this.extractJSON(content);
    
    return {
      provider: 'Anthropic Claude Sonnet 4',
      timestamp: new Date().toISOString(),
      analysis: analysisResult
    };
  }
  
  // 分析プロンプト取得
  getAnalysisPrompt() {
    return `
あなたは民事訴訟における証拠ファイルの完全言語化を行う専門家です。

以下の証拠画像を分析し、**完全言語化レベル4**（原文参照不要）の詳細記述を生成してください。

## 出力形式（JSON）

\`\`\`json
{
  "objective_analysis": {
    "complete_description": "この証拠は...[詳細な完全言語化]",
    "observable_facts": [
      "事実1の詳細な記述",
      "事実2の詳細な記述"
    ],
    "temporal_information": {
      "document_date": "YYYY-MM-DD",
      "document_date_source": "日付の根拠（例: 契約書末尾の契約締結日）",
      "date_confidence": "high/medium/low - 理由",
      "other_dates": [
        {"date": "YYYY-MM-DD", "context": "日付の意味"}
      ]
    },
    "parties_mentioned": [
      {
        "name": "人物名",
        "role": "役割",
        "context": "文脈"
      }
    ],
    "financial_information": {
      "amounts": [
        {"amount": 1000000, "currency": "JPY", "context": "金額の意味"}
      ],
      "total_amount": 1000000
    },
    "document_state": {
      "completeness": "完全/不完全/部分的",
      "legibility": "明瞭/やや不明瞭/不明瞭",
      "authenticity_indicators": ["署名あり", "社印あり"]
    }
  },
  "quality_assessment": {
    "completeness_score": 95.0,
    "confidence_score": 90.0,
    "verbalization_level": 4
  }
}
\`\`\`

## 重要な指示

1. **作成年月日の特定**（最優先）
   - 文書: 文書上部の日付、「作成日」の明示
   - 契約書: 契約締結日（署名欄付近の日付）
   - メール: 送信日時
   - 領収書・請求書: 発行日
   - 写真: 撮影日時（画像内の日付表示）

2. **完全言語化**
   - 原文参照なしで内容を完全に理解できる記述
   - 重要な固有名詞、日付、金額は必ず明記
   - 観察可能な事実のみを記述（推測や法的評価は不要）

3. **客観性の維持**
   - 中立的な立場で記述
   - 「原告に有利」「被告に不利」などの評価は含めない

必ずJSON形式で出力してください。
`;
  }
  
  // レスポンスからJSON抽出
  extractJSON(content) {
    // ```json ... ``` で囲まれている場合
    const jsonMatch = content.match(/```json\s*([\s\S]*?)\s*```/);
    if (jsonMatch) {
      return JSON.parse(jsonMatch[1]);
    }
    
    // { ... } の形式を直接探す
    const objectMatch = content.match(/\{[\s\S]*\}/);
    if (objectMatch) {
      return JSON.parse(objectMatch[0]);
    }
    
    throw new Error('AIレスポンスからJSONを抽出できませんでした');
  }
  
  // PDF分析
  analyzePDF(file) {
    // PDFの場合はテキスト抽出してGPT-4oで分析
    const text = this.extractPDFText(file);
    return this.analyzeText(text, 'PDF文書');
  }
  
  // PDF テキスト抽出
  extractPDFText(file) {
    // GASではPDFテキスト抽出が困難
    // 対策: Google Drive APIでテキストに変換
    try {
      const fileId = file.getId();
      const exportUrl = `https://www.googleapis.com/drive/v3/files/${fileId}/export?mimeType=text/plain`;
      
      const options = {
        headers: {
          'Authorization': 'Bearer ' + ScriptApp.getOAuthToken()
        }
      };
      
      const response = UrlFetchApp.fetch(exportUrl, options);
      return response.getContentText();
      
    } catch (error) {
      Logger.log(`PDF text extraction failed: ${error.message}`);
      return '[PDFテキスト抽出失敗]';
    }
  }
  
  // テキスト分析
  analyzeText(text, documentType) {
    const prompt = `
以下は${documentType}のテキスト内容です。

${text}

このテキストを分析し、完全言語化レベル4の記述とメタデータをJSON形式で出力してください。

出力形式:
${this.getAnalysisPrompt()}
`;
    
    const payload = {
      model: "gpt-4o",
      messages: [{
        role: "user",
        content: prompt
      }],
      max_tokens: 4000,
      temperature: 0.1
    };
    
    const options = {
      method: 'post',
      contentType: 'application/json',
      headers: { 
        'Authorization': 'Bearer ' + this.openaiApiKey 
      },
      payload: JSON.stringify(payload)
    };
    
    const response = UrlFetchApp.fetch('https://api.openai.com/v1/chat/completions', options);
    const result = JSON.parse(response.getContentText());
    const content = result.choices[0].message.content;
    const analysisResult = this.extractJSON(content);
    
    return {
      provider: 'OpenAI GPT-4o',
      timestamp: new Date().toISOString(),
      analysis: analysisResult
    };
  }
  
  // 文書分析
  analyzeDocument(file) {
    // Word文書などはテキストに変換して分析
    const text = this.extractDocumentText(file);
    return this.analyzeText(text, 'Word文書');
  }
  
  // 文書テキスト抽出
  extractDocumentText(file) {
    try {
      const fileId = file.getId();
      const exportUrl = `https://www.googleapis.com/drive/v3/files/${fileId}/export?mimeType=text/plain`;
      
      const options = {
        headers: {
          'Authorization': 'Bearer ' + ScriptApp.getOAuthToken()
        }
      };
      
      const response = UrlFetchApp.fetch(exportUrl, options);
      return response.getContentText();
      
    } catch (error) {
      Logger.log(`Document text extraction failed: ${error.message}`);
      return '[文書テキスト抽出失敗]';
    }
  }
}
```

### 4. DatabaseManager.gs - データベース管理

```javascript
/**
 * スプレッドシートデータベースを管理するクラス
 */
class DatabaseManager {
  constructor() {
    this.ss = SpreadsheetApp.getActiveSpreadsheet();
    this.evidenceListSheet = this.ss.getSheetByName('証拠一覧');
    this.evidenceDetailSheet = this.ss.getSheetByName('証拠詳細');
    this.timelineSheet = this.ss.getSheetByName('時系列イベント');
    this.clientSheet = this.ss.getSheetByName('依頼者発言');
  }
  
  // 証拠番号で証拠情報を取得
  getEvidenceByNumber(evidenceNumber) {
    const data = this.evidenceListSheet.getDataRange().getValues();
    
    // ヘッダー行をスキップして検索
    for (let i = 1; i < data.length; i++) {
      if (data[i][0] === evidenceNumber) {
        // Drive URLからファイルIDを抽出
        const driveUrl = data[i][4];
        const fileIdMatch = driveUrl.match(/\/d\/([a-zA-Z0-9_-]+)/);
        const fileId = fileIdMatch ? fileIdMatch[1] : null;
        
        return {
          evidenceNumber: data[i][0],
          fileName: data[i][1],
          documentDate: data[i][2],
          status: data[i][3],
          driveUrl: data[i][4],
          analyzedAt: data[i][5],
          notes: data[i][6],
          fileId: fileId,
          rowIndex: i + 1 // 1-based index
        };
      }
    }
    
    return null;
  }
  
  // AI分析結果を保存
  saveAnalysisResult(evidenceNumber, analysisResult) {
    // 証拠一覧シートを更新
    const evidenceInfo = this.getEvidenceByNumber(evidenceNumber);
    if (!evidenceInfo) {
      throw new Error(`証拠番号 ${evidenceNumber} が見つかりません`);
    }
    
    // 作成年月日を抽出
    const documentDate = analysisResult.analysis.objective_analysis.temporal_information.document_date;
    
    // 証拠一覧シートの該当行を更新
    this.evidenceListSheet.getRange(evidenceInfo.rowIndex, 3).setValue(documentDate); // 作成年月日
    this.evidenceListSheet.getRange(evidenceInfo.rowIndex, 6).setValue(new Date()); // 分析日時
    
    // 証拠詳細シートを更新
    const detailData = this.evidenceDetailSheet.getDataRange().getValues();
    let detailRowIndex = -1;
    
    for (let i = 1; i < detailData.length; i++) {
      if (detailData[i][0] === evidenceNumber) {
        detailRowIndex = i + 1;
        break;
      }
    }
    
    if (detailRowIndex > 0) {
      // 既存行を更新
      this.evidenceDetailSheet.getRange(detailRowIndex, 3).setValue(JSON.stringify(analysisResult)); // AI分析結果
      this.evidenceDetailSheet.getRange(detailRowIndex, 4).setValue(analysisResult.analysis.quality_assessment.completeness_score); // 品質スコア
      this.evidenceDetailSheet.getRange(detailRowIndex, 5).setValue(analysisResult.analysis.quality_assessment.verbalization_level); // 言語化レベル
      this.evidenceDetailSheet.getRange(detailRowIndex, 6).setValue(new Date().toISOString()); // 最終更新
    }
    
    // 時系列イベントシートに追加
    if (documentDate) {
      const completeDescription = analysisResult.analysis.objective_analysis.complete_description;
      const eventSummary = completeDescription.substring(0, 100) + '...'; // 最初の100文字
      
      this.timelineSheet.appendRow([
        documentDate,
        evidenceNumber,
        eventSummary,
        completeDescription,
        '' // 法的重要性（後で追加可能）
      ]);
    }
  }
  
  // すべての証拠を取得
  getAllEvidence() {
    const data = this.evidenceListSheet.getDataRange().getValues();
    const evidenceList = [];
    
    for (let i = 1; i < data.length; i++) {
      evidenceList.push({
        evidenceNumber: data[i][0],
        fileName: data[i][1],
        documentDate: data[i][2],
        status: data[i][3],
        driveUrl: data[i][4],
        analyzedAt: data[i][5],
        notes: data[i][6]
      });
    }
    
    return evidenceList;
  }
  
  // 時系列イベントを取得（日付順）
  getTimelineEvents() {
    const data = this.timelineSheet.getDataRange().getValues();
    const events = [];
    
    for (let i = 1; i < data.length; i++) {
      if (data[i][0]) { // 日付がある行のみ
        events.push({
          date: data[i][0],
          evidenceNumber: data[i][1],
          summary: data[i][2],
          detail: data[i][3],
          legalSignificance: data[i][4]
        });
      }
    }
    
    // 日付でソート
    events.sort((a, b) => {
      const dateA = new Date(a.date);
      const dateB = new Date(b.date);
      return dateA - dateB;
    });
    
    return events;
  }
  
  // 依頼者発言を追加
  addClientStatement(date, statement, relatedEvidence) {
    this.clientSheet.appendRow([
      date,
      statement,
      relatedEvidence,
      new Date().toISOString()
    ]);
  }
  
  // 依頼者発言を取得
  getClientStatements() {
    const data = this.clientSheet.getDataRange().getValues();
    const statements = [];
    
    for (let i = 1; i < data.length; i++) {
      statements.push({
        date: data[i][0],
        statement: data[i][1],
        relatedEvidence: data[i][2],
        registeredAt: data[i][3]
      });
    }
    
    return statements;
  }
  
  // database.jsonをGoogle Driveにエクスポート
  exportToDriveJSON() {
    const databaseObj = {
      case_info: this.getCaseInfo(),
      evidence: this.getAllEvidenceWithDetails(),
      timeline_events: this.getTimelineEvents(),
      client_statements: this.getClientStatements(),
      exported_at: new Date().toISOString()
    };
    
    const jsonString = JSON.stringify(databaseObj, null, 2);
    
    // Google Driveに保存
    const fileName = `database_${new Date().toISOString().split('T')[0]}.json`;
    const folder = DriveApp.getRootFolder(); // または特定のフォルダ
    
    folder.createFile(fileName, jsonString, MimeType.PLAIN_TEXT);
    
    return fileName;
  }
  
  // すべての証拠（詳細含む）を取得
  getAllEvidenceWithDetails() {
    const listData = this.evidenceListSheet.getDataRange().getValues();
    const detailData = this.evidenceDetailSheet.getDataRange().getValues();
    
    const evidenceList = [];
    
    for (let i = 1; i < listData.length; i++) {
      const evidenceNumber = listData[i][0];
      
      // 詳細情報を検索
      let metadata = {};
      let analysisResult = {};
      
      for (let j = 1; j < detailData.length; j++) {
        if (detailData[j][0] === evidenceNumber) {
          try {
            metadata = JSON.parse(detailData[j][1] || '{}');
            analysisResult = JSON.parse(detailData[j][2] || '{}');
          } catch (e) {
            Logger.log(`JSON parse error for ${evidenceNumber}: ${e.message}`);
          }
          break;
        }
      }
      
      evidenceList.push({
        evidence_number: evidenceNumber,
        file_name: listData[i][1],
        document_date: listData[i][2],
        status: listData[i][3],
        complete_metadata: metadata,
        phase1_complete_analysis: analysisResult
      });
    }
    
    return evidenceList;
  }
  
  // 事件情報を取得
  getCaseInfo() {
    const caseSheet = this.ss.getSheetByName('事件情報');
    const data = caseSheet.getDataRange().getValues();
    
    if (data.length > 1) {
      return {
        case_id: data[1][0],
        case_name: data[1][1],
        plaintiff: data[1][2],
        defendant: data[1][3],
        court: data[1][4]
      };
    }
    
    return {};
  }
}
```

---

## まとめ

### ✅ GASでの実現可能性: **80-90%**

現在のシステムの主要機能のほとんどはGASで実現可能です。

### 推奨実装戦略

1. **フェーズ1（2週間）**: MVPを実装
   - 基本的なDrive連携
   - スプレッドシートDB
   - OpenAI API連携
   - シンプルUI

2. **フェーズ2（1週間）**: 自動化
   - バッチ処理
   - Form連携
   - トリガー設定

3. **フェーズ3（1週間）**: 高度な機能
   - Claude API統合
   - 時系列ストーリー生成
   - マルチ事件対応

### 主な利点

- ✅ **インストール不要**: ブラウザで完結
- ✅ **クラウドベース**: どこからでもアクセス
- ✅ **共有が容易**: 複数ユーザーで共同作業
- ✅ **コスト効率**: サーバー管理不要

### 主な制約

- ⚠️ **実行時間制限**: 6分/実行
- ⚠️ **大容量ファイル**: 処理が困難
- ⚠️ **Python専用機能**: 一部は外部API必要

**総合評価**: GASでの実装は十分実現可能であり、特にチームでの共同作業や日常的な証拠管理においては現行のPythonシステムよりも使いやすい可能性があります。

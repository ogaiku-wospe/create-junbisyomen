# ファイル整理計画

## 📊 現状分析（2025-10-20）

### 総ファイル数: 31ファイル

## 🔍 ファイル分類

### ✅ 【必須】コアシステムファイル（保持）

#### 設定ファイル
- **global_config.py** (8.8KB) - ✅ **最新版** - 共有ドライブID一元管理
- ~~config.py~~ (8.9KB) - ❌ **旧版・削除候補** - 単一事件用（global_config.pyに統合済み）
- ~~config_template.py~~ (11KB) - ❌ **不要** - global_config.pyで代替可能

#### 実行スクリプト
- **run_phase1_multi.py** (21KB) - ✅ **最新版** - マルチ事件対応実行スクリプト
- ~~run_multi_case.py~~ (8.2KB) - ❌ **重複** - run_phase1_multi.pyと機能重複
- ~~run_phase1.py~~ (13KB) - ⚠️ **旧版** - 単一事件用（互換性のため残す）
- ~~phase1_cli.py~~ (10KB) - ❌ **旧版** - run_phase1_multi.pyに統合済み

#### 事件管理
- **case_manager.py** (18KB) - ✅ **最新版** - 事件自動検出・管理
- ~~case_selector.py~~ (5.7KB) - ❌ **旧版** - case_manager.pyに統合済み

#### 処理エンジン
- **metadata_extractor.py** (16KB) - ✅ 必須 - メタデータ抽出
- **file_processor.py** (24KB) - ✅ 必須 - ファイル処理
- **ai_analyzer_complete.py** (20KB) - ✅ 必須 - AI分析エンジン

#### バッチ処理
- **batch_process.py** (17KB) - ✅ 必須 - 一括処理機能
- ~~custom_workflow.py~~ (11KB) - ⚠️ **オプション** - カスタムワークフロー（使用頻度低）

#### セットアップ
- **setup_new_case.py** (18KB) - ⚠️ **旧版だが有用** - 新規事件セットアップ（手動フォルダ作成時に使用）

### 📚 【ドキュメント】整理が必要

#### メインREADME
- **README.md** (7.2KB) - ✅ **更新必要** - メインREADME（マルチ事件対応版の説明を追加）
- **README_MULTI_CASE.md** (13KB) - ✅ **最新版** - マルチ事件対応版の詳細ガイド
- ~~README_COMPLETE.md~~ (9.7KB) - ❌ **旧版** - 古い完全版説明（README_MULTI_CASE.mdに統合）

#### システム概要
- ~~COMPLETE_SYSTEM_SUMMARY.md~~ (17KB) - ❌ **古い実装報告** - 歴史的文書（不要）

#### 使用ガイド
- **USAGE_GUIDE.md** (17KB) - ⚠️ **要更新** - 詳細な使用方法（マルチ事件対応版に更新）
- ~~RESUME_AND_BATCH_GUIDE.md~~ (14KB) - ⚠️ **統合候補** - USAGE_GUIDE.mdに統合可能

#### Google Drive関連
- **GOOGLE_DRIVE_GUIDE.md** (25KB) - ✅ 必須 - Google Drive設定方法
- ~~GOOGLE_DRIVE_INTEGRATION_GUIDE.md~~ (20KB) - ❌ **重複** - GOOGLE_DRIVE_GUIDE.mdと内容重複

#### 事件管理関連
- ~~MULTI_CASE_GUIDE.md~~ (14KB) - ❌ **旧版** - README_MULTI_CASE.mdで代替
- ~~CASE_SELECTION_GUIDE.md~~ (8.0KB) - ❌ **旧版** - case_manager.pyで代替
- ~~CASE_SELECTOR_GUIDE.md~~ (11KB) - ❌ **旧版** - case_manager.pyで代替

### 🔧 【設定・スキーマ】

- **database_schema_v3.json** (11KB) - ✅ 必須 - データベーススキーマ定義
- **requirements.txt** (382B) - ✅ 必須 - 依存パッケージ
- **.env.example** - ✅ 必須 - 環境変数サンプル
- **credentials.json.example** - ✅ 必須 - Google認証サンプル
- **.gitignore** - ✅ 必須 - Git除外設定

### 📁 【プロンプト】

- **prompts/Phase1_EvidenceAnalysis.txt** - ✅ 必須 - AI分析用プロンプト

---

## 🗑️ 削除推奨ファイル（14ファイル）

### 設定ファイル（旧版）
1. ❌ `config.py` - global_config.pyに統合済み
2. ❌ `config_template.py` - global_config.pyで代替可能

### 実行スクリプト（重複・旧版）
3. ❌ `run_multi_case.py` - run_phase1_multi.pyと機能重複
4. ❌ `phase1_cli.py` - run_phase1_multi.pyに統合済み

### 事件管理（旧版）
5. ❌ `case_selector.py` - case_manager.pyに統合済み

### カスタムワークフロー（使用頻度低）
6. ⚠️ `custom_workflow.py` - オプション（削除検討）

### ドキュメント（重複・旧版）
7. ❌ `README_COMPLETE.md` - README_MULTI_CASE.mdに統合
8. ❌ `COMPLETE_SYSTEM_SUMMARY.md` - 古い実装報告
9. ❌ `GOOGLE_DRIVE_INTEGRATION_GUIDE.md` - GOOGLE_DRIVE_GUIDE.mdと重複
10. ❌ `MULTI_CASE_GUIDE.md` - README_MULTI_CASE.mdで代替
11. ❌ `CASE_SELECTION_GUIDE.md` - case_manager.pyで代替
12. ❌ `CASE_SELECTOR_GUIDE.md` - case_manager.pyで代替
13. ⚠️ `RESUME_AND_BATCH_GUIDE.md` - USAGE_GUIDE.mdに統合可能

---

## ✏️ 更新推奨ファイル（3ファイル）

1. **README.md** - マルチ事件対応版の説明を追加
2. **USAGE_GUIDE.md** - マルチ事件対応版の手順に更新
3. ~~run_phase1.py~~ - 旧版だが互換性のため保持（ドキュメントで「非推奨」と明記）

---

## 📂 最適化後のファイル構造（17ファイル）

```
create-junbisyomen/
├── 📄 設定
│   ├── global_config.py          ✅ 最新版
│   ├── .env.example              ✅
│   └── credentials.json.example  ✅
│
├── 🚀 実行スクリプト
│   ├── run_phase1_multi.py       ✅ 最新版（推奨）
│   ├── run_phase1.py             ⚠️ 旧版（互換性のため保持）
│   ├── batch_process.py          ✅
│   └── setup_new_case.py         ⚠️ 旧版だが有用
│
├── 🔧 コアエンジン
│   ├── case_manager.py           ✅ 最新版
│   ├── metadata_extractor.py     ✅
│   ├── file_processor.py         ✅
│   └── ai_analyzer_complete.py   ✅
│
├── 📚 ドキュメント
│   ├── README.md                 ✅ 要更新
│   ├── README_MULTI_CASE.md      ✅ 最新版
│   ├── USAGE_GUIDE.md            ⚠️ 要更新
│   └── GOOGLE_DRIVE_GUIDE.md     ✅
│
├── 🗂️ スキーマ・設定
│   ├── database_schema_v3.json   ✅
│   ├── requirements.txt          ✅
│   └── .gitignore                ✅
│
└── 📁 prompts/
    └── Phase1_EvidenceAnalysis.txt ✅
```

---

## 🎯 整理アクション

### ステップ1: 削除（13ファイル）
```bash
# 旧版設定ファイル
rm config.py config_template.py

# 旧版実行スクリプト
rm run_multi_case.py phase1_cli.py

# 旧版事件管理
rm case_selector.py

# 重複・旧版ドキュメント
rm README_COMPLETE.md COMPLETE_SYSTEM_SUMMARY.md
rm GOOGLE_DRIVE_INTEGRATION_GUIDE.md
rm MULTI_CASE_GUIDE.md CASE_SELECTION_GUIDE.md CASE_SELECTOR_GUIDE.md
rm RESUME_AND_BATCH_GUIDE.md

# オプション（必要に応じて）
# rm custom_workflow.py
```

### ステップ2: 更新
- `README.md` - マルチ事件対応版の説明を追加
- `USAGE_GUIDE.md` - 最新の使用方法に更新

### ステップ3: 新規作成
- `docs/` ディレクトリを作成してドキュメントを整理（オプション）

---

## 📊 整理効果

- **削除**: 13ファイル（約150KB）
- **保持**: 17ファイル（約220KB）
- **削減率**: 43% のファイル数削減
- **明確性**: 最新版と旧版の区別が明確に

---

**作成日**: 2025-10-20  
**目的**: ファイル構造の最適化とメンテナンス性向上

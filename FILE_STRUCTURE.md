# 📁 Phase 1システム - ファイル構造

## 🎯 整理済みのディレクトリ構造

```
create-junbisyomen/
├── 📄 README.md                       # メインREADME
├── 📄 QUICKSTART.md                   # クイックスタート
├── 📄 FILE_STRUCTURE.md              # このファイル
├── 📄 FILE_REORGANIZATION_PLAN.md    # 整理計画
├── 📄 requirements.txt               # Python依存関係
├── 📄 global_config.py               # グローバル設定
├── 📄 .gitignore                     # Git除外設定
│
├── ⚡ run_phase1.py                   # メイン実行スクリプト
├── ⚡ run_phase1_multi.py             # マルチケース実行
├── ⚡ batch_process.py                # バッチ処理
│
├── 📚 docs/                           # すべてのドキュメント
│   ├── README.md                      # ドキュメント索引
│   │
│   ├── user-guides/                   # ユーザーガイド
│   │   ├── USAGE_GUIDE.md
│   │   ├── GOOGLE_DRIVE_GUIDE.md
│   │   ├── TIMELINE_STORY_GUIDE.md
│   │   └── README_MULTI_CASE.md
│   │
│   ├── setup-guides/                  # セットアップガイド
│   │   ├── MIGRATION_QUICK_START.md
│   │   ├── MIGRATION_GUIDE_v3.2.md
│   │   ├── MIGRATION_V3.2.md
│   │   ├── UPDATE_GUIDE.md
│   │   ├── UPDATE_LOCAL_FROM_GITHUB.md
│   │   ├── LOCAL_UPDATE_INSTRUCTIONS.txt
│   │   └── QUICK_UPDATE_GUIDE.txt
│   │
│   ├── feature-guides/                # 機能ガイド
│   │   ├── EVIDENCE_TYPE_FEATURE.md
│   │   ├── EVIDENCE_TYPE_SEPARATION_GUIDE.md
│   │   ├── HIERARCHICAL_FOLDERS.md
│   │   ├── EVIDENCE_ID_CONVERSION_GUIDE.md
│   │   ├── EVIDENCE_STATUS_FIX_GUIDE.md
│   │   └── DISPLAY_FIX_GUIDE.md
│   │
│   ├── maintenance/                   # メンテナンスガイド
│   │   ├── CLEANUP_INSTRUCTIONS.md
│   │   ├── QUICK_CLEANUP_GUIDE.md
│   │   └── FIXES_v3.7.2.md
│   │
│   ├── architecture/                  # アーキテクチャ
│   │   ├── SYSTEM_STRUCTURE_SUMMARY.md
│   │   ├── DATABASE_JSON_FIELDS_COMPLETE_LIST.md
│   │   ├── DATABASE_JSON_FOR_AI_USAGE.md
│   │   ├── database_schema_v3.json
│   │   ├── database_schema_v3.1_practical.json ⭐ 最新
│   │   ├── GAS_FEASIBILITY_ANALYSIS.md
│   │   ├── GAS_VS_PYTHON_RECOMMENDATION.md
│   │   └── FILE_ORGANIZATION_PLAN.md
│   │
│   ├── phase1-improvements/           # Phase 1改善版（v3.1）
│   │   ├── IMPLEMENTATION_SUMMARY_V3.1.md ⭐ 重要
│   │   ├── PHASE1_PRACTICAL_IMPROVEMENT_PLAN.md
│   │   ├── PRACTICAL_USAGE_GUIDE_V3.1.md
│   │   └── USABILITY_IMPROVEMENT_PLAN.md
│   │
│   ├── changelogs/                    # 変更履歴
│   │   ├── CHANGELOG_v3.6.1.md
│   │   ├── CHANGELOG_v3.7.0.md
│   │   ├── CHANGELOG_v3.7.1.md
│   │   ├── IMPROVEMENTS.md
│   │   ├── IMPLEMENTATION_SUMMARY.md
│   │   ├── IMPLEMENTATION_SUMMARY_TIMELINE.md
│   │   └── COMPLETION_SUMMARY.md
│   │
│   └── templates/                     # テンプレート
│       ├── .env.example
│       └── credentials.json.example
│
├── 🐍 src/                            # Pythonソースコード
│   ├── __init__.py
│   ├── ai_analyzer_complete.py       # AI分析エンジン
│   ├── case_manager.py               # 事件管理
│   ├── evidence_organizer.py         # 証拠整理
│   ├── evidence_editor_ai.py         # 証拠編集AI
│   ├── file_processor.py             # ファイル処理
│   ├── gdrive_database_manager.py    # GDrive DB管理
│   ├── metadata_extractor.py         # メタデータ抽出
│   ├── timeline_builder.py           # タイムライン生成
│   └── utils/
│       ├── __init__.py
│       └── database_cleanup.py
│
├── 🔧 scripts/                        # ユーティリティスクリプト
│   ├── maintenance/                   # メンテナンス
│   │   ├── cleanup_local_database.py
│   │   ├── convert_evidence_ids.py
│   │   ├── migrate_to_hierarchical_folders.py
│   │   └── system_integrity_check.py
│   │
│   ├── analysis/                      # 分析ツール
│   │   ├── add_analysis_method_info.py
│   │   ├── check_analysis_methods.py
│   │   └── improve_usability.py
│   │
│   ├── setup/                         # セットアップ
│   │   ├── setup_new_case.py
│   │   └── check_permissions.py
│   │
│   ├── testing/                       # テスト
│   │   ├── test_gdrive_database.py
│   │   ├── test_timeline_builder.py
│   │   ├── debug_folders.py
│   │   └── find_shared_drives.py
│   │
│   └── shell/                         # シェルスクリプト
│       ├── setup.sh
│       ├── setup.bat
│       ├── start.sh
│       ├── start.bat
│       ├── start.command
│       ├── cleanup_project.sh
│       ├── cleanup_project.bat
│       ├── convert_ids.sh
│       ├── update_local.sh
│       ├── update_local_repo.sh
│       ├── update_local_repo.bat
│       └── update_local_repo.command
│
├── 📝 prompts/                        # AIプロンプト
│   ├── Phase1_EvidenceAnalysis.txt
│   └── Phase1_EvidenceAnalysis_v2_Practical.txt ⭐ 最新
│
└── 📊 data/                           # データファイル
    ├── database_uploaded.json
    └── analysis_method_report.json
```

---

## 🎯 ディレクトリの役割

### ルートディレクトリ
必要最小限のファイルのみ配置

| ファイル | 説明 |
|---------|------|
| `README.md` | システム全体の説明 |
| `QUICKSTART.md` | クイックスタート |
| `requirements.txt` | Python依存関係 |
| `global_config.py` | 設定ファイル |
| `run_phase1.py` | メイン実行スクリプト |
| `run_phase1_multi.py` | マルチケース実行 |
| `batch_process.py` | バッチ処理 |

### 📚 docs/ - ドキュメント
すべてのドキュメントを用途別に整理

| ディレクトリ | 内容 |
|------------|------|
| `user-guides/` | 日常的な使用方法 |
| `setup-guides/` | インストール・移行 |
| `feature-guides/` | 個別機能説明 |
| `maintenance/` | メンテナンス |
| `architecture/` | システム設計 |
| `phase1-improvements/` | v3.1改善版 |
| `changelogs/` | 変更履歴 |
| `templates/` | 設定テンプレート |

### 🐍 src/ - ソースコード
メインのPythonコード

| ファイル | 説明 |
|---------|------|
| `ai_analyzer_complete.py` | AI分析エンジン（GPT-4o/Claude） |
| `case_manager.py` | 事件管理 |
| `evidence_organizer.py` | 証拠整理 |
| `file_processor.py` | ファイル処理 |
| `metadata_extractor.py` | メタデータ抽出 |
| `timeline_builder.py` | タイムライン生成 |

### 🔧 scripts/ - スクリプト
ユーティリティスクリプト

| ディレクトリ | 内容 |
|------------|------|
| `maintenance/` | データベース整理・変換 |
| `analysis/` | 分析ツール |
| `setup/` | セットアップツール |
| `testing/` | テストスクリプト |
| `shell/` | シェルスクリプト |

### 📝 prompts/ - プロンプト
AI分析用プロンプト

| ファイル | 説明 |
|---------|------|
| `Phase1_EvidenceAnalysis.txt` | 旧版プロンプト |
| `Phase1_EvidenceAnalysis_v2_Practical.txt` | ⭐ 実用版（v3.1） |

### 📊 data/ - データ
実行時に生成されるデータ

| ファイル | 説明 |
|---------|------|
| `database_uploaded.json` | メインデータベース |
| `analysis_method_report.json` | 分析レポート |

---

## 🚀 使用方法

### 初めての方
1. **README.md** を読む
2. **QUICKSTART.md** でセットアップ
3. **docs/user-guides/USAGE_GUIDE.md** で使い方を学ぶ

### ドキュメントを探す
すべてのドキュメントは **docs/** 配下に整理されています
- **docs/README.md** でドキュメント索引を確認

### スクリプトを実行する
- メイン実行: `python run_phase1_multi.py`
- バッチ処理: `python batch_process.py`
- ユーティリティ: `python scripts/maintenance/xxx.py`

---

## 📖 重要なドキュメント

### すぐ読むべき
1. **README.md** - システム概要
2. **QUICKSTART.md** - 5分でセットアップ
3. **docs/phase1-improvements/IMPLEMENTATION_SUMMARY_V3.1.md** - 最新改善内容

### トラブル時
1. **docs/maintenance/CLEANUP_INSTRUCTIONS.md** - 問題解決
2. **docs/setup-guides/UPDATE_GUIDE.md** - アップデート手順

### 開発者向け
1. **docs/architecture/SYSTEM_STRUCTURE_SUMMARY.md** - システム全体像
2. **docs/architecture/database_schema_v3.1_practical.json** - 最新スキーマ
3. **docs/phase1-improvements/** - 改善内容詳細

---

## 🔍 ファイルの探し方

### 「XXXの使い方を知りたい」
→ `docs/user-guides/` または `docs/feature-guides/`

### 「システムをセットアップしたい」
→ `docs/setup-guides/`

### 「エラーが出た」
→ `docs/maintenance/`

### 「システムの中身を知りたい」
→ `docs/architecture/`

### 「最新の改善内容を知りたい」
→ `docs/phase1-improvements/` または `docs/changelogs/`

---

## ⚡ 簡単起動

### macOS
```bash
# ダブルクリック
start.command

# または
./scripts/shell/start.command
```

### Windows
```bash
# ダブルクリック
start.bat

# または
scripts\shell\start.bat
```

### Linux
```bash
# 実行
./scripts/shell/start.sh

# または
bash scripts/shell/start.sh
```

---

## 🔧 開発者向け

### インポート方法
ソースコードは `src/` 配下に移動しました

**変更前:**
```python
from ai_analyzer_complete import AIAnalyzerComplete
```

**変更後:**
```python
from src.ai_analyzer_complete import AIAnalyzerComplete
```

### スクリプトの配置
新しいスクリプトは適切なディレクトリに配置

- メンテナンス系 → `scripts/maintenance/`
- 分析系 → `scripts/analysis/`
- テスト系 → `scripts/testing/`

---

## 📦 整理による効果

### Before (整理前)
```
create-junbisyomen/
├── 40+ のマークダウンファイルが散在
├── Pythonスクリプトが混在
├── ドキュメントの分類が不明瞭
└── 視認性が低い
```

### After (整理後)
```
create-junbisyomen/
├── ルート: 必要最小限のファイルのみ
├── docs/: 用途別に整理されたドキュメント
├── src/: ソースコードをパッケージ化
├── scripts/: 機能別に分類されたスクリプト
└── 視認性・保守性が大幅に向上
```

---

## ✅ 整理のメリット

1. **視認性向上**: ルートディレクトリがスッキリ
2. **検索性向上**: ドキュメントが用途別に分類
3. **保守性向上**: コードとドキュメントが分離
4. **拡張性向上**: 新しいファイルの配置先が明確
5. **Git管理向上**: .gitignoreが効率的に機能

---

**整理日**: 2025-11-05  
**システムバージョン**: 3.1.0

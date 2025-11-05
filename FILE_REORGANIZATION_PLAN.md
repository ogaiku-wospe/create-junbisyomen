# ファイル構造整理計画

## 📊 現状の問題点

1. **ルートディレクトリの混雑**: 40+のマークダウンファイルがルートに散在
2. **ドキュメントの分類不足**: 用途別に整理されていない
3. **スクリプトとドキュメントの混在**: 視認性が低い
4. **古いファイルと新しいファイルの混在**: バージョン管理が不明瞭

---

## 🎯 整理方針

### 原則
1. **必要なファイルは削除しない**
2. **実行可能なスクリプトは維持**
3. **ドキュメントを用途別に分類**
4. **プロジェクト構造の可読性を向上**

### 新しいディレクトリ構造

```
create-junbisyomen-3/
├── README.md                          # メインREADME（残す）
├── QUICKSTART.md                      # クイックスタートガイド（残す）
├── requirements.txt                   # Python依存関係（残す）
├── global_config.py                   # グローバル設定（残す）
│
├── docs/                              # 📚 すべてのドキュメント
│   ├── README.md                      # docsディレクトリの説明
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
│   ├── architecture/                  # アーキテクチャ・設計
│   │   ├── SYSTEM_STRUCTURE_SUMMARY.md
│   │   ├── DATABASE_JSON_FIELDS_COMPLETE_LIST.md
│   │   ├── DATABASE_JSON_FOR_AI_USAGE.md
│   │   ├── database_schema_v3.json
│   │   ├── database_schema_v3.1_practical.json
│   │   ├── GAS_FEASIBILITY_ANALYSIS.md
│   │   ├── GAS_VS_PYTHON_RECOMMENDATION.md
│   │   └── FILE_ORGANIZATION_PLAN.md
│   │
│   ├── phase1-improvements/           # Phase 1改善関連（v3.1）
│   │   ├── IMPLEMENTATION_SUMMARY_V3.1.md
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
│   └── templates/                     # テンプレート・サンプル
│       ├── .env.example
│       └── credentials.json.example
│
├── src/                               # 🐍 メインのPythonコード
│   ├── __init__.py
│   ├── ai_analyzer_complete.py
│   ├── case_manager.py
│   ├── evidence_organizer.py
│   ├── evidence_editor_ai.py
│   ├── file_processor.py
│   ├── gdrive_database_manager.py
│   ├── metadata_extractor.py
│   ├── timeline_builder.py
│   └── utils/
│       ├── __init__.py
│       └── database_cleanup.py
│
├── scripts/                           # 🔧 ユーティリティスクリプト
│   ├── maintenance/
│   │   ├── cleanup_local_database.py
│   │   ├── convert_evidence_ids.py
│   │   ├── migrate_to_hierarchical_folders.py
│   │   └── system_integrity_check.py
│   │
│   ├── analysis/
│   │   ├── add_analysis_method_info.py
│   │   ├── check_analysis_methods.py
│   │   └── improve_usability.py
│   │
│   ├── setup/
│   │   ├── setup_new_case.py
│   │   └── check_permissions.py
│   │
│   ├── testing/
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
├── prompts/                           # 📝 AIプロンプト
│   ├── Phase1_EvidenceAnalysis.txt
│   └── Phase1_EvidenceAnalysis_v2_Practical.txt
│
├── data/                              # 📊 データファイル（新規作成）
│   ├── database_uploaded.json
│   └── analysis_method_report.json
│
├── run_phase1.py                      # ⚡ メイン実行スクリプト（残す）
├── run_phase1_multi.py                # ⚡ マルチケース実行（残す）
└── batch_process.py                   # ⚡ バッチ処理（残す）
```

---

## 📋 移行手順

### ステップ1: 新しいディレクトリを作成

```bash
mkdir -p docs/{user-guides,setup-guides,feature-guides,maintenance,architecture,phase1-improvements,changelogs,templates}
mkdir -p src/utils
mkdir -p scripts/{maintenance,analysis,setup,testing,shell}
mkdir -p data
```

### ステップ2: ドキュメントファイルを移動

#### User Guides
```bash
mv USAGE_GUIDE.md docs/user-guides/
mv GOOGLE_DRIVE_GUIDE.md docs/user-guides/
mv TIMELINE_STORY_GUIDE.md docs/user-guides/
mv README_MULTI_CASE.md docs/user-guides/
```

#### Setup Guides
```bash
mv MIGRATION_QUICK_START.md docs/setup-guides/
mv MIGRATION_GUIDE_v3.2.md docs/setup-guides/
mv MIGRATION_V3.2.md docs/setup-guides/
mv UPDATE_GUIDE.md docs/setup-guides/
mv UPDATE_LOCAL_FROM_GITHUB.md docs/setup-guides/
mv LOCAL_UPDATE_INSTRUCTIONS.txt docs/setup-guides/
mv QUICK_UPDATE_GUIDE.txt docs/setup-guides/
```

#### Feature Guides
```bash
mv EVIDENCE_TYPE_FEATURE.md docs/feature-guides/
mv EVIDENCE_TYPE_SEPARATION_GUIDE.md docs/feature-guides/
mv HIERARCHICAL_FOLDERS.md docs/feature-guides/
mv EVIDENCE_ID_CONVERSION_GUIDE.md docs/feature-guides/
mv EVIDENCE_STATUS_FIX_GUIDE.md docs/feature-guides/
mv DISPLAY_FIX_GUIDE.md docs/feature-guides/
```

#### Maintenance
```bash
mv CLEANUP_INSTRUCTIONS.md docs/maintenance/
mv QUICK_CLEANUP_GUIDE.md docs/maintenance/
mv FIXES_v3.7.2.md docs/maintenance/
```

#### Architecture
```bash
mv SYSTEM_STRUCTURE_SUMMARY.md docs/architecture/
mv DATABASE_JSON_FIELDS_COMPLETE_LIST.md docs/architecture/
mv DATABASE_JSON_FOR_AI_USAGE.md docs/architecture/
mv database_schema_v3.json docs/architecture/
mv database_schema_v3.1_practical.json docs/architecture/
mv GAS_FEASIBILITY_ANALYSIS.md docs/architecture/
mv GAS_VS_PYTHON_RECOMMENDATION.md docs/architecture/
mv FILE_ORGANIZATION_PLAN.md docs/architecture/
```

#### Phase 1 Improvements
```bash
mv IMPLEMENTATION_SUMMARY_V3.1.md docs/phase1-improvements/
mv PHASE1_PRACTICAL_IMPROVEMENT_PLAN.md docs/phase1-improvements/
mv PRACTICAL_USAGE_GUIDE_V3.1.md docs/phase1-improvements/
mv USABILITY_IMPROVEMENT_PLAN.md docs/phase1-improvements/
```

#### Changelogs
```bash
mv CHANGELOG_v3.6.1.md docs/changelogs/
mv CHANGELOG_v3.7.0.md docs/changelogs/
mv CHANGELOG_v3.7.1.md docs/changelogs/
mv IMPROVEMENTS.md docs/changelogs/
mv IMPLEMENTATION_SUMMARY.md docs/changelogs/
mv IMPLEMENTATION_SUMMARY_TIMELINE.md docs/changelogs/
mv COMPLETION_SUMMARY.md docs/changelogs/
```

#### Templates
```bash
mv .env.example docs/templates/
mv credentials.json.example docs/templates/
```

### ステップ3: Pythonスクリプトを移動

#### Main Source Code
```bash
mv ai_analyzer_complete.py src/
mv case_manager.py src/
mv evidence_organizer.py src/
mv evidence_editor_ai.py src/
mv file_processor.py src/
mv gdrive_database_manager.py src/
mv metadata_extractor.py src/
mv timeline_builder.py src/
mv utils/database_cleanup.py src/utils/
```

#### Maintenance Scripts
```bash
mv cleanup_local_database.py scripts/maintenance/
mv convert_evidence_ids.py scripts/maintenance/
mv migrate_to_hierarchical_folders.py scripts/maintenance/
mv system_integrity_check.py scripts/maintenance/
```

#### Analysis Scripts
```bash
mv add_analysis_method_info.py scripts/analysis/
mv check_analysis_methods.py scripts/analysis/
mv improve_usability.py scripts/analysis/
```

#### Setup Scripts
```bash
mv setup_new_case.py scripts/setup/
mv check_permissions.py scripts/setup/
```

#### Testing Scripts
```bash
mv test_gdrive_database.py scripts/testing/
mv test_timeline_builder.py scripts/testing/
mv debug_folders.py scripts/testing/
mv find_shared_drives.py scripts/testing/
```

#### Shell Scripts
```bash
mv setup.sh scripts/shell/
mv setup.bat scripts/shell/
mv start.sh scripts/shell/
mv start.bat scripts/shell/
mv start.command scripts/shell/
mv cleanup_project.sh scripts/shell/
mv cleanup_project.bat scripts/shell/
mv convert_ids.sh scripts/shell/
mv update_local.sh scripts/shell/
mv update_local_repo.sh scripts/shell/
mv update_local_repo.bat scripts/shell/
mv update_local_repo.command scripts/shell/
```

### ステップ4: データファイルを移動

```bash
mv database_uploaded.json data/
mv analysis_method_report.json data/
```

### ステップ5: __init__.py を作成

```bash
touch src/__init__.py
touch src/utils/__init__.py
```

---

## 📝 更新が必要なファイル

### 1. run_phase1.py, run_phase1_multi.py, batch_process.py

**変更前:**
```python
from ai_analyzer_complete import AIAnalyzerComplete
from case_manager import CaseManager
```

**変更後:**
```python
from src.ai_analyzer_complete import AIAnalyzerComplete
from src.case_manager import CaseManager
```

### 2. global_config.py

**変更前:**
```python
LOCAL_PROMPT_PATH = "prompts/Phase1_EvidenceAnalysis.txt"
```

**変更後:**
```python
# プロンプトパスは変更なし（promptsディレクトリは維持）
LOCAL_PROMPT_PATH = "prompts/Phase1_EvidenceAnalysis.txt"
```

### 3. README.md

ドキュメントへのリンクを更新

**変更後:**
```markdown
## 📚 ドキュメント

- [クイックスタート](QUICKSTART.md)
- [使用ガイド](docs/user-guides/USAGE_GUIDE.md)
- [セットアップガイド](docs/setup-guides/)
- [機能ガイド](docs/feature-guides/)
- [Phase 1改善版](docs/phase1-improvements/IMPLEMENTATION_SUMMARY_V3.1.md)
```

---

## ✅ 実行後の確認

### 確認項目
- [ ] すべてのドキュメントがdocsディレクトリに移動
- [ ] すべてのPythonコードがsrcディレクトリに移動
- [ ] すべてのスクリプトがscriptsディレクトリに移動
- [ ] run_phase1.py, run_phase1_multi.py, batch_process.pyのimportを更新
- [ ] README.mdのリンクを更新
- [ ] Gitコミット前に動作確認

---

## 🚀 実行

この整理を実行するには、次のセクションの実装を参照してください。

# 📚 Phase 1 証拠分析システム - ドキュメント

このディレクトリには、Phase 1システムの全てのドキュメントが整理されています。

---

## 📂 ディレクトリ構造

### 👥 [user-guides/](user-guides/) - ユーザーガイド
日常的な使用方法とベストプラクティス

- **USAGE_GUIDE.md** - 基本的な使用方法
- **GOOGLE_DRIVE_GUIDE.md** - Google Drive連携ガイド
- **TIMELINE_STORY_GUIDE.md** - タイムライン・ストーリー機能
- **README_MULTI_CASE.md** - 複数事件管理

### ⚙️ [setup-guides/](setup-guides/) - セットアップガイド
インストール、移行、アップデート手順

- **MIGRATION_QUICK_START.md** - クイックスタート
- **MIGRATION_GUIDE_v3.2.md** - v3.2移行ガイド
- **UPDATE_GUIDE.md** - アップデートガイド
- **UPDATE_LOCAL_FROM_GITHUB.md** - GitHubから更新

### 🎯 [feature-guides/](feature-guides/) - 機能ガイド
個別機能の詳細説明

- **EVIDENCE_TYPE_FEATURE.md** - 証拠タイプ機能
- **EVIDENCE_TYPE_SEPARATION_GUIDE.md** - 証拠分類ガイド
- **HIERARCHICAL_FOLDERS.md** - 階層的フォルダ管理
- **EVIDENCE_ID_CONVERSION_GUIDE.md** - 証拠ID変換
- **EVIDENCE_STATUS_FIX_GUIDE.md** - ステータス修正
- **DISPLAY_FIX_GUIDE.md** - 表示修正

### 🔧 [maintenance/](maintenance/) - メンテナンスガイド
システムのメンテナンスとトラブルシューティング

- **CLEANUP_INSTRUCTIONS.md** - クリーンアップ手順
- **QUICK_CLEANUP_GUIDE.md** - クイッククリーンアップ
- **FIXES_v3.7.2.md** - v3.7.2の修正内容

### 🏗️ [architecture/](architecture/) - アーキテクチャ・設計
システム設計と技術仕様

- **SYSTEM_STRUCTURE_SUMMARY.md** - システム構造概要
- **DATABASE_JSON_FIELDS_COMPLETE_LIST.md** - database.json全フィールド
- **DATABASE_JSON_FOR_AI_USAGE.md** - AI使用ガイド
- **database_schema_v3.json** - スキーマ v3.0
- **database_schema_v3.1_practical.json** - スキーマ v3.1（実用版）
- **GAS_FEASIBILITY_ANALYSIS.md** - GAS実装評価
- **GAS_VS_PYTHON_RECOMMENDATION.md** - GAS vs Python比較
- **FILE_ORGANIZATION_PLAN.md** - ファイル整理計画

### 🚀 [phase1-improvements/](phase1-improvements/) - Phase 1改善版（v3.1）
実用性向上のための改善

- **IMPLEMENTATION_SUMMARY_V3.1.md** - ⭐ 実装サマリー（まず読む）
- **PRACTICAL_USAGE_GUIDE_V3.1.md** - 実用的な使用ガイド
- **PHASE1_PRACTICAL_IMPROVEMENT_PLAN.md** - 改善計画詳細
- **USABILITY_IMPROVEMENT_PLAN.md** - ユーザビリティ改善計画

### 📝 [changelogs/](changelogs/) - 変更履歴
バージョンごとの変更内容

- **CHANGELOG_v3.6.1.md** - v3.6.1変更履歴
- **CHANGELOG_v3.7.0.md** - v3.7.0変更履歴
- **CHANGELOG_v3.7.1.md** - v3.7.1変更履歴
- **IMPROVEMENTS.md** - 改善履歴
- **IMPLEMENTATION_SUMMARY.md** - 実装サマリー
- **IMPLEMENTATION_SUMMARY_TIMELINE.md** - 実装タイムライン
- **COMPLETION_SUMMARY.md** - 完成サマリー

### 📄 [templates/](templates/) - テンプレート
設定ファイルのサンプル

- **.env.example** - 環境変数テンプレート
- **credentials.json.example** - Google認証情報テンプレート

---

## 🚀 クイックスタート

### 初めての方
1. **[../QUICKSTART.md](../QUICKSTART.md)** - システム全体のクイックスタート
2. **[setup-guides/MIGRATION_QUICK_START.md](setup-guides/MIGRATION_QUICK_START.md)** - セットアップ手順

### 既存ユーザー
1. **[setup-guides/UPDATE_GUIDE.md](setup-guides/UPDATE_GUIDE.md)** - アップデート手順
2. **[setup-guides/UPDATE_LOCAL_FROM_GITHUB.md](setup-guides/UPDATE_LOCAL_FROM_GITHUB.md)** - GitHub更新

### v3.1実用版について
1. **[phase1-improvements/IMPLEMENTATION_SUMMARY_V3.1.md](phase1-improvements/IMPLEMENTATION_SUMMARY_V3.1.md)** - ⭐ 実装サマリー
2. **[phase1-improvements/PRACTICAL_USAGE_GUIDE_V3.1.md](phase1-improvements/PRACTICAL_USAGE_GUIDE_V3.1.md)** - 使用ガイド

---

## 📖 おすすめの読み順

### 新規ユーザー
1. **QUICKSTART.md** (ルート) - 最初に読む
2. **user-guides/USAGE_GUIDE.md** - 基本的な使い方
3. **user-guides/GOOGLE_DRIVE_GUIDE.md** - Google Drive連携
4. **phase1-improvements/IMPLEMENTATION_SUMMARY_V3.1.md** - 最新機能

### システム管理者
1. **architecture/SYSTEM_STRUCTURE_SUMMARY.md** - システム全体像
2. **architecture/DATABASE_JSON_FIELDS_COMPLETE_LIST.md** - データ構造
3. **maintenance/CLEANUP_INSTRUCTIONS.md** - メンテナンス

### 開発者
1. **architecture/SYSTEM_STRUCTURE_SUMMARY.md** - アーキテクチャ
2. **architecture/database_schema_v3.1_practical.json** - 最新スキーマ
3. **architecture/DATABASE_JSON_FOR_AI_USAGE.md** - AI統合
4. **phase1-improvements/** - 最新改善内容

---

## 🔍 目的別ドキュメント検索

### 「システムを使いたい」
→ **user-guides/** を参照

### 「システムをセットアップしたい」
→ **setup-guides/** を参照

### 「特定の機能を使いたい」
→ **feature-guides/** を参照

### 「問題を解決したい」
→ **maintenance/** を参照

### 「システムの内部を知りたい」
→ **architecture/** を参照

### 「最新の改善内容を知りたい」
→ **phase1-improvements/** または **changelogs/** を参照

---

## 💡 ヘルプが必要な場合

### よくある質問
- 「証拠を追加したい」 → user-guides/USAGE_GUIDE.md
- 「Google Driveと連携したい」 → user-guides/GOOGLE_DRIVE_GUIDE.md
- 「タイムラインを作りたい」 → user-guides/TIMELINE_STORY_GUIDE.md
- 「複数の事件を管理したい」 → user-guides/README_MULTI_CASE.md
- 「システムを更新したい」 → setup-guides/UPDATE_GUIDE.md
- 「エラーが出た」 → maintenance/CLEANUP_INSTRUCTIONS.md

### 最新情報
- **Phase 1 v3.1実用版** - phase1-improvements/IMPLEMENTATION_SUMMARY_V3.1.md
- **最新の変更履歴** - changelogs/

---

## 📬 フィードバック

ドキュメントの改善提案や質問がある場合は、GitHubのIssueでお知らせください。

---

**最終更新**: 2025-11-05  
**システムバージョン**: 3.1.0 (実用版)

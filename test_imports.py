#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
インポートテストスクリプト

このスクリプトは、すべての必要なモジュールが正しくインポートできるかをテストします。
エラーが発生した場合は、IMPORT_FIX.md を参照してください。
"""

import os
import sys

# プロジェクトルートをPythonパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print("="*70)
print("  インポートテスト")
print("="*70)
print(f"\nプロジェクトルート: {project_root}")
print(f"Pythonバージョン: {sys.version.split()[0]}")
print()

# テスト対象のモジュール
test_modules = [
    ("global_config", "設定ファイル"),
    ("src.case_manager", "事件管理"),
    ("src.evidence_organizer", "証拠整理"),
    ("src.metadata_extractor", "メタデータ抽出"),
    ("src.file_processor", "ファイル処理"),
    ("src.ai_analyzer_complete", "AI分析"),
    ("src.evidence_editor_ai", "証拠編集"),
    ("src.timeline_builder", "タイムライン構築"),
]

errors = []
success_count = 0

print("モジュールのインポートをテスト中...")
print("-" * 70)

for module_name, description in test_modules:
    try:
        __import__(module_name)
        print(f"✅ {module_name:30s} のインポート成功 ({description})")
        success_count += 1
    except ImportError as e:
        error_msg = f"❌ {module_name:30s} のインポート失敗: {e}"
        print(error_msg)
        errors.append((module_name, str(e)))
    except Exception as e:
        error_msg = f"⚠️  {module_name:30s} で予期しないエラー: {e}"
        print(error_msg)
        errors.append((module_name, str(e)))

print("-" * 70)
print(f"\n結果: {success_count}/{len(test_modules)} 成功\n")

if errors:
    print("❌ エラーが発生しました:\n")
    for module_name, error in errors:
        print(f"  • {module_name}")
        print(f"    {error}\n")
    
    print("🔧 トラブルシューティング:\n")
    print("1. 依存パッケージをインストール:")
    print("   pip install -r requirements.txt\n")
    print("2. 仮想環境を再構築:")
    print("   rm -rf venv")
    print("   python3 -m venv venv")
    print("   source venv/bin/activate")
    print("   pip install -r requirements.txt\n")
    print("3. 詳細は IMPORT_FIX.md を参照してください\n")
    
    sys.exit(1)
else:
    print("🎉 すべてのモジュールのインポートに成功しました！")
    print()
    print("次のステップ:")
    print("  • マルチ事件対応版を実行: python3 run_phase1_multi.py")
    print("  • 単一事件版を実行: python3 run_phase1.py")
    print("  • 一括処理を実行: python3 batch_process.py --help")
    print()
    sys.exit(0)

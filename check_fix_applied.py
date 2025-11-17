#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正が適用されているか確認するスクリプト
"""

import os
import sys

# プロジェクトルートをPythonパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print("="*70)
print("  修正適用チェック")
print("="*70)

# ファイルの存在確認
ai_analyzer_path = os.path.join(project_root, 'src', 'ai_analyzer_complete.py')
print(f"\n1. ファイル存在確認:")
print(f"   {ai_analyzer_path}")
if os.path.exists(ai_analyzer_path):
    print(f"   ✅ 存在します")
else:
    print(f"   ❌ 存在しません")
    sys.exit(1)

# ファイル内容をチェック
print(f"\n2. 修正コードの確認:")
with open(ai_analyzer_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 修正1: Claude優先使用のコードが含まれているか
fix1_marker = "法律文書検出: Claude Vision APIを優先使用します"
if fix1_marker in content:
    print(f"   ✅ 修正1: Claude優先使用コードが含まれています")
    # 行番号を探す
    for i, line in enumerate(content.split('\n'), 1):
        if fix1_marker in line:
            print(f"      行番号: {i}")
            break
else:
    print(f"   ❌ 修正1: Claude優先使用コードが見つかりません")
    print(f"      git pull を実行してください")

# 修正2: JSON修復の改善コードが含まれているか
fix2_marker = "JSON修復戦略1: 不完全な文字列を検出"
if fix2_marker in content:
    print(f"   ✅ 修正2: JSON修復改善コードが含まれています")
    # 行番号を探す
    for i, line in enumerate(content.split('\n'), 1):
        if fix2_marker in line:
            print(f"      行番号: {i}")
            break
else:
    print(f"   ❌ 修正2: JSON修復改善コードが見つかりません")
    print(f"      git pull を実行してください")

# Pythonキャッシュの確認
print(f"\n3. Pythonキャッシュの確認:")
pycache_dir = os.path.join(project_root, 'src', '__pycache__')
if os.path.exists(pycache_dir):
    pyc_files = [f for f in os.listdir(pycache_dir) if f.endswith('.pyc')]
    if pyc_files:
        print(f"   ⚠️  __pycache__ に {len(pyc_files)} 個の .pyc ファイルがあります")
        print(f"      古いキャッシュの可能性があります")
        print(f"      推奨: find src/ -type d -name '__pycache__' -exec rm -rf {{}} + 2>/dev/null")
    else:
        print(f"   ✅ __pycache__ はクリーンです")
else:
    print(f"   ✅ __pycache__ ディレクトリがありません")

# モジュールのインポートテスト
print(f"\n4. モジュールインポートテスト:")
try:
    from src.ai_analyzer_complete import AIAnalyzerComplete
    print(f"   ✅ AIAnalyzerComplete のインポート成功")
    
    # インスタンス作成
    analyzer = AIAnalyzerComplete()
    print(f"   ✅ インスタンス作成成功")
    
    # _analyze_with_vision メソッドの存在確認
    if hasattr(analyzer, '_analyze_with_vision'):
        print(f"   ✅ _analyze_with_vision メソッドが存在します")
        
        # メソッドのソースコードをチェック
        import inspect
        source = inspect.getsource(analyzer._analyze_with_vision)
        if fix1_marker in source:
            print(f"   ✅ メソッド内に修正コードが含まれています")
        else:
            print(f"   ❌ メソッド内に修正コードが含まれていません")
            print(f"      古いコードがキャッシュされている可能性があります")
            print(f"      Python を再起動してください")
    else:
        print(f"   ❌ _analyze_with_vision メソッドが見つかりません")
        
except ImportError as e:
    print(f"   ❌ インポートエラー: {e}")
except Exception as e:
    print(f"   ❌ エラー: {e}")

# Gitコミット確認
print(f"\n5. Gitコミット確認:")
try:
    import subprocess
    result = subprocess.run(
        ['git', 'log', '--oneline', '-3'],
        cwd=project_root,
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        commits = result.stdout.strip().split('\n')
        print(f"   最新3コミット:")
        for commit in commits:
            print(f"   - {commit}")
            if 'def1c25' in commit:
                print(f"     ✅ 修正コミットが含まれています")
    else:
        print(f"   ⚠️  git コマンド実行失敗")
except Exception as e:
    print(f"   ⚠️  git 確認エラー: {e}")

# まとめ
print(f"\n" + "="*70)
print(f"  チェック完了")
print(f"="*70)
print(f"\n【推奨アクション】")
print(f"  1. 修正コードが見つからない場合:")
print(f"     git pull origin genspark_ai_developer")
print(f"")
print(f"  2. Pythonキャッシュがある場合:")
print(f"     find src/ -type d -name '__pycache__' -exec rm -rf {{}} + 2>/dev/null")
print(f"     find src/ -type f -name '*.pyc' -delete")
print(f"")
print(f"  3. 上記を実行後、再度このスクリプトを実行して確認:")
print(f"     python3 check_fix_applied.py")
print(f"")
print(f"  4. すべて✅になったら、証拠分析を実行:")
print(f"     python3 run_phase1_multi.py")
print(f"")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ユーザビリティ改善スクリプト
- 絵文字の削減（必要最小限に）
- エラーメッセージの明確化
- 入力検証の強化
"""

import re

def improve_usability(filepath):
    """ユーザビリティ改善"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 絵文字の削減（メニュー以外）
    replacements = [
        # エラーメッセージの絵文字削除
        (r'print\("❌', 'print("エラー:'),
        (r'print\(f"❌', 'print(f"エラー:'),
        (r'logger\.error\("❌', 'logger.error("'),
        (r'logger\.error\(f"❌', 'logger.error(f"'),
        
        # 成功メッセージの絵文字削除（logger）
        (r'logger\.info\("✅', 'logger.info("'),
        (r'logger\.info\(f"✅', 'logger.info(f"'),
        
        # 警告メッセージの絵文字削除
        (r'print\("⚠️', 'print("警告:'),
        (r'print\(f"⚠️', 'print(f"警告:'),
        (r'logger\.warning\("⚠️', 'logger.warning("'),
        (r'logger\.warning\(f"⚠️', 'logger.warning(f"'),
        
        # その他の絵文字（データ表示系）
        (r'print\("📋', 'print("'),
        (r'print\(f"📋', 'print(f"'),
        (r'print\("📊', 'print("'),
        (r'print\(f"📊', 'print(f"'),
        (r'print\("📁', 'print("'),
        (r'print\(f"📁', 'print(f"'),
        (r'print\("🔍', 'print("'),
        (r'print\(f"🔍', 'print(f"'),
        (r'print\("🤖', 'print("'),
        (r'print\(f"🤖', 'print(f"'),
        (r'print\("💾', 'print("'),
        (r'print\(f"💾', 'print(f"'),
        (r'print\("📈', 'print("'),
        (r'print\(f"📈', 'print(f"'),
        (r'print\("🔧', 'print("'),
        (r'print\(f"🔧', 'print(f"'),
        (r'print\("📝', 'print("'),
        (r'print\(f"📝', 'print(f"'),
        (r'print\("👋', 'print("'),
        (r'print\(f"👋', 'print(f"'),
        (r'print\("⏳', 'print("'),
        (r'print\(f"⏳', 'print(f"'),
        (r'print\("❓', 'print("'),
        (r'print\(f"❓', 'print(f"'),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # バックアップ
    with open(filepath + '.backup', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 書き込み
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("ユーザビリティ改善完了")
    print(f"  バックアップ: {filepath}.backup")

if __name__ == '__main__':
    import os
    import sys
    
    # コマンドライン引数でファイルパスを指定可能
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        # スクリプトと同じディレクトリのrun_phase1_multi.pyを対象
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(script_dir, 'run_phase1_multi.py')
    
    if not os.path.exists(filepath):
        print(f"エラー: ファイルが見つかりません: {filepath}")
        print(f"\n使用方法: python3 {sys.argv[0]} [ファイルパス]")
        sys.exit(1)
    
    print(f"対象ファイル: {filepath}")
    improve_usability(filepath)

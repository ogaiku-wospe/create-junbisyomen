#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
証拠番号の命名改善スクリプト

【機能】
- database.jsonの証拠番号をわかりやすい名前に変更
- ファイル内容に基づいた自動命名
- 手動での命名も可能

【使用方法】
    python3 scripts/analysis/improve_evidence_names.py <database.json>
"""

import os
import sys
import json
import re
from datetime import datetime
from typing import Dict, List, Optional

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


def analyze_evidence_content(evidence: Dict) -> str:
    """証拠の内容から推奨名を生成
    
    Args:
        evidence: 証拠データ
        
    Returns:
        推奨される証拠名
    """
    evidence_id = evidence.get('evidence_id', '')
    filename = evidence.get('original_filename', '')
    
    # analyzed_contentから内容を取得
    content_summary = ""
    if 'analyzed_content' in evidence:
        content = evidence['analyzed_content']
        if isinstance(content, dict):
            content_summary = content.get('content_summary', '')
    
    # キーワードベースの推奨名
    keywords_map = {
        '配達証明': '配達証明書',
        '内容証明': '内容証明郵便',
        '訴状': '訴状',
        '準備書面': '準備書面',
        '答弁書': '答弁書',
        '証拠説明書': '証拠説明書',
        '甲第': '甲号証',
        '乙第': '乙号証',
        '診断書': '診断書',
        '契約書': '契約書',
        '合意書': '合意書',
        '覚書': '覚書',
        '領収書': '領収書',
        '請求書': '請求書',
        '見積書': '見積書',
        'メール': 'メール',
        'LINE': 'LINE履歴',
        'チャット': 'チャット履歴',
        '通話記録': '通話記録',
        '録音': '録音データ',
        '写真': '写真',
        'スクリーンショット': 'スクリーンショット'
    }
    
    # ファイル名からキーワード検索
    for keyword, name in keywords_map.items():
        if keyword in filename or keyword in content_summary:
            return name
    
    # 拡張子ベースの推奨名
    ext = os.path.splitext(filename)[1].lower()
    ext_map = {
        '.pdf': 'PDF文書',
        '.docx': 'Word文書',
        '.doc': 'Word文書',
        '.xlsx': 'Excel文書',
        '.png': '画像',
        '.jpg': '画像',
        '.jpeg': '画像'
    }
    
    return ext_map.get(ext, '証拠')


def display_evidence_list(evidence_list: List[Dict]):
    """証拠一覧を表示
    
    Args:
        evidence_list: 証拠リスト
    """
    print("\n" + "=" * 80)
    print("証拠一覧")
    print("=" * 80)
    
    for i, ev in enumerate(evidence_list, 1):
        evidence_id = ev.get('evidence_id', 'N/A')
        evidence_number = ev.get('evidence_number', 'N/A')
        filename = ev.get('original_filename', 'N/A')
        
        # 推奨名を生成
        suggested_name = analyze_evidence_content(ev)
        
        print(f"\n{i}. {evidence_id}")
        print(f"   現在の証拠番号: {evidence_number}")
        print(f"   ファイル名: {filename}")
        print(f"   💡 推奨名: {suggested_name}")


def improve_evidence_names_interactive(database_path: str):
    """対話形式で証拠番号を改善
    
    Args:
        database_path: database.jsonのパス
    """
    # データベースを読み込み
    with open(database_path, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    evidence_list = db.get('evidence', [])
    
    if not evidence_list:
        print("❌ 証拠が見つかりません")
        return
    
    print("\n" + "=" * 80)
    print("証拠番号の命名改善")
    print("=" * 80)
    print(f"データベース: {database_path}")
    print(f"証拠数: {len(evidence_list)}件")
    
    # 証拠一覧を表示
    display_evidence_list(evidence_list)
    
    print("\n" + "=" * 80)
    print("改善方法を選択してください:")
    print("  1. 自動命名（推奨名を使用）")
    print("  2. 手動命名（1件ずつ確認）")
    print("  3. キャンセル")
    
    choice = input("\n> ").strip()
    
    if choice == '1':
        # 自動命名
        print("\n自動命名を実行中...")
        for i, ev in enumerate(evidence_list, 1):
            evidence_id = ev.get('evidence_id', '')
            if not evidence_id or evidence_id == 'N/A':
                continue
            
            suggested_name = analyze_evidence_content(ev)
            new_evidence_number = f"甲{i:03d}_{suggested_name}"
            
            ev['evidence_number'] = new_evidence_number
            print(f"  {i}. {evidence_id} → {new_evidence_number}")
        
        # 保存確認
        print("\n" + "-" * 80)
        confirm = input("変更を保存しますか？ (y/n): ").strip().lower()
        
        if confirm == 'y':
            # バックアップを作成
            backup_path = database_path + '.backup.' + datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(db, f, ensure_ascii=False, indent=2)
            print(f"✅ バックアップ作成: {backup_path}")
            
            # 保存
            with open(database_path, 'w', encoding='utf-8') as f:
                json.dump(db, f, ensure_ascii=False, indent=2)
            print(f"✅ 保存完了: {database_path}")
        else:
            print("❌ 変更をキャンセルしました")
    
    elif choice == '2':
        # 手動命名
        print("\n手動命名モード")
        print("（Enter: 推奨名を使用、カスタム入力: 独自の名前、skip: スキップ）")
        
        for i, ev in enumerate(evidence_list, 1):
            evidence_id = ev.get('evidence_id', '')
            if not evidence_id or evidence_id == 'N/A':
                continue
            
            current_number = ev.get('evidence_number', 'N/A')
            filename = ev.get('original_filename', 'N/A')
            suggested_name = analyze_evidence_content(ev)
            
            print("\n" + "-" * 80)
            print(f"{i}. {evidence_id}")
            print(f"   現在: {current_number}")
            print(f"   ファイル: {filename}")
            print(f"   推奨: 甲{i:03d}_{suggested_name}")
            
            custom_name = input("   新しい名前（Enter=推奨、skip=スキップ）: ").strip()
            
            if custom_name.lower() == 'skip':
                print("   ⏭️  スキップ")
                continue
            elif custom_name == '':
                new_evidence_number = f"甲{i:03d}_{suggested_name}"
            else:
                new_evidence_number = f"甲{i:03d}_{custom_name}"
            
            ev['evidence_number'] = new_evidence_number
            print(f"   ✅ 変更: {new_evidence_number}")
        
        # 保存確認
        print("\n" + "=" * 80)
        confirm = input("変更を保存しますか？ (y/n): ").strip().lower()
        
        if confirm == 'y':
            # バックアップを作成
            backup_path = database_path + '.backup.' + datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(db, f, ensure_ascii=False, indent=2)
            print(f"✅ バックアップ作成: {backup_path}")
            
            # 保存
            with open(database_path, 'w', encoding='utf-8') as f:
                json.dump(db, f, ensure_ascii=False, indent=2)
            print(f"✅ 保存完了: {database_path}")
        else:
            print("❌ 変更をキャンセルしました")
    
    else:
        print("❌ キャンセルしました")


def main():
    """メイン処理"""
    if len(sys.argv) < 2:
        print("使用方法: python3 improve_evidence_names.py <database.json>")
        sys.exit(1)
    
    database_path = sys.argv[1]
    
    if not os.path.exists(database_path):
        print(f"❌ ファイルが見つかりません: {database_path}")
        sys.exit(1)
    
    improve_evidence_names_interactive(database_path)


if __name__ == '__main__':
    main()

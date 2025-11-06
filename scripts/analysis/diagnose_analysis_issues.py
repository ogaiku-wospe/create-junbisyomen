#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI分析結果の診断スクリプト

【機能】
- 分析結果が異なる原因を特定
- 分析済み/未分析証拠の確認
- 分析エラーの検出

【使用方法】
    python3 scripts/analysis/diagnose_analysis_issues.py <database.json>
"""

import os
import sys
import json
from typing import Dict, List
from datetime import datetime

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


def diagnose_database(database_path: str):
    """データベースの診断
    
    Args:
        database_path: database.jsonのパス
    """
    print("\n" + "=" * 80)
    print("AI分析結果の診断")
    print("=" * 80)
    print(f"データベース: {database_path}\n")
    
    # データベースを読み込み
    with open(database_path, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    evidence_list = db.get('evidence', [])
    total_count = len(evidence_list)
    
    print(f"📊 基本情報")
    print(f"   総証拠数: {total_count}件")
    print(f"   データベースバージョン: {db.get('version', 'N/A')}")
    print(f"   最終更新: {db.get('metadata', {}).get('last_updated', 'N/A')}")
    
    # 分析状況を確認
    analyzed_count = 0
    unanalyzed_count = 0
    error_count = 0
    
    analyzed_list = []
    unanalyzed_list = []
    error_list = []
    
    for ev in evidence_list:
        evidence_id = ev.get('evidence_id', 'N/A')
        
        has_analyzed_content = 'analyzed_content' in ev
        has_ai_analysis = 'ai_analysis' in ev
        has_error = 'analysis_error' in ev or 'error' in ev
        
        if has_error:
            error_count += 1
            error_list.append({
                'evidence_id': evidence_id,
                'error': ev.get('analysis_error', ev.get('error', 'Unknown'))
            })
        elif has_analyzed_content or has_ai_analysis:
            analyzed_count += 1
            analyzed_list.append(evidence_id)
        else:
            unanalyzed_count += 1
            unanalyzed_list.append(evidence_id)
    
    print(f"\n📈 分析状況")
    print(f"   ✅ 分析済み: {analyzed_count}件")
    print(f"   ⏳ 未分析: {unanalyzed_count}件")
    print(f"   ❌ エラー: {error_count}件")
    
    # 未分析証拠の詳細
    if unanalyzed_list:
        print(f"\n⏳ 未分析証拠の一覧:")
        for i, evidence_id in enumerate(unanalyzed_list, 1):
            # 該当する証拠を取得
            ev = next((e for e in evidence_list if e.get('evidence_id') == evidence_id), None)
            if ev:
                filename = ev.get('original_filename', 'N/A')
                print(f"   {i}. {evidence_id} ({filename})")
    
    # エラー証拠の詳細
    if error_list:
        print(f"\n❌ エラー証拠の詳細:")
        for i, err_info in enumerate(error_list, 1):
            print(f"   {i}. {err_info['evidence_id']}")
            print(f"      エラー: {err_info['error']}")
    
    # 分析内容の品質チェック
    print(f"\n🔍 分析内容の品質チェック")
    
    for i, ev in enumerate(evidence_list[:5], 1):  # 最初の5件
        evidence_id = ev.get('evidence_id', 'N/A')
        filename = ev.get('original_filename', 'N/A')
        
        print(f"\n   {i}. {evidence_id} ({filename})")
        print(f"      " + "-" * 70)
        
        # complete_metadataのチェック
        if 'complete_metadata' in ev:
            meta = ev['complete_metadata']
            print(f"      ✅ complete_metadata: 存在")
            print(f"         - basic: {'✅' if 'basic' in meta else '❌'}")
            print(f"         - hashes: {'✅' if 'hashes' in meta else '❌'}")
            print(f"         - exif: {'✅' if 'exif' in meta else '❌'}")
        else:
            print(f"      ❌ complete_metadata: 存在しない")
        
        # analyzed_contentのチェック
        if 'analyzed_content' in ev:
            content = ev['analyzed_content']
            if isinstance(content, dict):
                print(f"      ✅ analyzed_content: 辞書形式 ({len(content)} keys)")
                
                # 主要フィールドの確認
                required_fields = ['content_summary', 'content_type', 'text_content']
                for field in required_fields:
                    if field in content:
                        value = content[field]
                        if isinstance(value, str):
                            preview = value[:50] + '...' if len(value) > 50 else value
                            print(f"         - {field}: {preview}")
                        else:
                            print(f"         - {field}: {type(value).__name__}")
                    else:
                        print(f"         - {field}: ❌ 存在しない")
            else:
                print(f"      ⚠️ analyzed_content: {type(content).__name__}")
        else:
            print(f"      ❌ analyzed_content: 存在しない")
        
        # ai_analysisのチェック
        if 'ai_analysis' in ev:
            ai = ev['ai_analysis']
            print(f"      ✅ ai_analysis: 存在 ({len(ai)} keys)")
        else:
            print(f"      ❌ ai_analysis: 存在しない")
    
    # 診断結果サマリー
    print(f"\n" + "=" * 80)
    print("📋 診断結果サマリー")
    print("=" * 80)
    
    if unanalyzed_count == total_count:
        print("⚠️  すべての証拠が未分析です")
        print("\n【原因の可能性】")
        print("  1. AI分析がまだ実行されていない")
        print("  2. 分析処理がエラーで中断された")
        print("  3. database.jsonが古いバージョンの可能性")
        print("\n【対処方法】")
        print("  1. run_phase1_multi.py のメニューから「2. 証拠分析」を実行")
        print("  2. 証拠番号を指定してAI分析を実行")
    
    elif unanalyzed_count > 0:
        print(f"⚠️  {unanalyzed_count}件の証拠が未分析です")
        print("\n【対処方法】")
        print("  - 未分析証拠に対してAI分析を実行してください")
    
    if error_count > 0:
        print(f"\n❌ {error_count}件の証拠でエラーが発生しています")
        print("\n【対処方法】")
        print("  1. エラーメッセージを確認")
        print("  2. ファイルが破損していないか確認")
        print("  3. 再度AI分析を実行")
    
    if analyzed_count == total_count:
        print("✅ すべての証拠が正常に分析されています")


def main():
    """メイン処理"""
    if len(sys.argv) < 2:
        print("使用方法: python3 diagnose_analysis_issues.py <database.json>")
        sys.exit(1)
    
    database_path = sys.argv[1]
    
    if not os.path.exists(database_path):
        print(f"❌ ファイルが見つかりません: {database_path}")
        sys.exit(1)
    
    diagnose_database(database_path)


if __name__ == '__main__':
    main()

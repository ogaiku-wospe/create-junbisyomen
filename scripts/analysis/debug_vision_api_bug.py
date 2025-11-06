#!/usr/bin/env python3
"""
Vision API Content Mismatch Debugger

このスクリプトは、Vision API分析結果がPDFファイル内容と一致しない問題を診断します。
チェック項目:
1. 分析済み vs 未分析の証拠
2. 分析結果にエラーがないか
3. 分析内容の品質評価
"""

import os
import sys
import json
from datetime import datetime

import global_config as gconfig

def main():
    """メイン診断関数"""
    
    print("=" * 80)
    print("Vision API Content Mismatch Debugger")
    print("=" * 80)
    
    # データベースファイルをチェック
    db_files = [
        'database_uploaded.json',
        'database_analyzed.json',
        'database.json'
    ]
    
    print("\n📁 データベースファイルを確認中...")
    selected_db = None
    for db_file in db_files:
        if os.path.exists(db_file):
            size = os.path.getsize(db_file)
            mtime = datetime.fromtimestamp(os.path.getmtime(db_file))
            print(f"  ✅ {db_file} - {size:,} bytes - 更新: {mtime}")
            if selected_db is None:
                selected_db = db_file
        else:
            print(f"  ❌ {db_file} - 見つかりません")
    
    if not selected_db:
        print("\n❌ データベースファイルが見つかりません！")
        return
    
    print(f"\n📖 使用するデータベース: {selected_db}")
    
    # データベース読み込み
    with open(selected_db, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    evidence_list = db.get('evidence', [])
    print(f"  証拠総数: {len(evidence_list)}")
    
    # 証拠を分析
    print("\n" + "=" * 80)
    print("証拠の分析")
    print("=" * 80)
    
    issues_found = []
    
    for ev in evidence_list:
        ev_num = ev.get('evidence_number', 'N/A')
        
        # phase1分析を取得
        phase1 = ev.get('phase1_complete_analysis', {})
        if not phase1:
            continue  # 未分析の証拠はスキップ
        
        file_result = phase1.get('file_processing_result', {})
        ai_result = phase1.get('ai_analysis', {})
        
        # 主要情報を抽出
        file_path = file_result.get('file_path', '')
        file_type = file_result.get('file_type', '')
        
        content = file_result.get('content', {})
        total_text = content.get('total_text', '')
        
        full_content = ai_result.get('full_content', '')
        
        # 問題をチェック
        has_file_result = len(total_text) > 0
        has_ai_result = len(str(full_content)) > 50  # 意味のあるコンテンツ
        
        # コンテンツ不一致検出
        content_mismatch = False
        if has_file_result and has_ai_result:
            # 最初の100文字を比較
            file_preview = total_text[:100].replace('\n', ' ').replace(' ', '')
            
            # full_contentが辞書の場合は文字列に変換
            if isinstance(full_content, dict):
                full_content_str = json.dumps(full_content, ensure_ascii=False)
            else:
                full_content_str = str(full_content)
            
            ai_preview = full_content_str[:100].replace('\n', ' ').replace(' ', '')
            
            # 簡易的な類似性チェック
            common_chars = sum(1 for a, b in zip(file_preview[:50], ai_preview[:50]) if a == b)
            similarity = common_chars / 50 if len(file_preview) >= 50 and len(ai_preview) >= 50 else 0
            
            if similarity < 0.3:  # 30%未満の類似度
                content_mismatch = True
        
        # 問題を記録
        if not has_ai_result or content_mismatch:
            issue = {
                'evidence_number': ev_num,
                'file_type': file_type,
                'file_path': file_path,
                'file_result_length': len(total_text),
                'ai_result_length': len(str(full_content)),
                'has_file_result': has_file_result,
                'has_ai_result': has_ai_result,
                'content_mismatch': content_mismatch,
                'file_preview': total_text[:200] if has_file_result else 'N/A',
                'ai_preview': str(full_content)[:200] if has_ai_result else 'N/A'
            }
            issues_found.append(issue)
    
    # 結果を報告
    if not issues_found:
        print("\n✅ 問題は見つかりませんでした！すべての証拠が正しく分析されています。")
        return
    
    print(f"\n⚠️  {len(issues_found)}件の証拠に問題が見つかりました:\n")
    
    for issue in issues_found:
        print(f"証拠番号: {issue['evidence_number']}")
        print(f"  ファイルタイプ: {issue['file_type']}")
        print(f"  ファイル処理結果: {issue['file_result_length']}文字")
        print(f"  AI分析結果: {issue['ai_result_length']}文字")
        
        if not issue['has_ai_result']:
            print(f"  ❌ 問題: AI分析結果が空またはエラー")
        elif issue['content_mismatch']:
            print(f"  ❌ 問題: ファイル内容とAI分析結果が一致しない")
        
        print(f"\n  📄 ファイル処理結果のプレビュー:")
        print(f"     {issue['file_preview'][:150]}...")
        
        print(f"\n  🤖 AI分析結果のプレビュー:")
        if issue['has_ai_result']:
            print(f"     {issue['ai_preview'][:150]}...")
        else:
            print(f"     （空またはエラー）")
        
        print("\n" + "-" * 80 + "\n")
    
    # 推奨事項
    print("=" * 80)
    print("推奨される対処方法")
    print("=" * 80)
    
    print("""
1. 証拠を再分析する:
   - run_phase1_multi.py のメニューから「2. 証拠分析」を実行
   - 問題のある証拠番号を指定して再分析

2. ログを確認する:
   - 最新のログファイルでVision API呼び出しの詳細を確認
   - PDF内容プレビューとVision API分析結果を比較

3. 一時ファイルをクリアする:
   - Vision API用の一時JPGファイルが古い可能性があります
   - 証拠ディレクトリ内の *_page*.jpg ファイルを削除して再分析
""")

if __name__ == '__main__':
    main()

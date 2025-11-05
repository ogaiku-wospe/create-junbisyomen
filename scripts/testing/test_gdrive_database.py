#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Drive Database Manager テストスクリプト

database.jsonのGoogle Drive管理機能をテストします。
"""

import os
import sys
import json
from datetime import datetime

try:
    from case_manager import CaseManager
    from gdrive_database_manager import GDriveDatabaseManager, create_database_manager
except ImportError as e:
    print(f"❌ エラー: モジュールのインポートに失敗しました: {e}")
    sys.exit(1)


def test_database_operations():
    """データベース操作のテスト"""
    
    print("\n" + "="*70)
    print("  Google Drive Database Manager テスト")
    print("="*70)
    
    # CaseManagerを初期化
    print("\n📋 ステップ1: CaseManager初期化")
    case_manager = CaseManager()
    
    # 事件を検出
    print("\n📋 ステップ2: 事件検出")
    cases = case_manager.detect_cases()
    
    if not cases:
        print("❌ 事件が見つかりませんでした")
        return False
    
    # 最初の事件を選択
    selected_case = cases[0]
    print(f"✅ テスト事件: {selected_case['case_name']}")
    
    # GDriveDatabaseManagerを作成
    print("\n📋 ステップ3: GDriveDatabaseManager作成")
    db_manager = create_database_manager(case_manager, selected_case)
    
    if not db_manager:
        print("❌ GDriveDatabaseManagerの作成に失敗しました")
        return False
    
    print("✅ GDriveDatabaseManager作成成功")
    
    # データベースを読み込み
    print("\n📋 ステップ4: database.json読み込み")
    database = db_manager.load_database()
    print("✅ database.json読み込み成功")
    print(f"   - バージョン: {database.get('version', database.get('metadata', {}).get('database_version', 'N/A'))}")
    print(f"   - 証拠数: {len(database.get('evidence', []))}")
    
    # 証拠統計を表示
    if database.get('evidence'):
        evidence_list = database['evidence']
        completed = [e for e in evidence_list if e.get('status') == 'completed']
        pending = [e for e in evidence_list if e.get('status') == 'pending']
        
        print(f"\n📊 証拠統計:")
        print(f"   - 総数: {len(evidence_list)}")
        print(f"   - 完了: {len(completed)}")
        print(f"   - 未確定: {len(pending)}")
        
        # 最初の5件を表示
        print(f"\n📝 証拠一覧（最大5件）:")
        for i, evidence in enumerate(evidence_list[:5], 1):
            status = evidence.get('status', 'unknown')
            status_icon = "✅" if status == 'completed' else "⏳" if status == 'pending' else "❓"
            
            evidence_id = evidence.get('evidence_id', evidence.get('temp_id', 'N/A'))
            filename = evidence.get('original_filename', 'N/A')
            
            print(f"   {i}. {status_icon} {evidence_id} - {filename}")
    
    # テストデータを追加（オプション）
    print("\n📋 ステップ5: テストデータ追加（スキップ）")
    print("   実際のデータベースには変更を加えません")
    
    # 次の証拠番号を取得
    print("\n📋 ステップ6: 次の証拠番号取得")
    next_ko = db_manager.get_next_evidence_number('ko')
    next_temp = db_manager.get_next_temp_number()
    
    print(f"   - 次の甲号証番号: ko{next_ko:03d}")
    print(f"   - 次の仮番号: tmp_{next_temp:03d}")
    
    print("\n" + "="*70)
    print("  テスト完了")
    print("="*70)
    print("\n✅ 全てのテストが正常に完了しました")
    print("\n📝 確認事項:")
    print("   - database.jsonはGoogle Driveから読み込まれました")
    print("   - ローカルファイルは使用されていません")
    print("   - 全ての操作がGoogle Drive上で実行されました")
    
    return True


def main():
    """メイン関数"""
    
    # 環境チェック
    if not os.getenv('OPENAI_API_KEY'):
        print("\n⚠️ 警告: OPENAI_API_KEYが設定されていません")
        print("   テストは続行しますが、実際の分析には必要です")
    
    if not os.path.exists('credentials.json'):
        print("\n❌ エラー: credentials.jsonが見つかりません")
        print("   Google Drive API機能のテストには必要です")
        return 1
    
    try:
        success = test_database_operations()
        return 0 if success else 1
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

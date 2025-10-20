#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1完全版システム - マルチケースランナー

【機能】
- 共有ドライブから事件を自動検出
- 複数事件の並行管理
- 事件選択後、通常のPhase 1処理を実行

【使用方法】
    python3 run_multi_case.py
    
    または
    
    python3 run_multi_case.py --auto  # 最近使用した事件を自動選択
"""

import os
import sys
import json
import argparse
from datetime import datetime

# 事件マネージャーをインポート
try:
    from case_manager import CaseManager
except ImportError:
    print("❌ case_manager.py が見つかりません")
    sys.exit(1)


def print_banner():
    """バナーを表示"""
    print("\n" + "="*70)
    print("  Phase 1 完全版システム - マルチケース対応")
    print("  複数事件の同時並行管理")
    print("="*70)


def save_last_used_case(case_info: dict):
    """最後に使用した事件を保存"""
    cache_file = os.path.expanduser("~/.phase1_last_case.json")
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({
                'case_id': case_info['case_id'],
                'case_name': case_info['case_name'],
                'case_folder_id': case_info['case_folder_id'],
                'last_used_at': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
    except:
        pass


def load_last_used_case():
    """最後に使用した事件を読み込み"""
    cache_file = os.path.expanduser("~/.phase1_last_case.json")
    if not os.path.exists(cache_file):
        return None
    
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None


def create_local_workspace(case_info: dict) -> str:
    """事件用のローカルワークスペースを作成
    
    Args:
        case_info: 事件情報
    
    Returns:
        ワークスペースのパス
    """
    workspace_root = os.path.expanduser("~/Documents/phase1_cases")
    os.makedirs(workspace_root, exist_ok=True)
    
    # 事件IDでフォルダを作成
    case_workspace = os.path.join(workspace_root, case_info['case_id'])
    os.makedirs(case_workspace, exist_ok=True)
    
    return case_workspace


def setup_case_environment(case_info: dict, workspace_path: str):
    """事件の環境をセットアップ
    
    Args:
        case_info: 事件情報
        workspace_path: ワークスペースのパス
    """
    print(f"\n🔧 事件環境をセットアップ中...")
    print(f"   ワークスペース: {workspace_path}")
    
    # case_config.json を作成
    config_path = os.path.join(workspace_path, "case_config.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(case_info, f, ensure_ascii=False, indent=2)
    print(f"   ✅ case_config.json を作成")
    
    # database.json を初期化（存在しない場合のみ）
    database_path = os.path.join(workspace_path, "database.json")
    if not os.path.exists(database_path):
        database = {
            "case_info": {
                "case_id": case_info['case_id'],
                "case_name": case_info['case_name'],
                "case_folder_id": case_info['case_folder_id']
            },
            "evidence": [],
            "metadata": {
                "version": "3.0",
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_evidence_count": 0,
                "completed_count": 0
            }
        }
        with open(database_path, 'w', encoding='utf-8') as f:
            json.dump(database, f, ensure_ascii=False, indent=2)
        print(f"   ✅ database.json を初期化")
    else:
        print(f"   ℹ️  database.json は既に存在します")
    
    # .env ファイルをコピー（存在する場合）
    root_env = os.path.join(os.getcwd(), ".env")
    case_env = os.path.join(workspace_path, ".env")
    if os.path.exists(root_env) and not os.path.exists(case_env):
        import shutil
        shutil.copy(root_env, case_env)
        print(f"   ✅ .env をコピー")
    
    print(f"✅ 環境セットアップ完了\n")


def run_phase1_for_case(case_info: dict, workspace_path: str):
    """事件のPhase 1処理を実行
    
    Args:
        case_info: 事件情報
        workspace_path: ワークスペースのパス
    """
    print("\n" + "="*70)
    print(f"  Phase 1処理を開始: {case_info['case_name']}")
    print("="*70)
    
    # ワークスペースに移動
    original_dir = os.getcwd()
    os.chdir(workspace_path)
    
    try:
        # run_phase1.py を実行（存在する場合）
        run_phase1_path = os.path.join(original_dir, "run_phase1.py")
        if os.path.exists(run_phase1_path):
            print(f"\n📋 run_phase1.py を実行中...\n")
            import subprocess
            result = subprocess.run([sys.executable, run_phase1_path], cwd=workspace_path)
            
            if result.returncode == 0:
                print("\n✅ Phase 1処理が完了しました")
            else:
                print("\n⚠️ Phase 1処理でエラーが発生しました")
        else:
            print(f"\n⚠️ run_phase1.py が見つかりません: {run_phase1_path}")
            print("   手動で証拠分析を実行してください")
    
    finally:
        # 元のディレクトリに戻る
        os.chdir(original_dir)


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Phase 1 マルチケースシステム')
    parser.add_argument('--auto', action='store_true', 
                       help='最後に使用した事件を自動選択')
    parser.add_argument('--refresh', action='store_true',
                       help='キャッシュをクリアして事件を再検出')
    args = parser.parse_args()
    
    print_banner()
    
    # 事件マネージャーを初期化
    try:
        manager = CaseManager()
    except ValueError as e:
        print(f"\n❌ エラー: {e}")
        print("\n💡 解決方法:")
        print("  global_config.py を開いて SHARED_DRIVE_ROOT_ID を設定してください")
        sys.exit(1)
    
    selected_case = None
    
    # 自動モード
    if args.auto:
        last_case = load_last_used_case()
        if last_case:
            print(f"\n✅ 最後に使用した事件: {last_case['case_name']}")
            use_last = input("この事件を使用しますか？ (Y/n): ").strip().lower()
            if use_last != 'n':
                # 事件情報を再取得
                cases = manager.detect_cases(use_cache=not args.refresh)
                selected_case = next(
                    (c for c in cases if c['case_id'] == last_case['case_id']),
                    None
                )
                if not selected_case:
                    print("⚠️ 事件が見つかりませんでした。再検索します...")
    
    # 事件を検出・選択
    if not selected_case:
        cases = manager.detect_cases(use_cache=not args.refresh)
        manager.display_cases(cases)
        selected_case = manager.select_case_interactive(cases)
    
    if not selected_case:
        print("\n❌ 事件が選択されませんでした")
        sys.exit(0)
    
    # 最後に使用した事件として保存
    save_last_used_case(selected_case)
    
    # ローカルワークスペースを作成
    workspace_path = create_local_workspace(selected_case)
    
    # 環境をセットアップ
    setup_case_environment(selected_case, workspace_path)
    
    # Phase 1処理を実行
    run_phase1_for_case(selected_case, workspace_path)
    
    print("\n" + "="*70)
    print("  処理完了")
    print("="*70)
    print(f"\n📁 ワークスペース: {workspace_path}")
    print(f"📊 database.json: {os.path.join(workspace_path, 'database.json')}")
    print("\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 中断されました")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

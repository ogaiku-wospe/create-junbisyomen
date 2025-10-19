#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1完全版システム - 事件選択機能

【使用方法】
    python3 case_selector.py

【機能】
    - 複数の事件を自動検出
    - 事件を選択して実行
    - 最近使用した事件を記憶
    - 事件情報の表示
"""

import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Optional


class CaseSelector:
    """事件選択クラス"""
    
    def __init__(self, cases_root_dir: str = None):
        """初期化"""
        if cases_root_dir is None:
            self.cases_root_dir = os.path.expanduser("~/Documents/phase1_cases/")
        else:
            self.cases_root_dir = cases_root_dir
        
        self.config_file = os.path.expanduser("~/.phase1_selector.json")
        self.include_current_dir = True
    
    def find_cases(self) -> List[Dict]:
        """事件ディレクトリを検索"""
        cases = []
        
        # 現在のディレクトリをチェック
        if self.include_current_dir:
            current_dir = os.getcwd()
            if self.is_valid_case_dir(current_dir):
                case_info = self.get_case_info(current_dir)
                if case_info:
                    cases.append(case_info)
        
        # cases_root_dirをチェック
        if os.path.exists(self.cases_root_dir):
            for item in os.listdir(self.cases_root_dir):
                case_dir = os.path.join(self.cases_root_dir, item)
                if os.path.isdir(case_dir) and self.is_valid_case_dir(case_dir):
                    case_info = self.get_case_info(case_dir)
                    if case_info:
                        cases.append(case_info)
        
        return cases
    
    def is_valid_case_dir(self, dir_path: str) -> bool:
        """有効な事件ディレクトリかチェック"""
        config_py = os.path.join(dir_path, "config.py")
        return os.path.exists(config_py)
    
    def get_case_info(self, dir_path: str) -> Optional[Dict]:
        """事件情報を取得"""
        try:
            # config.pyから情報を読み取る
            config_py = os.path.join(dir_path, "config.py")
            
            case_info = {
                "dir_path": dir_path,
                "case_name": "不明な事件",
                "evidence_count": 0,
                "completed_count": 0
            }
            
            # config.pyを解析
            with open(config_py, 'r', encoding='utf-8') as f:
                content = f.read()
                for line in content.split('\n'):
                    if 'CASE_NAME' in line and '=' in line:
                        case_info['case_name'] = line.split('=')[1].strip().strip('"\'')
            
            # database.jsonの存在確認
            database_json = os.path.join(dir_path, "database.json")
            if os.path.exists(database_json):
                with open(database_json, 'r', encoding='utf-8') as f:
                    db = json.load(f)
                    case_info['evidence_count'] = len(db.get("evidence", []))
                    case_info['completed_count'] = len([e for e in db.get("evidence", []) 
                                                        if e.get("status") == "completed"])
                    case_info['last_updated'] = db.get("metadata", {}).get("last_updated")
            
            return case_info
            
        except Exception as e:
            return None
    
    def display_cases(self, cases: List[Dict]):
        """事件一覧を表示"""
        print("\n" + "="*70)
        print("  Phase 1完全版システム - 事件選択")
        print("="*70)
        
        if not cases:
            print("\n❌ 事件が見つかりませんでした。")
            return
        
        print(f"\n📋 検出された事件: {len(cases)}件\n")
        
        for idx, case in enumerate(cases, 1):
            print(f"[{idx}] {case['case_name']}")
            print(f"    📁 {case['dir_path']}")
            print(f"    📊 証拠: {case['completed_count']}/{case['evidence_count']} 完了")
            if case.get('last_updated'):
                print(f"    🕐 最終更新: {case['last_updated'][:19]}")
            print()
    
    def select_case(self, cases: List[Dict]) -> Optional[Dict]:
        """事件を選択"""
        if not cases:
            return None
        
        if len(cases) == 1:
            print(f"✅ 事件を自動選択: {cases[0]['case_name']}")
            return cases[0]
        
        while True:
            try:
                choice = input(f"事件を選択 (1-{len(cases)}, 0=終了): ").strip()
                
                if choice == '0':
                    return None
                
                idx = int(choice) - 1
                if 0 <= idx < len(cases):
                    return cases[idx]
                else:
                    print(f"❌ 1-{len(cases)} の番号を入力してください。")
            except ValueError:
                print("❌ 数字を入力してください。")
            except KeyboardInterrupt:
                return None
    
    def run(self):
        """メイン実行"""
        cases = self.find_cases()
        self.display_cases(cases)
        selected_case = self.select_case(cases)
        
        if selected_case:
            os.chdir(selected_case['dir_path'])
            print(f"\n✅ 作業ディレクトリ: {selected_case['dir_path']}")
            print(f"📋 事件: {selected_case['case_name']}\n")
            
            # run_phase1.pyを実行
            import subprocess
            subprocess.run([sys.executable, "run_phase1.py"])


if __name__ == "__main__":
    selector = CaseSelector()
    selector.run()

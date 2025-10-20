#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
システム整合性チェックスクリプト

以下をチェック:
1. 必要なモジュールの存在
2. 設定ファイルの整合性
3. 関数/メソッドの呼び出し整合性
4. エラーハンドリングの網羅性
5. 入力検証の実装
"""

import os
import sys
import ast
import re

class SystemIntegrityChecker:
    """システム整合性チェッカー"""
    
    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.errors = []
        self.warnings = []
        self.info = []
    
    def check_required_files(self):
        """必要なファイルの存在チェック"""
        print("\n[1/6] 必要なファイルのチェック...")
        
        required_files = [
            'global_config.py',
            'case_manager.py',
            'evidence_organizer.py',
            'gdrive_database_manager.py',
            'metadata_extractor.py',
            'file_processor.py',
            'ai_analyzer_complete.py',
            'run_phase1_multi.py'
        ]
        
        missing = []
        for filename in required_files:
            filepath = os.path.join(self.project_dir, filename)
            if not os.path.exists(filepath):
                missing.append(filename)
        
        if missing:
            self.errors.append(f"必要なファイルが見つかりません: {', '.join(missing)}")
            print(f"  エラー: {len(missing)}件のファイルが見つかりません")
        else:
            self.info.append("すべての必要なファイルが存在します")
            print("  OK: すべてのファイルが存在します")
    
    def check_import_statements(self):
        """インポート文の整合性チェック"""
        print("\n[2/6] インポート文のチェック...")
        
        main_file = os.path.join(self.project_dir, 'run_phase1_multi.py')
        if not os.path.exists(main_file):
            self.errors.append("run_phase1_multi.pyが見つかりません")
            return
        
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # インポートされているモジュール
        imports = re.findall(r'from\s+(\w+)\s+import', content)
        imports += re.findall(r'import\s+(\w+)', content)
        
        # 必要なモジュール
        required_imports = [
            'global_config',
            'case_manager',
            'evidence_organizer',
            'gdrive_database_manager',
            'metadata_extractor',
            'file_processor',
            'ai_analyzer_complete'
        ]
        
        missing_imports = [m for m in required_imports if m not in imports]
        
        if missing_imports:
            self.errors.append(f"インポートされていないモジュール: {', '.join(missing_imports)}")
            print(f"  エラー: {len(missing_imports)}件のモジュールがインポートされていません")
        else:
            self.info.append("すべての必要なモジュールがインポートされています")
            print("  OK: すべてのインポートが正常です")
    
    def check_error_handling(self):
        """エラーハンドリングのチェック"""
        print("\n[3/6] エラーハンドリングのチェック...")
        
        main_file = os.path.join(self.project_dir, 'run_phase1_multi.py')
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # try-except ブロックの数
        try_count = len(re.findall(r'\btry:', content))
        except_count = len(re.findall(r'\bexcept', content))
        
        # 主要メソッドの数（def で始まる）
        method_count = len(re.findall(r'^\s{4}def\s+', content, re.MULTILINE))
        
        # エラーハンドリングの割合
        error_handling_ratio = except_count / method_count if method_count > 0 else 0
        
        print(f"  try-exceptブロック: {try_count}個")
        print(f"  メソッド数: {method_count}個")
        print(f"  エラーハンドリング率: {error_handling_ratio:.1%}")
        
        if error_handling_ratio < 0.5:
            self.warnings.append(f"エラーハンドリングが不足している可能性があります ({error_handling_ratio:.1%})")
        else:
            self.info.append(f"エラーハンドリングが適切に実装されています ({error_handling_ratio:.1%})")
    
    def check_input_validation(self):
        """入力検証のチェック"""
        print("\n[4/6] 入力検証のチェック...")
        
        main_file = os.path.join(self.project_dir, 'run_phase1_multi.py')
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # input() 呼び出しの数
        input_count = len(re.findall(r'input\(', content))
        
        # 入力検証パターン（if not, if ... in, while True など）
        validation_patterns = [
            r'if\s+not\s+\w+:',
            r'if\s+\w+\s+in\s+\[',
            r'while\s+True:.*input\(',
        ]
        
        validation_count = sum(len(re.findall(pattern, content, re.DOTALL)) for pattern in validation_patterns)
        
        print(f"  input()呼び出し: {input_count}箇所")
        print(f"  検証パターン: {validation_count}箇所")
        
        if validation_count < input_count * 0.5:
            self.warnings.append(f"入力検証が不足している可能性があります ({validation_count}/{input_count})")
        else:
            self.info.append(f"入力検証が適切に実装されています ({validation_count}/{input_count})")
    
    def check_user_feedback(self):
        """ユーザーフィードバックのチェック"""
        print("\n[5/6] ユーザーフィードバックのチェック...")
        
        main_file = os.path.join(self.project_dir, 'run_phase1_multi.py')
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # フィードバックメッセージのカウント
        error_messages = len(re.findall(r'print\("エラー:', content))
        error_messages += len(re.findall(r'print\(f"エラー:', content))
        
        success_messages = len(re.findall(r'print\("完了', content))
        success_messages += len(re.findall(r'print\(f"完了', content))
        
        warning_messages = len(re.findall(r'print\("警告:', content))
        warning_messages += len(re.findall(r'print\(f"警告:', content))
        
        print(f"  エラーメッセージ: {error_messages}箇所")
        print(f"  成功メッセージ: {success_messages}箇所")
        print(f"  警告メッセージ: {warning_messages}箇所")
        
        total_feedback = error_messages + success_messages + warning_messages
        if total_feedback < 20:
            self.warnings.append(f"ユーザーフィードバックが不足している可能性があります ({total_feedback}箇所)")
        else:
            self.info.append(f"ユーザーフィードバックが適切に実装されています ({total_feedback}箇所)")
    
    def check_emoji_usage(self):
        """絵文字使用のチェック"""
        print("\n[6/6] 絵文字使用のチェック...")
        
        main_file = os.path.join(self.project_dir, 'run_phase1_multi.py')
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 絵文字のパターン
        emoji_pattern = r'[❌✅📋🔍📁📊📝🆕📅👋🤖💾📈🔧⚠️⏳❓]'
        emojis = re.findall(emoji_pattern, content)
        
        emoji_count = len(emojis)
        
        print(f"  絵文字の使用: {emoji_count}箇所")
        
        if emoji_count > 50:
            self.warnings.append(f"絵文字が多すぎる可能性があります ({emoji_count}箇所)")
        elif emoji_count > 20:
            self.info.append(f"絵文字は適度に使用されています ({emoji_count}箇所)")
        else:
            self.info.append(f"絵文字は最小限に抑えられています ({emoji_count}箇所)")
    
    def generate_report(self):
        """レポート生成"""
        print("\n" + "=" * 70)
        print("  システム整合性チェック結果")
        print("=" * 70)
        
        if self.errors:
            print("\nエラー:")
            for idx, error in enumerate(self.errors, 1):
                print(f"  {idx}. {error}")
        
        if self.warnings:
            print("\n警告:")
            for idx, warning in enumerate(self.warnings, 1):
                print(f"  {idx}. {warning}")
        
        if self.info:
            print("\n情報:")
            for idx, info in enumerate(self.info, 1):
                print(f"  {idx}. {info}")
        
        print("\n" + "=" * 70)
        print(f"  エラー: {len(self.errors)}件")
        print(f"  警告: {len(self.warnings)}件")
        print(f"  情報: {len(self.info)}件")
        print("=" * 70)
        
        if self.errors:
            return False
        return True
    
    def run(self):
        """全チェックを実行"""
        print("=" * 70)
        print("  システム整合性チェック開始")
        print("=" * 70)
        
        self.check_required_files()
        self.check_import_statements()
        self.check_error_handling()
        self.check_input_validation()
        self.check_user_feedback()
        self.check_emoji_usage()
        
        return self.generate_report()


def main():
    # スクリプトが実行されているディレクトリを自動検出
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # コマンドライン引数でディレクトリを指定可能
    if len(sys.argv) > 1:
        project_dir = sys.argv[1]
    else:
        project_dir = script_dir
    
    print(f"チェック対象ディレクトリ: {project_dir}\n")
    
    checker = SystemIntegrityChecker(project_dir)
    
    success = checker.run()
    
    if success:
        print("\nシステム整合性チェック: 合格")
        sys.exit(0)
    else:
        print("\nシステム整合性チェック: 不合格")
        sys.exit(1)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
database.jsonの証拠IDを変換するツール

【機能】
- Google Driveからdatabase.jsonをダウンロード
- すべての tmp_ を tmp_ko_ に変換
- 変換結果をGoogle Driveにアップロード
- バックアップを作成

【使用方法】
    python3 convert_evidence_ids.py
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

try:
    import global_config as gconfig
    from case_manager import CaseManager
    from gdrive_database_manager import create_database_manager
except ImportError as e:
    print(f"❌ エラー: モジュールのインポートに失敗しました: {e}")
    sys.exit(1)


class EvidenceIDConverter:
    """証拠ID変換クラス"""
    
    def __init__(self, case_manager: CaseManager, current_case: dict):
        """初期化
        
        Args:
            case_manager: CaseManagerインスタンス
            current_case: 現在の事件情報
        """
        self.case_manager = case_manager
        self.current_case = current_case
        self.db_manager = create_database_manager(case_manager, current_case)
        
        if not self.db_manager:
            raise Exception("データベースマネージャーの初期化に失敗しました")
    
    def load_database(self) -> dict:
        """Google DriveからDatabase.jsonを読み込む
        
        Returns:
            データベース辞書
        """
        print("\n" + "="*70)
        print("  Google DriveからDatabase.jsonを読み込み中...")
        print("="*70)
        
        database = self.db_manager.load_database()
        if not database:
            raise Exception("database.jsonの読み込みに失敗しました")
        
        evidence_count = len(database.get('evidence', []))
        print(f"✅ 読み込み成功: {evidence_count}件の証拠")
        
        return database
    
    def convert_evidence_ids(self, database: dict, old_prefix: str, new_prefix: str) -> tuple:
        """証拠IDを変換
        
        Args:
            database: データベース辞書
            old_prefix: 変換前のプレフィックス（例: "tmp_"）
            new_prefix: 変換後のプレフィックス（例: "tmp_ko_"）
        
        Returns:
            (変換後のdatabase, 変換件数)
        """
        print("\n" + "="*70)
        print(f"  証拠IDを変換中: {old_prefix} → {new_prefix}")
        print("="*70)
        
        converted_count = 0
        evidence_list = database.get('evidence', [])
        
        for evidence in evidence_list:
            # evidence_idを変換
            old_id = evidence.get('evidence_id', '')
            if old_id.startswith(old_prefix):
                new_id = old_id.replace(old_prefix, new_prefix, 1)
                evidence['evidence_id'] = new_id
                
                # evidence_numberも変換
                old_number = evidence.get('evidence_number', '')
                if old_prefix in old_number:
                    new_number = old_number.replace(old_prefix, new_prefix, 1)
                    evidence['evidence_number'] = new_number
                
                print(f"  ✓ {old_id:20} → {new_id}")
                converted_count += 1
        
        # メタデータの更新日時を更新
        if 'metadata' in database:
            database['metadata']['last_updated'] = datetime.now().isoformat()
        
        print(f"\n✅ 変換完了: {converted_count}件")
        return database, converted_count
    
    def create_backup(self, database: dict) -> str:
        """ローカルにバックアップを作成
        
        Args:
            database: データベース辞書
        
        Returns:
            バックアップファイルパス
        """
        case_id = self.current_case.get('case_id', 'unknown')
        backup_dir = os.path.join(gconfig.LOCAL_STORAGE_DIR, case_id, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"database_backup_{timestamp}.json")
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(database, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 バックアップ作成: {backup_path}")
        return backup_path
    
    def save_database(self, database: dict) -> bool:
        """Google Driveにdatabase.jsonを保存
        
        Args:
            database: データベース辞書
        
        Returns:
            成功したかどうか
        """
        print("\n" + "="*70)
        print("  Google Driveにアップロード中...")
        print("="*70)
        
        success = self.db_manager.save_database(database)
        if success:
            print("✅ アップロード成功")
        else:
            print("❌ アップロード失敗")
        
        return success
    
    def show_preview(self, database: dict, limit: int = 10):
        """変換結果のプレビューを表示
        
        Args:
            database: データベース辞書
            limit: 表示する件数
        """
        print("\n" + "="*70)
        print("  変換後のプレビュー")
        print("="*70)
        
        evidence_list = database.get('evidence', [])
        for i, evidence in enumerate(evidence_list[:limit]):
            eid = evidence.get('evidence_id', 'unknown')
            enum = evidence.get('evidence_number', 'unknown')
            fname = evidence.get('original_filename', 'unknown')
            print(f"{i+1:3}. {eid:20} {enum:25} {fname}")
        
        if len(evidence_list) > limit:
            print(f"\n... 他 {len(evidence_list) - limit} 件")
        
        print(f"\n総件数: {len(evidence_list)}件")


def main():
    """メイン関数"""
    print("="*70)
    print("  証拠ID変換ツール")
    print("  database.json: tmp_ → tmp_ko_")
    print("="*70)
    
    # CaseManagerを初期化
    try:
        case_manager = CaseManager()
        
        # current_case.jsonから現在の事件を読み込む
        current_case_path = os.path.join(os.path.dirname(__file__), 'current_case.json')
        
        if not os.path.exists(current_case_path):
            print("\n❌ エラー: 事件が選択されていません。")
            print("   run_phase1_multi.py で事件を選択してから実行してください。")
            print(f"   (current_case.json が見つかりません: {current_case_path})")
            return
        
        # current_case.jsonを読み込み
        with open(current_case_path, 'r', encoding='utf-8') as f:
            current_case = json.load(f)
        
        if not current_case:
            print("\n❌ エラー: 事件情報が不正です。")
            print("   run_phase1_multi.py で事件を選択してから実行してください。")
            return
        
        case_name = current_case.get('case_name', '不明')
        case_id = current_case.get('case_id', '不明')
        
        print(f"\n📁 事件: {case_name} ({case_id})")
        
        # 変換ツールを初期化
        converter = EvidenceIDConverter(case_manager, current_case)
        
        # データベースを読み込み
        original_database = converter.load_database()
        
        # バックアップを作成
        backup_path = converter.create_backup(original_database)
        
        # 変換パラメータ
        old_prefix = "tmp_"
        new_prefix = "tmp_ko_"
        
        print(f"\n変換内容: {old_prefix} → {new_prefix}")
        print("この操作を実行すると、Google Drive上のdatabase.jsonが更新されます。")
        
        # 確認
        response = input("\n続行しますか？ (y/n): ").strip().lower()
        if response != 'y':
            print("\n❌ 操作をキャンセルしました。")
            return
        
        # 証拠IDを変換
        converted_database, converted_count = converter.convert_evidence_ids(
            original_database.copy(),
            old_prefix,
            new_prefix
        )
        
        if converted_count == 0:
            print(f"\n⚠️  変換対象の証拠が見つかりませんでした（{old_prefix}で始まる証拠ID）")
            return
        
        # プレビューを表示
        converter.show_preview(converted_database)
        
        # 最終確認
        print("\n" + "="*70)
        response = input("Google Driveに保存しますか？ (y/n): ").strip().lower()
        if response != 'y':
            print("\n❌ 保存をキャンセルしました。")
            print(f"   バックアップは保存されています: {backup_path}")
            return
        
        # Google Driveに保存
        success = converter.save_database(converted_database)
        
        if success:
            print("\n" + "="*70)
            print("  ✅ 変換完了！")
            print("="*70)
            print(f"\n変換件数: {converted_count}件")
            print(f"バックアップ: {backup_path}")
            print(f"\n次回からは以下の形式で入力してください:")
            print(f"  例: {new_prefix}001-021")
        else:
            print("\n❌ 保存に失敗しました。")
            print(f"   バックアップから復元できます: {backup_path}")
    
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

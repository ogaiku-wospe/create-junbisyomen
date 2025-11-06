#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ローカルdatabase.jsonのクリーンアップスクリプト

database.jsonをGoogle Driveで管理するようになったため、
ローカルに残っているdatabase.jsonファイルを削除します。
"""

import os
import sys
import shutil
from datetime import datetime

def backup_and_remove_local_database():
    """ローカルdatabase.jsonをバックアップして削除"""
    
    local_db_path = "database.json"
    
    if not os.path.exists(local_db_path):
        print("✅ ローカルdatabase.jsonは存在しません（クリーンアップ不要）")
        return True
    
    print("\n" + "="*70)
    print("  ローカルdatabase.jsonクリーンアップ")
    print("="*70)
    
    print(f"\n📁 検出: {local_db_path}")
    print(f"   サイズ: {os.path.getsize(local_db_path)} bytes")
    print(f"   最終更新: {datetime.fromtimestamp(os.path.getmtime(local_db_path))}")
    
    # バックアップディレクトリを作成
    backup_dir = "local_backup"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # タイムスタンプ付きでバックアップ
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"database_{timestamp}.json")
    
    print(f"\n📦 バックアップ先: {backup_path}")
    
    confirm = input("\nローカルdatabase.jsonを削除しますか？ (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("\n❌ キャンセルしました")
        return False
    
    try:
        # バックアップ
        shutil.copy2(local_db_path, backup_path)
        print(f"✅ バックアップ完了: {backup_path}")
        
        # 削除
        os.remove(local_db_path)
        print(f"✅ ローカルdatabase.json削除完了")
        
        print("\n" + "="*70)
        print("  クリーンアップ完了")
        print("="*70)
        print("\n📝 今後について:")
        print("  - database.jsonはGoogle Driveで管理されます")
        print("  - ローカルファイルは不要になりました")
        print("  - バックアップは local_backup/ に保存されています")
        
        return True
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """メイン関数"""
    print("\n" + "="*70)
    print("  database.jsonクリーンアップツール")
    print("="*70)
    print("\n📋 説明:")
    print("  このスクリプトは、ローカルに残っているdatabase.jsonを")
    print("  バックアップしてから削除します。")
    print("\n  今後、database.jsonはGoogle Driveで管理されます。")
    
    success = backup_and_remove_local_database()
    
    if success:
        print("\n✅ 処理が正常に完了しました")
        return 0
    else:
        print("\n❌ 処理に失敗しました")
        return 1


if __name__ == "__main__":
    sys.exit(main())

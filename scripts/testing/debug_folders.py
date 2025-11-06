#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
デバッグ用スクリプト - 共有ドライブのフォルダ構造を確認
"""

import os
import sys
from case_manager import CaseManager

def main():
    print("\n" + "="*70)
    print("  共有ドライブフォルダ構造確認")
    print("="*70)
    
    manager = CaseManager()
    service = manager.get_google_drive_service()
    
    if not service:
        print("❌ Google Drive認証に失敗しました")
        return
    
    # ルートフォルダの情報を取得
    print(f"\n🔍 共有ドライブルート: {manager.shared_drive_root_id}")
    
    try:
        # 共有ドライブ配下のフォルダを一覧取得
        query = f"'{manager.shared_drive_root_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        
        results = service.files().list(
            q=query,
            corpora='drive',
            driveId=manager.shared_drive_root_id,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            fields='files(id, name, createdTime, modifiedTime, webViewLink)',
            pageSize=100
        ).execute()
        
        folders = results.get('files', [])
        
        print(f"\n📁 検出されたフォルダ: {len(folders)}個\n")
        
        for i, folder in enumerate(folders, 1):
            print(f"{i}. {folder['name']}")
            print(f"   ID: {folder['id']}")
            print(f"   URL: {folder.get('webViewLink', 'N/A')}")
            
            # このフォルダ内のサブフォルダを確認
            sub_query = f"'{folder['id']}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
            
            sub_results = service.files().list(
                q=sub_query,
                corpora='drive',
                driveId=manager.shared_drive_root_id,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                fields='files(name)',
                pageSize=100
            ).execute()
            
            sub_folders = sub_results.get('files', [])
            
            if sub_folders:
                print(f"   サブフォルダ: {', '.join([f['name'] for f in sub_folders])}")
                
                # 甲号証フォルダがあるかチェック
                has_ko = any(f['name'] == '甲号証' for f in sub_folders)
                if has_ko:
                    print(f"   ✅ 甲号証フォルダあり → 事件として認識されます")
                else:
                    print(f"   ⚠️  甲号証フォルダなし → 事件として認識されません")
            else:
                print(f"   サブフォルダ: なし")
                print(f"   ⚠️  甲号証フォルダなし → 事件として認識されません")
            
            print()
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

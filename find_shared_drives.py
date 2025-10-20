#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
すべての共有ドライブを一覧表示するスクリプト
"""

import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
    print("\n" + "="*70)
    print("  利用可能な共有ドライブ一覧")
    print("="*70)
    
    # 認証
    if 'type' in json.load(open('credentials.json')) and json.load(open('credentials.json'))['type'] == 'service_account':
        print("🔐 サービスアカウント認証を使用\n")
        creds = service_account.Credentials.from_service_account_file(
            'credentials.json', scopes=SCOPES)
    else:
        print("❌ OAuth認証は未対応（このスクリプトはサービスアカウント専用）")
        return
    
    service = build('drive', 'v3', credentials=creds)
    
    try:
        # すべての共有ドライブを取得
        results = service.drives().list(pageSize=100).execute()
        drives = results.get('drives', [])
        
        if not drives:
            print("❌ アクセス可能な共有ドライブが見つかりません\n")
            print("💡 サービスアカウントが共有ドライブのメンバーになっていない可能性があります")
            print("   サービスアカウント: utd-tec-mamori@create-junbisyomen.iam.gserviceaccount.com")
            return
        
        print(f"✅ {len(drives)}個の共有ドライブが見つかりました\n")
        
        for i, drive in enumerate(drives, 1):
            print(f"{i}. 名前: {drive['name']}")
            print(f"   ID: {drive['id']}")
            
            # このIDを使ってフォルダを検索
            query = f"'{drive['id']}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
            
            folder_results = service.files().list(
                q=query,
                corpora='drive',
                driveId=drive['id'],
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                fields='files(name)',
                pageSize=10
            ).execute()
            
            folders = folder_results.get('files', [])
            
            if folders:
                folder_names = [f['name'] for f in folders]
                print(f"   フォルダ: {', '.join(folder_names)}")
            else:
                print(f"   フォルダ: なし（空の共有ドライブ）")
            
            print()
        
        print("="*70)
        print("💡 global_config.py に設定するIDは上記の「ID」の値です")
        print("="*70)
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
サービスアカウントの権限とスコープを確認するスクリプト
"""

import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

# 使用しているスコープ
SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
    print("\n" + "="*70)
    print("  サービスアカウント権限チェック")
    print("="*70)
    
    # credentials.jsonの形式を確認
    with open('credentials.json', 'r') as f:
        creds_data = json.load(f)
    
    if 'type' not in creds_data or creds_data['type'] != 'service_account':
        print("❌ credentials.jsonはサービスアカウント形式ではありません")
        print(f"   タイプ: {creds_data.get('type', 'unknown')}")
        return
    
    print(f"\n✅ サービスアカウント: {creds_data.get('client_email')}")
    print(f"📋 プロジェクトID: {creds_data.get('project_id')}")
    
    # 認証
    print(f"\n🔐 認証中（スコープ: {SCOPES}）...")
    creds = service_account.Credentials.from_service_account_file(
        'credentials.json', scopes=SCOPES)
    
    print("✅ 認証成功")
    
    # テスト: 共有ドライブ一覧取得
    print("\n📁 テスト1: 共有ドライブ一覧取得")
    try:
        service = build('drive', 'v3', credentials=creds)
        results = service.drives().list(pageSize=10).execute()
        drives = results.get('drives', [])
        print(f"✅ 成功: {len(drives)}個の共有ドライブを取得")
    except Exception as e:
        print(f"❌ 失敗: {e}")
    
    # テスト: フォルダ作成（実際には作成せず、権限だけチェック）
    print("\n📝 テスト2: 書き込み権限チェック")
    print("   （実際のフォルダは作成しません）")
    
    # 共有ドライブIDを取得
    shared_drive_id = "0AO6q4_G7DmYSUk9PVA"
    
    try:
        # ドライ��ン: メタデータのみ作成（実際には作成されない）
        folder_metadata = {
            'name': '__test_permission_check__',
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [shared_drive_id]
        }
        
        # NOTE: 実際には execute() を呼ばないので作成されない
        request = service.files().create(
            body=folder_metadata,
            supportsAllDrives=True,
            fields='id, name'
        )
        
        print(f"✅ リクエスト生成成功")
        print(f"   実際に作成するには .execute() を呼び出します")
        
        # 実際に作成テスト（確認付き）
        confirm = input("\n⚠️  実際にテストフォルダを作成して削除しますか？ (y/n): ").strip().lower()
        
        if confirm == 'y':
            print("\n📁 テストフォルダを作成中...")
            test_folder = request.execute()
            print(f"✅ 作成成功: {test_folder['name']} (ID: {test_folder['id']})")
            
            # 削除
            print("🗑️  テストフォルダを削除中...")
            service.files().delete(
                fileId=test_folder['id'],
                supportsAllDrives=True
            ).execute()
            print("✅ 削除成功")
            
            print("\n✅✅✅ サービスアカウントは正しく動作しています！")
        else:
            print("\n💡 スキップしました")
            print("   書き込みテストは実行されていません")
        
    except Exception as e:
        print(f"❌ 失敗: {e}")
        print("\n📋 考えられる原因:")
        print("  1. サービスアカウントが共有ドライブのメンバーになっていない")
        print("  2. サービスアカウントの役割が「閲覧者」または「編集者」")
        print("     → 「コンテンツ管理者」または「管理者」に変更してください")
        print("  3. APIスコープが不足している")
        print("     → OAuth 2.0認証への切り替えを検討してください")

if __name__ == "__main__":
    main()

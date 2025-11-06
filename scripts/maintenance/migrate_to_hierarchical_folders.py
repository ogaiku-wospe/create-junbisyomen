#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
既存フォルダ構成から階層的フォルダ構成への移行ツール

【移行内容】
旧構成:
  事件フォルダ/
  ├── 甲号証/              (確定済み証拠)
  ├── 乙号証/              (確定済み証拠)
  ├── 未分類/              (未整理)
  └── 整理済み_未確定/     (仮番号)

新構成:
  事件フォルダ/
  ├── 甲号証/
  │   ├── 確定済み/
  │   ├── 整理済み_未確定/
  │   └── 未分類/
  └── 乙号証/
      ├── 確定済み/
      ├── 整理済み_未確定/
      └── 未分類/

【使用方法】
    python3 migrate_to_hierarchical_folders.py
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional

# 自作モジュールのインポート
try:
    import global_config as gconfig
    from case_manager import CaseManager
except ImportError as e:
    print(f"エラー: モジュールのインポートに失敗しました: {e}")
    sys.exit(1)

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('migration.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FolderMigrationTool:
    """フォルダ構成移行ツール"""
    
    def __init__(self):
        """初期化"""
        self.case_manager = CaseManager()
        self.service = None
        self.dry_run = True  # デフォルトはドライラン（実際には変更しない）
    
    def migrate_case(self, case_info: Dict, dry_run: bool = True) -> bool:
        """事件のフォルダ構成を移行
        
        Args:
            case_info: 事件情報
            dry_run: True=ドライラン（変更しない）, False=実際に移行
        
        Returns:
            成功: True, 失敗: False
        """
        self.dry_run = dry_run
        
        print("\n" + "="*70)
        print(f"  フォルダ構成移行: {case_info['case_name']}")
        print(f"  モード: {'ドライラン（確認のみ）' if dry_run else '実際に移行'}")
        print("="*70)
        
        try:
            # Google Drive APIサービスを取得
            self.service = self.case_manager.get_google_drive_service()
            if not self.service:
                logger.error("Google Drive APIサービスの取得に失敗しました")
                return False
            
            # 事件フォルダIDを取得
            case_folder_id = case_info['case_folder_id']
            
            # 旧フォルダ構成を確認
            old_structure = self._check_old_folder_structure(case_folder_id)
            if not old_structure:
                print("\n⚠️  旧フォルダ構成が見つかりません")
                print("   既に新構成に移行済みか、フォルダ構成が異なります")
                return False
            
            # 新フォルダ構成を作成
            new_structure = self._create_new_folder_structure(case_folder_id)
            if not new_structure:
                logger.error("新フォルダ構成の作成に失敗しました")
                return False
            
            # ファイルを移行
            migration_plan = self._create_migration_plan(old_structure, new_structure)
            self._execute_migration(migration_plan)
            
            # database.jsonを更新
            self._update_database(case_info, migration_plan)
            
            print("\n" + "="*70)
            if dry_run:
                print("  ✅ ドライラン完了（実際の変更は行われていません）")
                print("  実際に移行する場合は --execute オプションを付けてください")
            else:
                print("  ✅ 移行完了！")
            print("="*70)
            
            return True
            
        except Exception as e:
            logger.error(f"移行中にエラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _check_old_folder_structure(self, case_folder_id: str) -> Optional[Dict]:
        """旧フォルダ構成を確認
        
        Args:
            case_folder_id: 事件フォルダID
        
        Returns:
            旧フォルダ構成の情報（見つからない場合はNone）
        """
        try:
            # 事件フォルダ直下のフォルダを取得
            query = f"'{case_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.service.files().list(
                q=query,
                corpora='drive',
                driveId=gconfig.SHARED_DRIVE_ROOT_ID,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                fields='files(id, name)',
                pageSize=100
            ).execute()
            
            folders = results.get('files', [])
            folder_dict = {f['name']: f['id'] for f in folders}
            
            # 旧構成のフォルダがあるかチェック
            old_structure = {}
            
            if '甲号証' in folder_dict:
                # 甲号証フォルダが事件フォルダ直下にある = 旧構成の可能性
                old_structure['ko_confirmed'] = {
                    'id': folder_dict['甲号証'],
                    'name': '甲号証'
                }
            
            if '乙号証' in folder_dict:
                old_structure['otsu_confirmed'] = {
                    'id': folder_dict['乙号証'],
                    'name': '乙号証'
                }
            
            if '未分類' in folder_dict:
                old_structure['unclassified'] = {
                    'id': folder_dict['未分類'],
                    'name': '未分類'
                }
            
            if '整理済み_未確定' in folder_dict:
                old_structure['pending'] = {
                    'id': folder_dict['整理済み_未確定'],
                    'name': '整理済み_未確定'
                }
            
            if old_structure:
                print("\n📁 旧フォルダ構成を検出しました:")
                for key, folder in old_structure.items():
                    print(f"   - {folder['name']}")
                return old_structure
            
            return None
            
        except Exception as e:
            logger.error(f"旧フォルダ構成の確認に失敗しました: {e}")
            return None
    
    def _create_new_folder_structure(self, case_folder_id: str) -> Optional[Dict]:
        """新フォルダ構成を作成
        
        Args:
            case_folder_id: 事件フォルダID
        
        Returns:
            新フォルダ構成の情報
        """
        print("\n🔨 新フォルダ構成を作成中...")
        
        new_structure = {}
        
        try:
            # 甲号証フォルダとサブフォルダを作成
            ko_folder = self._create_or_get_folder(
                '甲号証', case_folder_id
            )
            new_structure['ko_root'] = ko_folder
            
            new_structure['ko_confirmed'] = self._create_or_get_folder(
                '確定済み', ko_folder['id']
            )
            new_structure['ko_pending'] = self._create_or_get_folder(
                '整理済み_未確定', ko_folder['id']
            )
            new_structure['ko_unclassified'] = self._create_or_get_folder(
                '未分類', ko_folder['id']
            )
            
            # 乙号証フォルダとサブフォルダを作成
            otsu_folder = self._create_or_get_folder(
                '乙号証', case_folder_id
            )
            new_structure['otsu_root'] = otsu_folder
            
            new_structure['otsu_confirmed'] = self._create_or_get_folder(
                '確定済み', otsu_folder['id']
            )
            new_structure['otsu_pending'] = self._create_or_get_folder(
                '整理済み_未確定', otsu_folder['id']
            )
            new_structure['otsu_unclassified'] = self._create_or_get_folder(
                '未分類', otsu_folder['id']
            )
            
            print("\n✅ 新フォルダ構成:")
            print("   甲号証/")
            print("   ├── 確定済み/")
            print("   ├── 整理済み_未確定/")
            print("   └── 未分類/")
            print("   乙号証/")
            print("   ├── 確定済み/")
            print("   ├── 整理済み_未確定/")
            print("   └── 未分類/")
            
            return new_structure
            
        except Exception as e:
            logger.error(f"新フォルダ構成の作成に失敗しました: {e}")
            return None
    
    def _create_or_get_folder(self, folder_name: str, parent_id: str) -> Dict:
        """フォルダを作成または取得
        
        Args:
            folder_name: フォルダ名
            parent_id: 親フォルダID
        
        Returns:
            フォルダ情報 {'id': ..., 'name': ...}
        """
        if self.dry_run:
            # ドライランの場合は仮IDを返す
            return {
                'id': f"dry_run_{folder_name}_{parent_id}",
                'name': folder_name
            }
        
        try:
            # 既存のフォルダをチェック
            query = f"name='{folder_name}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.service.files().list(
                q=query,
                corpora='drive',
                driveId=gconfig.SHARED_DRIVE_ROOT_ID,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                fields='files(id, name)',
                pageSize=1
            ).execute()
            
            files = results.get('files', [])
            if files:
                # 既存のフォルダを使用
                return {'id': files[0]['id'], 'name': files[0]['name']}
            
            # フォルダを作成
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_id]
            }
            
            folder = self.service.files().create(
                body=folder_metadata,
                supportsAllDrives=True,
                fields='id, name'
            ).execute()
            
            logger.info(f"フォルダ作成: {folder_name}")
            return {'id': folder['id'], 'name': folder['name']}
            
        except Exception as e:
            logger.error(f"フォルダ作成に失敗しました: {folder_name}, {e}")
            raise
    
    def _create_migration_plan(self, old_structure: Dict, new_structure: Dict) -> List[Dict]:
        """移行プランを作成
        
        Args:
            old_structure: 旧フォルダ構成
            new_structure: 新フォルダ構成
        
        Returns:
            移行プラン（ファイル移動リスト）
        """
        print("\n📋 移行プランを作成中...")
        
        migration_plan = []
        
        # 旧「甲号証」→ 新「甲号証/確定済み」
        if 'ko_confirmed' in old_structure:
            files = self._list_files_in_folder(old_structure['ko_confirmed']['id'])
            for file in files:
                migration_plan.append({
                    'file_id': file['id'],
                    'file_name': file['name'],
                    'from_folder': old_structure['ko_confirmed']['name'],
                    'to_folder': '甲号証/確定済み',
                    'from_folder_id': old_structure['ko_confirmed']['id'],
                    'to_folder_id': new_structure['ko_confirmed']['id'],
                    'evidence_type': 'ko'
                })
        
        # 旧「乙号証」→ 新「乙号証/確定済み」
        if 'otsu_confirmed' in old_structure:
            files = self._list_files_in_folder(old_structure['otsu_confirmed']['id'])
            for file in files:
                migration_plan.append({
                    'file_id': file['id'],
                    'file_name': file['name'],
                    'from_folder': old_structure['otsu_confirmed']['name'],
                    'to_folder': '乙号証/確定済み',
                    'from_folder_id': old_structure['otsu_confirmed']['id'],
                    'to_folder_id': new_structure['otsu_confirmed']['id'],
                    'evidence_type': 'otsu'
                })
        
        # 旧「整理済み_未確定」→ 新「甲号証/整理済み_未確定」または「乙号証/整理済み_未確定」
        if 'pending' in old_structure:
            files = self._list_files_in_folder(old_structure['pending']['id'])
            for file in files:
                # ファイル名から証拠種別を判定
                evidence_type = self._detect_evidence_type_from_filename(file['name'])
                
                if evidence_type == 'ko':
                    migration_plan.append({
                        'file_id': file['id'],
                        'file_name': file['name'],
                        'from_folder': old_structure['pending']['name'],
                        'to_folder': '甲号証/整理済み_未確定',
                        'from_folder_id': old_structure['pending']['id'],
                        'to_folder_id': new_structure['ko_pending']['id'],
                        'evidence_type': 'ko',
                        'rename': file['name'].replace('tmp_', 'tmp_ko_')  # tmp_001 → tmp_ko_001
                    })
                else:
                    migration_plan.append({
                        'file_id': file['id'],
                        'file_name': file['name'],
                        'from_folder': old_structure['pending']['name'],
                        'to_folder': '乙号証/整理済み_未確定',
                        'from_folder_id': old_structure['pending']['id'],
                        'to_folder_id': new_structure['otsu_pending']['id'],
                        'evidence_type': 'otsu',
                        'rename': file['name'].replace('tmp_', 'tmp_otsu_')  # tmp_001 → tmp_otsu_001
                    })
        
        # 旧「未分類」→ 新「甲号証/未分類」（デフォルト）
        if 'unclassified' in old_structure:
            files = self._list_files_in_folder(old_structure['unclassified']['id'])
            for file in files:
                migration_plan.append({
                    'file_id': file['id'],
                    'file_name': file['name'],
                    'from_folder': old_structure['unclassified']['name'],
                    'to_folder': '甲号証/未分類',
                    'from_folder_id': old_structure['unclassified']['id'],
                    'to_folder_id': new_structure['ko_unclassified']['id'],
                    'evidence_type': 'ko'
                })
        
        print(f"\n📊 移行対象: {len(migration_plan)}ファイル")
        
        # サマリー表示
        ko_count = sum(1 for m in migration_plan if m['evidence_type'] == 'ko')
        otsu_count = sum(1 for m in migration_plan if m['evidence_type'] == 'otsu')
        print(f"   - 甲号証: {ko_count}ファイル")
        print(f"   - 乙号証: {otsu_count}ファイル")
        
        return migration_plan
    
    def _list_files_in_folder(self, folder_id: str) -> List[Dict]:
        """フォルダ内のファイル一覧を取得
        
        Args:
            folder_id: フォルダID
        
        Returns:
            ファイル一覧
        """
        try:
            query = f"'{folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                corpora='drive',
                driveId=gconfig.SHARED_DRIVE_ROOT_ID,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                fields='files(id, name, mimeType)',
                pageSize=1000
            ).execute()
            
            return results.get('files', [])
            
        except Exception as e:
            logger.error(f"ファイル一覧の取得に失敗しました: {e}")
            return []
    
    def _detect_evidence_type_from_filename(self, filename: str) -> str:
        """ファイル名から証拠種別を判定
        
        Args:
            filename: ファイル名
        
        Returns:
            'ko' または 'otsu'
        """
        # otsu, tmp_otsu で始まる場合は乙号証
        if filename.startswith('otsu') or filename.startswith('tmp_otsu'):
            return 'otsu'
        
        # それ以外はデフォルトで甲号証
        return 'ko'
    
    def _execute_migration(self, migration_plan: List[Dict]):
        """移行プランを実行
        
        Args:
            migration_plan: 移行プラン
        """
        print("\n🚀 ファイル移行を実行中...")
        
        for i, plan in enumerate(migration_plan, 1):
            print(f"\n[{i}/{len(migration_plan)}] {plan['file_name']}")
            print(f"   {plan['from_folder']} → {plan['to_folder']}")
            
            if self.dry_run:
                print("   (ドライラン: 実際には移行されません)")
                if 'rename' in plan:
                    print(f"   リネーム予定: {plan['file_name']} → {plan['rename']}")
                continue
            
            try:
                # ファイルを移動（親フォルダを変更）
                file_id = plan['file_id']
                from_folder_id = plan['from_folder_id']
                to_folder_id = plan['to_folder_id']
                
                # リネームが必要な場合
                if 'rename' in plan:
                    self.service.files().update(
                        fileId=file_id,
                        addParents=to_folder_id,
                        removeParents=from_folder_id,
                        body={'name': plan['rename']},
                        supportsAllDrives=True
                    ).execute()
                    print(f"   ✅ 移行完了（リネーム: {plan['rename']}）")
                else:
                    self.service.files().update(
                        fileId=file_id,
                        addParents=to_folder_id,
                        removeParents=from_folder_id,
                        supportsAllDrives=True
                    ).execute()
                    print("   ✅ 移行完了")
                
            except Exception as e:
                logger.error(f"ファイル移行に失敗しました: {plan['file_name']}, {e}")
                print(f"   ❌ 移行失敗: {e}")
    
    def _update_database(self, case_info: Dict, migration_plan: List[Dict]):
        """database.jsonを更新
        
        Args:
            case_info: 事件情報
            migration_plan: 移行プラン
        """
        print("\n📝 database.json を更新中...")
        
        if self.dry_run:
            print("   (ドライラン: 実際には更新されません)")
            return
        
        # TODO: database.jsonの更新ロジックを実装
        # - evidence_type フィールドを追加
        # - temp_id をリネーム (tmp_001 → tmp_ko_001)
        # - フォルダパスを更新
        
        print("   ⚠️  database.json の更新は手動で行ってください")


def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='既存フォルダ構成から階層的フォルダ構成への移行ツール'
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='実際に移行を実行（デフォルトはドライラン）'
    )
    parser.add_argument(
        '--case',
        type=str,
        help='移行する事件名（指定しない場合は全事件）'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("  フォルダ構成移行ツール")
    print("  旧構成 → 新階層的構成")
    print("="*70)
    
    if not args.execute:
        print("\n⚠️  ドライランモード（確認のみ、実際の変更は行われません）")
        print("   実際に移行する場合は --execute オプションを付けてください")
    else:
        print("\n🚨 実行モード（実際にファイルを移行します）")
        confirm = input("\n本当に実行しますか？ (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("\nキャンセルしました")
            return
    
    tool = FolderMigrationTool()
    
    # 事件一覧を取得
    cases = tool.case_manager.detect_cases(use_cache=False)
    
    if not cases:
        print("\n❌ 事件が見つかりませんでした")
        return
    
    # 特定の事件のみ移行する場合
    if args.case:
        cases = [c for c in cases if c['case_name'] == args.case]
        if not cases:
            print(f"\n❌ 事件 '{args.case}' が見つかりませんでした")
            return
    
    print(f"\n📁 移行対象: {len(cases)}件の事件")
    
    # 各事件を移行
    success_count = 0
    for case in cases:
        if tool.migrate_case(case, dry_run=not args.execute):
            success_count += 1
    
    print("\n" + "="*70)
    print(f"  移行結果: {success_count}/{len(cases)}件 成功")
    print("="*70)


if __name__ == "__main__":
    main()

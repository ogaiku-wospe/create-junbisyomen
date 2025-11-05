#!/usr/bin/env python3
"""
データベースクリーンアップユーティリティ

重複エントリの検出とマージを行います。
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class DatabaseCleanup:
    """データベースクリーンアップクラス"""
    
    def __init__(self, database_path: str):
        """初期化
        
        Args:
            database_path: database.jsonのパス
        """
        self.database_path = Path(database_path)
        self.database = self._load_database()
    
    def _load_database(self) -> Dict:
        """データベースをロード"""
        if not self.database_path.exists():
            logger.error(f"❌ データベースが見つかりません: {self.database_path}")
            return {"evidence": []}
        
        with open(self.database_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_database(self, backup: bool = True) -> None:
        """データベースを保存
        
        Args:
            backup: バックアップを作成するか
        """
        # バックアップを作成
        if backup:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.database_path.parent / f"database_backup_{timestamp}.json"
            
            with open(self.database_path, 'r', encoding='utf-8') as f:
                backup_data = f.read()
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(backup_data)
            
            logger.info(f"💾 バックアップ作成: {backup_path}")
        
        # 保存
        with open(self.database_path, 'w', encoding='utf-8') as f:
            json.dump(self.database, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ データベース保存: {self.database_path}")
    
    def find_duplicates(self) -> List[List[Dict]]:
        """重複エントリを検出
        
        Returns:
            重複グループのリスト（各グループは重複するエントリのリスト）
        """
        evidence_list = self.database.get("evidence", [])
        
        # 識別子の組み合わせでグループ化
        groups = {}
        
        for idx, entry in enumerate(evidence_list):
            # 識別子の組み合わせを作成
            # temp_id, evidence_id, evidence_number のいずれかが一致したらグループ化
            identifiers = []
            
            if entry.get('temp_id'):
                identifiers.append(('temp_id', entry['temp_id']))
            if entry.get('evidence_id'):
                identifiers.append(('evidence_id', entry['evidence_id']))
            if entry.get('evidence_number'):
                identifiers.append(('evidence_number', entry['evidence_number']))
            
            # いずれかの識別子が既存のグループと一致するか確認
            matched_group = None
            for group_key in list(groups.keys()):
                for id_type, id_value in identifiers:
                    if (id_type, id_value) in group_key:
                        matched_group = group_key
                        break
                if matched_group:
                    break
            
            # 既存グループに追加または新規グループ作成
            if matched_group:
                groups[matched_group].append((idx, entry))
            else:
                # 新規グループのキーは識別子のタプル
                new_key = tuple(identifiers)
                groups[new_key] = [(idx, entry)]
        
        # 重複（2つ以上のエントリがある）グループを抽出
        duplicates = []
        for key, entries in groups.items():
            if len(entries) > 1:
                # 完全に同一のオブジェクトは除外（参照が異なる別オブジェクトのみカウント）
                unique_entries = []
                seen_ids = set()
                
                for idx, entry in entries:
                    # インデックスで一意性を判定
                    if idx not in seen_ids:
                        unique_entries.append(entry)
                        seen_ids.add(idx)
                
                if len(unique_entries) > 1:
                    duplicates.append(unique_entries)
        
        return duplicates
    
    def analyze_duplicates(self) -> None:
        """重複エントリを分析して表示"""
        duplicates = self.find_duplicates()
        
        if not duplicates:
            logger.info("✅ 重複エントリは見つかりませんでした")
            return
        
        logger.info(f"\n⚠️  {len(duplicates)}個の重複グループが見つかりました\n")
        
        for i, group in enumerate(duplicates, 1):
            logger.info(f"【重複グループ {i}】")
            
            for j, entry in enumerate(group, 1):
                temp_id = entry.get('temp_id', 'なし')
                evidence_id = entry.get('evidence_id', 'なし')
                evidence_number = entry.get('evidence_number', 'なし')
                file_name = entry.get('file_name', 'なし')
                has_analysis = 'phase1_complete_analysis' in entry
                
                logger.info(f"  エントリ {j}:")
                logger.info(f"    temp_id: {temp_id}")
                logger.info(f"    evidence_id: {evidence_id}")
                logger.info(f"    evidence_number: {evidence_number}")
                logger.info(f"    file_name: {file_name}")
                logger.info(f"    分析完了: {'✅' if has_analysis else '❌'}")
            
            logger.info("")
    
    def merge_duplicates(self, dry_run: bool = True) -> None:
        """重複エントリをマージ
        
        Args:
            dry_run: True の場合は実際には変更せず、変更内容のみ表示
        """
        duplicates = self.find_duplicates()
        
        if not duplicates:
            logger.info("✅ 重複エントリは見つかりませんでした")
            return
        
        logger.info(f"\n🔧 {len(duplicates)}個の重複グループをマージします\n")
        
        evidence_list = self.database.get("evidence", [])
        indices_to_remove = set()
        
        for group in duplicates:
            # 分析完了済みのエントリを優先
            analyzed = [e for e in group if 'phase1_complete_analysis' in e]
            unanalyzed = [e for e in group if 'phase1_complete_analysis' not in e]
            
            if analyzed:
                # 分析完了済みエントリが存在する場合
                primary = analyzed[0]  # 最初の分析完了エントリを使用
                
                # temp_idを未分析エントリから取得（もしあれば）
                for unanalyzed_entry in unanalyzed:
                    if unanalyzed_entry.get('temp_id') and not primary.get('temp_id'):
                        primary['temp_id'] = unanalyzed_entry['temp_id']
                    if unanalyzed_entry.get('temp_number') and not primary.get('temp_number'):
                        primary['temp_number'] = unanalyzed_entry['temp_number']
                
                # 削除対象のインデックスを記録
                for entry in group:
                    if entry is not primary:
                        try:
                            idx = evidence_list.index(entry)
                            indices_to_remove.add(idx)
                        except ValueError:
                            pass
                
                logger.info(f"✅ マージ: {primary.get('evidence_id', primary.get('temp_id'))}")
                logger.info(f"   保持: {primary.get('file_name')}")
                logger.info(f"   削除: {len(group) - 1}個のエントリ")
            else:
                # すべて未分析の場合は最初のエントリを保持
                primary = group[0]
                
                for entry in group[1:]:
                    try:
                        idx = evidence_list.index(entry)
                        indices_to_remove.add(idx)
                    except ValueError:
                        pass
                
                logger.info(f"⚠️  マージ（未分析）: {primary.get('temp_id', primary.get('evidence_id'))}")
        
        # 削除を実行（dry_runでない場合）
        if not dry_run:
            # インデックスを降順にソートして削除（インデックスのずれを防ぐ）
            for idx in sorted(indices_to_remove, reverse=True):
                del evidence_list[idx]
            
            self.database["evidence"] = evidence_list
            self._save_database(backup=True)
            
            logger.info(f"\n✅ {len(indices_to_remove)}個のエントリを削除しました")
            logger.info(f"   残り: {len(evidence_list)}個のエントリ")
        else:
            logger.info(f"\n💡 ドライラン完了（実際の変更は行われていません）")
            logger.info(f"   実行する場合は dry_run=False で実行してください")


def main():
    """メイン処理"""
    import argparse
    
    parser = argparse.ArgumentParser(description="データベースクリーンアップユーティリティ")
    parser.add_argument("database", help="database.jsonのパス")
    parser.add_argument("--analyze", action="store_true", help="重複を分析して表示")
    parser.add_argument("--merge", action="store_true", help="重複をマージ")
    parser.add_argument("--execute", action="store_true", help="実際に変更を実行（デフォルトはドライラン）")
    
    args = parser.parse_args()
    
    cleanup = DatabaseCleanup(args.database)
    
    if args.analyze:
        cleanup.analyze_duplicates()
    
    if args.merge:
        dry_run = not args.execute
        cleanup.merge_duplicates(dry_run=dry_run)
    
    if not args.analyze and not args.merge:
        parser.print_help()


if __name__ == "__main__":
    main()

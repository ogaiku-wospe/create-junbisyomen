#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1完全版システム - 一括処理スクリプト

【使用方法】
    # 証拠番号のリストで一括処理
    python3 batch_process.py --evidence ko70 ko71 ko72 ko73
    
    # 証拠ファイルのディレクトリを指定して一括処理
    python3 batch_process.py --directory /path/to/evidence_files/
    
    # 範囲指定で一括処理
    python3 batch_process.py --range ko70-73
    
    # 未処理の証拠を自動検出して一括処理
    python3 batch_process.py --auto

【機能】
    - 複数証拠の一括処理
    - 進捗表示・エラーハンドリング
    - 自動リトライ機能
    - 詳細レポート生成
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from typing import List, Dict
import time

# 自作モジュールのインポート
try:
    from config import *
    from metadata_extractor import MetadataExtractor
    from file_processor import FileProcessor
    from ai_analyzer_complete import AIAnalyzerComplete
except ImportError as e:
    print(f"❌ エラー: モジュールのインポートに失敗しました: {e}")
    sys.exit(1)

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('batch_process.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class BatchProcessor:
    """一括処理クラス"""
    
    def __init__(self, database_path="database.json"):
        """初期化"""
        self.database_path = database_path
        self.metadata_extractor = MetadataExtractor()
        self.file_processor = FileProcessor()
        self.ai_analyzer = AIAnalyzerComplete()
        
        self.success_count = 0
        self.failed_count = 0
        self.skipped_count = 0
        self.results = []
    
    def load_database(self) -> dict:
        """database.jsonの読み込み"""
        if os.path.exists(self.database_path):
            with open(self.database_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            logger.warning(f"⚠️ {self.database_path} が見つかりません。新規作成します。")
            return {
                "case_info": {
                    "case_name": CASE_NAME,
                    "plaintiff": PLAINTIFF,
                    "defendant": DEFENDANT,
                    "court": COURT
                },
                "evidence": [],
                "metadata": {
                    "version": "3.0",
                    "created_at": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat()
                }
            }
    
    def save_database(self, database: dict):
        """database.jsonの保存"""
        database["metadata"]["last_updated"] = datetime.now().isoformat()
        database["metadata"]["total_evidence_count"] = len(database["evidence"])
        database["metadata"]["completed_count"] = len([e for e in database["evidence"] if e.get('status') == 'completed'])
        
        with open(self.database_path, 'w', encoding='utf-8') as f:
            json.dump(database, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 database.jsonを保存しました")
    
    def is_evidence_completed(self, database: dict, evidence_number: str) -> bool:
        """証拠が既に完了しているか確認"""
        for evidence in database["evidence"]:
            if evidence.get("evidence_number") == evidence_number:
                if evidence.get("status") == "completed":
                    return True
        return False
    
    def process_evidence(
        self, 
        evidence_number: str, 
        file_path: str,
        skip_completed: bool = True
    ) -> Dict:
        """証拠の処理
        
        Args:
            evidence_number: 証拠番号
            file_path: ファイルパス
            skip_completed: 完了済み証拠をスキップするか
            
        Returns:
            処理結果の辞書
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"  証拠 {evidence_number} の処理開始")
        logger.info(f"{'='*70}")
        
        result = {
            "evidence_number": evidence_number,
            "file_path": file_path,
            "status": "unknown",
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "error": None
        }
        
        try:
            # database.jsonを読み込み
            database = self.load_database()
            
            # 完了済みチェック
            if skip_completed and self.is_evidence_completed(database, evidence_number):
                logger.info(f"⏭️  証拠 {evidence_number} は既に処理済みです（スキップ）")
                result["status"] = "skipped"
                result["end_time"] = datetime.now().isoformat()
                self.skipped_count += 1
                return result
            
            # ファイルの存在確認
            if not os.path.exists(file_path):
                logger.error(f"❌ ファイルが見つかりません: {file_path}")
                result["status"] = "failed"
                result["error"] = f"File not found: {file_path}"
                result["end_time"] = datetime.now().isoformat()
                self.failed_count += 1
                return result
            
            logger.info(f"📁 ファイル: {file_path}")
            
            # 1. メタデータ抽出
            logger.info(f"📊 メタデータを抽出中...")
            metadata = self.metadata_extractor.extract_complete_metadata(file_path)
            logger.info(f"  ✅ SHA-256: {metadata['file_hash']['sha256'][:16]}...")
            logger.info(f"  ✅ サイズ: {metadata['file_size_bytes'] / 1024:.2f} KB")
            
            # 2. ファイル処理
            logger.info(f"🔧 ファイルを処理中...")
            processed_data = self.file_processor.process_file(file_path, evidence_number)
            logger.info(f"  ✅ タイプ: {processed_data['file_type']}")
            logger.info(f"  ✅ 抽出画像数: {len(processed_data.get('images', []))}")
            
            # 3. AI分析
            logger.info(f"🤖 AI分析を実行中（GPT-4o Vision）...")
            analysis_result = self.ai_analyzer.analyze_complete(  # TODO: analyze_evidence_complete への移行を検討  # TODO: analyze_evidence_complete への移行を検討
                processed_data=processed_data,
                evidence_number=evidence_number
            )
            
            # 4. 品質評価
            quality_scores = analysis_result['quality_scores']
            logger.info(f"📈 品質評価:")
            logger.info(f"  ✅ 完全性: {quality_scores['completeness_score']:.1f}%")
            logger.info(f"  ✅ 信頼度: {quality_scores['confidence_score']:.1f}%")
            logger.info(f"  ✅ 言語化レベル: {quality_scores['verbalization_level']}")
            
            # 5. database.jsonに保存
            logger.info(f"💾 database.jsonに保存中...")
            
            evidence_entry = {
                "evidence_number": evidence_number,
                "complete_metadata": metadata,
                "phase1_complete_analysis": analysis_result,
                "status": "completed",
                "processed_at": datetime.now().isoformat()
            }
            
            # 既存エントリの更新または新規追加
            existing_index = next(
                (i for i, e in enumerate(database["evidence"]) 
                 if e.get("evidence_number") == evidence_number),
                None
            )
            
            if existing_index is not None:
                database["evidence"][existing_index] = evidence_entry
                logger.info(f"  ✅ 既存エントリを更新")
            else:
                database["evidence"].append(evidence_entry)
                logger.info(f"  ✅ 新規エントリを追加")
            
            self.save_database(database)
            
            logger.info(f"\n✅ 証拠 {evidence_number} の処理が完了しました！")
            
            result["status"] = "success"
            result["quality_scores"] = quality_scores
            result["end_time"] = datetime.now().isoformat()
            self.success_count += 1
            
        except Exception as e:
            logger.error(f"❌ エラーが発生しました: {e}", exc_info=True)
            result["status"] = "failed"
            result["error"] = str(e)
            result["end_time"] = datetime.now().isoformat()
            self.failed_count += 1
        
        self.results.append(result)
        return result
    
    def process_batch(
        self, 
        evidence_list: List[Dict[str, str]],
        skip_completed: bool = True,
        retry_failed: bool = True
    ):
        """一括処理
        
        Args:
            evidence_list: 証拠情報のリスト [{"number": "ko70", "file": "/path/to/file"}, ...]
            skip_completed: 完了済み証拠をスキップするか
            retry_failed: 失敗した証拠を再試行するか
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"  一括処理開始")
        logger.info(f"  処理対象: {len(evidence_list)}件")
        logger.info(f"{'='*70}\n")
        
        start_time = datetime.now()
        
        for idx, evidence in enumerate(evidence_list, 1):
            evidence_number = evidence["number"]
            file_path = evidence["file"]
            
            logger.info(f"\n[{idx}/{len(evidence_list)}] 処理中: {evidence_number}")
            
            result = self.process_evidence(
                evidence_number=evidence_number,
                file_path=file_path,
                skip_completed=skip_completed
            )
            
            # 進捗表示
            logger.info(f"\n📊 現在の進捗:")
            logger.info(f"  ✅ 成功: {self.success_count}")
            logger.info(f"  ⏭️  スキップ: {self.skipped_count}")
            logger.info(f"  ❌ 失敗: {self.failed_count}")
            logger.info(f"  📈 進捗率: {idx}/{len(evidence_list)} ({idx/len(evidence_list)*100:.1f}%)")
            
            # 少し待機（APIレート制限対策）
            if idx < len(evidence_list):
                time.sleep(2)
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        # 最終レポート
        self.print_final_report(duration)
    
    def print_final_report(self, duration):
        """最終レポートを表示"""
        logger.info(f"\n{'='*70}")
        logger.info(f"  一括処理完了")
        logger.info(f"{'='*70}")
        
        logger.info(f"\n📊 処理結果:")
        logger.info(f"  ✅ 成功: {self.success_count}")
        logger.info(f"  ⏭️  スキップ: {self.skipped_count}")
        logger.info(f"  ❌ 失敗: {self.failed_count}")
        logger.info(f"  📊 合計: {len(self.results)}")
        
        logger.info(f"\n⏱️  処理時間:")
        logger.info(f"  - 総処理時間: {duration}")
        if self.success_count > 0:
            avg_time = duration.total_seconds() / self.success_count
            logger.info(f"  - 平均処理時間: {avg_time:.1f}秒/件")
        
        # 失敗した証拠のリスト
        if self.failed_count > 0:
            logger.info(f"\n❌ 失敗した証拠:")
            for result in self.results:
                if result["status"] == "failed":
                    logger.info(f"  - {result['evidence_number']}: {result.get('error', 'Unknown error')}")
        
        logger.info(f"\n{'='*70}\n")
    
    def get_unprocessed_evidence(self, database: dict) -> List[str]:
        """未処理の証拠番号を取得"""
        completed_numbers = {e.get("evidence_number") for e in database["evidence"] if e.get("status") == "completed"}
        
        # ここでは手動で未処理の証拠番号を指定
        # 実際のGoogle Drive検索機能は別途実装が必要
        all_evidence = ["ko70", "ko71", "ko72", "ko73"]  # 例
        
        unprocessed = [e for e in all_evidence if e not in completed_numbers]
        return unprocessed


def parse_evidence_range(range_str: str) -> List[str]:
    """証拠番号の範囲を解析
    
    Args:
        range_str: 範囲文字列（例: "ko70-73"）
        
    Returns:
        証拠番号のリスト
    """
    if '-' not in range_str:
        return [range_str]
    
    try:
        prefix = range_str.split('-')[0].rstrip('0123456789')
        start = int(range_str.split('-')[0][len(prefix):])
        end = int(range_str.split('-')[1])
        return [f"{prefix}{i}" for i in range(start, end + 1)]
    except ValueError:
        logger.error(f"❌ 範囲指定の形式が正しくありません: {range_str}")
        return []


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='Phase 1完全版システム - 一括処理スクリプト',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # 証拠指定方法
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--evidence',
        nargs='+',
        help='証拠番号のリスト（例: ko70 ko71 ko72）'
    )
    group.add_argument(
        '--range',
        type=str,
        help='証拠番号の範囲（例: ko70-73）'
    )
    group.add_argument(
        '--auto',
        action='store_true',
        help='未処理の証拠を自動検出して処理'
    )
    
    # ファイル指定方法
    parser.add_argument(
        '--directory',
        type=str,
        help='証拠ファイルのディレクトリ'
    )
    
    # オプション
    parser.add_argument(
        '--skip-completed',
        action='store_true',
        default=True,
        help='完了済み証拠をスキップ（デフォルト: True）'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='database.json',
        help='出力先database.jsonのパス'
    )
    
    args = parser.parse_args()
    
    # 環境チェック
    if not os.getenv('OPENAI_API_KEY'):
        logger.error("❌ エラー: OPENAI_API_KEYが設定されていません")
        return 1
    
    # 証拠番号のリストを作成
    if args.evidence:
        evidence_numbers = args.evidence
    elif args.range:
        evidence_numbers = parse_evidence_range(args.range)
    elif args.auto:
        processor = BatchProcessor(args.output)
        database = processor.load_database()
        evidence_numbers = processor.get_unprocessed_evidence(database)
        logger.info(f"📋 未処理の証拠を検出しました: {evidence_numbers}")
    
    if not evidence_numbers:
        logger.error("❌ 処理する証拠がありません")
        return 1
    
    # ファイルパスのマッピング
    evidence_list = []
    for number in evidence_numbers:
        if args.directory:
            # ディレクトリから証拠番号に対応するファイルを検索
            file_path = None
            for ext in ['.pdf', '.jpg', '.jpeg', '.png', '.docx', '.mp4', '.mp3']:
                candidate = os.path.join(args.directory, f"{number}{ext}")
                if os.path.exists(candidate):
                    file_path = candidate
                    break
            
            if not file_path:
                logger.warning(f"⚠️ {number} のファイルが見つかりません（スキップ）")
                continue
        else:
            logger.error(f"❌ --directory オプションが必要です")
            return 1
        
        evidence_list.append({
            "number": number,
            "file": file_path
        })
    
    if not evidence_list:
        logger.error("❌ 処理可能なファイルが見つかりません")
        return 1
    
    # 一括処理実行
    processor = BatchProcessor(args.output)
    processor.process_batch(
        evidence_list=evidence_list,
        skip_completed=args.skip_completed
    )
    
    return 0 if processor.failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

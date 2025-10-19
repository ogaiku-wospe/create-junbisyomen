#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1完全版システム - コマンドライン実行スクリプト
提起前_名誉毀損等損害賠償請求事件 証拠分析システム

使用方法:
    # 単一証拠の分析
    python phase1_cli.py ko70
    
    # 複数証拠の分析
    python phase1_cli.py ko70 ko71 ko72 ko73
    
    # 範囲指定（未実装）
    python phase1_cli.py --range ko70-73
    
    # ファイル直接指定
    python phase1_cli.py --file /path/to/evidence.pdf --number ko70
    
    # 詳細オプション
    python phase1_cli.py ko70 --verbose --output custom_database.json
"""

import argparse
import os
import sys
import json
import logging
from datetime import datetime
from typing import List

# 自作モジュールのインポート
try:
    from config import *
    from metadata_extractor import MetadataExtractor
    from file_processor import FileProcessor
    from ai_analyzer_complete import AIAnalyzerComplete
except ImportError as e:
    print(f"❌ エラー: モジュールのインポートに失敗しました: {e}")
    sys.exit(1)


def setup_logging(verbose: bool = False):
    """ロギング設定"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler('phase1_cli.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )


def load_database(path: str) -> dict:
    """database.jsonの読み込み"""
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {
            "case_info": {
                "case_name": "提起前_名誉毀損等損害賠償請求事件",
                "plaintiff": "小原瞳（しろくまクラフト）",
                "defendant": "石村まゆか（SUB×MISSION）",
                "court": "東京地方裁判所"
            },
            "evidence": [],
            "metadata": {
                "version": "3.0",
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
        }


def save_database(database: dict, path: str):
    """database.jsonの保存"""
    database["metadata"]["last_updated"] = datetime.now().isoformat()
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(database, f, ensure_ascii=False, indent=2)


def process_evidence(
    evidence_number: str,
    file_path: str = None,
    database_path: str = "database.json"
) -> bool:
    """証拠の処理
    
    Args:
        evidence_number: 証拠番号（例: ko70）
        file_path: ファイルパス（指定しない場合はGoogle Driveから検索）
        database_path: database.jsonのパス
        
    Returns:
        処理成功: True, 失敗: False
    """
    logger = logging.getLogger(__name__)
    logger.info(f"\n{'='*60}")
    logger.info(f"  証拠 {evidence_number} の処理開始")
    logger.info(f"{'='*60}")
    
    try:
        # モジュール初期化
        metadata_extractor = MetadataExtractor()
        file_processor = FileProcessor()
        ai_analyzer = AIAnalyzerComplete()
        
        # 1. ファイルパス取得
        if not file_path:
            logger.info(f"🔍 Google Driveでファイルを検索中...")
            # ※Google Drive検索機能は別途実装が必要
            logger.error("❌ ファイルパスが指定されていません")
            logger.info("💡 --file オプションでファイルパスを指定してください")
            return False
        
        if not os.path.exists(file_path):
            logger.error(f"❌ ファイルが見つかりません: {file_path}")
            return False
        
        logger.info(f"📁 ファイル: {file_path}")
        
        # 2. メタデータ抽出
        logger.info(f"📊 メタデータを抽出中...")
        metadata = metadata_extractor.extract_complete_metadata(file_path)
        logger.info(f"  ✅ SHA-256: {metadata['file_hash']['sha256'][:16]}...")
        logger.info(f"  ✅ サイズ: {metadata['file_size_bytes'] / 1024:.2f} KB")
        
        # 3. ファイル処理
        logger.info(f"🔧 ファイルを処理中...")
        processed_data = file_processor.process_file(file_path, evidence_number)
        logger.info(f"  ✅ タイプ: {processed_data['file_type']}")
        logger.info(f"  ✅ 抽出画像数: {len(processed_data.get('images', []))}")
        
        # 4. AI分析
        logger.info(f"🤖 AI分析を実行中（GPT-4o Vision）...")
        analysis_result = ai_analyzer.analyze_complete(  # TODO: analyze_evidence_complete への移行を検討  # TODO: analyze_evidence_complete への移行を検討
            processed_data=processed_data,
            evidence_number=evidence_number
        )
        
        # 5. 品質評価
        logger.info(f"📈 品質評価:")
        logger.info(f"  ✅ 完全性: {analysis_result['quality_scores']['completeness_score']:.1f}%")
        logger.info(f"  ✅ 信頼度: {analysis_result['quality_scores']['confidence_score']:.1f}%")
        logger.info(f"  ✅ 言語化レベル: {analysis_result['quality_scores']['verbalization_level']}")
        
        # 6. database.jsonに保存
        logger.info(f"💾 database.jsonに保存中...")
        database = load_database(database_path)
        
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
        
        save_database(database, database_path)
        
        logger.info(f"\n✅ 証拠 {evidence_number} の処理が完了しました！")
        return True
        
    except Exception as e:
        logger.error(f"❌ エラーが発生しました: {e}", exc_info=True)
        return False


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='Phase 1完全版システム - コマンドライン実行',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用例:
  # 単一証拠の分析（ファイルパス指定）
  python phase1_cli.py ko70 --file /path/to/ko70.pdf
  
  # 複数証拠の分析
  python phase1_cli.py ko70 ko71 ko72 --file-dir /path/to/evidence_files/
  
  # 詳細ログ出力
  python phase1_cli.py ko70 --file /path/to/ko70.pdf --verbose
  
  # カスタムdatabase.json
  python phase1_cli.py ko70 --file /path/to/ko70.pdf --output custom_db.json
        '''
    )
    
    parser.add_argument(
        'evidence_numbers',
        nargs='+',
        help='証拠番号（例: ko70 ko71 ko72）'
    )
    
    parser.add_argument(
        '--file',
        type=str,
        help='証拠ファイルのパス（単一証拠の場合）'
    )
    
    parser.add_argument(
        '--file-dir',
        type=str,
        help='証拠ファイルのディレクトリ（複数証拠の場合）'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='database.json',
        help='出力先database.jsonのパス（デフォルト: database.json）'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='詳細ログを出力'
    )
    
    args = parser.parse_args()
    
    # ロギング設定
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # 環境チェック
    if not os.getenv('OPENAI_API_KEY'):
        logger.error("❌ エラー: OPENAI_API_KEYが設定されていません")
        logger.info("export OPENAI_API_KEY='sk-your-api-key' を実行してください")
        return 1
    
    # 処理開始
    logger.info("="*60)
    logger.info("  Phase 1完全版システム - CLI実行")
    logger.info("="*60)
    
    success_count = 0
    failed_count = 0
    
    for evidence_number in args.evidence_numbers:
        # ファイルパスの決定
        if args.file:
            file_path = args.file
        elif args.file_dir:
            # ディレクトリから証拠番号に対応するファイルを検索
            file_path = None
            for ext in ['.pdf', '.jpg', '.jpeg', '.png', '.docx', '.mp4', '.mp3']:
                candidate = os.path.join(args.file_dir, f"{evidence_number}{ext}")
                if os.path.exists(candidate):
                    file_path = candidate
                    break
            if not file_path:
                logger.warning(f"⚠️ {evidence_number} のファイルが見つかりません")
                failed_count += 1
                continue
        else:
            logger.error("❌ --file または --file-dir オプションが必要です")
            return 1
        
        # 処理実行
        if process_evidence(evidence_number, file_path, args.output):
            success_count += 1
        else:
            failed_count += 1
    
    # 結果サマリー
    logger.info("\n" + "="*60)
    logger.info("  処理結果サマリー")
    logger.info("="*60)
    logger.info(f"✅ 成功: {success_count}")
    logger.info(f"❌ 失敗: {failed_count}")
    logger.info(f"📊 合計: {success_count + failed_count}")
    logger.info("="*60)
    
    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

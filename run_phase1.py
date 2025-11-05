#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1完全版システム - 対話的実行スクリプト
提起前_名誉毀損等損害賠償請求事件 証拠分析システム

使用方法:
    python run_phase1.py

機能:
    - 証拠番号の指定（例: ko70, ko71-73）
    - 個別ファイル分析
    - 完全自動実行
    - 進捗表示・品質評価
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import List, Optional

# プロジェクトルートをPythonパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 自作モジュールのインポート
try:
    from global_config import *
    from src.metadata_extractor import MetadataExtractor
    from src.file_processor import FileProcessor
    from src.ai_analyzer_complete import AIAnalyzerComplete
except ImportError as e:
    print(f"❌ エラー: モジュールのインポートに失敗しました: {e}")
    print("現在のディレクトリを確認してください。")
    sys.exit(1)

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('phase1_complete.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class Phase1Runner:
    """Phase 1完全版実行クラス"""
    
    def __init__(self):
        """初期化"""
        self.metadata_extractor = MetadataExtractor()
        self.file_processor = FileProcessor()
        self.ai_analyzer = AIAnalyzerComplete()
        self.database_path = "database.json"
        
    def load_database(self) -> dict:
        """database.jsonの読み込み"""
        if os.path.exists(self.database_path):
            with open(self.database_path, 'r', encoding='utf-8') as f:
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
    
    def save_database(self, database: dict):
        """database.jsonの保存"""
        database["metadata"]["last_updated"] = datetime.now().isoformat()
        with open(self.database_path, 'w', encoding='utf-8') as f:
            json.dump(database, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ database.jsonを保存しました")
    
    def display_menu(self):
        """メニュー表示"""
        print("\n" + "="*60)
        print("  Phase 1完全版システム - 証拠分析")
        print("  提起前_名誉毀損等損害賠償請求事件")
        print("="*60)
        print("\n【実行モード】")
        print("  1. 証拠番号を指定して分析（例: ko70）")
        print("  2. 範囲指定して分析（例: ko70-73）")
        print("  3. 個別ファイルを分析（Google Drive URL指定）")
        print("  4. 未処理の証拠を自動検索・分析")
        print("  5. database.jsonの状態確認")
        print("  6. 終了")
        print("-"*60)
    
    def get_evidence_number_input(self) -> Optional[List[str]]:
        """証拠番号の入力取得"""
        user_input = input("\n証拠番号を入力してください（例: ko70 または ko70-73）: ").strip()
        
        if not user_input:
            return None
        
        # 範囲指定の処理（例: ko70-73）
        if '-' in user_input and user_input.count('-') == 1:
            try:
                prefix = user_input.split('-')[0].rstrip('0123456789')
                start = int(user_input.split('-')[0][len(prefix):])
                end = int(user_input.split('-')[1])
                return [f"{prefix}{i}" for i in range(start, end + 1)]
            except ValueError:
                logger.error("❌ 範囲指定の形式が正しくありません")
                return None
        else:
            # 単一証拠番号
            return [user_input]
    
    def process_evidence(self, evidence_number: str) -> bool:
        """証拠の処理（完全版）
        
        Args:
            evidence_number: 証拠番号（例: ko70）
            
        Returns:
            処理成功: True, 失敗: False
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"  証拠 {evidence_number} の処理開始")
        logger.info(f"{'='*60}")
        
        try:
            # 1. Google Driveからファイル検索
            logger.info(f"🔍 Google Driveでファイルを検索中...")
            # ※実際のGoogle Drive検索機能は別途実装が必要
            # ここでは仮のファイルパスを使用
            file_path = f"/tmp/{evidence_number}_sample.pdf"
            
            if not os.path.exists(file_path):
                logger.warning(f"⚠️ ファイルが見つかりません: {file_path}")
                logger.info("📝 Google Driveから手動でダウンロードしてください")
                return False
            
            # 2. メタデータ抽出
            logger.info(f"📊 メタデータを抽出中...")
            metadata = self.metadata_extractor.extract_complete_metadata(file_path)
            logger.info(f"  - ファイルハッシュ: {metadata['file_hash']['sha256'][:16]}...")
            logger.info(f"  - ファイルサイズ: {metadata['file_size_bytes'] / 1024:.2f} KB")
            
            # 3. ファイル処理（画像抽出、テキスト抽出等）
            logger.info(f"🔧 ファイルを処理中...")
            processed_data = self.file_processor.process_file(file_path, evidence_number)
            logger.info(f"  - 処理タイプ: {processed_data['file_type']}")
            logger.info(f"  - 抽出画像数: {len(processed_data.get('images', []))}")
            
            # 4. AI分析（GPT-4o Vision）
            logger.info(f"🤖 AI分析を実行中（GPT-4o Vision）...")
            analysis_result = self.ai_analyzer.analyze_complete(  # TODO: analyze_evidence_complete への移行を検討  # TODO: analyze_evidence_complete への移行を検討  # TODO: analyze_evidence_complete への移行を検討  # TODO: analyze_evidence_complete への移行を検討
                processed_data=processed_data,
                evidence_number=evidence_number
            )
            
            # 5. 品質評価
            logger.info(f"📈 品質評価:")
            logger.info(f"  - 完全性スコア: {analysis_result['quality_scores']['completeness_score']:.1f}%")
            logger.info(f"  - 信頼度スコア: {analysis_result['quality_scores']['confidence_score']:.1f}%")
            logger.info(f"  - 言語化レベル: {analysis_result['quality_scores']['verbalization_level']}")
            
            # 6. database.jsonに追加
            logger.info(f"💾 database.jsonに保存中...")
            database = self.load_database()
            
            evidence_entry = {
                "evidence_number": evidence_number,
                "complete_metadata": metadata,
                "phase1_complete_analysis": analysis_result,
                "status": "completed",
                "processed_at": datetime.now().isoformat()
            }
            
            # 既存のエントリを更新、または新規追加
            existing_index = next(
                (i for i, e in enumerate(database["evidence"]) 
                 if e.get("evidence_number") == evidence_number),
                None
            )
            
            if existing_index is not None:
                database["evidence"][existing_index] = evidence_entry
                logger.info(f"  ✅ 既存エントリを更新しました")
            else:
                database["evidence"].append(evidence_entry)
                logger.info(f"  ✅ 新規エントリを追加しました")
            
            self.save_database(database)
            
            logger.info(f"\n✅ 証拠 {evidence_number} の処理が完了しました！")
            return True
            
        except Exception as e:
            logger.error(f"❌ エラーが発生しました: {e}", exc_info=True)
            return False
    
    def show_database_status(self):
        """database.jsonの状態表示"""
        database = self.load_database()
        
        print("\n" + "="*60)
        print("  database.json 状態確認")
        print("="*60)
        
        print(f"\n📁 事件情報:")
        print(f"  - 事件名: {database['case_info']['case_name']}")
        print(f"  - 原告: {database['case_info']['plaintiff']}")
        print(f"  - 被告: {database['case_info']['defendant']}")
        
        print(f"\n📊 証拠統計:")
        print(f"  - 総証拠数: {len(database['evidence'])}")
        
        completed = [e for e in database['evidence'] if e.get('status') == 'completed']
        print(f"  - 完了: {len(completed)}")
        
        in_progress = [e for e in database['evidence'] if e.get('status') == 'in_progress']
        print(f"  - 処理中: {len(in_progress)}")
        
        print(f"\n📝 証拠一覧:")
        for evidence in database['evidence']:
            status_icon = "✅" if evidence.get('status') == 'completed' else "⏳"
            print(f"  {status_icon} {evidence.get('evidence_number', 'N/A')}")
        
        print("\n" + "="*60)
    
    def run(self):
        """メイン実行ループ"""
        while True:
            self.display_menu()
            choice = input("\n選択してください (1-6): ").strip()
            
            if choice == '1':
                # 証拠番号を指定して分析
                evidence_numbers = self.get_evidence_number_input()
                if evidence_numbers:
                    for evidence_number in evidence_numbers:
                        self.process_evidence(evidence_number)
                        
            elif choice == '2':
                # 範囲指定して分析
                evidence_numbers = self.get_evidence_number_input()
                if evidence_numbers:
                    print(f"\n📋 処理対象: {', '.join(evidence_numbers)}")
                    confirm = input("処理を開始しますか？ (y/n): ").strip().lower()
                    if confirm == 'y':
                        for evidence_number in evidence_numbers:
                            self.process_evidence(evidence_number)
                            
            elif choice == '3':
                # 個別ファイルを分析
                file_url = input("\nGoogle Drive URLを入力してください: ").strip()
                if file_url:
                    print("⚠️ この機能は実装中です")
                    
            elif choice == '4':
                # 未処理の証拠を自動検索・分析
                print("\n⚠️ この機能は実装中です")
                
            elif choice == '5':
                # database.jsonの状態確認
                self.show_database_status()
                
            elif choice == '6':
                # 終了
                print("\n👋 Phase 1完全版システムを終了します")
                break
                
            else:
                print("\n❌ 無効な選択です。1-6の番号を入力してください。")
            
            input("\nEnterキーを押して続行...")


def main():
    """メイン関数"""
    print("\n" + "="*60)
    print("  Phase 1完全版システム 起動中...")
    print("="*60)
    
    # 環境チェック
    if not os.getenv('OPENAI_API_KEY'):
        print("\n❌ エラー: OPENAI_API_KEYが設定されていません")
        print("export OPENAI_API_KEY='sk-your-api-key' を実行してください")
        return
    
    # Google認証チェック
    if not os.path.exists('credentials.json'):
        print("\n⚠️ 警告: credentials.jsonが見つかりません")
        print("Google Drive API機能が制限されます")
    
    # 実行
    runner = Phase1Runner()
    runner.run()


if __name__ == "__main__":
    main()

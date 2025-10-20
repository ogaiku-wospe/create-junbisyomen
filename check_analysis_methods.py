#!/usr/bin/env python3
"""
AI画像分析メソッドの確認ツール
- Vision APIの使用状況
- OCRフォールバックの使用状況
- 各エントリの分析成功/失敗状態
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

def load_database(db_path: str) -> Dict:
    """データベースを読み込む"""
    with open(db_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_methods(db: Dict) -> Dict:
    """分析メソッドの統計情報を生成"""
    stats = {
        "total": 0,
        "vision_api_attempted": 0,
        "vision_api_success": 0,
        "vision_api_failed": 0,
        "ocr_fallback_used": 0,
        "text_only": 0,
        "retry_used": 0,
        "by_file_type": defaultdict(lambda: {
            "total": 0,
            "vision_success": 0,
            "vision_failed": 0,
            "ocr_fallback": 0
        }),
        "failures": [],
        "ocr_quality": {
            "high": 0,  # >= 0.5
            "medium": 0,  # 0.3 - 0.5
            "low": 0,  # < 0.3
            "unknown": 0
        }
    }
    
    for evidence in db.get('evidence', []):
        if 'phase1_complete_analysis' not in evidence:
            continue
        
        stats["total"] += 1
        
        analysis = evidence['phase1_complete_analysis']
        ai_analysis = analysis.get('ai_analysis', {})
        
        # 分析メソッド情報を取得
        method_info = ai_analysis.get('_analysis_method', {})
        
        # ファイルタイプ
        file_type = analysis.get('file_processing_result', {}).get('file_type', 'unknown')
        
        # Vision API試行
        if method_info.get('vision_api_used', False):
            stats["vision_api_attempted"] += 1
            stats["by_file_type"][file_type]["total"] += 1
            
            if method_info.get('vision_api_success', False):
                stats["vision_api_success"] += 1
                stats["by_file_type"][file_type]["vision_success"] += 1
            else:
                stats["vision_api_failed"] += 1
                stats["by_file_type"][file_type]["vision_failed"] += 1
        
        # OCRフォールバック
        if method_info.get('ocr_fallback_used', False):
            stats["ocr_fallback_used"] += 1
            stats["by_file_type"][file_type]["ocr_fallback"] += 1
            
            # OCR品質
            ocr_quality = method_info.get('ocr_quality', {})
            if ocr_quality:
                score = ocr_quality.get('score', 0)
                if score >= 0.5:
                    stats["ocr_quality"]["high"] += 1
                elif score >= 0.3:
                    stats["ocr_quality"]["medium"] += 1
                else:
                    stats["ocr_quality"]["low"] += 1
            else:
                stats["ocr_quality"]["unknown"] += 1
        
        # テキストのみ分析
        if method_info.get('successful_method') == 'text_analysis':
            stats["text_only"] += 1
        
        # リトライ使用
        if ai_analysis.get('_retry_count', 0) > 0:
            stats["retry_used"] += 1
        
        # 失敗したエントリ
        verbalization_level = ai_analysis.get('verbalization_level', 0)
        if verbalization_level == 0:
            stats["failures"].append({
                "evidence_id": evidence.get('evidence_id', evidence.get('temp_id', 'unknown')),
                "filename": evidence.get('original_filename', 'unknown'),
                "file_type": file_type,
                "method_info": method_info,
                "raw_response": ai_analysis.get('raw_response', '')[:100]
            })
    
    return stats

def print_statistics(stats: Dict):
    """統計情報を表示"""
    print("=" * 80)
    print("AI画像分析メソッドの統計")
    print("=" * 80)
    print()
    
    # 全体統計
    print("【全体統計】")
    print(f"総証拠数: {stats['total']}")
    print()
    
    # Vision API統計
    print("【Vision API使用状況】")
    print(f"Vision API試行: {stats['vision_api_attempted']}件")
    print(f"  ├─ 成功: {stats['vision_api_success']}件 ({stats['vision_api_success']/stats['vision_api_attempted']*100:.1f}%)" if stats['vision_api_attempted'] > 0 else "  ├─ 成功: 0件")
    print(f"  ├─ 失敗: {stats['vision_api_failed']}件 ({stats['vision_api_failed']/stats['vision_api_attempted']*100:.1f}%)" if stats['vision_api_attempted'] > 0 else "  ├─ 失敗: 0件")
    print(f"  └─ リトライ使用: {stats['retry_used']}件")
    print()
    
    # OCRフォールバック統計
    print("【OCRフォールバック使用状況】")
    print(f"OCRフォールバック使用: {stats['ocr_fallback_used']}件")
    if stats['ocr_fallback_used'] > 0:
        print(f"  OCR品質分布:")
        print(f"    ├─ 高品質 (≥0.5): {stats['ocr_quality']['high']}件")
        print(f"    ├─ 中品質 (0.3-0.5): {stats['ocr_quality']['medium']}件")
        print(f"    ├─ 低品質 (<0.3): {stats['ocr_quality']['low']}件")
        print(f"    └─ 不明: {stats['ocr_quality']['unknown']}件")
    print()
    
    # ファイルタイプ別統計
    print("【ファイルタイプ別統計】")
    for file_type, type_stats in stats['by_file_type'].items():
        if type_stats['total'] > 0:
            print(f"{file_type}:")
            print(f"  総数: {type_stats['total']}")
            print(f"  Vision成功: {type_stats['vision_success']}件")
            print(f"  Vision失敗: {type_stats['vision_failed']}件")
            print(f"  OCRフォールバック: {type_stats['ocr_fallback']}件")
            print()
    
    # テキストのみ分析
    print("【その他の分析メソッド】")
    print(f"テキストのみ分析: {stats['text_only']}件")
    print()
    
    # 失敗エントリの詳細
    if stats['failures']:
        print("=" * 80)
        print("【失敗エントリの詳細】")
        print("=" * 80)
        print()
        
        for i, failure in enumerate(stats['failures'], 1):
            print(f"{i}. {failure['evidence_id']}")
            print(f"   ファイル名: {failure['filename']}")
            print(f"   ファイルタイプ: {failure['file_type']}")
            
            method_info = failure['method_info']
            print(f"   試行メソッド: {method_info.get('attempted_method', 'unknown')}")
            print(f"   成功メソッド: {method_info.get('successful_method', 'none')}")
            
            if method_info.get('vision_api_used'):
                print(f"   Vision API: {'✅ 成功' if method_info.get('vision_api_success') else '❌ 失敗'}")
                if not method_info.get('vision_api_success'):
                    print(f"   拒否理由: {method_info.get('rejection_reason', 'unknown')}")
            
            if method_info.get('ocr_fallback_used'):
                ocr_q = method_info.get('ocr_quality', {})
                if ocr_q:
                    print(f"   OCRフォールバック: 使用")
                    print(f"   OCR品質: {ocr_q.get('score', 0):.2f} ({'十分' if ocr_q.get('is_sufficient') else '不十分'})")
                else:
                    print(f"   OCRフォールバック: 使用（品質情報なし）")
            
            if failure['raw_response']:
                print(f"   応答: {failure['raw_response']}...")
            
            print()
    
    # 成功率サマリー
    print("=" * 80)
    print("【成功率サマリー】")
    print("=" * 80)
    success_count = stats['total'] - len(stats['failures'])
    success_rate = (success_count / stats['total'] * 100) if stats['total'] > 0 else 0
    
    print(f"成功: {success_count}/{stats['total']} ({success_rate:.1f}%)")
    print(f"失敗: {len(stats['failures'])}/{stats['total']} ({(len(stats['failures'])/stats['total']*100):.1f}%)")
    print()
    
    if stats['vision_api_attempted'] > 0:
        vision_success_rate = (stats['vision_api_success'] / stats['vision_api_attempted'] * 100)
        print(f"Vision API成功率: {stats['vision_api_success']}/{stats['vision_api_attempted']} ({vision_success_rate:.1f}%)")
        
        if stats['ocr_fallback_used'] > 0:
            print(f"OCRフォールバック率: {stats['ocr_fallback_used']}/{stats['vision_api_attempted']} ({(stats['ocr_fallback_used']/stats['vision_api_attempted']*100):.1f}%)")
    print()

def export_report(stats: Dict, output_path: str):
    """レポートをJSONファイルにエクスポート"""
    # defaultdictを通常のdictに変換
    exportable_stats = {
        **stats,
        "by_file_type": dict(stats["by_file_type"])
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(exportable_stats, f, ensure_ascii=False, indent=2)
    
    print(f"✅ レポートをエクスポートしました: {output_path}")
    print()

def main():
    """メイン関数"""
    # データベースパスの決定
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        # デフォルトパス（Google Driveからローカルに変更）
        db_path = "database.json"
        
        # ローカルに存在しない場合はエラー
        if not Path(db_path).exists():
            print("❌ エラー: database.jsonが見つかりません")
            print()
            print("使用方法:")
            print("  python check_analysis_methods.py [database.jsonのパス]")
            print()
            print("例:")
            print("  python check_analysis_methods.py database.json")
            print("  python check_analysis_methods.py ~/Library/CloudStorage/GoogleDrive-.../database.json")
            sys.exit(1)
    
    print(f"📂 データベース: {db_path}")
    print()
    
    try:
        # データベース読み込み
        db = load_database(db_path)
        
        # 分析メソッド統計を生成
        stats = analyze_methods(db)
        
        # 統計情報を表示
        print_statistics(stats)
        
        # レポートをエクスポート
        output_path = "analysis_method_report.json"
        export_report(stats, output_path)
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

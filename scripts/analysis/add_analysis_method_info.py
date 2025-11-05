#!/usr/bin/env python3
"""
既存のdatabase.jsonに分析メソッド情報を追加するツール
（過去に分析されたデータに対して推定情報を追加）
"""

import json
import sys
from pathlib import Path
from typing import Dict

def infer_analysis_method(evidence: Dict) -> Dict:
    """
    既存の分析結果から分析メソッドを推定
    """
    method_info = {
        "attempted_method": "unknown",
        "successful_method": "unknown",
        "vision_api_used": False,
        "vision_api_success": False,
        "vision_api_retry_count": 0,
        "ocr_fallback_used": False,
        "ocr_quality": None,
        "rejection_reason": None,
        "_inferred": True  # 推定情報であることを示すフラグ
    }
    
    if 'phase1_complete_analysis' not in evidence:
        return method_info
    
    analysis = evidence['phase1_complete_analysis']
    ai_analysis = analysis.get('ai_analysis', {})
    
    # 既に分析メソッド情報がある場合はそのまま返す
    if '_analysis_method' in ai_analysis:
        return ai_analysis['_analysis_method']
    
    # ファイルタイプを確認
    file_type = analysis.get('file_processing_result', {}).get('file_type', 'unknown')
    
    # 画像・PDF・文書の場合、Vision APIを試行したと推定
    if file_type in ['image', 'pdf', 'document']:
        method_info["vision_api_used"] = True
        method_info["attempted_method"] = "vision_api"
        
        # 分析結果を確認
        verbalization_level = ai_analysis.get('verbalization_level', 0)
        raw_response = ai_analysis.get('raw_response', '')
        
        # Vision API拒否を検出
        if verbalization_level == 0 and "I'm sorry" in raw_response and "assist" in raw_response:
            method_info["vision_api_success"] = False
            method_info["rejection_reason"] = "content_policy_rejection"
            method_info["ocr_fallback_used"] = True
            method_info["successful_method"] = "none"  # 最終的に失敗
            
            # OCR情報を取得
            ocr_info = None
            file_content = analysis.get('file_processing_result', {}).get('content', {})
            
            if 'ocr_text' in file_content:
                ocr_text = file_content.get('ocr_text', '')
                ocr_confidence = file_content.get('ocr_confidence', 0.0)
                ocr_info = {
                    "score": ocr_confidence,
                    "is_sufficient": ocr_confidence >= 0.3 or len(ocr_text) >= 50,
                    "details": {
                        "ocr_confidence": ocr_confidence,
                        "text_length": len(ocr_text)
                    }
                }
            elif 'ocr_results' in file_content and file_content['ocr_results']:
                ocr_result = file_content['ocr_results'][0]
                ocr_text = ocr_result.get('ocr_text', '')
                ocr_confidence = ocr_result.get('confidence', 0.0)
                ocr_info = {
                    "score": ocr_confidence,
                    "is_sufficient": ocr_confidence >= 0.3 or len(ocr_text) >= 50,
                    "details": {
                        "ocr_confidence": ocr_confidence,
                        "text_length": len(ocr_text)
                    }
                }
            
            method_info["ocr_quality"] = ocr_info
        else:
            # Vision APIで成功したと推定
            method_info["vision_api_success"] = True
            method_info["successful_method"] = "vision_api"
    else:
        # テキストベース分析
        method_info["attempted_method"] = "text_analysis"
        method_info["successful_method"] = "text_analysis"
    
    return method_info

def add_method_info_to_database(db_path: str, output_path: str = None):
    """
    データベースに分析メソッド情報を追加
    """
    # データベース読み込み
    with open(db_path, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    print(f"📂 データベース: {db_path}")
    print(f"証拠数: {len(db.get('evidence', []))}")
    print()
    
    added_count = 0
    already_exists_count = 0
    
    # 各証拠に分析メソッド情報を追加
    for evidence in db.get('evidence', []):
        if 'phase1_complete_analysis' not in evidence:
            continue
        
        analysis = evidence['phase1_complete_analysis']
        ai_analysis = analysis.get('ai_analysis', {})
        
        # 既に情報がある場合はスキップ
        if '_analysis_method' in ai_analysis:
            already_exists_count += 1
            continue
        
        # 分析メソッド情報を推定して追加
        method_info = infer_analysis_method(evidence)
        ai_analysis['_analysis_method'] = method_info
        added_count += 1
    
    print(f"✅ 分析メソッド情報を追加: {added_count}件")
    print(f"ℹ️  既に存在: {already_exists_count}件")
    print()
    
    # 出力パスの決定
    if output_path is None:
        output_path = db_path
    
    # データベースを保存
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    
    print(f"💾 保存完了: {output_path}")
    print()
    
    # 統計情報を表示
    print("【追加された情報の統計】")
    vision_attempted = 0
    vision_success = 0
    ocr_fallback = 0
    
    for evidence in db.get('evidence', []):
        if 'phase1_complete_analysis' not in evidence:
            continue
        
        method_info = evidence['phase1_complete_analysis'].get('ai_analysis', {}).get('_analysis_method', {})
        
        if method_info.get('vision_api_used'):
            vision_attempted += 1
            if method_info.get('vision_api_success'):
                vision_success += 1
        
        if method_info.get('ocr_fallback_used'):
            ocr_fallback += 1
    
    print(f"Vision API試行: {vision_attempted}件")
    print(f"Vision API成功: {vision_success}件 ({vision_success/vision_attempted*100:.1f}%)" if vision_attempted > 0 else "Vision API成功: 0件")
    print(f"OCRフォールバック: {ocr_fallback}件")
    print()

def main():
    """メイン関数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python add_analysis_method_info.py <database.jsonのパス> [出力パス]")
        print()
        print("例:")
        print("  python add_analysis_method_info.py database.json")
        print("  python add_analysis_method_info.py database.json database_updated.json")
        sys.exit(1)
    
    db_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not Path(db_path).exists():
        print(f"❌ エラー: {db_path} が見つかりません")
        sys.exit(1)
    
    try:
        add_method_info_to_database(db_path, output_path)
        print("✅ 完了しました")
        print()
        print("次のステップ:")
        print("  python check_analysis_methods.py " + (output_path or db_path))
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

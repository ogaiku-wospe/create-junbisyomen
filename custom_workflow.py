#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1完全版システム - カスタムワークフロー例
独自の処理フローを構築する際の参考実装

使用例:
    python custom_workflow.py
"""

import os
import json
from datetime import datetime
from config import *
from metadata_extractor import MetadataExtractor
from file_processor import FileProcessor
from ai_analyzer_complete import AIAnalyzerComplete


def custom_batch_process(evidence_list: list, output_dir: str):
    """カスタムバッチ処理
    
    Args:
        evidence_list: 証拠情報のリスト [{"number": "ko70", "file": "/path/to/file.pdf"}, ...]
        output_dir: 出力ディレクトリ
    """
    print(f"\n{'='*60}")
    print(f"  カスタムバッチ処理開始")
    print(f"  処理対象: {len(evidence_list)}件")
    print(f"{'='*60}\n")
    
    # モジュール初期化
    metadata_extractor = MetadataExtractor()
    file_processor = FileProcessor()
    ai_analyzer = AIAnalyzerComplete()
    
    results = []
    
    for idx, evidence in enumerate(evidence_list, 1):
        evidence_number = evidence["number"]
        file_path = evidence["file"]
        
        print(f"[{idx}/{len(evidence_list)}] 処理中: {evidence_number}")
        
        try:
            # 1. メタデータ抽出
            metadata = metadata_extractor.extract_complete_metadata(file_path)
            
            # 2. ファイル処理
            processed_data = file_processor.process_file(file_path, evidence_number)
            
            # 3. AI分析
            analysis_result = ai_analyzer.analyze_complete(
                processed_data=processed_data,
                evidence_number=evidence_number
            )
            
            # 4. 結果保存
            result = {
                "evidence_number": evidence_number,
                "complete_metadata": metadata,
                "phase1_complete_analysis": analysis_result,
                "status": "success",
                "processed_at": datetime.now().isoformat()
            }
            results.append(result)
            
            # 個別JSONファイルとして保存
            individual_output = os.path.join(output_dir, f"{evidence_number}_complete.json")
            with open(individual_output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"  ✅ 完了: {individual_output}")
            
        except Exception as e:
            print(f"  ❌ エラー: {e}")
            results.append({
                "evidence_number": evidence_number,
                "status": "failed",
                "error": str(e),
                "processed_at": datetime.now().isoformat()
            })
    
    # 統合結果の保存
    summary_output = os.path.join(output_dir, "batch_process_summary.json")
    with open(summary_output, 'w', encoding='utf-8') as f:
        json.dump({
            "processed_at": datetime.now().isoformat(),
            "total_count": len(evidence_list),
            "success_count": len([r for r in results if r["status"] == "success"]),
            "failed_count": len([r for r in results if r["status"] == "failed"]),
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ バッチ処理完了: {summary_output}")


def custom_quality_check(database_path: str):
    """品質チェック実行
    
    Args:
        database_path: database.jsonのパス
    """
    print(f"\n{'='*60}")
    print(f"  品質チェック実行")
    print(f"{'='*60}\n")
    
    with open(database_path, 'r', encoding='utf-8') as f:
        database = json.load(f)
    
    issues = []
    
    for evidence in database.get("evidence", []):
        evidence_number = evidence.get("evidence_number", "N/A")
        
        # チェック1: 完全性スコア
        try:
            completeness = evidence["phase1_complete_analysis"]["quality_scores"]["completeness_score"]
            if completeness < 90.0:
                issues.append({
                    "evidence": evidence_number,
                    "issue": "低い完全性スコア",
                    "value": completeness,
                    "threshold": 90.0
                })
        except KeyError:
            issues.append({
                "evidence": evidence_number,
                "issue": "完全性スコアが存在しません"
            })
        
        # チェック2: 信頼度スコア
        try:
            confidence = evidence["phase1_complete_analysis"]["quality_scores"]["confidence_score"]
            if confidence < 80.0:
                issues.append({
                    "evidence": evidence_number,
                    "issue": "低い信頼度スコア",
                    "value": confidence,
                    "threshold": 80.0
                })
        except KeyError:
            issues.append({
                "evidence": evidence_number,
                "issue": "信頼度スコアが存在しません"
            })
        
        # チェック3: 言語化レベル
        try:
            verbalization = evidence["phase1_complete_analysis"]["quality_scores"]["verbalization_level"]
            if verbalization < 4:
                issues.append({
                    "evidence": evidence_number,
                    "issue": "言語化レベルが不十分",
                    "value": verbalization,
                    "threshold": 4
                })
        except KeyError:
            issues.append({
                "evidence": evidence_number,
                "issue": "言語化レベルが存在しません"
            })
    
    # 結果表示
    if issues:
        print(f"⚠️ {len(issues)}件の問題が見つかりました:\n")
        for issue in issues:
            print(f"  - {issue['evidence']}: {issue['issue']}")
            if 'value' in issue:
                print(f"    現在値: {issue['value']}, 閾値: {issue['threshold']}")
    else:
        print("✅ 問題は見つかりませんでした")
    
    return issues


def custom_export_report(database_path: str, output_path: str):
    """カスタムレポート出力
    
    Args:
        database_path: database.jsonのパス
        output_path: 出力HTMLファイルパス
    """
    print(f"\n{'='*60}")
    print(f"  HTMLレポート生成")
    print(f"{'='*60}\n")
    
    with open(database_path, 'r', encoding='utf-8') as f:
        database = json.load(f)
    
    # HTML生成
    html = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Phase 1完全版 分析レポート</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        .evidence { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .evidence h3 { color: #2980b9; margin-top: 0; }
        .quality-score { display: inline-block; padding: 5px 10px; border-radius: 3px; font-weight: bold; }
        .high { background: #2ecc71; color: white; }
        .medium { background: #f39c12; color: white; }
        .low { background: #e74c3c; color: white; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #34495e; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Phase 1完全版 分析レポート</h1>
        <p><strong>事件名:</strong> """ + database['case_info']['case_name'] + """</p>
        <p><strong>原告:</strong> """ + database['case_info']['plaintiff'] + """</p>
        <p><strong>被告:</strong> """ + database['case_info']['defendant'] + """</p>
        
        <h2>証拠一覧</h2>
"""
    
    for evidence in database.get("evidence", []):
        evidence_number = evidence.get("evidence_number", "N/A")
        
        # 品質スコアの取得
        try:
            scores = evidence["phase1_complete_analysis"]["quality_scores"]
            completeness = scores["completeness_score"]
            confidence = scores["confidence_score"]
            verbalization = scores["verbalization_level"]
            
            # スコアに応じたクラス
            comp_class = "high" if completeness >= 90 else "medium" if completeness >= 70 else "low"
            conf_class = "high" if confidence >= 80 else "medium" if confidence >= 60 else "low"
            
            html += f"""
        <div class="evidence">
            <h3>{evidence_number}</h3>
            <p><strong>処理日時:</strong> {evidence.get('processed_at', 'N/A')}</p>
            <p>
                <strong>完全性スコア:</strong> <span class="quality-score {comp_class}">{completeness:.1f}%</span>
                <strong>信頼度スコア:</strong> <span class="quality-score {conf_class}">{confidence:.1f}%</span>
                <strong>言語化レベル:</strong> <span class="quality-score high">{verbalization}/5</span>
            </p>
        </div>
"""
        except KeyError:
            html += f"""
        <div class="evidence">
            <h3>{evidence_number}</h3>
            <p><strong>エラー:</strong> 品質スコアデータが不完全です</p>
        </div>
"""
    
    html += """
    </div>
</body>
</html>
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ HTMLレポート生成完了: {output_path}")


# ============================================================================
# 使用例
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  Phase 1完全版システム - カスタムワークフロー例")
    print("="*60)
    
    # 例1: バッチ処理
    print("\n【例1】バッチ処理")
    evidence_list = [
        {"number": "ko70", "file": "/tmp/ko70.pdf"},
        {"number": "ko71", "file": "/tmp/ko71.pdf"},
    ]
    # custom_batch_process(evidence_list, "/tmp/batch_output/")
    
    # 例2: 品質チェック
    print("\n【例2】品質チェック")
    # issues = custom_quality_check("database.json")
    
    # 例3: HTMLレポート生成
    print("\n【例3】HTMLレポート生成")
    # custom_export_report("database.json", "phase1_report.html")
    
    print("\n💡 上記の例をコメント解除して実行してください")

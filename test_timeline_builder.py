#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
時系列ストーリー組み立て機能のテストスクリプト

このスクリプトは timeline_builder.py の動作確認用です。
実際の使用は run_phase1_multi.py のメニューから行ってください。
"""

import os
import sys
import json
from datetime import datetime

# 自作モジュールのインポート
try:
    import global_config as gconfig
    from case_manager import CaseManager
    from timeline_builder import TimelineBuilder, TimelineEvent
except ImportError as e:
    print(f"❌ エラー: モジュールのインポートに失敗しました: {e}")
    sys.exit(1)


def test_timeline_event():
    """TimelineEventクラスのテスト"""
    print("\n" + "="*70)
    print("TimelineEventクラスのテスト")
    print("="*70)
    
    # テストデータ作成
    event1 = TimelineEvent(
        date="2020-01-15",
        evidence_id="ko001",
        evidence_number="甲001",
        description="契約書の写し。A社とB社の間で締結された業務委託契約。",
        confidence="確実"
    )
    
    event2 = TimelineEvent(
        date="2020-03",
        evidence_id="ko002",
        evidence_number="甲002",
        description="請求書の写し。",
        confidence="確実"
    )
    
    event3 = TimelineEvent(
        date=None,
        evidence_id="ko003",
        evidence_number="甲003",
        description="日付不明の証拠",
        confidence="不明"
    )
    
    # 日付表示のテスト
    print("\n【日付表示テスト】")
    print(f"event1: {event1.format_date_display()} (precision: {event1.date_precision})")
    print(f"event2: {event2.format_date_display()} (precision: {event2.date_precision})")
    print(f"event3: {event3.format_date_display()} (precision: {event3.date_precision})")
    
    # ソートキーのテスト
    print("\n【ソートキーテスト】")
    events = [event3, event2, event1]
    events.sort(key=lambda e: e.sort_key)
    
    print("ソート後の順序:")
    for i, event in enumerate(events, 1):
        print(f"  {i}. {event.evidence_number}: {event.format_date_display()}")
    
    # 辞書変換のテスト
    print("\n【辞書変換テスト】")
    print(json.dumps(event1.to_dict(), ensure_ascii=False, indent=2))
    
    print("\n✅ TimelineEventクラスのテスト完了")


def test_timeline_builder_without_data():
    """データなしでTimelineBuilderをテスト"""
    print("\n" + "="*70)
    print("TimelineBuilderクラスのテスト（データなし）")
    print("="*70)
    
    try:
        # CaseManagerを初期化
        case_manager = CaseManager()
        
        # 事件を検出
        cases = case_manager.detect_cases()
        
        if not cases:
            print("\n⚠️ 事件が見つかりません。")
            print("テストを実行するには、事前に事件を作成してください。")
            return
        
        # 最初の事件を使用
        current_case = cases[0]
        print(f"\nテスト対象事件: {current_case['case_name']}")
        
        # TimelineBuilderを初期化（AI無効）
        print("\nTimelineBuilderを初期化中（AI無効）...")
        builder = TimelineBuilder(case_manager, current_case, use_ai=False)
        
        # タイムラインを構築
        print("タイムラインを構築中...")
        timeline_events = builder.build_timeline()
        
        if not timeline_events:
            print("\n⚠️ タイムラインを構築できませんでした。")
            print("証拠が登録されていないか、証拠に日付情報がありません。")
            return
        
        # 基本的なナラティブを生成
        print(f"\n生成されたイベント数: {len(timeline_events)}件")
        
        print("\n【最初の3件のイベント】")
        for i, event in enumerate(timeline_events[:3], 1):
            print(f"\n{i}. {event.format_date_display()} ({event.evidence_number})")
            desc_lines = event.description.split('\n')
            for line in desc_lines[:3]:  # 最初の3行のみ
                if line.strip():
                    print(f"   {line.strip()}")
        
        # エクスポートテスト（JSON形式のみ）
        print("\n【エクスポートテスト】JSON形式")
        output_path = builder.export_timeline(
            timeline_events, 
            output_format="json",
            include_ai_narrative=False
        )
        
        if output_path:
            print(f"\n✅ エクスポート成功: {output_path}")
        
        print("\n✅ TimelineBuilderクラスのテスト完了")
        
    except Exception as e:
        print(f"\n❌ テスト中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


def test_date_parsing():
    """日付パース機能のテスト"""
    print("\n" + "="*70)
    print("日付パース機能のテスト")
    print("="*70)
    
    # CaseManagerを初期化
    case_manager = CaseManager()
    cases = case_manager.detect_cases()
    
    if not cases:
        print("\n⚠️ 事件が見つかりません。")
        return
    
    current_case = cases[0]
    builder = TimelineBuilder(case_manager, current_case, use_ai=False)
    
    # テスト用の日付文字列
    test_dates = [
        "2020-01-15",
        "2020-01-15T10:30:00",
        "2020:01:15 10:30:00",
        "2020年1月15日",
        "2020年1月",
        "2020年",
        "2020/01/15",
        "invalid_date",
    ]
    
    print("\n【日付パーステスト】")
    for date_str in test_dates:
        parsed = builder._parse_date(date_str)
        print(f"  '{date_str}' -> {parsed}")
    
    print("\n✅ 日付パース機能のテスト完了")


def main():
    """メイン関数"""
    print("="*70)
    print("  時系列ストーリー組み立て機能 - テストスクリプト")
    print("="*70)
    print("\nこのスクリプトは timeline_builder.py の動作確認用です。")
    print("実際の使用は run_phase1_multi.py のメニューから行ってください。")
    
    # テスト項目を選択
    print("\n【テスト項目】")
    print("  1. TimelineEventクラスのテスト")
    print("  2. TimelineBuilderクラスのテスト（データなし）")
    print("  3. 日付パース機能のテスト")
    print("  4. すべてのテストを実行")
    print("  0. 終了")
    
    choice = input("\n選択 (0-4): ").strip()
    
    if choice == '1':
        test_timeline_event()
    elif choice == '2':
        test_timeline_builder_without_data()
    elif choice == '3':
        test_date_parsing()
    elif choice == '4':
        test_timeline_event()
        test_date_parsing()
        test_timeline_builder_without_data()
    elif choice == '0':
        print("\n終了します")
    else:
        print("\n無効な選択です")


if __name__ == "__main__":
    main()

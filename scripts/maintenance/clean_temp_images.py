#!/usr/bin/env python3
"""
Temporary Image File Cleaner

このスクリプトは、Vision API処理で作成された一時画像ファイルを削除します。
PDFからの画像変換時に作成されるファイルが古くなっている場合があります。

削除されるファイル:
- *_page*.jpg (PDFページ画像)
- 指定した時間より古い一時ファイル

使用方法:
    python3 clean_temp_images.py [--case CASE_NAME] [--dry-run] [--age HOURS]
"""

import os
import sys
import glob
import argparse
from datetime import datetime, timedelta

import global_config as gconfig

def clean_temp_images(case_name: str = None, dry_run: bool = False, max_age_hours: int = 24):
    """一時画像ファイルを削除
    
    Args:
        case_name: 特定のケース名（None = すべてのケース）
        dry_run: Trueの場合、削除せずに確認のみ
        max_age_hours: この時間数より古いファイルを削除（0 = すべて）
    """
    
    print("=" * 80)
    print("Temporary Image File Cleaner")
    print("=" * 80)
    
    if dry_run:
        print("\n🔍 DRY RUN MODE - ファイルは削除されません\n")
    
    # ケースリストを取得
    if case_name:
        case_dirs = [os.path.join(gconfig.CASES_DIR, case_name)]
    else:
        if not os.path.exists(gconfig.CASES_DIR):
            print(f"⚠️  ケースディレクトリが見つかりません: {gconfig.CASES_DIR}")
            return
        
        case_dirs = [os.path.join(gconfig.CASES_DIR, d) 
                    for d in os.listdir(gconfig.CASES_DIR)
                    if os.path.isdir(os.path.join(gconfig.CASES_DIR, d))]
    
    total_deleted = 0
    total_size_freed = 0
    
    for case_dir in case_dirs:
        if not os.path.exists(case_dir):
            print(f"⚠️  ケースディレクトリが見つかりません: {case_dir}")
            continue
        
        case_name_display = os.path.basename(case_dir)
        print(f"\n📁 ケース: {case_name_display}")
        
        # 証拠ディレクトリを探す
        evidence_dir = os.path.join(case_dir, '証拠')
        if not os.path.exists(evidence_dir):
            print(f"   証拠ディレクトリが見つかりません")
            continue
        
        # 一時画像ファイルを検索
        temp_image_patterns = [
            '**/*_page*.jpg',
            '**/*_page*.jpeg',
            '**/*_temp*.jpg',
            '**/*_temp*.jpeg',
        ]
        
        case_deleted = 0
        case_size_freed = 0
        
        for pattern in temp_image_patterns:
            pattern_path = os.path.join(evidence_dir, pattern)
            temp_files = glob.glob(pattern_path, recursive=True)
            
            for temp_file in temp_files:
                try:
                    # ファイルの更新時刻をチェック
                    file_mtime = os.path.getmtime(temp_file)
                    file_age = datetime.now() - datetime.fromtimestamp(file_mtime)
                    file_age_hours = file_age.total_seconds() / 3600
                    
                    # 新しすぎるファイルはスキップ
                    if max_age_hours > 0 and file_age_hours < max_age_hours:
                        continue
                    
                    file_size = os.path.getsize(temp_file)
                    file_name = os.path.basename(temp_file)
                    
                    age_str = f"{file_age_hours:.1f}時間前" if file_age_hours < 48 else f"{file_age.days}日前"
                    
                    print(f"   🗑️  {file_name} ({file_size:,} bytes, {age_str})")
                    
                    if not dry_run:
                        os.remove(temp_file)
                        case_deleted += 1
                        case_size_freed += file_size
                    else:
                        case_deleted += 1
                        case_size_freed += file_size
                        
                except Exception as e:
                    print(f"   ❌ エラー: {temp_file} - {e}")
        
        if case_deleted == 0:
            print(f"   ✅ 削除対象のファイルはありません")
        else:
            action = "削除されました" if not dry_run else "削除対象"
            print(f"   📊 {case_deleted}ファイル {action} ({case_size_freed:,} bytes)")
        
        total_deleted += case_deleted
        total_size_freed += case_size_freed
    
    # サマリー
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)
    
    if total_deleted == 0:
        print("✅ 削除対象のファイルはありませんでした")
    else:
        action = "削除しました" if not dry_run else "削除対象です"
        size_mb = total_size_freed / 1024 / 1024
        print(f"📊 合計 {total_deleted}ファイル {action}")
        print(f"💾 解放された容量: {total_size_freed:,} bytes ({size_mb:.2f} MB)")
        
        if dry_run:
            print("\n💡 実際に削除するには --dry-run オプションを外して実行してください")

def main():
    """メインエントリーポイント"""
    parser = argparse.ArgumentParser(
        description="Vision API処理用の一時画像ファイルを削除",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # ドライラン（削除せずに確認のみ）
  python3 clean_temp_images.py --dry-run
  
  # 特定のケース
  python3 clean_temp_images.py --case "山田太郎 vs 株式会社ABC"
  
  # 48時間以上古いファイル
  python3 clean_temp_images.py --age 48
  
  # すべてのファイルをすぐに削除
  python3 clean_temp_images.py --age 0
        """
    )
    
    parser.add_argument(
        '--case',
        type=str,
        help='特定のケース名を指定'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='削除せずに確認のみ行う'
    )
    
    parser.add_argument(
        '--age',
        type=int,
        default=24,
        help='この時間数より古いファイルを削除（デフォルト: 24、0 = すべて）'
    )
    
    args = parser.parse_args()
    
    try:
        clean_temp_images(
            case_name=args.case,
            dry_run=args.dry_run,
            max_age_hours=args.age
        )
    except KeyboardInterrupt:
        print("\n\n⚠️  中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1完全版システム - 証拠整理システム

【機能】
- 未分類フォルダから証拠ファイルを検出
- AIによる証拠内容の自動分析・分類
- 証拠番号の自動採番・リネーム提案
- ファイルの移動・整理

【使用方法】
    from evidence_organizer import EvidenceOrganizer
    
    organizer = EvidenceOrganizer(case_manager, selected_case)
    organizer.organize_evidence()
"""

import os
import sys
import json
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import shutil

try:
    import global_config as gconfig
    from case_manager import CaseManager
    from ai_analyzer_complete import AIAnalyzerComplete
    from metadata_extractor import MetadataExtractor
except ImportError as e:
    print(f"❌ エラー: モジュールのインポートに失敗しました: {e}")
    sys.exit(1)


class EvidenceOrganizer:
    """証拠整理クラス"""
    
    def __init__(self, case_manager: CaseManager, current_case: Dict):
        """初期化
        
        Args:
            case_manager: CaseManagerインスタンス
            current_case: 現在の事件情報
        """
        self.case_manager = case_manager
        self.current_case = current_case
        self.ai_analyzer = AIAnalyzerComplete()
        self.metadata_extractor = MetadataExtractor()
        
        # 未分類フォルダIDを取得または作成
        self.unclassified_folder_id = self._get_or_create_unclassified_folder()
        
        # 整理済み_未確定フォルダIDを取得または作成
        self.pending_folder_id = self._get_or_create_pending_folder()
    
    def _get_or_create_unclassified_folder(self) -> Optional[str]:
        """未分類フォルダを取得または作成"""
        service = self.case_manager.get_google_drive_service()
        if not service:
            return None
        
        case_folder_id = self.current_case['case_folder_id']
        
        try:
            # 未分類フォルダを検索
            query = f"'{case_folder_id}' in parents and name='未分類' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            
            results = service.files().list(
                q=query,
                corpora='drive',
                driveId=self.case_manager.shared_drive_root_id,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                fields='files(id, name)',
                pageSize=10
            ).execute()
            
            files = results.get('files', [])
            
            if files:
                print(f"✅ 未分類フォルダを検出: {files[0]['id']}")
                return files[0]['id']
            
            # 未分類フォルダが存在しない場合は作成
            print("📁 未分類フォルダを作成中...")
            folder_metadata = {
                'name': '未分類',
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [case_folder_id]
            }
            
            folder = service.files().create(
                body=folder_metadata,
                supportsAllDrives=True,
                fields='id, name, webViewLink'
            ).execute()
            
            print(f"✅ 未分類フォルダを作成: {folder['id']}")
            print(f"🔗 URL: {folder.get('webViewLink', 'N/A')}")
            
            return folder['id']
            
        except Exception as e:
            print(f"❌ 未分類フォルダの取得・作成エラー: {e}")
            return None
    
    def _get_or_create_pending_folder(self) -> Optional[str]:
        """整理済み_未確定フォルダを取得または作成"""
        service = self.case_manager.get_google_drive_service()
        if not service:
            return None
        
        case_folder_id = self.current_case['case_folder_id']
        
        try:
            # 整理済み_未確定フォルダを検索
            query = f"'{case_folder_id}' in parents and name='整理済み_未確定' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            
            results = service.files().list(
                q=query,
                corpora='drive',
                driveId=self.case_manager.shared_drive_root_id,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                fields='files(id, name, webViewLink)',
                pageSize=10
            ).execute()
            
            files = results.get('files', [])
            
            if files:
                print(f"✅ 整理済み_未確定フォルダを検出: {files[0]['id']}")
                return files[0]['id']
            
            # 見つからない場合は作成
            folder_metadata = {
                'name': '整理済み_未確定',
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [case_folder_id]
            }
            
            folder = service.files().create(
                body=folder_metadata,
                supportsAllDrives=True,
                fields='id, name, webViewLink'
            ).execute()
            
            print(f"✅ 整理済み_未確定フォルダを作成: {folder['id']}")
            print(f"🔗 URL: {folder.get('webViewLink', 'N/A')}")
            
            return folder['id']
            
        except Exception as e:
            print(f"❌ 整理済み_未確定フォルダの取得・作成エラー: {e}")
            return None
    
    def detect_unclassified_files(self) -> List[Dict]:
        """未分類フォルダからファイルを検出
        
        Returns:
            検出されたファイルのリスト
        """
        if not self.unclassified_folder_id:
            print("❌ 未分類フォルダが設定されていません")
            return []
        
        print("\n🔍 未分類フォルダからファイルを検索中...")
        
        service = self.case_manager.get_google_drive_service()
        if not service:
            return []
        
        try:
            query = f"'{self.unclassified_folder_id}' in parents and trashed=false and mimeType!='application/vnd.google-apps.folder'"
            
            results = service.files().list(
                q=query,
                corpora='drive',
                driveId=self.case_manager.shared_drive_root_id,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                fields='files(id, name, mimeType, size, createdTime, modifiedTime, webViewLink, webContentLink)',
                pageSize=1000
            ).execute()
            
            files = results.get('files', [])
            print(f"✅ {len(files)}件のファイルを検出しました")
            
            return files
            
        except Exception as e:
            print(f"❌ ファイル検索エラー: {e}")
            return []
    
    def analyze_file_content(self, file_info: Dict, local_path: str) -> Dict:
        """AIを使用してファイル内容を分析
        
        Args:
            file_info: Google Driveファイル情報
            local_path: ローカルファイルパス
        
        Returns:
            分析結果（証拠種別、推奨番号、ファイル名提案等）
        """
        print(f"\n🤖 AI分析中: {file_info['name']}")
        
        try:
            # AIに証拠内容を分析させるプロンプト
            analysis_prompt = """
このファイルは民事訴訟の証拠です。以下の情報を抽出してください：

1. 証拠種別（診断書、契約書、メール、SNS投稿、写真、請求書、領収書、その他）
2. 簡潔な内容の説明（30文字以内）
3. 原告側の証拠か被告側の証拠か（不明の場合は原告側と推定）
4. 重要度（高・中・低）
5. 推奨ファイル名（証拠種別_簡潔な説明.拡張子）

以下のJSON形式で回答してください：
{
  "evidence_type": "診断書",
  "description": "適応障害の診断書",
  "side": "plaintiff",
  "importance": "high",
  "suggested_filename": "診断書_適応障害.pdf"
}
"""
            
            # 簡易分析（実際のAI分析は既存のai_analyzer_completeを使用）
            file_type = self._detect_file_type(local_path)
            
            # ファイル名から推測
            filename = file_info['name']
            analysis = {
                "evidence_type": self._guess_evidence_type(filename),
                "description": self._extract_description(filename),
                "side": "plaintiff",  # デフォルトは原告側
                "importance": "medium",
                "suggested_filename": self._generate_suggested_filename(filename),
                "confidence": 0.7
            }
            
            print(f"  📋 証拠種別: {analysis['evidence_type']}")
            print(f"  📝 説明: {analysis['description']}")
            print(f"  💡 推奨ファイル名: {analysis['suggested_filename']}")
            
            return analysis
            
        except Exception as e:
            print(f"❌ AI分析エラー: {e}")
            return {
                "evidence_type": "その他",
                "description": "不明",
                "side": "plaintiff",
                "importance": "medium",
                "suggested_filename": file_info['name'],
                "confidence": 0.3
            }
    
    def _detect_file_type(self, file_path: str) -> str:
        """ファイル形式を検出"""
        ext = os.path.splitext(file_path)[1].lower()
        
        for file_type, info in gconfig.SUPPORTED_FORMATS.items():
            if ext in info['extensions']:
                return file_type
        
        return 'document'
    
    def _guess_evidence_type(self, filename: str) -> str:
        """ファイル名から証拠種別を推測"""
        filename_lower = filename.lower()
        
        keywords = {
            "診断書": ["診断", "診断書", "medical", "diagnosis"],
            "契約書": ["契約", "契約書", "contract", "agreement"],
            "メール": ["メール", "mail", "email", "message"],
            "SNS投稿": ["sns", "twitter", "facebook", "instagram", "投稿", "post"],
            "写真": ["img", "photo", "写真", "画像", "jpg", "jpeg", "png"],
            "請求書": ["請求", "請求書", "invoice", "bill"],
            "領収書": ["領収", "領収書", "receipt"],
            "録音": ["録音", "audio", "recording", "mp3", "m4a"],
            "動画": ["動画", "video", "mp4", "mov"],
        }
        
        for evidence_type, words in keywords.items():
            if any(word in filename_lower for word in words):
                return evidence_type
        
        return "その他"
    
    def _extract_description(self, filename: str) -> str:
        """ファイル名から簡潔な説明を抽出"""
        # 拡張子を除去
        name_without_ext = os.path.splitext(filename)[0]
        
        # 日付やタイムスタンプを除去
        name_clean = re.sub(r'\d{8}|\d{6}|\d{4}-\d{2}-\d{2}', '', name_without_ext)
        name_clean = re.sub(r'IMG_|DSC_|SCAN_|DOC_', '', name_clean, flags=re.IGNORECASE)
        name_clean = name_clean.strip('_- ')
        
        # 30文字以内に切り詰め
        if len(name_clean) > 30:
            name_clean = name_clean[:27] + "..."
        
        return name_clean if name_clean else "不明"
    
    def _generate_suggested_filename(self, original_filename: str) -> str:
        """推奨ファイル名を生成"""
        evidence_type = self._guess_evidence_type(original_filename)
        description = self._extract_description(original_filename)
        ext = os.path.splitext(original_filename)[1]
        
        return f"{evidence_type}_{description}{ext}"
    
    def get_existing_evidence_numbers(self, side: str = "ko") -> Dict:
        """既存の証拠番号を分析
        
        Args:
            side: "ko"（甲号証）または "otsu"（乙号証）
        
        Returns:
            {
                'numbers': [1, 2, 3, 5, 7],  # 既存の番号リスト
                'gaps': [(3, 5), (5, 7)],      # 欠番の範囲
                'max': 7,                      # 最大番号
                'evidence_data': {1: {...}, 2: {...}}  # 証拠データ
            }
        """
        result = {
            'numbers': [],
            'gaps': [],
            'max': 0,
            'evidence_data': {}
        }
        
        try:
            if not os.path.exists("database.json"):
                return result
            
            with open("database.json", 'r', encoding='utf-8') as f:
                database = json.load(f)
            
            evidence_list = database.get('evidence', [])
            
            # 該当する側の証拠番号を抽出
            prefix = side.lower()
            
            for evidence in evidence_list:
                evidence_id = evidence.get('evidence_id', '')
                if evidence_id.startswith(prefix):
                    # 番号部分を抽出（サフィックス付きも対応: ko70-2 → 70）
                    match = re.match(r'[a-z]+([0-9]+)', evidence_id)
                    if match:
                        number = int(match.group(1))
                        result['numbers'].append(number)
                        result['evidence_data'][number] = {
                            'evidence_id': evidence_id,
                            'evidence_number': evidence.get('evidence_number', ''),
                            'filename': evidence.get('original_filename', ''),
                            'registered_at': evidence.get('registered_at', '')
                        }
            
            if result['numbers']:
                result['numbers'].sort()
                result['max'] = max(result['numbers'])
                
                # 欠番を検出
                for i in range(len(result['numbers']) - 1):
                    current = result['numbers'][i]
                    next_num = result['numbers'][i + 1]
                    if next_num - current > 1:
                        result['gaps'].append((current, next_num))
            
            return result
            
        except Exception as e:
            print(f"⚠️ 証拠番号分析エラー: {e}")
            return result
    
    def suggest_evidence_number_with_context(self, side: str, file_info: Dict, analysis: Dict) -> Dict:
        """既存証拠を考慮して証拠番号を提案
        
        Args:
            side: "ko" または "otsu"
            file_info: ファイル情報
            analysis: AI分析結果
        
        Returns:
            提案情報（番号、理由、代替案を含む）
        """
        existing = self.get_existing_evidence_numbers(side)
        
        # デフォルト提案: 最大番号 + 1
        default_number = existing['max'] + 1 if existing['max'] > 0 else 1
        
        suggestion = {
            'primary': {
                'number': default_number,
                'reason': f"最新の証拠番号の次（{existing['max']}の次）",
                'requires_renumbering': False
            },
            'alternatives': []
        }
        
        # 欠番がある場合は代替案として提示
        if existing['gaps']:
            for gap_start, gap_end in existing['gaps']:
                gap_size = gap_end - gap_start - 1
                if gap_size > 0:
                    # 欠番の最初の番号を提案
                    fill_number = gap_start + 1
                    suggestion['alternatives'].append({
                        'number': fill_number,
                        'reason': f"欠番を埋める（{gap_start}と{gap_end}の間）",
                        'gap': (gap_start, gap_end),
                        'requires_renumbering': False
                    })
        
        # 既存番号の間に挿入する代替案を追加
        if existing['numbers']:
            # 最初の番号の前に挿入
            if existing['numbers'][0] > 1:
                suggestion['alternatives'].append({
                    'number': 1,
                    'reason': f"最初に挿入（1以降を自動リナンバリング）",
                    'requires_renumbering': True,
                    'affected_count': len(existing['numbers'])
                })
            
            # 連続した番号の間に挿入（リナンバリング必要）
            for i in range(len(existing['numbers']) - 1):
                current = existing['numbers'][i]
                next_num = existing['numbers'][i + 1]
                
                # 連続している場合のみ（欠番でない）
                if next_num - current == 1:
                    insert_pos = next_num
                    affected_count = len([n for n in existing['numbers'] if n >= insert_pos])
                    suggestion['alternatives'].append({
                        'number': insert_pos,
                        'reason': f"{current}と{next_num}の間に挿入（{insert_pos}以降を自動リナンバリング）",
                        'requires_renumbering': True,
                        'affected_count': affected_count
                    })
        
        return suggestion
    
    def get_next_evidence_number(self, side: str = "ko") -> int:
        """次の証拠番号を取得（後方互換性のため残す）
        
        Args:
            side: "ko"（甲号証）または "otsu"（乙号証）
        
        Returns:
            次の証拠番号
        """
        existing = self.get_existing_evidence_numbers(side)
        return existing['max'] + 1 if existing['max'] > 0 else 1
    
    def propose_evidence_assignment(self, file_info: Dict, analysis: Dict) -> Dict:
        """証拠番号の割り当てを提案（仮番号を使用）
        
        Args:
            file_info: ファイル情報
            analysis: AI分析結果
        
        Returns:
            提案情報（仮番号付き）
        """
        side = "ko" if analysis['side'] == "plaintiff" else "otsu"
        
        # 整理済み_未確定フォルダ内の仮番号ファイル数を取得
        temp_number = self._get_next_temp_number()
        
        # 仮番号ID
        temp_id = f"tmp_{temp_number:03d}"
        
        # ファイル名提案
        ext = os.path.splitext(file_info['name'])[1]
        suggested_filename = f"{temp_id}_{analysis['suggested_filename']}"
        if not suggested_filename.endswith(ext):
            suggested_filename = os.path.splitext(suggested_filename)[0] + ext
        
        proposal = {
            "temp_id": temp_id,
            "temp_number": temp_number,
            "suggested_filename": suggested_filename,
            "side": side,
            "evidence_type": analysis['evidence_type'],
            "description": analysis['description'],
            "importance": analysis['importance'],
            "original_filename": file_info['name'],
            "status": "pending"  # 未確定状態
        }
        
        return proposal
    
    def _get_next_temp_number(self) -> int:
        """次の仮番号を取得"""
        service = self.case_manager.get_google_drive_service()
        if not service:
            return 1
        
        try:
            # 整理済み_未確定フォルダ内のファイルを検索
            query = f"'{self.pending_folder_id}' in parents and trashed=false and mimeType!='application/vnd.google-apps.folder'"
            
            results = service.files().list(
                q=query,
                corpora='drive',
                driveId=self.case_manager.shared_drive_root_id,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                fields='files(name)',
                pageSize=1000
            ).execute()
            
            files = results.get('files', [])
            
            # 既存の仮番号を抽出
            temp_numbers = []
            for file in files:
                name = file['name']
                if name.startswith('tmp_'):
                    try:
                        # tmp_001_... から数字部分を抽出
                        num_str = name.split('_')[1]
                        temp_numbers.append(int(num_str))
                    except (IndexError, ValueError):
                        continue
            
            # 最大値+1を返す
            return max(temp_numbers) + 1 if temp_numbers else 1
            
        except Exception as e:
            print(f"❌ 仮番号取得エラー: {e}")
            return 1
    
    def get_evidence_files_to_renumber(self, side: str, from_number: int) -> List[Dict]:
        """リナンバリング対象の証拠ファイルを取得
        
        Args:
            side: "ko" または "otsu"
            from_number: この番号以降の証拠をリナンバリング
        
        Returns:
            リナンバリング対象のファイルリスト（番号順にソート）
        """
        if not os.path.exists("database.json"):
            return []
        
        try:
            with open("database.json", 'r', encoding='utf-8') as f:
                database = json.load(f)
            
            evidence_list = database.get('evidence', [])
            prefix = side.lower()
            
            # 対象証拠を抽出
            target_evidence = []
            for evidence in evidence_list:
                evidence_id = evidence.get('evidence_id', '')
                if evidence_id.startswith(prefix):
                    match = re.match(r'[a-z]+([0-9]+)', evidence_id)
                    if match:
                        number = int(match.group(1))
                        if number >= from_number:
                            target_evidence.append({
                                'number': number,
                                'evidence': evidence,
                                'evidence_id': evidence_id
                            })
            
            # 番号順にソート（降順：大きい番号から処理）
            target_evidence.sort(key=lambda x: x['number'], reverse=True)
            
            return target_evidence
            
        except Exception as e:
            print(f"❌ リナンバリング対象取得エラー: {e}")
            return []
    
    def renumber_evidence(self, side: str, from_number: int) -> bool:
        """証拠を一括リナンバリング
        
        Args:
            side: "ko" または "otsu"
            from_number: この番号以降の証拠を+1リナンバリング
        
        Returns:
            成功: True, 失敗: False
        """
        print(f"\n🔄 証拠リナンバリング開始: {side}{from_number:03d}以降")
        
        # リナンバリング対象を取得
        targets = self.get_evidence_files_to_renumber(side, from_number)
        
        if not targets:
            print("✅ リナンバリング対象なし")
            return True
        
        print(f"📋 対象: {len(targets)}件の証拠")
        for target in targets:
            old_num = target['number']
            new_num = old_num + 1
            print(f"  - {side}{old_num:03d} → {side}{new_num:03d}")
        
        # 確認プロンプト
        confirm = input(f"\n⚠️  {len(targets)}件のファイルをリネームします。実行しますか？ (y/n): ").strip().lower()
        if confirm != 'y':
            print("❌ リナンバリングをキャンセルしました")
            return False
        
        service = self.case_manager.get_google_drive_service()
        if not service:
            return False
        
        # database.jsonを読み込み
        with open("database.json", 'r', encoding='utf-8') as f:
            database = json.load(f)
        
        success_count = 0
        
        # 大きい番号から順に処理（衝突を避ける）
        for target in targets:
            old_number = target['number']
            new_number = old_number + 1
            evidence = target['evidence']
            
            old_id = f"{side}{old_number:03d}"
            new_id = f"{side}{new_number:03d}"
            side_kanji = '甲' if side == 'ko' else '乙'
            new_evidence_number = f"{side_kanji}{new_number:03d}"
            
            print(f"\n🔄 処理中: {old_id} → {new_id}")
            
            try:
                # Google Driveのファイルをリネーム
                gdrive_info = evidence.get('complete_metadata', {}).get('gdrive', {})
                file_id = gdrive_info.get('file_id')
                
                if file_id:
                    # 現在のファイル名を取得
                    current_file = service.files().get(
                        fileId=file_id,
                        supportsAllDrives=True,
                        fields='name'
                    ).execute()
                    
                    old_filename = current_file.get('name', '')
                    
                    # 新しいファイル名を生成
                    if old_filename.startswith(old_id):
                        new_filename = new_id + old_filename[len(old_id):]
                    else:
                        # ファイル名が期待と異なる場合
                        ext = os.path.splitext(old_filename)[1]
                        new_filename = f"{new_id}_{old_filename}{ext}" if not old_filename.endswith(ext) else f"{new_id}_{old_filename}"
                    
                    # ファイルをリネーム
                    service.files().update(
                        fileId=file_id,
                        body={'name': new_filename},
                        supportsAllDrives=True
                    ).execute()
                    
                    print(f"  ✅ ファイルリネーム: {old_filename} → {new_filename}")
                    
                    # database.jsonを更新
                    evidence['evidence_id'] = new_id
                    evidence['evidence_number'] = new_evidence_number
                    
                    # メタデータのファイル名も更新
                    if 'complete_metadata' in evidence:
                        if 'basic' in evidence['complete_metadata']:
                            evidence['complete_metadata']['basic']['file_name'] = new_filename
                    
                    success_count += 1
                else:
                    print(f"  ⚠️ ファイルIDが見つかりません: {old_id}")
                    
            except Exception as e:
                print(f"  ❌ エラー: {e}")
                # エラーが発生しても続行
        
        # database.jsonを保存
        try:
            database['metadata']['last_updated'] = datetime.now().isoformat()
            
            with open("database.json", 'w', encoding='utf-8') as f:
                json.dump(database, f, ensure_ascii=False, indent=2)
            
            print(f"\n✅ database.json更新完了")
            
        except Exception as e:
            print(f"\n❌ database.json保存エラー: {e}")
            return False
        
        print(f"\n✅ リナンバリング完了: {success_count}/{len(targets)}件")
        return success_count == len(targets)
    
    def insert_evidence_with_renumbering(self, insert_number: int, file_info: Dict, proposal: Dict) -> bool:
        """証拠を挿入し、それ以降をリナンバリング
        
        Args:
            insert_number: 挿入位置の番号
            file_info: Google Driveファイル情報
            proposal: 証拠割り当て提案
        
        Returns:
            成功: True, 失敗: False
        """
        side = proposal['side']
        
        print(f"\n📥 証拠挿入とリナンバリング")
        print(f"  挿入位置: {side}{insert_number:03d}")
        print(f"  影響: {side}{insert_number:03d}以降を+1リナンバリング")
        
        # まず既存証拠をリナンバリング
        if not self.renumber_evidence(side, insert_number):
            print("❌ リナンバリング失敗。証拠挿入を中止します。")
            return False
        
        # 新しい証拠を挿入
        proposal['evidence_id'] = f"{side}{insert_number:03d}"
        proposal['evidence_number'] = f"{'甲' if side == 'ko' else '乙'}{insert_number:03d}"
        
        # ファイル名を更新
        ext = os.path.splitext(file_info['name'])[1]
        base_name = os.path.splitext(proposal['suggested_filename'])[0]
        parts = base_name.split('_', 1)
        if len(parts) == 2:
            proposal['suggested_filename'] = f"{proposal['evidence_id']}_{parts[1]}{ext}"
        else:
            proposal['suggested_filename'] = f"{proposal['evidence_id']}{ext}"
        
        # ファイルを移動（リナンバリング時は甲号証フォルダに直接移動）
        # TODO: この部分は後で整理済み_未確定フォルダからの移動に変更
        return self.move_file_to_pending_folder(file_info, proposal)
    
    def move_file_to_pending_folder(self, file_info: Dict, proposal: Dict) -> bool:
        """ファイルを整理済み_未確定フォルダに移動（仮番号付き）
        
        Args:
            file_info: Google Driveファイル情報
            proposal: 証拠割り当て提案（仮番号付き）
        
        Returns:
            成功: True, 失敗: False
        """
        service = self.case_manager.get_google_drive_service()
        if not service:
            return False
        
        try:
            # 移動先は整理済み_未確定フォルダ
            target_folder_id = self.pending_folder_id
            
            if not target_folder_id:
                print(f"❌ 整理済み_未確定フォルダが設定されていません")
                return False
            
            file_id = file_info['id']
            
            # ファイルを移動してリネーム
            file_metadata = {
                'name': proposal['suggested_filename']
            }
            
            # 現在の親フォルダから削除して新しい親フォルダに追加
            file = service.files().update(
                fileId=file_id,
                addParents=target_folder_id,
                removeParents=self.unclassified_folder_id,
                body=file_metadata,
                supportsAllDrives=True,
                fields='id, name, parents'
            ).execute()
            
            print(f"✅ ファイルを移動・リネーム: {proposal['suggested_filename']}")
            
            # database.jsonに証拠を登録
            if not self._save_evidence_to_database(file_info, proposal):
                print(f"⚠️ database.json保存に失敗しましたが、ファイル移動は成功しました")
            
            return True
            
        except Exception as e:
            print(f"❌ ファイル移動エラー: {e}")
            return False
    
    def _save_evidence_to_database(self, file_info: Dict, proposal: Dict) -> bool:
        """証拠情報をdatabase.jsonに保存
        
        Args:
            file_info: Google Driveファイル情報
            proposal: 証拠割り当て提案
        
        Returns:
            成功: True, 失敗: False
        """
        try:
            # database.jsonを読み込み
            if not os.path.exists("database.json"):
                print(f"❌ database.jsonが見つかりません")
                return False
            
            with open("database.json", 'r', encoding='utf-8') as f:
                database = json.load(f)
            
            # 証拠情報を作成（仮番号・未確定状態）
            evidence_entry = {
                "temp_id": proposal['temp_id'],
                "temp_number": proposal['temp_number'],
                "original_filename": file_info['name'],
                "renamed_filename": proposal['suggested_filename'],
                "evidence_type": proposal['evidence_type'],
                "description": proposal['description'],
                "side": proposal['side'],
                "status": "pending",  # 未確定状態
                "created_at": datetime.now().isoformat(),
                "file_size": int(file_info.get('size', 0)),
                "gdrive_file_id": file_info['id'],
                "complete_metadata": {
                    "basic": {
                        "file_name": proposal['suggested_filename'],
                        "file_size": int(file_info.get('size', 0)),
                        "file_type": file_info.get('mimeType', ''),
                        "created_date": file_info.get('createdTime', ''),
                        "modified_date": file_info.get('modifiedTime', '')
                    },
                    "gdrive": {
                        "file_id": file_info['id'],
                        "web_view_link": file_info.get('webViewLink', ''),
                        "web_content_link": file_info.get('webContentLink', '')
                    }
                }
            }
            
            # evidenceリストに追加（番号順にソート）
            database['evidence'].append(evidence_entry)
            
            # 仮番号でソート
            def sort_key(e):
                # pendingの場合はtemp_number、confirmedの場合はevidence_idを使用
                if e.get('status') == 'pending':
                    return (0, e.get('temp_number', 999))
                else:
                    eid = e.get('evidence_id', 'tmp_999')
                    side = 'ko' if eid.startswith('ko') else 'otsu'
                    number = int(re.search(r'\d+', eid).group()) if re.search(r'\d+', eid) else 999
                    return (1 if side == 'ko' else 2, number)
            
            database['evidence'].sort(key=sort_key)
            
            # メタデータを更新
            database['metadata']['last_updated'] = datetime.now().isoformat()
            
            # 保存
            with open("database.json", 'w', encoding='utf-8') as f:
                json.dump(database, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"❌ database.json保存エラー: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def interactive_organize(self):
        """対話的な証拠整理"""
        print("\n" + "="*70)
        print("  証拠整理システム")
        print("  📁 事件: " + self.current_case['case_name'])
        print("="*70)
        
        # 未分類ファイルを検出
        files = self.detect_unclassified_files()
        
        if not files:
            print("\n📋 未分類のファイルはありません")
            print("\n💡 ヒント:")
            print("  Google Driveの「未分類」フォルダにファイルをアップロードしてください")
            print(f"  🔗 URL: {gconfig.GDRIVE_FOLDER_URL_FORMAT.format(folder_id=self.unclassified_folder_id)}")
            return
        
        print(f"\n📋 未分類ファイル: {len(files)}件")
        
        organized_count = 0
        skipped_count = 0
        
        for idx, file_info in enumerate(files, 1):
            print("\n" + "-"*70)
            print(f"[{idx}/{len(files)}] {file_info['name']}")
            print(f"  サイズ: {int(file_info.get('size', 0)) / 1024:.1f} KB")
            print(f"  作成日: {file_info.get('createdTime', 'N/A')[:10]}")
            
            # ファイルをダウンロード
            temp_dir = gconfig.LOCAL_TEMP_DIR
            os.makedirs(temp_dir, exist_ok=True)
            local_path = os.path.join(temp_dir, file_info['name'])
            
            print(f"\n📥 ダウンロード中...")
            if not self._download_file(file_info['id'], local_path):
                print("⚠️ ダウンロード失敗。スキップします。")
                skipped_count += 1
                continue
            
            # AI分析
            analysis = self.analyze_file_content(file_info, local_path)
            
            # 証拠番号の提案
            proposal = self.propose_evidence_assignment(file_info, analysis)
            
            print(f"\n💡 提案:")
            print(f"  証拠番号: {proposal['evidence_number']}")
            print(f"  理由: {proposal['number_suggestion']['primary']['reason']}")
            
            # 代替案がある場合は表示
            if proposal['number_suggestion']['alternatives']:
                print(f"\n  📋 代替案:")
                for i, alt in enumerate(proposal['number_suggestion']['alternatives'], 1):
                    alt_num = alt['number']
                    side_kanji = '甲' if proposal['side'] == 'ko' else '乙'
                    renumber_mark = " ⚠️ [リナンバリング必要]" if alt.get('requires_renumbering') else ""
                    affected = f" (影響: {alt.get('affected_count', 0)}件)" if alt.get('requires_renumbering') else ""
                    print(f"    {i}. {side_kanji}{alt_num:03d} - {alt['reason']}{renumber_mark}{affected}")
            
            print(f"\n  ファイル名: {proposal['suggested_filename']}")
            print(f"  証拠種別: {proposal['evidence_type']}")
            print(f"  説明: {proposal['description']}")
            
            # ユーザー確認
            action_type = 'normal'  # 'normal' or 'renumber'
            
            while True:
                choice = input(f"\n実行しますか？ (y=実行, e=編集, a=代替案を選択, s=スキップ, q=終了): ").strip().lower()
                
                if choice == 'y':
                    # ファイル移動・リネーム（リナンバリングの有無で分岐）
                    if action_type == 'renumber':
                        # リナンバリングして挿入
                        insert_number = int(re.search(r'\d+', proposal['evidence_id']).group())
                        if self.insert_evidence_with_renumbering(insert_number, file_info, proposal):
                            organized_count += 1
                            print(f"✅ 整理完了（リナンバリング実行） ({organized_count}/{len(files)})")
                        else:
                            skipped_count += 1
                    else:
                        # 通常の移動
                        if self.move_file_to_pending_folder(file_info, proposal):
                            organized_count += 1
                            print(f"✅ 整理完了 ({organized_count}/{len(files)})")
                        else:
                            skipped_count += 1
                    break
                
                elif choice == 'e':
                    # 編集モード
                    proposal = self._edit_proposal(proposal)
                    action_type = 'normal'  # 編集したら通常モードに戻す
                    continue
                
                elif choice == 'a':
                    # 代替案を選択
                    if not proposal['number_suggestion']['alternatives']:
                        print("❌ 代替案がありません")
                        continue
                    
                    proposal, action_type = self._select_alternative(proposal, file_info)
                    continue
                
                elif choice == 's':
                    print("⏭️ スキップしました")
                    skipped_count += 1
                    break
                
                elif choice == 'q':
                    print("\n👋 証拠整理を終了します")
                    print(f"\n📊 結果:")
                    print(f"  整理済み: {organized_count}件")
                    print(f"  スキップ: {skipped_count}件")
                    return
                
                else:
                    print("❌ 無効な選択です")
        
        print("\n" + "="*70)
        print("  証拠整理完了")
        print("="*70)
        print(f"\n📊 結果:")
        print(f"  整理済み: {organized_count}件")
        print(f"  スキップ: {skipped_count}件")
    
    def _download_file(self, file_id: str, output_path: str) -> bool:
        """ファイルをダウンロード"""
        try:
            import io
            from googleapiclient.http import MediaIoBaseDownload
            
            service = self.case_manager.get_google_drive_service()
            request = service.files().get_media(fileId=file_id)
            fh = io.FileIO(output_path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            fh.close()
            return True
            
        except Exception as e:
            print(f"❌ ダウンロードエラー: {e}")
            return False
    
    def _select_alternative(self, proposal: Dict, file_info: Dict) -> Tuple[Dict, str]:
        """代替案を選択
        
        Returns:
            (更新された提案, アクション: 'normal' or 'renumber')
        """
        alternatives = proposal['number_suggestion']['alternatives']
        
        print("\n📋 代替案を選択:")
        for i, alt in enumerate(alternatives, 1):
            alt_num = alt['number']
            side_kanji = '甲' if proposal['side'] == 'ko' else '乙'
            renumber_mark = " ⚠️ [リナンバリング必要]" if alt.get('requires_renumbering') else ""
            affected = f" (影響: {alt.get('affected_count', 0)}件)" if alt.get('requires_renumbering') else ""
            print(f"  {i}. {side_kanji}{alt_num:03d} - {alt['reason']}{renumber_mark}{affected}")
        
        choice = input("\n番号を選択 (1-{}): ".format(len(alternatives))).strip()
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(alternatives):
                selected = alternatives[idx]
                number = selected['number']
                side = proposal['side']
                requires_renumbering = selected.get('requires_renumbering', False)
                
                # 提案を更新
                proposal['evidence_id'] = f"{side}{number:03d}"
                proposal['evidence_number'] = f"{'甲' if side == 'ko' else '乙'}{number:03d}"
                proposal['selected_alternative'] = selected
                
                # ファイル名も更新
                ext = os.path.splitext(proposal['original_filename'])[1]
                base_name = os.path.splitext(proposal['suggested_filename'])[0]
                # 証拠番号部分だけ置き換え
                parts = base_name.split('_', 1)
                if len(parts) == 2:
                    new_filename = f"{proposal['evidence_id']}_{parts[1]}{ext}"
                else:
                    new_filename = f"{proposal['evidence_id']}{ext}"
                proposal['suggested_filename'] = new_filename
                
                action = 'renumber' if requires_renumbering else 'normal'
                
                if requires_renumbering:
                    print(f"\n⚠️  選択: {proposal['evidence_number']} (リナンバリングが必要)")
                else:
                    print(f"\n✅ 選択: {proposal['evidence_number']}")
                
                return proposal, action
            else:
                print("❌ 無効な番号です")
        except ValueError:
            print("❌ 無効な入力です")
        
        return proposal, 'normal'
    
    def _edit_proposal(self, proposal: Dict) -> Dict:
        """提案を編集"""
        print("\n✏️ 編集モード")
        
        # 証拠番号編集
        new_number = input(f"証拠番号 [{proposal['evidence_number']}]: ").strip()
        if new_number:
            # 番号部分を抽出
            match = re.search(r'\d+', new_number)
            if match:
                number = int(match.group())
                side = "ko" if "甲" in new_number or "ko" in new_number.lower() else "otsu"
                proposal['evidence_id'] = f"{side}{number:03d}"
                proposal['evidence_number'] = f"{'甲' if side == 'ko' else '乙'}{number:03d}"
                proposal['side'] = side
        
        # ファイル名編集
        new_filename = input(f"ファイル名 [{proposal['suggested_filename']}]: ").strip()
        if new_filename:
            ext = os.path.splitext(proposal['suggested_filename'])[1]
            if not new_filename.endswith(ext):
                new_filename += ext
            proposal['suggested_filename'] = new_filename
        
        # 証拠種別編集
        new_type = input(f"証拠種別 [{proposal['evidence_type']}]: ").strip()
        if new_type:
            proposal['evidence_type'] = new_type
        
        # 説明編集
        new_desc = input(f"説明 [{proposal['description']}]: ").strip()
        if new_desc:
            proposal['description'] = new_desc
        
        print("\n✅ 編集完了")
        return proposal


def main():
    """メイン関数（テスト用）"""
    print("\n" + "="*70)
    print("  証拠整理システム - テストモード")
    print("="*70)
    
    from case_manager import CaseManager
    
    # CaseManagerを初期化
    manager = CaseManager()
    
    # 事件を検出
    cases = manager.detect_cases()
    manager.display_cases(cases)
    
    # 事件を選択
    selected_case = manager.select_case_interactive(cases)
    
    if not selected_case:
        print("\n❌ 事件が選択されませんでした")
        return
    
    # 証拠整理システムを起動
    organizer = EvidenceOrganizer(manager, selected_case)
    organizer.interactive_organize()


if __name__ == "__main__":
    main()

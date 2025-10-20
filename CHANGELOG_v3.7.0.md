# v3.7.0 変更履歴（2025年10月20日）

## 🎯 証拠の作成年月日に特化 + メニュー構造の大幅簡素化

### 概要
証拠説明書に必要な「証拠の作成年月日」の抽出に特化し、メニュー構造を10項目→7項目に簡素化しました。

---

## 1️⃣ 日付抽出の焦点を「作成年月日」に変更

### 変更の背景
- **問題**: 証拠説明書には「証拠の作成年月日」の記載が必須
- **旧仕様**: 複数の日付を抽出するが、どれが「作成日」か不明確
- **新仕様**: `creation_date`を明示的に特定し、根拠も記録

### データ構造の変更

#### 旧形式（v3.6.1まで）
```json
"temporal_information": {
  "dates_mentioned": ["2021-08-15", "2021-10-20", "2022-01-01"],
  "date_context": "契約日、支払期限、有効期限",
  "timeline": "時系列の整理",
  "primary_date": "2021-08-15"
}
```
**問題点:**
- `dates_mentioned`に複数日付が混在
- `primary_date`の意味が不明確（最重要？作成日？）
- 証拠説明書に記載すべき日付がどれか判断が必要

#### 新形式（v3.7.0以降）
```json
"temporal_information": {
  "creation_date": "2021-08-15",
  "creation_date_source": "契約書末尾の契約締結日",
  "other_dates": [
    {"date": "2021-10-20", "context": "支払期限"},
    {"date": "2022-01-01", "context": "有効期限"}
  ],
  "timeline": "2021年8月15日に契約締結、同年10月20日が支払期限、翌年1月1日から有効"
}
```
**改善点:**
- ✅ `creation_date`で作成年月日を明示
- ✅ `creation_date_source`で根拠を記録
- ✅ その他の日付は`other_dates`に分離
- ✅ 証拠説明書に直接使える情報

### 作成年月日の特定基準

**Phase1プロンプトで以下の優先順を明示:**

1. **文書**: 文書上部の日付、「作成日」「○年○月○日」の明示的記載
2. **契約書**: 契約締結日（署名欄付近の日付）
3. **メール**: 送信日時
4. **領収書・請求書**: 発行日
5. **写真**: 撮影日時（画像内の日付表示、またはEXIFデータ）
6. **その他**: 文脈から推定される作成時期

### プロンプトの変更箇所

**prompts/Phase1_EvidenceAnalysis.txt:**

**変更前（line 62-66）:**
```markdown
4. **重要情報の抽出（特に日付情報は必須）**
   - **日付（最優先）**: 複数ある場合はすべて抽出し、各日付の意味（契約日、作成日、有効期限等）も記録
```

**変更後:**
```markdown
4. **重要情報の抽出（特に作成年月日は必須）**
   - **作成年月日（最優先）**: 文書・画像の作成日を特定（契約書の作成日、メールの送信日、写真の撮影日等）
   - **その他の日付**: 有効期限、支払期限、署名日など、作成日以外の日付も記録
   
   **📝 作成年月日の特定方法:**
   - 文書の場合: 文書上部の日付、「作成日」「○年○月○日」などの明示的記載
   - 契約書の場合: 契約締結日（末尾の署名欄付近の日付）
   - メールの場合: 送信日時
   - 領収書・請求書の場合: 発行日
   - 写真の場合: 撮影日時（画像内の日付表示、EXIFデータ）
```

**変更前（line 220-224）:**
```markdown
## 🗓️ 日付情報の抽出は特に重要
**temporal_informationフィールドは必ず詳細に記入してください:**
1. 文書や画像から読み取れる全ての日付を`dates_mentioned`に記載
2. 各日付の意味・文脈を`date_context`に明確に記述
3. 最も重要な日付を`primary_date`にYYYY-MM-DD形式で記載
```

**変更後:**
```markdown
## 🗓️ 証拠の作成年月日の抽出は最重要
**temporal_informationフィールドは必ず詳細に記入してください:**

### 最優先事項：creation_date（証拠の作成年月日）
1. **必ず特定**: 証拠説明書に記載するため、作成年月日は必須項目です
2. **YYYY-MM-DD形式**: 2021-08-15のように統一形式で記載
3. **根拠を明記**: `creation_date_source`に作成日の根拠を記載
4. **推定も可**: 明示的な日付がない場合、EXIFデータや文脈から推定

### 作成年月日の特定基準（優先順）
1. **文書**: 文書上部の日付、「作成日」「○年○月○日」の明示
2. **契約書**: 契約締結日（署名欄付近の日付）
3. **メール**: 送信日時
4. **領収書・請求書**: 発行日
5. **写真**: 撮影日時（画像内の日付表示、またはEXIFデータ）
6. **その他**: 文脈から推定される作成時期

### その他の日付
- 作成日以外の日付（有効期限、支払期限等）は`other_dates`に記載
- 複数の日付がある場合、時系列順に整理して`timeline`に記載
```

**ai_analyzer_complete.py:**

**変更前（line 201-206）:**
```python
**重要:** 
- 証拠に記載されている事実のみを記録
- 法的評価や主観的解釈は一切含めない
- 訴訟の当事者や事件の詳細は知らない前提で分析
- あなたは中立的な記録者として振る舞う
- **日付情報（temporal_information）は必ず詳細に抽出してください**
```

**変更後:**
```python
**重要:** 
- 証拠に記載されている事実のみを記録
- 法的評価や主観的解釈は一切含めない
- 訴訟の当事者や事件の詳細は知らない前提で分析
- あなたは中立的な記録者として振る舞う
- **証拠の作成年月日（creation_date）は必ず特定してください（証拠説明書記載用）**
```

---

## 2️⃣ メニュー構造の大幅簡素化（10項目 → 7項目）

### 旧メニュー構造の問題点

```
1. 証拠整理 (未分類フォルダから自動整理)
2. 証拠番号を指定して分析 (例: ko70)
3. 範囲指定して分析 (例: ko70-73)          ← 2と重複（入力形式だけの違い）
4. Google Driveから自動検出して分析       ← 実装中（⚠️ 不完全）
5. database.jsonの状態確認
6. 事件を切り替え
7. 並び替え・確定 (整理済み_未確定 -> 甲号証)
8. AI分析で日付抽出・自動ソート (未確定証拠) ← 7と機能が重複
10. AI対話形式で証拠内容を改善           ← 番号が10（9がスキップ）
9. 終了
```

**問題点:**
1. **機能の重複**: メニュー2と3は入力形式が違うだけ
2. **未完成機能**: メニュー4は実装途中で使えない
3. **分離されたワークフロー**: メニュー7と8は実質同じ処理
4. **不自然な番号**: 10→9の順序が混乱を招く

### 新メニュー構造

```
【証拠の整理・分析】
1. 証拠整理 (未分類フォルダ → 整理済み_未確定)
2. 証拠分析 (番号指定: ko70, tmp_001 / 範囲指定: ko70-73)
3. AI対話形式で分析内容を改善

【証拠の確定・管理】
4. 日付順に並び替えて確定 (整理済み_未確定 → 甲号証)

【システム管理】
5. database.jsonの状態確認
6. 事件を切り替え
9. 終了
```

**改善点:**
- ✅ メニュー2+3を統合（入力形式で自動判定）
- ✅ メニュー4削除（未完成機能）
- ✅ メニュー7+8を統合（日付取得とソートを一括処理）
- ✅ メニュー10→3に繰り上げ（論理的な順序）
- ✅ 論理的なグループ分け（整理→分析→確定→管理）
- ✅ 自然な番号並び（1-6, 9）

### 実装の変更

**run_phase1_multi.py:**

**display_main_menu() の変更:**
```python
# 変更前
print("\n実行モード:")
print("  1. 証拠整理 (未分類フォルダから自動整理)")
print("  2. 証拠番号を指定して分析 (例: ko70)")
print("  3. 範囲指定して分析 (例: ko70-73)")
print("  4. Google Driveから自動検出して分析")
print("  5. database.jsonの状態確認")
print("  6. 事件を切り替え")
print("  7. 並び替え・確定 (整理済み_未確定 -> 甲号証)")
print("  8. AI分析で日付抽出・自動ソート (未確定証拠)")
print("  10. AI対話形式で証拠内容を改善")
print("  9. 終了")

# 変更後
print("\n【証拠の整理・分析】")
print("  1. 証拠整理 (未分類フォルダ → 整理済み_未確定)")
print("  2. 証拠分析 (番号指定: ko70, tmp_001 / 範囲指定: ko70-73)")
print("  3. AI対話形式で分析内容を改善")
print("\n【証拠の確定・管理】")
print("  4. 日付順に並び替えて確定 (整理済み_未確定 → 甲号証)")
print("\n【システム管理】")
print("  5. database.jsonの状態確認")
print("  6. 事件を切り替え")
print("  9. 終了")
```

**メインループの変更:**
```python
# 変更前: choice == '2' と choice == '3' が別処理
elif choice == '2':
    evidence_numbers = self.get_evidence_number_input()
    if evidence_numbers:
        for evidence_number in evidence_numbers:
            self.process_evidence(evidence_number, gdrive_file_info)

elif choice == '3':
    evidence_numbers = self.get_evidence_number_input()
    if evidence_numbers:
        print(f"\n処理対象: {', '.join(evidence_numbers)}")
        confirm = input("処理を開始しますか？ (y/n): ").strip().lower()
        if confirm == 'y':
            for evidence_number in evidence_numbers:
                self.process_evidence(evidence_number, gdrive_file_info)

# 変更後: choice == '2' で両方対応
elif choice == '2':
    evidence_numbers = self.get_evidence_number_input()
    if evidence_numbers:
        # 複数件の場合は確認
        if len(evidence_numbers) > 1:
            print(f"\n処理対象: {', '.join(evidence_numbers)}")
            confirm = input("処理を開始しますか？ (y/n): ").strip().lower()
            if confirm != 'y':
                continue
        
        # 分析実行
        for evidence_number in evidence_numbers:
            gdrive_file_info = self._get_gdrive_info_from_database(evidence_number)
            self.process_evidence(evidence_number, gdrive_file_info)
```

---

## 3️⃣ メニュー4「日付順に並び替えて確定」の最適化

### 旧方式の問題点

**メニュー7（並び替え・確定）:**
- 手動で並び替えが必要
- 日付情報を活用できない

**メニュー8（AI日付抽出・自動ソート）:**
- 全証拠に対してAI日付抽出を実行（時間とコストがかかる）
- 既に分析済みでcreation_dateがあっても再抽出

### 新方式の改善点

**メニュー4の処理フロー:**
```
1. 未確定証拠のリストを取得
   ↓
2. 各証拠について:
   ├─ 分析済み（phase1_complete_analysis存在）
   │  └─ objective_analysis.temporal_information.creation_date を使用
   └─ 未分析
      └─ 軽量AI分析で日付抽出（別途API呼び出し）
   ↓
3. 作成年月日順にソート（古い順）
   ↓
4. 確定番号割り当て（ko001, ko002...）
   ↓
5. 甲号証フォルダへ移動
```

**メリット:**
- ✅ 分析済み証拠は再処理不要（高速化、コスト削減）
- ✅ 通常分析で取得したcreation_dateを有効活用
- ✅ 未分析証拠のみ軽量抽出
- ✅ 1つのメニューで完結

### 実装の変更

**analyze_and_sort_pending_evidence() の更新:**

```python
# 変更前: 全証拠に対してAI日付抽出を実行
for idx, evidence in enumerate(pending_evidence, 1):
    # 日付抽出
    date_result = self.ai_analyzer.extract_date_from_evidence(
        evidence_id=evidence['temp_id'],
        file_path=file_path,
        file_type=file_type,
        original_filename=evidence['original_filename']
    )
    evidence['date_extraction'] = date_result
    evidence['extracted_date'] = date_result.get('primary_date')

# 変更後: 既存分析のcreation_dateを優先使用
for idx, evidence in enumerate(pending_evidence, 1):
    # まず、既存のAI分析からcreation_dateを取得
    creation_date = None
    if 'phase1_complete_analysis' in evidence:
        ai_analysis = evidence['phase1_complete_analysis'].get('ai_analysis', {})
        obj_analysis = ai_analysis.get('objective_analysis', {})
        temporal_info = obj_analysis.get('temporal_information', {})
        creation_date = temporal_info.get('creation_date')
        
        if creation_date:
            print(f"  ✅ 既存分析から取得: {creation_date}")
            evidence['extracted_date'] = creation_date
            continue
    
    # 既存分析がない場合のみ、別途日付抽出を実行
    print(f"  ⚠️ 未分析のため日付抽出を実行...")
    date_result = self.ai_analyzer.extract_date_from_evidence(...)
    evidence['extracted_date'] = date_result.get('primary_date')
```

**表示メッセージの更新:**
```python
# 変更前
print("  [1/3] 日付抽出中...")
print("  [2/3] 日付順にソート中...")

# 変更後
print("  [1/3] 作成年月日の取得中...")
print("  [2/3] 作成年月日順にソート中...")
```

---

## 期待される効果

### 1. ユーザビリティの向上
- ✅ メニュー項目が7つに減り、理解しやすい
- ✅ 論理的なグループ分けで迷わない
- ✅ 不自然な番号並びを解消

### 2. 証拠説明書作成の効率化
- ✅ 作成年月日が確実に取得される
- ✅ 根拠（creation_date_source）も記録されて信頼性向上
- ✅ database.jsonから直接証拠説明書に転記可能

### 3. 処理速度とコストの改善
- ✅ 分析済み証拠は再処理不要
- ✅ 不要なAI API呼び出しを削減
- ✅ ワークフローが一本化

### 4. データ構造の明確化
- ✅ 作成日とその他の日付が明確に分離
- ✅ 日付の意味が明確（作成日 vs 支払期限等）
- ✅ プログラムでの解釈が容易

---

## 実装ファイル

**変更されたファイル:**
1. `prompts/Phase1_EvidenceAnalysis.txt` - 作成年月日特定の詳細指示を追加
2. `ai_analyzer_complete.py` - temporal_information構造を更新
3. `run_phase1_multi.py` - メニュー構造と処理ロジックを簡素化

**コミット:**
- `df43a68` - v3.7.0: Focus on creation_date and streamline menu structure
- `e15d051` - docs: Add v3.7.0 documentation

---

## 移行ガイド

### 既存ユーザーへの影響

**データ互換性:**
- ✅ 旧形式（primary_date）も引き続き認識
- ✅ 既存のdatabase.jsonはそのまま使用可能
- ⚠️ 新規分析はcreation_date形式で記録される

**メニュー番号の変更:**
```
旧番号 → 新番号
2, 3  → 2  (統合)
4     → (削除)
7, 8  → 4  (統合)
10    → 3  (繰り上げ)
5, 6, 9 → 5, 6, 9 (変更なし)
```

### 推奨移行手順

1. **最新版の取得**
   ```bash
   cd /path/to/create-junbisyomen
   git pull origin main
   ```

2. **新メニューの確認**
   ```bash
   python3 run_phase1_multi.py
   # メニュー構造が変わっていることを確認
   ```

3. **新規証拠の分析**
   - メニュー2で分析すると自動的にcreation_dateが記録される

4. **既存証拠の再分析（オプション）**
   - 証拠説明書に使う証拠のみ再分析推奨
   - 既存のprimary_dateも使用可能（緊急性低）

---

## 今後の課題

1. **データ移行ツール**
   - 旧形式（primary_date）を新形式（creation_date）に一括変換するツール

2. **証拠説明書自動生成**
   - database.jsonのcreation_dateを使った証拠説明書テンプレート生成

3. **日付検証機能**
   - creation_dateの妥当性を検証（例：未来の日付はエラー）

4. **複数日付の取り扱い**
   - 契約日と署名日が異なる場合の処理ルール明確化

---

**v3.7.0リリース日**: 2025年10月20日  
**担当**: AI Assistant  
**リリースタイプ**: マイナーアップデート（機能改善）

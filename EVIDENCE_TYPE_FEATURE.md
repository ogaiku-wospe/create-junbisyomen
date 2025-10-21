# 証拠種別機能（甲号証/乙号証分離管理）

## 📋 実装概要

証拠を**甲号証（こちら側の証拠）**と**乙号証（相手方の証拠）**に完全に分離して管理できる機能を実装しました。

---

## ✨ 主な機能

### 1. 証拠種別の選択

すべてのメニュー操作で、証拠種別を明示的に選択できます：

```
証拠種別を選択してください:
  1. 甲号証（こちらの証拠）
  2. 乙号証（相手方の証拠）
  3. キャンセル

> 1
```

### 2. 対応メニュー

以下のメニュー項目で証拠種別を選択します：

#### 【証拠の整理・分析】
- **1. 証拠整理** - 未分類フォルダ → 整理済み_未確定
  - 選択した種別の証拠のみを整理
  - ファイル名に種別が反映される

- **2. 証拠分析** - 番号指定 / 範囲指定
  - 選択した種別の証拠のみを分析
  - 証拠番号の接頭辞で区別 (ko001 / otsu001)

- **3. AI対話形式で分析内容を改善**
  - 選択した種別の証拠のみを編集

#### 【証拠の確定・管理】
- **4. 日付順に並び替えて確定**
  - 選択した種別の未確定証拠のみを確定
  - ko001, ko002... または otsu001, otsu002...

#### 【証拠の閲覧】
- **5. 証拠分析一覧を表示**
  - 選択した種別の証拠のみを表示
  - 甲号証/乙号証で完全に分離

- **6. 証拠一覧をエクスポート（CSV/Excel）**
  - 選択した種別の証拠のみをエクスポート
  - ファイル名に種別が含まれる

---

## 📊 エクスポート機能の強化

### CSV形式

```csv
証拠種別,ステータス,証拠番号,仮番号,作成日,分析状態,ファイル名,...
甲号証,確定済み,ko001,tmp_001,2024-01-15,分析済み,契約書.pdf,...
甲号証,整理済み_未確定,,tmp_005,2024-02-10,未分析,請求書.pdf,...
```

**特徴:**
- 最初の列に「証拠種別」を追加
- UTF-8 BOM エンコーディング（Excel対応）
- ファイル名: `evidence_list_[事件名]_ko_[timestamp].csv`

### Excel形式

```
| 証拠種別 | ステータス | 証拠番号 | 仮番号 | 作成日 | 分析状態 | ファイル名 | ...
|----------|-----------|---------|--------|--------|----------|-----------|-----
| 甲号証   | 確定済み   | ko001   | tmp_001| 2024-01-15 | 分析済み | 契約書.pdf | ...
| 甲号証   | 整理済み   |         | tmp_005| 2024-02-10 | 未分析   | 請求書.pdf | ...
```

**特徴:**
- 最初の列に「証拠種別」を追加
- カラフルな書式設定（色分け維持）
- 自動列幅調整
- ファイル名: `evidence_list_[事件名]_otsu_[timestamp].xlsx`

---

## 🔧 技術的な実装詳細

### 1. 新しいメソッド

```python
def select_evidence_type(self) -> Optional[str]:
    """証拠種別を選択
    
    Returns:
        'ko': 甲号証, 'otsu': 乙号証, None: キャンセル
    """
```

### 2. 更新されたメソッドシグネチャ

すべての主要メソッドに `evidence_type` パラメータを追加：

```python
# 証拠番号入力
def get_evidence_number_input(self, evidence_type: str = 'ko') -> Optional[List[str]]

# 証拠処理
def process_evidence(self, evidence_number: str, gdrive_file_info: Dict = None, evidence_type: str = 'ko') -> bool

# AI対話編集
def edit_evidence_with_ai(self, evidence_type: str = 'ko')

# 証拠確定
def analyze_and_sort_pending_evidence(self, evidence_type: str = 'ko')

# 一覧表示
def show_evidence_list(self, evidence_type: str = 'ko')

# エクスポート
def export_evidence_list(self, evidence_type: str = 'ko')
def _export_to_csv(self, evidence_list: List[Dict], filename: str, evidence_type: str = 'ko')
def _export_to_excel(self, evidence_list: List[Dict], filename: str, evidence_type: str = 'ko')

# 証拠整理
def interactive_organize(self, evidence_type: str = 'ko')  # in evidence_organizer.py
```

### 3. データベース構造

証拠データに `evidence_type` フィールドが追加されます：

```json
{
  "evidence_id": "ko001",
  "evidence_type": "ko",
  "temp_id": "tmp_001",
  "status": "確定済み",
  ...
}
```

または

```json
{
  "evidence_id": "otsu001",
  "evidence_type": "otsu",
  "temp_id": "tmp_otsu_001",
  "status": "確定済み",
  ...
}
```

### 4. グローバル設定 (global_config.py)

```python
# 証拠種別の定数
EVIDENCE_TYPE_KO = "ko"      # 甲号証（こちら側の証拠）
EVIDENCE_TYPE_OTSU = "otsu"  # 乙号証（相手側の証拠）

# 証拠種別の表示名
EVIDENCE_TYPE_DISPLAY_NAMES = {
    EVIDENCE_TYPE_KO: "甲号証",
    EVIDENCE_TYPE_OTSU: "乙号証"
}

# 証拠種別とフォルダ名のマッピング
EVIDENCE_TYPE_FOLDER_MAP = {
    EVIDENCE_TYPE_KO: "甲号証",
    EVIDENCE_TYPE_OTSU: "乙号証"
}

# 証拠番号の接頭辞
EVIDENCE_PREFIX_MAP = {
    EVIDENCE_TYPE_KO: "ko",
    EVIDENCE_TYPE_OTSU: "otsu"
}
```

---

## 📁 Google Driveフォルダ構成

```
事件フォルダ/
├── 甲号証/                      # こちら側の確定済み証拠
│   ├── ko001_契約書.pdf
│   ├── ko002_請求書.pdf
│   └── ko003_領収書.pdf
│
├── 乙号証/                      # 相手方の確定済み証拠
│   ├── otsu001_答弁書.pdf
│   ├── otsu002_準備書面1.pdf
│   └── otsu003_証拠説明書.pdf
│
├── 未分類/                      # まだ分類されていない証拠
│   ├── document1.pdf
│   └── image1.jpg
│
├── 整理済み_未確定/             # 仮番号が付与された証拠
│   ├── tmp_ko_001_契約書案.pdf    # 甲号証候補
│   ├── tmp_ko_002_メール.pdf      # 甲号証候補
│   ├── tmp_otsu_001_相手回答.pdf  # 乙号証候補
│   └── tmp_otsu_002_相手資料.pdf  # 乙号証候補
│
└── database.json               # 証拠データベース
```

---

## 🎯 使用例

### 例1: 甲号証の証拠を分析

```
メニューで「2」を選択
→ 証拠種別選択: 「1」（甲号証）
→ 証拠番号入力: tmp_001
→ AI分析実行
→ 結果がデータベースに保存（evidence_type: "ko"）
```

### 例2: 乙号証の一覧をExcelエクスポート

```
メニューで「6」を選択
→ 証拠種別選択: 「2」（乙号証）
→ 出力形式選択: 「2」（Excel）
→ ファイル生成: evidence_list_[事件名]_otsu_20251021_123456.xlsx
→ 乙号証のみが含まれる
```

### 例3: 甲号証の未確定証拠を確定

```
メニューで「4」を選択
→ 証拠種別選択: 「1」（甲号証）
→ 甲号証の未確定証拠が日付順にソート
→ ko001, ko002, ko003... として確定
→ 「整理済み_未確定」→「甲号証」フォルダへ移動
```

---

## ✅ 動作確認項目

実装後、以下の項目を確認してください：

### 証拠種別選択
- [ ] すべてのメニュー項目で証拠種別を選択できるか
- [ ] 甲号証/乙号証の選択が正しく表示されるか
- [ ] キャンセルが正しく動作するか

### 証拠整理
- [ ] 甲号証として整理できるか
- [ ] 乙号証として整理できるか
- [ ] ファイル名に種別が反映されるか

### 証拠分析
- [ ] 甲号証の証拠を分析できるか
- [ ] 乙号証の証拠を分析できるか
- [ ] 証拠番号の接頭辞が正しいか (ko / otsu)

### 証拠確定
- [ ] 甲号証の未確定証拠を確定できるか（ko001, ko002...）
- [ ] 乙号証の未確定証拠を確定できるか（otsu001, otsu002...）
- [ ] フォルダ移動が正しいか

### 一覧表示
- [ ] 甲号証のみを表示できるか
- [ ] 乙号証のみを表示できるか
- [ ] ステータスが正しく表示されるか

### エクスポート
- [ ] CSV: 証拠種別列が含まれているか
- [ ] Excel: 証拠種別列が含まれているか
- [ ] ファイル名に種別が含まれているか (_ko_ / _otsu_)
- [ ] 色分けが正しいか

---

## 🐛 既知の制限事項

### 1. データベース永続化
- `evidence_type` フィールドの保存ロジックが未実装
- 現在は各操作時に動的に判定

**対処予定:**
- 証拠整理時に `evidence_type` を database.json に保存
- 証拠分析時に `evidence_type` を更新
- 証拠確定時に `evidence_type` を維持

### 2. 既存データの移行
- 既存の証拠には `evidence_type` フィールドがない
- デフォルトで 'ko'（甲号証）として扱われる

**対処方法:**
- 既存証拠は手動で種別を指定して再分析
- または、database.json に直接 `evidence_type` を追加

### 3. 混在モード
- 現在は完全分離モード（甲/乙を別々に管理）のみ
- 混在表示機能は未実装

**将来の拡張:**
- 「全て」オプションを追加して混在表示も可能にする

---

## 📚 参考情報

### 関連ファイル

- `run_phase1_multi.py` - メイン実装
- `evidence_organizer.py` - 証拠整理機能
- `global_config.py` - グローバル設定
- `gdrive_database_manager.py` - データベース管理（今後更新予定）

### コミット履歴

```
* 96971e9 feat: Add evidence type (ko/otsu) support for separate management
* 799312b feat: Add complete evidence type separation (ko/otsu)
```

### ブランチ

`fix/evidence-analysis-file-input`

---

## 📞 サポート

問題が発生した場合は、以下の情報を添えてお問い合わせください：

1. 実行したメニュー項目
2. 選択した証拠種別
3. エラーメッセージ全文
4. 証拠番号

---

**最終更新日:** 2025年10月21日  
**実装者:** AI Assistant  
**ステータス:** ✅ 基本機能実装完了（データベース永続化は次のフェーズ）

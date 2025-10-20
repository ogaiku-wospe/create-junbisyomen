# Phase 1 完全版システム - マルチ事件対応版

**大元の共有ドライブIDのみを設定し、複数事件を同時並行で管理できるシステムです。**

## 🎯 新機能

### ✨ マルチ事件対応の特徴

1. **共有ドライブIDの一元管理**
   - `global_config.py` で大元の共有ドライブIDを1回だけ設定
   - 個別事件ごとにフォルダIDを設定する必要がない

2. **事件の自動検出**
   - 共有ドライブ配下のフォルダから事件を自動検出
   - 「甲号証」フォルダが存在するフォルダを事件として認識

3. **複数事件の並行管理**
   - 事件を簡単に切り替え可能
   - 各事件の進捗状況を一覧表示
   - 事件ごとに独立したdatabase.jsonを管理

4. **キャッシュ機能**
   - 事件情報を24時間キャッシュ
   - 高速な事件一覧表示

## 📋 システム構成

### 新規追加ファイル

| ファイル | 説明 | サイズ |
|---------|------|--------|
| **global_config.py** | グローバル設定（共有ドライブID設定） | 7.5KB |
| **case_manager.py** | 事件管理クラス（自動検出・選択） | 16KB |
| **run_phase1_multi.py** | マルチ事件対応実行スクリプト | 18KB |
| **README_MULTI_CASE.md** | このファイル | - |

### 既存ファイル（そのまま使用）

- `metadata_extractor.py` - メタデータ抽出
- `file_processor.py` - ファイル処理
- `ai_analyzer_complete.py` - AI分析エンジン
- その他既存モジュール

## 🚀 クイックスタート

### 1. 共有ドライブIDの設定

`global_config.py` を開いて、大元の共有ドライブIDを設定します：

```python
# global_config.py
SHARED_DRIVE_ROOT_ID = "your-shared-drive-id-here"  # ← ここに設定
```

**共有ドライブIDの取得方法:**
1. Google Driveで共有ドライブを開く
2. ブラウザのURLを確認
3. `https://drive.google.com/drive/folders/【ここがID】` の部分をコピー

### 2. 共有ドライブに事件フォルダを作成

共有ドライブ配下に、以下の構造で事件フォルダを作成します：

```
共有ドライブ（SHARED_DRIVE_ROOT_ID）
├── meiyokison_名誉毀損等損害賠償請求事件/
│   ├── 甲号証/           # ← 必須（証拠ファイルを格納）
│   │   ├── ko001.pdf
│   │   ├── ko002.jpg
│   │   └── ...
│   ├── 乙号証/           # オプション
│   └── database.json     # 自動生成される
│
├── keiyaku_契約違反損害賠償請求事件/
│   ├── 甲号証/
│   └── ...
│
└── 他の事件フォルダ...
```

**重要:** 事件フォルダ内に「**甲号証**」フォルダが存在することで、システムが事件フォルダとして認識します。

### 3. システムの起動

```bash
# マルチ事件対応版を起動
python3 run_phase1_multi.py
```

### 4. 事件の選択

起動すると、自動的に事件一覧が表示されます：

```
======================================================================
  Phase 1完全版システム - 事件一覧
======================================================================

📋 検出された事件: 2件

[1] 名誉毀損等損害賠償請求事件
    📁 フォルダ: meiyokison_名誉毀損等損害賠償請求事件
    🆔 事件ID: meiyokison
    📊 甲号証: 45件
    ✅ 完了: 23件
    🕐 最終更新: 2025-01-15 10:30:45
    🔗 URL: https://drive.google.com/drive/folders/1abc...

[2] 契約違反損害賠償請求事件
    📁 フォルダ: keiyaku_契約違反損害賠償請求事件
    🆔 事件ID: keiyaku
    📊 甲号証: 12件
    ✅ 完了: 0件
    🔗 URL: https://drive.google.com/drive/folders/2def...

事件を選択 (1-2, 0=終了, r=再読み込み): 
```

番号を入力して事件を選択します。

### 5. 証拠の分析

事件を選択後、メインメニューが表示されます：

```
======================================================================
  Phase 1完全版システム - 証拠分析
  📁 事件: 名誉毀損等損害賠償請求事件
======================================================================

【実行モード】
  1. 証拠番号を指定して分析（例: ko70）
  2. 範囲指定して分析（例: ko70-73）
  3. Google Driveから自動検出して分析
  4. database.jsonの状態確認
  5. 事件を切り替え
  6. 終了
----------------------------------------------------------------------

選択してください (1-6): 
```

## 📚 詳細な使用方法

### 事件フォルダの命名規則

システムは以下の命名規則で事件を識別します：

```
{事件ID}_{事件名}
```

例:
- `meiyokison_名誉毀損等損害賠償請求事件`
- `keiyaku_契約違反損害賠償請求事件`
- `case_20250115_損害賠償請求事件`

事件IDは英数字を推奨します（日本語も可能）。

### 事件フォルダの必須要件

システムが事件フォルダとして認識するには、以下のいずれかが必要です：

1. **「甲号証」フォルダが存在** （推奨）
2. `config.json` が存在
3. `database.json` が存在

通常は「甲号証」フォルダを作成するだけでOKです。

### 証拠番号の指定方法

#### 単一証拠の分析
```
証拠番号を入力してください（例: ko70 または ko70-73）: ko70
```

#### 範囲指定での一括分析
```
証拠番号を入力してください（例: ko70 または ko70-73）: ko70-73
```
→ ko70, ko71, ko72, ko73 を順次処理

### Google Driveからの自動検出

メニューで「3. Google Driveから自動検出して分析」を選択すると：

1. 選択中の事件の「甲号証」フォルダ内のファイルを一覧表示
2. 未処理のファイルを検出
3. 自動的にダウンロード・分析（実装中）

### 事件の切り替え

メニューで「5. 事件を切り替え」を選択すると：

1. 事件一覧を再表示
2. 別の事件を選択可能
3. 切り替え後は新しい事件のdatabase.jsonを使用

## 🔧 高度な設定

### global_config.py の主要設定

```python
# 大元の共有ドライブID（必須）
SHARED_DRIVE_ROOT_ID = "0AO6q4_G7DmYSUk9PVA"

# 事件フォルダの命名規則
CASE_FOLDER_NAME_FORMAT = "{case_id}_{case_name}"

# 証拠フォルダの標準名
EVIDENCE_FOLDER_NAME_KO = "甲号証"
EVIDENCE_FOLDER_NAME_OTSU = "乙号証"

# 事件検出の条件
CASE_FOLDER_INDICATORS = [
    "甲号証",        # 甲号証フォルダが存在
    "config.json",   # または config.json が存在
    "database.json"  # または database.json が存在
]

# 自動検出を有効化
AUTO_DETECT_CASES = True

# OpenAI API設定
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-4o"
OPENAI_MAX_TOKENS = 16000
OPENAI_TEMPERATURE = 0.1

# 品質保証設定
QUALITY_THRESHOLDS = {
    'completeness_score': 90.0,
    'confidence_score': 80.0,
    'verbalization_level': 4,
    'metadata_coverage': 95.0
}
```

### キャッシュの管理

事件情報は `~/.phase1_cases_cache.json` にキャッシュされます：

```bash
# キャッシュをクリア
rm ~/.phase1_cases_cache.json

# 次回起動時に自動的に再検出されます
```

または、事件選択画面で `r` を入力すると再読み込みされます。

## 📊 ファイル構造

### プロジェクトディレクトリ

```
create-junbisyomen/
├── global_config.py              # グローバル設定
├── case_manager.py               # 事件管理クラス
├── run_phase1_multi.py           # マルチ事件対応実行スクリプト
├── run_phase1.py                 # 従来版（単一事件）
├── metadata_extractor.py         # メタデータ抽出
├── file_processor.py             # ファイル処理
├── ai_analyzer_complete.py       # AI分析エンジン
├── credentials.json              # Google Drive認証情報
├── .env                          # 環境変数（APIキー）
├── README.md                     # 従来版README
├── README_MULTI_CASE.md          # このファイル
└── prompts/
    └── Phase1_EvidenceAnalysis.txt
```

### 各事件のローカルファイル（自動生成）

システムを実行すると、選択した事件用に以下のファイルが生成されます：

```
create-junbisyomen/
├── current_case.json    # 現在選択中の事件情報
├── database.json        # 選択中の事件のデータベース
└── phase1_multi.log     # 実行ログ
```

**注意:** 事件を切り替えると、`current_case.json` と `database.json` は新しい事件のものに切り替わります。

## 🔄 ワークフロー例

### シナリオ1: 新規事件の追加

1. Google Driveの共有ドライブに新しい事件フォルダを作成
   ```
   shared_drive/
   └── case_20250120_新規事件/
       └── 甲号証/
   ```

2. `run_phase1_multi.py` を起動

3. 自動的に新規事件が検出される

4. 事件を選択して証拠分析を開始

### シナリオ2: 複数事件の並行作業

**午前: 事件A（名誉毀損）の作業**
```bash
python3 run_phase1_multi.py
# → 事件Aを選択
# → ko70-73 を分析
```

**午後: 事件B（契約違反）の作業**
```bash
python3 run_phase1_multi.py
# → 事件Bを選択（または実行中に切り替え）
# → ko01-10 を分析
```

**夕方: 事件Aに戻る**
```bash
python3 run_phase1_multi.py
# → 事件Aを再選択
# → ko74-75 を追加分析
```

### シナリオ3: 進捗確認

```bash
python3 run_phase1_multi.py
# → 事件を選択
# → メニューで「4. database.jsonの状態確認」を選択
```

## 🆚 従来版との比較

| 機能 | 従来版 (run_phase1.py) | マルチ事件対応版 (run_phase1_multi.py) |
|------|----------------------|-----------------------------------|
| **設定の簡便性** | 事件ごとにconfig.pyを編集 | global_config.pyで一元管理 |
| **複数事件の管理** | ❌ ディレクトリごとに分離 | ✅ 1つのシステムで管理 |
| **事件の検出** | ❌ 手動設定 | ✅ 自動検出 |
| **事件の切り替え** | ❌ ディレクトリ移動が必要 | ✅ メニューから即座に切り替え |
| **進捗の確認** | ✅ database.json | ✅ 複数事件の進捗を一覧表示 |
| **Google Drive連携** | ✅ 対応 | ✅ 対応（強化） |

## ⚠️ 重要な注意事項

### 1. セキュリティ

- `credentials.json` と `.env` は絶対にGitHubにアップロードしないでください
- `.gitignore` に以下を追加済み:
  ```
  credentials.json
  token.pickle
  .env
  current_case.json
  database.json
  *.log
  ```

### 2. 事件フォルダの命名

- 事件フォルダ名にスペースは使用可能ですが、アンダースコア `_` での区切りを推奨
- 事件IDは英数字を推奨（日本語も可能）

### 3. Google Drive API制限

- 1日のAPI呼び出し上限: 10,000回
- 大量の証拠がある場合は複数日に分けて処理を推奨

### 4. database.jsonの管理

- 各事件の `database.json` は共有ドライブに保存することを推奨
- ローカルの `database.json` は選択中の事件のものです
- 事件を切り替えると上書きされるため、重要な場合はバックアップを取ってください

## 🐛 トラブルシューティング

### Q1: 事件が検出されない

**確認ポイント:**
1. `global_config.py` の `SHARED_DRIVE_ROOT_ID` が正しいか
2. 共有ドライブへのアクセス権限があるか
3. 事件フォルダ内に「甲号証」フォルダが存在するか
4. Google Drive認証（`credentials.json`）が正しいか

**解決方法:**
```bash
# キャッシュをクリア
rm ~/.phase1_cases_cache.json

# 再起動して 'r' で再読み込み
python3 run_phase1_multi.py
```

### Q2: Google Drive認証エラー

```bash
# token.pickleを削除して再認証
rm token.pickle
python3 run_phase1_multi.py
```

### Q3: OpenAI APIエラー

```bash
# APIキーを確認
echo $OPENAI_API_KEY

# または .env ファイルを確認
cat .env
```

## 📖 関連ドキュメント

- [従来版README](README.md) - 単一事件での使用方法
- [使用ガイド](USAGE_GUIDE.md) - 詳細な使用方法
- [複数事件管理](MULTI_CASE_GUIDE.md) - 従来版の複数事件管理方法
- [Google Drive連携](GOOGLE_DRIVE_GUIDE.md) - Google Drive設定方法

## 🎯 今後の拡張予定

- [ ] 事件ごとの統計ダッシュボード
- [ ] 複数事件の横断検索
- [ ] 証拠の自動分類
- [ ] Webインターフェース
- [ ] チーム共同作業機能

## 📞 サポート

問題が発生した場合:
1. このREADMEの「トラブルシューティング」を確認
2. [Issues](https://github.com/ogaiku-wospe/create-junbisyomen/issues) を検索
3. 新しいIssueを作成

---

**バージョン**: 3.1.0  
**最終更新**: 2025年10月20日  
**対応Phase**: Phase 1（証拠分析・マルチ事件対応）

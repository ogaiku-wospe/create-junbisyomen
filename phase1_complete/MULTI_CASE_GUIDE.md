# Phase 1完全版システム - 複数事件対応ガイド

## 📋 概要

Phase 1完全版システムは**汎用的に設計されており**、どの民事訴訟事件にも使用できます。

このガイドでは、他の事件で使用する方法を説明します。

---

## ✅ 使用可能な事件の種類

Phase 1完全版システムは以下のような事件で使用できます：

- ✅ **名誉毀損・誹謗中傷事件**（デフォルト設定）
- ✅ **契約違反・債務不履行事件**
- ✅ **交通事故・不法行為事件**
- ✅ **労働紛争事件**
- ✅ **知的財産権侵害事件**
- ✅ **不動産関連紛争**
- ✅ **その他の民事訴訟全般**

---

## 🔧 他の事件で使用する方法

### 方法1: セットアップウィザードを使用（推奨・最も簡単）

新規事件用の設定ファイルを**対話形式**で作成します。

```bash
# セットアップウィザードを実行
python3 setup_new_case.py
```

**ウィザードの流れ:**

```
==================================================================
  Phase 1完全版システム - 新規事件セットアップウィザード
==================================================================

このウィザードは、新しい事件用の設定ファイルを作成します。
質問に答えて、事件情報を入力してください。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ステップ1: 事件情報の入力
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【基本情報】
事件ID（英数字、任意） [case_20251019]: contract_dispute_2025
事件名（例: 損害賠償請求事件） []: 売買契約違反損害賠償請求事件
事件番号（例: 令和6年(ワ)第1234号） [未定]: 令和7年(ワ)第5678号

【当事者情報】
原告名 []: 株式会社ABC
被告名 []: 株式会社XYZ
管轄裁判所 [東京地方裁判所]: 大阪地方裁判所

【証拠番号設定】
甲号証の接頭辞（例: ko, kou, k） [ko]: ko
乙号証の接頭辞（例: otsu, otsu, o） [otsu]: otsu

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ステップ2: Google Drive設定
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Google DriveフォルダIDの取得方法:
  1. Google Driveでフォルダを開く
  2. ブラウザのURLを確認
     例: https://drive.google.com/drive/folders/1abc...xyz
  3. 'folders/' の後の文字列がフォルダID

共有ドライブを使用しますか？ (y/n) [n]: y
共有ドライブID []: 0AO6q4_G7DmYSUk9PVA
事件フォルダID（必須） []: 1xxx...yyy
甲号証フォルダID（必須） []: 1zzz...www
乙号証フォルダを設定しますか？ (y/n) [n]: y
乙号証フォルダID []: 1aaa...bbb

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ステップ3: OpenAI API設定
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 環境変数にOpenAI APIキーが設定されています
   キー: sk-proj-xxxxxxxxxxxx...

使用するモデル [gpt-4o]: gpt-4o

==================================================================
  設定内容の確認
==================================================================

【事件情報】
  - 事件ID: contract_dispute_2025
  - 事件名: 売買契約違反損害賠償請求事件
  - 事件番号: 令和7年(ワ)第5678号
  - 原告: 株式会社ABC
  - 被告: 株式会社XYZ
  - 管轄: 大阪地方裁判所

【Google Drive】
  - 共有ドライブID: 0AO6q4_G7DmYSUk9PVA
  - 事件フォルダID: 1xxx...yyy
  - 甲号証フォルダID: 1zzz...www
  - 乙号証フォルダID: 1aaa...bbb

【OpenAI API】
  - モデル: gpt-4o
  - APIキー: 設定済み

==================================================================

この内容で設定ファイルを作成しますか？ (y/n) [y]: y

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ファイルを生成中...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 既存のconfig.pyをバックアップしました: config_backup_20251019_153000.py

✅ config.pyを作成しました: config.py
✅ database.jsonを初期化しました: database.json

==================================================================
  セットアップ完了！
==================================================================

✅ 以下のファイルが作成されました:
  - config.py: 事件専用設定ファイル
  - database.json: 初期化されたデータベース

📋 次のステップ:
  1. OpenAI APIキーを環境変数に設定（未設定の場合）:
     export OPENAI_API_KEY='sk-proj-your-key'

  2. credentials.jsonを配置:
     Google Cloud Consoleからダウンロードして配置

  3. システムを実行:
     python3 run_phase1.py

  4. 証拠ファイルを分析:
     メニューで「1」を選択して証拠番号を入力

==================================================================
```

---

### 方法2: config.pyを手動で編集

設定ファイルを直接編集する方法です。

```bash
# 1. テンプレートをコピー
cp config_template.py config.py

# 2. エディタで開く
# macOS: open -a TextEdit config.py
# Windows: notepad config.py
# Linux: nano config.py

# 3. 以下の項目を変更
```

**変更が必要な項目:**

```python
# ================================
# 事件情報
# ================================

CASE_ID = "contract_dispute_2025"  # 事件ID（英数字）
CASE_NAME = "売買契約違反損害賠償請求事件"  # 事件名
CASE_NUMBER = "令和7年(ワ)第5678号"  # 事件番号

PLAINTIFF = "株式会社ABC"  # 原告名
DEFENDANT = "株式会社XYZ"  # 被告名
COURT = "大阪地方裁判所"  # 管轄裁判所

# ================================
# Google Drive設定
# ================================

SHARED_DRIVE_ID = "0AO6q4_G7DmYSUk9PVA"  # 共有ドライブID
CASE_FOLDER_ID = "1xxx...yyy"  # 事件フォルダID
KO_EVIDENCE_FOLDER_ID = "1zzz...www"  # 甲号証フォルダID
OTSU_EVIDENCE_FOLDER_ID = "1aaa...bbb"  # 乙号証フォルダID（オプション）
```

---

### 方法3: 複数事件を並行管理

複数の事件を同時に管理する方法です。

```bash
# 事件ごとにディレクトリを作成
mkdir -p ~/Documents/phase1_cases/

# 事件1: 名誉毀損事件
cp -r phase1_complete_system ~/Documents/phase1_cases/meiyokison/
cd ~/Documents/phase1_cases/meiyokison/
# config.pyを名誉毀損事件用に設定

# 事件2: 契約違反事件
cp -r phase1_complete_system ~/Documents/phase1_cases/contract_dispute/
cd ~/Documents/phase1_cases/contract_dispute/
# config.pyを契約違反事件用に設定

# 事件3: 交通事故事件
cp -r phase1_complete_system ~/Documents/phase1_cases/traffic_accident/
cd ~/Documents/phase1_cases/traffic_accident/
# config.pyを交通事故事件用に設定
```

**ディレクトリ構造例:**

```
phase1_cases/
├── meiyokison/               # 名誉毀損事件
│   ├── config.py             # 名誉毀損事件専用設定
│   ├── database.json         # 名誉毀損事件の証拠データ
│   ├── credentials.json
│   └── ...
│
├── contract_dispute/         # 契約違反事件
│   ├── config.py             # 契約違反事件専用設定
│   ├── database.json         # 契約違反事件の証拠データ
│   ├── credentials.json
│   └── ...
│
└── traffic_accident/         # 交通事故事件
    ├── config.py             # 交通事故事件専用設定
    ├── database.json         # 交通事故事件の証拠データ
    ├── credentials.json
    └── ...
```

---

## 📁 Google DriveフォルダIDの取得方法

### ステップ1: Google Driveでフォルダを開く

1. Google Drive（https://drive.google.com/）にアクセス
2. 事件用のフォルダを開く

### ステップ2: URLからIDを取得

ブラウザのURLを確認します：

```
https://drive.google.com/drive/folders/1uux0sGt8j3EUI08nOFkBre_99jR8sN-a
                                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                        これがフォルダID
```

### ステップ3: config.pyに設定

```python
CASE_FOLDER_ID = "1uux0sGt8j3EUI08nOFkBre_99jR8sN-a"
```

---

## 🔧 事件種類別の設定例

### 例1: 交通事故損害賠償請求事件

```python
CASE_ID = "traffic_accident_2025"
CASE_NAME = "交通事故損害賠償請求事件"
CASE_NUMBER = "令和7年(ワ)第1234号"
PLAINTIFF = "山田太郎"
DEFENDANT = "佐藤花子"
COURT = "横浜地方裁判所"
```

### 例2: 契約違反損害賠償請求事件

```python
CASE_ID = "contract_breach_2025"
CASE_NAME = "売買契約違反損害賠償請求事件"
CASE_NUMBER = "令和7年(ワ)第5678号"
PLAINTIFF = "株式会社ABC商事"
DEFENDANT = "株式会社XYZ物産"
COURT = "大阪地方裁判所"
```

### 例3: 労働紛争（解雇無効確認）事件

```python
CASE_ID = "labor_dispute_2025"
CASE_NAME = "解雇無効確認等請求事件"
CASE_NUMBER = "令和7年(ワ)第9012号"
PLAINTIFF = "鈴木一郎"
DEFENDANT = "株式会社ブラック企業"
COURT = "東京地方裁判所"
```

### 例4: 不動産関連紛争

```python
CASE_ID = "real_estate_2025"
CASE_NAME = "建物明渡請求事件"
CASE_NUMBER = "令和7年(ワ)第3456号"
PLAINTIFF = "田中地主"
DEFENDANT = "高橋借主"
COURT = "名古屋地方裁判所"
```

---

## ✅ 設定の検証

設定ファイルが正しく作成されたか確認します。

```bash
# 設定内容を表示
python3 -c "import config; config.print_config()"

# または
python3 config.py
```

**期待される出力:**

```
============================================================
  Phase 1完全版システム - 現在の設定
============================================================

📋 事件情報:
  - 事件ID: contract_dispute_2025
  - 事件名: 売買契約違反損害賠償請求事件
  - 事件番号: 令和7年(ワ)第5678号
  - 原告: 株式会社ABC
  - 被告: 株式会社XYZ
  - 管轄: 大阪地方裁判所

📁 Google Drive:
  - 共有ドライブID: 0AO6q4_G7DmYSUk9PVA
  - 事件フォルダID: 1xxx...yyy
  - 甲号証フォルダID: 1zzz...www
  - 乙号証フォルダID: 1aaa...bbb

🤖 OpenAI API:
  - モデル: gpt-4o
  - APIキー: 設定済み

📊 品質保証:
  - 完全性スコア閾値: 90.0%
  - 信頼度スコア閾値: 80.0%
  - 言語化レベル閾値: 4

============================================================

✅ 設定の検証が完了しました
```

---

## 🚀 実行方法

設定が完了したら、通常通りシステムを実行できます。

```bash
# 対話的実行
python3 run_phase1.py

# CLI実行
python3 phase1_cli.py ko1 --file /path/to/evidence.pdf
```

---

## 💾 database.jsonの初期化

新しい事件用に database.json を初期化します。

### 方法1: セットアップウィザード使用時

自動的に初期化されます。

### 方法2: 手動で初期化

```bash
# 既存のdatabase.jsonをバックアップ
mv database.json database_backup_$(date +%Y%m%d_%H%M%S).json

# 新規作成
python3 -c "
import json
from datetime import datetime

database = {
    'case_info': {
        'case_id': 'contract_dispute_2025',
        'case_name': '売買契約違反損害賠償請求事件',
        'case_number': '令和7年(ワ)第5678号',
        'plaintiff': '株式会社ABC',
        'defendant': '株式会社XYZ',
        'court': '大阪地方裁判所'
    },
    'evidence': [],
    'metadata': {
        'version': '3.0',
        'created_at': datetime.now().isoformat(),
        'last_updated': datetime.now().isoformat()
    }
}

with open('database.json', 'w', encoding='utf-8') as f:
    json.dump(database, f, ensure_ascii=False, indent=2)
"
```

---

## 📝 まとめ

### ✅ Phase 1完全版システムは汎用的

- ✅ どの民事訴訟事件にも対応可能
- ✅ 設定ファイル（config.py）を変更するだけ
- ✅ セットアップウィザードで簡単設定
- ✅ 複数事件の並行管理も可能

### 🔧 変更が必要な項目

1. **事件情報**（CASE_NAME, PLAINTIFF, DEFENDANT等）
2. **Google DriveフォルダID**（CASE_FOLDER_ID, KO_EVIDENCE_FOLDER_ID等）
3. **database.jsonの初期化**

### 📋 推奨ワークフロー

```bash
# 1. セットアップウィザードで設定
python3 setup_new_case.py

# 2. 設定を確認
python3 config.py

# 3. システムを実行
python3 run_phase1.py

# 4. 証拠を分析
メニューで証拠番号を入力
```

---

**最終更新:** 2025-10-19  
**バージョン:** 3.0  
**対応範囲:** 民事訴訟全般

# Phase 1完全版システム - 事件選択機能ガイド

## 📋 概要

複数の事件を並行管理している場合に、起動時に事件を選択できる機能です。

---

## 🎯 使用方法

### 方法1: 事件選択スクリプトを直接実行（推奨）

```bash
# 事件選択画面を表示
python3 case_selector.py
```

**実行例:**

```
======================================================================
  Phase 1完全版システム - 事件選択
======================================================================

📋 検出された事件: 3件

   [1] 提起前_名誉毀損等損害賠償請求事件
    📁 パス: /Users/user/Documents/phase1_cases/meiyokison/
    🔢 事件番号: 未定
    👤 原告: 小原瞳（しろくまクラフト）
    👤 被告: 石村まゆか（SUB×MISSION）
    🏛️  裁判所: 東京地方裁判所
    📊 証拠: 6/6 完了
    🕐 最終更新: 2025-10-19 10:55:00

👉 [2] 売買契約違反損害賠償請求事件
    📁 パス: /Users/user/Documents/phase1_cases/contract_dispute/
    🔢 事件番号: 令和7年(ワ)第5678号
    👤 原告: 株式会社ABC
    👤 被告: 株式会社XYZ
    🏛️  裁判所: 大阪地方裁判所
    📊 証拠: 3/10 完了
    🕐 最終更新: 2025-10-18 15:30:00
    ⭐ 最近使用

   [3] 交通事故損害賠償請求事件
    📁 パス: /Users/user/Documents/phase1_cases/traffic_accident/
    🔢 事件番号: 令和7年(ワ)第1234号
    👤 原告: 山田太郎
    👤 被告: 佐藤花子
    🏛️  裁判所: 横浜地方裁判所
    📊 証拠: 0/5 完了
    🕐 最終更新: 2025-10-17 09:15:00

======================================================================

事件を選択してください (1-3, 0: 終了): 2

✅ 選択された事件: 売買契約違反損害賠償請求事件

======================================================================
  Phase 1完全版システムを起動します...
======================================================================

📁 作業ディレクトリ: /Users/user/Documents/phase1_cases/contract_dispute/
📋 事件名: 売買契約違反損害賠償請求事件

[Phase 1システムのメニューが表示されます...]
```

---

## 📁 複数事件の管理方法

### 推奨ディレクトリ構造

```
~/Documents/phase1_cases/
├── meiyokison/                      # 事件1: 名誉毀損事件
│   ├── config.py                    # 事件1専用設定
│   ├── database.json                # 事件1の証拠データ
│   ├── credentials.json
│   ├── token.json
│   └── ... (システムファイル)
│
├── contract_dispute/                # 事件2: 契約違反事件
│   ├── config.py                    # 事件2専用設定
│   ├── database.json                # 事件2の証拠データ
│   ├── credentials.json
│   ├── token.json
│   └── ... (システムファイル)
│
└── traffic_accident/                # 事件3: 交通事故事件
    ├── config.py                    # 事件3専用設定
    ├── database.json                # 事件3の証拠データ
    ├── credentials.json
    ├── token.json
    └── ... (システムファイル)
```

### セットアップ手順

#### ステップ1: ルートディレクトリを作成

```bash
# 複数事件管理用のディレクトリを作成
mkdir -p ~/Documents/phase1_cases/
```

#### ステップ2: 事件ごとにシステムをコピー

```bash
# AI Driveからダウンロードしたシステムをコピー

# 事件1: 名誉毀損事件
cp -r phase1_complete_system ~/Documents/phase1_cases/meiyokison/

# 事件2: 契約違反事件
cp -r phase1_complete_system ~/Documents/phase1_cases/contract_dispute/

# 事件3: 交通事故事件
cp -r phase1_complete_system ~/Documents/phase1_cases/traffic_accident/
```

#### ステップ3: 各事件のconfig.pyを設定

```bash
# 事件1の設定
cd ~/Documents/phase1_cases/meiyokison/
python3 setup_new_case.py
# 名誉毀損事件の情報を入力

# 事件2の設定
cd ~/Documents/phase1_cases/contract_dispute/
python3 setup_new_case.py
# 契約違反事件の情報を入力

# 事件3の設定
cd ~/Documents/phase1_cases/traffic_accident/
python3 setup_new_case.py
# 交通事故事件の情報を入力
```

#### ステップ4: 事件選択スクリプトを実行

```bash
# どこからでも実行可能
cd ~/Documents/phase1_cases/
python3 meiyokison/case_selector.py

# または、事件ディレクトリ内から
cd ~/Documents/phase1_cases/meiyokison/
python3 case_selector.py
```

---

## 🔧 高度な使用方法

### カスタムルートディレクトリを指定

```bash
# デフォルト以外の場所を検索
python3 case_selector.py --cases-dir /path/to/custom/cases/
```

### エイリアスを設定（便利）

```bash
# .bashrc または .zshrc に追加
echo 'alias phase1="python3 ~/Documents/phase1_cases/meiyokison/case_selector.py"' >> ~/.bashrc
source ~/.bashrc

# その後、どこからでも実行可能
phase1
```

---

## 💡 機能の詳細

### 自動検出

事件選択スクリプトは以下を自動的に検出します：

1. **現在のディレクトリ**
   - `config.py` が存在する場合、事件ディレクトリとして認識

2. **~/Documents/phase1_cases/**
   - このディレクトリ内のすべての事件ディレクトリを検出

3. **有効性チェック**
   - `config.py` の存在を確認
   - `database.json` から進捗情報を取得

### 最近使用した事件の記憶

```
~/.phase1_case_selector.json
```

このファイルに最近使用した事件が記録され、次回起動時に👉マークで表示されます。

**内容例:**

```json
{
  "last_used_case": "/Users/user/Documents/phase1_cases/contract_dispute/",
  "recent_cases": [
    "/Users/user/Documents/phase1_cases/contract_dispute/",
    "/Users/user/Documents/phase1_cases/meiyokison/",
    "/Users/user/Documents/phase1_cases/traffic_accident/"
  ]
}
```

### 進捗情報の表示

各事件について以下の情報を表示：

- ✅ 事件名
- ✅ 事件番号
- ✅ 原告・被告
- ✅ 管轄裁判所
- ✅ 証拠の完了数/総数
- ✅ 最終更新日時
- ✅ 最近使用したかどうか

---

## 🔄 ワークフロー例

### 例1: 複数事件の並行作業

```bash
# 朝: 契約違反事件の作業
python3 case_selector.py
# [2] 契約違反事件を選択
# ko10-15を一括処理

# 昼: 名誉毀損事件の確認
python3 case_selector.py
# [1] 名誉毀損事件を選択
# 進捗確認

# 夕方: 交通事故事件の開始
python3 case_selector.py
# [3] 交通事故事件を選択
# 新規証拠を処理
```

### 例2: 事件の途中再開

```bash
# 前回: 契約違反事件で作業中断

# 今回: 事件選択で自動復元
python3 case_selector.py
# [2] 契約違反事件を選択（👉マークが表示）
# database.jsonから進捗が復元され、未処理の証拠から再開
```

---

## 📊 事件情報の表示項目

### 基本情報

| 項目 | 説明 | 取得元 |
|------|------|--------|
| 事件名 | 事件の正式名称 | config.py の CASE_NAME |
| 事件番号 | 裁判所の事件番号 | config.py の CASE_NUMBER |
| 原告 | 原告の氏名・名称 | config.py の PLAINTIFF |
| 被告 | 被告の氏名・名称 | config.py の DEFENDANT |
| 裁判所 | 管轄裁判所 | config.py の COURT |

### 進捗情報

| 項目 | 説明 | 取得元 |
|------|------|--------|
| 証拠完了数 | 処理完了した証拠の数 | database.json の status="completed" |
| 証拠総数 | 登録されている証拠の総数 | database.json の evidence配列の長さ |
| 最終更新 | 最後に更新された日時 | database.json の metadata.last_updated |

---

## 🔍 トラブルシューティング

### 問題1: 事件が検出されない

**症状:**
```
❌ 事件が見つかりませんでした。
```

**解決策:**

1. **config.pyが存在するか確認:**
```bash
ls ~/Documents/phase1_cases/*/config.py
```

2. **正しいディレクトリ構造か確認:**
```bash
# 各事件ディレクトリに config.py が必要
ls ~/Documents/phase1_cases/meiyokison/config.py
```

3. **カスタムパスを指定:**
```bash
python3 case_selector.py --cases-dir /your/custom/path/
```

### 問題2: 事件情報が表示されない

**症状:**
```
⚠️ 警告: /path/to/case/ の情報取得に失敗しました
```

**解決策:**

1. **config.pyが正しいか確認:**
```bash
python3 -c "import sys; sys.path.insert(0, '/path/to/case/'); import config; print(config.CASE_NAME)"
```

2. **database.jsonが存在するか確認:**
```bash
ls /path/to/case/database.json
```

### 問題3: 最近使用した事件がハイライトされない

**症状:**
👉マークが表示されない

**解決策:**

設定ファイルを確認または削除して再生成:
```bash
cat ~/.phase1_case_selector.json

# または、削除して再生成
rm ~/.phase1_case_selector.json
```

---

## 📝 まとめ

### 事件選択機能の利点

1. ✅ **複数事件の並行管理**
   - 事件ごとに独立したdatabase.json
   - 設定の分離

2. ✅ **簡単な切り替え**
   - 1コマンドで事件選択
   - 最近使用した事件を記憶

3. ✅ **進捗の可視化**
   - 各事件の完了状況を一覧表示
   - 最終更新日時を表示

4. ✅ **自動検出**
   - 手動設定不要
   - config.pyがあれば自動認識

### 推奨ワークフロー

```bash
# 1. 事件ディレクトリ構造を作成
mkdir -p ~/Documents/phase1_cases/
cp -r phase1_complete_system ~/Documents/phase1_cases/case1/
cp -r phase1_complete_system ~/Documents/phase1_cases/case2/

# 2. 各事件を設定
cd ~/Documents/phase1_cases/case1/
python3 setup_new_case.py

cd ~/Documents/phase1_cases/case2/
python3 setup_new_case.py

# 3. 事件選択スクリプトで起動
python3 ~/Documents/phase1_cases/case1/case_selector.py

# 4. 事件を選択して作業
# メニューで事件番号を入力
```

---

**最終更新:** 2025-10-19  
**バージョン:** 3.3  
**機能:** 複数事件選択、進捗表示、最近使用記憶

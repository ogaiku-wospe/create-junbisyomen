# Phase 1完全版システム - 事件選択機能ガイド

## 📋 概要

複数の事件を並行管理している場合、起動時に事件を選択できる機能です。

---

## 🎯 事件選択機能の使い方

### 方法1: 事件選択スクリプトで起動

```bash
# 事件選択スクリプトを実行
python3 case_selector.py
```

**実行例:**

```
======================================================================
  Phase 1完全版システム - 事件選択
======================================================================

📋 検出された事件: 3件

[1] 提起前_名誉毀損等損害賠償請求事件
    📁 /Users/you/Documents/phase1_cases/meiyokison/
    📊 証拠: 6/6 完了
    🕐 最終更新: 2025-10-19 10:55:00

[2] 売買契約違反損害賠償請求事件
    📁 /Users/you/Documents/phase1_cases/contract_dispute/
    📊 証拠: 3/10 完了
    🕐 最終更新: 2025-10-18 15:30:00

[3] 交通事故損害賠償請求事件
    📁 /Users/you/Documents/phase1_cases/traffic_accident/
    📊 証拠: 0/5 完了
    🕐 最終更新: 2025-10-17 09:15:00

======================================================================

事件を選択 (1-3, 0=終了): 2

✅ 作業ディレクトリ: /Users/you/Documents/phase1_cases/contract_dispute/
📋 事件: 売買契約違反損害賠償請求事件

[Phase 1システムが起動します...]
```

---

## 📁 複数事件の管理方法

### 推奨ディレクトリ構造

```bash
~/Documents/phase1_cases/
├── meiyokison/                    # 事件1: 名誉毀損事件
│   ├── config.py                  # 名誉毀損事件専用設定
│   ├── database.json              # 名誉毀損事件の証拠データ
│   ├── credentials.json
│   ├── token.json
│   └── [その他のシステムファイル]
│
├── contract_dispute/              # 事件2: 契約違反事件
│   ├── config.py                  # 契約違反事件専用設定
│   ├── database.json              # 契約違反事件の証拠データ
│   ├── credentials.json
│   ├── token.json
│   └── [その他のシステムファイル]
│
└── traffic_accident/              # 事件3: 交通事故事件
    ├── config.py                  # 交通事故事件専用設定
    ├── database.json              # 交通事故事件の証拠データ
    ├── credentials.json
    ├── token.json
    └── [その他のシステムファイル]
```

### セットアップ手順

```bash
# 1. 管理ディレクトリを作成
mkdir -p ~/Documents/phase1_cases/

# 2. 最初の事件をセットアップ
cp -r phase1_complete_system ~/Documents/phase1_cases/meiyokison/
cd ~/Documents/phase1_cases/meiyokison/
python3 setup_new_case.py
# → 名誉毀損事件の情報を入力

# 3. 2つ目の事件をセットアップ
cp -r phase1_complete_system ~/Documents/phase1_cases/contract_dispute/
cd ~/Documents/phase1_cases/contract_dispute/
python3 setup_new_case.py
# → 契約違反事件の情報を入力

# 4. 3つ目の事件をセットアップ
cp -r phase1_complete_system ~/Documents/phase1_cases/traffic_accident/
cd ~/Documents/phase1_cases/traffic_accident/
python3 setup_new_case.py
# → 交通事故事件の情報を入力
```

---

## 🚀 使用方法

### ケース1: 事件選択スクリプトから起動

```bash
# どこからでも実行可能
cd ~/Documents/phase1_cases/
python3 meiyokison/case_selector.py

# または、どれかの事件ディレクトリから
cd ~/Documents/phase1_cases/meiyokison/
python3 case_selector.py
```

### ケース2: 特定の事件ディレクトリで直接起動

```bash
# 事件ディレクトリに移動
cd ~/Documents/phase1_cases/contract_dispute/

# 直接起動（事件選択をスキップ）
python3 run_phase1.py
```

### ケース3: エイリアスを設定（便利）

```bash
# ~/.bashrc または ~/.zshrc に追加
alias phase1='python3 ~/Documents/phase1_cases/meiyokison/case_selector.py'

# ターミナルを再起動後、どこからでも起動可能
phase1
```

---

## 🔄 途中再開の流れ

### シナリオ: 契約違反事件の続きを処理

```bash
# 1. 事件選択スクリプトを起動
python3 case_selector.py

# 2. 契約違反事件を選択
事件を選択 (1-3, 0=終了): 2

# 3. Phase 1システムが起動
# → 自動的に contract_dispute/ ディレクトリに移動
# → database.json を読み込み
# → 未処理の証拠を表示

# 4. メニューで「5」を選択して進捗確認
選択してください (1-6): 5

📊 証拠統計:
  - 総証拠数: 10
  - 完了: 3
  - 処理中: 0

📝 証拠一覧:
  ✅ ko1  （完了）
  ✅ ko2  （完了）
  ✅ ko3  （完了）
  ❌ ko4  （未処理）← 次はこれ
  ❌ ko5  （未処理）
  ...

# 5. 未処理の証拠を処理
選択してください (1-6): 2
証拠番号を入力: ko4-10

# 6. 一括処理が開始
```

---

## 📊 事件情報の確認

### 各事件のdatabase.jsonで確認できる情報

```bash
cd ~/Documents/phase1_cases/contract_dispute/
cat database.json | python3 -m json.tool | less
```

**表示内容:**
- 事件名
- 原告・被告
- 証拠数
- 完了済み証拠数
- 最終更新日時
- 各証拠の詳細

---

## 💡 ベストプラクティス

### 1. 事件ごとに独立したGoogle Drive設定

```python
# meiyokison/config.py
CASE_FOLDER_ID = "1uux0sGt8j3EUI08nOFkBre_99jR8sN-a"  # 名誉毀損事件フォルダ

# contract_dispute/config.py
CASE_FOLDER_ID = "1xxx...yyy"  # 契約違反事件フォルダ

# traffic_accident/config.py
CASE_FOLDER_ID = "1zzz...www"  # 交通事故事件フォルダ
```

### 2. 事件ごとに独立したcredentials.json

各事件ディレクトリに個別のcredentials.jsonを配置することを推奨します。

```bash
# 各事件に同じcredentials.jsonをコピー
cp ~/Downloads/credentials.json ~/Documents/phase1_cases/meiyokison/
cp ~/Downloads/credentials.json ~/Documents/phase1_cases/contract_dispute/
cp ~/Downloads/credentials.json ~/Documents/phase1_cases/traffic_accident/
```

### 3. 定期的なバックアップ

```bash
# 各事件のdatabase.jsonをバックアップ
for case in ~/Documents/phase1_cases/*/; do
    cp "$case/database.json" "$case/database_backup_$(date +%Y%m%d).json"
done
```

---

## 🛠️ トラブルシューティング

### 問題1: 事件が検出されない

**原因:**
- config.pyが存在しないディレクトリ
- 権限の問題

**解決策:**
```bash
# 各事件ディレクトリにconfig.pyがあるか確認
ls -la ~/Documents/phase1_cases/*/config.py

# ない場合は setup_new_case.py を実行
cd ~/Documents/phase1_cases/your_case/
python3 setup_new_case.py
```

### 問題2: 間違った事件を選択してしまった

**解決策:**
```bash
# Ctrl+C で中断
# 再度 case_selector.py を実行
python3 case_selector.py
```

### 問題3: 事件の追加方法

**手順:**
```bash
# 1. 新しい事件ディレクトリを作成
cp -r phase1_complete_system ~/Documents/phase1_cases/new_case/

# 2. 事件情報をセットアップ
cd ~/Documents/phase1_cases/new_case/
python3 setup_new_case.py

# 3. 次回起動時に自動的に検出される
python3 case_selector.py
```

---

## 📝 まとめ

### 事件選択機能の利点

- ✅ **複数事件を並行管理**: 事件ごとに独立した設定・データ
- ✅ **簡単な切り替え**: 1コマンドで事件を選択
- ✅ **進捗の可視化**: 各事件の進捗を一目で確認
- ✅ **途中再開が簡単**: 未処理の証拠を自動検出

### 推奨ワークフロー

```bash
# 1. 事件選択スクリプトを起動
python3 case_selector.py

# 2. 処理したい事件を選択
事件を選択 (1-3, 0=終了): 2

# 3. Phase 1システムで作業
# → 進捗確認
# → 証拠処理
# → 品質確認

# 4. 別の事件に切り替え
# → 終了してから再度 case_selector.py を実行
```

---

**最終更新:** 2025-10-19  
**バージョン:** 3.2  
**機能:** 事件選択、並行管理

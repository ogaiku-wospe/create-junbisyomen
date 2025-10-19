# Phase 1完全版システム - 途中再開と一括分析ガイド

## 📋 目次

1. [途中から再開する方法](#途中から再開する方法)
2. [一括分析の方法](#一括分析の方法)
3. [進捗確認](#進捗確認)
4. [エラー対処](#エラー対処)

---

## 🔄 途中から再開する方法

### 基本原理

Phase 1完全版システムは**自動的に進捗を保存**します：

- ✅ **database.jsonに保存**: 処理が完了するたびに自動保存
- ✅ **重複処理を回避**: 完了済み証拠は自動的にスキップ
- ✅ **いつでも再開可能**: 中断してもdatabase.jsonから状態を復元

---

### 方法1: 対話的実行で再開（初心者向け）

```bash
# システムディレクトリに移動
cd ~/Documents/phase1_complete_system/

# システムを起動
python3 run_phase1.py
```

**メニューが表示されます:**

```
==============================================================
  Phase 1完全版システム - 証拠分析
==============================================================

【実行モード】
  1. 証拠番号を指定して分析（例: ko70）
  2. 範囲指定して分析（例: ko70-73）
  3. 個別ファイルを分析（Google Drive URL指定）
  4. 未処理の証拠を自動検索・分析
  5. database.jsonの状態確認  ← まずはこれで進捗確認
  6. 終了
--------------------------------------------------------------

選択してください (1-6):
```

#### ステップ1: 進捗を確認

```
選択してください (1-6): 5
```

**出力例:**

```
==============================================================
  database.json 状態確認
==============================================================

📁 事件情報:
  - 事件名: 提起前_名誉毀損等損害賠償請求事件
  - 原告: 小原瞳（しろくまクラフト）
  - 被告: 石村まゆか（SUB×MISSION）

📊 証拠統計:
  - 総証拠数: 6
  - 完了: 6
  - 処理中: 0

📝 証拠一覧:
  ✅ ko62  （完了 - 2025-10-19 10:30:00）
  ✅ ko63  （完了 - 2025-10-19 10:35:00）
  ✅ ko64  （完了 - 2025-10-19 10:40:00）
  ✅ ko65  （完了 - 2025-10-19 10:45:00）
  ✅ ko66  （完了 - 2025-10-19 10:50:00）
  ✅ ko67  （完了 - 2025-10-19 10:55:00）

📋 次に処理すべき証拠:
  ❌ ko70  （未処理）← 次はこれ
  ❌ ko71  （未処理）
  ❌ ko72  （未処理）
  ❌ ko73  （未処理）
```

#### ステップ2: 未処理の証拠を処理

```
選択してください (1-6): 2

証拠番号を入力してください: ko70-73

📋 処理対象: ko70, ko71, ko72, ko73
処理を開始しますか？ (y/n): y

[処理開始...]
```

---

### 方法2: CLIで再開（上級者向け）

```bash
# 未処理の証拠を一括処理
python3 phase1_cli.py ko70 ko71 ko72 ko73 --file-dir /path/to/evidence_files/

# または範囲指定
python3 batch_process.py --range ko70-73 --directory /path/to/evidence_files/
```

---

### 方法3: 自動再開（最も簡単）

未処理の証拠を**自動的に検出して処理**します。

```bash
# 未処理の証拠を自動検出して一括処理
python3 batch_process.py --auto --directory /path/to/evidence_files/
```

**実行例:**

```
==================================================================
  一括処理開始
  処理対象: 4件
==================================================================

📋 未処理の証拠を検出しました: ['ko70', 'ko71', 'ko72', 'ko73']

[1/4] 処理中: ko70
======================================================================
  証拠 ko70 の処理開始
======================================================================
📁 ファイル: /path/to/evidence_files/ko70.pdf
📊 メタデータを抽出中...
  ✅ SHA-256: abc123def456...
  ✅ サイズ: 3200.50 KB
🔧 ファイルを処理中...
  ✅ タイプ: PDF
  ✅ 抽出画像数: 15
🤖 AI分析を実行中（GPT-4o Vision）...
📈 品質評価:
  ✅ 完全性: 95.0%
  ✅ 信頼度: 90.0%
  ✅ 言語化レベル: 4
💾 database.jsonに保存中...
  ✅ 新規エントリを追加

✅ 証拠 ko70 の処理が完了しました！

📊 現在の進捗:
  ✅ 成功: 1
  ⏭️  スキップ: 0
  ❌ 失敗: 0
  📈 進捗率: 1/4 (25.0%)

[2/4] 処理中: ko71
...
```

---

## 📦 一括分析の方法

複数の証拠を一度に処理する方法を説明します。

---

### 方法1: 範囲指定で一括分析

#### 対話的実行の場合

```bash
python3 run_phase1.py

# メニューで「2」を選択
選択してください (1-6): 2

# 範囲を入力
証拠番号を入力してください: ko70-73
```

#### CLIの場合

```bash
# batch_process.pyを使用
python3 batch_process.py --range ko70-73 --directory /path/to/evidence_files/
```

**処理される証拠:**
- ko70
- ko71
- ko72
- ko73

---

### 方法2: 証拠番号を個別指定

```bash
# 複数の証拠番号を指定
python3 batch_process.py \
    --evidence ko70 ko71 ko72 ko73 \
    --directory /path/to/evidence_files/
```

---

### 方法3: ディレクトリ内のすべてを一括処理

```bash
# ディレクトリ内の証拠ファイルをすべて処理
python3 batch_process.py \
    --evidence ko70 ko71 ko72 ko73 ko74 ko75 \
    --directory /path/to/evidence_files/
```

---

### 方法4: 自動検出で一括処理（推奨）

```bash
# 未処理の証拠を自動検出して一括処理
python3 batch_process.py --auto --directory /path/to/evidence_files/
```

**メリット:**
- ✅ 手動で証拠番号を指定する必要なし
- ✅ database.jsonから未処理を自動検出
- ✅ 完了済み証拠は自動的にスキップ

---

## 📊 進捗確認の方法

### 方法1: 対話的実行で確認

```bash
python3 run_phase1.py

# メニューで「5」を選択
選択してください (1-6): 5
```

### 方法2: database.jsonを直接確認

```bash
# database.jsonを表示
cat database.json | python3 -m json.tool | less

# または、証拠一覧だけを表示
python3 -c "
import json
with open('database.json', 'r') as f:
    db = json.load(f)
    
print('証拠一覧:')
for e in db['evidence']:
    status = '✅' if e.get('status') == 'completed' else '❌'
    number = e.get('evidence_number', 'N/A')
    processed_at = e.get('processed_at', 'N/A')
    print(f'{status} {number} - {processed_at}')
"
```

### 方法3: ログファイルを確認

```bash
# 最新のログを表示
tail -f phase1_complete.log

# または、処理済み証拠を確認
grep "処理が完了しました" phase1_complete.log
```

---

## 🔧 コマンドラインオプション詳細

### batch_process.py のオプション

```bash
# 基本形式
python3 batch_process.py [証拠指定] [ファイル指定] [オプション]
```

#### 証拠指定（いずれか1つ必須）

| オプション | 説明 | 例 |
|-----------|------|-----|
| `--evidence` | 証拠番号のリスト | `--evidence ko70 ko71 ko72` |
| `--range` | 証拠番号の範囲 | `--range ko70-73` |
| `--auto` | 未処理を自動検出 | `--auto` |

#### ファイル指定（必須）

| オプション | 説明 | 例 |
|-----------|------|-----|
| `--directory` | 証拠ファイルのディレクトリ | `--directory /path/to/evidence/` |

#### その他のオプション

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `--skip-completed` | 完了済み証拠をスキップ | True |
| `--output` | 出力先database.jsonのパス | `database.json` |

---

## 📝 使用例

### 例1: ko70-73を一括処理

```bash
python3 batch_process.py \
    --range ko70-73 \
    --directory ~/Downloads/evidence_files/
```

### 例2: 未処理の証拠を自動検出して処理

```bash
python3 batch_process.py \
    --auto \
    --directory ~/Downloads/evidence_files/
```

### 例3: 特定の証拠だけを処理

```bash
python3 batch_process.py \
    --evidence ko70 ko72 \
    --directory ~/Downloads/evidence_files/
```

### 例4: 完了済みも再処理する

```bash
python3 batch_process.py \
    --range ko62-67 \
    --directory ~/Downloads/evidence_files/ \
    --skip-completed=False
```

### 例5: カスタム出力先を指定

```bash
python3 batch_process.py \
    --auto \
    --directory ~/Downloads/evidence_files/ \
    --output custom_database.json
```

---

## 🚦 処理の流れ

### 一括処理の流れ

```
1. database.jsonの読み込み
   ↓
2. 証拠番号のリスト作成
   ↓
3. 完了済み証拠のスキップ判定
   ↓
4. 各証拠の処理ループ
   │
   ├─ ファイル存在確認
   ├─ メタデータ抽出
   ├─ ファイル処理
   ├─ AI分析
   ├─ 品質評価
   └─ database.jsonに保存
   ↓
5. 最終レポート表示
```

### 進捗表示の例

```
[1/4] 処理中: ko70
  ✅ 成功
  📊 進捗: 1/4 (25.0%)

[2/4] 処理中: ko71
  ✅ 成功
  📊 進捗: 2/4 (50.0%)

[3/4] 処理中: ko72
  ⏭️  スキップ（完了済み）
  📊 進捗: 3/4 (75.0%)

[4/4] 処理中: ko73
  ✅ 成功
  📊 進捗: 4/4 (100.0%)

======================================================================
  一括処理完了
======================================================================

📊 処理結果:
  ✅ 成功: 3
  ⏭️  スキップ: 1
  ❌ 失敗: 0
  📊 合計: 4

⏱️  処理時間:
  - 総処理時間: 0:15:30
  - 平均処理時間: 310.0秒/件
```

---

## 🛠️ エラー対処

### エラー1: ファイルが見つからない

**エラーメッセージ:**
```
❌ ファイルが見つかりません: /path/to/ko70.pdf
```

**解決策:**
```bash
# ファイルの存在を確認
ls -lh /path/to/evidence_files/

# ファイル名を確認（拡張子が正しいか）
ls /path/to/evidence_files/ | grep ko70

# 正しいディレクトリを指定
python3 batch_process.py --range ko70-73 --directory /correct/path/
```

---

### エラー2: OpenAI APIエラー

**エラーメッセージ:**
```
❌ エラーが発生しました: openai.error.RateLimitError
```

**解決策:**
```bash
# APIレート制限に達した場合は待機
# batch_process.pyは自動的に2秒間隔を空けますが、
# それでもエラーが出る場合は手動で少しずつ処理

# 1件ずつ処理（確実）
python3 phase1_cli.py ko70 --file /path/to/ko70.pdf
# 少し待機
sleep 10
python3 phase1_cli.py ko71 --file /path/to/ko71.pdf
```

---

### エラー3: メモリ不足

**エラーメッセージ:**
```
❌ MemoryError: Unable to allocate array
```

**解決策:**

1. **config.pyで設定を調整:**

```python
# PDF処理の最大ページ数を減らす
PDF_MAX_PAGES = 50  # デフォルト100から削減

# 画像の最大サイズを減らす
IMAGE_MAX_SIZE = (1920, 1080)  # デフォルト(3840, 2160)から削減
```

2. **一度に処理する証拠数を減らす:**

```bash
# 2件ずつ処理
python3 batch_process.py --evidence ko70 ko71 --directory /path/
python3 batch_process.py --evidence ko72 ko73 --directory /path/
```

---

### エラー4: 一部の証拠が失敗した

**エラーメッセージ:**
```
❌ 失敗した証拠:
  - ko72: PDF processing error
```

**解決策:**

1. **失敗した証拠だけを再処理:**

```bash
python3 phase1_cli.py ko72 --file /path/to/ko72.pdf --verbose
```

2. **ログを確認してエラー原因を特定:**

```bash
grep "ko72" phase1_complete.log
grep "ERROR" phase1_complete.log
```

3. **必要に応じてファイルを修復:**
   - PDFが破損している場合は再ダウンロード
   - 画像が開けない場合は形式変換

---

## 💡 ベストプラクティス

### 1. 定期的なバックアップ

```bash
# database.jsonを定期的にバックアップ
cp database.json database_backup_$(date +%Y%m%d_%H%M%S).json
```

### 2. ログの確認

```bash
# 処理中はログをリアルタイム監視
tail -f phase1_complete.log
```

### 3. 段階的な処理

大量の証拠がある場合は、少しずつ処理：

```bash
# 5件ずつ処理
python3 batch_process.py --range ko70-74 --directory /path/
python3 batch_process.py --range ko75-79 --directory /path/
python3 batch_process.py --range ko80-84 --directory /path/
```

### 4. 品質チェック

処理後は品質を確認：

```bash
# database.jsonの状態確認
python3 run_phase1.py
# メニューで「5」を選択

# 品質スコアをチェック
python3 -c "
import json
with open('database.json', 'r') as f:
    db = json.load(f)

print('品質スコア一覧:')
for e in db['evidence']:
    number = e.get('evidence_number', 'N/A')
    scores = e.get('phase1_complete_analysis', {}).get('quality_scores', {})
    completeness = scores.get('completeness_score', 0)
    confidence = scores.get('confidence_score', 0)
    print(f'{number}: 完全性={completeness:.1f}%, 信頼度={confidence:.1f}%')
"
```

---

## 📋 まとめ

### 途中から再開

- ✅ **自動進捗保存**: database.jsonに自動保存
- ✅ **重複回避**: 完了済み証拠は自動スキップ
- ✅ **いつでも再開**: 中断しても安心

### 一括分析

- ✅ **範囲指定**: `--range ko70-73`
- ✅ **自動検出**: `--auto`
- ✅ **個別指定**: `--evidence ko70 ko71 ko72`

### 推奨ワークフロー

```bash
# 1. 進捗確認
python3 run_phase1.py
# メニューで「5」を選択

# 2. 一括処理
python3 batch_process.py --auto --directory /path/to/evidence_files/

# 3. 品質確認
python3 run_phase1.py
# メニューで「5」を選択
```

---

**最終更新:** 2025-10-19  
**バージョン:** 3.1  
**機能:** 途中再開、一括分析対応

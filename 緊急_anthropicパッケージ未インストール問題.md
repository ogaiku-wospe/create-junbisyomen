# ❌ 緊急: anthropicパッケージ未インストール問題

## 🔍 問題の診断

OCR改善が全く動作していない根本原因が判明しました：

```
❌ インポートエラー: No module named 'anthropic'
```

### 影響

- **段階的分析システムが起動しない**
- **`full_content`が空になる**（総文字数: 0）
- **OCR改善が全く適用されない**
- **Claude Vision APIが使用できない**

---

## ✅ 解決方法

### ステップ1: anthropicパッケージのインストール

```bash
# 仮想環境が有効化されていることを確認
# プロンプトに (venv) が表示されているはず

# anthropicをインストール
pip3 install anthropic>=0.39.0
```

**期待される出力**:
```
Collecting anthropic>=0.39.0
  Downloading anthropic-0.39.0-py3-none-any.whl
...
Successfully installed anthropic-0.39.0
```

### ステップ2: インストール確認

```bash
# バージョン確認
pip3 show anthropic
```

**期待される出力**:
```
Name: anthropic
Version: 0.39.0 (またはそれ以上)
Summary: The official Python library for the anthropic API
...
```

### ステップ3: インポート確認

```bash
# Pythonで確認
python3 -c "import anthropic; print(f'anthropic {anthropic.__version__} インストール済み')"
```

**期待される出力**:
```
anthropic 0.39.0 インストール済み
```

### ステップ4: 段階的分析モジュールの確認

```bash
# StepwiseAnalyzerがインポートできるか確認
python3 -c "
from src.ai_analyzer_stepwise import StepwiseAnalyzer
print('✅ StepwiseAnalyzerをインポートできました')
print('✅ 段階的分析システムが利用可能です')
"
```

**期待される出力**:
```
✅ StepwiseAnalyzerをインポートできました
✅ 段階的分析システムが利用可能です
```

---

## 🔄 再分析の実行

anthropicインストール後、証拠を再分析してください：

### tmp_ko_004の再分析

```bash
python3 run_phase1_multi.py
```

プロンプトで:
1. 事件選択
2. **「1. 個別証拠を分析」**
3. **「tmp_ko_004」** を選択

### tmp_ko_013の再分析

同様に：
1. 事件選択
2. 「1. 個別証拠を分析」
3. **「tmp_ko_013」** を選択

---

## 🔍 正しく動作しているかの確認

### コンソールログで以下を確認：

#### ✅ 段階的分析の開始ログ
```
🎯 段階的分析開始: tmp_ko_004 (3ページ)
```

もしこれが表示されない場合、まだanthropicの問題があります。

#### ✅ 各ステップのログ
```
📊 [1/6] メタデータ抽出
   ✅ メタデータ抽出完了: 250文字
📄 [2/6] OCRテキスト抽出
   📄 ページ1のOCR実行中...
   ✅ ページ1完了: 450文字
   📄 ページ2のOCR実行中...
   ✅ ページ2完了: 680文字
   📄 ページ3のOCR実行中...
   ✅ ページ3完了: 520文字
   ✅ OCRテキスト抽出完了: 1650文字（3ページ）
📋 [3/6] 文書内容分析
⚖️ [4/6] 法的意義抽出
🔍 [5/6] 関連事実抽出
🔗 [6/6] 最終統合
🎉 段階的分析完了: tmp_ko_004
```

#### ✅ 画像品質ログ
```
📷 ページ1画像: tmp_ko_004_page1_xxx.jpg
   サイズ: 2480x3508px, 850,234 bytes, JPEG品質95%
```

---

## ❓ なぜrequirements.txtがあるのにインストールされていないのか

`requirements.txt`には`anthropic>=0.39.0`が含まれていますが、インストールされていません。

### 考えられる原因

1. **`pip3 install -r requirements.txt`を実行していない**
2. **仮想環境が別のもの**（複数のvenvがある）
3. **インストール時にエラーが発生していた**（気づかなかった）

### 解決策

```bash
# requirements.txtから全パッケージを再インストール
pip3 install -r requirements.txt

# または、個別にanth

ropicのみインストール
pip3 install anthropic>=0.39.0
```

---

## 📊 期待される改善結果

### tmp_ko_004

#### 改善前（database 22.json）
```
総文字数: 0
ページ数: 0
full_content: {}
```

#### 改善後（期待値）
```
総文字数: 1650+
ページ数: 3
ページ1: 450文字（配達証明ヘッダー）
ページ2: 680文字（本文 - 画像ベース）← 最重要！
ページ3: 520文字（差出人・受取人詳細）
```

### tmp_ko_013

#### 改善前（database 22.json）
```
総文字数: 0
ページ数: 0
full_content: {}
```

#### 改善後（期待値）
```
総文字数: 不明（PDFによる）
ページ数: 1以上
各ページ: 適切な文字数抽出
(cid:X)エラー: 大幅に削減（Claude Vision OCR使用）
```

**Note**: tmp_ko_013のPDFプレビューで`(cid:1)`パターンが多数見られました。これはフォント埋め込みの問題で、Claude Vision OCRを使えば改善されるはずです。

---

## 🔧 トラブルシューティング

### Q1: pip3 installでエラーが出る

```bash
# pipを最新版にアップグレード
pip3 install --upgrade pip

# 再度インストール
pip3 install anthropic>=0.39.0
```

### Q2: 仮想環境が有効化されているか不明

```bash
# 現在のPythonパスを確認
which python3

# 仮想環境内のpipを使用
python3 -m pip install anthropic>=0.39.0
```

### Q3: インストール成功したがインポートできない

```bash
# Pythonキャッシュをクリア
find . -type d -name '__pycache__' -exec rm -r {} + 2>/dev/null
find . -type f -name '*.pyc' -delete

# Python再起動
python3 -c "import anthropic; print('OK')"
```

### Q4: 「段階的分析開始」ログが表示されない

**原因**: まだanthropicのインポートエラーがある

**確認**:
```bash
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from src.ai_analyzer_stepwise import StepwiseAnalyzer
    print('✅ OK')
except Exception as e:
    print(f'❌ エラー: {e}')
"
```

---

## ✅ 確認チェックリスト

anthropicインストール後:

- [ ] `pip3 show anthropic`でバージョン確認
- [ ] `import anthropic`が成功
- [ ] `StepwiseAnalyzer`がインポート可能
- [ ] tmp_ko_004を再分析実行
- [ ] tmp_ko_013を再分析実行
- [ ] コンソールログで「🎯 段階的分析開始」を確認
- [ ] コンソールログで「[1/6]〜[6/6]」を確認
- [ ] database.jsonで`full_content`が埋まっている
- [ ] 総文字数が0ではない

**全てチェック完了**: ✅ OCR改善が正常に動作しています

**一部チェック失敗**: このドキュメントのトラブルシューティングを参照

---

## 📝 まとめ

### 根本原因
```
❌ No module named 'anthropic'
```

### 解決手順
```bash
# 1. anthropicインストール
pip3 install anthropic>=0.39.0

# 2. 確認
python3 -c "import anthropic; print('OK')"

# 3. Pythonキャッシュクリア
find . -type d -name '__pycache__' -exec rm -r {} + 2>/dev/null

# 4. 再分析実行
python3 run_phase1_multi.py
```

### 期待される結果
- tmp_ko_004: 総文字数 0 → 1650+
- tmp_ko_013: 総文字数 0 → 適切な値
- (cid:X)エラー大幅削減

---

**作成日**: 2025-11-06  
**問題**: anthropicパッケージ未インストール  
**影響**: 段階的分析システム完全停止  
**優先度**: 🔴 最高（これを解決しないとOCR改善は動作しません）

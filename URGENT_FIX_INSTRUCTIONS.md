# 🚨 緊急: tmp_ko_004 分析エラーの解決手順

## 問題の状況

ログを見ると、**最新の修正が実行されていません**：

```
✅ PDF全ページ分析: 3ページ
HTTP Request: POST https://api.openai.com/v1/chat/completions  ← OpenAIを先に呼んでいる（古いコード）
⚠️ OpenAI Vision API: コンテンツポリシーで拒否されました
```

**期待されるログ（修正後）**:
```
📄 法律文書検出: Claude Vision APIを優先使用します（3ページ）
   理由: OpenAIのコンテンツポリシーは個人情報を含む文書を拒否する傾向があります
✅ Claude Vision APIで分析成功（OpenAIスキップ）
```

## 🔧 解決手順

### ステップ1: 最新コードを取得

```bash
cd /path/to/create-junbisyomen

# 現在のブランチを確認
git branch
# → genspark_ai_developer にいることを確認

# 最新コードをプル
git pull origin genspark_ai_developer

# 最新コミットを確認（def1c25 があるはず）
git log --oneline -3
# 出力例:
# def1c25 fix(ai-analyzer): Prioritize Claude Vision API for PDFs...
# fe61683 docs(troubleshooting): Add comprehensive Vision API fix...
# 5b235ed feat(evidence-system): Comprehensive evidence...
```

### ステップ2: Pythonキャッシュをクリア

古い `.pyc` ファイルが原因の可能性があります：

```bash
# src/ ディレクトリの .pyc ファイルと __pycache__ を削除
find src/ -type f -name "*.pyc" -delete
find src/ -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# または全体をクリア
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
```

### ステップ3: 修正が適用されているか確認

```bash
# ai_analyzer_complete.py の502行目付近をチェック
grep -A 3 "法律文書検出: Claude Vision APIを優先使用" src/ai_analyzer_complete.py
```

**期待される出力**:
```python
logger.info(f"📄 法律文書検出: Claude Vision APIを優先使用します（{len(image_paths)}ページ）")
logger.info(f"   理由: OpenAIのコンテンツポリシーは個人情報を含む文書を拒否する傾向があります")
```

出力がない場合は、ファイルが更新されていません → git pull を再実行

### ステップ4: 再分析を実行

```bash
# 証拠を再分析
python run_phase1.py

# プロンプトで証拠番号を入力
証拠番号を入力: ko_004
```

### ステップ5: ログを確認

**成功の確認ポイント**:

1. ✅ **Claudeの優先使用ログが表示される**
   ```
   📄 法律文書検出: Claude Vision APIを優先使用します（3ページ）
      理由: OpenAIのコンテンツポリシーは個人情報を含む文書を拒否する傾向があります
   ```

2. ✅ **OpenAIのAPI呼び出しがスキップされる**
   - `HTTP Request: POST https://api.openai.com/v1/chat/completions` が**表示されない**（最初は）

3. ✅ **Claudeで分析成功**
   ```
   ✅ Claude Vision APIで分析成功（OpenAIスキップ）
   ```

4. ✅ **信頼度スコアが高い**
   ```
   完全言語化レベル: 4
   信頼度スコア: 95.0%  （0.0% ではない！）
   ```

## 🔍 トラブルシューティング

### 問題1: git pull でエラーが出る

```bash
# ローカル変更がある場合
git stash
git pull origin genspark_ai_developer
git stash pop
```

### 問題2: ブランチが main になっている

```bash
# genspark_ai_developer に切り替え
git checkout genspark_ai_developer
git pull origin genspark_ai_developer
```

### 問題3: まだ OpenAI を先に呼んでいる

**原因**: 別の場所で `run_phase1.py` を実行している可能性

```bash
# 実行中の Python プロセスを確認
ps aux | grep python

# 正しいディレクトリから実行しているか確認
pwd
# /path/to/create-junbisyomen であることを確認

# 実行するファイルの場所を確認
which python
python --version
```

### 問題4: JSON解析エラーがまだ出る

これは別の問題です。Claude の応答が途中で切れているため：

1. JSON修復ロジックが動作しているかログを確認：
   ```
   🔧 JSON修復戦略1: 不完全な文字列を検出、修復試行中...
   ✅ JSON修復成功（戦略1-a: エラー位置特定）
   ```

2. もし修復に失敗している場合は、`max_tokens` を増やす必要があるかもしれません

## 📊 修正内容の詳細

### 修正1: Claude Vision APIの優先使用

**ファイル**: `src/ai_analyzer_complete.py` (行502-565)

**変更内容**:
```python
# 🚨 個人情報を含む法律文書はOpenAIのコンテンツポリシーで拒否されやすい
# そのため、PDFや文書ファイルの場合は最初からClaudeを使用する
if file_type in ['pdf', 'document'] and self.anthropic_client and len(image_paths) > 0:
    logger.info(f"📄 法律文書検出: Claude Vision APIを優先使用します（{len(image_paths)}ページ）")
    logger.info(f"   理由: OpenAIのコンテンツポリシーは個人情報を含む文書を拒否する傾向があります")
    
    # Claudeで分析を試行
    claude_result = self._analyze_with_claude_multi_page(image_paths, claude_prompt)
    if claude_result:
        logger.info("✅ Claude Vision APIで分析成功（OpenAIスキップ）")
        return claude_result  # 成功したらここで即return、OpenAIは呼ばない
```

### 修正2: JSON修復ロジックの改善

**ファイル**: `src/ai_analyzer_complete.py` (行1253-1324)

**変更内容**:
- エラー位置からchar位置を抽出
- 最後の完全なフィールドまで巻き戻し
- 2段階の修復戦略（戦略1-a、戦略1-b）

## 🎯 まとめ

**実行する手順**:
```bash
cd /path/to/create-junbisyomen
git pull origin genspark_ai_developer
find src/ -type f -name "*.pyc" -delete
find src/ -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
python run_phase1.py
# → ko_004 を入力
```

**成功の証**:
- ログに「📄 法律文書検出: Claude Vision APIを優先使用します」が表示される
- OpenAI API呼び出しがスキップされる
- 信頼度スコアが 0.0% ではなく 95% 程度になる

---

**コミット**: `def1c25` - Prioritize Claude Vision API for PDFs  
**PR**: https://github.com/ogaiku-wospe/create-junbisyomen/pull/3

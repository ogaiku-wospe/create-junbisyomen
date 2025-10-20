# Phase 1 完全版システム - マルチケース対応版

複数の事件を同時並行で管理できる改良版システムです。

## 🎯 主な特徴

### ✨ 新機能
- **大元の共有ドライブIDのみ設定** - 個別の事件フォルダIDは不要
- **事件の自動検出** - 共有ドライブ配下のフォルダから自動的に事件を検出
- **複数事件の並行管理** - 事件ごとに独立したワークスペースで管理
- **簡単な事件切り替え** - 対話的なメニューで事件を選択可能
- **キャッシュ機能** - 事件情報をキャッシュして高速化

### 🔄 従来版との違い

| 項目 | 従来版 | マルチケース版 |
|------|--------|---------------|
| **設定方法** | 事件ごとにconfig.pyを編集 | global_config.pyで共有ドライブIDのみ設定 |
| **事件検出** | 手動で事件情報を入力 | 自動検出 |
| **複数事件** | 事件ごとにディレクトリを作成 | 自動的にワークスペース作成 |
| **事件切り替え** | ディレクトリ移動が必要 | メニューから選択 |

## 📋 システム要件

- **Python**: 3.8以上
- **OS**: macOS, Linux, Windows (WSL2)
- **必須ライブラリ**: requirements.txt 参照

### 必須APIキー
- OpenAI API キー（GPT-4o Vision用）
- Google Drive API 認証情報

## 🚀 セットアップ手順

### 1. リポジトリのクローン

```bash
git clone https://github.com/ogaiku-wospe/create-junbisyomen.git
cd create-junbisyomen
```

### 2. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 3. Google Drive API認証の設定

#### 3.1 Google Cloud Consoleでプロジェクトを作成
1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成
3. Google Drive APIを有効化

#### 3.2 OAuth 2.0クライアントIDを作成
1. 「認証情報」→「認証情報を作成」→「OAuth クライアント ID」
2. アプリケーションの種類: **デスクトップアプリ**
3. 作成後、JSONをダウンロード

#### 3.3 credentials.jsonを配置
```bash
# ダウンロードしたJSONファイルを credentials.json としてプロジェクトルートに配置
cp ~/Downloads/client_secret_*.json ./credentials.json
```

### 4. グローバル設定ファイルを編集

```bash
# global_config.py を開く
nano global_config.py
```

**重要: 以下の1箇所のみ編集してください**

```python
# ================================
# 【重要】大元の共有ドライブID設定
# ================================

# ここに大元の共有ドライブIDを設定してください
SHARED_DRIVE_ROOT_ID = "YOUR_SHARED_DRIVE_ID_HERE"
```

#### 共有ドライブIDの取得方法
1. Google Driveで共有ドライブを開く
2. ブラウザのURLを確認
   ```
   https://drive.google.com/drive/folders/0AO6q4_G7DmYSUk9PVA
                                      ^^^^^^^^^^^^^^^^^^^^^^^^
                                      これが共有ドライブID
   ```
3. `folders/` の後の文字列をコピー

### 5. OpenAI APIキーを設定

```bash
# .envファイルを作成
cp .env.example .env

# エディタで開いてAPIキーを設定
nano .env
```

**.env の内容:**
```
OPENAI_API_KEY=sk-proj-your-actual-api-key-here
```

### 6. 共有ドライブに事件フォルダを準備

共有ドライブ配下に以下の構造で事件フォルダを作成：

```
共有ドライブ (SHARED_DRIVE_ROOT_ID)
├── meiyokison_名誉毀損等損害賠償請求事件/
│   ├── 甲号証/          ← 必須（証拠ファイルを配置）
│   ├── 乙号証/          ← オプション
│   ├── config.json      ← オプション（事件情報）
│   └── database.json    ← オプション（分析結果）
│
├── kasai_火災保険金請求事件/
│   └── 甲号証/
│
└── roudou_労働審判申立事件/
    └── 甲号証/
```

**事件フォルダの命名規則:**
- フォルダ名: `{事件ID}_{事件名}`
- 例: `meiyokison_名誉毀損等損害賠償請求事件`
- `{事件ID}`: 英数字で短く（例: `meiyokison`）
- `{事件名}`: 日本語OK（例: `名誉毀損等損害賠償請求事件`）

**必須条件:**
- フォルダ内に **「甲号証」フォルダ** が存在すること
- または `config.json` または `database.json` が存在すること

## 📖 使用方法

### 基本的な使い方

```bash
# マルチケースシステムを起動
python3 run_multi_case.py
```

実行すると以下のように進みます:

1. **Google Drive認証** (初回のみ)
   - ブラウザが開き、Google アカウントでログイン
   - アクセスを許可

2. **事件の自動検出**
   ```
   🔍 共有ドライブから事件フォルダを検索中...
   📁 3個のフォルダを検出しました
     ✅ 事件フォルダ検出: 名誉毀損等損害賠償請求事件
     ✅ 事件フォルダ検出: 火災保険金請求事件
     ✅ 事件フォルダ検出: 労働審判申立事件
   
   ✅ 3件の事件を検出しました
   ```

3. **事件一覧の表示**
   ```
   ======================================================================
     Phase 1完全版システム - 事件一覧
   ======================================================================
   
   📋 検出された事件: 3件
   
   [1] 名誉毀損等損害賠償請求事件
       📁 フォルダ: meiyokison_名誉毀損等損害賠償請求事件
       🆔 事件ID: meiyokison
       📊 甲号証: 74件
       ✅ 完了: 68件
       🕐 最終更新: 2025-01-15 14:30:45
       🔗 URL: https://drive.google.com/drive/folders/1uux0sGt...
   
   [2] 火災保険金請求事件
       ...
   
   [3] 労働審判申立事件
       ...
   ```

4. **事件を選択**
   ```
   事件を選択 (1-3, 0=終了, r=再読み込み): 1
   
   ✅ 選択: 名誉毀損等損害賠償請求事件
   ```

5. **環境のセットアップ**
   ```
   🔧 事件環境をセットアップ中...
      ワークスペース: ~/Documents/phase1_cases/meiyokison
      ✅ case_config.json を作成
      ✅ database.json を初期化
      ✅ .env をコピー
   ✅ 環境セットアップ完了
   ```

6. **Phase 1処理の実行**
   - 通常のPhase 1メニューが表示されます
   - 証拠番号を指定して分析を実行

### 高度な使い方

#### 自動モード（最後に使用した事件を自動選択）

```bash
python3 run_multi_case.py --auto
```

#### キャッシュをクリアして再検出

```bash
python3 run_multi_case.py --refresh
```

#### 事件マネージャーを単独で使用

```bash
# 事件の検出とリスト表示のみ
python3 case_manager.py
```

### ワークスペースの構造

各事件は独立したワークスペースで管理されます:

```
~/Documents/phase1_cases/
├── meiyokison/                    # 事件1のワークスペース
│   ├── case_config.json           # 事件設定
│   ├── database.json              # 分析結果データベース
│   ├── .env                       # 環境変数（コピー）
│   └── temp/                      # 一時ファイル
│
├── kasai/                         # 事件2のワークスペース
│   ├── case_config.json
│   ├── database.json
│   └── ...
│
└── roudou/                        # 事件3のワークスペース
    └── ...
```

## 📊 config.json の構造（オプション）

事件フォルダ内に `config.json` を配置すると、詳細情報を設定できます:

```json
{
  "case_id": "meiyokison",
  "case_name": "名誉毀損等損害賠償請求事件",
  "case_number": "令和7年(ワ)第1234号",
  "plaintiff": "原告名",
  "defendant": "被告名",
  "court": "東京地方裁判所",
  "evidence_prefix_ko": "ko",
  "evidence_prefix_otsu": "otsu"
}
```

## 🔧 トラブルシューティング

### Q: 「事件が見つかりませんでした」と表示される

**確認事項:**
1. `global_config.py` で `SHARED_DRIVE_ROOT_ID` が正しく設定されているか
2. 共有ドライブへのアクセス権限があるか
3. 事件フォルダ内に「甲号証」フォルダが存在するか

**解決方法:**
```bash
# キャッシュをクリアして再検出
python3 run_multi_case.py --refresh
```

### Q: Google Drive認証エラー

**原因:**
- `credentials.json` が存在しない
- Google Drive APIが有効化されていない

**解決方法:**
1. Google Cloud Consoleで設定を確認
2. `credentials.json` をプロジェクトルートに配置
3. `token.pickle` を削除して再認証
   ```bash
   rm token.pickle
   python3 run_multi_case.py
   ```

### Q: OpenAI APIエラー

**確認事項:**
- `.env` ファイルに `OPENAI_API_KEY` が設定されているか
- APIキーが有効か

**解決方法:**
```bash
# APIキーを確認
cat .env

# APIキーを再設定
export OPENAI_API_KEY='sk-proj-your-key'
```

### Q: 証拠ファイルが検出されない

**原因:**
- 証拠ファイルが「甲号証」フォルダに配置されていない

**解決方法:**
1. Google Driveで「甲号証」フォルダを開く
2. 証拠ファイルをアップロード
3. システムを再実行

## 📚 関連ドキュメント

- [README.md](README.md) - 基本ガイド
- [USAGE_GUIDE.md](USAGE_GUIDE.md) - 詳細な使用方法
- [COMPLETE_SYSTEM_SUMMARY.md](COMPLETE_SYSTEM_SUMMARY.md) - システム全体の概要
- [GOOGLE_DRIVE_GUIDE.md](GOOGLE_DRIVE_GUIDE.md) - Google Drive連携の詳細

## 🎯 システムの流れ

```
1. run_multi_case.py を実行
   ↓
2. global_config.py から共有ドライブIDを読み込み
   ↓
3. case_manager.py が共有ドライブを検索
   ↓
4. 事件フォルダを自動検出（「甲号証」フォルダの存在確認）
   ↓
5. 事件一覧を表示
   ↓
6. ユーザーが事件を選択
   ↓
7. ローカルワークスペースを作成
   ↓
8. 事件専用の環境をセットアップ
   ↓
9. Phase 1処理を実行
   ↓
10. database.json に結果を保存
```

## 💡 ベストプラクティス

### 1. 共有ドライブの構造を整理

```
共有ドライブ/
├── 2024年度/
│   ├── case001_事件A/
│   └── case002_事件B/
├── 2025年度/
│   ├── case003_事件C/
│   └── case004_事件D/
└── アーカイブ/
```

### 2. 事件IDの命名規則

- **短く明確に**: `meiyokison`, `kasai2024`, `roudou001`
- **英数字のみ**: 日本語は避ける（フォルダ名全体には使用可）
- **一貫性を保つ**: プロジェクト内で統一

### 3. 定期的なバックアップ

```bash
# ワークスペース全体をバックアップ
tar -czf phase1_backup_$(date +%Y%m%d).tar.gz ~/Documents/phase1_cases/
```

### 4. キャッシュの管理

```bash
# キャッシュファイルの場所
~/.phase1_cases_cache.json      # 事件リストのキャッシュ
~/.phase1_last_case.json        # 最後に使用した事件
~/.phase1_selector.json         # 事件選択の履歴

# キャッシュをクリア
rm ~/.phase1_*.json
```

## 🔒 セキュリティ注意事項

### 絶対にGitHubにアップロードしてはいけないファイル

- `credentials.json` - Google Drive API認証情報
- `token.pickle` - アクセストークン
- `.env` - APIキー
- `database.json` - 事件データ（個人情報含む）
- `case_config.json` - 事件設定

### .gitignore の確認

```bash
# .gitignore に以下が含まれているか確認
cat .gitignore

# 必須エントリ
credentials.json
token.pickle
.env
database.json
case_config.json
*.backup
*.bak
```

## 📞 サポート

問題が発生した場合:

1. このドキュメントの「トラブルシューティング」を確認
2. [Issues](https://github.com/ogaiku-wospe/create-junbisyomen/issues) を検索
3. 新しいIssueを作成

---

**バージョン**: 3.0.0 (マルチケース対応版)  
**最終更新**: 2025年10月20日  
**対応Phase**: Phase 1（証拠分析）

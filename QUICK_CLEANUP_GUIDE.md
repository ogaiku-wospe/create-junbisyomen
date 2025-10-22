# 🚀 クイックスタート: プロジェクトクリーンアップ

## 📥 ステップ1: 最新版をダウンロード

```bash
cd /Users/ogaiku/create-junbisyomen
git pull origin main
```

## 🧹 ステップ2: クリーンアップ実行

### Macの場合:
```bash
chmod +x cleanup_project.sh
./cleanup_project.sh
```

### Windowsの場合:
```cmd
cleanup_project.bat
```

## ✅ ステップ3: 確認

プロンプトが表示されたら `yes` と入力してください。

---

## 🗑️ 削除されるファイル

- `__pycache__/` - Pythonキャッシュ
- `*.pyc` - バイトコード
- `venv/` - 仮想環境
- `*.log` - ログファイル
- `credentials.json` - 認証情報（バックアップされます）
- `token.pickle` - トークン（バックアップされます）
- `current_case.json` - 一時状態
- `database_uploaded.json` - 一時状態

## 🔒 安全機能

✅ 削除前に確認プロンプト  
✅ 機密ファイルは自動バックアップ  
✅ 詳細なログ出力

---

詳細な手順は [CLEANUP_INSTRUCTIONS.md](CLEANUP_INSTRUCTIONS.md) をご覧ください。

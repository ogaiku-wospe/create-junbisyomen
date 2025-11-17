# System Dependencies / システム依存関係

このプロジェクトを完全に動作させるには、Python パッケージ（`requirements.txt`）に加えて、以下のシステムレベルのソフトウェアが必要です。

---

## 必須依存関係 (Required)

### 1. LibreOffice
**用途**: Word文書（.docx, .doc）をPDFに変換し、Vision APIで画像として分析

**インストール方法**:

#### macOS
```bash
brew install libreoffice
```

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install libreoffice
```

#### CentOS/RHEL
```bash
sudo yum install libreoffice
```

#### Windows
1. [LibreOffice公式サイト](https://www.libreoffice.org/download/download/)からインストーラーをダウンロード
2. インストーラーを実行

**インストール確認**:
```bash
soffice --version
```

出力例:
```
LibreOffice 7.6.4.1 00(Build:1)
```

**必要な理由**:
- Word文書をPDF経由で画像化
- Vision APIで全ページを視覚的に分析
- 図表、レイアウト、視覚的要素の解析に必須
- なければテキストベース分析にフォールバック（品質低下）

---

### 2. Poppler (pdf2image用)
**用途**: PDFを画像に変換（複数ページPDF分析に必須）

**インストール方法**:

#### macOS
```bash
brew install poppler
```

#### Ubuntu/Debian
```bash
sudo apt-get install poppler-utils
```

#### CentOS/RHEL
```bash
sudo yum install poppler-utils
```

#### Windows
1. [Poppler for Windows](http://blog.alivate.com.au/poppler-windows/)からダウンロード
2. `bin`フォルダをPATHに追加

**インストール確認**:
```bash
pdftoppm -v
```

**必要な理由**:
- Pythonパッケージ`pdf2image`が内部で使用
- PDFの各ページを画像として抽出
- 複数ページPDF分析機能に必須

---

## オプション依存関係 (Optional)

### 3. Tesseract OCR
**用途**: 画像からテキストを抽出（OCR）

**インストール方法**:

#### macOS
```bash
brew install tesseract
```

#### Ubuntu/Debian
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-jpn  # 日本語サポート
```

#### CentOS/RHEL
```bash
sudo yum install tesseract
```

#### Windows
1. [Tesseract GitHub Releases](https://github.com/UB-Mannheim/tesseract/wiki)からインストーラーをダウンロード
2. インストール時に日本語データを選択

**インストール確認**:
```bash
tesseract --version
```

**必要な理由**:
- スキャンされた文書や画像からテキスト抽出
- テキストが少ないPDFのバックアップ
- なくても動作するが、OCR機能が無効化

---

## インストール手順（推奨順序）

### Step 1: Pythonパッケージのインストール
```bash
cd /home/user/webapp
pip3 install -r requirements.txt
```

### Step 2: LibreOfficeのインストール（必須）
```bash
# macOS
brew install libreoffice

# Ubuntu/Debian
sudo apt-get install libreoffice
```

### Step 3: Popplerのインストール（必須）
```bash
# macOS
brew install poppler

# Ubuntu/Debian
sudo apt-get install poppler-utils
```

### Step 4: Tesseractのインストール（オプション）
```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-jpn
```

### Step 5: 確認
```bash
# LibreOffice確認
soffice --version

# Poppler確認
pdftoppm -v

# Tesseract確認（オプション）
tesseract --version
```

---

## トラブルシューティング

### LibreOfficeが見つからない (soffice: command not found)

**原因**: LibreOfficeがインストールされていないか、PATHに含まれていない

**解決策**:
```bash
# macOS: Homebrewで再インストール
brew reinstall libreoffice

# PATHに追加（macOS）
export PATH="/Applications/LibreOffice.app/Contents/MacOS:$PATH"

# 永続化（~/.zshrc または ~/.bash_profile に追加）
echo 'export PATH="/Applications/LibreOffice.app/Contents/MacOS:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### pdf2imageエラー (Unable to get page count)

**原因**: Popplerがインストールされていない

**解決策**:
```bash
# macOS
brew install poppler

# Ubuntu/Debian
sudo apt-get install poppler-utils
```

### Word文書の変換が遅い

**原因**: LibreOfficeの初回起動は遅い場合がある

**解決策**:
- 通常の動作です
- 2回目以降は高速化されます
- タイムアウト設定は30秒（`ai_analyzer_complete.py` line 939）

---

## 依存関係マトリックス

| 機能 | LibreOffice | Poppler | Tesseract |
|------|-------------|---------|-----------|
| PDF分析 | - | ✅ 必須 | - |
| 複数ページPDF | - | ✅ 必須 | - |
| Word文書分析（Vision） | ✅ 必須 | ✅ 必須 | - |
| Word文書分析（Text） | - | - | - |
| 画像分析 | - | - | - |
| OCR機能 | - | - | ⭕ 推奨 |

凡例:
- ✅ 必須: この機能には必ず必要
- ⭕ 推奨: なくても動作するが、あると品質向上
- `-`: 不要

---

## Docker環境の場合

Dockerfileに以下を追加してください:

```dockerfile
# Ubuntu base image
FROM python:3.11-slim

# System dependencies
RUN apt-get update && apt-get install -y \
    libreoffice \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-jpn \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application
COPY . /app
WORKDIR /app

CMD ["python", "run_phase1_multi.py"]
```

---

## バージョン情報

推奨バージョン:
- **LibreOffice**: 7.0以上
- **Poppler**: 0.86以上
- **Tesseract**: 4.0以上

最小動作バージョン:
- **LibreOffice**: 6.0以上
- **Poppler**: 0.82以上
- **Tesseract**: 3.04以上

---

## FAQ

### Q1: LibreOfficeなしで動作しますか？
**A**: はい、動作します。ただし：
- Word文書はテキストベースで分析（構造情報のみ）
- 図表、レイアウトは解析不可
- 分析品質が低下

### Q2: Homebrewがない場合は？
**A**: 
- macOS: [Homebrew公式サイト](https://brew.sh/)からインストール
- または各ソフトウェアの公式サイトから直接インストーラーをダウンロード

### Q3: Windowsでの動作は？
**A**: 
- 基本的に動作しますが、パス設定が必要な場合があります
- LibreOffice: `C:\Program Files\LibreOffice\program\soffice.exe`
- 環境変数PATHに追加が必要

### Q4: これらをインストールしないとどうなる？
**A**:
- **LibreOfficeなし**: Word文書の分析品質が低下（テキストのみ）
- **Popplerなし**: PDFの複数ページ分析が動作しない
- **Tesseractなし**: OCR機能が無効化（それ以外は正常動作）

---

**最終更新**: 2025-10-22
**関連**: requirements.txt, ai_analyzer_complete.py

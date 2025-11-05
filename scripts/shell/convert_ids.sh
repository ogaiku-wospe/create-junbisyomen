#!/bin/bash
# 証拠ID変換スクリプト
# database.json内のtmp_をtmp_ko_に変換

# このスクリプトのディレクトリに移動
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

python3 convert_evidence_ids.py

#!/bin/bash
# 準備書面作成支援システム - 起動スクリプト
# 使い方: bash start.sh または ./start.sh

# スクリプトのディレクトリに移動
cd "$(dirname "$0")"

# Python 3で起動
python3 run_phase1_multi.py

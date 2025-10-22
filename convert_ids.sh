#!/bin/bash
# 証拠ID変換スクリプト
# database.json内のtmp_をtmp_ko_に変換

cd /home/user/webapp
python3 convert_evidence_ids.py

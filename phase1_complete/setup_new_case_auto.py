#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1完全版システム - 自動フォルダ作成セットアップ

【使用方法】
    python3 setup_new_case_auto.py

【機能】
    - 共有ドライブIDのみ指定
    - 事件フォルダと証拠フォルダを自動作成
    - config.pyとdatabase.jsonを自動生成
"""

import os
import json
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

print("Phase 1完全版システム - 自動セットアップ")
print("共有ドライブIDのみで自動的にフォルダを作成します")
print("\n詳細は setup_new_case.py を参照してください")

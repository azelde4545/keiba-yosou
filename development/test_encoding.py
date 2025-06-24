#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import os

def test_encoding_fix():
    """文字化け対策テスト"""
    print("=== 文字化け対策テスト ===")
    
    try:
        # UTF-8環境でPython実行
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        result = subprocess.run([
            sys.executable, 'encoding_safe_predictor.py'
        ], capture_output=True, text=True, encoding='utf-8', 
          cwd=r'C:\Users\setsu\Desktop\競馬用', env=env)
        
        print("=== 実行結果 ===")
        if result.returncode == 0:
            print("✅ 正常実行")
            print(result.stdout[:1000])  # 最初の1000文字表示
            
            # 日本語文字の確認
            if "競馬" in result.stdout and "予想" in result.stdout:
                print("\n✅ 日本語表示: 正常")
            else:
                print("\n⚠️ 日本語表示: 問題あり")
        else:
            print("❌ 実行エラー")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ テストエラー: {e}")

if __name__ == "__main__":
    test_encoding_fix()

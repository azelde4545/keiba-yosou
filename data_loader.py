# -*- coding: utf-8 -*-
"""
競馬予想システム - データクリア+読み込み統合モジュール
過去データクリア機能 + 安全なデータ読み込み機能
"""

import os
import json
import sqlite3
import gc
# import chardet  # 一時的にコメントアウト
from datetime import datetime
from typing import Dict, List, Optional, Any


class DataCleaner:
    """ソフト内部の古いデータを完全にクリアするクラス"""
    
    def __init__(self, project_dir: str):
        self.project_dir = project_dir
        self.cleanup_files = [
            'prediction_result_v2.txt',
            'prediction_result.json',
            'cache/random_forest_model.pkl'
        ]
    
    def clear_config_cache(self) -> bool:
        """config.jsonの古いレース情報をクリア"""
        print("[推論] config.jsonの古いレース情報をクリア中...")
        
        config_path = os.path.join(self.project_dir, 'config.json')
        if not os.path.exists(config_path):
            return False
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if 'race_info' in config:
                old_race_name = config['race_info'].get('name', '不明')
                print(f"[事実] 古いレース情報を削除: {old_race_name}")
                
                config['race_info'] = {
                    "name": "新レース待機中",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "venue": "未定",
                    "race_time": "00:00"
                }
                
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                
                print("[事実] config.json更新完了")
                return True
                
        except Exception as e:
            print(f"[不明] config.json処理エラー: {e}")
            return False
    
    def clear_sqlite_cache(self) -> bool:
        """SQLiteデータベースの一時キャッシュをクリア"""
        print("[推論] SQLiteキャッシュテーブルをクリア中...")
        
        db_path = os.path.join(self.project_dir, 'dark_horse.db')
        if not os.path.exists(db_path):
            return False
            
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                tables_to_clear = ['temp_predictions', 'cache_evaluations', 'session_data']
                cleared_count = 0
                
                for table in tables_to_clear:
                    try:
                        cursor.execute(f"DELETE FROM {table}")
                        cleared_count += 1
                    except sqlite3.OperationalError:
                        pass
                
                conn.commit()
                cursor.execute("VACUUM")
            
            print(f"[事実] {cleared_count}個のキャッシュテーブルをクリア")
            return True
            
        except Exception as e:
            print(f"[不明] SQLite処理エラー: {e}")
            return False
    
    def clear_prediction_cache(self) -> int:
        """予想結果キャッシュをクリア"""
        print("[事実] 古い予想結果をクリア中...")
        
        cleared_count = 0
        for filename in self.cleanup_files:
            file_path = os.path.join(self.project_dir, filename)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"[事実] 削除完了: {filename}")
                    cleared_count += 1
                except Exception as e:
                    print(f"[推測] 削除失敗: {filename} - {e}")
        
        print(f"[事実] {cleared_count}個のキャッシュファイルをクリア")
        return cleared_count
    
    def force_clear_python_modules(self) -> bool:
        """競馬予想関連のPythonモジュールを強制アンロード"""
        import sys
        print("[推論] Pythonモジュールキャッシュを強制クリア中...")
        
        # 競馬関連キーワード
        keiba_keywords = [
            'keiba', 'predictor', 'race', 'horse', 'dark_horse',
            'pdf_to_json', 'pdf_reader', 'improved_predictor',
            'run_prediction', 'CorePredictor', 'FastAnaumaDB', 
            'TimeManager', 'clean_predictor', 'japanese_data',
            'complete_extraction', 'complete_horse_data',
            'quality_assessment', 'race_prediction_pipeline'
        ]
        
        # パターンマッチで対象モジュールを特定
        modules_to_remove = []
        for module_name in list(sys.modules.keys()):
            for keyword in keiba_keywords:
                if keyword.lower() in module_name.lower():
                    # 自分自身は除外
                    if 'data_loader' not in module_name:
                        modules_to_remove.append(module_name)
                        break
        
        # モジュール削除実行
        cleared_count = 0
        for module_name in modules_to_remove:
            try:
                if module_name in sys.modules:
                    del sys.modules[module_name]
                    cleared_count += 1
            except Exception:
                pass
        
        print(f"[事実] {cleared_count}個のモジュールをクリア")
        return cleared_count > 0
    
    def clear_pycache_directories(self) -> bool:
        """__pycache__ディレクトリの削除"""
        import shutil
        import glob
        print("[推論] __pycache__ディレクトリをクリア中...")
        
        cleared_count = 0
        try:
            # __pycache__ディレクトリを探して削除
            for root, dirs, files in os.walk(self.project_dir):
                if '__pycache__' in dirs:
                    pycache_path = os.path.join(root, '__pycache__')
                    try:
                        shutil.rmtree(pycache_path)
                        cleared_count += 1
                    except Exception:
                        pass
            
            # .pycファイルも削除
            pyc_files = glob.glob(os.path.join(self.project_dir, '**', '*.pyc'), recursive=True)
            for pyc_file in pyc_files:
                try:
                    os.remove(pyc_file)
                    cleared_count += 1
                except Exception:
                    pass
            
            print(f"[事実] {cleared_count}個のキャッシュファイル/ディレクトリを削除")
            return cleared_count > 0
            
        except Exception as e:
            print(f"[不明] __pycache__クリアエラー: {e}")
            return False
    
    def create_fresh_environment(self) -> bool:
        """クリーンな実行環境を作成"""
        print("[推論] フレッシュな実行環境を準備中...")
        
        # 環境変数をクリア（競馬予想関連のみ）
        env_vars_to_clear = [
            'KEIBA_CACHE_DIR',
            'RACE_DATA_CACHE', 
            'PREDICTION_CACHE'
        ]
        
        for var in env_vars_to_clear:
            if var in os.environ:
                del os.environ[var]
                print(f"[事実] 環境変数クリア: {var}")
        
        # 一時ディレクトリの作成
        temp_dir = os.path.join(self.project_dir, 'temp_clean')
        os.makedirs(temp_dir, exist_ok=True)
        
        print("[事実] クリーンな実行環境準備完了")
        return True
    
    def comprehensive_cleanup(self) -> Dict[str, bool]:
        """全機能統合クリーンアップ実行"""
        print("=== 完全クリーンアップ実行開始 ===")
        
        results = {
            "config_cleared": self.clear_config_cache(),
            "sqlite_cleared": self.clear_sqlite_cache(), 
            "cache_cleared": self.clear_prediction_cache() > 0,
            "modules_cleared": self.force_clear_python_modules(),
            "pycache_cleared": self.clear_pycache_directories(),
            "environment_fresh": self.create_fresh_environment()
        }
        
        success_count = sum(results.values())
        total_count = len(results)
        
        print(f"[事実] クリーンアップ結果: {success_count}/{total_count}項目成功")
        print("=== 完全クリーンアップ実行完了 ===")
        
        return results


class SafeDataLoader:
    """安全なデータ読み込みクラス"""
    
    def safe_load_json(self, file_path: str) -> Optional[Dict[str, Any]]:
        """安全なJSON読み込み"""
        if not os.path.exists(file_path):
            print(f"[WARNING] ファイルが見つかりません: {file_path}")
            return None
        
        try:
            # 一時的にutf-8固定に変更
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                data = json.load(f)
            
            print(f"[SUCCESS] JSON読み込み完了: {file_path}")
            return data
            
        except Exception as e:
            print(f"[ERROR] ファイル読み込みエラー: {e}")
            return None
    
    def safe_load_config(self, config_path: str = 'config.json') -> Dict[str, Any]:
        """安全な設定ファイル読み込み"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(script_dir, config_path)
        
        config = self.safe_load_json(full_path)
        if config is None:
            return {
                "race_info": {
                    "name": "新レース待機中",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "venue": "未定",
                    "race_time": "00:00"
                },
                "betting_strategy": {
                    "total_budget": 400,
                    "min_bet_unit": 100,
                    "auto_mode": False
                }
            }
        
        return config


class DataLoader:
    """データクリア+読み込み統合クラス"""
    
    def __init__(self, project_dir: str = None):
        if project_dir is None:
            project_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.project_dir = project_dir
        self.cleaner = DataCleaner(project_dir)
        self.loader = SafeDataLoader()
    
    def cleanup_and_load(self, race_data_path: str) -> Dict[str, Any]:
        """データクリア→読み込みの統合実行"""
        print("=== データクリア+読み込み統合処理開始 ===")
        
        # 入力検証
        if not race_data_path:
            raise ValueError("レースデータのJSONファイルパスを指定してください")
        
        if not os.path.exists(race_data_path):
            raise FileNotFoundError(f"指定されたファイルが見つかりません: {race_data_path}")
        
        # Step 1: 古いデータをクリア
        self.cleaner.clear_config_cache()
        self.cleaner.clear_sqlite_cache()
        gc.collect()  # メモリクリア
        
        # Step 2: 設定ファイル読み込み
        config = self.loader.safe_load_config()
        
        # Step 3: レースデータ読み込み
        race_data = self.loader.safe_load_json(race_data_path)
        
        if race_data is None:
            raise ValueError(f"JSONファイルの読み込みに失敗しました: {race_data_path}")
        
        print("=== データクリア+読み込み統合処理完了 ===")
        
        return {
            "config": config,
            "race_data": race_data,
            "status": "success"
        }
    
    def load_with_fallback(self, primary_file: str, fallback_file: str = None) -> Dict:
        """フォールバック付きデータ読み込み（安定性向上）"""
        try:
            # メイン読み込み
            return self.loader.safe_load_json(primary_file)
        except Exception as e:
            print(f"[WARN] メインデータ読み込み失敗: {e}")
            
            if fallback_file and os.path.exists(fallback_file):
                print(f"[INFO] フォールバックデータを使用: {fallback_file}")
                return self.loader.safe_load_json(fallback_file)
            
            # 最後の手段：ダミーデータ生成
            print("[INFO] ダミーデータで継続実行")
            return self._generate_dummy_race_data()

    def _generate_dummy_race_data(self) -> Dict:
        """最小限のダミーレースデータ"""
        return {
            "race_info": {"name": "テストレース", "date": "2025-01-01"},
            "horses": [{"number": i, "name": f"テスト馬{i}", "odds": 5.0, "jockey": "テスト騎手", "weight": 55.0} 
                      for i in range(1, 6)]
        }

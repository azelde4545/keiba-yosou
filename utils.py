# -*- coding: utf-8 -*-
"""
競馬予想システム - エラー処理・キャッシュ・共通機能
フォールバック機能・安全性確保・パフォーマンス最適化
"""

import os
import sys
import traceback
import gc
import psutil
from typing import Dict, List, Optional, Any, Callable
from functools import wraps
from datetime import datetime
from pathlib import Path


def safe_path_join(base_dir: str, filename: str) -> str:
    """安全なパス結合（パストラバーサル攻撃防止）"""
    base_path = Path(base_dir).resolve()
    full_path = (base_path / filename).resolve()
    
    if not str(full_path).startswith(str(base_path)):
        raise ValueError(f"安全でないパス: {filename}")
    
    return str(full_path)


def safe_table_name(table: str) -> str:
    """安全なテーブル名（SQLインジェクション防止）"""
    allowed_tables = {'temp_predictions', 'cache_evaluations', 'session_data'}
    if table not in allowed_tables:
        raise ValueError(f"許可されていないテーブル: {table}")
    return table


class ErrorHandler:
    """強化されたエラーハンドリングクラス"""
    
    @staticmethod
    def enhanced_error_handler(error: Exception, context: str, **kwargs) -> None:
        """強化されたエラーハンドリング（詳細情報付き）"""
        try:
            error_type = type(error).__name__
            error_message = str(error)
            
            print(f"[ERROR_REPORT] エラー詳細レポート:")
            print(f"   [LOCATION] 発生場所: {context}")
            print(f"   [LABEL]  エラー種類: {error_type}")
            print(f"   [MSG] エラーメッセージ: {error_message}")
            
            # 追加のコンテキスト情報
            if kwargs:
                print(f"   [INFO] 関連データ:")
                for key, value in kwargs.items():
                    # 値が長すぎる場合は短縮表示
                    if isinstance(value, str) and len(value) > 100:
                        display_value = value[:100] + "..."
                    elif isinstance(value, dict) and len(str(value)) > 200:
                        display_value = f"Dict with {len(value)} keys"
                    elif isinstance(value, list) and len(str(value)) > 200:
                        display_value = f"List with {len(value)} items"
                    else:
                        display_value = value
                    
                    print(f"      {key}: {display_value}")
            
            # スタックトレース（開発モード）
            if os.environ.get('DEBUG_MODE') == '1':
                print(f"   [STACK] スタックトレース:")
                traceback.print_exc()
        
        except Exception as nested_error:
            print(f"[CRITICAL] エラーハンドラー自体でエラー: {nested_error}")
    
    @staticmethod
    def safe_execute(func: Callable, context: str, fallback_value: Any = None, **kwargs) -> Any:
        """安全な関数実行ラッパー"""
        try:
            return func(**kwargs)
        except Exception as e:
            ErrorHandler.enhanced_error_handler(e, context, **kwargs)
            return fallback_value


class CacheManager:
    """キャッシュ管理クラス"""
    
    def __init__(self, max_entries: int = 100):
        self._cache = {}
        self.max_entries = max_entries
        self.hit_count = 0
        self.miss_count = 0
    
    def get(self, key: str) -> Optional[Any]:
        """キャッシュから値を取得"""
        if key in self._cache:
            self.hit_count += 1
            # アクセス時刻を更新
            self._cache[key]['last_access'] = datetime.now()
            return self._cache[key]['value']
        else:
            self.miss_count += 1
            return None
    
    def set(self, key: str, value: Any) -> None:
        """キャッシュに値を設定"""
        # キャッシュサイズ制限チェック
        if len(self._cache) >= self.max_entries:
            self._evict_oldest()
        
        self._cache[key] = {
            'value': value,
            'created_at': datetime.now(),
            'last_access': datetime.now()
        }
    
    def _evict_oldest(self) -> None:
        """最も古いキャッシュエントリを削除"""
        if not self._cache:
            return
        
        oldest_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k]['last_access']
        )
        del self._cache[oldest_key]
    
    def clear(self) -> None:
        """キャッシュをクリア"""
        self._cache.clear()
        self.hit_count = 0
        self.miss_count = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """キャッシュ統計を取得"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'entries': len(self._cache),
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': round(hit_rate, 2),
            'max_entries': self.max_entries
        }


class FallbackSystem:
    """フォールバック機能システム"""
    
    def __init__(self):
        self.manual_data_cache = {}
        self.recovery_attempts = 0
        self.max_recovery_attempts = 3
    
    def manual_data_entry_mode(self, expected_horses: int) -> List[Dict]:
        """手動データ入力モード"""
        print("[FALLBACK] 手動データ入力モードを開始します")
        
        horses_data = []
        
        try:
            for i in range(1, min(expected_horses + 1, 6)):  # 最大5頭まで
                print(f"\n=== {i}番馬の情報入力 ===")
                
                horse_data = {
                    'horse_number': i,
                    'horse_name': self._safe_input(f"{i}番馬名", f"手動入力馬{i}"),
                    'jockey': self._safe_input("騎手名", "手動入力騎手"),
                    'odds': self._safe_float_input("オッズ", 5.0),
                    'father': self._safe_input("父馬名", "手動入力父"),
                    'recent_results': self._create_default_recent_results()
                }
                
                horses_data.append(horse_data)
                print(f"[MANUAL] {i}番馬データ入力完了: {horse_data['horse_name']}")
        
        except KeyboardInterrupt:
            print("[WARNING] 手動入力がキャンセルされました")
            return self._generate_minimal_fallback_data(expected_horses)
        
        print(f"[FALLBACK] 手動データ入力完了: {len(horses_data)}頭")
        return horses_data
    
    def _safe_input(self, prompt: str, default: str) -> str:
        """安全な入力取得"""
        try:
            value = input(f"{prompt} (デフォルト: {default}): ").strip()
            return value if value else default
        except (EOFError, KeyboardInterrupt):
            return default
    
    def _safe_float_input(self, prompt: str, default: float) -> float:
        """安全な浮動小数点入力取得"""
        try:
            value = input(f"{prompt} (デフォルト: {default}): ").strip()
            return float(value) if value else default
        except (ValueError, EOFError, KeyboardInterrupt):
            return default
    
    def _create_default_recent_results(self) -> List[Dict]:
        """デフォルト近走成績作成"""
        return [
            {'result': 5, 'date': '2024-01-01', 'distance': 2000, 'time_margin': 0.5},
            {'result': 3, 'date': '2023-12-01', 'distance': 1800, 'time_margin': 0.3}
        ]
    
    def _generate_minimal_fallback_data(self, horse_count: int) -> List[Dict]:
        """最小限のフォールバックデータ生成"""
        horses = []
        for i in range(1, min(horse_count + 1, 9)):
            horses.append({
                'horse_number': i,
                'horse_name': f"フォールバック馬{i}",
                'jockey': "フォールバック騎手",
                'odds': 5.0 + i,
                'recent_results': self._create_default_recent_results()
            })
        
        return horses


class SystemMonitor:
    """システム監視クラス"""
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """システム情報取得"""
        try:
            memory_info = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            return {
                'memory_total': round(memory_info.total / (1024**3), 2),  # GB
                'memory_available': round(memory_info.available / (1024**3), 2),  # GB
                'memory_percent': memory_info.percent,
                'cpu_percent': cpu_percent,
                'cpu_count': psutil.cpu_count()
            }
        except Exception:
            return {'error': 'システム情報取得に失敗'}
    
    @staticmethod
    def force_garbage_collection() -> Dict[str, int]:
        """強制ガベージコレクション"""
        before = len(gc.get_objects())
        collected = gc.collect()
        after = len(gc.get_objects())
        
        return {
            'objects_before': before,
            'objects_after': after,
            'objects_collected': collected,
            'objects_freed': before - after
        }


class UtilityTools:
    """ユーティリティツール統合クラス"""
    
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.cache_manager = CacheManager()
        self.fallback_system = FallbackSystem()
        self.monitor = SystemMonitor()
    
    def safe_get(self, data: Dict, key: str, default: Any = None) -> Any:
        """安全な辞書値取得"""
        try:
            return data.get(key, default) if isinstance(data, dict) else default
        except Exception:
            return default
    
    def safe_get_nested(self, data: Dict, keys: List[str], default: Any = None) -> Any:
        """安全なネストした辞書値取得"""
        try:
            result = data
            for key in keys:
                if isinstance(result, dict) and key in result:
                    result = result[key]
                else:
                    return default
            return result
        except Exception:
            return default
    
    def validate_horse_data(self, horse: Dict[str, Any]) -> bool:
        """馬データの妥当性検証"""
        required_fields = ['name', 'odds', 'number']
        
        try:
            for field in required_fields:
                if field not in horse or horse[field] is None:
                    return False
            
            # オッズの妥当性チェック
            odds = horse.get('odds', 0)
            if not isinstance(odds, (int, float)) or odds <= 0:
                return False
            
            return True
            
        except Exception:
            return False
    
    def get_system_health(self) -> Dict[str, Any]:
        """システムヘルス取得"""
        return {
            'system_info': self.monitor.get_system_info(),
            'cache_stats': self.cache_manager.get_stats(),
            'timestamp': datetime.now().isoformat()
        }


# シンプルなデータ検証関数（機能性向上）
def validate_horse_data(horse: Dict) -> bool:
    """馬データの基本検証"""
    required_fields = ['number', 'name', 'odds']
    
    for field in required_fields:
        if field not in horse:
            return False
    
    # 基本的な値チェック
    if not (1 <= horse.get('number', 0) <= 20):
        return False
    if not (0.1 <= horse.get('odds', 0) <= 999):
        return False
    
    return True


def clean_horse_data(horses: List[Dict]) -> List[Dict]:
    """不正データの除去"""
    return [horse for horse in horses if validate_horse_data(horse)]

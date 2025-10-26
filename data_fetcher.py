# -*- coding: utf-8 -*-
"""
競馬予想システム - データ取得モジュール
外部APIやファイルからレースデータを取得する
"""

import asyncio
import orjson
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
import logging

# httpxは将来的な外部API取得用に準備（現在はローカルファイル読み込みのみ）
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    logging.warning("httpx not available. External API fetching will be disabled.")

logger = logging.getLogger(__name__)


class DataFetcher:
    """レースデータ取得クラス（同期・非同期対応）"""

    def __init__(self, timeout: float = 5.0, allowed_base_dir: Optional[Path] = None):
        """
        Args:
            timeout: HTTP通信のタイムアウト時間（秒）
            allowed_base_dir: ファイル読み込みを許可する基準ディレクトリ
        """
        self.timeout = timeout
        self.cache = {}
        self.allowed_base_dir = allowed_base_dir or (Path.cwd() / 'data')

    def _validate_file_path(self, file_path: str) -> Path:
        """
        ファイルパスのセキュリティ検証

        Args:
            file_path: 検証するファイルパス

        Returns:
            検証済みのPathオブジェクト

        Raises:
            ValueError: パスが許可されたディレクトリ外の場合
        """
        path = Path(file_path).resolve()

        # 許可されたディレクトリ内かチェック
        try:
            # is_relative_toはPython 3.9+
            if hasattr(path, 'is_relative_to'):
                if not path.is_relative_to(self.allowed_base_dir.resolve()):
                    raise ValueError(f"Path {path} is outside allowed directory")
            else:
                # Python 3.8以前の互換性対応
                try:
                    path.relative_to(self.allowed_base_dir.resolve())
                except ValueError:
                    raise ValueError(f"Path {path} is outside allowed directory")
        except ValueError as e:
            logger.error(f"Path validation failed: {e}")
            raise

        return path

    def get_race_data(self, source: str) -> Optional[Dict[str, Any]]:
        """
        レースデータを取得（同期版）

        Args:
            source: データソース（ファイルパスまたはURL）

        Returns:
            レースデータ辞書、失敗時はNone
        """
        # キャッシュチェック
        if source in self.cache:
            logger.info(f"Cache hit: {source}")
            return self.cache[source]

        # ファイルパスかURLかを判定
        if source.startswith('http://') or source.startswith('https://'):
            # 外部API取得（同期版）
            data = self._fetch_from_api_sync(source)
        else:
            # ローカルファイル読み込み
            data = self._load_from_file(source)

        if data:
            self.cache[source] = data

        return data

    async def get_race_data_async(self, source: str) -> Optional[Dict[str, Any]]:
        """
        レースデータを取得（非同期版）

        Args:
            source: データソース（ファイルパスまたはURL）

        Returns:
            レースデータ辞書、失敗時はNone
        """
        # キャッシュチェック
        if source in self.cache:
            logger.info(f"Cache hit: {source}")
            return self.cache[source]

        # ファイルパスかURLかを判定
        if source.startswith('http://') or source.startswith('https://'):
            # 外部API取得（非同期版）
            data = await self._fetch_from_api_async(source)
        else:
            # ローカルファイル読み込み（非同期対応）
            data = await self._load_from_file_async(source)

        if data:
            self.cache[source] = data

        return data

    async def get_multiple_races_async(self, sources: List[str]) -> List[Dict[str, Any]]:
        """
        複数レースのデータを並列取得（非同期版）

        Args:
            sources: データソースのリスト

        Returns:
            レースデータのリスト
        """
        tasks = [self.get_race_data_async(source) for source in sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # エラーを除外してデータのみ返す
        return [r for r in results if isinstance(r, dict)]

    def _load_from_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        ローカルファイルからJSON読み込み（同期版）

        Args:
            file_path: JSONファイルパス

        Returns:
            読み込んだデータ、失敗時はNone
        """
        path = Path(file_path)
        if not path.exists():
            logger.error(f"File not found: {file_path}")
            return None

        try:
            with open(path, 'rb') as f:
                data = orjson.loads(f.read())
            logger.info(f"Loaded from file: {file_path}")
            return data
        except Exception as e:
            logger.error(f"Failed to load file {file_path}: {e}")
            return None

    async def _load_from_file_async(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        ローカルファイルからJSON読み込み（非同期版）

        Args:
            file_path: JSONファイルパス

        Returns:
            読み込んだデータ、失敗時はNone
        """
        path = Path(file_path)
        if not path.exists():
            logger.error(f"File not found: {file_path}")
            return None

        try:
            # 非同期ファイル読み込み
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None,
                lambda: orjson.loads(path.read_bytes())
            )
            logger.info(f"Loaded from file (async): {file_path}")
            return data
        except Exception as e:
            logger.error(f"Failed to load file {file_path}: {e}")
            return None

    def _fetch_from_api_sync(self, url: str) -> Optional[Dict[str, Any]]:
        """
        外部APIからデータ取得（同期版）

        Args:
            url: API URL

        Returns:
            取得したデータ、失敗時はNone
        """
        if not HTTPX_AVAILABLE:
            logger.error("httpx is not installed. Cannot fetch from API.")
            return None

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url)
                response.raise_for_status()
                data = orjson.loads(response.content)
                logger.info(f"Fetched from API: {url}")
                return data
        except httpx.TimeoutException:
            logger.error(f"Timeout fetching {url}")
            return None
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to fetch from API {url}: {e}")
            return None

    async def _fetch_from_api_async(self, url: str) -> Optional[Dict[str, Any]]:
        """
        外部APIからデータ取得（非同期版）

        Args:
            url: API URL

        Returns:
            取得したデータ、失敗時はNone
        """
        if not HTTPX_AVAILABLE:
            logger.error("httpx is not installed. Cannot fetch from API.")
            return None

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = orjson.loads(response.content)
                logger.info(f"Fetched from API (async): {url}")
                return data
        except httpx.TimeoutException:
            logger.error(f"Timeout fetching {url}")
            return None
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to fetch from API {url}: {e}")
            return None

    def clear_cache(self):
        """キャッシュをクリア"""
        self.cache.clear()
        logger.info("Cache cleared")


# 便利関数
def load_race_data(file_path: str) -> Optional[Dict[str, Any]]:
    """
    レースデータを読み込む簡易関数

    Args:
        file_path: JSONファイルパス

    Returns:
        レースデータ辞書
    """
    fetcher = DataFetcher()
    return fetcher.get_race_data(file_path)


async def load_race_data_async(file_path: str) -> Optional[Dict[str, Any]]:
    """
    レースデータを読み込む簡易関数（非同期版）

    Args:
        file_path: JSONファイルパス

    Returns:
        レースデータ辞書
    """
    fetcher = DataFetcher()
    return await fetcher.get_race_data_async(file_path)


async def load_multiple_races(file_paths: List[str]) -> List[Dict[str, Any]]:
    """
    複数レースのデータを並列読み込み

    Args:
        file_paths: JSONファイルパスのリスト

    Returns:
        レースデータのリスト
    """
    fetcher = DataFetcher()
    return await fetcher.get_multiple_races_async(file_paths)

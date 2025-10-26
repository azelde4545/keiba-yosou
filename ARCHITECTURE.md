# 競馬予想システム - アーキテクチャドキュメント

## システムアーキテクチャ概要

### 設計原則

1. **モジュール性**: 各機能を独立したモジュールとして実装
2. **拡張性**: 新機能の追加が容易な設計
3. **パフォーマンス**: 並列処理とキャッシングによる高速化
4. **セキュリティ**: 入力検証とエラーハンドリングの徹底

---

## コンポーネント図

```
┌─────────────────────────────────────────────────────────────┐
│                        main.py                              │
│                   (メインコントローラー)                      │
│  - コマンドライン引数解析                                     │
│  - 処理フロー制御                                            │
│  - パフォーマンス計測                                        │
└─────────────┬───────────────────────────────────────────────┘
              │
              ├─────────────────────────────────────────────┐
              │                                             │
              ▼                                             ▼
┌──────────────────────────┐                  ┌──────────────────────────┐
│   data_loader.py         │                  │   data_fetcher.py        │
│  (データクリーニング)      │                  │  (データ取得)             │
│  - 古いデータのクリア      │                  │  - 同期/非同期取得        │
│  - JSON読み込み           │                  │  - キャッシュ管理         │
│  - 設定ファイル管理        │                  │  - セキュリティ検証       │
└──────────────────────────┘                  └──────────────────────────┘
              │
              │
              ▼
┌──────────────────────────────────────────────────────────────┐
│                   horse_evaluator.py                         │
│                    (馬評価エンジン)                           │
│  - モード別評価ウェイト                                        │
│  - 実力評価 / 期待値評価                                      │
│  - 並列処理（ThreadPoolExecutor）                             │
│  - キャッシング（@lru_cache, LRUCache）                       │
└─────────────┬────────────────────────────────────────────────┘
              │
              ├──────────────┬─────────────────┐
              ▼              ▼                 ▼
┌───────────────────┐ ┌──────────────┐ ┌─────────────────────┐
│ running_style     │ │ pace_data    │ │ dark_horse.db       │
│ _analyzer.py      │ │ _parser.py   │ │ (SQLite)            │
│ (脚質分析)         │ │ (ペース解析) │ │ (穴馬DB)            │
└───────────────────┘ └──────────────┘ └─────────────────────┘
              │
              │
              ▼
┌──────────────────────────────────────────────────────────────┐
│                 betting_strategy.py                          │
│                  (購入プラン生成)                             │
│  - 実力評価と期待値評価の統合                                  │
│  - 馬券タイプの推奨                                           │
└─────────────┬────────────────────────────────────────────────┘
              │
              ├──────────────────────┬──────────────────────┐
              ▼                      ▼                      ▼
┌──────────────────────┐  ┌──────────────────┐  ┌──────────────────────┐
│ result_formatter     │  │ obsidian_logger  │  │ unified_race_data    │
│ _v2.py               │  │ .py              │  │ .json                │
│ (V2フォーマッター)    │  │ (Obsidian連携)   │  │ (機械向けJSON)        │
└──────────────────────┘  └──────────────────┘  └──────────────────────┘
```

---

## データフロー

```
1. データ入力
   └─> data_loader.py (クリーニング + 読み込み)
        └─> config.json + race_data.json

2. 評価処理
   └─> horse_evaluator.py (モード別評価)
        ├─> running_style_analyzer.py (脚質分析 - 5min/fullのみ)
        ├─> pace_data_parser.py (ペース解析)
        ├─> dark_horse.db (穴馬情報)
        └─> 並列評価実行
             ├─> 実力評価結果
             └─> 期待値評価結果

3. プラン生成
   └─> betting_strategy.py
        └─> 購入プラン

4. 出力生成
   ├─> unified_race_data.json (常時)
   ├─> software_analysis.txt (3min/5min/full)
   ├─> prediction_report_v2.txt (オプション)
   └─> prediction_*.md (オプション - Obsidian)
```

---

## モジュール詳細

### 1. main.py
**責務**: システム全体の制御とパフォーマンス計測

**主要機能**:
- コマンドライン引数の解析
- モード別処理フローの制御
- 各フェーズの実行時間計測
- エラーハンドリングとログ出力

**依存関係**:
- data_loader
- horse_evaluator
- betting_strategy
- result_formatter_v2
- obsidian_logger

---

### 2. data_loader.py
**責務**: データのクリーニングと読み込み

**主要機能**:
- 古いデータのクリア（config.json, SQLite, キャッシュ）
- JSON読み込み（orjson使用）
- フォールバック機能

**セキュリティ**:
- ファイルパスの検証
- エンコーディングの明示（UTF-8）

---

### 3. data_fetcher.py (v4.0新規)
**責務**: データ取得（同期/非同期）

**主要機能**:
- ローカルファイル読み込み
- 外部API取得（将来対応 - httpx使用）
- キャッシュ管理
- パストラバーサル対策

**設計パターン**:
- Strategy Pattern（同期/非同期の切り替え）
- Cache Aside Pattern

---

### 4. horse_evaluator.py
**責務**: 馬の評価（実力評価・期待値評価）

**主要機能**:
- モード別ウェイト設定
  - 1分: Tier 1特徴量（3つ）
  - 3分: Tier 2特徴量（7つ）
  - 5分/full: Tier 3特徴量（11個）+ 脚質分析
- 並列評価処理（ThreadPoolExecutor）
- キャッシング（@lru_cache, LRUCache）

**評価アルゴリズム**:
```python
final_score = (
    past_performance * weight['past_performance'] +
    course_fit * weight['course_fit'] +
    track_condition * weight['track_condition'] +
    weight_change * weight['weight_change'] +
    interval * weight['interval'] +
    odds_value * weight['odds_value'] +
    dark_horse * weight['dark_horse'] +
    class_penalty
) * pace_adjustment
```

---

### 5. betting_strategy.py
**責務**: 購入プラン生成

**主要機能**:
- 実力評価と期待値評価の統合
- 馬券タイプの推奨
- 予算配分の最適化

---

### 6. obsidian_logger.py (v4.0改善)
**責務**: Obsidian用Markdown生成

**主要機能**:
- テンプレート処理
- 最終決定の自動判断
- 評価スコアの平均計算
- 展開予想のフォーマット

**セキュリティ**:
- ファイル名のサニタイゼーション
- パス検証

---

## パフォーマンス最適化

### 1. JSON処理
- **ライブラリ**: orjson
- **速度向上**: 標準jsonの2-3倍
- **使用箇所**: data_loader.py, data_fetcher.py, main.py

### 2. キャッシング
- **functools.lru_cache**: 関数レベルのキャッシング
- **cachetools.LRUCache**: グローバルキャッシュ
- **効果**: 重複計算の削減

### 3. 並列処理
- **ThreadPoolExecutor**: 馬評価の並列実行
- **max_workers**: os.cpu_count()で動的決定
- **効果**: マルチコア活用による高速化

### 4. モード別最適化
- **1分モード**: 脚質分析スキップ、特徴量削減
- **3分モード**: 脚質分析スキップ、標準特徴量
- **5分/fullモード**: 全機能使用

---

## セキュリティ設計

### 1. 入力検証

#### ファイルパス検証（data_fetcher.py）
```python
def _validate_file_path(self, file_path: str) -> Path:
    path = Path(file_path).resolve()
    if not path.is_relative_to(self.allowed_base_dir.resolve()):
        raise ValueError("Path outside allowed directory")
    return path
```

#### ファイル名サニタイゼーション（obsidian_logger.py）
```python
safe_race_name = "".join(c for c in race_name if c.isalnum() or c in (' ', '_', '-')).strip()
```

### 2. 例外処理

#### 具体的な例外型の指定
```python
try:
    # 処理
except (sqlite3.Error, IOError) as e:
    logger.warning(f"Expected error: {e}")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
```

### 3. ログ出力
- **機密情報の除外**: パスワード、APIキーなどは出力しない
- **適切なログレベル**: ERROR, WARNING, INFO, DEBUGの使い分け
- **ファイルとコンソール**: 両方に出力

---

## 拡張性設計

### 1. プラグインアーキテクチャ（将来）
新しい評価指標を簡単に追加できる設計

```python
class EvaluationPlugin:
    def evaluate(self, horse: Dict, race_data: Dict) -> float:
        pass

# 新しい評価指標の追加
evaluator.register_plugin(NewEvaluationPlugin())
```

### 2. API連携（data_fetcher.py）
外部APIからのデータ取得に対応

```python
# 現在はローカルファイルのみ
data = fetcher.get_race_data("data/race.json")

# 将来はAPIにも対応
data = await fetcher.get_race_data_async("https://api.example.com/race/123")
```

### 3. 新しい出力形式
新しいフォーマッターを追加可能

```python
# V3フォーマッターの追加例
formatter_v3 = ResultFormatterV3()
report = formatter_v3.format_complete_report(race_data, results)
```

---

## テスタビリティ

### 依存性注入
```python
# 現在
evaluator = HorseEvaluator(config, mode='3min')

# テスト時（モックDB使用）
mock_db = MockAnaumaDB()
evaluator = HorseEvaluator(config, mode='3min', db=mock_db)
```

### ユニットテスト（将来実装）
```python
# tests/test_horse_evaluator.py
def test_evaluate_horse_1min_mode():
    evaluator = HorseEvaluator(config, mode='1min')
    result = evaluator._evaluate_horse(sample_horse, sample_race_data)
    assert result['final_score'] > 0
```

---

## デプロイメント

### 必要環境
- Python 3.7+
- 8GB RAM推奨（大規模レースの場合）
- マルチコアCPU推奨（並列処理活用）

### 推奨設定
```bash
# 本番環境
export PYTHONUNBUFFERED=1
export LOG_LEVEL=INFO

# 開発環境
export LOG_LEVEL=DEBUG
```

---

## 監視とログ

### ログファイル
- **場所**: `logs/keiba_system.log`
- **ローテーション**: 推奨（外部ツール使用）
- **保持期間**: 30日推奨

### パフォーマンス監視
```bash
# ベンチマーク実行
python benchmark.py

# 処理時間確認
python main.py data/race.json --mode 3min | grep "総処理時間"
```

---

## 今後の改善計画

### 短期（1-3ヶ月）
- [ ] ユニットテストの追加
- [ ] CI/CDパイプラインの構築
- [ ] 静的解析ツールの導入

### 中期（3-6ヶ月）
- [ ] Web UI版の開発
- [ ] データベースのマイグレーション管理
- [ ] API版の提供

### 長期（6ヶ月以上）
- [ ] 機械学習モデルの強化
- [ ] リアルタイム予測機能
- [ ] マルチレース最適化

---

## 参考資料

- [README.md](README.md) - ユーザーガイド
- [CHANGELOG.md](CHANGELOG.md) - 変更履歴
- [requirements.txt](requirements.txt) - 依存パッケージ
- [config.json](config.json) - 評価基準設定

---

**Last Updated**: 2025-10-26
**Version**: 4.0.0
**Maintainer**: Claude Code

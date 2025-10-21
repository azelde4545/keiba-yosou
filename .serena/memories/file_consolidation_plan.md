# 競馬予想システム ファイル統合・削除計画

## 作業日時
2025-08-10

## 現状
- 総ファイル数: 50個以上
- 目標: 3ファイル（keiba_predictor.py, purchase_guide.py, config.json）

## 削除推奨ファイル・ディレクトリ

### 即座削除可能（キャッシュ系）
- [ ] `__pycache__/` ディレクトリ全体
- [ ] `analysis/__pycache__/` ディレクトリ
- [ ] `utils/__pycache__/` ディレクトリ
- [ ] `cache/` ディレクトリ
- [ ] `model_cache/` ディレクトリ
- [ ] `data_cache/` ディレクトリ
- [ ] `logs/` ディレクトリ
- [ ] `prediction_results/` ディレクトリ

### 統合後削除予定（モジュール系）
- [ ] `analysis/calculation_engine.py`
- [ ] `analysis/compact_race_analyzer.py`
- [ ] `analysis/performance_analyzer.py`
- [ ] `utils/fallback_system.py`
- [ ] `utils/safe_file_handler.py`
- [ ] `utils/utils.py`
- [ ] `scripts/run_prediction.py`
- [ ] `scripts/run_prediction_enhanced.py`
- [ ] `scripts/run_random_forest_analysis.py`

### その他の削除候補
- [ ] `core/` ディレクトリ（空の場合）
- [ ] `config/` ディレクトリ内の不要なファイル
- [ ] `data/` ディレクトリ内の重複ファイル

## 統合作業計画

### Phase 1: keiba_predictor.pyへの統合
1. analysisディレクトリの機能統合
   - calculation_engine.py → 計算メソッドとして統合
   - performance_analyzer.py → 評価メソッドとして統合
   - compact_race_analyzer.py → 必要な部分のみ統合

2. utilsディレクトリの機能統合
   - safe_file_handler.py → ファイル処理部分に統合
   - fallback_system.py → エラーハンドリング部分に統合
   - utils.py → 必要なユーティリティのみ統合

### Phase 2: purchase_guide.py作成
- keiba_predictor.pyから購入ガイド生成機能を分離
- 独立したモジュールとして整理

### Phase 3: 実行スクリプト統合
- scripts/内の3つのファイルを1つに統合
- または、keiba_predictor.pyに直接main関数を実装

## 最終的な構成（目標）
```
keiba/
├── keiba_predictor.py      # メイン予想システム
├── purchase_guide.py        # 購入ガイド生成
├── config.json             # 設定ファイル
├── dark_horse.db           # 穴馬データベース
└── data/
    └── race_data.json      # レースデータ
```

## 注意事項
- 削除前に必要な機能が統合されているか確認
- バックアップを取ってから削除実行
- 実行時間を測定して3分以内を確認
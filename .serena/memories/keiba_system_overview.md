# 競馬予想ソフト（keiba）の構成と動作

## [事実] システムの全体像

### 目的
レースデータJSONを入力として、2種類の評価（実力評価・期待値評価）を行い、購入プラン推奨まで提供する競馬予想ソフト。

### 動作フロー（4ステップ）
1. **STEP 1: データ読み込み** (DataLoader)
   - 古いデータをクリア（config.json, SQLiteキャッシュ, __pycache__など）
   - レースデータJSONを安全に読み込み

2. **STEP 2: 6要素評価（2種類）** (HorseEvaluator)
   - 実力評価: 過去成績、コース適性を重視
   - 期待値評価: オッズ妙味、穴馬を重視

3. **STEP 3: 購入プラン生成** (BettingStrategy)
   - 実力評価・期待値評価の結果から購入戦略を策定
   - 単勝購入のみ対応（予算に応じた複数点買い）

4. **STEP 4: デュアル・アウトプット生成**
   - unified_race_data.json（機械向け統合JSON）
   - software_analysis.txt（人間向け分析レポート）
   - prediction_report_v2.txt（オプション: 見やすいV2レポート）
   - prediction_*.md（オプション: Obsidian形式）

## [事実] 主要ファイル構成

### メインスクリプト
- **main.py**: システム全体の統合実行ファイル、コマンドライン引数処理

### コアモジュール
- **data_loader.py**: 古いデータ削除＋JSON読み込み
  - DataCleanerクラス: config, SQLite, __pycache__などをクリア
  - SafeDataLoaderクラス: JSON安全読み込み
  - DataLoaderクラス: 両者の統合

- **horse_evaluator.py**: 6要素評価システム（2種類の評価）
  - HorseEvaluatorクラス: 評価ロジック
  - FastAnaumaDBクラス: [不明] 役割不明

- **betting_strategy.py**: 購入プラン生成
  - BettingStrategyクラス: 予算に応じた購入戦略選択

- **result_formatter_v2.py**: V2フォーマッター
  - ResultFormatterV2クラス: 見やすいレポート生成

### 設定・データ
- **config.json**: システム基本設定
- **config/**: 複数の評価基準JSON
- **data/**: レースデータJSON（複数の過去レース）
- **data_backup/**: バックアップデータ

### 補助ファイル
- **README_v3.1.md**: 完全な使い方ガイド
- **logs/**: システムログ
- **output_analysis/**: 出力先ディレクトリ

### 不要な可能性あり
- **__pycache__/**: Pythonキャッシュ（自動削除対象）
- **input_pdf/, PDF/**: 入力PDF保管用？
- **.git/**: Gitバージョン管理（プロジェクトで必要な場合は保持）

## [推論] 整理提案

1. メインスクリプトをルートに集約
2. モジュール間の依存関係を明確化
3. 不要な一時ファイル・キャッシュの削除
4. ディレクトリ構成の標準化

## [不明] 確認が必要な点
- horse_evaluator.py内のFastAnaumaDBクラスの役割
- 複数の*_formatter*.pyファイルの関係性と使い分け
- 各output_*ファイル（test_output.txt等）の用途
- 複数のREADMEの役割分担

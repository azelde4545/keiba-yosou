# ファイル整理計画

## [事実] 現在の状況分析

### 使用中のファイル
- **main.py**: メインスクリプト（result_formatter_v2.py を17行目で import）
- **result_formatter_v2.py**: V2フォーマッター（実際に使用中）
- **data_loader.py**: データ読み込み（実際に使用中）
- **horse_evaluator.py**: 馬評価（実際に使用中）
- **betting_strategy.py**: 購入プラン（実際に使用中）
- **config/**: 複数の設定JSON
- **data/**: レースデータJSON（複数のレース）
- **README_v3.1.md**: 最新の使用ガイド

### [推論] 使用中の可能性がある補助ファイル
- **utils.py, pace_data_parser.py, running_style_analyzer.py**: 補助モジュール
- **config.json**: システム設定
- **logs/**: 実行ログ

### [推論] 削除候補1: 不要な古いフォーマッター
- **output_formatter.py**: main.py で import されていない
- **result_formatter.py**: main.py で import されていない
→ これらは古いバージョンの可能性

### [推論] 削除候補2: テストファイル
- **test_running_style.py**: 疾走型分析のテスト？
- **test_shuka.py**: 不明（ファイル内容確認が必要）
- **test_output.txt**: テスト出力ファイル
→ 本番運用では不要の可能性

### [推論] 削除候補3: 自動生成・キャッシュ関連
- **__pycache__/**: Python自動生成キャッシュ（100% 削除推奨）
- **dark_horse.db**: SQLiteデータベース（古いキャッシュデータを含む可能性）

### [推測] ディレクトリ整理
- **input_pdf/, PDF/**: PDFファイル保管用？（用途確認が必要）
- **data_backup/**: バックアップディレクトリ

## [不明] 確認が必要な点
1. output_formatter.py と result_formatter.py の用途
2. test_shuka.py の目的
3. input_pdf/ と PDF/ の区別
4. dark_horse.db の役割（system.log に記録があるか？）
5. utils.py 内のどの機能が実際に使用中か

## [推論] 推奨される整理フロー
1. 古いformatterファイルを確認後、削除
2. テストファイルを削除
3. __pycache__ を削除
4. data_backup を確認後、不要なら削除
5. ディレクトリ構成を標準化

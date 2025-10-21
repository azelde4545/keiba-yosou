# 現在のファイル状況確認（2025年10月19日）

## 📁 ディレクトリ構成

### ルートディレクトリのPythonファイル
- **main.py** - メイン実行エントリポイント
  - 4ステップの実行フロー（データ読込→馬評価→購入計画→出力生成）
  - コマンドライン引数対応：詳細ログ、V2フォーマッター、Obsidian出力

- **horse_evaluator.py** - HorseEvaluatorクラス（32-521行）
  - 主メソッド：evaluate_horses(), _evaluate_horse()
  - 評価メソッド×10（過去成績、コース適性、クラス適性、馬場条件、出走間隔、オッズ価値、穴馬判定、体重変化、クラスペナルティ）
  - スコア計算パラメータ約25個定義

- **data_loader.py** - DataLoaderクラス
  - JSONデータ読み込み
  - cleanup_and_load()メソッド

- **betting_strategy.py** - BettingStrategyクラス
  - generate_betting_plan()メソッド

- **output_formatter.py**, **result_formatter.py**, **result_formatter_v2.py**
  - 出力フォーマット管理

### 新規脚質判定モジュール
- **pace_data_parser.py** - ペースデータパーサー
  - parse_pace_data() - time_margin_paceから位置情報を抽出
  - calculate_running_style_stats() - 脚質統計を計算
  - 抽出項目：front_count, close_count, avg_up, avg_pos

- **running_style_analyzer.py** - 脚質判定メイン
  - RunningStyleAnalyzerクラス
  - determine_running_style() - 脚質判定（逃げ、先行、差し、追込、不明）
  - analyze() - 展開予測＋補正倍率計算

- **test_running_style.py** - テストスクリプト
  - 秋華賞サンプルデータで動作確認
  - ✅ テスト実行完了（脚質判定＆展開予測）

### データファイル（data/配下）
- 複数のレースJSON
  - data/race_data_20251018_富士ステークス.json
  - data/race_data_20251012_アイルランドトロフィー.json
  - 等×12ファイル

- 各JSONの構造：
  - race_info（レース情報）
  - horses[]（馬情報）
    - name, number, odds
    - recent_races[]
      - date, venue, distance, finish, runners
      - past_4_races[]:
        - **time_margin_pace** - パース対象
        - position_runners_pop - パース対象
        - その他の成績情報

## 🔄 データフロー現状

### 現在のフロー（main.py）
```
データ読込
  ↓
馬評価（HorseEvaluator）
  ├─ 過去成績評価
  ├─ コース適性
  ├─ クラス適性
  ├─ 馬場条件
  ├─ 出走間隔
  ├─ オッズ価値
  ├─ 穴馬判定
  └─ 他×3項目
  ↓
購入計画生成（BettingStrategy）
  ↓
出力生成（デュアル形式）
```

### 新規脚質判定モジュール（独立状態）
```
JSONデータ（past_4_races）
  ↓
pace_data_parser
  ├─ time_margin_paceをパース
  └─ front_count, close_count, avg_up, avg_pos を計算
  ↓
running_style_analyzer
  ├─ 個馬脚質判定
  ├─ レース展開予測
  └─ 補正倍率（±8-10%）を計算
```

## 📊 テスト結果

### 脚質判定テスト ✅ 成功
- ダノンフェアレディ：先行型（前傾2回、後傾2回）
- ジョスラン：差し型（前傾1回、後傾3回）
- カムニャック：先行型（前傾2回、後傾2回）

### 展開予測テスト
- 判定結果：平均（前傾上位合計1.41 = 後傾上位合計1.41）
- 補正倍率：全馬1.0000（±0%）
- ⚠️ サンプルデータが「平均展開」だったため、補正が発生しなかった

## 🔗 統合ポイント

### 統合前の課題認識
1. **脚質判定モジュールが独立している**
   - horse_evaluatorに組み込まれていない
   - main.pyで呼び出されていない

2. **データパイプラインの整合性**
   - horse_evaluatorの_eval_past_performance()は脚質データを使っていない
   - pace_data_parserの出力がhorse_evaluatorに入力されない

3. **補正倍率の活用方法**
   - 現在：calculate()で計算されるだけ
   - 必要：performance_scoreに補正倍率を掛ける

### 統合実装への準備
- ✅ ペースデータパーサー：完成
- ✅ 脚質判定モジュール：完成
- ✅ テスト：成功
- ⏳ 統合実装：次のステップ

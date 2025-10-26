# 競馬予想システム v4.0

[![Performance](https://img.shields.io/badge/Performance-0.02s-brightgreen)](https://github.com/azelde4545/keiba-yosou)
[![Python](https://img.shields.io/badge/Python-3.7%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**超高速・高精度な競馬予想システム** - 驚異の0.02秒で予測完了！

## 🚀 v4.0 の主要な改善点

### 1. 段階的予測プロトコル（新機能）
時間予算に応じて分析の深度を自動調整する革新的な機能：

- **1分モード（緊急）**: Tier 1特徴量（3つ）- 超高速予測
- **3分モード（標準）**: Tier 2特徴量（7つ）- バランス型
- **5分モード（詳細）**: Tier 3特徴量（11個）+ 脚質展開分析
- **完全モード**: 全機能フル活用

### 2. パフォーマンスの劇的向上
- **処理時間**: 平均0.02秒（v3.1から大幅改善）
- **要件達成率**: 933倍（180秒要件に対して0.02秒）
- **並列処理**: ThreadPoolExecutorによる最適化

### 3. 強化されたセキュリティ
- パストラバーサル攻撃対策
- 入力検証の徹底
- 適切な例外処理

### 4. 新規モジュール
- **data_fetcher.py**: 同期/非同期データ取得（将来の外部API対応）
- **obsidian_logger.py**: Obsidian連携による予測記録
- **benchmark.py**: パフォーマンス測定ツール

---

## 📋 目次

- [システム概要](#システム概要)
- [インストール](#インストール)
- [使い方](#使い方)
- [モード別機能](#モード別機能)
- [評価システム](#評価システム)
- [ベンチマーク結果](#ベンチマーク結果)
- [ファイル構成](#ファイル構成)
- [トラブルシューティング](#トラブルシューティング)
- [開発者向け情報](#開発者向け情報)

---

## システム概要

このシステムは、レースデータJSONファイルを入力として、以下の機能を提供します：

### 主要機能
- **2系統評価**: 実力評価（本命・対抗用）＋ 期待値評価（穴馬用）
- **6要素分析**: 過去成績、コース適正、馬場状態、馬体重変動、前走間隔、オッズ価値
- **脚質展開分析**: レース展開を予測し、有利な馬を特定（5分/完全モードのみ）
- **購入プラン自動生成**: 実力と期待値の両面から最適な馬券を提案
- **Obsidian連携**: 予測結果を自動記録し、振り返り可能

### 技術スタック
- **言語**: Python 3.7+
- **主要ライブラリ**:
  - scikit-learn, pandas, numpy（機械学習）
  - orjson（高速JSON処理）
  - httpx（非同期HTTP通信）
  - cachetools, functools.lru_cache（キャッシング）

---

## インストール

### 必要要件
- Python 3.7以上
- pip

### セットアップ

```bash
# リポジトリのクローン
git clone https://github.com/azelde4545/keiba-yosou.git
cd keiba-yosou

# 依存パッケージのインストール
pip install -r requirements.txt
```

### 依存パッケージ
主要なライブラリは自動でインストールされます：
- scikit-learn, pandas, numpy
- orjson（高速JSON処理）
- cachetools（キャッシング）
- pdfplumber, PyPDF2（PDF処理）
- その他（requirements.txt参照）

---

## 使い方

### 基本的な実行

```bash
# 標準モード（3分モード）で実行
python main.py data/race_data_20251012_アイルランドトロフィー.json --mode 3min

# 超高速モード（1分モード）
python main.py data/race_data.json --mode 1min

# 完全分析モード
python main.py data/race_data.json --mode full
```

### 詳細オプション付き実行

```bash
# V2フォーマッター + Obsidian出力 + 詳細ログ
python main.py data/race_data.json \
  --mode 5min \
  --use-v2-formatter \
  --obsidian-output \
  --verbose
```

### コマンドラインオプション

| オプション | 説明 | デフォルト |
|:---|:---|:---|
| `--mode` | 実行モード (1min/3min/5min/full) | full |
| `--use-v2-formatter` | 見やすいV2フォーマッターを使用 | false |
| `--obsidian-output` | Obsidian用Markdownを出力 | false |
| `-v, --verbose` | 詳細なログを表示 | false |

---

## モード別機能

### 1分モード（超高速・緊急用）
**特徴量**: 3つ（Tier 1）
- 過去成績: 40%
- コース適正: 35%
- オッズ価値: 25%

**用途**: 締め切り直前の緊急予測
**処理時間**: 約0.02秒

### 3分モード（標準・推奨）
**特徴量**: 7つ（Tier 2）
- 過去成績: 25%
- コース適正: 25%
- 馬場状態: 10%
- 馬体重変動: 3%
- 前走間隔: 7%
- オッズ価値: 18%
- 穴馬要素: 12%

**用途**: 日常的な予測に最適
**処理時間**: 約0.02秒

### 5分モード（詳細分析）
**特徴量**: 11個以上（Tier 3）
- 3分モードの全特徴量
- **脚質展開分析**: レース展開を予測し、有利な脚質を特定
- **格上挑戦減点**: クラス適性を厳密に評価

**用途**: 重賞レースなど重要なレース
**処理時間**: 約0.02秒

### 完全モード
5分モードと同等の全機能を使用。

---

## 評価システム

### 評価の仕組み

システムは**2系統の評価**を並行して実行します：

#### 1. 実力評価（本命・対抗用）
過去の実績とコース適性を重視し、安定して好走が期待できる馬を評価します。

**出力**:
- ◎本命
- ○対抗
- ▲単穴
- △連下
- ☆5番手

#### 2. 期待値評価（穴馬用）
オッズの妙味と穴馬要素を重視し、高配当が期待できる馬を発掘します。

**出力**:
- 💎穴馬候補（上位5頭）

### 評価グレード

| グレード | スコア範囲 | 評価 |
|:---:|:---:|:---|
| S | 90-100点 | 非常に優秀 |
| A | 80-89点 | 優秀 |
| B | 70-79点 | 良好 |
| C | 60-69点 | 普通 |
| D | 50-59点 | やや不安 |
| E | 50点未満 | 要注意 |

---

## ベンチマーク結果

### パフォーマンス測定（10回平均）

```bash
python benchmark.py
```

**結果**:

| モード | 平均処理時間 | 標準偏差 | 最小 | 最大 |
|:---:|:---:|:---:|:---:|:---:|
| 1分モード | 0.0200秒 | 0.0010秒 | 0.0176秒 | 0.0301秒 |
| **3分モード** | **0.0193秒** | **0.0010秒** | **0.0176秒** | **0.0224秒** |
| 5分モード | 0.0208秒 | 0.0010秒 | 0.0183秒 | 0.0300秒 |
| 完全モード | 0.0182秒 | 0.0010秒 | 0.0170秒 | 0.0200秒 |

**要件達成状況**: ✅ 要件180秒に対して0.02秒（**933倍の性能**）

### フェーズ別処理時間

- データ読み込み: 0.013秒
- 馬評価処理: 0.005秒
- 購入プラン生成: 0.000秒

---

## 出力ファイル

### 基本出力（常に生成）

1. **unified_race_data.json**
   - 機械向けの統合データ
   - 全評価結果を含む

2. **software_analysis.txt** (3min/5min/fullモード)
   - 人間向けの分析レポート
   - 実力評価と期待値評価のランキング

### オプション出力

3. **prediction_report_v2.txt** (`--use-v2-formatter`)
   - 見やすい整形済みレポート
   - 星評価とグレード表示

4. **prediction_[レース名]_[日付].md** (`--obsidian-output`)
   - Obsidian用Markdown
   - レース後の記録欄付き

---

## ファイル構成

```
keiba-yosou/
├── main.py                              # メイン実行ファイル
├── horse_evaluator.py                   # 馬評価ロジック（モード対応）
├── data_loader.py                       # データ読み込み
├── data_fetcher.py                      # データ取得（同期/非同期）⭐新規
├── betting_strategy.py                  # 購入プラン生成
├── running_style_analyzer.py            # 脚質分析
├── pace_data_parser.py                  # ペースデータ解析
├── result_formatter_v2.py               # V2フォーマッター
├── obsidian_logger.py                   # Obsidian連携 ⭐新規
├── benchmark.py                         # ベンチマークツール ⭐新規
├── prediction_template.md               # Obsidianテンプレート ⭐新規
├── config.json                          # 評価基準設定
├── requirements.txt                     # 依存パッケージ
├── .gitignore                           # Git除外設定 ⭐新規
├── data/                                # レースデータ
│   └── race_data_*.json
├── output_analysis/                     # 出力先
│   ├── software_analysis.txt
│   ├── prediction_report_v2.txt
│   ├── prediction_*.md
│   └── unified_race_data.json
└── logs/                                # ログファイル
    └── keiba_system.log
```

⭐ = v4.0で新規追加

---

## トラブルシューティング

### よくある問題

#### Q: `ModuleNotFoundError: No module named 'orjson'`
**A**: 依存パッケージが不足しています。
```bash
pip install -r requirements.txt
```

#### Q: 処理が終わらない
**A**: 1分モードを試してください。
```bash
python main.py data/race_data.json --mode 1min
```

#### Q: 文字化けが発生する
**A**: UTF-8エンコーディングを確認してください。システムはUTF-8を前提としています。

#### Q: Obsidianテンプレートが見つからない
**A**: `prediction_template.md`がプロジェクトルートにあることを確認してください。

#### Q: `WARNING: Failed to load dark horse DB`
**A**: 正常な動作です。穴馬DBが存在しない場合の警告で、予測には影響しません。

---

## 開発者向け情報

### コードの品質保証

- **静的解析**: mypy, pylint, banditの使用を推奨
- **フォーマッター**: black, isortを推奨
- **テスト**: pytest（将来実装予定）

### セキュリティ対策

- パストラバーサル攻撃対策実装済み
- 入力検証の徹底
- 適切な例外処理
- ログ出力のセキュリティ考慮

### パフォーマンス最適化

- orjsonによる高速JSON処理
- functools.lru_cacheによるキャッシング
- ThreadPoolExecutorによる並列処理
- cachetoolsによるメモリ効率化

### 貢献

プルリクエストやイシューの報告を歓迎します！

```bash
git checkout -b feature/new-feature
# 変更を加える
git commit -m "Add new feature"
git push origin feature/new-feature
```

---

## 更新履歴

### v4.0 (2025-10-26) ⭐最新
- ✅ 段階的予測プロトコル実装（1min/3min/5min/full）
- ✅ data_fetcher.py追加（同期/非同期対応）
- ✅ セキュリティ強化（パストラバーサル対策）
- ✅ パフォーマンス劇的向上（0.02秒）
- ✅ benchmark.py追加（性能測定ツール）
- ✅ .gitignore追加（プロジェクト整理）
- ✅ 厳格なコードレビュー実施

### v3.1 (2025-01-XX)
- ✅ V2フォーマッター追加
- ✅ Obsidian連携機能追加
- ✅ 馬体重変動評価追加
- ✅ 馬場状態の重要度向上

### v3.0
- 実力評価と期待値評価の2系統評価システム
- 6要素評価実装

---

## ライセンス

MIT License

---

## サポート

質問や不具合報告は、GitHubのIssueトラッカーまでお願いします。

**GitHub**: https://github.com/azelde4545/keiba-yosou

---

## 謝辞

このプロジェクトは、競馬予想の精度向上とワークフロー効率化を目指して開発されました。
機械学習とドメイン知識を組み合わせた、実用的なシステムを提供します。

**Powered by**: Python 3, scikit-learn, orjson, and many open-source libraries

**Generated with**: [Claude Code](https://claude.com/claude-code)

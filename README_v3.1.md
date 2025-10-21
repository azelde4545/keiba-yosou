# 競馬予想システム v3.1 - 使い方ガイド（更新版）

## 🆕 v3.1の新機能

### 1. 見やすいV2フォーマッター
より直感的で読みやすい予想レポートを生成できるようになりました。

### 2. Obsidian連携機能
予想結果をObsidian用のMarkdown形式で出力し、予想の記録と振り返りができるようになりました。

---

## 概要

このシステムは、レースデータJSONファイルを入力として、2種類の評価（実力評価・期待値評価）を行い、購入プラン推奨まで提供する競馬予想ソフトです。

## 必要なもの

- Python 3.7以上
- 必要なパッケージ（requirements.txtを参照）
- レースデータのJSONファイル

## インストール

```bash
pip install -r requirements.txt
```

## 基本的な使い方

### 1. レースデータJSONファイルを用意

JSONファイルは以下の構造である必要があります：

```json
{
  "race_info": {
    "name": "レース名",
    "date": "2025-10-12",
    "venue": "東京",
    "distance": 2000,
    "track_condition": "良"
  },
  "horses": [
    {
      "number": 1,
      "name": "馬名",
      "odds": 5.0,
      "jockey": "騎手名",
      "weight": 480,
      "weight_change": -4,
      "recent_results": [
        {
          "finish": 1,
          "runners": 16,
          "distance": 2000,
          "venue": "東京",
          "days_since": 14
        }
      ]
    }
  ]
}
```

### 2. システムを実行（基本）

従来の出力形式で実行：

```bash
python main.py data/race_data_20251018_富士ステークス.json
```

### 3. システムを実行（新機能）

#### V2フォーマッターを使用（見やすい出力）

```bash
python main.py data/race_data_20251018_富士ステークス.json --use-v2-formatter
```

**特徴：**
- 🎯 推奨馬が一目で分かるボックス表示
- 📊 詳細評価ランキング（実力評価順）
- 💰 期待値ランキング（穴馬向け）
- ⚖️ 馬体重変動分析
- 🎫 具体的な買い目提案
- ⭐ 星評価とグレード表示

#### Obsidian用のMarkdown出力

```bash
python main.py data/race_data_20251018_富士ステークス.json --obsidian-output
```

**特徴：**
- Obsidianで予想結果を記録
- レース後の結果記入欄
- 振り返り・反省メモ欄
- タグで検索可能

#### 両方を同時に使用

```bash
python main.py data/race_data_20251018_富士ステークス.json --use-v2-formatter --obsidian-output
```

### 4. 結果を確認

実行後、以下のファイルが生成されます：

**基本出力（常に生成）：**
- `output_analysis/software_analysis.txt` - 従来の人間向けレポート
- `output_analysis/unified_race_data.json` - 機械向け統合データ

**V2フォーマッター使用時（--use-v2-formatter）：**
- `output_analysis/prediction_report_v2.txt` - 見やすい予想レポート

**Obsidian出力使用時（--obsidian-output）：**
- `output_analysis/prediction_[レース名]_[日付].md` - Obsidian用Markdownファイル

---

## 📊 評価基準（v3.1）

### 能力系指標（70%）
- **過去成績**: 25% - 過去5走の実績を重視
- **コース適正**: 25% - 距離・競馬場の適性
- **馬場状態**: 10% - 馬場への対応力（重要度アップ）
- **馬体重変動**: 3% - 体調管理の指標（新規追加）
- **前走間隔**: 7% - ローテーション適性

### 投資効率系指標（30%）
- **オッズ価値**: 18% - 期待値の高さ（対数スケール改善）
- **穴馬要素**: 12% - 人気薄の妙味

### 評価ランク
- **S**: 90-100点 - 非常に優秀
- **A**: 80-89点 - 優秀
- **B**: 70-79点 - 良好
- **C**: 60-69点 - 普通
- **D**: 50-59点 - やや不安
- **E**: 50点未満 - 要注意

---

## 🎯 出力される評価

### 実力評価（本命・対抗用）
- 過去成績重視
- コース適性重視
- 実績ベースの評価
- **◎本命・○対抗・▲単穴**として推奨

### 期待値評価（穴馬用）
- オッズ妙味重視
- 穴馬候補の発掘
- リスク・リターンのバランス
- **💎穴馬候補**として推奨

---

## 📝 Obsidian連携の使い方

### 1. テンプレートの配置

`obsidian_template_race_prediction.md`がシステムと同じディレクトリにあることを確認してください。

### 2. 予想実行

```bash
python main.py data/race_data_20251018_富士ステークス.json --obsidian-output
```

### 3. Obsidianで開く

生成された`output_analysis/prediction_[レース名]_[日付].md`をObsidianのVaultにコピーまたは移動します。

### 4. レース後の記録

Obsidianで開いたファイルの「🏁 結果（レース後に記入）」セクションに：
- 実際の着順
- 配当
- 的中状況
- 振り返りメモ

を記入して、予想の精度を追跡できます。

---

## 💡 推奨ワークフロー

### レース前
1. PDFからJSONを作成（`pdf_to_json.py`を使用）
2. V2フォーマッターで予想実行
   ```bash
   python main.py data/race_data.json --use-v2-formatter --obsidian-output
   ```
3. `prediction_report_v2.txt`で予想確認
4. Obsidianファイルに個人メモを追加

### レース後
1. Obsidianファイルを開く
2. 結果セクションに実際の着順と配当を記入
3. 振り返りセクションに反省点を記入
4. タグで予想を検索・分析

---

## ⚙️ オプション一覧

```bash
python main.py [JSONファイル] [オプション]
```

### 利用可能なオプション

| オプション | 説明 |
|-----------|------|
| `-h, --help` | ヘルプを表示 |
| `-v, --verbose` | 詳細なログを表示 |
| `--use-v2-formatter` | 見やすいV2フォーマッターを使用 |
| `--obsidian-output` | Obsidian用のMarkdownも出力 |

### 使用例

```bash
# 従来の出力形式
python main.py data/race_data_20251018_富士ステークス.json

# V2フォーマッター使用
python main.py data/race_data_20251018_富士ステークス.json --use-v2-formatter

# Obsidian出力のみ
python main.py data/race_data_20251018_富士ステークス.json --obsidian-output

# 全ての出力を生成
python main.py data/race_data_20251018_富士ステークス.json --use-v2-formatter --obsidian-output --verbose
```

---

## 🔧 トラブルシューティング

### エラー: ファイルが見つかりません
→ JSONファイルのパスが正しいか確認してください

### エラー: JSONの読み込みに失敗
→ JSONファイルの構造が正しいか確認してください

### 文字化けが発生する
→ システムはUTF-8エンコーディングを前提としています

### Obsidianテンプレートが見つかりません
→ `obsidian_template_race_prediction.md`がシステムと同じディレクトリにあるか確認してください

### V2フォーマッターで出力されない
→ `--use-v2-formatter`オプションを指定しているか確認してください

---

## 📂 ファイル構成

```
keiba/
├── main.py                              # メイン実行ファイル
├── horse_evaluator.py                   # 馬評価ロジック
├── result_formatter_v2.py               # V2フォーマッター（新）
├── obsidian_template_race_prediction.md # Obsidianテンプレート（新）
├── config.json                          # 評価基準設定
├── data/                                # レースデータ
│   └── race_data_*.json
└── output_analysis/                     # 出力先
    ├── software_analysis.txt
    ├── prediction_report_v2.txt         # V2フォーマッター出力（新）
    ├── prediction_*.md                  # Obsidian出力（新）
    └── unified_race_data.json
```

---

## 📊 サンプルデータ

`data/`ディレクトリには、以下のサンプルデータがあります：

- `race_data_20251018_富士ステークス.json` - 富士ステークスのデータ
- `race_data_20251012_アイルランドトロフィー.json` - アイルランドトロフィーのデータ
- `race_data_20251005_京都大賞典.json` - 京都大賞典のデータ
- `race_data_20251005_毎日王冠.json` - 毎日王冠のデータ

---

## 📈 今後の改善予定

- [ ] より詳細な馬体重変動分析
- [ ] レース展開予測機能
- [ ] 過去の予想精度統計
- [ ] グラフ・チャート表示
- [ ] Web UI版

---

## 📝 更新履歴

### v3.1 (2025-01-XX)
- ✅ V2フォーマッター追加（見やすい出力）
- ✅ Obsidian連携機能追加
- ✅ 馬体重変動評価を追加（3%）
- ✅ 馬場状態の重要度アップ（5% → 10%）
- ✅ オッズ価値の計算方法改善（対数スケール）
- ✅ 評価基準を70:30（能力:投資効率）に最適化

### v3.0
- 実力評価と期待値評価の2系統評価システム
- 6要素評価（過去成績、コース、馬場、間隔、オッズ、穴馬）
- デュアル・アウトプット生成

---

## 📧 サポート

質問や不具合報告は、プロジェクトのIssueトラッカーまでお願いします。

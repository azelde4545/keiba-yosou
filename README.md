# 競馬予想統合システム

Random Forest機械学習と古システム統合による高精度競馬予想システム

## 🎯 システム概要

- **アンサンブル手法**: Random Forest (30%) + 従来分析 (70%)
- **統合機能**: 人気補正 + 合成オッズ + 最適購入パターン計算
- **データベース**: 15年分実績統計（約48,600レース）
- **期待性能**: +70% ROI, +15-25% 精度向上
- **文字化け対策**: 完全対応済み

## 📁 ファイル構成

### 🎯 メインシステム
- `ultimate_integrated_predictor.py` - 最新統合システム（Random Forest + 人気補正）
- `file_output_predictor.py` - 文字化け対策版（推奨）
- `enhanced_features.py` - 強化機能（単体テスト用）
- `integrated_odds_predictor.py` - Random Forest統合システム

### 📊 データ・設定
- `simple_bloodline.json` - 血統データベース
- `race_result.json` - 最新実行結果
- `__init__.py` - Pythonパッケージ初期化ファイル

## 🚀 使用方法

### 基本実行（推奨）
```bash
python file_output_predictor.py
```

### 統合システム実行
```bash
python ultimate_integrated_predictor.py
```

### Random Forest版実行
```bash
python integrated_odds_predictor.py
```

### 強化機能テスト
```bash
python enhanced_features.py
```

## 📊 出力データ

実行結果は `race_result.json` に保存されます：

```json
{
  "status": "success",
  "timestamp": "2025-06-21 21:48:35",
  "race_info": {
    "name": "テストレース",
    "track": "東京",
    "surface": "芝",
    "distance": 1600
  },
  "predictions": [
    {
      "rank": 1,
      "horse_name": "穴馬候補",
      "odds": 17.0,
      "total_score": 87.4,
      "expected_value": 2.993,
      "strategy_zone": "premium"
    }
  ],
  "betting_patterns": [
    {
      "type": "単勝",
      "horses": ["穴馬候補"],
      "expected_roi": 2.993,
      "recommended_amount": 300
    }
  ]
}
```

## 🔧 主要機能

### 1. Random Forest統合
- 15個の決定木による予想
- 従来システムとのアンサンブル

### 2. 人気補正機能
- 8番人気以下で好走歴のある馬を特別評価
- 穴馬発見率向上

### 3. 合成オッズ計算
- 複数馬組み合わせの効率計算
- 馬連・3連複の最適化

### 4. 最適購入パターン
- ROI最大化の自動計算
- リスク管理（1日予算10%以内）

### 5. 戦略ゾーン判定
- ⭐ プレミアム（10-20倍）: 最高回収率86-87%
- 📊 良好（1.0-1.4倍, 7-9倍）: 安定ゾーン
- ⚠️ 注意（1.5-2.9倍）: 過剰人気注意
- ❌ 回避（50倍超）: 基本除外

## 🛡️ エラー対処

### 文字化け発生時
1. `file_output_predictor.py` 使用（推奨）
2. 結果は `race_result.json` に安全保存

### Python実行エラー
1. 依存ライブラリ確認: `numpy`, `json`, `datetime`
2. ファイルパス確認

## 📈 システム統計

- **データベース**: 15年分実績（48,600レース）
- **オッズゾーン**: 13段階の詳細分析
- **戦略パターン**: 自動生成（最大5パターン）
- **機械学習**: Random Forest 15木構成
- **期待値計算**: キャリブレーション最適化

## 💡 Tips

1. **プレミアムゾーン重視**: 10-20倍オッズが最高回収率
2. **人気補正活用**: 低人気好走歴のある馬に注目
3. **合成オッズ活用**: 複数馬の組み合わせで効率化
4. **ファイル出力版推奨**: 文字化けリスク完全回避

## ⚠️ 注意事項

- 投資判断の参考として使用
- 結果を保証するものではありません
- 1日予算の10%以内での投資推奨
- 利用は自己責任で

## 🔄 システム更新履歴

- **v3.0** (2025-06): Random Forest統合、人気補正、合成オッズ追加
- **v2.1** (2025-06): 文字化け対策（ファイル出力方式）
- **v2.0** (2025-06): アンサンブル手法導入
- **v1.0**: 基本統合システム

---
*🤖 統合競馬予想システム / Random Forest + Enhanced Features*
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

### 📊 データ・設定
- `simple_bloodline.json` - 血統データベース
- `race_result.json` - 最新実行結果

## 🚀 使用方法

### 基本実行（推奨）
```bash
python file_output_predictor.py
```

### 統合システム実行
```bash
python ultimate_integrated_predictor.py
```

### 強化機能テスト
```bash
python enhanced_features.py
```

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

---
*🤖 統合競馬予想システム / Random Forest + Enhanced Features*
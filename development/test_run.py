#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(__file__))

from integrated_odds_predictor import IntegratedOddsPredictor, create_sample_race_with_complete_odds

def test_system():
    print("=== 競馬予想システム動作確認 ===")
    
    # システム初期化
    predictor = IntegratedOddsPredictor()
    
    # テストレース作成
    test_race = create_sample_race_with_complete_odds()
    
    # 予想実行
    result = predictor.predict_race_with_odds_analysis(test_race)
    
    print(f"\n【{test_race['race_name']}】")
    print(f"コース: {test_race['track']} {test_race['surface']}{test_race['distance']}m")
    print("-" * 50)
    
    # 上位3頭の結果表示
    for i, pred in enumerate(result['predictions'][:3], 1):
        zone_icon = "⭐" if pred['strategy_zone'] == 'premium' else \
                   "📊" if pred['strategy_zone'] == 'good' else \
                   "⚠️" if pred['strategy_zone'] == 'caution' else "❌"
        
        print(f"{i}位: {pred['horse_name']} {zone_icon}")
        print(f"   オッズ: {pred['odds']}倍 | スコア: {pred['total_score']} | 期待値: {pred['expected_value']:+.3f}")
        print(f"   勝率: {pred['actual_stats']['win_rate']:.1%} | 回収率: {pred['actual_stats']['recovery_rate']}%")
        print()
    
    # システム情報
    summary = result['analysis_summary']
    print(f"✅ システム正常動作確認")
    print(f"📈 プレミアムゾーン: {summary['premium_zone_horses']}頭")
    print(f"💰 期待値プラス: {summary['positive_expected_value']}頭")
    
    return True

if __name__ == "__main__":
    try:
        test_system()
        print("\n🎯 システム準備完了！")
    except Exception as e:
        print(f"❌ エラー: {e}")

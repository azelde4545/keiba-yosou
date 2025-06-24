#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(__file__))

from ultimate_integrated_predictor import UltimateIntegratedPredictor, create_enhanced_test_race

def test_complete_system():
    """完全システムテスト"""
    print("=== 新・競馬予想統合システム テスト ===")
    print()
    
    try:
        # システム初期化
        print("🤖 システム初期化中...")
        predictor = UltimateIntegratedPredictor()
        
        # テストレース作成
        test_race = create_enhanced_test_race()
        print(f"📊 テストレース: {test_race['race_name']}")
        print()
        
        # 予想実行
        print("🎯 予想実行中...")
        result = predictor.predict_race_with_enhanced_analysis(test_race)
        
        # 結果表示
        print(f"【{test_race['race_name']}】")
        print(f"コース: {test_race['track']} {test_race['surface']}{test_race['distance']}m")
        print("-" * 50)
        
        # 上位3頭の結果表示
        for i, pred in enumerate(result['predictions'][:3], 1):
            zone_icon = "⭐" if pred['strategy_zone'] == 'premium' else \
                       "📊" if pred['strategy_zone'] == 'good' else \
                       "⚠️" if pred['strategy_zone'] == 'caution' else "❌"
            
            print(f"{i}位: {pred['horse_name']} {zone_icon}")
            print(f"   オッズ: {pred['odds']}倍 | スコア: {pred['total_score']} | 期待値: {pred['expected_value']:+.3f}")
            
            # 強化機能確認
            if pred['enhanced_features']['popularity_correction']:
                print(f"   ✅ 人気補正機能: ON")
            if pred['enhanced_features']['synthetic_odds_ready']:
                print(f"   ✅ 合成オッズ: 対応")
            if pred['enhanced_features']['optimal_betting_ready']:
                print(f"   ✅ 最適購入パターン: 対応")
            print()
        
        # 最適購入パターン
        patterns = result['optimal_betting_patterns']
        if patterns:
            print("💰 最適購入パターン:")
            for i, pattern in enumerate(patterns[:2], 1):
                print(f"  {i}. {pattern['type']}: {', '.join(pattern['horses'])}")
                print(f"     期待ROI: {pattern['expected_roi']:+.3f} | 推奨: {pattern['recommended_amount']}円")
            print()
        
        # システム情報
        system_info = result['system_info']
        print("🔧 システム構成:")
        print(f"- {system_info['ensemble_method']}")
        for feature in system_info['enhanced_features'][:2]:
            print(f"- {feature}")
        print()
        
        # 分析サマリー
        summary = result['analysis_summary']
        print("📈 分析結果:")
        print(f"- 総出走頭数: {summary['total_horses']}頭")
        print(f"- プレミアムゾーン: {summary['premium_zone_horses']}頭")
        print(f"- 期待値プラス: {summary['positive_expected_value']}頭")
        print(f"- 推奨戦略: {summary['recommended_focus']}")
        print()
        
        print("✅ システム正常動作確認完了")
        return True
        
    except Exception as e:
        print(f"❌ エラー発生: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_system()
    if success:
        print("\n🎯 新・競馬予想統合システム 準備完了！")
        print("📝 新しいワークフローでスムーズな予想が可能です")
    else:
        print("\n⚠️ システムエラーが発生しました。修正が必要です。")

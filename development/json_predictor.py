#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON出力版競馬予想システム
- 文字化けの心配がない英語・数値出力
- Obsidianテンプレートでの読み込み用
"""

import json
import sys
import os
from datetime import datetime

# メインシステムをインポート
try:
    from ultimate_integrated_predictor import UltimateIntegratedPredictor, create_enhanced_test_race
except ImportError as e:
    print(json.dumps({"error": f"Import failed: {e}"}))
    sys.exit(1)

def main_json_output():
    """JSON形式で結果出力"""
    try:
        # システム初期化・実行
        predictor = UltimateIntegratedPredictor()
        test_race = create_enhanced_test_race()
        result = predictor.predict_race_with_enhanced_analysis(test_race)
        
        # JSON用データ構造化
        json_output = {
            "status": "success",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "race_info": {
                "name": test_race.get('race_name', ''),
                "track": test_race.get('track', ''),
                "surface": test_race.get('surface', ''),
                "distance": test_race.get('distance', 0),
                "condition": test_race.get('condition', '')
            },
            "predictions": [],
            "betting_patterns": result.get('optimal_betting_patterns', []),
            "system_info": {
                "method": result['system_info']['ensemble_method'],
                "performance": result['system_info']['expected_performance'],
                "features_count": len(result['system_info']['enhanced_features'])
            },
            "summary": result.get('analysis_summary', {})
        }
        
        # 予想結果を構造化
        for i, pred in enumerate(result['predictions'], 1):
            json_output["predictions"].append({
                "rank": i,
                "horse_name": pred.get('horse_name', ''),
                "horse_number": pred.get('horse_number', 0),
                "jockey": pred.get('jockey', ''),
                "odds": pred.get('odds', 0.0),
                "total_score": pred.get('total_score', 0.0),
                "expected_value": pred.get('expected_value', 0.0),
                "strategy_zone": pred.get('strategy_zone', ''),
                "win_probability": pred.get('win_probability', 0.0),
                "popularity_correction": pred.get('enhanced_features', {}).get('popularity_correction', False),
                "recovery_rate": pred.get('actual_stats', {}).get('recovery_rate', 0)
            })
        
        # JSON出力
        print(json.dumps(json_output, ensure_ascii=False, indent=2))
        
    except Exception as e:
        # エラー時もJSON形式
        error_output = {
            "status": "error",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "error_message": str(e),
            "fallback_mode": True
        }
        print(json.dumps(error_output, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main_json_output()

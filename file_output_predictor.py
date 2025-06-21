#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ファイル出力版競馬予想システム（予算対応版）
- 結果をJSONファイルに保存
- Obsidianテンプレートはファイルを読み込み
- 文字化けを完全に回避
- ユーザー予算に応じた最適購入パターン計算
- 詳細な選択馬情報表示
"""

import json
import sys
import os
from datetime import datetime

def setup_windows_encoding():
    """Windows環境での文字化け対策"""
    if sys.platform.startswith('win'):
        # 環境変数設定
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        
        # 標準出力の再設定
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# エンコーディング設定
setup_windows_encoding()

# メインシステムをインポート
try:
    from ultimate_integrated_predictor import UltimateIntegratedPredictor, create_enhanced_test_race
    from enhanced_features import EnhancedFeatures, get_user_budget
except ImportError as e:
    # エラーをファイルに出力
    error_data = {
        "status": "error",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "error_type": "import_error",
        "error_message": str(e)
    }
    with open('race_result.json', 'w', encoding='utf-8') as f:
        json.dump(error_data, f, ensure_ascii=False, indent=2)
    sys.exit(1)

def main_file_output():
    """ファイル出力メイン処理（予算対応版）"""
    output_file = 'race_result.json'
    
    try:
        # 予算取得（300円・600円の安全網付き）
        budgets = get_user_budget()
        
        print("\\n競馬予想システム実行中...")
        
        # システム初期化・実行
        predictor = UltimateIntegratedPredictor()
        enhanced_features = EnhancedFeatures()
        test_race = create_enhanced_test_race()
        result = predictor.predict_race_with_enhanced_analysis(test_race)
        
        # 各予算での最適購入パターン計算
        all_betting_patterns = {}
        for budget in budgets:
            patterns = enhanced_features.find_optimal_betting_patterns(result['predictions'], budget)
            all_betting_patterns[f"{budget}円"] = patterns
        
        # 結果データ構造化
        output_data = {
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
            "budgets": budgets,
            "betting_patterns_by_budget": all_betting_patterns,
            "system_info": {
                "method": result['system_info']['ensemble_method'],
                "performance": result['system_info']['expected_performance'],
                "features": result['system_info']['enhanced_features'],
                "budget_feature": "予算対応版"
            },
            "summary": result.get('analysis_summary', {}),
            "encoding_safe": True,
            "file_output_method": True
        }
        
        # 予想結果を構造化
        for i, pred in enumerate(result['predictions'], 1):
            prediction_data = {
                "rank": i,
                "horse_name": pred.get('horse_name', ''),
                "horse_number": pred.get('horse_number', 0),
                "jockey": pred.get('jockey', ''),
                "odds": pred.get('odds', 0.0),
                "total_score": pred.get('total_score', 0.0),
                "expected_value": pred.get('expected_value', 0.0),
                "strategy_zone": pred.get('strategy_zone', ''),
                "win_probability": pred.get('win_probability', 0.0),
                "enhanced_features": pred.get('enhanced_features', {}),
                "actual_stats": pred.get('actual_stats', {})
            }
            output_data["predictions"].append(prediction_data)
        
        # JSONファイルに保存
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        # 詳細な結果表示
        premium_horses = [p['horse_name'] for p in output_data['predictions'] if p.get('strategy_zone') == 'プレミアム']
        positive_ev_horses = [p['horse_name'] for p in output_data['predictions'] if p.get('expected_value', 0) > 0]
        
        print(f"✅ 競馬予想完了: {output_file} に保存")
        print(f"📊 分析対象: {len(output_data['predictions'])}頭")
        
        # プレミアムゾーンの詳細表示
        if premium_horses:
            premium_list = "、".join(premium_horses)
            print(f"⭐ プレミアムゾーン: {len(premium_horses)}頭 ({premium_list})")
        else:
            print(f"⭐ プレミアムゾーン: なし")
        
        # 期待値プラスの詳細表示
        if positive_ev_horses:
            positive_list = "、".join(positive_ev_horses)
            print(f"💰 期待値プラス: {len(positive_ev_horses)}頭 ({positive_list})")
        else:
            print(f"💰 期待値プラス: なし")
        
        # 予算別購入パターン表示
        print(f"\\n🎯 予算別最適購入パターン:")
        for budget_str, patterns in all_betting_patterns.items():
            print(f"\\n【{budget_str}】")
            if patterns:
                for i, pattern in enumerate(patterns[:3], 1):  # 上位3パターン
                    horses_str = "×".join(pattern['horses'])
                    roi_percent = pattern['expected_roi'] * 100
                    print(f"  {i}. {pattern['type']}: {horses_str} ({pattern['recommended_amount']}円, ROI: {roi_percent:+.1f}%)")
            else:
                print("  推奨パターンなし")
        
        # 上位馬の詳細情報
        print(f"\\n🏇 上位予想:")
        for i, pred in enumerate(output_data['predictions'][:5], 1):
            zone_mark = "⭐" if pred.get('strategy_zone') == 'プレミアム' else "📈" if pred.get('expected_value', 0) > 0 else "📊"
            print(f"  {i}位 {zone_mark} {pred['horse_name']} (#{pred['horse_number']}, {pred['odds']:.1f}倍, {pred['jockey']})")
        
    except Exception as e:
        # エラー時もファイル出力
        error_data = {
            "status": "error",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "error_type": "execution_error",
            "error_message": str(e),
            "fallback_mode": True
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=2)
        
        print(f"❌ エラー発生: {output_file} にエラー情報を保存")

if __name__ == "__main__":
    main_file_output()

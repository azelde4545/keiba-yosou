#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
古いシステムから移植した強化機能
- 人気による補正機能（穴馬発見）
- 合成オッズ計算機能
- 最適購入パターン計算
"""

from typing import Dict, List, Tuple, Optional
import math
from itertools import combinations

class EnhancedFeatures:
    """強化機能クラス"""
    
    def apply_popularity_correction(self, score: float, result: int, popularity: int) -> float:
        """人気による補正機能（穴馬発見用）"""
        base_score = score
        
        # 人気別補正
        if popularity <= 3 and result <= 3:
            base_score += 10  # 人気馬が好走 → 普通
        elif popularity >= 8 and result <= 3:
            base_score += 20  # 低人気で好走 → 大きく評価UP（穴馬！）
        elif popularity >= 12 and result <= 5:
            base_score += 15  # 大穴馬でも5着以内は評価
        
        return min(base_score, 100.0)
    
    def calculate_synthetic_odds(self, odds_list: List[float]) -> float:
        """合成オッズ計算"""
        if not odds_list or any(odds <= 0 for odds in odds_list):
            return 0.0
        
        # 合成オッズ = 1 ÷ (1/オッズA + 1/オッズB + 1/オッズC ...)
        inverse_sum = sum(1 / odds for odds in odds_list)
        return 1 / inverse_sum if inverse_sum > 0 else 0.0
    
    def find_optimal_betting_patterns(self, predictions: List[Dict], 
                                     budget: int = 1000) -> List[Dict]:
        """最適購入パターン計算（ROI最大化）"""
        patterns = []
        
        # 期待値プラスの馬だけを対象
        positive_ev_horses = [p for p in predictions if p.get('expected_value', 0) > 0]
        
        if not positive_ev_horses:
            return patterns
        
        # 単勝パターン
        for horse in positive_ev_horses[:3]:  # 上位3頭
            roi = horse['expected_value']
            patterns.append({
                'type': '単勝',
                'horses': [horse['horse_name']],
                'odds': horse['odds'],
                'expected_roi': roi,
                'recommended_amount': min(budget * 0.3, 300)
            })
        
        # 複勝パターン
        for horse in positive_ev_horses[:2]:
            place_prob = horse.get('actual_stats', {}).get('place_rate', 0.3)
            roi = place_prob * (horse['odds'] * 0.2) - 1  # 複勝は単勝の約20%
            if roi > 0:
                patterns.append({
                    'type': '複勝',
                    'horses': [horse['horse_name']],
                    'odds': horse['odds'] * 0.2,
                    'expected_roi': roi,
                    'recommended_amount': min(budget * 0.2, 200)
                })
        
        # 馬連パターン（上位2頭の組み合わせ）
        if len(positive_ev_horses) >= 2:
            horse1, horse2 = positive_ev_horses[0], positive_ev_horses[1]
            combined_odds = self.calculate_synthetic_odds([horse1['odds'], horse2['odds']])
            combined_prob = horse1['win_probability'] * horse2['win_probability'] * 2  # 順序考慮
            roi = combined_prob * combined_odds - 1
            
            if roi > 0:
                patterns.append({
                    'type': '馬連',
                    'horses': [horse1['horse_name'], horse2['horse_name']],
                    'odds': combined_odds,
                    'expected_roi': roi,
                    'recommended_amount': min(budget * 0.25, 250)
                })
        
        # ROI順でソート
        patterns.sort(key=lambda x: x['expected_roi'], reverse=True)
        return patterns[:5]  # 上位5パターン
    
    def enhanced_recent_form_with_popularity(self, horse_data: Dict, race_info: Dict) -> float:
        """人気補正付き近走成績分析"""
        recent_results = horse_data.get('recent_results', [])
        if not recent_results:
            return 50.0
        
        score = 60.0
        weights = [0.4, 0.25, 0.2, 0.1, 0.05]
        weighted_score = 0.0
        total_weight = 0.0
        
        for i, result in enumerate(recent_results[:5]):
            if i >= len(weights):
                break
                
            weight = weights[i]
            race_result = result.get('result', 10)
            popularity = result.get('popularity', 8)
            
            # 基本成績評価
            if race_result == 1:
                result_score = 100
            elif race_result <= 3:
                result_score = 85
            elif race_result <= 5:
                result_score = 70
            else:
                result_score = 30
            
            # 人気による補正を適用
            result_score = self.apply_popularity_correction(result_score, race_result, popularity)
            
            weighted_score += result_score * weight
            total_weight += weight
        
        if total_weight > 0:
            score = weighted_score / total_weight
        
        return min(score, 100.0)
    
    def analyze_dark_horse_potential(self, horse_data: Dict, race_info: Dict) -> Dict:
        """穴馬ポテンシャル分析"""
        odds = horse_data.get('odds', 0.0)
        recent_results = horse_data.get('recent_results', [])
        
        # 穴馬の条件
        is_dark_horse = 8.0 <= odds <= 30.0
        
        if not is_dark_horse or not recent_results:
            return {'is_dark_horse': False, 'potential_score': 0}
        
        # 穴馬ポテンシャルスコア計算
        potential_score = 0
        
        # 最近の低人気好走歴
        for result in recent_results[:3]:
            popularity = result.get('popularity', 10)
            race_result = result.get('result', 10)
            
            if popularity >= 8 and race_result <= 5:
                potential_score += 25  # 低人気で好走歴あり
            elif popularity >= 5 and race_result <= 3:
                potential_score += 15  # 中人気で上位
        
        # 距離適性
        target_distance = race_info.get('distance', 1600)
        for result in recent_results:
            race_distance = result.get('distance', 0)
            if abs(race_distance - target_distance) <= 200 and result.get('result', 10) <= 5:
                potential_score += 10
        
        return {
            'is_dark_horse': True,
            'potential_score': min(potential_score, 100),
            'recommendation': 'HIGH' if potential_score >= 40 else 'MEDIUM' if potential_score >= 20 else 'LOW'
        }


def test_enhanced_features():
    """強化機能のテスト"""
    print("=== 強化機能テスト ===")
    
    features = EnhancedFeatures()
    
    # サンプルデータ
    sample_predictions = [
        {
            'horse_name': '穴馬候補', 'odds': 12.0, 'expected_value': 0.5,
            'win_probability': 0.15, 'actual_stats': {'place_rate': 0.35}
        },
        {
            'horse_name': '本命馬', 'odds': 2.5, 'expected_value': 0.2,
            'win_probability': 0.35, 'actual_stats': {'place_rate': 0.65}
        }
    ]
    
    # 合成オッズテスト
    combined_odds = features.calculate_synthetic_odds([12.0, 2.5])
    print(f"合成オッズ: {combined_odds:.2f}倍")
    
    # 最適購入パターン
    patterns = features.find_optimal_betting_patterns(sample_predictions, 1000)
    print(f"\n最適購入パターン:")
    for i, pattern in enumerate(patterns, 1):
        print(f"{i}. {pattern['type']}: {pattern['horses']} (ROI: {pattern['expected_roi']:+.3f})")
    
    # 穴馬分析
    dark_horse_data = {
        'odds': 15.0,
        'recent_results': [
            {'popularity': 10, 'result': 3, 'distance': 1600},
            {'popularity': 8, 'result': 5, 'distance': 1400}
        ]
    }
    
    dark_horse_analysis = features.analyze_dark_horse_potential(dark_horse_data, {'distance': 1600})
    print(f"\n穴馬分析: {dark_horse_analysis}")
    
    print("\n✅ 強化機能テスト完了")


if __name__ == "__main__":
    test_enhanced_features()

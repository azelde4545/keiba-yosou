#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合成オッズ機能付き競馬予想システム
- 期待値計算
- 合成オッズ計算
- 馬券購入推奨機能（4倍以上、最低100円条件対応）
"""

import json
import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from itertools import combinations

class EnhancedOddsPredictor:
    """合成オッズ機能付き予想システム"""
    
    def __init__(self):
        # 重み設定
        self.weights = {
            'recent_form': 0.28,     # 近走成績
            'distance_fit': 0.25,    # 距離適性  
            'running_style': 0.20,   # 脚質適性
            'track_condition': 0.12, # 馬場適性
            'jockey': 0.10,          # 騎手
            'course_fit': 0.05       # コース適性
        }
        
        # 距離カテゴリ定義
        self.distance_categories = {
            '芝': {
                'sprint': (1000, 1399),
                'mile': (1400, 1899),
                'intermediate': (1900, 2199),
                'long': (2200, 2799),
                'extended': (2800, 3600)
            },
            'ダート': {
                'sprint': (1000, 1399),
                'mile': (1400, 1899),
                'intermediate': (1900, 2199),
                'long': (2200, 2799),
                'extended': (2800, 3600)
            }
        }
        
        # トップ騎手リスト
        self.top_jockeys = [
            'C.ルメール', '武豊', '戸崎圭太', '川田将雅', 
            'M.デムーロ', '福永祐一', '池添謙一', '横山武史'
        ]
        
        # 血統データ
        self.bloodline_data = {
            "短距離が得意な血統": ["ダイワメジャー", "クロフネ", "ロードカナロア"],
            "重馬場が得意な血統": ["クロフネ", "ゴールドアリュール", "キングカメハメハ"]
        }
    
    def calculate_synthetic_odds(self, odds_list: List[float]) -> float:
        """合成オッズの計算
        合成オッズ = 1 ÷ (1 ÷ オッズA + 1 ÷ オッズB + 1 ÷ オッズC ...)
        """
        if not odds_list or any(odds <= 0 for odds in odds_list):
            return 0.0
        
        inverse_sum = sum(1 / odds for odds in odds_list)
        return 1 / inverse_sum if inverse_sum > 0 else 0.0
    
    def calculate_bet_allocation(self, total_amount: int, odds_list: List[float], synthetic_odds: float) -> List[int]:
        """馬券購入金額配分の計算
        買い目の購入金額 = 総購入金額 × 合成オッズ ÷ 買い目のオッズ
        """
        if synthetic_odds <= 0 or not odds_list:
            return []
        
        allocations = []
        for odds in odds_list:
            if odds <= 0:
                allocations.append(0)
                continue
            
            # 理論的な金額を計算
            theoretical_amount = total_amount * synthetic_odds / odds
            
            # 100円単位で調整（最低100円）
            adjusted_amount = max(100, round(theoretical_amount / 100) * 100)
            allocations.append(int(adjusted_amount))
        
        return allocations
    
    def find_recommended_betting_patterns(self, predictions: List[Dict], total_budget: int = 1000) -> List[Dict]:
        """推奨馬券購入パターンを検索
        条件: 合成オッズ4倍以上、最低100円以上購入
        """
        betting_patterns = []
        
        # 期待値が正の馬を候補とする
        candidates = [
            pred for pred in predictions
            if pred.get('odds', 0) > 0 and self.calculate_expected_value(
                pred.get('win_probability', 0), pred.get('odds', 0)
            ) > 0
        ]
        
        if not candidates:
            return []
        
        # 2頭から4頭の組み合わせを検討
        for combo_size in range(2, min(5, len(candidates) + 1)):
            for combo in combinations(candidates, combo_size):
                odds_list = [horse['odds'] for horse in combo]
                synthetic_odds = self.calculate_synthetic_odds(odds_list)
                
                # 合成オッズが4倍以上の条件をチェック
                if synthetic_odds < 4.0:
                    continue
                
                # 金額配分を計算
                allocations = self.calculate_bet_allocation(total_budget, odds_list, synthetic_odds)
                
                # 最低100円条件をチェック
                if not allocations or any(amount < 100 for amount in allocations):
                    continue
                
                # 実際の総投資額
                actual_total = sum(allocations)
                
                # 期待収益を計算
                expected_returns = []
                for i, horse in enumerate(combo):
                    win_prob = horse.get('win_probability', 0)
                    payout = allocations[i] * horse['odds']
                    expected_return = win_prob * payout
                    expected_returns.append(expected_return)
                
                total_expected_return = sum(expected_returns)
                profit = total_expected_return - actual_total
                roi = profit / actual_total if actual_total > 0 else 0
                
                pattern = {
                    'horses': [
                        {
                            'horse_name': horse['horse_name'],
                            'horse_number': horse['horse_number'],
                            'odds': horse['odds'],
                            'bet_amount': allocations[i],
                            'expected_payout': allocations[i] * horse['odds']
                        }
                        for i, horse in enumerate(combo)
                    ],
                    'synthetic_odds': round(synthetic_odds, 2),
                    'total_investment': actual_total,
                    'expected_return': round(total_expected_return, 1),
                    'profit': round(profit, 1),
                    'roi': round(roi * 100, 1)
                }
                
                betting_patterns.append(pattern)
        
        # ROI順で並び替え
        betting_patterns.sort(key=lambda x: x['roi'], reverse=True)
        
        return betting_patterns[:5]  # 上位5パターンを返す
    
    def odds_to_probability(self, odds: float) -> float:
        """オッズから勝率を計算"""
        if odds <= 1.0:
            return 0.0
        return 1.0 / odds
    
    def calculate_expected_value(self, predicted_prob: float, odds: float) -> float:
        """期待値を計算"""
        if odds <= 1.0:
            return 0.0
        return predicted_prob * odds - 1.0
    
    def get_distance_category(self, distance: int, surface: str) -> str:
        """距離カテゴリを取得"""
        surface_key = surface if surface in self.distance_categories else '芝'
        
        for category, (min_dist, max_dist) in self.distance_categories[surface_key].items():
            if min_dist <= distance <= max_dist:
                return category
        
        return 'intermediate'
    
    def analyze_recent_form(self, recent_results: List[Dict]) -> float:
        """近走成績の分析"""
        if not recent_results:
            return 30.0
        
        score = 0
        weights = [0.4, 0.3, 0.2, 0.1]
        
        for i, race in enumerate(recent_results[:4]):
            if i >= len(weights):
                break
                
            result = race.get('result', 999)
            popularity = race.get('popularity', 10)
            
            if result == 1:
                base_score = 100
            elif result == 2:
                base_score = 80
            elif result == 3:
                base_score = 60
            elif result <= 5:
                base_score = 40
            else:
                base_score = 20
            
            if popularity <= 3 and result <= 3:
                base_score += 10
            elif popularity >= 8 and result <= 3:
                base_score += 20
            
            score += base_score * weights[i]
        
        return min(score, 100)
    
    def analyze_distance_fit(self, horse_data: Dict, race_info: Dict) -> float:
        """距離適性の分析"""
        score = 60.0
        target_distance = race_info.get('distance', 1600)
        target_surface = race_info.get('surface', '芝')
        target_category = self.get_distance_category(target_distance, target_surface)
        
        recent_results = horse_data.get('recent_results', [])
        
        # 同距離カテゴリでの成績
        same_category_count = 0
        same_category_avg = 0
        
        for race in recent_results:
            race_distance = race.get('distance', 0)
            race_surface = race.get('surface', '芝')
            
            if race_distance:
                race_category = self.get_distance_category(race_distance, race_surface)
                if race_category == target_category and race_surface == target_surface:
                    same_category_count += 1
                    same_category_avg += race.get('result', 10)
        
        if same_category_count > 0:
            avg_result = same_category_avg / same_category_count
            if avg_result <= 3:
                score += 25
            elif avg_result <= 5:
                score += 15
        
        return min(score, 100)
    
    def analyze_other_factors(self, horse_data: Dict, race_info: Dict) -> float:
        """その他の要素をまとめて分析"""
        score = 60.0
        
        # 騎手ボーナス
        jockey = horse_data.get('jockey', '')
        if any(top_j in jockey for top_j in self.top_jockeys):
            score += 15
        
        # 同コース実績
        target_track = race_info.get('track', '')
        recent_results = horse_data.get('recent_results', [])
        same_track_results = [r for r in recent_results if target_track in r.get('place', '')]
        
        if same_track_results:
            avg_result = sum(r.get('result', 10) for r in same_track_results) / len(same_track_results)
            if avg_result <= 3:
                score += 10
        
        return min(score, 100)
    
    def predict_race_with_synthetic_odds(self, race_data: Dict) -> Dict:
        """合成オッズ分析付きレース予想"""
        horses = race_data.get('horses', [])
        predictions = []
        
        for horse in horses:
            # 基本分析
            recent_score = self.analyze_recent_form(horse.get('recent_results', []))
            distance_score = self.analyze_distance_fit(horse, race_data)
            other_score = self.analyze_other_factors(horse, race_data)
            
            # 総合スコア
            total_score = (
                recent_score * 0.5 +
                distance_score * 0.3 +
                other_score * 0.2
            )
            
            # 勝率推定
            win_probability = min(total_score / 100 * 0.35, 0.8)
            
            prediction = {
                'horse_number': horse.get('horse_number', 0),
                'horse_name': horse.get('horse_name', ''),
                'jockey': horse.get('jockey', ''),
                'odds': horse.get('odds', 0.0),
                'popularity': horse.get('popularity', 0),
                'total_score': round(total_score, 1),
                'win_probability': round(win_probability, 3),
                'expected_value': self.calculate_expected_value(win_probability, horse.get('odds', 0))
            }
            predictions.append(prediction)
        
        # スコア順でソート
        predictions.sort(key=lambda x: x['total_score'], reverse=True)
        
        # 馬券購入推奨パターンを計算
        betting_patterns = self.find_recommended_betting_patterns(predictions)
        
        return {
            'race_info': race_data,
            'predictions': predictions,
            'betting_patterns': betting_patterns
        }


def create_sample_race_with_odds():
    """サンプルレース（オッズ付き）"""
    return {
        'race_name': 'サンプル特別',
        'track': '東京',
        'surface': '芝',
        'distance': 1600,
        'condition': '良',
        'horses': [
            {
                'horse_number': 1,
                'horse_name': '本命馬',
                'jockey': 'C.ルメール',
                'odds': 2.8,
                'popularity': 1,
                'recent_results': [
                    {'place': '東京', 'distance': 1600, 'surface': '芝', 'result': 2, 'popularity': 1},
                    {'place': '中山', 'distance': 1800, 'surface': '芝', 'result': 1, 'popularity': 2}
                ]
            },
            {
                'horse_number': 2, 
                'horse_name': '対抗馬',
                'jockey': '武豊',
                'odds': 5.2,
                'popularity': 3,
                'recent_results': [
                    {'place': '東京', 'distance': 1600, 'surface': '芝', 'result': 3, 'popularity': 4},
                    {'place': '東京', 'distance': 1400, 'surface': '芝', 'result': 1, 'popularity': 7}
                ]
            },
            {
                'horse_number': 3,
                'horse_name': '穴馬候補', 
                'jockey': '戸崎圭太',
                'odds': 12.5,
                'popularity': 6,
                'recent_results': [
                    {'place': '中山', 'distance': 1600, 'surface': '芝', 'result': 4, 'popularity': 8},
                    {'place': '東京', 'distance': 1800, 'surface': '芝', 'result': 2, 'popularity': 9}
                ]
            },
            {
                'horse_number': 4,
                'horse_name': '大穴馬',
                'jockey': 'M.デムーロ',
                'odds': 25.0,
                'popularity': 10,
                'recent_results': [
                    {'place': '東京', 'distance': 1600, 'surface': '芝', 'result': 6, 'popularity': 12},
                    {'place': '中山', 'distance': 1400, 'surface': '芝', 'result': 3, 'popularity': 15}
                ]
            }
        ]
    }


def main():
    """メイン処理"""
    print("=== 合成オッズ機能付き競馬予想システム ===")
    print("条件: 合成オッズ4倍以上、最低100円購入")
    print()
    
    predictor = EnhancedOddsPredictor()
    race_data = create_sample_race_with_odds()
    
    result = predictor.predict_race_with_synthetic_odds(race_data)
    
    print(f"【{race_data['race_name']}】予想結果")
    print(f"コース: {race_data['track']} {race_data['surface']}{race_data['distance']}m")
    print("-" * 70)
    
    # 基本予想
    print("◆ 基本予想 ◆")
    for pred in result['predictions']:
        print(f"{pred['horse_name']} (人気{pred['popularity']}番, オッズ{pred['odds']}倍)")
        print(f"  予想勝率: {pred['win_probability']:.1%}, 期待値: {pred['expected_value']:+.2f}")
        print()
    
    # 推奨馬券購入パターン
    print("◆ 推奨馬券購入パターン ◆")
    if result['betting_patterns']:
        for i, pattern in enumerate(result['betting_patterns'], 1):
            print(f"【パターン{i}】合成オッズ: {pattern['synthetic_odds']}倍")
            print(f"総投資額: {pattern['total_investment']}円, 期待収益: {pattern['expected_return']:.0f}円")
            print(f"予想ROI: {pattern['roi']:+.1f}%")
            
            for horse in pattern['horses']:
                print(f"  {horse['horse_name']}: {horse['bet_amount']}円 (オッズ{horse['odds']}倍)")
            print()
    else:
        print("条件を満たす推奨パターンがありませんでした。")
    
    return result


if __name__ == "__main__":
    result = main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
古いシステムから移植した強化機能
- 人気による補正機能（穴馬発見）
- 合成オッズ計算機能
- 最適購入パターン計算（予算対応版・馬券ルール準拠）
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
        synthetic_odds = 1 / inverse_sum if inverse_sum > 0 else 0.0
        
        # 下限チェック：2.0倍未満は除外
        return synthetic_odds if synthetic_odds >= 2.0 else 0.0
    
    def round_to_100yen(self, amount: int) -> int:
        """100円単位に調整（馬券の最低購入単位）"""
        if amount < 100:
            return 100
        return ((amount + 50) // 100) * 100  # 四捨五入で100円単位
    
    def find_optimal_betting_patterns(self, predictions: List[Dict], 
                                     budget: int = 1000) -> List[Dict]:
        """最適購入パターン計算（馬券ルール準拠版）"""
        patterns = []
        
        # 期待値プラスの馬だけを対象
        positive_ev_horses = [p for p in predictions if p.get('expected_value', 0) > 0]
        
        if not positive_ev_horses:
            return patterns
        
        # 予算に応じた適切な配分計算（100円単位）
        if budget <= 600:
            # 小額の場合（300円・600円）
            single_raw = max(100, budget // 2)
            place_raw = max(100, budget // 3)
            combo_raw = max(100, budget // 2)
        elif budget <= 1500:
            # 中額の場合（1000円程度）
            single_raw = budget // 2
            place_raw = budget // 3
            combo_raw = budget // 2
        else:
            # 高額の場合
            single_raw = min(budget * 0.4, budget // 2)
            place_raw = min(budget * 0.3, budget // 3)
            combo_raw = min(budget * 0.5, budget // 2)
        
        # 100円単位に調整
        single_amount = self.round_to_100yen(single_raw)
        place_amount = self.round_to_100yen(place_raw)
        combo_amount = self.round_to_100yen(combo_raw)
        
        # 予算オーバーチェック
        single_amount = min(single_amount, budget)
        place_amount = min(place_amount, budget)
        combo_amount = min(combo_amount, budget)
        
        # 単勝パターン
        for horse in positive_ev_horses[:3]:  # 上位3頭
            if horse['odds'] >= 2.0:  # オッズ下限チェック
                roi = horse['expected_value']
                patterns.append({
                    'type': '単勝',
                    'horses': [horse['horse_name']],
                    'odds': horse['odds'],
                    'expected_roi': roi,
                    'recommended_amount': single_amount
                })
        
        # 複勝パターン
        for horse in positive_ev_horses[:2]:
            place_odds = horse['odds'] * 0.2  # 複勝は単勝の約20%
            if place_odds >= 2.0:  # オッズ下限チェック
                place_prob = horse.get('actual_stats', {}).get('place_rate', 0.3)
                roi = place_prob * place_odds - 1
                if roi > 0:
                    patterns.append({
                        'type': '複勝',
                        'horses': [horse['horse_name']],
                        'odds': place_odds,
                        'expected_roi': roi,
                        'recommended_amount': place_amount
                    })
        
        # 馬連パターン（上位2頭の組み合わせ）
        if len(positive_ev_horses) >= 2:
            horse1, horse2 = positive_ev_horses[0], positive_ev_horses[1]
            combined_odds = self.calculate_synthetic_odds([horse1['odds'], horse2['odds']])
            
            # 合成オッズが有効（2.0以上）かチェック
            if combined_odds >= 3.0:  # 馬連は3.0以上を推奨
                combined_prob = horse1['win_probability'] * horse2['win_probability'] * 2  # 順序考慮
                roi = combined_prob * combined_odds - 1
                
                if roi > 0:
                    patterns.append({
                        'type': '馬連',
                        'horses': [horse1['horse_name'], horse2['horse_name']],
                        'odds': combined_odds,
                        'expected_roi': roi,
                        'recommended_amount': combo_amount
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


def get_user_budget():
    """ユーザー予算取得（安全網付き）"""
    print("=== 競馬予想システム ===")
    
    try:
        user_input = input("今日の予算を入力してください（円、Enterで自動計算）: ").strip()
        
        # 空入力の場合は自動で両方計算
        if not user_input:
            print("自動で300円・600円の2パターンで計算します。")
            return [300, 600]
        
        budget = int(user_input)
        if budget < 100:
            print("予算が少ないので、300円・600円で計算します。")
            return [300, 600]
        
        print(f"予算{budget:,}円で分析を開始します。")
        return [budget]
        
    except:
        print("自動で300円・600円の2パターンで計算します。")
        return [300, 600]


def print_betting_guide():
    """馬券購入ガイド（簡潔版）"""
    print("\n📋 馬券購入ガイド（簡潔版）")
    print("・最低購入金額：100円（100円単位のみ）")
    print("・単勝：1着を当てる　複勝：3着以内を当てる")
    print("・馬連：1-2着の組み合わせ（順序不問）")
    print("・馬単：1-2着を順序通り　ワイド：3着以内の2頭")
    print("・BOX買い：選択馬の全組み合わせ")
    print("・流し買い：軸馬と相手馬の組み合わせ")


def test_enhanced_features():
    """強化機能のテスト（馬券ルール準拠版）"""
    print("=== 強化機能テスト（馬券ルール準拠版） ===")
    
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
    
    # 100円単位調整テスト
    test_amounts = [150, 250, 333, 166]
    print(f"\n100円単位調整テスト:")
    for amount in test_amounts:
        adjusted = features.round_to_100yen(amount)
        print(f"  {amount}円 → {adjusted}円")
    
    # 複数予算でのテスト
    test_budgets = [300, 600, 1000]
    for budget in test_budgets:
        print(f"\n=== 予算{budget}円での最適購入パターン ===")
        patterns = features.find_optimal_betting_patterns(sample_predictions, budget)
        print("※各券種から1つを選んで購入（100円単位）")
        for i, pattern in enumerate(patterns, 1):
            horses_str = "×".join(pattern['horses'])
            print(f"{i}. {pattern['type']}: {horses_str} ({pattern['recommended_amount']}円, ROI: {pattern['expected_roi']:+.3f})")
    
    print("\n✅ 強化機能テスト完了")
    print_betting_guide()


if __name__ == "__main__":
    test_enhanced_features()

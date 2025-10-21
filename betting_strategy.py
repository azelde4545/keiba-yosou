# -*- coding: utf-8 -*-
"""
競馬予想システム - 賭け戦略・購入プランモジュール
単勝3点買い専用（シンプル設計）
"""

from typing import Dict, List, Any


class BettingStrategy:
    """賭け戦略・購入プランクラス"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.default_budget = 400
    
    def estimate_combined_odds(self, horse1: Dict, horse2: Dict, bet_type: str = '馬連') -> float:
        """複式馬券のオッズ概算（ユーザー相談時のアドバイス用）
        
        Args:
            horse1: 1頭目の馬情報（単勝オッズ含む）
            horse2: 2頭目の馬情報（単勝オッズ含む）
            bet_type: 馬券の種類（馬連/ワイド/馬単/3連複）
            
        Returns:
            概算オッズ（実際のオッズと異なる場合があります）
        """
        odds1 = horse1.get('odds', 10.0)
        odds2 = horse2.get('odds', 10.0)
        
        if bet_type == '馬連':
            return round((odds1 * odds2) / 2.5, 1)
        elif bet_type == 'ワイド':
            return round((odds1 * odds2) / 5.5, 1)
        elif bet_type == '馬単':
            return round((odds1 * odds2) / 2.0, 1)
        else:
            return round((odds1 * odds2) / 2.5, 1)
    
    def _adjust_amounts_to_budget(self, plan: List[Dict[str, Any]], budget: int) -> List[Dict[str, Any]]:
        """購入プランの金額を予算に合わせて調整（100%使い切り）"""
        if not plan:
            return plan
        
        current_total = sum(p['amount'] for p in plan)
        
        if current_total == 0:
            amount_per_bet = budget // len(plan)
            remainder = budget % len(plan)
            
            for i, p in enumerate(plan):
                p['amount'] = amount_per_bet + (1 if i < remainder else 0)
            return plan
        
        # 比例配分で調整
        ratio = budget / current_total
        adjusted_plan = []
        allocated_total = 0
        
        for i, p in enumerate(plan):
            if i < len(plan) - 1:
                adjusted_amount = int(p['amount'] * ratio / 100) * 100
                adjusted_amount = max(100, adjusted_amount)
            else:
                adjusted_amount = budget - allocated_total
                adjusted_amount = max(100, adjusted_amount)
            
            adjusted_plan.append({
                'type': p['type'],
                'horses': p['horses'],
                'amount': adjusted_amount
            })
            allocated_total += adjusted_amount
        
        return adjusted_plan

    def generate_betting_plan(self, eval_results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """購入戦略生成 - 実力評価と期待値評価を使用"""
        ability_results = eval_results.get('ability_results', [])
        value_results = eval_results.get('value_results', [])
        
        if len(ability_results) < 3:
            return {"error": "評価データが3頭未満です。"}
        
        budget = self.config.get('betting_strategy', {}).get('total_budget', self.default_budget)
        
        # 本命・対抗：実力評価の上位3頭
        honmei_horse = ability_results[0].copy()
        honmei_horse['ability_score'] = honmei_horse.get('final_score', 0)
        
        taikou_horses = []
        for h in ability_results[1:3]:
            horse_copy = h.copy()
            horse_copy['ability_score'] = horse_copy.get('final_score', 0)
            taikou_horses.append(horse_copy)
        
        # 穴馬：期待値評価から、本命・対抗以外を2頭選ぶ
        honmei_taikou_numbers = {honmei_horse['number'], taikou_horses[0]['number'], taikou_horses[1]['number']}
        anaume_candidates = []
        for h in value_results:
            if h['number'] not in honmei_taikou_numbers:
                horse_copy = h.copy()
                horse_copy['value_score'] = horse_copy.get('final_score', 0)
                anaume_candidates.append(horse_copy)
        
        anaume_horses = anaume_candidates[:2] if len(anaume_candidates) >= 2 else anaume_candidates
        
        # 予算に応じた購入プラン選択
        if budget < 100:
            return {"error": f"予算が不足しています（最低100円必要）。現在の予算: {budget}円"}
        elif budget < 300:
            # 本命のみ
            purchase_plan = [
                {'type': '単勝', 'horses': [honmei_horse], 'amount': budget}
            ]
            strategy = "単勝1点買い（本命）"
        elif budget < 500:
            # 本命+対抗1頭+穴馬1頭
            purchase_plan = [
                {'type': '単勝', 'horses': [honmei_horse], 'amount': int(budget * 0.5)},
                {'type': '単勝', 'horses': [taikou_horses[0]], 'amount': int(budget * 0.3)},
                {'type': '単勝', 'horses': [anaume_horses[0] if anaume_horses else taikou_horses[1]], 'amount': int(budget * 0.2)}
            ]
            strategy = "単勝3点買い"
        else:
            # 本命+対抗2頭+穴馬2頭
            purchase_plan = [
                {'type': '単勝', 'horses': [honmei_horse], 'amount': int(budget * 0.35)},
                {'type': '単勝', 'horses': [taikou_horses[0]], 'amount': int(budget * 0.25)},
                {'type': '単勝', 'horses': [taikou_horses[1]], 'amount': int(budget * 0.15)},
            ]
            # 穴馬を追加
            if len(anaume_horses) >= 2:
                purchase_plan.extend([
                    {'type': '単勝', 'horses': [anaume_horses[0]], 'amount': int(budget * 0.15)},
                    {'type': '単勝', 'horses': [anaume_horses[1]], 'amount': int(budget * 0.10)}
                ])
            elif len(anaume_horses) == 1:
                purchase_plan.append({'type': '単勝', 'horses': [anaume_horses[0]], 'amount': int(budget * 0.25)})
            
            strategy = f"単勝{len(purchase_plan)}点買い"
        
        # 予算100%使い切るように調整
        purchase_plan = self._adjust_amounts_to_budget(purchase_plan, budget)
        
        total_bet = sum(p['amount'] for p in purchase_plan)
        
        # 購入ガイド生成
        purchase_guide = self._generate_purchase_guide_v2(
            honmei_horse, taikou_horses, anaume_horses, purchase_plan
        )
        
        return {
            "strategy": strategy,
            "purchase_plan": purchase_plan,
            "total_bet": total_bet,
            "purchase_guide": purchase_guide,
            "horses": {
                "honmei": honmei_horse,
                "taikou": taikou_horses,
                "anaume": anaume_horses
            }
        }
    
    def _generate_purchase_guide(self, honmei: Dict, taikou: Dict, anaume: Dict,
                                purchase_plan: List[Dict]) -> str:
        """購入ガイド生成"""
        guide = f"""
【購入ガイド - 単勝3点買い】
={'='*50}

推奨馬（評価スコア順）
本命: {honmei['number']}番 {honmei['name']}
   オッズ: {honmei['odds']}倍 | 評価: {honmei.get('final_score', 0)}点
   
対抗: {taikou['number']}番 {taikou['name']}
   オッズ: {taikou['odds']}倍 | 評価: {taikou.get('final_score', 0)}点
   
穴馬: {anaume['number']}番 {anaume['name']}
   オッズ: {anaume['odds']}倍 | 評価: {anaume.get('final_score', 0)}点

購入プラン（単勝のみ）
"""
        
        for i, plan in enumerate(purchase_plan, 1):
            horse = plan['horses'][0]
            guide += f"{i}. 単勝 {horse['number']}番 {horse['name']}: {plan['amount']}円\n"
        
        total_amount = sum(p['amount'] for p in purchase_plan)
        guide += f"""
投資戦略
総投資額: {total_amount}円
購入馬券: 単勝3点

他の馬券を検討する場合
馬連・ワイド等の購入を検討される場合は、お気軽にご相談ください。
概算オッズの計算や、期待値の分析などをサポートいたします。

注意事項
・投資は自己責任でお願いします
・オッズは変動する可能性があります
・予想は過去データに基づく分析です
"""
        
        return guide

    def _generate_purchase_guide_v2(self, honmei: Dict, taikou_list: List[Dict], 
                                   anaume_list: List[Dict], purchase_plan: List[Dict]) -> str:
        """購入ガイド生成 v2 - 複数の対抗・穴馬に対応"""
        # 購入プラン種別を判定
        plan_count = len(purchase_plan)
        if plan_count == 1:
            plan_type = "単勝1点買い"
        elif plan_count <= 3:
            plan_type = "単勝3点買い"
        else:
            plan_type = f"単勝{plan_count}点買い"
        
        guide = f"""
【購入ガイド - {plan_type}】
{'='*50}

◆ 推奨馬（役割別）

【本命】 {honmei['number']}番 {honmei['name']}
   オッズ: {honmei['odds']}倍 | 実力評価: {honmei.get('ability_score', 0):.2f}点
   理由: 実力評価で最高スコア
"""
        
        # 対抗馬を追加
        if taikou_list:
            for i, taikou in enumerate(taikou_list, 1):
                guide += f"""
【対抗{i}】 {taikou['number']}番 {taikou['name']}
   オッズ: {taikou['odds']}倍 | 実力評価: {taikou.get('ability_score', 0):.2f}点
"""
        
        # 穴馬を追加
        if anaume_list:
            for i, anaume in enumerate(anaume_list, 1):
                guide += f"""
【穴馬{i}】 {anaume['number']}番 {anaume['name']}
   オッズ: {anaume['odds']}倍 | 期待値評価: {anaume.get('value_score', 0):.2f}点
   理由: 実力に対してオッズが割安
"""
        
        # 購入プラン詳細
        guide += f"""
◆ 購入プラン（単勝のみ）
"""
        
        for i, plan in enumerate(purchase_plan, 1):
            horse = plan['horses'][0]
            guide += f"{i}. 単勝 {horse['number']}番 {horse['name']}: {plan['amount']}円\n"
        
        total_amount = sum(p['amount'] for p in purchase_plan)
        guide += f"""
◆ 投資戦略
総投資額: {total_amount}円
購入馬券: {plan_type}

◆ 他の馬券を検討する場合
馬連・ワイド等の購入を検討される場合は、お気軽にご相談ください。
概算オッズの計算や、期待値の分析などをサポートいたします。

◆ 注意事項
・投資は自己責任でお願いします
・オッズは変動する可能性があります
・予想は過去データに基づく分析です
"""
        
        return guide

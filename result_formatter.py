# -*- coding: utf-8 -*-
"""
競馬予想結果フォーマッター
見やすい予想結果を表示するためのモジュール
"""

from typing import Dict, List, Any


class ResultFormatter:
    """予想結果を見やすく表示するフォーマッター"""
    
    def __init__(self):
        self.separator = "=" * 80
        self.sub_separator = "-" * 80
    
    def format_prediction_summary(self, race_data: Dict[str, Any], 
                                  ability_results: List[Dict[str, Any]], 
                                  value_results: List[Dict[str, Any]]) -> str:
        """予想結果の総合サマリーを生成"""
        output = []
        
        # ヘッダー
        output.append("\n" + self.separator)
        output.append("🏇 競馬予想結果サマリー")
        output.append(self.separator)
        
        # レース情報
        race_info = race_data.get('race_info', {})
        output.append(f"\n📋 レース情報")
        output.append(f"  レース名: {race_info.get('name', '不明')}")
        output.append(f"  開催日: {race_info.get('date', '不明')}")
        output.append(f"  競馬場: {race_info.get('track', '不明')}")
        output.append(f"  距離: {race_data.get('distance', '不明')}m")
        output.append(f"  馬場: {race_info.get('track_condition', '不明')}")
        
        # 推奨馬券
        output.append(f"\n{self.sub_separator}")
        output.append("🎯 推奨馬券")
        output.append(self.sub_separator)
        
        # 本命・対抗・穴馬を抽出
        if ability_results:
            honmei = ability_results[0]
            taikou = ability_results[1] if len(ability_results) > 1 else None
            output.append(f"\n◎ 本命: {honmei['number']}番 {honmei['name']} (オッズ: {honmei['odds']}倍)")
            output.append(f"   総合評価: {honmei['final_score']}点")
            if taikou:
                output.append(f"\n○ 対抗: {taikou['number']}番 {taikou['name']} (オッズ: {taikou['odds']}倍)")
                output.append(f"   総合評価: {taikou['final_score']}点")
        
        if value_results:
            # 穴馬候補（実力評価の上位3頭に含まれていない馬）
            top3_names = {h['name'] for h in ability_results[:3]}
            anauma_candidates = [h for h in value_results if h['name'] not in top3_names][:2]
            
            if anauma_candidates:
                output.append(f"\n▲ 穴馬候補:")
                for i, horse in enumerate(anauma_candidates, 1):
                    output.append(f"   {i}. {horse['number']}番 {horse['name']} (オッズ: {horse['odds']}倍)")
                    output.append(f"      期待値評価: {horse['final_score']}点")
        
        # 推奨買い目
        output.append(f"\n💰 推奨買い目:")
        if ability_results and len(ability_results) >= 3:
            top3 = ability_results[:3]
            output.append(f"   3連複: {top3[0]['number']}-{top3[1]['number']}-{top3[2]['number']}番")
            output.append(f"   3連単: {top3[0]['number']}→{top3[1]['number']}→{top3[2]['number']}番")
        
        if anauma_candidates and ability_results:
            output.append(f"\n   【穴狙い】")
            honmei_num = ability_results[0]['number']
            for anauma in anauma_candidates[:1]:
                output.append(f"   3連複: {honmei_num}-{anauma['number']}-流し")
        
        return "\n".join(output)
    
    def format_detailed_ranking(self, ability_results: List[Dict[str, Any]], 
                               value_results: List[Dict[str, Any]], 
                               top_n: int = 10) -> str:
        """詳細ランキング表を生成"""
        output = []
        
        output.append(f"\n{self.separator}")
        output.append("📊 詳細評価ランキング")
        output.append(self.separator)
        
        # 実力評価ランキング
        output.append(f"\n【実力評価順位】（本命・対抗向け）")
        output.append(self.sub_separator)
        output.append(f"{'順位':<4} {'馬番':<4} {'馬名':<20} {'総合':<6} {'過去':<6} {'コース':<6} {'馬場':<6} {'馬体重':<6} {'間隔':<6} {'オッズ':<8}")
        output.append(self.sub_separator)
        
        for i, horse in enumerate(ability_results[:top_n], 1):
            rank_mark = self._get_rank_mark(i)
            output.append(
                f"{rank_mark:<4} "
                f"{horse['number']:<4} "
                f"{horse['name']:<20} "
                f"{horse['final_score']:<6.1f} "
                f"{horse['performance_score']:<6.1f} "
                f"{horse['course_fit_score']:<6.1f} "
                f"{horse['track_condition_score']:<6.1f} "
                f"{horse.get('weight_change_score', 50.0):<6.1f} "
                f"{horse['interval_score']:<6.1f} "
                f"{horse['odds']:<8.1f}倍"
            )
        
        # 期待値評価ランキング
        output.append(f"\n【期待値評価順位】（穴馬向け）")
        output.append(self.sub_separator)
        output.append(f"{'順位':<4} {'馬番':<4} {'馬名':<20} {'総合':<6} {'過去':<6} {'コース':<6} {'オッズ価値':<10} {'穴馬':<6} {'オッズ':<8}")
        output.append(self.sub_separator)
        
        for i, horse in enumerate(value_results[:top_n], 1):
            rank_mark = self._get_rank_mark(i)
            output.append(
                f"{rank_mark:<4} "
                f"{horse['number']:<4} "
                f"{horse['name']:<20} "
                f"{horse['final_score']:<6.1f} "
                f"{horse['performance_score']:<6.1f} "
                f"{horse['course_fit_score']:<6.1f} "
                f"{horse['odds_value_score']:<10.1f} "
                f"{horse['dark_horse_score']:<6.1f} "
                f"{horse['odds']:<8.1f}倍"
            )
        
        return "\n".join(output)
    
    def format_weight_analysis(self, horses: List[Dict[str, Any]]) -> str:
        """馬体重分析を生成"""
        output = []
        
        output.append(f"\n{self.separator}")
        output.append("⚖️ 馬体重分析")
        output.append(self.separator)
        
        # 馬体重変動が大きい馬を抽出
        weight_changes = []
        for horse in horses:
            weight = horse.get('weight', '?')
            weight_change = horse.get('weight_change', 0)
            
            if isinstance(weight_change, str):
                try:
                    weight_change = int(weight_change.replace('+', '').replace('kg', '').strip())
                except:
                    weight_change = 0
            
            if weight_change != 0:
                weight_changes.append({
                    'name': horse['name'],
                    'number': horse['number'],
                    'weight': weight,
                    'change': weight_change,
                    'score': horse.get('weight_change_score', 50.0)
                })
        
        # 増減順にソート
        weight_changes.sort(key=lambda x: x['change'], reverse=True)
        
        output.append(f"\n{'馬番':<4} {'馬名':<20} {'馬体重':<10} {'増減':<8} {'評価':<6} {'コメント':<30}")
        output.append(self.sub_separator)
        
        for horse in weight_changes:
            change = horse['change']
            comment = self._get_weight_comment(change)
            change_str = f"{change:+d}kg" if change != 0 else "±0kg"
            
            output.append(
                f"{horse['number']:<4} "
                f"{horse['name']:<20} "
                f"{horse['weight']:<10} "
                f"{change_str:<8} "
                f"{horse['score']:<6.1f} "
                f"{comment:<30}"
            )
        
        return "\n".join(output)
    
    def _get_rank_mark(self, rank: int) -> str:
        """順位マークを取得"""
        if rank == 1:
            return "◎"
        elif rank == 2:
            return "○"
        elif rank == 3:
            return "▲"
        elif rank <= 5:
            return "△"
        else:
            return f"{rank}位"
    
    def _get_weight_comment(self, change: int) -> str:
        """馬体重変動のコメントを生成"""
        if -3 <= change <= 3:
            return "✅ 理想的な仕上がり"
        elif -8 <= change < -3:
            return "✅ 良好（絞り込み）"
        elif 3 < change <= 8:
            return "⚠️ やや増（まずまず）"
        elif change < -15:
            return "❌ 大幅減（仕上げすぎ？）"
        elif change > 15:
            return "❌ 大幅増（太め残り？）"
        elif -15 <= change < -8:
            return "⚠️ かなり減（やや心配）"
        elif 8 < change <= 15:
            return "⚠️ かなり増（調整不足？）"
        else:
            return ""
    
    def format_complete_report(self, race_data: Dict[str, Any], 
                              ability_results: List[Dict[str, Any]], 
                              value_results: List[Dict[str, Any]]) -> str:
        """完全レポートを生成"""
        output = []
        
        # サマリー
        output.append(self.format_prediction_summary(race_data, ability_results, value_results))
        
        # 詳細ランキング
        output.append(self.format_detailed_ranking(ability_results, value_results))
        
        # 馬体重分析
        output.append(self.format_weight_analysis(ability_results))
        
        # フッター
        output.append(f"\n{self.separator}")
        output.append("📌 評価基準:")
        output.append("  能力系70%: 過去成績25% + コース適性25% + 馬場10% + 馬体重3% + 前走間隔7%")
        output.append("  投資系30%: オッズ価値18% + 穴馬要素12%")
        output.append(self.separator + "\n")
        
        return "\n".join(output)


def main():
    """テスト用メイン関数"""
    # サンプルデータでテスト
    formatter = ResultFormatter()
    
    sample_race = {
        'race_info': {
            'name': 'テストステークス',
            'date': '2025-10-18',
            'track': '東京',
            'track_condition': '良'
        },
        'distance': 1600
    }
    
    sample_horses = [
        {
            'name': 'サンプルホース1',
            'number': '1',
            'odds': 3.5,
            'weight': '480kg',
            'weight_change': '-2',
            'final_score': 78.5,
            'performance_score': 82.0,
            'course_fit_score': 75.0,
            'track_condition_score': 70.0,
            'weight_change_score': 70.0,
            'interval_score': 15.0,
            'odds_value_score': 65.0,
            'dark_horse_score': 40.0
        }
    ]
    
    print(formatter.format_complete_report(sample_race, sample_horses, sample_horses))


if __name__ == "__main__":
    main()

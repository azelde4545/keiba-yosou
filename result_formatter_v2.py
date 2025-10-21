# -*- coding: utf-8 -*-
"""
競馬予想結果フォーマッター v2
見やすく、分かりやすい予想結果を表示するためのモジュール
"""

from typing import Dict, List, Any


class ResultFormatterV2:
    """予想結果を見やすく表示する改善版フォーマッター"""
    
    def __init__(self):
        self.separator = "=" * 100
        self.sub_separator = "-" * 100
        self.box_separator = "┌" + "─" * 98 + "┐"
        self.box_end = "└" + "─" * 98 + "┘"
    
    def format_complete_report(self, race_data: Dict[str, Any], 
                              ability_results: List[Dict[str, Any]], 
                              value_results: List[Dict[str, Any]]) -> str:
        """完全レポートを生成"""
        output = []
        
        # ヘッダー
        output.append(self._format_header(race_data))
        
        # メイン推奨（最重要セクション）
        output.append(self._format_main_recommendations(ability_results, value_results))
        
        # 詳細評価表
        output.append(self._format_detailed_table(ability_results))
        
        # 期待値ランキング
        output.append(self._format_value_ranking(value_results))
        
        # 馬体重分析
        output.append(self._format_weight_analysis(ability_results))
        
        # 買い目提案
        output.append(self._format_betting_suggestions(ability_results, value_results))
        
        # フッター
        output.append(self._format_footer())
        
        return "\n".join(output)
    
    def _format_header(self, race_data: Dict[str, Any]) -> str:
        """レース情報ヘッダー"""
        output = []
        race_info = race_data.get('race_info', {})
        
        output.append("\n" + self.separator)
        output.append("🏇 競馬予想システム - 予想結果レポート")
        output.append(self.separator)
        output.append("")
        output.append(f"📋 レース名: {race_info.get('name', '不明')}")
        output.append(f"📅 開催日: {race_info.get('date', '不明')}")
        output.append(f"🏟️  競馬場: {race_info.get('track', '不明')}  "
                     f"📏 距離: {race_data.get('distance', '不明')}m  "
                     f"🌱 馬場: {race_info.get('track_condition', '不明')}")
        output.append("")
        
        return "\n".join(output)
    
    def _format_main_recommendations(self, ability_results: List[Dict[str, Any]], 
                                    value_results: List[Dict[str, Any]]) -> str:
        """メイン推奨セクション（最も目立つ部分）"""
        output = []
        
        output.append(self.box_separator)
        output.append("│" + " " * 35 + "🎯 本日の推奨馬" + " " * 48 + "│")
        output.append("├" + "─" * 98 + "┤")
        
        if ability_results:
            # 本命
            honmei = ability_results[0]
            stars_honmei = self._get_stars(honmei['final_score'])
            output.append(f"│  ◎ 本命: {honmei['number']:>2}番 {honmei['name']:<20}  "
                         f"総合評価: {honmei['final_score']:>5.1f}点 {stars_honmei:<15}  "
                         f"オッズ: {honmei['odds']:>5.1f}倍" + " " * 10 + "│")
            
            # 対抗
            if len(ability_results) > 1:
                taikou = ability_results[1]
                stars_taikou = self._get_stars(taikou['final_score'])
                output.append(f"│  ○ 対抗: {taikou['number']:>2}番 {taikou['name']:<20}  "
                             f"総合評価: {taikou['final_score']:>5.1f}点 {stars_taikou:<15}  "
                             f"オッズ: {taikou['odds']:>5.1f}倍" + " " * 10 + "│")
            
            # 単穴
            if len(ability_results) > 2:
                tanana = ability_results[2]
                stars_tanana = self._get_stars(tanana['final_score'])
                output.append(f"│  ▲ 単穴: {tanana['number']:>2}番 {tanana['name']:<20}  "
                             f"総合評価: {tanana['final_score']:>5.1f}点 {stars_tanana:<15}  "
                             f"オッズ: {tanana['odds']:>5.1f}倍" + " " * 10 + "│")
        
        output.append("├" + "─" * 98 + "┤")
        
        # 穴馬候補
        if value_results and ability_results:
            top3_names = {h['name'] for h in ability_results[:3]}
            anauma_candidates = [h for h in value_results if h['name'] not in top3_names][:2]
            
            if anauma_candidates:
                output.append("│  💎 穴馬候補（高配当狙い）:" + " " * 71 + "│")
                for i, horse in enumerate(anauma_candidates, 1):
                    stars = self._get_stars(horse['final_score'])
                    output.append(f"│     {i}. {horse['number']:>2}番 {horse['name']:<20}  "
                                 f"期待値評価: {horse['final_score']:>5.1f}点 {stars:<15}  "
                                 f"オッズ: {horse['odds']:>5.1f}倍" + " " * 8 + "│")
        
        output.append(self.box_end)
        output.append("")
        
        return "\n".join(output)
    
    def _format_detailed_table(self, ability_results: List[Dict[str, Any]]) -> str:
        """詳細評価表（実力評価順）"""
        output = []
        
        output.append(self.separator)
        output.append("📊 詳細評価ランキング（実力評価順）")
        output.append(self.separator)
        output.append("")
        output.append(f"{'順位':<6} {'馬番':<6} {'馬名':<22} {'総合':<8} "
                     f"{'過去':<8} {'コース':<8} {'馬場':<8} {'馬体重':<8} {'間隔':<8} {'オッズ':<10}")
        output.append(self.sub_separator)
        
        for i, horse in enumerate(ability_results[:10], 1):
            rank_mark = self._get_rank_mark(i)
            grade = self._get_grade(horse['final_score'])
            
            output.append(
                f"{rank_mark:<6} "
                f"{horse['number']:<6} "
                f"{horse['name']:<22} "
                f"{horse['final_score']:<8.1f} "
                f"{horse['performance_score']:<8.1f} "
                f"{horse['course_fit_score']:<8.1f} "
                f"{horse['track_condition_score']:<8.1f} "
                f"{horse.get('weight_change_score', 50.0):<8.1f} "
                f"{horse.get('interval_score', 0.0):<8.1f} "
                f"{horse['odds']:<10.1f}倍  {grade}"
            )
        
        output.append("")
        return "\n".join(output)
    
    def _format_value_ranking(self, value_results: List[Dict[str, Any]]) -> str:
        """期待値ランキング（穴馬向け）"""
        output = []
        
        output.append(self.separator)
        output.append("💰 期待値評価ランキング（穴馬向け）")
        output.append(self.separator)
        output.append("")
        output.append(f"{'順位':<6} {'馬番':<6} {'馬名':<22} {'総合':<8} "
                     f"{'過去':<8} {'コース':<8} {'オッズ価値':<12} {'穴馬':<8} {'オッズ':<10}")
        output.append(self.sub_separator)
        
        for i, horse in enumerate(value_results[:10], 1):
            rank_mark = self._get_rank_mark(i)
            grade = self._get_grade(horse['final_score'])
            
            output.append(
                f"{rank_mark:<6} "
                f"{horse['number']:<6} "
                f"{horse['name']:<22} "
                f"{horse['final_score']:<8.1f} "
                f"{horse['performance_score']:<8.1f} "
                f"{horse['course_fit_score']:<8.1f} "
                f"{horse['odds_value_score']:<12.1f} "
                f"{horse['dark_horse_score']:<8.1f} "
                f"{horse['odds']:<10.1f}倍  {grade}"
            )
        
        output.append("")
        return "\n".join(output)
    
    def _format_weight_analysis(self, ability_results: List[Dict[str, Any]]) -> str:
        """馬体重変動分析"""
        output = []
        
        output.append(self.separator)
        output.append("⚖️  馬体重変動分析")
        output.append(self.separator)
        output.append("")
        
        # 馬体重変動が大きい馬をピックアップ
        weight_notable = []
        for horse in ability_results[:10]:
            weight_change = horse.get('weight_change', 0)
            if abs(weight_change) >= 10:  # ±10kg以上
                weight_notable.append({
                    'horse': horse,
                    'change': weight_change
                })
        
        if weight_notable:
            output.append("注目すべき馬体重変動:")
            output.append("")
            for item in weight_notable:
                horse = item['horse']
                change = item['change']
                change_str = f"+{change}kg" if change > 0 else f"{change}kg"
                status = "🔴 大幅増" if change >= 15 else "🔵 大幅減" if change <= -15 else "⚠️  変動大"
                
                output.append(f"  {status}  {horse['number']:>2}番 {horse['name']:<20}  "
                             f"馬体重変動: {change_str:>6}  評価: {horse.get('weight_change_score', 50.0):.1f}点")
        else:
            output.append("特に注目すべき馬体重変動はありません（±10kg未満）")
        
        output.append("")
        return "\n".join(output)
    
    def _format_betting_suggestions(self, ability_results: List[Dict[str, Any]], 
                                   value_results: List[Dict[str, Any]]) -> str:
        """買い目提案"""
        output = []
        
        output.append(self.separator)
        output.append("🎫 推奨馬券")
        output.append(self.separator)
        output.append("")
        
        if len(ability_results) >= 5:
            # 本命軸の馬連・馬単
            honmei = ability_results[0]['number']
            taikou = ability_results[1]['number']
            tanana = ability_results[2]['number']
            
            output.append("【本命型】堅実重視")
            output.append(f"  馬連: {honmei}-{taikou}, {honmei}-{tanana}")
            output.append(f"  馬単: {honmei}→{taikou}, {honmei}→{tanana}")
            output.append(f"  ワイド: {honmei}-{taikou}, {honmei}-{tanana}, {taikou}-{tanana}")
            output.append("")
            
            # 3連複（本命から上位5頭）
            top5 = [h['number'] for h in ability_results[:5]]
            output.append("【3連複】")
            output.append(f"  軸1頭流し: {honmei}軸 相手{top5[1:]}")
            output.append(f"  BOX: {top5[:4]}")
            output.append("")
        
        # 穴馬狙い
        if value_results and ability_results:
            top3_names = {h['name'] for h in ability_results[:3]}
            anauma = [h for h in value_results if h['name'] not in top3_names][:2]
            
            if anauma:
                honmei_num = ability_results[0]['number']
                anauma_nums = [h['number'] for h in anauma]
                
                output.append("【穴馬型】高配当狙い")
                output.append(f"  馬連: {honmei_num}軸 相手{anauma_nums}")
                output.append(f"  3連複: {honmei_num}軸 相手{anauma_nums + [ability_results[1]['number']]}")
                output.append("")
        
        output.append("※ 資金配分は各自の判断で調整してください")
        output.append("")
        
        return "\n".join(output)
    
    def _format_footer(self) -> str:
        """フッター"""
        output = []
        output.append(self.separator)
        output.append("📝 評価基準")
        output.append(self.separator)
        output.append("")
        output.append("【能力系指標 70%】")
        output.append("  ・過去成績: 25%  ・コース適正: 25%  ・馬場状態: 10%")
        output.append("  ・馬体重変動: 3%  ・前走間隔: 7%")
        output.append("")
        output.append("【投資効率系指標 30%】")
        output.append("  ・オッズ価値: 18%  ・穴馬要素: 12%")
        output.append("")
        output.append("評価ランク: S(90-100) / A(80-89) / B(70-79) / C(60-69) / D(50-59) / E(50未満)")
        output.append(self.separator)
        output.append("")
        
        return "\n".join(output)
    
    def _get_rank_mark(self, rank: int) -> str:
        """順位マーク"""
        marks = {
            1: "🥇1位",
            2: "🥈2位", 
            3: "🥉3位"
        }
        return marks.get(rank, f"  {rank}位")
    
    def _get_grade(self, score: float) -> str:
        """評価グレード"""
        if score >= 90:
            return "S"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "E"
    
    def _get_stars(self, score: float) -> str:
        """星評価"""
        if score >= 90:
            return "★★★★★"
        elif score >= 80:
            return "★★★★☆"
        elif score >= 70:
            return "★★★☆☆"
        elif score >= 60:
            return "★★☆☆☆"
        elif score >= 50:
            return "★☆☆☆☆"
        else:
            return "☆☆☆☆☆"

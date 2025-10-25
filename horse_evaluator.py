# -*- coding: utf-8 -*-
"""
競馬予想システム - 最適化評価システム
過去成績25% + コース35% + オッズ15% + 間隔10% + クラス5% + 馬場5% + 穴馬5%
"""

import os
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import lru_cache
from typing import Dict, List, Optional, Any
from cachetools import cached, LRUCache

from pace_data_parser import calculate_running_style_stats
from running_style_analyzer import RunningStyleAnalyzer, determine_running_style


# グローバルキャッシュ（メモリ効率化）
_anauma_cache = LRUCache(maxsize=1000)

class FastAnaumaDB:
    """穴馬DBキャッシュ（LRUCache強化版）"""
    def __init__(self, db_path: str):
        self.cache = {}
        try:
            con = sqlite3.connect(db_path)
            con.row_factory = sqlite3.Row
            for row in con.execute("SELECT * FROM dark_horses"):
                self.cache[row['horse_name']] = dict(row)
            con.close()
        except: pass
    
    @cached(cache=_anauma_cache)
    def search(self, name: str) -> Optional[Dict]:
        return self.cache.get(name)


class HorseEvaluator:
    """最適化評価システム"""
    
# 評価スコア計算用の定数
    # 過去成績評価
    SCORE_WIN_BASE = 100
    SCORE_WIN_BONUS_MAX = 20
    SCORE_WIN_MARGIN_MULTIPLIER = 5
    SCORE_PLACE_MIN = 30
    SCORE_PLACE_BASE = 100
    SCORE_PLACE_PENALTY = 8
    SCORE_MARGIN_PENALTY_THRESHOLD = 0.5
    SCORE_MARGIN_PENALTY_MULTIPLIER = -3
    
    # コース適性評価
    DISTANCE_TOLERANCE = 200  # 許容距離差（メートル）
    DISTANCE_BONUS_TOP3 = 12
    DISTANCE_BONUS_TOP5 = 4
    TRACK_BONUS_TOP3 = 15
    TRACK_BONUS_TOP5 = 5
    
    # 前走間隔評価
    INTERVAL_OPTIMAL_MIN = 14   # 最適間隔（日）
    INTERVAL_OPTIMAL_MAX = 42
    INTERVAL_SHORT_MIN = 7      # 短すぎる間隔
    INTERVAL_SHORT_MAX = 13
    INTERVAL_NORMAL_MAX = 84    # 普通の間隔
    INTERVAL_SCORE_OPTIMAL = 15
    INTERVAL_SCORE_SHORT = -5
    INTERVAL_SCORE_NORMAL = 0
    INTERVAL_SCORE_LONG = -10
    
    # 穴馬評価
    ODDS_THRESHOLD_HIGH = 20
    ODDS_THRESHOLD_MID = 10
    DARK_HORSE_SCORE_HIGH = 80
    DARK_HORSE_SCORE_MID = 65
    DARK_HORSE_SCORE_LOW = 40

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.anauma_db = FastAnaumaDB(os.path.join(script_dir, 'dark_horse.db'))
        
        # 実力評価ウェイト（本命・対抗用）- 格上挑戦減点あり
        self.ability_weights = {
            'past_performance': 0.25,
            'course_fit': 0.25,
            'track_condition': 0.10,
            'weight_change': 0.03,
            'interval': 0.07,
            'odds_value': 0.18,
            'dark_horse': 0.12,
            'apply_class_penalty': True
        }
        
        # 期待値評価ウェイト（穴馬用）- 格上挑戦減点なし
        self.value_weights = {
            'past_performance': 0.22,
            'course_fit': 0.23,
            'track_condition': 0.08,
            'weight_change': 0.02,
            'interval': 0.07,
            'odds_value': 0.23,
            'dark_horse': 0.15,
            'apply_class_penalty': False
        }
    
    def evaluate_horses(self, race_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """並列処理で馬評価（実力評価と期待値評価の2回）"""
        horses = race_data.get('horses', [])
        if not horses: return {'ability_results': [], 'value_results': []}
        
        # 脚質判定を実行
        horses_stats = []
        for h in horses:
            recent_races = h.get('recent_races', [])
            if recent_races:
                stats = calculate_running_style_stats(recent_races)
                stats['name'] = h.get('name')
                horses_stats.append(stats)
        
        # レース展開を分析
        analyzer = RunningStyleAnalyzer(top_n=2, adjustment_scale=0.10)
        pace, adjustments, meta = analyzer.analyze(horses_stats)
        
        # 実力評価（本命・対抗用）
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            ability_results = list(executor.map(
                lambda h: self._evaluate_horse(h, race_data, self.ability_weights, adjustments.get(h.get('name'), 1.0)), horses
            ))
        ability_results.sort(key=lambda x: x['final_score'], reverse=True)
        
        # 期待値評価（穴馬用）
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            value_results = list(executor.map(
                lambda h: self._evaluate_horse(h, race_data, self.value_weights, adjustments.get(h.get('name'), 1.0)), horses
            ))
        value_results.sort(key=lambda x: x['final_score'], reverse=True)
        
        return {
            'ability_results': ability_results,
            'value_results': value_results,
            'pace_analysis': {'pace': pace, 'adjustments': adjustments}
        }
    
    def _evaluate_horse(self, horse: Dict[str, Any], race_data: Dict[str, Any], weights: Dict[str, float], adjustment: float = 1.0) -> Dict[str, Any]:
        """単一馬の評価"""
        # 各要素評価
        past_score = self._eval_past_performance(horse)
        course_score = self._eval_course_fit(horse, race_data)
        track_score = self._eval_track_condition(horse, race_data)
        weight_change_score = self._eval_weight_change(horse)
        interval_score = self._eval_interval(horse, race_data)
        odds_score = self._eval_odds_value(horse, past_score, course_score)
        dark_score = self._eval_dark_horse(horse)
        
        # 格上挑戦減点（実力評価のみ）
        class_penalty = 0
        if weights.get('apply_class_penalty', False):
            class_penalty = self._eval_class_penalty(horse, race_data)
        
        # 最終スコア
        final = (
            past_score * weights['past_performance'] +
            course_score * weights['course_fit'] +
            track_score * weights['track_condition'] +
            weight_change_score * weights['weight_change'] +
            interval_score * weights['interval'] +
            odds_score * weights['odds_value'] +
            dark_score * weights['dark_horse'] +
            class_penalty
        )
        
        # 脚質判定による補正を適用
        final = final * adjustment
        
        return {
            "name": horse.get("name", "不明"),
            "number": horse.get("number", "?"),
            "odds": horse.get("odds", 0),
            "jockey": horse.get("jockey", "?"),
            "weight": horse.get("weight", "?"),
            "weight_change": horse.get("weight_change", "?"),
            "popularity": horse.get("popularity", "?"),
            "final_score": round(final, 2),
            "performance_score": round(past_score, 1),
            "course_fit_score": round(course_score, 1),
            "track_condition_score": round(track_score, 1),
            "weight_change_score": round(weight_change_score, 1),
            "interval_score": round(interval_score, 1),
            "odds_value_score": round(odds_score, 1),
            "dark_horse_score": round(dark_score, 1),
            "class_penalty": round(class_penalty, 1)
        }
    
    def _eval_past_performance(self, horse: Dict[str, Any]) -> float:
        """過去成績+調子トレンド（25%）"""
        races = horse.get('recent_races', [])
        if not races: return 50
        
        # 過去成績評価（70%）
        scores, weights = [], [1.5, 1.2, 1.0, 0.8, 0.5]
        for i, race in enumerate(races[:5]):
            # finishフィールドを使用（JSONデータの実際の構造に合わせる）
            result = race.get('finish', race.get('result', 18))
            if isinstance(result, str):
                import re
                match = re.search(r'\d+', result)
                result = int(match.group()) if match else 18
            
            # 頭数を考慮した評価
            runners = race.get('runners', 16)
            margin = race.get('time_margin', 1.0)
            
            if result == 1:
                # 頭数を考慮した1着の評価
                base_score = 100 + min(20, margin * 5)
                if runners >= 16:
                    base_score *= 1.2  # 多頭数レースでの勝利は価値が高い
                elif runners <= 10:
                    base_score *= 0.9  # 少頭数レースは割引
                score = base_score
            else:
                score = max(30, 100 - (result-1) * 8) + max(-15, (margin-0.5) * -3)
            
            scores.append(max(0, score) * weights[i])
        
        base = sum(scores) / sum(weights[:len(scores)])
        
        # 連勝ボーナス（アンゴラブラックのような馬を評価）
        consecutive_wins = 0
        for race in races:
            if race.get('finish', race.get('result', 18)) == 1:
                consecutive_wins += 1
            else:
                break
        
        bonus = 0
        if consecutive_wins >= 3:
            bonus = 15  # 3連勝以上は大幅ボーナス
        elif consecutive_wins == 2:
            bonus = 8   # 2連勝もボーナス
        
        base = min(100, base + bonus)
        
        # 調子トレンド（30%）
        trend = 0
        if len(races) >= 3:
            for i in range(1, 3):
                current_result = races[i].get('result', 18)
                prev_result = races[i-1].get('result', 18)
                
                # resultが文字列の場合は数値に変換
                if isinstance(current_result, str):
                    import re
                    match = re.search(r'\d+', current_result)
                    current_result = int(match.group()) if match else 18
                if isinstance(prev_result, str):
                    import re
                    match = re.search(r'\d+', prev_result)
                    prev_result = int(match.group()) if match else 18
                
                if current_result < prev_result:
                    trend += 15  # 上昇
                elif current_result > prev_result:
                    trend -= 10  # 下降
        
        return base * 0.7 + (50 + trend) * 0.3
    
    def _eval_course_fit(self, horse: Dict[str, Any], race_data: Dict[str, Any]) -> float:
        """コース適性：距離60% + 競馬場40%（35%）"""
        races = horse.get('recent_races', [])
        if not races: return 60
        
        current_dist = race_data.get('distance', 2000)
        current_track = race_data.get('race_info', {}).get('track', '')
        
        # 距離適性（60%）
        dist_score = 60
        for race in races[:5]:
            if abs(race.get('distance', 0) - current_dist) <= 200:
                result = race.get('finish', race.get('result', 18))  # finishを優先
                # resultが文字列の場合は数値に変換
                if isinstance(result, str):
                    import re
                    match = re.search(r'\d+', result)
                    result = int(match.group()) if match else 18
                if result <= 3: dist_score += 12
                elif result <= 5: dist_score += 4
        dist_score = min(100, dist_score)
        
        # 競馬場適性（40%）
        track_score = 60
        for race in races[:5]:
            if race.get('venue', race.get('track', '')) == current_track:
                result = race.get('finish', race.get('result', 18))  # finishを優先
                # resultが文字列の場合は数値に変換
                if isinstance(result, str):
                    import re
                    match = re.search(r'\d+', result)
                    result = int(match.group()) if match else 18
                if result <= 3: track_score += 15
                elif result <= 5: track_score += 5
        track_score = min(100, track_score)
        
        return dist_score * 0.6 + track_score * 0.4
    
    def _eval_class_fit(self, horse: Dict[str, Any]) -> float:
        """クラス適性（5%）"""
        races = horse.get('recent_races', [])
        if not races: return 50
        
        current_class = horse.get('class', '')
        same_class_results = []
        
        for race in races[:5]:
            if race.get('class', '') == current_class:
                result = race.get('result', 18)
                # resultが文字列の場合は数値に変換
                if isinstance(result, str):
                    import re
                    match = re.search(r'[0-9]+', result)
                    result = int(match.group()) if match else 18
                same_class_results.append(result)
        
        if not same_class_results: return 40  # 昇級直後はペナルティ
        
        # 同クラスでの平均着順から評価
        avg = sum(same_class_results) / len(same_class_results)
        return max(0, min(100, 100 - (avg - 1) * 10))
    
    def _eval_track_condition(self, horse: Dict[str, Any], race_data: Dict[str, Any]) -> float:
        """馬場状態適性（5%）"""
        races = horse.get('recent_races', [])
        if not races: return 50
        
        current_condition = race_data.get('race_info', {}).get('track_condition', '良')
        
        # 同じ馬場状態での成績
        same_condition_results = []
        for race in races[:5]:
            if race.get('track_condition', '') == current_condition:
                result = race.get('result', 18)
                # resultが文字列の場合は数値に変換
                if isinstance(result, str):
                    import re
                    match = re.search(r'[0-9]+', result)
                    result = int(match.group()) if match else 18
                same_condition_results.append(result)
        
        if not same_condition_results: return 50
        
        avg = sum(same_condition_results) / len(same_condition_results)
        return max(0, min(100, 100 - (avg - 1) * 10))
    
    def _eval_interval(self, horse: Dict[str, Any], race_data: Dict[str, Any]) -> float:
        """前走間隔（10%）"""
        race_date_str = race_data.get('race_info', {}).get('date')
        races = horse.get('recent_races', [])
        
        if not race_date_str or not races: return 0
        
        try:
            race_date = datetime.strptime(race_date_str, '%Y-%m-%d')
            last_date = datetime.strptime(races[0].get('date', ''), '%Y-%m-%d')
            days = (race_date - last_date).days
        except: return 0
        
        if 14 <= days <= 42: return 15    # 最適
        elif 7 <= days <= 13: return -5   # 短すぎ
        elif 43 <= days <= 84: return 0   # 普通
        else: return -10                   # 長すぎ
    
    def _eval_odds_value(self, horse: Dict[str, Any], past: float, course: float) -> float:
        """オッズ価値（18%）- 改善版（対数スケール+上限設定）"""
        import math
        
        ability = (past + course) / 2
        odds = horse.get('odds', 1.0)
        
        # オッズ1.0未満は異常値
        if odds < 1.0:
            return 0
        
        # 能力スコアを0-1の範囲に正規化
        ability_norm = ability / 100.0
        
        # 対数スケールで調整（極端なオッズを抑制）
        if odds > 20:
            # オッズ20倍以上は対数スケールで減衰
            odds_factor = 20 + math.log(odds / 20 + 1) * 5
        else:
            odds_factor = odds
        
        # 調整後の期待値
        adjusted_ev = (ability_norm * odds_factor) - 1
        
        # スコア化（-1〜+9の範囲を0-100点に変換）
        score = 50 + adjusted_ev * 10
        
        # 0-100点に制限
        score = max(0, min(100, score))
        
        # 追加ルール: 能力が極端に低い馬は高オッズでも評価しない
        if ability_norm < 0.3 and odds > 30:
            score *= 0.5  # 半減
        
        return score
    
    def _eval_dark_horse(self, horse: Dict[str, Any]) -> float:
        """穴馬要素（5%）"""
        name = horse.get('name')
        db_data = self.anauma_db.search(name)
        if db_data and db_data.get('evaluation_score'):
            return db_data['evaluation_score']
        
        odds = horse.get('odds', 1.0)
        if odds > 20: return 80
        if odds > 10: return 65
        return 40
    
    def _eval_weight_change(self, horse: Dict[str, Any]) -> float:
        """馬体重変動評価（3%）"""
        weight = horse.get('weight', 0)
        weight_change = horse.get('weight_change', 0)
        
        # 馬体重データがない場合は中立スコア
        if weight == 0 or weight == '?':
            return 50
        
        # 文字列の場合は数値に変換
        if isinstance(weight, str):
            try:
                weight = int(weight.replace('kg', '').strip())
            except:
                return 50
        
        if isinstance(weight_change, str):
            try:
                weight_change = int(weight_change.replace('+', '').replace('kg', '').strip())
            except:
                weight_change = 0
        
        # 基本スコア
        score = 50
        
        # 理想的な馬体重範囲（450-520kg）
        if 450 <= weight <= 520:
            score += 10
        elif weight < 420 or weight > 550:
            score -= 10
        
        # 馬体重の増減評価
        if -3 <= weight_change <= 3:
            # 適度な維持（ベスト）
            score += 20
        elif -8 <= weight_change < -3:
            # やや減（良好）
            score += 10
        elif 3 < weight_change <= 8:
            # やや増（まずまず）
            score += 5
        elif weight_change < -15:
            # 大幅減（仕上げすぎ、疲労の可能性）
            score -= 15
        elif weight_change > 15:
            # 大幅増（太め残り、調整不足）
            score -= 20
        elif -15 <= weight_change < -8:
            # かなり減（やや心配）
            score -= 5
        elif 8 < weight_change <= 15:
            # かなり増（調整不足の可能性）
            score -= 10
        
        # 休み明けの場合は増減の許容範囲を広げる
        races = horse.get('recent_races', [])
        if races:
            try:
                from datetime import datetime
                # 前走日を取得
                last_date_str = races[0].get('date', '')
                if last_date_str:
                    last_date = datetime.strptime(last_date_str, '%Y-%m-%d')
                    # 今日の日付
                    today = datetime.now()
                    interval_days = (today - last_date).days
                    
                    # 60日以上の休み明けの場合
                    if interval_days > 60:
                        if 0 <= weight_change <= 20:
                            score += 5  # 休み明けはある程度の増加は自然
            except:
                pass
        
        return max(0, min(100, score))
    
    def _eval_class_penalty(self, horse: Dict[str, Any], race_data: Dict[str, Any]) -> float:
        """格上挑戦時の減点（実力評価のみに適用）"""
        # 今回のレースグレード
        current_grade = race_data.get('race_info', {}).get('grade', '')
        
        # 前走情報
        races = horse.get('recent_races', [])
        if not races:
            return 0
        
        last_race = races[0]
        last_race_name = last_race.get('race', '')
        
        # グレードの序列（数字が大きいほど格上）
        grade_levels = {
            'GI': 5,
            'GII': 4,
            'GIII': 3,
            'OP': 2,  # オープン・リステッド
            '3勝': 1,
            '2勝': 0,
            '1勝': -1
        }
        
        current_level = grade_levels.get(current_grade, 2)
        
        # 前走のグレード推定
        last_level = 2  # デフォルトはOP
        for grade, level in grade_levels.items():
            if grade in last_race_name or grade in str(last_race.get('class', '')):
                last_level = level
                break
        
        # 格上挑戦の場合は減点
        level_diff = current_level - last_level
        if level_diff <= 0:
            return 0
        
        # 1段階格上: -5点、2段階: -10点、3段階以上: -15点
        if level_diff == 1:
            return -5
        elif level_diff == 2:
            return -10
        else:
            return -15

"""
高度競馬予測・馬券最適化統合システム (Advanced Recursive Racing Analysis System)

【概要】
このシステムは馬の能力を多層的・回帰的に分析し、最適な馬券購入プランを提案します。
距離に依存しない普遍的な評価基準を採用し、本命馬/対抗馬/穴馬の選定と精緻な馬券構築を行います。
予算300円、100円単位で馬券を提案します。

【特徴】
- 多層的評価プロセス: 各評価要素が複数の下位要素から構成され、相互に影響し合う複雑なシステム
- 回帰的分析手法: 評価結果を再度入力として利用し、より精度の高い予測を実現
- 馬券最適化アルゴリズム: 本命馬/対抗馬/穴馬の特定と、状況に応じた最適な馬券構成の提案

【使用例】
horses = [
    {'horse_number': 1, 'horse_name': 'アタルサン', 'odds': 3.4, 'horse_age': 4, 'jockey': 'ルメール', 'weight': 450, 'weight_change': 2},
    {'horse_number': 2, 'horse_name': 'ウララ', 'odds': 7.8, 'horse_age': 3, 'jockey': '福永', 'weight': 458, 'weight_change': -3},
    # 他の馬データ...
]

race_info = {
    'race_name': '東京優駿（日本ダービー）',
    'track': '東京',
    'surface': '芝',
    'distance': 2400,
    'track_condition': '良'
}

result = analyze_race(horses, race_info)
"""

import numpy as np
from typing import List, Dict, Optional, Tuple, Callable, Any, Set
from functools import lru_cache
import math
import json
import os
import sys
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re

class AdvancedRacingSystem:
    """高度な再帰的競馬予測・馬券最適化統合システム"""
    
    def __init__(self):
        """初期化"""
        # 評価レイヤー構造
        self.evaluation_layers = {
            'primary': {
                'base_ability': 0.40,       # 基礎能力（勝率など）
                'competitive_profile': 0.35, # 競争適性プロファイル
                'condition_factors': 0.25    # コンディションファクター
            },
            'secondary': {
                'base_ability': {
                    'win_rate': 0.30,        # 勝率
                    'consistency': 0.25,      # 安定性
                    'performance_level': 0.25, # パフォーマンスレベル
                    'class_record': 0.20      # クラス実績
                },
                'competitive_profile': {
                    'distance_aptitude': 0.30, # 距離適性
                    'course_aptitude': 0.30,   # コース適性
                    'race_style_match': 0.25,  # レーススタイル適合性
                    'jockey_synergy': 0.15     # 騎手との相性
                },
                'condition_factors': {
                    'physical_condition': 0.40, # 馬体状態
                    'form_cycle': 0.30,         # 調子サイクル
                    'environmental_adaptation': 0.15, # 環境適応性
                    'psychological_state': 0.15  # 精神状態
                }
            },
            'tertiary': {
                # 三次評価層の詳細構造（実装の簡略化のため一部省略）
                'win_rate': {'recent': 0.60, 'career': 0.40},
                'consistency': {'finishing_position_variance': 0.60, 'performance_stability': 0.40},
                'physical_condition': {'weight_trend': 0.50, 'appearance': 0.30, 'workout': 0.20},
                'jockey_synergy': {'success_rate': 0.70, 'riding_style_match': 0.30}
                # 他の評価要素も同様の構造
            }
        }
        
        # 馬場状態調整係数
        self.track_adjustments = {
            '良': 1.0, '稍重': 0.98, '重': 0.96, '不良': 0.94
        }
        
        # 馬券種類
        self.bet_types = {
            'win': '単勝', 'place': '複勝', 'show': '複勝', 
            'quinella': '馬連', 'exacta': '馬単',
            'wide': 'ワイド', 'trio': '三連複', 'trifecta': '三連単',
            'quinella_formation': '馬連フォーメーション', 
            'exacta_formation': '馬単フォーメーション',
            'trio_formation': '三連複フォーメーション', 
            'trifecta_formation': '三連単フォーメーション'
        }
        
        # レース特性解析用パラメーター
        self.race_characteristic_params = {
            'pace_dependency': 0.0,    # ペース依存度（0-1）
            'upset_likelihood': 0.0,   # 波乱度（0-1）
            'form_importance': 0.0,    # 調子重要度（0-1）
            'class_gap': 0.0           # クラス差（0-1）
        }
        
        # 再帰分析の深度制限
        self.max_recursion_depth = 3
        
        # 馬券構成テンプレート（必要に応じて遅延初期化）
        self._betting_templates_cache = None
    
    def analyze_race(self, horses: List[Dict], race_info: Optional[Dict] = None) -> Dict:
        """レース分析の統合エントリーポイント"""
        if not horses:
            return {"error": "馬データがありません"}
        
        # レース情報の前処理
        race_info = self._preprocess_race_info(race_info)
        
        # レース特性の解析
        race_characteristics = self._analyze_race_characteristics(horses, race_info)
        race_info['race_characteristics'] = race_characteristics
        
        # 馬の多層的評価（回帰的処理を含む）
        evaluated_horses = self._evaluate_horses_recursively(horses, race_info)
        
        # 馬の分類（本命馬/対抗馬/穴馬）
        classified_horses = self._classify_horses(evaluated_horses)
        
        # 予測とランキング
        predictions = self._predict_race(evaluated_horses, race_info)
        
        # 馬券最適化（多層的処理）
        betting_plan = self._multi_layer_betting_optimization(
            predictions, classified_horses, race_info, budget=300
        )
        
        # 結果のまとめ
        result = {
            "race_info": race_info,
            "predictions": predictions,
            "classified_horses": classified_horses,
            "betting_plan": betting_plan
        }
        
        return result
    
    def _preprocess_race_info(self, race_info: Optional[Dict]) -> Dict:
        """レース情報の前処理と補完"""
        if race_info is None:
            race_info = {}
        
        # デフォルト値の設定
        default_info = {
            'race_name': '不明', 'track': '不明', 'surface': '芝',
            'distance': 1800, 'track_condition': '良',
            'date': '不明', 'class': '不明', 'grade': '一般',
            'prize': 0, 'race_type': '一般', 'age_restriction': '3歳以上'
        }
        
        # 欠損情報の補完
        for key, value in default_info.items():
            if key not in race_info:
                race_info[key] = value
        
        # レースグレードの正規化
        if 'grade' in race_info:
            grade = race_info['grade'].upper()
            if 'G1' in grade or '１' in grade or '1' in grade and 'G' in grade:
                race_info['normalized_grade'] = 'G1'
            elif 'G2' in grade or '２' in grade or '2' in grade and 'G' in grade:
                race_info['normalized_grade'] = 'G2'
            elif 'G3' in grade or '３' in grade or '3' in grade and 'G' in grade:
                race_info['normalized_grade'] = 'G3'
            elif '特別' in grade or 'OP' in grade:
                race_info['normalized_grade'] = 'OP'
            else:
                race_info['normalized_grade'] = '一般'
        else:
            race_info['normalized_grade'] = '一般'
        
        # 馬場状態の正規化
        track_condition = race_info.get('track_condition', '良')
        
        normalized_condition = '良'
        for cond in ['良', '稍重', '重', '不良']:
            if cond in track_condition:
                normalized_condition = cond
                break
        race_info['normalized_condition'] = normalized_condition
        
        return race_info
    
    def _analyze_race_characteristics(self, horses: List[Dict], race_info: Dict) -> Dict:
        """レース特性の詳細な分析"""
        characteristics = self.race_characteristic_params.copy()
        
        # オッズ分布の分析
        odds_list = [horse.get('odds', 10.0) for horse in horses if 'odds' in horse]
        if odds_list:
            # オッズの標準偏差で波乱度を推定
            odds_array = np.array(odds_list)
            odds_std = np.std(odds_array) if len(odds_list) > 1 else 0
            odds_mean = np.mean(odds_array)
            
            # 標準化した波乱度（0-1スケール）
            upset_likelihood = min(1.0, odds_std / (odds_mean * 2))
            characteristics['upset_likelihood'] = upset_likelihood
            
            # 人気の集中度
            favorites_ratio = sum(1 for o in odds_array if o < 10.0) / len(odds_array)
            characteristics['favorites_concentration'] = 1.0 - favorites_ratio
        
        # レースクラスによる調整
        grade = race_info.get('normalized_grade', '一般')
        if 'G1' in grade:
            characteristics['class_gap'] = 0.2  # G1は馬のレベルが近い傾向
            characteristics['form_importance'] = 0.8  # 調子が非常に重要
        elif 'G2' in grade or 'G3' in grade:
            characteristics['class_gap'] = 0.3
            characteristics['form_importance'] = 0.7
        elif 'OP' in grade or '特別' in grade:
            characteristics['class_gap'] = 0.5
            characteristics['form_importance'] = 0.6
        else:
            characteristics['class_gap'] = 0.7  # 一般戦は馬のレベル差が大きい傾向
            characteristics['form_importance'] = 0.5
        
        # 距離による特性調整（統計データに基づく一般的傾向）
        distance = race_info.get('distance', 1800)
        if distance <= 1400:  # 短距離
            characteristics['pace_dependency'] = 0.8  # ペース依存度が高い
        elif 1401 <= distance <= 1800:  # マイル
            characteristics['pace_dependency'] = 0.6
        elif 1801 <= distance <= 2400:  # 中距離
            characteristics['pace_dependency'] = 0.5
        else:  # 長距離
            characteristics['pace_dependency'] = 0.3  # ペース依存度が低い
        
        # 出走頭数に基づく調整
        num_horses = len(horses)
        if num_horses >= 16:
            characteristics['race_complexity'] = 0.8  # 競争が複雑になる
        elif 12 <= num_horses < 16:
            characteristics['race_complexity'] = 0.6
        elif 8 <= num_horses < 12:
            characteristics['race_complexity'] = 0.4
        else:
            characteristics['race_complexity'] = 0.2  # 少頭数で競争がシンプル
        
        # 馬齢構成分析
        ages = [horse.get('horse_age', 3) for horse in horses if 'horse_age' in horse]
        if ages:
            age_variance = np.var(ages) if len(ages) > 1 else 0
            characteristics['age_homogeneity'] = max(0, 1.0 - (age_variance / 5.0))
        
        return characteristics
    
    def _evaluate_horses_recursively(self, horses: List[Dict], race_info: Dict, depth: int = 0) -> List[Dict]:
        """馬の多層的・回帰的評価"""
        if depth >= self.max_recursion_depth:
            return horses
        
        # 初期評価（一次処理）
        evaluated_horses = self._evaluate_horses_primary(horses, race_info)
        
        if depth == 0:
            # 相対評価情報の追加（群としての特性を考慮）
            evaluated_horses = self._add_relative_evaluation(evaluated_horses, race_info)
        
        # 前の評価結果を入力として再評価（回帰的処理）
        refined_horses = self._refine_evaluation_based_on_previous(evaluated_horses, race_info)
        
        # 次の再帰レベルへ
        return self._evaluate_horses_recursively(refined_horses, race_info, depth + 1)
    
    def _evaluate_horses_primary(self, horses: List[Dict], race_info: Dict) -> List[Dict]:
        """馬の一次評価処理"""
        evaluated_horses = []
        
        for horse in horses:
            # 基本情報のコピー
            evaluated_horse = horse.copy()
            
            # 各要素の多層評価
            evaluations = self._multi_layer_horse_evaluation(horse, race_info)
            
            # 評価をhorseに追加
            evaluated_horse.update(evaluations)
            
            # 総合評価スコアの計算
            total_score = self._calculate_total_score(evaluations, race_info)
            
            # 馬場状態による調整
            track_factor = self.track_adjustments.get(
                race_info.get('normalized_condition', '良'), 1.0
            )
            
            # 最終スコア（100点満点）
            final_score = min(100, total_score * 100 * track_factor)
            
            # ランク付け
            rank = self._determine_rank(final_score)
            
            # 評価結果の保存
            evaluated_horse.update({
                'total_score': final_score,
                'rank': rank,
                'evaluation_details': evaluations  # 詳細評価を保存
            })
            
            evaluated_horses.append(evaluated_horse)
        
        return evaluated_horses
    
    def _multi_layer_horse_evaluation(self, horse: Dict, race_info: Dict) -> Dict:
        """馬の多層的能力評価"""
        # 一次評価要素
        primary_evaluations = {}
        
        # 一次層の各要素を評価
        for factor, weight in self.evaluation_layers['primary'].items():
            # 二次評価層の取得
            secondary_factors = self.evaluation_layers['secondary'].get(factor, {})
            
            # 二次評価の実行
            secondary_evaluations = {}
            for sec_factor, sec_weight in secondary_factors.items():
                # 二次評価要素の計算
                secondary_evaluations[sec_factor] = self._evaluate_secondary_factor(
                    sec_factor, horse, race_info
                )
            
            # 一次評価の計算（二次評価の加重平均）
            if secondary_evaluations:
                factor_score = sum(
                    val * secondary_factors[key] for key, val in secondary_evaluations.items()
                )
                primary_evaluations[factor] = factor_score
            else:
                # 二次評価がない場合はデフォルト値
                primary_evaluations[factor] = 0.5
        
        # すべての評価層を結合
        all_evaluations = {
            'primary': primary_evaluations,
            # 詳細な二次・三次評価も保存（省略）
        }
        
        return all_evaluations
    
    @lru_cache(maxsize=128)
    def _evaluate_secondary_factor(self, factor: str, horse: Dict, race_info: Dict) -> float:
        """二次評価要素の評価"""
        # 要素ごとの評価関数をマッピング
        evaluation_functions = {
            'win_rate': self._evaluate_win_rate,
            'consistency': self._evaluate_consistency,
            'performance_level': self._evaluate_performance_level,
            'class_record': self._evaluate_class_record,
            'distance_aptitude': self._evaluate_distance_aptitude,
            'course_aptitude': self._evaluate_course_aptitude,
            'race_style_match': self._evaluate_race_style_match,
            'physical_condition': self._evaluate_physical_condition,
            'form_cycle': self._evaluate_form_cycle,
            'environmental_adaptation': self._evaluate_environmental_adaptation,
            'psychological_state': self._evaluate_psychological_state
        }
        
        # 対応する評価関数を呼び出し
        if factor in evaluation_functions:
            return evaluation_functions[factor](horse, race_info)
        
        # 未定義の要素はデフォルト値
        return 0.5
    
    def _evaluate_win_rate(self, horse: Dict, race_info: Dict) -> float:
        """勝率評価"""
        # 三次評価要素の取得
        tertiary_factors = self.evaluation_layers['tertiary'].get('win_rate', {})
        
        # 最近の勝率評価（直近5走）
        recent_races = horse.get('recent_races', 5)
        recent_wins = horse.get('recent_wins', 0)
        recent_win_rate = recent_wins / max(1, recent_races)
        
        # キャリア全体の勝率評価
        career_races = horse.get('career_races', 0)
        career_wins = horse.get('career_wins', 0)
        career_win_rate = career_wins / max(1, career_races)
        
        # 勝率に基づくスコア計算
        recent_score = min(1.0, recent_win_rate * 3)  # 33%以上で満点
        career_score = min(1.0, career_win_rate * 4)  # 25%以上で満点
        
        # 加重平均
        win_rate_score = (
            recent_score * tertiary_factors.get('recent', 0.6) +
            career_score * tertiary_factors.get('career', 0.4)
        )
        
        return win_rate_score
    
    def _evaluate_consistency(self, horse: Dict, race_info: Dict) -> float:
        """安定性評価"""
        # 着順のバラつき評価
        positions = horse.get('recent_positions', [])
        
        trend_score = 0.5  # デフォルト
        
        if len(positions) >= 3:
            # 着順の変化傾向を分析
            trend = np.polyfit(range(len(positions)), positions, 1)[0]
            if trend < -0.5:  # 着順が上がっていく（数字が小さくなる）
                trend_score = 0.8  # 上昇傾向
            elif trend > 0.5:  # 着順が下がっていく
                trend_score = 0.3  # 下降傾向
            else:
                trend_score = 0.6  # 安定傾向
        
        # 激走と凡走の頻度
        great_performances = horse.get('great_performances', 0)
        poor_performances = horse.get('poor_performances', 0)
        total_races = max(1, horse.get('recent_races', 5))
        
        stability_score = 1.0 - ((great_performances + poor_performances) / total_races)
        
        # 加重平均
        consistency_score = (
            trend_score * 0.6 +
            stability_score * 0.4
        )
        
        return consistency_score
    
    def _evaluate_performance_level(self, horse: Dict, race_info: Dict) -> float:
        """パフォーマンスレベルの評価"""
        # 馬のベストパフォーマンス評価
        best_speed_figure = horse.get('best_speed_figure', 0)
        avg_speed_figure = horse.get('avg_speed_figure', 0)
        recent_speed_figure = horse.get('recent_speed_figure', 0)
        
        # 正規化（0-1スケール）
        # 通常、競馬のスピード指数は80-120程度の範囲
        norm_best = max(0, min(1.0, (best_speed_figure - 80) / 40))
        norm_avg = max(0, min(1.0, (avg_speed_figure - 80) / 40))
        norm_recent = max(0, min(1.0, (recent_speed_figure - 80) / 40))
        
        # 加重平均
        performance_score = (
            norm_best * 0.3 +
            norm_avg * 0.3 +
            norm_recent * 0.4  # 最近のパフォーマンスをより重視
        )
        
        return performance_score
    
    def _evaluate_class_record(self, horse: Dict, race_info: Dict) -> float:
        """クラス実績の評価"""
        # 現在のレースクラス
        current_class = race_info.get('normalized_grade', '一般')
        
        # このクラスでの成績
        class_races = horse.get(f'{current_class}_races', 0)
        class_wins = horse.get(f'{current_class}_wins', 0)
        class_top3 = horse.get(f'{current_class}_top3', 0)
        
        # クラス戦績スコア
        if class_races > 0:
            class_win_rate = class_wins / class_races
            class_top3_rate = class_top3 / class_races
            
            class_score = (
                class_win_rate * 0.7 +
                class_top3_rate * 0.3
            )
        else:
            # 経験なしの場合は中程度の評価
            class_score = 0.4
        
        # 昇降級履歴
        up_class = horse.get('up_class', False)
        down_class = horse.get('down_class', False)
        
        # 昇降級補正
        if up_class:
            # 昇級馬は少し厳しめに評価
            class_score *= 0.9
        elif down_class:
            # 降級馬はやや高め
            class_score *= 1.1
        
        # 最終スコア（0-1に収める）
        return max(0.1, min(1.0, class_score))
    
    def _evaluate_distance_aptitude(self, horse: Dict, race_info: Dict) -> float:
        """距離適性の統合評価"""
        # 現在のレース距離
        race_distance = race_info.get('distance', 1800)
        
        # 距離レンジごとの成績
        distance_records = {}
        ranges = [(0, 1400), (1401, 1800), (1801, 2400), (2401, 4000)]
        
        for min_dist, max_dist in ranges:
            range_key = f'{min_dist}-{max_dist}'
            range_races = horse.get(f'{range_key}_races', 0)
            range_wins = horse.get(f'{range_key}_wins', 0)
            range_top3 = horse.get(f'{range_key}_top3', 0)
            
            if range_races > 0:
                win_rate = range_wins / range_races
                top3_rate = range_top3 / range_races
                distance_records[range_key] = {
                    'races': range_races,
                    'win_rate': win_rate,
                    'top3_rate': top3_rate,
                    'score': win_rate * 0.7 + top3_rate * 0.3
                }
        
        # 該当距離レンジのスコア
        current_range = None
        for min_dist, max_dist in ranges:
            if min_dist <= race_distance <= max_dist:
                current_range = f'{min_dist}-{max_dist}'
                break
        
        if current_range and current_range in distance_records:
            range_score = distance_records[current_range]['score']
        else:
            # データなしの場合はベスト距離との差から推定
            best_distance = horse.get('best_distance', 1800)
            distance_diff = abs(race_distance - best_distance)
            range_score = max(0.3, 1.0 - (distance_diff / 1000))
        
        # 血統からの距離適性評価
        pedigree_distance_aptitude = horse.get('pedigree_distance_aptitude', 0.5)
        
        # 最終的な距離適性スコア（過去実績70%、血統30%）
        aptitude_score = range_score * 0.7 + pedigree_distance_aptitude * 0.3
        
        return max(0.1, min(1.0, aptitude_score))
    
    def _evaluate_course_aptitude(self, horse: Dict, race_info: Dict) -> float:
        """コース適性の評価"""
        # 現在のコースと馬場
        track = race_info.get('track', '')
        surface = race_info.get('surface', '')
        
        # コース別成績
        track_races = horse.get(f'{track}_races', 0)
        track_wins = horse.get(f'{track}_wins', 0)
        track_top3 = horse.get(f'{track}_top3', 0)
        
        # 馬場別成績
        surface_races = horse.get(f'{surface}_races', 0)
        surface_wins = horse.get(f'{surface}_wins', 0)
        surface_top3 = horse.get(f'{surface}_top3', 0)
        
        # スコア計算
        track_score = 0.5  # デフォルト
        if track_races > 0:
            win_rate = track_wins / track_races
            top3_rate = track_top3 / track_races
            track_score = win_rate * 0.7 + top3_rate * 0.3
        
        surface_score = 0.5  # デフォルト
        if surface_races > 0:
            win_rate = surface_wins / surface_races
            top3_rate = surface_top3 / surface_races
            surface_score = win_rate * 0.7 + top3_rate * 0.3
        
        # コース形状適性
        course_shape = race_info.get('course_shape', '')
        shape_aptitude = horse.get(f'{course_shape}_aptitude', 0.5)
        
        # 総合コース適性スコア
        aptitude_score = (
            track_score * 0.4 +
            surface_score * 0.4 +
            shape_aptitude * 0.2
        )
        
        return max(0.1, min(1.0, aptitude_score))
    
    def _evaluate_race_style_match(self, horse: Dict, race_info: Dict) -> float:
        """レーススタイルの適合性評価"""
        # 馬の走法
        running_style = horse.get('running_style', 'unknown')
        
        # レース展開予想
        pace_dependency = race_info.get('race_characteristics', {}).get('pace_dependency', 0.5)
        
        # 走法ごとのスコア（レース特性に応じて調整）
        style_scores = {
            'front': 0.7 - (pace_dependency * 0.3),  # ペース依存度が高いと逃げ馬は不利
            'stalker': 0.5 + (pace_dependency * 0.3),  # ペース依存度が高いと先行有利
            'mid': 0.5,  # 中団は比較的安定
            'closer': 0.3 + (pace_dependency * 0.5)  # ペース依存度が高いと差し馬有利
        }
        
        # 走法に応じたスコア
        style_score = style_scores.get(running_style, 0.5)
        
        # 得意な展開との一致度
        preferred_pace = horse.get('preferred_pace', 'normal')
        expected_pace = race_info.get('expected_pace', 'normal')
        
        pace_match = 0.5  # デフォルト
        
        if preferred_pace == expected_pace:
            pace_match = 0.9  # 高い一致
        elif (preferred_pace == 'slow' and expected_pace == 'normal') or \
             (preferred_pace == 'normal' and expected_pace == 'slow'):
            pace_match = 0.7  # 部分的一致
        elif (preferred_pace == 'fast' and expected_pace == 'normal') or \
             (preferred_pace == 'normal' and expected_pace == 'fast'):
            pace_match = 0.7  # 部分的一致
        elif preferred_pace == 'any':
            pace_match = 0.8  # 汎用性
        
        # 最終スコア
        style_match_score = style_score * 0.6 + pace_match * 0.4
        
        return max(0.1, min(1.0, style_match_score))
    
    def _evaluate_physical_condition(self, horse: Dict, race_info: Dict) -> float:
        """馬体状態の評価"""
        # 馬体重と変化
        weight = horse.get('weight', 0)
        weight_change = horse.get('weight_change', 0)
        
        # 馬体重スコア（標準範囲内が良い）
        if 440 <= weight <= 480:
            weight_score = 0.9  # 理想的な範囲
        elif 420 <= weight < 440 or 480 < weight <= 500:
            weight_score = 0.7  # 許容範囲
        elif 400 <= weight < 420 or 500 < weight <= 520:
            weight_score = 0.5  # やや懸念
        else:
            weight_score = 0.3  # 明らかに懸念
        
        # 体重変化スコア
        if -3 <= weight_change <= 5:
            change_score = 0.9  # 理想的な変化
        elif -8 <= weight_change < -3 or 5 < weight_change <= 10:
            change_score = 0.6  # 許容範囲
        else:
            change_score = 0.3  # 懸念される変化
        
        # 調教評価
        workout_evaluation = horse.get('workout_evaluation', 0.5)
        
        # 馬体診断（見た目の評価）
        appearance = horse.get('appearance', 0.5)
        
        # 総合的な馬体状態
        condition_score = (
            weight_score * 0.25 +
            change_score * 0.25 +
            workout_evaluation * 0.25 +
            appearance * 0.25
        )
        
        return max(0.1, min(1.0, condition_score))
    
    def _evaluate_form_cycle(self, horse: Dict, race_info: Dict) -> float:
        """調子サイクルの評価"""
        # 最近のレース結果からトレンドを分析
        recent_positions = horse.get('recent_positions', [])
        
        trend_score = 0.5  # デフォルト
        
        if len(recent_positions) >= 3:
            # 着順の変化傾向を分析
            trend = np.polyfit(range(len(recent_positions)), recent_positions, 1)[0]
            if trend < -0.5:  # 着順が上がっていく（数字が小さくなる）
                trend_score = 0.8  # 上昇傾向
            elif trend > 0.5:  # 着順が下がっていく
                trend_score = 0.3  # 下降傾向
            else:
                trend_score = 0.6  # 安定傾向
        
        # 休養後の初戦判定
        days_since_last_race = horse.get('days_since_last_race', 0)
        
        rest_factor = 0.5  # デフォルト
        # 初出走（データなし）は平均的評価
        if days_since_last_race == 0:
            rest_factor = 0.5
        # 休養明け（60日以上）
        elif days_since_last_race > 60:
            # 長期休養後は不安要素あり
            rest_factor = 0.4
        # 微妙な間隔（30-60日）
        elif 30 < days_since_last_race <= 60:
            rest_factor = 0.6
        # 適切な間隔（15-30日）
        elif 15 <= days_since_last_race <= 30:
            rest_factor = 0.8
        # 詰めた出走（14日以内）
        else:
            # 疲労懸念
            rest_factor = 0.5
        
        # 調教評価
        workout_evaluation = horse.get('workout_evaluation', 0.5)
        
        # 総合的な調子サイクル評価
        form_score = (
            trend_score * 0.4 +
            rest_factor * 0.3 +
            workout_evaluation * 0.3
        )
        
        return form_score
    
    def _evaluate_environmental_adaptation(self, horse: Dict, race_info: Dict) -> float:
        """環境適応性の評価"""
        # 馬場状態
        track_condition = race_info.get('normalized_condition', '良')
        
        # 馬場状態への適応度
        condition_aptitude = horse.get(f'{track_condition}_aptitude', 0.5)
        
        # 気象条件
        weather = race_info.get('weather', '晴')
        weather_aptitude = horse.get(f'{weather}_aptitude', 0.5)
        
        # 地方適性（関東/関西など）
        region = 'east' if race_info.get('track', '') in ['東京', '中山', '新潟', '福島', '札幌'] else 'west'
        region_aptitude = horse.get(f'{region}_aptitude', 0.5)
        
        # 総合環境適応性
        adaptation_score = (
            condition_aptitude * 0.5 +
            weather_aptitude * 0.2 +
            region_aptitude * 0.3
        )
        
        return max(0.1, min(1.0, adaptation_score))
    
    def _evaluate_psychological_state(self, horse: Dict, race_info: Dict) -> float:
        """精神状態の評価"""
        # 精神状態評価の代理変数
        psychological_score = 0.7  # デフォルト値
        
        # 前走の順位から精神状態を推測
        previous_race = horse.get('previous_races', [{}])[0] if 'previous_races' in horse else {}
        if previous_race:
            previous_position = previous_race.get('position', 0)
            if previous_position == 1:
                psychological_score += 0.2  # 前走勝利で自信
            elif previous_position <= 3:
                psychological_score += 0.1  # 前走好成績で状態良好
            elif previous_position >= 10:
                psychological_score -= 0.1  # 前走不調で注意
        
        return max(0.1, min(1.0, psychological_score))
    
    def _calculate_total_score(self, evaluations: Dict, race_info: Dict) -> float:
        """総合評価スコアの計算"""
        primary_scores = evaluations.get('primary', {})
        
        # 一次評価の重み付け合計
        weighted_sum = sum(
            score * self.evaluation_layers['primary'].get(factor, 0)
            for factor, score in primary_scores.items()
        )
        
        # レース特性に基づいた調整
        race_characteristics = race_info.get('race_characteristics', {})
        
        # 総合スコア（0-1スケール）
        return max(0.1, min(1.0, weighted_sum))
    
    def _add_relative_evaluation(self, horses: List[Dict], race_info: Dict) -> List[Dict]:
        """他の馬との相対的な評価情報を追加"""
        if not horses:
            return horses
        
        # 有効な馬数
        valid_horses = [h for h in horses if 'total_score' in h]
        if not valid_horses:
            return horses
        
        # スコアの抽出
        scores = np.array([h['total_score'] for h in valid_horses])
        
        # 統計値の計算
        mean_score = np.mean(scores)
        std_score = np.std(scores) if len(scores) > 1 else 1.0
        
        # 相対値の計算と追加
        for horse in horses:
            if 'total_score' in horse:
                # Z値（標準化スコア）
                z_score = (horse['total_score'] - mean_score) / max(0.1, std_score)
                
                # パーセンタイルランク
                percentile = sum(1 for s in scores if s <= horse['total_score']) / len(scores) * 100
                
                # 格付け（AAA, AA, A, BBB, BB, B, C）
                if z_score > 2.0:
                    rating = 'AAA'
                elif z_score > 1.5:
                    rating = 'AA'
                elif z_score > 0.5:
                    rating = 'A'
                elif z_score > -0.5:
                    rating = 'BBB'
                elif z_score > -1.5:
                    rating = 'BB'
                elif z_score > -2.0:
                    rating = 'B'
                else:
                    rating = 'C'
                
                # 相対評価を追加
                horse.update({
                    'relative': {
                        'z_score': z_score,
                        'percentile': percentile,
                        'rating': rating
                    }
                })
        
        return horses
    
    def _refine_evaluation_based_on_previous(self, horses: List[Dict], race_info: Dict) -> List[Dict]:
        """前の評価結果を利用した再評価"""
        refined_horses = []
        
        for horse in horses:
            # 基本情報をコピー
            refined_horse = horse.copy()
            
            # 評価の調整
            primary_evaluations = horse.get('primary', {}).copy()
            
            # 相対ランクに基づく調整
            relative_ranks = horse.get('relative_ranks', {})
            
            # 特定の条件に基づく調整
            # 例：特定の要素が群を抜いている場合は評価を上げる
            for factor in primary_evaluations.keys():
                percentile = relative_ranks.get(f'{factor}_percentile', 50)
                
                # 群を抜いて高い（上位10%以内）
                if percentile >= 90:
                    primary_evaluations[factor] = min(1.0, primary_evaluations[factor] * 1.1)
                # 極めて低い（下位10%以内）
                elif percentile <= 10:
                    primary_evaluations[factor] = max(0.1, primary_evaluations[factor] * 0.9)
            
            # 特定の相互関係に基づく調整
            # 例：コンディションと基礎能力のバランス
            base_ability = primary_evaluations.get('base_ability', 0.5)
            condition = primary_evaluations.get('condition_factors', 0.5)
            
            # 能力は高いがコンディションが悪い場合は能力評価を下げる
            if base_ability > 0.7 and condition < 0.4:
                primary_evaluations['base_ability'] = max(0.5, base_ability * 0.85)
            
            # コンディションが極めて良いが能力が低い場合はコンディション評価の影響を強める
            if condition > 0.8 and base_ability < 0.5:
                primary_evaluations['condition_factors'] = min(1.0, condition * 1.15)
            
            # 更新された評価を保存
            refined_horse['primary'] = primary_evaluations
            
            # 総合スコアの再計算
            total_score = self._calculate_total_score(
                {'primary': primary_evaluations}, race_info
            )
            refined_horse['total_score'] = min(100, total_score * 100)
            
            refined_horses.append(refined_horse)
        
        return refined_horses
    
    def _determine_rank(self, score: float) -> str:
        """能力スコアからランクを決定"""
        if score >= 85:
            return "S"  # 超一流
        elif score >= 75:
            return "A"  # 一流
        elif score >= 65:
            return "B"  # 準一流
        elif score >= 55:
            return "C"  # 平均以上
        elif score >= 45:
            return "D"  # 平均的
        else:
            return "E"  # 平均以下
    
    def _classify_horses(self, evaluated_horses: List[Dict]) -> Dict:
        """馬を本命馬/対抗馬/穴馬に分類"""
        if not evaluated_horses:
            return {'honmei': [], 'taikou': [], 'ana': []}
        
        # スコアで降順ソート
        sorted_horses = sorted(evaluated_horses, key=lambda x: -x.get('total_score', 0))
        
        # オッズ情報の取得（穴馬選定用）
        odds_info = [(i, horse.get('odds', 10.0)) for i, horse in enumerate(sorted_horses) if 'odds' in horse]
        odds_info.sort(key=lambda x: x[1])  # オッズで昇順ソート
        
        # 高評価馬から本命馬を選定（最大2頭）
        honmei_candidates = []
        for horse in sorted_horses[:3]:  # 上位3頭から検討
            score = horse.get('total_score', 0)
            if score >= 70:  # スコア70以上
                honmei_candidates.append(horse)
            if len(honmei_candidates) >= 2:
                break
        
        # 本命馬の調整（期待値が高い馬を優先）
        honmei = []
        for horse in honmei_candidates:
            odds = horse.get('odds', 10.0)
            score = horse.get('total_score', 0) / 100  # 0-1スケールに
            expected_value = score * odds
            
            if expected_value >= 1.0 or len(honmei) < 1:  # 期待値1.0以上または最低1頭は選択
                honmei.append(horse)
            if len(honmei) >= 2:
                break
        
        # 対抗馬の選定（本命馬に次ぐ評価で、異なる特性を持つ馬）
        # 本命馬以外の上位馬から選定
        taikou_candidates = []
        honmei_ids = [h['horse_number'] for h in honmei]
        
        for horse in sorted_horses:
            if horse['horse_number'] not in honmei_ids and len(taikou_candidates) < 2:
                score = horse.get('total_score', 0)
                if score >= 60:  # スコア60以上
                    taikou_candidates.append(horse)
        
        # 穴馬の選定（オッズが高く、かつある程度評価も高い馬）
        ana_candidates = []
        selected_ids = honmei_ids + [h['horse_number'] for h in taikou_candidates]
        
        # オッズが高い順に検討
        for horse_idx, odds in sorted(odds_info, key=lambda x: -x[1]):
            horse = sorted_horses[horse_idx]
            if horse['horse_number'] not in selected_ids and len(ana_candidates) < 2:
                score = horse.get('total_score', 0)
                if odds >= 10.0 and score >= 50:  # オッズ10倍以上、スコア50以上
                    ana_candidates.append(horse)
        
        return {
            'honmei': honmei,
            'taikou': taikou_candidates,
            'ana': ana_candidates
        }
    
    def _predict_race(self, horses: List[Dict], race_info: Dict) -> List[Dict]:
        """レース結果予測"""
        # 総合スコアでソート
        sorted_horses = sorted(
            horses, 
            key=lambda h: h.get('total_score', 0), 
            reverse=True
        )
        
        # 実際のオッズデータ取得を試みる
        real_odds = self._fetch_jra_odds(race_info)
        
        # オッズデータが取得できた場合は更新
        if real_odds:
            for horse in sorted_horses:
                horse_number = horse.get('horse_number')
                if horse_number in real_odds:
                    horse['odds'] = real_odds[horse_number]
                    
        # 勝率の計算
        horses_with_probs = self._calculate_win_probabilities(sorted_horses, race_info)
        
        # 期待値の計算と追加
        horses_with_ev = []
        for horse in horses_with_probs:
            horse_copy = horse.copy()
            win_prob = horse_copy.get('win_probability', 0)
            odds = horse_copy.get('odds', 0)
            expected_value = win_prob * odds
            horse_copy['expected_value'] = expected_value
            horses_with_ev.append(horse_copy)
        
        # 期待値でソート
        return sorted(horses_with_ev, key=lambda h: h.get('expected_value', 0), reverse=True)
    
    def _fetch_jra_odds(self, race_info: Dict) -> Dict:
        """JRA公式サイトからオッズ情報を取得する"""
        odds_dict = {}
        
        try:
            # レース情報から日付と開催場所、レース番号を取得
            race_date = race_info.get('date', '')
            track = race_info.get('track', '')
            race_number = race_info.get('race_number', '')
            
            # 日付をフォーマット (例: 20250328)
            formatted_date = ''
            if isinstance(race_date, str) and len(race_date) >= 10:
                # YYYY-MM-DD形式を想定
                formatted_date = race_date.replace('-', '')[:8]
            elif isinstance(race_date, datetime):
                formatted_date = race_date.strftime('%Y%m%d')
                
            # トラックコード取得
            track_code = self._get_jra_track_code(track)
            
            if formatted_date and track_code and race_number:
                # JRA公式サイトのオッズページURL構築
                url = f"https://www.jra.go.jp/JRADB/accessO.html?RACE_ID={formatted_date}{track_code}{race_number.zfill(2)}&rf=race_list&fb=1"
                
                # リクエスト送信
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                # HTMLパース
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # オッズテーブル取得 (単勝オッズ)
                odds_table = soup.select_one('table.oztan')
                if odds_table:
                    rows = odds_table.select('tr')[1:]  # ヘッダー行をスキップ
                    for row in rows:
                        cols = row.select('td')
                        if len(cols) >= 2:
                            try:
                                horse_number = int(cols[0].text.strip())
                                odds_text = cols[1].text.strip().replace(',', '')
                                odds = float(odds_text)
                                odds_dict[horse_number] = odds
                            except (ValueError, IndexError):
                                pass
            
            return odds_dict
                
        except Exception as e:
            print(f"オッズデータ取得エラー: {e}")
            return {}
    
    def _get_jra_track_code(self, track_name: str) -> str:
        """トラック名からJRAコードを取得する"""
        track_codes = {
            '札幌': '01', '函館': '02', '福島': '03', '新潟': '04', 
            '東京': '05', '中山': '06', '中京': '07', '京都': '08', 
            '阪神': '09', '小倉': '10'
        }
        
        for name, code in track_codes.items():
            if name in track_name:
                return code
        
        return ''
    
    def _calculate_win_probabilities(self, horses: List[Dict], race_info: Dict) -> List[Dict]:
        """勝率計算モデル（距離によらない統一モデル）"""
        # 総合スコアのリスト
        scores = [horse.get('total_score', 0) for horse in horses]
        
        # スコアの合計が0の場合の対策
        total_score = sum(scores)
        if total_score <= 0:
            total_score = len(horses)  # 各馬に等確率を割り当て
            scores = [1.0] * len(horses)
        
        # 指数関数的変換でスコアの差を強調
        exp_scores = [math.exp(score * 0.1) for score in scores]
        total_exp_score = sum(exp_scores)
        
        # 確率の正規化
        horses_with_probs = []
        for i, horse in enumerate(horses):
            horse_copy = horse.copy()
            win_prob = exp_scores[i] / total_exp_score
            horse_copy['win_probability'] = win_prob
            horses_with_probs.append(horse_copy)
        
        return horses_with_probs
    
    def _multi_layer_betting_optimization(self, predictions: List[Dict], 
                                           classified_horses: Dict, 
                                           race_info: Dict, 
                                           budget: int = 300) -> Dict:
        """多層的な馬券最適化処理"""
        # 本命馬・対抗馬・穴馬の取得
        honmei = classified_horses.get('honmei', [])
        taikou = classified_horses.get('taikou', [])
        ana = classified_horses.get('ana', [])
        
        # レース特性に基づく馬券戦略の選択
        race_chars = race_info.get('race_characteristics', {})
        upset_likelihood = race_chars.get('upset_likelihood', 0.5)
        
        # 馬券戦略の生成
        strategies = self._generate_betting_strategies(
            predictions, honmei, taikou, ana, race_info, budget
        )
        
        # レース特性に応じた最適戦略の選択
        selected_strategy = {}
        
        if upset_likelihood >= 0.7:
            # 波乱度が高い場合は穴馬重視または積極的戦略
            if ana:
                selected_strategy = strategies.get('longshot', {})
            else:
                selected_strategy = strategies.get('aggressive', {})
                
        elif 0.4 <= upset_likelihood < 0.7:
            # 中程度の波乱度ではバランス型かフォーメーション
            if len(honmei) >= 1 and (len(taikou) + len(ana)) >= 2:
                selected_strategy = strategies.get('formation', {})
            else:
                selected_strategy = strategies.get('balanced', {})
                
        else:
            # 波乱度が低い場合は堅実戦略
            selected_strategy = strategies.get('solid', {})
        
        # 最適化レポートの作成
        optimization_report = {
            'race_analysis': {
                'upset_likelihood': upset_likelihood,
                'selected_strategy_type': next((k for k, v in strategies.items() if v == selected_strategy), 'unknown')
            },
            'betting_plan': selected_strategy,
            'alternative_strategies': {k: v for k, v in strategies.items() if v != selected_strategy}
        }
        
        return optimization_report
    
    def _generate_betting_strategies(self, predictions: List[Dict], 
                                     honmei: List[Dict], 
                                     taikou: List[Dict], 
                                     ana: List[Dict], 
                                     race_info: Dict, 
                                     budget: int) -> Dict:
        """複数の馬券戦略を生成"""
        strategies = {}
        
        # 基本戦略
        strategies['solid'] = self._solid_betting_strategy(predictions, honmei, taikou, budget)
        strategies['balanced'] = self._balanced_betting_strategy(predictions, honmei, taikou, ana, budget)
        strategies['aggressive'] = self._aggressive_betting_strategy(predictions, honmei, taikou, ana, budget)
        
        # 応用戦略
        strategies['wide_coverage'] = self._wide_coverage_strategy(predictions, honmei, taikou, ana, budget)
        strategies['formation'] = self._formation_betting_strategy(predictions, honmei, taikou, ana, budget)
        strategies['box'] = self._box_betting_strategy(predictions, honmei, taikou, budget)
        
        # 特殊戦略
        if ana:  # 穴馬がある場合
            strategies['longshot'] = self._longshot_betting_strategy(predictions, honmei, ana, budget)
        
        if len(honmei) >= 2:  # 本命馬が複数いる場合
            strategies['multi_honmei'] = self._multi_honmei_strategy(predictions, honmei, taikou, budget)
        
        return strategies
    
    def _solid_betting_strategy(self, predictions: List[Dict], 
                                honmei: List[Dict], 
                                taikou: List[Dict], 
                                budget: int) -> Dict:
        """堅実な馬券戦略 - 本命馬中心"""
        bets = []
        remaining_budget = budget
        
        # 本命馬がいない場合は上位馬を本命とみなす
        if not honmei and predictions:
            honmei = [predictions[0]]
            if len(predictions) > 1:
                taikou = [predictions[1]]
        
        if not honmei:
            return {'type': 'solid', 'bets': []}
        
        # 単勝馬券は期待値が最大の馬を選択
        best_win_bet = None
        best_ev = 0
        
        # 本命馬と対抗馬の中から最も期待値の高い馬を選ぶ
        candidates = honmei + taikou
        
        for horse in candidates:
            win_odds = horse.get('odds', 3.0)
            win_prob = horse.get('win_probability', 0.3)
            expected_value = win_prob * win_odds
            
            if expected_value > best_ev:
                best_ev = expected_value
                best_win_bet = horse
        
        # 最適な単勝馬券を購入
        if best_win_bet and remaining_budget >= 100:
            best_horse_num = best_win_bet['horse_number']
            win_odds = best_win_bet.get('odds', 3.0)
            win_prob = best_win_bet.get('win_probability', 0.3)
            
            bets.append({
                'type': 'win',
                'horses': [best_horse_num],
                'odds': win_odds,
                'probability': win_prob,
                'expected_value': win_prob * win_odds,
                'amount': 100
            })
            remaining_budget -= 100
        
        # 対抗馬がいれば馬連
        if taikou and remaining_budget >= 100 and honmei:
            top_honmei = honmei[0]
            top_honmei_num = top_honmei['horse_number']
            
            for taikou_horse in taikou:
                taikou_num = taikou_horse['horse_number']
                
                # 馬連オッズと確率の推定
                win_odds = top_honmei.get('odds', 3.0)
                exacta_odds = max(2.0, (win_odds * taikou_horse.get('odds', 5.0)) / 3.0)
                exacta_prob = min(0.2, top_honmei.get('win_probability', 0.3) * taikou_horse.get('win_probability', 0.15) * 5)
                
                if remaining_budget >= 100:
                    bets.append({
                        'type': 'quinella',
                        'horses': [top_honmei_num, taikou_num],
                        'odds': exacta_odds,
                        'probability': exacta_prob,
                        'expected_value': exacta_prob * exacta_odds,
                        'amount': 100
                    })
                    remaining_budget -= 100
        
        # 2頭目の最適な単勝馬券を購入（最初に選んだ馬と異なる馬）
        if candidates and remaining_budget >= 100:
            second_best_win_bet = None
            second_best_ev = 0
            
            for horse in candidates:
                # 最初に選んだ馬はスキップ
                if best_win_bet and horse['horse_number'] == best_win_bet['horse_number']:
                    continue
                    
                win_odds = horse.get('odds', 3.0)
                win_prob = horse.get('win_probability', 0.3)
                expected_value = win_prob * win_odds
                
                if expected_value > second_best_ev:
                    second_best_ev = expected_value
                    second_best_win_bet = horse
            
            if second_best_win_bet:
                second_horse_num = second_best_win_bet['horse_number']
                second_win_odds = second_best_win_bet.get('odds', 5.0)
                second_win_prob = second_best_win_bet.get('win_probability', 0.2)
                
                bets.append({
                    'type': 'win',
                    'horses': [second_horse_num],
                    'odds': second_win_odds,
                    'probability': second_win_prob,
                    'expected_value': second_win_prob * second_win_odds,
                    'amount': 100
                })
                remaining_budget -= 100
        
        return {'type': 'solid', 'bets': bets}
    
    def _balanced_betting_strategy(self, predictions: List[Dict], 
                                   honmei: List[Dict], 
                                   taikou: List[Dict], 
                                   ana: List[Dict], 
                                   budget: int) -> Dict:
        """バランスの取れた馬券戦略 - 本命と対抗のバランス"""
        bets = []
        remaining_budget = budget
        
        # 本命馬がいない場合は上位馬を本命とみなす
        if not honmei and predictions:
            honmei = [predictions[0]]
            if len(predictions) > 1:
                taikou = [predictions[1]]
        
        if not honmei:
            return {'type': 'balanced', 'bets': []}
        
        # 本命馬
        honmei_nums = [h['horse_number'] for h in honmei]
        
        # 対抗馬
        taikou_nums = [t['horse_number'] for t in taikou]
        
        # 穴馬
        ana_nums = [a['horse_number'] for a in ana]
        
        # 本命馬の単勝または複勝
        if honmei and remaining_budget >= 100:
            top_honmei = honmei[0]
            top_honmei_num = top_honmei['horse_number']
            win_odds = top_honmei.get('odds', 3.0)
            
            if win_odds <= 3.0:  # オッズが低い場合は単勝
                bets.append({
                    'type': 'win',
                    'horses': [top_honmei_num],
                    'odds': win_odds,
                    'probability': top_honmei.get('win_probability', 0.3),
                    'expected_value': top_honmei.get('win_probability', 0.3) * win_odds,
                    'amount': 100
                })
            else:  # オッズが高い場合は複勝
                place_odds = max(1.1, win_odds / 2)
                place_prob = min(0.5, top_honmei.get('win_probability', 0.3) * 1.5)
                bets.append({
                    'type': 'place',
                    'horses': [top_honmei_num],
                    'odds': place_odds,
                    'probability': place_prob,
                    'expected_value': place_prob * place_odds,
                    'amount': 100
                })
            
            remaining_budget -= 100
        
        # 馬連（本命と対抗/穴）
        if honmei and (taikou or ana) and remaining_budget >= 100:
            top_honmei_num = honmei[0]['horse_number']
            target_nums = []
            if taikou:
                target_nums.append(taikou[0]['horse_number'])
            if ana:
                target_nums.append(ana[0]['horse_number'])
            
            for target_num in target_nums:
                if remaining_budget >= 100:
                    target_horse = next((h for h in predictions if h['horse_number'] == target_num), None)
                    if target_horse:
                        exacta_odds = max(2.0, (honmei[0].get('odds', 3.0) * target_horse.get('odds', 5.0)) / 3.0)
                        exacta_prob = min(0.2, honmei[0].get('win_probability', 0.3) * target_horse.get('win_probability', 0.15) * 5)
                        
                        bets.append({
                            'type': 'quinella',
                            'horses': [top_honmei_num, target_num],
                            'odds': exacta_odds,
                            'probability': exacta_prob,
                            'expected_value': exacta_prob * exacta_odds,
                            'amount': 100
                        })
                        remaining_budget -= 100
                        
                        if remaining_budget < 100:
                            break
        
        # 残りの予算で本命の複勝
        if honmei and remaining_budget >= 100:
            place_odds = max(1.1, honmei[0].get('odds', 3.0) / 2.5)
            place_prob = min(0.5, honmei[0].get('win_probability', 0.3) * 1.7)
            
            bets.append({
                'type': 'place',
                'horses': [honmei[0]['horse_number']],
                'odds': place_odds,
                'probability': place_prob,
                'expected_value': place_prob * place_odds,
                'amount': 100
            })
            remaining_budget -= 100
        
        return {'type': 'balanced', 'bets': bets}
    
    def _aggressive_betting_strategy(self, predictions: List[Dict], 
                                     honmei: List[Dict], 
                                     taikou: List[Dict], 
                                     ana: List[Dict], 
                                     budget: int) -> Dict:
        """積極的な馬券戦略 - 高配当を狙う"""
        bets = []
        remaining_budget = budget
        
        # 本命馬がいない場合は上位馬を本命とみなす
        if not honmei and predictions:
            honmei = [predictions[0]]
            if len(predictions) > 1:
                taikou = [predictions[1]]
        
        if not honmei:
            return {'type': 'aggressive', 'bets': []}
        
        # 本命馬
        honmei_nums = [h['horse_number'] for h in honmei]
        
        # 対抗馬
        taikou_nums = [t['horse_number'] for t in taikou]
        
        # 穴馬
        ana_nums = [a['horse_number'] for a in ana]
        
        # 三連複BOX（本命＋対抗＋穴）
        combination_horses = []
        if honmei:
            combination_horses.append(honmei[0]['horse_number'])
        if taikou:
            combination_horses.append(taikou[0]['horse_number'])
        if ana:
            combination_horses.append(ana[0]['horse_number'])
        
        if len(combination_horses) >= 3 and remaining_budget >= 100:
            # 三連複BOXのオッズと確率の推定
            trio_odds = 0
            trio_prob = 0
            
            horse1 = next((h for h in predictions if h['horse_number'] == combination_horses[0]), None)
            horse2 = next((h for h in predictions if h['horse_number'] == combination_horses[1]), None)
            horse3 = next((h for h in predictions if h['horse_number'] == combination_horses[2]), None)
            
            if horse1 and horse2 and horse3:
                odds_product = horse1.get('odds', 3.0) * horse2.get('odds', 5.0) * horse3.get('odds', 10.0)
                trio_odds = max(10.0, odds_product / 8.0)
                
                prob_product = horse1.get('win_probability', 0.3) * horse2.get('win_probability', 0.15) * horse3.get('win_probability', 0.1)
                trio_prob = min(0.05, prob_product * 25)
            else:
                trio_odds = 20.0  # デフォルト
                trio_prob = 0.03  # デフォルト
            
            bets.append({
                'type': 'trio',
                'horses': combination_horses[:3],
                'odds': trio_odds,
                'probability': trio_prob,
                'expected_value': trio_prob * trio_odds,
                'amount': 100
            })
            remaining_budget -= 100
        
        # 馬単（本命→対抗/穴）
        if honmei and (taikou or ana) and remaining_budget >= 100:
            top_honmei_num = honmei[0]['horse_number']
            target_nums = []
            if taikou:
                target_nums.append(taikou[0]['horse_number'])
            if ana:
                target_nums.append(ana[0]['horse_number'])
            
            for target_num in target_nums:
                if remaining_budget >= 100:
                    target_horse = next((h for h in predictions if h['horse_number'] == target_num), None)
                    if target_horse:
                        exacta_odds = max(4.0, (honmei[0].get('odds', 3.0) * target_horse.get('odds', 8.0)) * 0.7)
                        exacta_prob = min(0.1, honmei[0].get('win_probability', 0.3) * target_horse.get('win_probability', 0.1) * 3)
                        
                        bets.append({
                            'type': 'exacta',
                            'horses': [top_honmei_num, target_num],
                            'odds': exacta_odds,
                            'probability': exacta_prob,
                            'expected_value': exacta_prob * exacta_odds,
                            'amount': 100
                        })
                        remaining_budget -= 100
        
        # 残りの予算で本命の単勝
        if honmei and remaining_budget >= 100:
            bets.append({
                'type': 'win',
                'horses': [honmei[0]['horse_number']],
                'odds': honmei[0].get('odds', 3.0),
                'probability': honmei[0].get('win_probability', 0.3),
                'expected_value': honmei[0].get('win_probability', 0.3) * honmei[0].get('odds', 3.0),
                'amount': 100
            })
            remaining_budget -= 100
        
        return {'type': 'aggressive', 'bets': bets}
    
    def _wide_coverage_strategy(self, predictions: List[Dict], 
                                honmei: List[Dict], 
                                taikou: List[Dict], 
                                ana: List[Dict], 
                                budget: int) -> Dict:
        """幅広いカバレッジ戦略 - 複数的中を狙う"""
        bets = []
        remaining_budget = budget
        
        # 本命馬がいない場合は上位馬を本命とみなす
        if not honmei and predictions:
            honmei = [predictions[0]]
            if len(predictions) > 1:
                taikou = [predictions[1]]
        
        if not honmei or not taikou:
            return {'type': 'wide_coverage', 'bets': []}
        
        # 本命馬
        honmei_nums = [h['horse_number'] for h in honmei]
        
        # 対抗馬
        taikou_nums = [t['horse_number'] for t in taikou]
        
        # 穴馬
        ana_nums = [a['horse_number'] for a in ana]
        
        # ワイド馬券（本命と対抗/穴の組み合わせ）
        if honmei:
            top_honmei_num = honmei[0]['horse_number']
            target_nums = taikou_nums + ana_nums
            
            for target_num in target_nums:
                if remaining_budget >= 100:
                    target_horse = next((h for h in predictions if h['horse_number'] == target_num), None)
                    if target_horse:
                        wide_odds = max(1.5, (honmei[0].get('odds', 3.0) * target_horse.get('odds', 5.0)) / 5.0)
                        wide_prob = min(0.3, honmei[0].get('win_probability', 0.3) * target_horse.get('win_probability', 0.15) * 6)
                        
                        bets.append({
                            'type': 'wide',
                            'horses': [top_honmei_num, target_num],
                            'odds': wide_odds,
                            'probability': wide_prob,
                            'expected_value': wide_prob * wide_odds,
                            'amount': 100
                        })
                        remaining_budget -= 100
                        
                        if remaining_budget < 100:
                            break
        
        # 残りの予算で本命の複勝
        if honmei and remaining_budget >= 100:
            place_odds = max(1.1, honmei[0].get('odds', 3.0) / 2.5)
            place_prob = min(0.5, honmei[0].get('win_probability', 0.3) * 1.7)
            
            bets.append({
                'type': 'place',
                'horses': [honmei[0]['horse_number']],
                'odds': place_odds,
                'probability': place_prob,
                'expected_value': place_prob * place_odds,
                'amount': 100
            })
            remaining_budget -= 100
        
        return {'type': 'wide_coverage', 'bets': bets}
    
    def _formation_betting_strategy(self, predictions: List[Dict], 
                                   honmei: List[Dict], 
                                   taikou: List[Dict], 
                                   ana: List[Dict], 
                                   budget: int) -> Dict:
        """フォーメーション戦略 - 軸馬を中心とした組み合わせ"""
        bets = []
        remaining_budget = budget
        
        # 本命馬がいない場合は上位馬を本命とみなす
        if not honmei and predictions:
            honmei = [predictions[0]]
            if len(predictions) > 1:
                taikou = [predictions[1]]
                if len(predictions) > 2:
                    ana = [predictions[2]]
        
        if not honmei or (not taikou and not ana):
            return {'type': 'formation', 'bets': []}
        
        # 本命馬
        top_honmei = honmei[0]
        top_honmei_num = top_honmei['horse_number']
        
        # 対抗馬と穴馬の組み合わせ
        target_horses = []
        if taikou:
            target_horses.extend(taikou)
        if ana:
            target_horses.extend(ana)
        
        target_nums = [h['horse_number'] for h in target_horses]
        
        # 購入可能な馬券数を計算
        max_bets = min(len(target_nums), remaining_budget // 100)
        
        # 馬連フォーメーション
        if max_bets >= 2:
            formation_odds = []
            formation_probs = []
            
            for target_num in target_nums[:max_bets]:
                target_horse = next((h for h in predictions if h['horse_number'] == target_num), None)
                if target_horse:
                    odds = max(2.0, (top_honmei.get('odds', 3.0) * target_horse.get('odds', 5.0)) / 3.0)
                    prob = min(0.15, top_honmei.get('win_probability', 0.3) * target_horse.get('win_probability', 0.15) * 4)
                    
                    formation_odds.append(odds)
                    formation_probs.append(prob)
            
            # 平均オッズと確率
            avg_odds = sum(formation_odds) / len(formation_odds) if formation_odds else 5.0
            avg_prob = sum(formation_probs) / len(formation_probs) if formation_probs else 0.1
            
            bets.append({
                'type': 'quinella_formation',
                'horses': [top_honmei_num] + target_nums[:max_bets],
                'odds': avg_odds,
                'probability': avg_prob,
                'expected_value': avg_prob * avg_odds,
                'amount': max_bets * 100
            })
            remaining_budget -= max_bets * 100
        
        # 残りの予算で本命馬の単勝
        if remaining_budget >= 100:
            bets.append({
                'type': 'win',
                'horses': [top_honmei_num],
                'odds': top_honmei.get('odds', 3.0),
                'probability': top_honmei.get('win_probability', 0.3),
                'expected_value': top_honmei.get('win_probability', 0.3) * top_honmei.get('odds', 3.0),
                'amount': 100
            })
            remaining_budget -= 100
        
        return {'type': 'formation', 'bets': bets}
    
    def _box_betting_strategy(self, predictions: List[Dict], 
                             honmei: List[Dict], 
                             taikou: List[Dict], 
                             budget: int) -> Dict:
        """BOX買い戦略 - 複数の馬を対等に扱う"""
        bets = []
        remaining_budget = budget
        
        # 本命馬がいない場合は上位馬を本命とみなす
        if not honmei and predictions:
            honmei = [predictions[0]]
            if len(predictions) > 1:
                taikou = [predictions[1]]
                if len(predictions) > 2:
                    taikou.append(predictions[2])
        
        if not honmei or not taikou:
            return {'type': 'box', 'bets': []}
        
        # BOX対象の馬
        box_horses = []
        if honmei:
            box_horses.extend([h['horse_number'] for h in honmei])
        if taikou:
            box_horses.extend([t['horse_number'] for t in taikou])
        
        box_horses = box_horses[:3]
        
        if len(box_horses) < 2:
            return {'type': 'box', 'bets': []}
        
        # 馬連BOX
        if len(box_horses) >= 2:
            # 組み合わせ数
            combo_count = len(box_horses) * (len(box_horses) - 1) // 2
            bet_amount = combo_count * 100
            
            if bet_amount <= remaining_budget:
                # オッズと確率の推定
                box_odds = []
                box_probs = []
                
                for i in range(len(box_horses)):
                    for j in range(i+1, len(box_horses)):
                        horse1 = next((h for h in predictions if h['horse_number'] == box_horses[i]), None)
                        horse2 = next((h for h in predictions if h['horse_number'] == box_horses[j]), None)
                        
                        if horse1 and horse2:
                            odds = max(2.0, (horse1.get('odds', 3.0) * horse2.get('odds', 5.0)) / 3.0)
                            prob = min(0.15, horse1.get('win_probability', 0.2) * horse2.get('win_probability', 0.15) * 5)
                            
                            box_odds.append(odds)
                            box_probs.append(prob)
                
                # 平均オッズと確率
                avg_odds = sum(box_odds) / len(box_odds) if box_odds else 4.0
                avg_prob = sum(box_probs) / len(box_probs) if box_probs else 0.1
                
                bets.append({
                    'type': 'quinella',
                    'horses': box_horses,
                    'box': True,
                    'odds': avg_odds,
                    'probability': avg_prob,
                    'expected_value': avg_prob * avg_odds,
                    'amount': bet_amount
                })
                remaining_budget -= bet_amount
        
        # 残りの予算で単勝
        if honmei and remaining_budget >= 100:
            top_horse = sorted(honmei, key=lambda h: h.get('total_score', 0), reverse=True)[0]
            bets.append({
                'type': 'win',
                'horses': [top_horse['horse_number']],
                'odds': top_horse.get('odds', 3.0),
                'probability': top_horse.get('win_probability', 0.3),
                'expected_value': top_horse.get('win_probability', 0.3) * top_horse.get('odds', 3.0),
                'amount': 100
            })
            remaining_budget -= 100
        
        return {
            'strategy_name': 'BOX買い戦略',
            'description': '有力馬を対等に扱うBOX買い',
            'bets': bets,
            'total_amount': budget - remaining_budget
        }
    
    def _longshot_betting_strategy(self, predictions: List[Dict], 
                                  honmei: List[Dict], 
                                  ana: List[Dict], 
                                  budget: int) -> Dict:
        """穴馬を重視した戦略 - 大波乱を狙う"""
        bets = []
        remaining_budget = budget
        
        # 本命馬がいない場合は上位馬を本命とみなす
        if not honmei and predictions:
            honmei = [predictions[0]]
        
        if not honmei or not ana:
            return {'type': 'longshot', 'bets': []}
        
        # 穴馬の単勝
        for ana_horse in ana:
            if remaining_budget >= 100:
                ana_num = ana_horse['horse_number']
                win_odds = ana_horse.get('odds', 15.0)
                win_prob = ana_horse.get('win_probability', 0.05)
                
                bets.append({
                    'type': 'win',
                    'horses': [ana_num],
                    'odds': win_odds,
                    'probability': win_prob,
                    'expected_value': win_prob * win_odds,
                    'amount': 100
                })
                remaining_budget -= 100
        
        # 穴馬の複勝
        for ana_horse in ana:
            if remaining_budget >= 100:
                ana_num = ana_horse['horse_number']
                place_odds = max(1.5, ana_horse.get('odds', 15.0) / 3.0)
                place_prob = min(0.2, ana_horse.get('win_probability', 0.05) * 3)
                
                bets.append({
                    'type': 'place',
                    'horses': [ana_num],
                    'odds': place_odds,
                    'probability': place_prob,
                    'expected_value': place_prob * place_odds,
                    'amount': 100
                })
                remaining_budget -= 100
        
        # 本命馬と穴馬のワイド
        if honmei and ana and remaining_budget >= 100:
            top_honmei = honmei[0]
            top_honmei_num = top_honmei['horse_number']
            
            for ana_horse in ana:
                if remaining_budget >= 100:
                    ana_num = ana_horse['horse_number']
                    wide_odds = max(2.5, (top_honmei.get('odds', 3.0) * ana_horse.get('odds', 15.0)) / 8.0)
                    wide_prob = min(0.25, top_honmei.get('win_probability', 0.3) * ana_horse.get('win_probability', 0.05) * 10)
                    
                    bets.append({
                        'type': 'wide',
                        'horses': [top_honmei_num, ana_num],
                        'odds': wide_odds,
                        'probability': wide_prob,
                        'expected_value': wide_prob * wide_odds,
                        'amount': 100
                    })
                    remaining_budget -= 100
        
        return {'type': 'longshot', 'bets': bets}
    
    @property
    def betting_templates(self):
        """馬券テンプレートの遅延初期化"""
        if self._betting_templates_cache is None:
            self._betting_templates_cache = self._initialize_betting_templates()
        return self._betting_templates_cache
    
    def _initialize_betting_templates(self) -> Dict[str, Dict[str, Any]]:
        """馬券構成テンプレートの初期化"""
        # 最適化：直接辞書を返す
        return {
            # 本命中心（堅実型）
            'honmei_focus': {
                'description': '本命馬中心の堅実な馬券構成',
                'distribution': {
                    'win': 0.5,      # 単勝に50%
                    'quinella': 0.3, # 馬連に30%
                    'trio': 0.2      # 三連複に20%
                },
                'risk_level': 'low'
            },
            
            # バランス型
            'balanced': {
                'description': '本命と対抗をバランスよく組み合わせる',
                'distribution': {
                    'win': 0.3,      # 単勝に30%
                    'quinella': 0.4, # 馬連に40%
                    'trio': 0.3      # 三連複に30%
                },
                'risk_level': 'medium'
            },
            
            # 穴狙い型
            'longshot': {
                'description': '穴馬を絡めた高配当狙い',
                'distribution': {
                    'win': 0.1,        # 単勝に10%
                    'quinella': 0.3,   # 馬連に30%
                    'trio': 0.3,       # 三連複に30%
                    'trifecta': 0.3    # 三連単に30%
                },
                'risk_level': 'high'
            },
            
            # 幅広く買う型
            'wide_coverage': {
                'description': '様々な馬券種類に分散して幅広くカバー',
                'distribution': {
                    'win': 0.2,       # 単勝に20%
                    'place': 0.2,     # 複勝に20%
                    'quinella': 0.2,  # 馬連に20%
                    'wide': 0.2,      # ワイドに20%
                    'trio': 0.2       # 三連複に20%
                },
                'risk_level': 'medium'
            },
            
            # 三連単フォーメーション型
            'trifecta_formation': {
                'description': '本命を軸にした三連単フォーメーション',
                'distribution': {
                    'win': 0.2,                # 単勝に20%
                    'trifecta_formation': 0.8  # 三連単フォーメーションに80%
                },
                'risk_level': 'high'
            }
        }
    
def main():
    """高度競馬予測・馬券最適化統合システムのメイン実行関数"""
    import json
    import os
    import sys
    from datetime import datetime
    
    # Windows環境での文字化け対策
    try:
        import ctypes
        # Set console code page to UTF-8
        if sys.platform == 'win32':
            ctypes.windll.kernel32.SetConsoleCP(65001)
            ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    except Exception:
        # 無視して続行（一部環境ではうまく動作しない可能性）
        pass

    # システムのタイトルを表示
    print("\n" + "="*80)
    print("  高度競馬予測・馬券最適化統合システム (Advanced Recursive Racing Analysis System)")
    print("="*80 + "\n")
    
    # データ入力方法の選択
    print("データ入力方法を選択してください：")
    print("1. サンプルデータを使用")
    print("2. JSONファイルから読み込む")
    print("3. 手動でデータを入力")
    choice = input("\n選択 (1-3): ")
    
    # 馬データと競走情報を取得
    horses = []
    race_info = {}
    
    if choice == '1':
        # サンプルデータの使用
        print("\nサンプルデータを使用します...\n")
        horses = [
            {'horse_number': 1, 'horse_name': 'アタルサン', 'odds': 3.4, 'horse_age': 4, 'jockey': 'ルメール', 'weight': 450, 'weight_change': 2},
            {'horse_number': 2, 'horse_name': 'ウララ', 'odds': 7.8, 'horse_age': 3, 'jockey': '福永', 'weight': 458, 'weight_change': -3},
            {'horse_number': 3, 'horse_name': 'エイシンヒカリ', 'odds': 5.2, 'horse_age': 5, 'jockey': '川田', 'weight': 462, 'weight_change': 0},
            {'horse_number': 4, 'horse_name': 'オジュウチョウサン', 'odds': 12.5, 'horse_age': 6, 'jockey': '武豊', 'weight': 470, 'weight_change': -2},
            {'horse_number': 5, 'horse_name': 'キタサンブラック', 'odds': 4.1, 'horse_age': 5, 'jockey': '横山武', 'weight': 466, 'weight_change': 1},
            {'horse_number': 6, 'horse_name': 'クリソベリル', 'odds': 9.3, 'horse_age': 4, 'jockey': 'デムーロ', 'weight': 455, 'weight_change': -1},
            {'horse_number': 7, 'horse_name': 'コントレイル', 'odds': 2.8, 'horse_age': 3, 'jockey': '福永', 'weight': 454, 'weight_change': 3},
            {'horse_number': 8, 'horse_name': 'サリオス', 'odds': 6.7, 'horse_age': 3, 'jockey': '戸崎', 'weight': 452, 'weight_change': 2},
            {'horse_number': 9, 'horse_name': 'シャフリヤール', 'odds': 8.4, 'horse_age': 3, 'jockey': '岩田康', 'weight': 451, 'weight_change': 0},
            {'horse_number': 10, 'horse_name': 'ソダシ', 'odds': 15.7, 'horse_age': 3, 'jockey': '吉田隼', 'weight': 448, 'weight_change': -2},
        ]
        
        race_info = {
            'race_name': '東京優駿（日本ダービー）',
            'track': '東京',
            'surface': '芝',
            'distance': 2400,
            'track_condition': '良',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'class': 'G1',
            'grade': 'G1',
            'race_type': '一般',
            'age_restriction': '3歳'
        }
    
    elif choice == '2':
        # JSONファイルからの読み込み
        file_path = input("\nJSONファイルのパスを入力してください: ")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                horses = data.get('horses', [])
                race_info = data.get('race_info', {})
            print(f"\n{len(horses)}頭の馬データと競走情報を読み込みました。\n")
        except Exception as e:
            print(f"\nエラー: ファイルの読み込みに失敗しました。{e}")
            sys.exit(1)
    
    elif choice == '3':
        # 手動でのデータ入力
        print("\n競走情報を入力してください:")
        race_info = {
            'race_name': input("レース名: "),
            'track': input("競馬場: "),
            'surface': input("馬場の種類 (芝/ダート): "),
            'distance': int(input("距離 (m): ")),
            'track_condition': input("馬場状態 (良/稍重/重/不良): "),
            'grade': input("グレード (G1/G2/G3/OP/一般): "),
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        
        num_horses = int(input("\n出走馬の頭数: "))
        print("\n各馬のデータを入力してください:")
        
        for i in range(num_horses):
            print(f"\n--- 馬 {i+1} ---")
            horse = {
                'horse_number': int(input("馬番: ")),
                'horse_name': input("馬名: "),
                'odds': float(input("オッズ: ")),
                'horse_age': int(input("年齢: ")),
                'jockey': input("騎手名: "),
                'weight': int(input("馬体重 (kg): ")),
                'weight_change': int(input("体重増減 (kg): "))
            }
            horses.append(horse)
    
    else:
        print("\n無効な選択です。プログラムを終了します。")
        sys.exit(1)
    
    # 馬データが存在するか確認
    if not horses:
        print("\nエラー: 馬データがありません。プログラムを終了します。")
        sys.exit(1)
    
    # 分析の実行
    print("\n分析を実行しています...\n")
    system = AdvancedRacingSystem()
    result = system.analyze_race(horses, race_info)
    
    # 結果の表示
    display_results(result)
    
    # 結果の保存
    save_choice = input("\n結果をJSONファイルに保存しますか？ (y/n): ")
    if save_choice.lower() == 'y':
        # 保存先ディレクトリの作成
        output_dir = "race_analysis_results"
        os.makedirs(output_dir, exist_ok=True)
        
        # ファイル名の生成
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        race_name = race_info.get('race_name', '').replace(' ', '_')
        file_name = f"{output_dir}/{timestamp}_{race_name}.json"
        
        # 結果の保存
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n結果を {file_name} に保存しました。")
    
    print("\n分析を終了します。お疲れ様でした。")


def display_results(result: dict):
    """分析結果を表示する関数"""
    # レース情報の表示
    race_info = result.get('race_info', {})
    print(f"\n■ レース情報: {race_info.get('race_name', '不明')}")
    print(f"  競馬場: {race_info.get('track', '不明')} / {race_info.get('surface', '不明')} / {race_info.get('distance', '不明')}m")
    print(f"  馬場状態: {race_info.get('track_condition', '不明')}")
    print(f"  クラス: {race_info.get('grade', '不明')}")
    
    # レース特性の表示
    characteristics = race_info.get('race_characteristics', {})
    if characteristics:
        print("\n■ レース特性分析:")
        print(f"  波乱度: {characteristics.get('upset_likelihood', 0):.2f} (0-1)")
        print(f"  調子重要度: {characteristics.get('form_importance', 0):.2f} (0-1)")
        print(f"  ペース依存度: {characteristics.get('pace_dependency', 0):.2f} (0-1)")
        print(f"  クラス差: {characteristics.get('class_gap', 0):.2f} (0-1)")
    
    # 馬の分類を表示
    classified = result.get('classified_horses', {})
    if classified:
        print("\n■ 馬の分類:")
        
        # 本命馬の表示
        honmei = classified.get('honmei', [])
        if honmei:
            print("  【本命馬】")
            for horse in honmei:
                print(f"   {horse.get('horse_number', '?')}. {horse.get('horse_name', '不明')} " +
                      f"(オッズ:{horse.get('odds', '-'):.1f} / スコア:{horse.get('total_score', 0):.1f})")
        
        # 対抗馬の表示
        taikou = classified.get('taikou', [])
        if taikou:
            print("  【対抗馬】")
            for horse in taikou:
                print(f"   {horse.get('horse_number', '?')}. {horse.get('horse_name', '不明')} " +
                      f"(オッズ:{horse.get('odds', '-'):.1f} / スコア:{horse.get('total_score', 0):.1f})")
        
        # 穴馬の表示
        ana = classified.get('ana', [])
        if ana:
            print("  【穴馬】")
            for horse in ana:
                print(f"   {horse.get('horse_number', '?')}. {horse.get('horse_name', '不明')} " +
                      f"(オッズ:{horse.get('odds', '-'):.1f} / スコア:{horse.get('total_score', 0):.1f})")
    
    # 予測結果を表示
    predictions = result.get('predictions', [])
    if predictions:
        print("\n■ 予測順位:")
        for i, horse in enumerate(predictions[:5], 1):  # 上位5頭まで表示
            print(f"  {i}着: {horse.get('horse_number', '?')}. {horse.get('horse_name', '不明')} " +
                  f"(勝率:{horse.get('win_probability', 0):.1%})")
    
    # 馬券提案を表示
    betting_plan = result.get('betting_plan', {})
    if betting_plan:
        print("\n■ 馬券最適化プラン (予算:300円):")
        
        # 選択された戦略
        selected_strategy = betting_plan.get('selected_strategy', {})
        strategy_name = selected_strategy.get('strategy_name', '不明')
        print(f"  【推奨戦略】{strategy_name}")
        
        # 馬券内訳
        tickets = selected_strategy.get('tickets', [])
        if tickets:
            print("  【馬券内訳】")
            for ticket in tickets:
                bet_type = ticket.get('bet_type', '不明')
                horses_str = '-'.join(map(str, ticket.get('horses', [])))
                amount = ticket.get('amount', 0)
                expected_value = ticket.get('expected_value', 0)
                
                print(f"   {bet_type}: {horses_str} / {amount}円 (期待値:{expected_value:.2f})")
        
        # 総額
        total_amount = selected_strategy.get('total_amount', 0)
        total_expected_value = selected_strategy.get('total_expected_value', 0)
        print(f"  【総額】{total_amount}円 (総期待値:{total_expected_value:.2f})")


if __name__ == "__main__":
    main()
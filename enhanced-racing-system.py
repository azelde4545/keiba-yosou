# -*- coding: utf-8 -*-
"""
高度競馬予測システム (Advanced Recursive Racing Analysis System)
詳細な馬評価と競走特性分析による予測システム
"""

import numpy as np
from typing import List, Dict, Optional, Tuple, Callable, Any
from functools import lru_cache
import math
import json
import os
import sys
import time
import locale
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re
import random
import copy

# 日本語出力用のヘルパー関数
def print_jp(text):
    """日本語テキストを適切に出力するヘルパー関数"""
    # UTF-8でエンコードしてからデコード
    try:
        if isinstance(text, bytes):
            text = text.decode('utf-8')
        print(text)
        sys.stdout.flush()
    except Exception as e:
        print(f"Error printing text: {e}")

class AdvancedRacingSystem:
    """高度な再帰的競馬予測・馬券最適化統合システム"""
    
    def __init__(self):
        """初期化 - 評価レイヤー・パラメータの設定"""
        # 基本パラメータ
        self.max_recursion_depth = 2
        
        # 評価層の構造定義
        self.evaluation_layers = {
            'speed': {'win_rate': 0.3, 'recent_form': 0.3, 'speed': 0.4},
            'stamina': {'stamina': 0.5, 'adapt_distance': 0.5},
            'track_fit': {'adapt_track': 0.6, 'course_suitability': 0.4},
            'jockey': {'jockey_skill': 1.0},
            'race_style': {'race_style_match': 0.7, 'post_position': 0.3},
            'class': {'competing_level': 1.0}
        }
        
        # 各要素の重み付け
        self.factor_weights = {
            'speed': 0.30,
            'stamina': 0.25,
            'track_fit': 0.15,
            'jockey': 0.10,
            'race_style': 0.10,
            'class': 0.10
        }
        
        # 馬場状態調整係数
        self.track_adjustments = {
            '良': 1.0, '稍重': 0.98, '重': 0.96, '不良': 0.94
        }
        
        # レース特性解析用パラメーター
        self.race_characteristic_params = {
            'pace_dependency': 0.0,    # ペース依存度（0-1）
            'upset_likelihood': 0.0,   # 波乱度（0-1）
            'form_importance': 0.0,    # 調子重要度（0-1）
            'class_gap': 0.0           # クラス差（0-1）
        }
        
        # 再帰分析の深度制限
        self.max_recursion_depth = 1
        
        # キャッシュ用ディクショナリ
        self._cache = {}
    
    def analyze_race(self, horses: List[Dict], race_info: Optional[Dict] = None) -> Dict:
        """レース分析の実行 - 馬のデータとレース情報を受け取り、分析結果を返す"""
        if not horses:
            return {"error": "馬データがありません"}
        
        # 処理時間測定
        start_time = time.time()
        
        # レース情報の初期化
        if race_info is None:
            race_info = {}
        
        # レース情報の前処理
        processed_race_info = self._preprocess_race_info(race_info)
        
        # ハッシュ可能な形式へ変換 - horses_tupleを作成
        horses_tuple = tuple(self._make_horse_tuple(h) for h in horses)
        race_info_key = processed_race_info.get('_cache_key', tuple())
        
        # レース特性の分析
        race_characteristics = self._analyze_race_characteristics(horses_tuple, race_info_key)
        processed_race_info['race_characteristics'] = race_characteristics
        
        # 各馬の評価
        evaluated_horses = []
        for horse in horses:
            # ハッシュ可能なキーを作成
            horse_tuple = self._make_horse_tuple(horse)
            
            # 馬の評価
            evaluated_horse = self._evaluate_horse(horse_tuple, race_info_key)
            evaluated_horses.append(evaluated_horse)

        # 人気順でソート
        evaluated_horses.sort(key=lambda x: x.get('odds', float('inf')))
        for index, horse in enumerate(evaluated_horses):
            horse['popularity_rank'] = index + 1  # 1-based ranking
        
        # 馬群の分類 - 辞書のリストをタプルに変換
        evaluated_horses_tuple = self._convert_horses_to_tuples(evaluated_horses)
        classified_horses = self._classify_horses(evaluated_horses_tuple)
        
        # レース展開予測
        race_development = self._predict_race_development(evaluated_horses, processed_race_info)
        
        # 強化されたレース予測
        predictions = self._enhanced_race_prediction(evaluated_horses, processed_race_info)
        
        # 詳細な分析結果
        detailed_analysis = self._generate_detailed_analysis(evaluated_horses, processed_race_info)
        
        # 処理時間測定終了
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 結果をまとめる
        result = {
            'horses': evaluated_horses,
            'race_info': processed_race_info,
            'race_characteristics': race_characteristics,
            'classified_horses': classified_horses,
            'predictions': predictions,
            'race_development': race_development,
            'detailed_analysis': detailed_analysis,
            'execution_time': execution_time
        }
        
        return result
    
    def _make_horse_tuple(self, horse: Dict) -> Tuple:
        """馬の辞書をハッシュ可能なタプルに変換する"""
        result = []
        for k, v in sorted(horse.items()):
            if isinstance(v, dict):
                # 内部辞書を再帰的に処理
                v = self._dict_to_tuple(v)
            elif isinstance(v, list):
                # リストをタプルのリストに変換
                v = tuple(self._process_list_item(item) for item in v)
            result.append((k, v))
        return tuple(result)
    
    def _dict_to_tuple(self, d: Dict) -> Tuple:
        """辞書をタプルに再帰的に変換"""
        result = []
        for k, v in sorted(d.items()):
            if isinstance(v, dict):
                v = self._dict_to_tuple(v)
            elif isinstance(v, list):
                v = tuple(self._process_list_item(item) for item in v)
            result.append((k, v))
        return tuple(result)
    
    def _process_list_item(self, item):
        """リストのアイテムを再帰的に処理"""
        if isinstance(item, dict):
            return self._dict_to_tuple(item)
        elif isinstance(item, list):
            return tuple(self._process_list_item(i) for i in item)
        return item
    
    def _convert_horses_to_tuples(self, horses: List[Dict]) -> Tuple:
        """馬のリストをタプルに変換する"""
        return tuple(self._make_horse_tuple(h) for h in horses)
    
    def _preprocess_race_info(self, race_info: Dict) -> Dict:
        """レース情報の前処理"""
        # 深いコピーで元データを変更しないように
        processed_info = copy.deepcopy(race_info)
        
        # レース特性が無い場合は追加
        if 'race_characteristics' not in processed_info:
            processed_info['race_characteristics'] = {}
        
        # グレードの正規化
        if 'grade' in processed_info and 'normalized_grade' not in processed_info:
            grade = processed_info['grade']
            if 'G1' in grade or 'Ｇ１' in grade or '１' in grade and 'G' in grade:
                processed_info['normalized_grade'] = 'G1'
            elif 'G2' in grade or 'Ｇ２' in grade or '２' in grade and 'G' in grade:
                processed_info['normalized_grade'] = 'G2'
            elif 'G3' in grade or 'Ｇ３' in grade or '３' in grade and 'G' in grade:
                processed_info['normalized_grade'] = 'G3'
            elif 'OP' in grade or '特別' in grade:
                processed_info['normalized_grade'] = 'OP'
            else:
                processed_info['normalized_grade'] = '一般'
        
        # レース種別の判定
        if 'race_type' not in processed_info:
            race_name = processed_info.get('race_name', '')
            if '障害' in race_name:
                processed_info['race_type'] = '障害'
            else:
                processed_info['race_type'] = '平地'
        
        # lru_cacheのためにハッシュ可能なキーを作成
        # 辞書はそのままでは使えないので、ハッシュ可能な形式に変換
        processed_info['_cache_key'] = self._create_cache_key(processed_info)
        
        return processed_info
        
    def _create_cache_key(self, info_dict: Dict) -> Tuple:
        """辞書からハッシュ可能なキーを作成"""
        # レース特性は別途処理
        race_chars = info_dict.get('race_characteristics', {})
        
        # レース特性を除いた基本情報でタプルを作成
        base_info = []
        for k, v in sorted(info_dict.items()):
            if k != 'race_characteristics':
                if isinstance(v, (str, int, float, bool, type(None))):
                    base_info.append((k, v))
        
        # レース特性を処理
        race_chars_tuple = []
        for k, v in sorted(race_chars.items()):
            if isinstance(v, (str, int, float, bool, type(None))):
                race_chars_tuple.append((k, v))
        
        # 最終的なキーを作成
        return tuple(base_info), tuple(race_chars_tuple)
    
    @lru_cache(maxsize=16)
    def _analyze_race_characteristics(self, horses_tuple: Tuple, race_info_tuple: Tuple) -> Dict:
        """レース特性の詳細な分析"""
        # タプルからリスト/辞書へ変換（キャッシュのため）
        horses = list(horses_tuple)
        race_info = {}
        
        # base_infoとrace_chars_tupleに分割された形式から戻す
        base_info, race_chars_tuple = race_info_tuple
        
        for k, v in base_info:
            race_info[k] = v
            
        race_info['race_characteristics'] = {}
        for k, v in race_chars_tuple:
            race_info['race_characteristics'][k] = v
        
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
    
    @lru_cache(maxsize=128)
    def _evaluate_horse(self, horse_tuple: Tuple, race_info_tuple: Tuple) -> Dict:
        """馬の能力を評価"""
        # タプルから辞書に戻す
        horse = {}
        for key, value in horse_tuple:
            # タプルの形式をチェック
            if isinstance(value, tuple):
                # 安全に変換
                nested_dict = self._safe_tuple_to_dict(value)
                if nested_dict is not None:
                    horse[key] = nested_dict
                else:
                    horse[key] = value
            else:
                horse[key] = value
        
        # race_info_tupleからrace_infoを再構成
        race_info = {}
        base_info, race_chars_tuple = race_info_tuple
        
        for k, v in base_info:
            race_info[k] = v
            
        race_info['race_characteristics'] = {}
        for k, v in race_chars_tuple:
            race_info['race_characteristics'][k] = v
        
        # 基本情報のコピー
        evaluated_horse = horse.copy()
        
        # 各要素の多層評価 - ここでタプルに変換
        evaluations = self._multi_layer_horse_evaluation(horse_tuple, race_info_tuple)
        
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
        
        return evaluated_horse
    
    def _safe_tuple_to_dict(self, tup: Tuple) -> Optional[Dict]:
        """タプルを安全に辞書に変換する"""
        if not isinstance(tup, tuple):
            return None
            
        result = {}
        try:
            # キー・バリューのペアのタプルかチェック
            for item in tup:
                # すべてのアイテムがタプル、かつ長さが2であることを確認
                if not isinstance(item, tuple) or len(item) != 2:
                    # 条件を満たさない場合はNoneを返す
                    return None
                    
                k, v = item
                # 再帰的に処理
                if isinstance(v, tuple):
                    nested = self._safe_tuple_to_dict(v)
                    if nested is not None:
                        result[k] = nested
                    else:
                        result[k] = v
                else:
                    result[k] = v
            return result
        except (ValueError, TypeError):
            # いずれかのエラーが発生した場合もNoneを返す
            return None
            
    @lru_cache(maxsize=128)
    def _multi_layer_horse_evaluation(self, horse_tuple: Tuple, race_info_tuple: Tuple) -> Dict:
        """馬の多層的能力評価"""
        # タプルから辞書に戻す
        horse = {}
        for key, value in horse_tuple:
            # タプルの形式をチェック
            if isinstance(value, tuple):
                # 安全に変換
                nested_dict = self._safe_tuple_to_dict(value)
                if nested_dict is not None:
                    horse[key] = nested_dict
                else:
                    horse[key] = value
            else:
                horse[key] = value
                
        # race_info_tupleからrace_infoを再構成
        race_info = {}
        base_info, race_chars_tuple = race_info_tuple
        
        for k, v in base_info:
            race_info[k] = v
            
        race_info['race_characteristics'] = {}
        for k, v in race_chars_tuple:
            race_info['race_characteristics'][k] = v
            
        # 一次評価要素
        primary_evaluations = {}
        
        # 各一次評価要素について多層評価
        for prim_factor, secondary_factors in self.evaluation_layers.items():
            # 二次評価要素の集計
            secondary_evaluations = {}
            secondary_weights_sum = sum(secondary_factors.values())
            
            for sec_factor, sec_weight in secondary_factors.items():
                # 二次評価要素の計算
                secondary_evaluations[sec_factor] = self._evaluate_secondary_factor(
                    sec_factor, horse_tuple, race_info_tuple
                )
            
            # 一次評価の計算（二次評価の加重平均）
            weighted_sum = 0.0
            if secondary_weights_sum > 0:
                weighted_sum = sum(
                    sec_score * (sec_weight / secondary_weights_sum)
                    for sec_factor, sec_score in secondary_evaluations.items()
                    for sec_factor_name, sec_weight in secondary_factors.items()
                    if sec_factor == sec_factor_name
                )
            
            # 一次評価スコアを保存
            primary_evaluations[prim_factor] = weighted_sum
        
        # 全ての評価を一つの辞書にまとめる
        all_evaluations = primary_evaluations.copy()
        
        return all_evaluations
    
    @lru_cache(maxsize=256)
    def _evaluate_secondary_factor(self, factor: str, horse_tuple: Tuple, race_info_tuple: Tuple) -> float:
        """二次評価要素の評価"""
        # タプルから辞書に戻す
        horse = {}
        for key, value in horse_tuple:
            # タプルの形式をチェック
            if isinstance(value, tuple):
                # 安全に変換
                nested_dict = self._safe_tuple_to_dict(value)
                if nested_dict is not None:
                    horse[key] = nested_dict
                else:
                    horse[key] = value
            else:
                horse[key] = value
                
        # race_info_tupleからrace_infoを再構成
        race_info = {}
        base_info, race_chars_tuple = race_info_tuple
        
        for k, v in base_info:
            race_info[k] = v
            
        race_info['race_characteristics'] = {}
        for k, v in race_chars_tuple:
            race_info['race_characteristics'][k] = v
        
        # 要素ごとの評価関数をマッピング
        evaluation_functions = {
            'win_rate': self._evaluate_win_rate,
            'consistency': self._evaluate_consistency,
            'speed': self._evaluate_speed,
            'stamina': self._evaluate_stamina,
            'adapt_track': self._evaluate_track_adaptation,
            'adapt_distance': self._evaluate_distance_adaptation,
            'jockey_skill': self._evaluate_jockey,
            'recent_form': self._evaluate_recent_form,
            'race_style_match': self._evaluate_race_style_match,
            'weight_advantage': self._evaluate_weight_advantage,
            'post_position': self._evaluate_post_position,
            'competing_level': self._evaluate_competing_level,
            'course_suitability': self._evaluate_course_suitability
        }
        
        # 対応する評価関数が存在すれば実行、なければデフォルト値を返す
        if factor in evaluation_functions:
            return evaluation_functions[factor](horse, race_info)
        
        return 0.5  # デフォルト値（0-1の範囲の中間）
    
    def _evaluate_win_rate(self, horse: Dict, race_info: Dict) -> float:
        """勝率評価"""
        # 勝率の取得（デフォルト値は5%）
        win_rate = horse.get('win_rate', 0.05)
        
        # 直近の勝率と通算勝率の加重平均
        recent_win_rate = horse.get('recent_win_rate', win_rate)
        
        # 加重平均（直近の結果を重視）
        weighted_win_rate = (recent_win_rate * 0.6) + (win_rate * 0.4)
        
        # スコア化（0-1の範囲に収める, 30%以上なら満点）
        return min(1.0, weighted_win_rate / 0.3)
    
    def _evaluate_consistency(self, horse: Dict, race_info: Dict) -> float:
        """安定性評価"""
        # 着順バラつき（標準偏差）の取得
        position_variance = horse.get('position_variance', 5.0)
        
        # パフォーマンスの安定性（0-1、高いほど安定）
        performance_stability = horse.get('performance_stability', 0.5)
        
        # 加重平均（着順のバラつきを重視）
        # 着順バラつきは逆スコア化（小さいほど良い）
        variance_score = max(0, min(1, 1 - (position_variance / 10)))
        
        return (variance_score * 0.6) + (performance_stability * 0.4)
    
    def _evaluate_performance_level(self, horse: Dict, race_info: Dict) -> float:
        """パフォーマンスレベル評価"""
        # 過去の最高評価
        best_rating = horse.get('best_rating', 50)
        average_rating = horse.get('average_rating', 45)
        
        # レースのレベル
        race_grade = race_info.get('normalized_grade', '一般')
        
        # グレードごとの基準レーティング
        grade_ratings = {
            'G1': 110,
            'G2': 105,
            'G3': 100,
            'OP': 95,
            '特別': 90,
            '一般': 85
        }
        
        # レースの基準レーティング
        base_rating = grade_ratings.get(race_grade, 85)
        
        # 相対評価（馬の最高評価/レースの基準レーティング）
        relative_best = min(1.2, best_rating / base_rating)
        relative_avg = min(1.1, average_rating / base_rating)
        
        # 加重平均
        return max(0, min(1, (relative_best * 0.7) + (relative_avg * 0.3)))
    
    def _evaluate_class_record(self, horse: Dict, race_info: Dict) -> float:
        """クラス実績評価"""
        # 現クラスでの成績
        class_win_rate = horse.get('class_win_rate', 0)
        class_place_rate = horse.get('class_place_rate', 0)
        
        # 上のクラスでの経験
        higher_class_experience = horse.get('higher_class_experience', 0)
        
        # スコア計算（勝率30%以上またはクラス経験1.0以上で満点）
        win_score = min(1.0, class_win_rate / 0.3)
        place_score = min(1.0, class_place_rate / 0.5)
        exp_score = min(1.0, higher_class_experience)
        
        # 加重平均
        return (win_score * 0.5) + (place_score * 0.3) + (exp_score * 0.2)
    
    def _evaluate_distance_aptitude(self, horse: Dict, race_info: Dict) -> float:
        """距離適性評価"""
        # レース距離
        race_distance = race_info.get('distance', 1800)
        
        # 馬の最適距離
        optimal_distance = horse.get('optimal_distance', 1800)
        
        # 距離適性スコア
        if 'distance_aptitude' in horse:
            # 明示的な適性値がある場合
            return horse['distance_aptitude']
        
        # 最適距離との差（絶対値）
        distance_diff = abs(race_distance - optimal_distance)
        
        # 差が小さいほど高スコア（400m以内なら0.9以上）
        if distance_diff <= 200:
            return min(1.0, 0.95 + (200 - distance_diff) / 4000)
        elif distance_diff <= 400:
            return min(0.95, 0.9 + (400 - distance_diff) / 4000)
        else:
            # 差が大きいほどスコア減少（ただし下限0.3）
            return max(0.3, 0.9 - (distance_diff - 400) / 3000)
    
    def _evaluate_course_aptitude(self, horse: Dict, race_info: Dict) -> float:
        """コース適性評価"""
        # コース名
        course = race_info.get('course', '東京')
        
        # コース別成績
        course_records = horse.get('course_records', {})
        
        # 該当コースの成績
        course_record = course_records.get(course, {})
        
        # コースでの勝率・複勝率
        course_win_rate = course_record.get('win_rate', 0)
        course_place_rate = course_record.get('place_rate', 0)
        
        # 同様の特性を持つコースでの成績
        similar_courses = horse.get('similar_course_aptitude', 0.5)
        
        # スコア計算（コース勝率・複勝率が高いほど高スコア）
        win_score = min(1.0, course_win_rate / 0.3)
        place_score = min(1.0, course_place_rate / 0.5)
        
        # 実績がある場合は実績重視、ない場合は類似コース参照
        if course_win_rate > 0 or course_place_rate > 0:
            return (win_score * 0.6) + (place_score * 0.4)
        else:
            return similar_courses
    
    def _evaluate_race_style_match(self, horse: Dict, race_info: Dict) -> float:
        """レーススタイルとの適合性評価"""
        # 馬の走法
        running_style = horse.get('running_style', 'unknown')
        
        # レースの想定ペース
        expected_pace = race_info.get('race_characteristics', {}).get('expected_pace', 'medium')
        
        # 走法とペースの適合性マップ
        compatibility = {
            'front': {'slow': 0.9, 'medium': 0.7, 'fast': 0.4},  # 逃げ馬
            'stalker': {'slow': 0.8, 'medium': 0.8, 'fast': 0.6},  # 先行
            'mid': {'slow': 0.5, 'medium': 0.7, 'fast': 0.7},  # 中団
            'closer': {'slow': 0.3, 'medium': 0.6, 'fast': 0.9},  # 差し・追込
            'unknown': {'slow': 0.5, 'medium': 0.5, 'fast': 0.5}  # 不明
        }
        
        # 適合性スコアを取得
        style_match = compatibility.get(running_style, {}).get(expected_pace, 0.5)
        
        # レースの特性に合わせて調整
        race_characteristics = race_info.get('race_characteristics', {})
        
        # コーナーの数（直線の長さ）
        corners = race_characteristics.get('corners', 4)
        if corners < 4 and running_style == 'closer':
            # 直線が短いと差し馬不利
            style_match *= 0.8
        
        return style_match
    
    def _evaluate_jockey_synergy(self, horse: Dict, race_info: Dict) -> float:
        """騎手との相性評価"""
        # 騎手名
        jockey = horse.get('jockey', {}).get('name', '')
        
        # 馬と騎手の過去の成績
        synergy = horse.get('jockey_synergy', {}).get(jockey, 0.5)
        
        # 騎手の走法適性と馬の走法の一致度
        horse_style = horse.get('running_style', 'unknown')
        jockey_styles = horse.get('jockey', {}).get('style_aptitude', {})
        
        # 騎手の得意な走法との一致度
        style_match = jockey_styles.get(horse_style, 0.5)
        
        # 総合評価
        return (synergy * 0.7) + (style_match * 0.3)
    
    def _evaluate_physical_condition(self, horse: Dict, race_info: Dict) -> float:
        """馬体状態の評価"""
        # 馬体重の推移
        weight = horse.get('weight', 470)
        weight_diff = horse.get('weight_diff', 0)
        
        # 調教評価
        workout = horse.get('workout_evaluation', 0.5)
        
        # 馬体重の適正範囲（適正範囲内なら高評価）
        weight_score = 0.5
        if 440 <= weight <= 520:
            # 適正範囲内
            weight_score = 0.8
            
            # 変化量も評価
            if -5 <= weight_diff <= 3:
                # 適正変化量
                weight_score = 0.9
        elif weight < 440 and weight_diff > 0:
            # 軽すぎるが増加傾向
            weight_score = 0.6
        elif weight > 520 and weight_diff < 0:
            # 重すぎるが減少傾向
            weight_score = 0.6
        else:
            # それ以外は若干マイナス評価
            weight_score = 0.4
        
        # 総合評価
        return (weight_score * 0.5) + (workout * 0.5)
    
    def _evaluate_form_cycle(self, horse: Dict, race_info: Dict) -> float:
        """調子サイクルの評価"""
        # 休養日数
        days_since_last_race = horse.get('days_since_last_race', 0)
        
        # 馬の適正休養日数
        optimal_rest = horse.get('optimal_rest_period', 28)
        
        # 前走からの調子推移
        form_transition = horse.get('form_transition', 0.5)
        
        # 休養期間の評価
        rest_score = 0.5
        
        # 休養日数の適正範囲
        if days_since_last_race == 0:
            # 初出走
            rest_score = 0.5
        elif 0.7 * optimal_rest <= days_since_last_race <= 1.3 * optimal_rest:
            # 適正範囲内
            rest_score = 0.9
        elif days_since_last_race > 2 * optimal_rest:
            # 長すぎる休養
            rest_score = 0.3
        else:
            # それ以外
            rest_score = 0.6
        
        # 総合評価
        return (rest_score * 0.6) + (form_transition * 0.4)
    
    def _evaluate_environmental_adaptation(self, horse: Dict, race_info: Dict) -> float:
        """環境適応性の評価"""
        # レースの条件
        weather = race_info.get('weather', '晴')
        season = race_info.get('season', '春')
        
        # 馬の各条件への適応性
        weather_adaptation = horse.get('weather_adaptation', {}).get(weather, 0.5)
        season_adaptation = horse.get('season_adaptation', {}).get(season, 0.5)
        
        # 総合評価
        return (weather_adaptation * 0.5) + (season_adaptation * 0.5)
    
    def _evaluate_psychological_state(self, horse: Dict, race_info: Dict) -> float:
        """精神状態の評価"""
        # パドックでの様子
        paddock_state = horse.get('paddock_state', 0.5)
        
        # 気性の安定度
        temperament = horse.get('temperament', 0.5)
        
        # 成長度合い
        growth_stage = horse.get('growth_stage', 0.5)
        
        # 総合評価（パドックでの様子を重視）
        psychological_score = (paddock_state * 0.5) + (temperament * 0.3) + (growth_stage * 0.2)
        
        return max(0.1, min(1.0, psychological_score))
    
    def _evaluate_speed(self, horse: Dict, race_info: Dict) -> float:
        """馬のスピード評価"""
        # サンプルデータモードでは中程度の評価を返す
        return 0.5 + (random.random() * 0.3)
    
    def _evaluate_stamina(self, horse: Dict, race_info: Dict) -> float:
        """馬のスタミナ評価"""
        # サンプルデータモードでは中程度の評価を返す
        return 0.5 + (random.random() * 0.3)
    
    def _evaluate_track_adaptation(self, horse: Dict, race_info: Dict) -> float:
        """馬場適性の評価"""
        # サンプルデータモードでは中程度の評価を返す
        return 0.5 + (random.random() * 0.3)
    
    def _evaluate_distance_adaptation(self, horse: Dict, race_info: Dict) -> float:
        """距離適性の評価"""
        # サンプルデータモードでは中程度の評価を返す
        return 0.5 + (random.random() * 0.3)
    
    def _evaluate_jockey(self, horse: Dict, race_info: Dict) -> float:
        """騎手の評価"""
        # サンプルデータモードでは中程度の評価を返す
        return 0.5 + (random.random() * 0.3)
    
    def _evaluate_recent_form(self, horse: Dict, race_info: Dict) -> float:
        """最近の調子を評価"""
        # サンプルデータモードでは中程度の評価を返す
        return 0.5 + (random.random() * 0.3)
    
    def _evaluate_race_style_match(self, horse: Dict, race_info: Dict) -> float:
        """レース展開と馬の走法の相性を評価"""
        # サンプルデータモードでは中程度の評価を返す
        return 0.5 + (random.random() * 0.3)
    
    def _evaluate_weight_advantage(self, horse: Dict, race_info: Dict) -> float:
        """斤量のアドバンテージを評価"""
        # サンプルデータモードでは中程度の評価を返す
        return 0.5 + (random.random() * 0.3)
    
    def _evaluate_post_position(self, horse: Dict, race_info: Dict) -> float:
        """枠順の有利さを評価"""
        # サンプルデータモードでは中程度の評価を返す
        return 0.5 + (random.random() * 0.3)
    
    def _evaluate_competing_level(self, horse: Dict, race_info: Dict) -> float:
        """馬のクラスとレースレベルの適合性を評価"""
        # サンプルデータモードでは中程度の評価を返す
        return 0.5 + (random.random() * 0.3)
    
    def _evaluate_course_suitability(self, horse: Dict, race_info: Dict) -> float:
        """コース適性の評価"""
        # サンプルデータモードでは中程度の評価を返す
        return 0.5 + (random.random() * 0.3)
    
    def _calculate_total_score(self, evaluations: Dict, race_info: Dict) -> float:
        """総合評価スコアの計算"""
        total_score = 0.0
        weights_sum = 0.0
        
        # 各一次要素の重み付け加算
        for factor, weight in self.factor_weights.items():
            if factor in evaluations:
                total_score += evaluations[factor] * weight
                weights_sum += weight
        
        # 正規化
        if weights_sum > 0:
            total_score /= weights_sum
        
        return total_score
    
    def _add_relative_evaluation(self, horses: List[Dict], race_info: Dict) -> List[Dict]:
        """他の馬との相対的な評価情報を追加 - NumPyベクトル化による最適化版"""
        if not horses or len(horses) < 2:
            return horses
        
        # 評価項目と各馬のスコアを抽出
        primary_factors = self.evaluation_layers.keys()
        
        # NumPy配列を使用した高速化
        total_scores = np.array([horse.get('total_score', 0) for horse in horses])
        
        # 統計値の計算
        mean_score = np.mean(total_scores)
        std_score = np.std(total_scores)
        
        # 全ての評価を一括で処理
        for horse in horses:
            # 相対評価情報の初期化
            horse['relative_ranks'] = {}
            
            # 各要素のパーセンタイルランクを計算
            for factor in primary_factors:
                value = horse.get('primary', {}).get(factor, 0.5)
                percentile = np.sum(total_scores <= value) / len(total_scores) * 100
                horse['relative_ranks'][f'{factor}_percentile'] = percentile
            
            # スコアのZ値（標準化スコア）
            z_score = (horse['total_score'] - mean_score) / max(0.1, std_score)
            
            # パーセンタイルランク
            percentile = np.sum(total_scores <= horse['total_score']) / len(total_scores) * 100
            
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
    
    @lru_cache(maxsize=32)
    def _classify_horses(self, horses_tuple: Tuple) -> Dict:
        """馬の分類（本命馬/対抗馬/穴馬）"""
        # タプルからリストに戻す
        evaluated_horses = []
        for horse_tuple in horses_tuple:
            horse_dict = {}
            for key, value in horse_tuple:
                # タプルの形式をチェック
                if isinstance(value, tuple):
                    # 安全に変換
                    nested_dict = self._safe_tuple_to_dict(value)
                    if nested_dict is not None:
                        horse_dict[key] = nested_dict
                    else:
                        horse_dict[key] = value
                else:
                    horse_dict[key] = value
            evaluated_horses.append(horse_dict)
            
        if not evaluated_horses:
            return {'honmei': [], 'taikou': [], 'ana': []}
        
        # スコアで降順ソート（一度だけソート処理を実行）
        sorted_horses = sorted(
            evaluated_horses, 
            key=lambda h: h.get('total_score', 0), 
            reverse=True
        )
        
        # NumPy配列を使用した高速化
        scores = np.array([horse.get('total_score', 0) for horse in sorted_horses])
        
        # スコア閾値の設定
        max_score = np.max(scores) if len(scores) > 0 else 0
        honmei_threshold = max_score * 0.9  # 90%以上で本命
        taikou_threshold = max_score * 0.8  # 80%以上で対抗
        ana_threshold = max_score * 0.7    # 70%以上で穴
        
        # 高オッズ（穴馬）の閾値
        high_odds_threshold = np.median([horse.get('odds', 10.0) for horse in sorted_horses]) * 1.5 if len(sorted_horses) > 0 else 10.0
        
        # 各カテゴリーに馬を分類
        honmei = []
        taikou = []
        ana = []
        
        for horse in sorted_horses:
            score = horse.get('total_score', 0)
            horse_odds = horse.get('odds', 10.0)
            
            if score >= honmei_threshold:
                honmei.append(horse)
            elif score >= taikou_threshold:
                taikou.append(horse)
            elif score >= ana_threshold and horse_odds >= high_odds_threshold:
                ana.append(horse)
            elif len(ana) < 1 and score >= max_score * 0.6:  # 最低1頭は穴馬として提案
                ana.append(horse)
        
        # 各カテゴリーの上限設定
        honmei = honmei[:2]  # 最大2頭
        taikou = taikou[:3]  # 最大3頭
        ana = ana[:2]        # 最大2頭
        
        return {
            'honmei': honmei,
            'taikou': taikou,
            'ana': ana
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
    
    def _enhanced_race_prediction(self, horses: List[Dict], race_info: Dict) -> List[Dict]:
        """強化したレース結果予測"""
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
        
        # レース展開を予測
        race_development = self._predict_race_development(sorted_horses, race_info)
        
        # レース展開に基づく調整
        development_type = race_development.get('development', 'mid')
        for horse in sorted_horses:
            running_style = horse.get('running_style', 'unknown')
            
            # レース展開による馬の評価補正
            if development_type == 'fast':
                # 先行有利の場合
                if running_style == 'front':
                    horse['development_bonus'] = 1.15  # 逃げ馬に15%ボーナス
                elif running_style == 'stalker':
                    horse['development_bonus'] = 1.10  # 先行馬に10%ボーナス
                elif running_style == 'mid':
                    horse['development_bonus'] = 0.95  # 中団に5%ペナルティ
                else:  # closer
                    horse['development_bonus'] = 0.85  # 差し馬に15%ペナルティ
            elif development_type == 'slow':
                # 差し有利の場合
                if running_style == 'closer':
                    horse['development_bonus'] = 1.15  # 差し馬に15%ボーナス
                elif running_style == 'mid':
                    horse['development_bonus'] = 1.10  # 中団に10%ボーナス
                elif running_style == 'stalker':
                    horse['development_bonus'] = 0.95  # 先行馬に5%ペナルティ
                else:  # front
                    horse['development_bonus'] = 0.85  # 逃げ馬に15%ペナルティ
            else:  # mid
                # バランス展開の場合
                if running_style == 'mid':
                    horse['development_bonus'] = 1.10  # 中団に10%ボーナス
                elif running_style in ['stalker', 'closer']:
                    horse['development_bonus'] = 1.05  # 先行・差しに5%ボーナス
                else:
                    horse['development_bonus'] = 0.95  # 逃げに5%ペナルティ
            
            # スコアの調整
            development_bonus = horse.get('development_bonus', 1.0)
            horse['adjusted_score'] = horse.get('total_score', 0) * development_bonus
            
            # 勝率の再計算
            adjusted_scores = np.array([h.get('adjusted_score', 0) for h in sorted_horses])
            total_adjusted = np.sum(adjusted_scores)
            if total_adjusted > 0:
                horse['win_probability'] = horse.get('adjusted_score', 0) / total_adjusted
            else:
                horse['win_probability'] = 1.0 / len(sorted_horses)
            
            # 期待値の計算
            horse['expected_value'] = horse.get('win_probability', 0) * horse.get('odds', 0)
        
        # 調整後のスコアで再ソート
        return sorted(sorted_horses, key=lambda h: h.get('adjusted_score', 0), reverse=True)
    
    def _predict_race_development(self, horses: List[Dict], race_info: Dict) -> Dict:
        """レース展開予測"""
        # レース特性の分析
        race_characteristics = race_info.get('race_characteristics', {})
        
        # ペース依存度に基づく展開予測
        pace_dependency = race_characteristics.get('pace_dependency', 0.5)
        
        if pace_dependency >= 0.7:
            # ペース依存度が高い場合は先行有利
            development = 'fast'
            development_explanation = '先行馬が有利な展開が予想されます。'
        elif pace_dependency >= 0.4:
            # ペース依存度が中程度の場合は中団有利
            development = 'mid'
            development_explanation = '中団馬が有利な展開が予想されます。'
        else:
            # ペース依存度が低い場合は差し有利
            development = 'slow'
            development_explanation = '差し馬が有利な展開が予想されます。'
        
        return {
            'development': development,
            'explanation': development_explanation
        }
    
    def _evaluate_horses_with_development(self, horses: List[Dict], race_development: Dict) -> List[Dict]:
        """レース展開に基づく馬の評価"""
        development = race_development.get('development', 'mid')
        
        for horse in horses:
            # レース展開に基づく評価
            if development == 'fast':
                # 先行有利の場合は先行馬を高く評価
                if horse.get('running_style', 'unknown') == 'front':
                    horse['development_score'] = 1.2
                elif horse.get('running_style', 'unknown') == 'stalker':
                    horse['development_score'] = 1.0
                else:
                    horse['development_score'] = 0.8
            elif development == 'mid':
                # 中団有利の場合は中団馬を高く評価
                if horse.get('running_style', 'unknown') == 'mid':
                    horse['development_score'] = 1.1
                elif horse.get('running_style', 'unknown') == 'stalker':
                    horse['development_score'] = 1.0
                else:
                    horse['development_score'] = 0.9
            else:
                # 差し有利の場合は差し馬を高く評価
                if horse.get('running_style', 'unknown') == 'closer':
                    horse['development_score'] = 1.2
                elif horse.get('running_style', 'unknown') == 'mid':
                    horse['development_score'] = 1.0
                else:
                    horse['development_score'] = 0.8
        
        return horses
    
    def _generate_detailed_analysis(self, horses: List[Dict], race_info: Dict) -> Dict:
        """詳細な分析結果の生成"""
        # レース特性の分析
        race_characteristics = race_info.get('race_characteristics', {})
        
        # 馬の評価
        horse_evaluations = {}
        for horse in horses:
            horse_evaluations[horse.get('horse_number', 0)] = horse.get('evaluation_details', {})
        
        # 詳細な分析結果
        detailed_analysis = {
            'race_characteristics': race_characteristics,
            'horse_evaluations': horse_evaluations
        }
        
        return detailed_analysis
    
    def _determine_rank(self, score: float) -> str:
        """スコアに基づいてランクを決定する"""
        if score >= 90:
            return 'S'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B'
        elif score >= 60:
            return 'C'
        elif score >= 50:
            return 'D'
        else:
            return 'E'
    
    def _fetch_jra_odds(self, race_info: Dict) -> Dict:
        """JRAからオッズ情報を取得（サンプルデータモードではダミーデータを返す）"""
        # サンプルデータモードでは、スコアに基づいて生成されたオッズを返す
        return {
            'win_odds': {},  # 馬番:オッズのマップ
            'place_odds': {},
            'quinella_odds': {},
            'exacta_odds': {},
            'trio_odds': {}
        }
    
def main():
    """高度競馬予測統合システムのメイン実行関数"""
    import json
    import os
    import sys
    import time
    import locale
    from datetime import datetime
    
    # ターミナルの文字コードを設定
    if sys.platform == 'win32':
        import ctypes
        # UTF-8モードを有効化
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleCP(65001)
        kernel32.SetConsoleOutputCP(65001)
    
    # ロケールを設定
    try:
        locale.setlocale(locale.LC_ALL, 'ja_JP.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'Japanese_Japan.932')
        except locale.Error:
            pass
    
    # システムヘッダーを表示
    print_jp("=" * 80)
    print_jp("  高度競馬予測システム (Advanced Recursive Racing Analysis System)")
    print_jp("=" * 80)
    print_jp("")
    
    # システムの初期化
    system = AdvancedRacingSystem()
    
    # 処理時間測定用
    start_time = time.time()
    
    # 最終更新時間を取得
    last_updated = datetime.fromtimestamp(os.path.getmtime(__file__)).strftime('%Y-%m-%d %H:%M:%S')
    
    # システムバージョン
    version = "1.3.0"

    # システムのタイトルを表示
    print_jp("\n" + "="*80)
    print_jp("  高度競馬予測システム (Advanced Recursive Racing Analysis System)")
    print_jp("="*80 + "\n")
    
    # テスト用サンプルデータを使用
    use_sample_data = True
    
    if use_sample_data:
        print_jp("サンプルデータを使用した分析を開始します...\n")
        
        # サンプルレース情報
        race_info = {
            'race_name': '東京優駿（日本ダービー）',
            'track': '東京',
            'surface': '芝',
            'distance': 2400,
            'track_condition': '良',
            'grade': 'G1',
            'normalized_grade': 'G1',
            'race_characteristics': {
                'upset_likelihood': 0.3,  # 波乱度（低め）
                'form_importance': 0.8,   # 調子重要度（高め）
                'pace_dependency': 0.5,   # ペース依存度（中程度）
                'class_gap': 0.7          # クラス差（大きめ）
            }
        }
        
        # サンプル馬データ
        horses = [
            {
                'horse_number': 1, 
                'horse_name': 'イクイノックス', 
                'odds': 2.7, 
                'horse_age': 3, 
                'jockey': 'C.ルメール', 
                'weight': 465, 
                'weight_change': 1,
                'running_style': 'stalker',
                'past_performances': [
                    {'race_name': '皐月賞', 'result': 1, 'surface': '芝', 'distance': 2000},
                    {'race_name': '弥生賞', 'result': 1, 'surface': '芝', 'distance': 2000}
                ]
            },
            {
                'horse_number': 2, 
                'horse_name': 'ドウデュース', 
                'odds': 3.2, 
                'horse_age': 3, 
                'jockey': '戸崎圭太', 
                'weight': 472, 
                'weight_change': -2,
                'running_style': 'mid',
                'past_performances': [
                    {'race_name': '2000ギニー', 'result': 1, 'surface': '芝', 'distance': 1600},
                    {'race_name': '朝日杯FS', 'result': 2, 'surface': '芝', 'distance': 1600}
                ]
            },
            {
                'horse_number': 3, 
                'horse_name': 'アスクビクターモア', 
                'odds': 12.1, 
                'horse_age': 3, 
                'jockey': '福永祐一', 
                'weight': 456, 
                'weight_change': 3,
                'running_style': 'front',
                'past_performances': [
                    {'race_name': '青葉賞', 'result': 1, 'surface': '芝', 'distance': 2400},
                    {'race_name': '共同通信杯', 'result': 5, 'surface': '芝', 'distance': 1800}
                ]
            },
            {
                'horse_number': 4, 
                'horse_name': 'キングオブドラゴン', 
                'odds': 18.4, 
                'horse_age': 3, 
                'jockey': '川田将雅', 
                'weight': 468, 
                'weight_change': 0,
                'running_style': 'closer',
                'past_performances': [
                    {'race_name': '京都新聞杯', 'result': 2, 'surface': '芝', 'distance': 2200},
                    {'race_name': '毎日杯', 'result': 3, 'surface': '芝', 'distance': 1800}
                ]
            },
            {
                'horse_number': 5, 
                'horse_name': 'ジオグリフ', 
                'odds': 7.2, 
                'horse_age': 3, 
                'jockey': '横山武史', 
                'weight': 470, 
                'weight_change': -1,
                'running_style': 'mid',
                'past_performances': [
                    {'race_name': '皐月賞', 'result': 2, 'surface': '芝', 'distance': 2000},
                    {'race_name': '共同通信杯', 'result': 1, 'surface': '芝', 'distance': 1800}
                ]
            }
        ]
        
        # 分析実行
        try:
            result = system.analyze_race(horses, race_info)
            
            # 結果表示
            display_results(result)
            
            # 分析時間を表示
            end_time = time.time()
            print_jp(f"\n実行時間: {end_time - start_time:.2f}秒")
            
            print_jp("\nサンプルデータによる分析が完了しました。")
        except Exception as e:
            print_jp(f"エラーが発生しました: {str(e)}")
            import traceback
            traceback.print_exc()
        return

def display_results(result: dict):
    """分析結果を表示する関数"""
    # レース情報の表示
    race_info = result.get('race_info', {})
    print_jp(f"\n■ レース情報: {race_info.get('race_name', '不明')}")
    print_jp(f"  競馬場: {race_info.get('track', '不明')} / {race_info.get('surface', '不明')} / {race_info.get('distance', '不明')}m")
    print_jp(f"  馬場状態: {race_info.get('track_condition', '不明')}")
    print_jp(f"  クラス: {race_info.get('grade', '不明')}")
    
    # レース特性の表示
    characteristics = race_info.get('race_characteristics', {})
    if characteristics:
        print_jp("\n■ レース特性分析:")
        print_jp(f"  波乱度: {characteristics.get('upset_likelihood', 0):.2f} (0-1)")
        print_jp(f"  調子重要度: {characteristics.get('form_importance', 0):.2f} (0-1)")
        print_jp(f"  ペース依存度: {characteristics.get('pace_dependency', 0):.2f} (0-1)")
        print_jp(f"  クラス差: {characteristics.get('class_gap', 0):.2f} (0-1)")
    
    # 馬の分類を表示
    classified = result.get('classified_horses', {})
    if classified:
        print_jp("\n■ 馬の分類:")
        
        # 本命馬の表示
        honmei = classified.get('honmei', [])
        if honmei:
            print_jp("  【本命馬】")
            for horse in honmei:
                print_jp(f"   {horse.get('horse_number', '?')}. {horse.get('horse_name', '不明')} " +
                      f"(オッズ:{horse.get('odds', '-'):.1f} / スコア:{horse.get('adjusted_score', horse.get('total_score', 0)):.1f})")
        
        # 対抗馬の表示
        taikou = classified.get('taikou', [])
        if taikou:
            print_jp("  【対抗馬】")
            for horse in taikou:
                print_jp(f"   {horse.get('horse_number', '?')}. {horse.get('horse_name', '不明')} " +
                      f"(オッズ:{horse.get('odds', '-'):.1f} / スコア:{horse.get('adjusted_score', horse.get('total_score', 0)):.1f})")
        
        # 穴馬の表示
        ana = classified.get('ana', [])
        if ana:
            print_jp("  【穴馬】")
            for horse in ana:
                print_jp(f"   {horse.get('horse_number', '?')}. {horse.get('horse_name', '不明')} " +
                      f"(オッズ:{horse.get('odds', '-'):.1f} / スコア:{horse.get('adjusted_score', horse.get('total_score', 0)):.1f})")
    
    # 予測結果を表示
    predictions = result.get('predictions', [])
    if predictions:
        print_jp("\n■ 予測順位:")
        for i, horse in enumerate(predictions[:5], 1):  # 上位5頭まで表示
            print_jp(f"  {i}着: {horse.get('horse_number', '?')}. {horse.get('horse_name', '不明')} " +
                  f"(勝率:{horse.get('win_probability', 0):.1%})")
    
    # レース展開予測を表示
    race_development = result.get('race_development', {})
    if race_development:
        print_jp("\n■ レース展開予測:")
        development_type = race_development.get('development', '不明')
        
        # 展開タイプの日本語表示
        development_japanese = {
            'fast': 'ハイペース',
            'mid': '平均ペース',
            'slow': 'スローペース',
            '不明': '不明'
        }
        
        print_jp(f"  予測展開: {development_japanese.get(development_type, '不明')}")
        print_jp(f"  詳細: {race_development.get('explanation', '情報なし')}")
        print_jp(f"  上がり: {race_development.get('closing_explanation', '情報なし')}")
    
    # レースパターン分析を表示
    detailed_analysis = result.get('detailed_analysis', {})
    if detailed_analysis:
        pattern_analysis = detailed_analysis.get('pattern_analysis', {})
        if pattern_analysis:
            print_jp("\n■ レースパターン分析:")
            print_jp(f"  パターン: {pattern_analysis.get('race_pattern', '不明')}")
            print_jp(f"  説明: {pattern_analysis.get('pattern_explanation', '情報なし')}")
    
    # 各馬の詳細分析表示
    horse_evaluations = detailed_analysis.get('horse_evaluations', {})
    if horse_evaluations and result.get('horses'):
        print_jp("\n■ 詳細分析（主要な馬）:")
        
        # 対象馬を抽出（本命馬と対抗馬）
        target_horses = []
        honmei = classified.get('honmei', [])
        taikou = classified.get('taikou', [])
        
        if honmei:
            target_horses.extend([h.get('horse_number') for h in honmei])
        if taikou:
            target_horses.extend([h.get('horse_number') for h in taikou])
        
        # 最大3頭まで詳細表示
        displayed_count = 0
        for horse_number in target_horses:
            if displayed_count >= 3:
                break
                
            if not isinstance(horse_number, (int, float)):
                continue
                
            horse_eval = horse_evaluations.get(horse_number)
            if not horse_eval:
                continue
                
            # 対象の馬を探す
            horse_info = next((h for h in result.get('horses', []) if h.get('horse_number') == horse_number), {})
            if not horse_info:
                continue
                
            print_jp(f"\n  【{horse_info.get('horse_name', f'馬番{horse_number}')}の詳細】")
            
            # 主要評価要素
            primary_factors = horse_eval.get('primary_factors', {})
            if primary_factors:
                print_jp("   ◇評価要素:")
                factor_names = {
                    'base_ability': '基礎能力',
                    'competitive_profile': '競争適性',
                    'condition_factors': 'コンディション'
                }
                for factor, value in primary_factors.items():
                    print_jp(f"    {factor_names.get(factor, factor)}: {value:.2f}")
            
            # 相対評価
            relative = horse_eval.get('relative', {})
            if relative:
                print_jp("   ◇相対評価:")
                if 'rating' in relative:
                    print_jp(f"    格付け: {relative.get('rating', '')}")
                if 'percentile' in relative:
                    print_jp(f"    パーセンタイル: {relative.get('percentile', 0):.1f}")
            
            # レース展開との相性
            development = horse_eval.get('development', {})
            if development:
                print_jp("   ◇展開適性:")
                running_style_names = {
                    'front': '逃げ',
                    'stalker': '先行',
                    'mid': '中団',
                    'closer': '差し・追込',
                    'unknown': '不明'
                }
                style = development.get('running_style', 'unknown')
                print_jp(f"    走法: {running_style_names.get(style, style)}")
                print_jp(f"    展開適性スコア: {development.get('development_score', 1.0):.2f}")
                print_jp(f"    展開補正: {development.get('development_bonus', 1.0):.2f}")
            
            # 勝率
            print_jp(f"   ◇勝率: {horse_eval.get('win_probability', 0):.1%}")
            
            displayed_count += 1

if __name__ == "__main__":
    main()
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
    try:
        if isinstance(text, bytes):
            text = text.decode('utf-8')
        print(text)
        sys.stdout.flush()
    except Exception as e:
        print(f"Error printing text: {e}")

# JRA情報URL生成関数
def generate_jra_url(url_type, info=None):
    """JRA関連URLを生成するヘルパー関数
    
    Args:
        url_type: URL種別 ('race', 'horse', 'odds', 'result')
        info: 参照情報 (レース情報や馬名など)
        
    Returns:
        str: 該当するJRA情報のURL
    """
    base_urls = {
        'race': "https://www.jra.go.jp/JRADB/accessK.html",
        'horse': "https://www.jra.go.jp/JRADB/accessU.html",
        'odds': "https://www.jra.go.jp/JRADB/accessO.html",
        'result': "https://www.jra.go.jp/JRADB/accessC.html"
    }
    
    url = base_urls.get(url_type, base_urls['race'])
    
    # G1レースの場合は特設ページがあることが多い
    if url_type == 'race' and info and 'grade' in info:
        grade = info.get('grade', '')
        if 'G1' in grade or 'Ｇ１' in grade or ('１' in grade and 'G' in grade):
            return "https://www.jra.go.jp/keiba/tokubetsu/index.html"
    
    return url

# 表示フォーマット用クラス
class TableFormatter:
    """表形式データ表示用ヘルパークラス"""
    
    @staticmethod
    def print_separator(char="=", length=80):
        """区切り線を表示"""
        print_jp(char * length)
    
    @staticmethod
    def print_section_header(title, char="■"):
        """セクションヘッダーを表示"""
        print_jp("\n" + char + " " + title)
        print_jp("─" * 80)
    
    @staticmethod
    def print_table_row(columns, widths):
        """列幅を指定してテーブル行を表示"""
        row = "│ "
        for i, col in enumerate(columns):
            row += str(col).ljust(widths[i]) + " │ "
        print_jp(row)
    
    @staticmethod
    def print_table_header(headers, widths):
        """テーブルヘッダーを表示"""
        # 上部の罫線
        top_line = "┌─"
        for w in widths:
            top_line += "─" * w + "─┬─"
        top_line = top_line[:-2] + "┐"
        print_jp(top_line)
        
        # ヘッダー行
        TableFormatter.print_table_row(headers, widths)
        
        # ヘッダー下の罫線
        mid_line = "├─"
        for w in widths:
            mid_line += "─" * w + "─┼─"
        mid_line = mid_line[:-2] + "┤"
        print_jp(mid_line)
    
    @staticmethod
    def print_table_footer(widths):
        """テーブルフッターを表示"""
        bottom_line = "└─"
        for w in widths:
            bottom_line += "─" * w + "─┴─"
        bottom_line = bottom_line[:-2] + "┘"
        print_jp(bottom_line)
    
    @staticmethod
    def display_table(headers, data_rows, widths, title=None):
        """表全体を表示するヘルパーメソッド"""
        if title:
            print_jp(f"\n▼ {title}")
            
        TableFormatter.print_table_header(headers, widths)
        
        # データ行
        for row in data_rows:
            TableFormatter.print_table_row(row, widths)
        
        # 下部の罫線
        bottom_line = "└─"
        for w in widths:
            bottom_line += "─" * w + "─┴─"
        bottom_line = bottom_line[:-2] + "┘"
        print_jp(bottom_line)
    
    @staticmethod
    def display_odds_table(result, odds_dict, title, column_settings=None):
        """オッズ情報を表形式で表示する
        
        Args:
            result: 分析結果の辞書
            odds_dict: オッズ情報の辞書（馬番：オッズ値）
            title: 表のタイトル
            column_settings: 列設定（オプション）
        """
        if not odds_dict:
            return
            
        # デフォルト列設定
        if column_settings is None:
            headers = ["馬番", "馬名", "オッズ"]
            widths = [8, 20, 10]
        else:
            headers = column_settings.get('headers', ["馬番", "馬名", "オッズ"])
            widths = column_settings.get('widths', [8, 20, 10])
        
        rows = []
        
        # 馬番順に整列
        horse_numbers = sorted(odds_dict.keys())
        
        for horse_number in horse_numbers:
            # 該当する馬を探す
            horse_info = next((h for h in result.get('horses', []) 
                               if h.get('horse_number') == horse_number), {})
            
            if horse_info:
                row = [
                    horse_number,
                    horse_info.get('horse_name', '不明'),
                    f"{odds_dict.get(horse_number, '-'):.1f}"
                ]
                rows.append(row)
        
        TableFormatter.display_table(headers, rows, widths, title)
    
    @staticmethod
    def display_horse_category(category_name, horses, column_settings=None):
        """馬のカテゴリ分類を表形式で表示する
        
        Args:
            category_name: カテゴリ名（本命馬、対抗馬など）
            horses: 馬情報のリスト
            column_settings: 列設定（オプション）
        """
        if not horses:
            return
            
        print_jp(f"【{category_name}】")
        
        # デフォルト列設定
        if column_settings is None:
            headers = ["馬番", "馬名", "オッズ", "スコア"]
            widths = [6, 20, 10, 10]
        else:
            headers = column_settings.get('headers', ["馬番", "馬名", "オッズ", "スコア"])
            widths = column_settings.get('widths', [6, 20, 10, 10])
        
        rows = []
        
        for horse in horses:
            row = [
                horse.get('horse_number', '?'),
                horse.get('horse_name', '不明'),
                f"{horse.get('odds', '-'):.1f}",
                f"{horse.get('adjusted_score', horse.get('total_score', 0)):.1f}"
            ]
            rows.append(row)
        
        TableFormatter.display_table(headers, rows, widths)
        print_jp("")  # 空行

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
        
        # ハッシュ可能な形式へ変換
        horses_tuple = tuple(self._make_horse_tuple(h) for h in horses)
        race_info_key = processed_race_info.get('_cache_key', tuple())
        
        # レース特性の分析
        race_characteristics = self._analyze_race_characteristics(horses_tuple, race_info_key)
        processed_race_info['race_characteristics'] = race_characteristics
        
        # オッズ情報の取得（サンプルまたは実際のデータソースから）
        odds_info = self._get_odds_info(horses, processed_race_info)
        processed_race_info['odds_info'] = odds_info
        
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
        
        # 馬群の分類
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
    
    def _get_odds_info(self, horses, race_info):
        """オッズ情報を取得または生成する"""
        # 実際の環境では外部APIまたはWebスクレイピングでデータを取得します
        
        odds_info = {
            'win_odds': {},      # 単勝オッズ
            'place_odds': {},    # 複勝オッズ
            'quinella_odds': {}, # 連勝オッズ
            'exacta_odds': {},   # 馬単オッズ
            'trio_odds': {},     # 3連複オッズ
            'trifecta_odds': {}, # 3連単オッズ
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 各馬の単勝・複勝オッズを設定
        for horse in horses:
            horse_number = horse.get('horse_number')
            if horse_number:
                # 既存のオッズがあればそれを使用、なければ計算
                win_odds = horse.get('odds', self._calculate_theoretical_odds(horse))
                odds_info['win_odds'][horse_number] = win_odds
                
                # 複勝オッズは単勝の約0.4倍〜0.8倍程度（経験則）
                place_multiplier = random.uniform(0.4, 0.8)
                odds_info['place_odds'][horse_number] = max(1.1, win_odds * place_multiplier)
        
        return odds_info

def display_results(result: dict):
    """分析結果を表示する関数"""
    # 表示ヘルパーのインスタンス化
    tf = TableFormatter
    
    # タイトル表示
    tf.print_separator()
    print_jp("分析結果レポート")
    tf.print_separator()
    
    # レース情報の表示
    race_info = result.get('race_info', {})
    tf.print_section_header("レース情報")
    print_jp(f"レース名: {race_info.get('race_name', '不明')}")
    print_jp(f"競馬場: {race_info.get('track', '不明')} / {race_info.get('surface', '不明')} / {race_info.get('distance', '不明')}m")
    print_jp(f"馬場状態: {race_info.get('track_condition', '不明')}")
    print_jp(f"クラス: {race_info.get('grade', '不明')}")
    
    # JRA公式サイトへのリンクを表示
    jra_url = generate_jra_url('race', race_info)
    print_jp(f"\nJRA公式サイト参照: {jra_url}")
    
    # レース特性の表示
    characteristics = race_info.get('race_characteristics', {})
    if characteristics:
        tf.print_section_header("レース特性分析")
        
        # 特性を表で表示
        headers = ["特性", "値", "説明"]
        widths = [15, 10, 45]
        
        # 特性データ
        traits = [
            ["波乱度", f"{characteristics.get('upset_likelihood', 0):.2f}", "レースの波乱度合い (0-1)"],
            ["調子重要度", f"{characteristics.get('form_importance', 0):.2f}", "馬の調子が結果に与える影響 (0-1)"],
            ["ペース依存度", f"{characteristics.get('pace_dependency', 0):.2f}", "レースペースが結果に与える影響 (0-1)"],
            ["クラス差", f"{characteristics.get('class_gap', 0):.2f}", "出走馬間のクラス差 (0-1)"]
        ]
        
        tf.display_table(headers, traits, widths)
    
    # オッズ情報を表示
    _display_odds_info(result, tf)
    
    # 馬の分類を表示
    _display_horse_classifications(result, tf)
    
    # 予測結果を表示
    _display_predictions(result, tf)
    
    # レース展開予測を表示
    _display_race_development(result, tf)
    
    # レースパターン分析を表示
    _display_race_pattern(result, tf)
    
    # 各馬の詳細分析表示
    _display_detailed_horse_analysis(result, tf)

def _display_odds_info(result, tf):
    """オッズ情報表示のヘルパー関数"""
    race_info = result.get('race_info', {})
    odds_info = race_info.get('odds_info', {})
    
    if not odds_info:
        return
        
    tf.print_section_header("オッズ情報")
    print_jp(f"最終更新: {odds_info.get('updated_at', '不明')}")
    
    # 単勝・複勝オッズの表示（TableFormatterのメソッドを使用）
    tf.display_odds_table(result, odds_info.get('win_odds', {}), "単勝オッズ")
    tf.display_odds_table(result, odds_info.get('place_odds', {}), "複勝オッズ")
    
    # オッズ情報へのリンク
    odds_url = generate_jra_url('odds')
    print_jp(f"\nオッズ詳細（JRA公式サイト）: {odds_url}")

def _display_horse_classifications(result, tf):
    """馬の分類表示のヘルパー関数"""
    classified = result.get('classified_horses', {})
    if not classified:
        return
        
    tf.print_section_header("馬の分類")
    
    # 各カテゴリの表示（TableFormatterのメソッドを使用）
    categories = [
        ("本命馬", classified.get('honmei', [])),
        ("対抗馬", classified.get('taikou', [])),
        ("穴馬", classified.get('ana', []))
    ]
    
    for name, horses in categories:
        tf.display_horse_category(name, horses)

def _display_predictions(result, tf):
    """予測結果表示のヘルパー関数"""
    predictions = result.get('predictions', [])
    if not predictions:
        return
        
    tf.print_section_header("予測順位")
    
    # データ準備
    headers = ["着順", "馬番", "馬名", "勝率"]
    widths = [6, 6, 20, 10]
    rows = []
    
    for i, horse in enumerate(predictions[:5], 1):  # 上位5頭まで表示
        row = [
            i,
            horse.get('horse_number', '?'),
            horse.get('horse_name', '不明'),
            f"{horse.get('win_probability', 0):.1%}"
        ]
        rows.append(row)
    
    tf.display_table(headers, rows, widths)

def _display_race_development(result, tf):
    """レース展開予測表示のヘルパー関数"""
    race_development = result.get('race_development', {})
    if not race_development:
        return
        
    tf.print_section_header("レース展開予測")
    
    # 展開タイプの日本語表示
    development_type = race_development.get('development', '不明')
    development_japanese = {
        'fast': 'ハイペース',
        'mid': '平均ペース',
        'slow': 'スローペース',
        '不明': '不明'
    }
    
    print_jp(f"予測展開: {development_japanese.get(development_type, '不明')}")
    print_jp(f"詳細: {race_development.get('explanation', '情報なし')}")
    print_jp(f"上がり: {race_development.get('closing_explanation', '情報なし')}")

def _display_race_pattern(result, tf):
    """レースパターン分析表示のヘルパー関数"""
    detailed_analysis = result.get('detailed_analysis', {})
    if not detailed_analysis:
        return
        
    pattern_analysis = detailed_analysis.get('pattern_analysis', {})
    if not pattern_analysis:
        return
        
    tf.print_section_header("レースパターン分析")
    print_jp(f"パターン: {pattern_analysis.get('race_pattern', '不明')}")
    print_jp(f"説明: {pattern_analysis.get('pattern_explanation', '情報なし')}")

def _display_detailed_horse_analysis(result, tf):
    """各馬の詳細分析表示のヘルパー関数"""
    detailed_analysis = result.get('detailed_analysis', {})
    if not detailed_analysis:
        return
        
    horse_evaluations = detailed_analysis.get('horse_evaluations', {})
    if not horse_evaluations or not result.get('horses'):
        return
        
    tf.print_section_header("詳細分析（すべての出走馬）")
    
    # すべての馬を表示対象とする
    target_horses = []
    for horse in result.get('horses', []):
        horse_number = horse.get('horse_number')
        if horse_number is not None:
            target_horses.append(horse_number)
    
    # 各馬の詳細表示
    displayed_count = 0
    for horse_number in target_horses:
        if not isinstance(horse_number, (int, float)):
            continue
            
        horse_eval = horse_evaluations.get(horse_number)
        if not horse_eval:
            continue
            
        # 対象の馬を探す
        horse_info = next((h for h in result.get('horses', []) if h.get('horse_number') == horse_number), {})
        if not horse_info:
            continue
        
        # 馬の詳細情報ヘッダー
        print_jp(f"\n{horse_info.get('horse_number', '?')}. {horse_info.get('horse_name', f'馬番{horse_number}')} の詳細分析")
        print_jp("─" * 50)
        
        # 馬の詳細情報へのリンク
        horse_name = horse_info.get('horse_name', '')
        if horse_name:
            horse_url = generate_jra_url('horse')
            print_jp(f"JRA競走馬情報: {horse_url}")
            print_jp("")  # 空行
        
        # 詳細分析表示共通処理
        def display_factor_table(factor_dict, title, name_mapping=None):
            if not factor_dict:
                return
                
            print_jp(f"\n◇{title}")
            
            # データ行の準備
            rows = []
            for key, value in factor_dict.items():
                display_name = key
                if name_mapping and key in name_mapping:
                    display_name = name_mapping[key]
                    
                if isinstance(value, (int, float)):
                    value_str = f"{value:.2f}"
                else:
                    value_str = str(value)
                    
                rows.append([display_name, value_str])
            
            # テーブル表示
            if rows:
                headers = ["項目", "評価"]
                widths = [20, 10]
                tf.display_table(headers, rows, widths)
        
        # 主要評価要素
        factor_names = {
            'base_ability': '基礎能力',
            'competitive_profile': '競争適性',
            'condition_factors': 'コンディション'
        }
        display_factor_table(horse_eval.get('primary_factors', {}), "評価要素", factor_names)
        
        # 相対評価
        relative = horse_eval.get('relative', {})
        if relative:
            rel_data = {}
            if 'rating' in relative:
                rel_data['格付け'] = relative.get('rating', '')
            if 'percentile' in relative:
                rel_data['パーセンタイル'] = relative.get('percentile', 0)
            
            display_factor_table(rel_data, "相対評価")
        
        # レース展開との相性
        development = horse_eval.get('development', {})
        if development:
            running_style_names = {
                'front': '逃げ',
                'stalker': '先行',
                'mid': '中団',
                'closer': '差し・追込',
                'unknown': '不明'
            }
            
            style = development.get('running_style', 'unknown')
            dev_data = {
                '走法': running_style_names.get(style, style),
                '展開適性スコア': development.get('development_score', 1.0),
                '展開補正': development.get('development_bonus', 1.0)
            }
            
            display_factor_table(dev_data, "展開適性")
        
        # 勝率
        print_jp(f"\n◇勝率: {horse_eval.get('win_probability', 0):.1%}")
        
        displayed_count += 1
        
        # 馬の区切り線
        if displayed_count < len(target_horses):
            print_jp("\n" + "─" * 80)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
穴馬データベース連携予想システム
- keiba-sqliteデータベースとの連携
- 穴馬候補の自動検出
- 条件マッチング機能
"""

import json
import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class DarkHorsePredictor:
    """穴馬データベース連携予想システム"""
    
    def __init__(self):
        # 基本的な重み設定
        self.weights = {
            'recent_form': 0.25,      # 近走成績（データベース優先のため少し下げた）
            'distance_fit': 0.22,     # 距離適性
            'running_style': 0.18,    # 脚質適性
            'track_condition': 0.10,  # 馬場適性
            'jockey': 0.08,           # 騎手
            'course_fit': 0.05,       # コース適性
            'dark_horse_bonus': 0.12  # 穴馬データベースボーナス
        }
        
        # SMILE基準距離カテゴリ
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
            '福永祐一', 'M.デムーロ', '池添謙一', '横山武史',
            '松岡正海', '藤岡佑介', '岩田康誠'
        ]
    
    def query_dark_horse_data(self, horse_name: str) -> Optional[Dict]:
        """穴馬データベースから馬の情報を取得"""
        # 実際のクエリ実行はMCPサーバー経由で行う
        # ここでは疑似的な実装
        query = f"SELECT * FROM unified_dark_horses WHERE horse_name = '{horse_name}'"
        
        # 注意: 実際にはSQLインジェクション対策が必要
        try:
            # MCPサーバーでクエリを実行
            result = self._execute_query(query)
            return result[0] if result else None
        except Exception as e:
            print(f"データベースエラー: {e}")
            return None
    
    def _execute_query(self, query: str) -> List[Dict]:
        """SQLクエリを実行（疑似実装）"""
        # 実際の実装では、MCPサーバーのread_queryを使用
        # ここでは動作確認用のサンプル
        sample_data = {
            'ミュージアムマイル': {
                'evaluation_score': 95,
                'evaluation_reason': '皐月賞勝ち馬が2番人気6着で信頼失墜。芝2000-2400m・内枠・7番人気以下が狙い目',
                'expected_odds_min': 8
            },
            'エンブロイダリー': {
                'evaluation_score': 93,
                'evaluation_reason': 'オークス1番人気9着は距離2400m不適応。芝1600-2000m・ルメール・距離短縮で激変期待',
                'expected_odds_min': 5
            }
        }
        
        horse_name = query.split("'")[1] if "'" in query else ""
        return [sample_data.get(horse_name)] if horse_name in sample_data else []
    
    def analyze_dark_horse_conditions(self, horse_data: Dict, race_info: Dict, db_data: Dict) -> Dict:
        """穴馬条件の分析"""
        if not db_data:
            return {'score': 0, 'matched_conditions': [], 'reason': ''}
        
        score = db_data.get('evaluation_score', 0)
        reason = db_data.get('evaluation_reason', '')
        matched_conditions = []
        
        # 条件マッチングロジック
        race_distance = race_info.get('distance', 0)
        race_surface = race_info.get('surface', '')
        jockey = horse_data.get('jockey', '')
        popularity = horse_data.get('popularity', 1)
        
        # 距離条件チェック
        if '1600-2000m' in reason and 1600 <= race_distance <= 2000:
            matched_conditions.append('適正距離')
            score += 10
        elif '2000-2400m' in reason and 2000 <= race_distance <= 2400:
            matched_conditions.append('適正距離')
            score += 10
        
        # 騎手条件チェック
        if 'ルメール' in reason and 'ルメール' in jockey:
            matched_conditions.append('指定騎手')
            score += 15
        elif '藤岡佑介' in reason and '藤岡佑介' in jockey:
            matched_conditions.append('指定騎手')
            score += 15
        
        # 人気条件チェック
        if '7番人気以下' in reason and popularity >= 7:
            matched_conditions.append('人気条件')
            score += 20
        
        # 馬場条件チェック
        race_condition = race_info.get('condition', '良')
        if '良馬場' in reason and race_condition == '良':
            matched_conditions.append('馬場条件')
            score += 10
        
        return {
            'score': min(score, 100),
            'matched_conditions': matched_conditions,
            'reason': reason,
            'base_evaluation': db_data.get('evaluation_score', 0)
        }
    
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
            
            # 人気による補正
            if popularity <= 3 and result <= 3:
                base_score += 10
            elif popularity >= 8 and result <= 3:
                base_score += 20
            
            score += base_score * weights[i]
        
        return min(score, 100)
    
    def analyze_basic_factors(self, horse_data: Dict, race_info: Dict) -> float:
        """基本的な要素の分析（簡略化）"""
        score = 60.0
        
        # 騎手ボーナス
        jockey = horse_data.get('jockey', '')
        if any(top_j in jockey for top_j in self.top_jockeys):
            score += 15
        
        # 距離適性（簡易版）
        target_distance = race_info.get('distance', 1600)
        recent_results = horse_data.get('recent_results', [])
        
        similar_distance_results = [
            r for r in recent_results 
            if abs(r.get('distance', 0) - target_distance) <= 200
        ]
        
        if similar_distance_results:
            avg_result = sum(r.get('result', 10) for r in similar_distance_results) / len(similar_distance_results)
            if avg_result <= 3:
                score += 20
            elif avg_result <= 5:
                score += 10
        
        return min(score, 100)
    
    def predict_race_with_dark_horse_db(self, race_data: Dict) -> Dict:
        """穴馬データベース連携予想"""
        horses = race_data.get('horses', [])
        predictions = []
        dark_horse_findings = []
        
        for horse in horses:
            horse_name = horse.get('horse_name', '')
            
            # 基本分析
            recent_score = self.analyze_recent_form(horse.get('recent_results', []))
            basic_score = self.analyze_basic_factors(horse, race_data)
            
            # 穴馬データベース検索
            db_data = self.query_dark_horse_data(horse_name)
            dark_horse_analysis = self.analyze_dark_horse_conditions(horse, race_data, db_data)
            
            # 総合スコア計算
            total_score = (
                recent_score * self.weights['recent_form'] +
                basic_score * self.weights['distance_fit'] +
                dark_horse_analysis['score'] * self.weights['dark_horse_bonus']
            )
            
            # 勝率推定
            win_probability = min(total_score / 100 * 0.35, 0.8)
            
            prediction = {
                'horse_number': horse.get('horse_number', 0),
                'horse_name': horse_name,
                'jockey': horse.get('jockey', ''),
                'odds': horse.get('odds', 0.0),
                'popularity': horse.get('popularity', 0),
                'total_score': round(total_score, 1),
                'win_probability': round(win_probability, 3),
                'dark_horse_data': dark_horse_analysis,
                'breakdown': {
                    'recent_form': round(recent_score, 1),
                    'basic_factors': round(basic_score, 1),
                    'dark_horse_bonus': round(dark_horse_analysis['score'], 1)
                }
            }
            
            predictions.append(prediction)
            
            # 穴馬候補として条件マッチした馬を記録
            if dark_horse_analysis['matched_conditions']:
                dark_horse_findings.append({
                    'horse_name': horse_name,
                    'matched_conditions': dark_horse_analysis['matched_conditions'],
                    'evaluation_reason': dark_horse_analysis['reason'],
                    'bonus_score': dark_horse_analysis['score']
                })
        
        # スコア順でソート
        predictions.sort(key=lambda x: x['total_score'], reverse=True)
        
        return {
            'race_info': race_data,
            'predictions': predictions,
            'dark_horse_findings': dark_horse_findings
        }


def create_sample_race_for_db_test():
    """データベーステスト用サンプルレース"""
    return {
        'race_name': 'テストレース',
        'track': '東京',
        'surface': '芝',
        'distance': 1800,
        'condition': '良',
        'horses': [
            {
                'horse_number': 1,
                'horse_name': 'ミュージアムマイル',
                'jockey': '戸崎圭太',
                'odds': 12.0,
                'popularity': 8,
                'recent_results': [
                    {'place': '東京', 'distance': 2000, 'result': 6, 'popularity': 2},
                    {'place': '中山', 'distance': 2400, 'result': 1, 'popularity': 1}
                ]
            },
            {
                'horse_number': 2,
                'horse_name': 'エンブロイダリー',
                'jockey': 'C.ルメール',
                'odds': 8.5,
                'popularity': 6,
                'recent_results': [
                    {'place': '東京', 'distance': 2400, 'result': 9, 'popularity': 1},
                    {'place': '阪神', 'distance': 1600, 'result': 2, 'popularity': 3}
                ]
            },
            {
                'horse_number': 3,
                'horse_name': '普通の馬',
                'jockey': '武豊',
                'odds': 5.2,
                'popularity': 3,
                'recent_results': [
                    {'place': '中山', 'distance': 1800, 'result': 4, 'popularity': 4},
                    {'place': '東京', 'distance': 1600, 'result': 3, 'popularity': 5}
                ]
            }
        ]
    }


def main():
    """メイン処理"""
    print("=== 穴馬データベース連携予想システム ===")
    
    predictor = DarkHorsePredictor()
    race_data = create_sample_race_for_db_test()
    
    result = predictor.predict_race_with_dark_horse_db(race_data)
    
    print(f"\n【{race_data['race_name']}】予想結果")
    print("-" * 60)
    
    # 基本予想結果
    for pred in result['predictions']:
        print(f"{pred['horse_name']} (人気{pred['popularity']}番)")
        print(f"  総合スコア: {pred['total_score']}点")
        
        dark_horse_data = pred['dark_horse_data']
        if dark_horse_data['matched_conditions']:
            print(f"  ★穴馬候補★ 条件マッチ: {', '.join(dark_horse_data['matched_conditions'])}")
            print(f"  理由: {dark_horse_data['reason'][:50]}...")
        
        print()
    
    # 穴馬発見まとめ
    if result['dark_horse_findings']:
        print("=== 穴馬データベースマッチ ===")
        for finding in result['dark_horse_findings']:
            print(f"★ {finding['horse_name']}")
            print(f"  条件: {', '.join(finding['matched_conditions'])}")
            print(f"  理由: {finding['evaluation_reason'][:60]}...")
            print()
    
    return result


if __name__ == "__main__":
    result = main()
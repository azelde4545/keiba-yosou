# -*- coding: utf-8 -*-
"""
競馬予想システム - 結果出力・購入ガイド生成モジュール
詳細分析結果とフォーマット済み購入ガイドの生成
"""

from typing import Dict, List, Any, Optional
from datetime import datetime


class OutputFormatter:
    """結果出力・購入ガイド生成クラス"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
    
    def format_output(self, evaluation_results: List[Dict[str, Any]], 
                     betting_results: Dict[str, Any],
                     race_data: Dict[str, Any]) -> str:
        """メイン結果出力フォーマット"""
        race_info = race_data.get('race_info', {})
        
        output = f"""
競馬予想システム v3.0 - 詳細分析結果
{'='*80}

レース情報
レース名: {race_info.get('name', '不明')}
開催日: {race_info.get('date', '不明')}
競馬場: {race_info.get('venue', '不明')}
距離: {race_info.get('distance', '不明')}m
馬場: {race_info.get('course_type', '不明')}

{'='*80}

6要素評価システム結果
"""
        
        # 上位馬の詳細分析
        for i, horse in enumerate(evaluation_results[:5], 1):
            rank_labels = {1: "本命", 2: "対抗", 3: "単穴", 4: "連下", 5: "5番手"}
            
            output += f"""
【{i}位】 {rank_labels.get(i, str(i)+'番手')}: {horse['number']}番 {horse['name']}
{'─'*60}
オッズ: {horse['odds']}倍 (人気: {horse.get('popularity', '?')}番人気)
騎手: {horse['jockey']} | 体重: {horse['weight']}
総合評価: {horse['final_score']}点

詳細スコア内訳:
  - 過去成績評価: {horse['performance_score']}点 (30%重み)
  - コース適正: {horse['course_fit_score']}点 (35%重み)
  - オッズ価値: {horse['odds_value_score']}点 (15%重み)
  - 前走間隔: {horse['interval_score']}点 (10%重み)
  - 穴馬要素: {horse['dark_horse_score']}点 (10%重み)

詳細分析:
{self._generate_horse_analysis(horse)}
"""
        
        # 購入戦略セクション
        output += f"""
{'='*80}

推奨購入戦略: {betting_results.get('strategy', '不明')}
"""
        
        # 購入ガイドを追加
        purchase_guide = betting_results.get('purchase_guide', '')
        if purchase_guide:
            output += purchase_guide
        
        # フッター情報
        output += f"""
{'='*80}

分析完了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
使用システム: 6要素評価システム + ThreadPoolExecutor並列処理
注意事項: この予想は過去データに基づく分析結果です。
          実際の投資は自己責任でお願いします。

競馬予想システム v3.0 - Good Luck!
"""
        
        return output
    
    def _generate_horse_analysis(self, horse: Dict[str, Any]) -> str:
        """個別馬の詳細分析生成"""
        analysis = []
        
        # 過去成績分析
        perf_score = horse.get('performance_score', 0)
        if perf_score >= 80:
            analysis.append("[○] 過去成績: 非常に優秀な実績")
        elif perf_score >= 65:
            analysis.append("[○] 過去成績: 好調な成績を維持")
        elif perf_score >= 50:
            analysis.append("[△] 過去成績: 平均的な実績")
        else:
            analysis.append("[×] 過去成績: 成績に不安要素")
        
        # コース適正分析
        course_score = horse.get('course_fit_score', 0)
        if course_score >= 80:
            analysis.append("[○] コース適正: このコースに非常に適している")
        elif course_score >= 65:
            analysis.append("[○] コース適正: コース経験豊富")
        elif course_score >= 50:
            analysis.append("[△] コース適正: 普通の適正")
        else:
            analysis.append("[×] コース適正: コース経験不足")
        
        # オッズ価値分析
        odds_score = horse.get('odds_value_score', 0)
        odds = horse.get('odds', 0)
        if odds_score >= 65:
            analysis.append(f"[○] 投資価値: 高い (オッズ{odds}倍は割安)")
        elif odds_score >= 50:
            analysis.append(f"[△] 投資価値: 適正 (オッズ{odds}倍は妥当)")
        else:
            analysis.append(f"[×] 投資価値: 低い (オッズ{odds}倍は割高)")
        
        # 前走間隔分析
        interval_score = horse.get('interval_score', 0)
        interval_days = horse.get('interval_days')
        if interval_days:
            if interval_score >= 10:
                analysis.append(f"[○] 調整: ベストコンディション ({interval_days}日前走)")
            elif interval_score >= 0:
                analysis.append(f"[△] 調整: 普通の仕上がり ({interval_days}日前走)")
            else:
                analysis.append(f"[×] 調整: 調整に不安 ({interval_days}日前走)")
        
        # 穴馬要素分析
        dark_horse_score = horse.get('dark_horse_score', 0)
        if dark_horse_score >= 70:
            analysis.append("[!] 穴馬度: 大穴候補として注目")
        elif dark_horse_score >= 50:
            analysis.append("[!] 穴馬度: 中穴候補として面白い")
        else:
            analysis.append("[-] 穴馬度: 堅実な人気馬")
        
        return "\n  ".join(analysis)
    
    def save_results(self, formatted_output: str, filename: str = None) -> str:
        """結果をファイルに保存"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"prediction_result_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(formatted_output)
            
            print(f"[成功] 結果をファイルに保存しました: {filename}")
            return filename
            
        except Exception as e:
            print(f"[エラー] ファイル保存エラー: {e}")
            return ""
    
    def generate_simple_summary(self, evaluation_results: List[Dict[str, Any]], 
                               betting_results: Dict[str, Any]) -> str:
        """簡易サマリー生成（コンソール表示用）"""
        if not evaluation_results:
            return "[エラー] 評価結果がありません"
        
        top3 = evaluation_results[:3]
        
        summary = """
競馬予想 - 簡易サマリー
───────────────────────────
"""
        
        labels = ["本命", "対抗", "穴馬"]
        for i, (label, horse) in enumerate(zip(labels, top3)):
            summary += f"[{label}]: {horse['number']}番 {horse['name']}\n"
            summary += f"   オッズ: {horse['odds']}倍 | 評価: {horse['final_score']}点\n"
        
        strategy = betting_results.get('strategy', '不明')
        expected_return = betting_results.get('expected_return', 0)
        
        summary += f"""
───────────────────────────
推奨戦略: {strategy}
期待倍率: {expected_return}倍
投資は自己責任でお願いします
"""
        
        return summary
    
    def export_to_json(self, evaluation_results: List[Dict[str, Any]], 
                      betting_results: Dict[str, Any],
                      race_data: Dict[str, Any]) -> Dict[str, Any]:
        """結果をJSON形式でエクスポート"""
        return {
            "timestamp": datetime.now().isoformat(),
            "race_info": race_data.get('race_info', {}),
            "evaluation_results": evaluation_results,
            "betting_strategy": betting_results,
            "system_info": {
                "version": "3.0",
                "evaluation_method": "6要素評価システム",
                "parallel_processing": "ThreadPoolExecutor"
            }
        }

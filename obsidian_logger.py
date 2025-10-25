# -*- coding: utf-8 -*-
"""
競馬予想システム - Obsidian連携モジュール
予測結果をMarkdownテンプレートに整形して出力
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List


class ObsidianLogger:
    """予測結果をObsidian用Markdownに出力するクラス"""

    def __init__(self, template_path: str = "prediction_template.md", output_dir: str = "output_analysis"):
        """
        Args:
            template_path: テンプレートファイルのパス
            output_dir: 出力先ディレクトリ
        """
        self.template_path = Path(template_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def create_prediction_note(
        self,
        race_data: Dict[str, Any],
        ability_results: List[Dict[str, Any]],
        value_results: List[Dict[str, Any]],
        pace_analysis: Dict[str, Any],
        betting_plan: str,
        protocol_mode: str = "3分モード",
        processing_time: float = 0.0
    ) -> str:
        """
        予測結果をMarkdownファイルに出力

        Args:
            race_data: レースデータ
            ability_results: 実力評価結果
            value_results: 期待値評価結果
            pace_analysis: 脚質展開分析
            betting_plan: 購入プラン
            protocol_mode: 使用プロトコル（1分/3分/5分モード）
            processing_time: 処理時間（秒）

        Returns:
            出力したファイルのパス
        """
        # テンプレート読み込み
        if not self.template_path.exists():
            raise FileNotFoundError(f"テンプレートファイルが見つかりません: {self.template_path}")

        with open(self.template_path, 'r', encoding='utf-8') as f:
            template = f.read()

        # レース情報
        race_info = race_data.get('race_info', {})
        race_name = race_info.get('name', '不明なレース')
        race_date = race_info.get('date', datetime.now().strftime('%Y-%m-%d'))

        # トップ3候補
        top3 = ability_results[:3] if len(ability_results) >= 3 else ability_results

        # 最終決定の判断
        decision, confidence, main_reason = self._make_decision(ability_results, value_results)

        # 主要評価因子の平均値
        avg_scores = self._calculate_average_scores(ability_results[:3])

        # 展開予想
        pace_prediction = self._format_pace_prediction(pace_analysis)

        # テンプレート置換
        replacements = {
            '{{race_name}}': race_name,
            '{{race_date}}': race_date,
            '{{execution_date}}': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            '{{protocol_mode}}': protocol_mode,
            '{{processing_time}}': f"{processing_time:.2f}",
            '{{decision}}': decision,
            '{{confidence}}': confidence,
            '{{main_reason}}': main_reason,
            '{{horse1_number}}': str(top3[0]['number']) if len(top3) > 0 else '-',
            '{{horse1_name}}': top3[0]['name'] if len(top3) > 0 else '-',
            '{{horse1_score}}': f"{top3[0]['final_score']:.2f}" if len(top3) > 0 else '-',
            '{{horse2_number}}': str(top3[1]['number']) if len(top3) > 1 else '-',
            '{{horse2_name}}': top3[1]['name'] if len(top3) > 1 else '-',
            '{{horse2_score}}': f"{top3[1]['final_score']:.2f}" if len(top3) > 1 else '-',
            '{{horse3_number}}': str(top3[2]['number']) if len(top3) > 2 else '-',
            '{{horse3_name}}': top3[2]['name'] if len(top3) > 2 else '-',
            '{{horse3_score}}': f"{top3[2]['final_score']:.2f}" if len(top3) > 2 else '-',
            '{{past_performance_avg}}': f"{avg_scores.get('performance', 0):.1f}",
            '{{course_fit_avg}}': f"{avg_scores.get('course_fit', 0):.1f}",
            '{{odds_value_avg}}': f"{avg_scores.get('odds_value', 0):.1f}",
            '{{track_condition_avg}}': f"{avg_scores.get('track_condition', 0):.1f}",
            '{{interval_avg}}': f"{avg_scores.get('interval', 0):.1f}",
            '{{weight_change_avg}}': f"{avg_scores.get('weight_change', 0):.1f}",
            '{{dark_horse_avg}}': f"{avg_scores.get('dark_horse', 0):.1f}",
            '{{pace_analysis}}': pace_analysis.get('pace', '不明'),
            '{{betting_plan}}': betting_plan,
            '{{pace_prediction}}': pace_prediction
        }

        # Jinja2風の条件分岐を処理
        content = self._process_conditions(template, protocol_mode)

        # 置換実行
        for key, value in replacements.items():
            content = content.replace(key, str(value))

        # ファイル名生成
        safe_race_name = "".join(c for c in race_name if c.isalnum() or c in (' ', '_', '-')).strip()
        filename = f"prediction_{safe_race_name}_{race_date.replace('-', '')}.md"
        output_path = self.output_dir / filename

        # ファイル書き込み
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(output_path)

    def _make_decision(
        self,
        ability_results: List[Dict[str, Any]],
        value_results: List[Dict[str, Any]]
    ) -> tuple:
        """最終決定を判断"""
        if not ability_results:
            return "パス", "低", "評価可能な馬がいません"

        top_horse = ability_results[0]
        top_score = top_horse['final_score']
        top_odds = top_horse['odds']

        # 高評価かつ適正オッズ
        if top_score >= 80 and top_odds <= 5.0:
            return "賭ける", "高", f"{top_horse['name']}が高評価で適正オッズ"
        elif top_score >= 70 and top_odds <= 8.0:
            return "賭ける", "中", f"{top_horse['name']}が良好な評価"
        elif top_score >= 60:
            # 穴馬候補もチェック
            if value_results and value_results[0]['final_score'] >= 70:
                value_horse = value_results[0]
                return "賭ける", "中", f"穴馬候補{value_horse['name']}に妙味"
            return "パス", "低", "評価は普通だが確信が持てない"
        else:
            return "パス", "低", "高評価の馬がいない"

    def _calculate_average_scores(self, horses: List[Dict[str, Any]]) -> Dict[str, float]:
        """トップ馬の平均スコアを計算"""
        if not horses:
            return {key: 0.0 for key in ['past_performance', 'course_fit', 'odds_value',
                                         'track_condition', 'interval', 'weight_change', 'dark_horse']}

        avg = {}
        keys = ['performance_score', 'course_fit_score', 'odds_value_score',
                'track_condition_score', 'interval_score', 'weight_change_score', 'dark_horse_score']

        for key in keys:
            values = [h.get(key, 0) for h in horses]
            avg[key.replace('_score', '')] = sum(values) / len(values) if values else 0.0

        return avg

    def _format_pace_prediction(self, pace_analysis: Dict[str, Any]) -> str:
        """展開予想をフォーマット"""
        pace = pace_analysis.get('pace', '不明')
        adjustments = pace_analysis.get('adjustments', {})

        prediction = f"**予想ペース**: {pace}\n\n"

        if adjustments:
            prediction += "**有利な馬**:\n"
            # 補正値が高い順にソート
            sorted_horses = sorted(adjustments.items(), key=lambda x: x[1], reverse=True)
            for horse_name, adj in sorted_horses[:3]:
                if adj > 1.0:
                    prediction += f"- {horse_name} (補正: {adj:.2f})\n"

        return prediction

    def _process_conditions(self, template: str, protocol_mode: str) -> str:
        """Jinja2風の条件分岐を簡易処理"""
        lines = template.split('\n')
        output_lines = []
        skip_mode = False

        for line in lines:
            # 条件開始
            if '{% if protocol_mode != "1分モード" %}' in line:
                skip_mode = (protocol_mode == "1分モード")
                continue
            elif '{% if protocol_mode == "5分モード" %}' in line:
                skip_mode = (protocol_mode != "5分モード")
                continue
            # 条件終了
            elif '{% endif %}' in line:
                skip_mode = False
                continue

            # スキップモードでなければ行を追加
            if not skip_mode:
                output_lines.append(line)

        return '\n'.join(output_lines)

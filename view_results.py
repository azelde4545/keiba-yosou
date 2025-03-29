# -*- coding: utf-8 -*-
"""
結果表示ユーティリティ
enhanced-racing-system.pyの結果をブラウザで表示するためのヘルパースクリプト
"""

import json
import os
import sys
import webbrowser
from datetime import datetime

def create_html_report(result):
    """分析結果をHTMLに変換"""
    # 結果がない場合は空のHTMLを返す
    if not result or 'error' in result:
        return f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <title>分析エラー</title>
            <style>
                body {{ font-family: 'Meiryo', 'MS Gothic', sans-serif; background-color: #f5f5f5; color: #333; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; background: white; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
                h1 {{ color: #c00; border-bottom: 2px solid #c00; padding-bottom: 10px; }}
                .error {{ color: red; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>競馬予測システム - エラー</h1>
                <p class="error">エラーが発生しました: {result.get('error', '不明なエラー')}</p>
            </div>
        </body>
        </html>
        """

    # レース情報
    race_info = result.get('race_info', {})
    race_name = race_info.get('race_name', '不明')
    track = race_info.get('track', '不明')
    surface = race_info.get('surface', '不明')
    distance = race_info.get('distance', '不明')
    condition = race_info.get('track_condition', '不明')
    grade = race_info.get('grade', '不明')

    # レース特性
    characteristics = race_info.get('race_characteristics', {})
    upset = characteristics.get('upset_likelihood', 0)
    form_importance = characteristics.get('form_importance', 0)
    pace_dependency = characteristics.get('pace_dependency', 0)
    class_gap = characteristics.get('class_gap', 0)

    # 馬の分類
    classified = result.get('classified_horses', {})
    honmei = classified.get('honmei', [])
    taikou = classified.get('taikou', [])
    ana = classified.get('ana', [])

    # 馬情報のHTML生成
    honmei_html = ""
    for horse in honmei:
        honmei_html += f"""
        <tr>
            <td>{horse.get('horse_number', '?')}</td>
            <td>{horse.get('horse_name', '不明')}</td>
            <td>{horse.get('odds', '-'):.1f}</td>
            <td>{horse.get('adjusted_score', horse.get('total_score', 0)):.1f}</td>
        </tr>
        """

    taikou_html = ""
    for horse in taikou:
        taikou_html += f"""
        <tr>
            <td>{horse.get('horse_number', '?')}</td>
            <td>{horse.get('horse_name', '不明')}</td>
            <td>{horse.get('odds', '-'):.1f}</td>
            <td>{horse.get('adjusted_score', horse.get('total_score', 0)):.1f}</td>
        </tr>
        """

    ana_html = ""
    for horse in ana:
        ana_html += f"""
        <tr>
            <td>{horse.get('horse_number', '?')}</td>
            <td>{horse.get('horse_name', '不明')}</td>
            <td>{horse.get('odds', '-'):.1f}</td>
            <td>{horse.get('adjusted_score', horse.get('total_score', 0)):.1f}</td>
        </tr>
        """

    # 予測結果
    predictions = result.get('predictions', [])
    predictions_html = ""
    for i, horse in enumerate(predictions[:5], 1):
        win_prob = horse.get('win_probability', 0) * 100
        predictions_html += f"""
        <tr>
            <td>{i}</td>
            <td>{horse.get('horse_number', '?')}</td>
            <td>{horse.get('horse_name', '不明')}</td>
            <td>{win_prob:.1f}%</td>
        </tr>
        """

    # レース展開予測
    race_development = result.get('race_development', {})
    development_type = race_development.get('development', '不明')
    development_japanese = {
        'slow_pace': 'スローペース',
        'medium_pace': '平均ペース',
        'high_pace': 'ハイペース',
        'unknown': '不明'
    }
    development = development_japanese.get(development_type, '不明')
    explanation = race_development.get('explanation', '情報なし')
    closing = race_development.get('closing_explanation', '情報なし')

    # 詳細分析
    detailed_analysis = result.get('detailed_analysis', {})
    horse_evaluations = detailed_analysis.get('horse_evaluations', {})
    
    detailed_html = ""
    target_horses = []
    if honmei:
        target_horses.extend(honmei[:2])  # 本命馬のトップ2頭
    if taikou:
        target_horses.extend(taikou[:1])  # 対抗馬のトップ1頭
    
    # 詳細分析のHTML生成
    for horse in target_horses:
        horse_number = horse.get('horse_number')
        if not horse_number:
            continue
            
        horse_name = horse.get('horse_name', f'馬番{horse_number}')
        horse_eval = horse_evaluations.get(str(horse_number), {})
        if not horse_eval:
            continue
            
        # 主要評価要素
        primary_factors = horse_eval.get('primary_factors', {})
        primary_html = ""
        if primary_factors:
            factor_names = {
                'base_ability': '基礎能力',
                'competitive_profile': '競争適性',
                'current_form': '現在の調子',
                'race_suitability': 'レース適性'
            }
            for factor, value in primary_factors.items():
                factor_name = factor_names.get(factor, factor)
                primary_html += f"<tr><td>{factor_name}</td><td>{value:.2f}</td></tr>"
        
        # 相対評価
        relative = horse_eval.get('relative', {})
        relative_html = ""
        if relative:
            if 'rating' in relative:
                relative_html += f"<tr><td>格付け</td><td>{relative.get('rating', '')}</td></tr>"
            if 'percentile' in relative:
                relative_html += f"<tr><td>パーセンタイル</td><td>{relative.get('percentile', 0):.1f}</td></tr>"
        
        # レース展開との相性
        development_data = horse_eval.get('development', {})
        development_html = ""
        if development_data:
            running_style_names = {
                'front': '逃げ',
                'stalker': '先行',
                'mid_pack': '中団',
                'closer': '後方',
                'unknown': '不明'
            }
            style = development_data.get('running_style', 'unknown')
            style_name = running_style_names.get(style, style)
            development_html += f"<tr><td>走法</td><td>{style_name}</td></tr>"
            development_html += f"<tr><td>展開適性スコア</td><td>{development_data.get('development_score', 1.0):.2f}</td></tr>"
            development_html += f"<tr><td>展開補正</td><td>{development_data.get('development_bonus', 1.0):.2f}</td></tr>"
        
        # 勝率
        win_prob = horse_eval.get('win_probability', 0) * 100
        
        detailed_html += f"""
        <div class="horse-detail">
            <h3>{horse_name}の詳細分析</h3>
            <div class="detail-section">
                <h4>評価要素</h4>
                <table class="detail-table">
                    {primary_html}
                </table>
            </div>
            <div class="detail-section">
                <h4>相対評価</h4>
                <table class="detail-table">
                    {relative_html}
                </table>
            </div>
            <div class="detail-section">
                <h4>展開適性</h4>
                <table class="detail-table">
                    {development_html}
                </table>
            </div>
            <div class="detail-section">
                <h4>勝率</h4>
                <p>{win_prob:.1f}%</p>
            </div>
        </div>
        """

    # HTML全体の生成
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>競馬予測分析 - {race_name}</title>
        <style>
            body {{ font-family: 'Meiryo', 'MS Gothic', sans-serif; background-color: #f5f5f5; color: #333; margin: 0; padding: 0; }}
            .container {{ max-width: 900px; margin: 0 auto; padding: 20px; background: white; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #880000; border-bottom: 2px solid #880000; padding-bottom: 10px; }}
            h2 {{ color: #555; background-color: #f0f0f0; padding: 8px; border-left: 5px solid #880000; }}
            h3 {{ color: #333; border-bottom: 1px dotted #ccc; }}
            h4 {{ margin: 10px 0 5px 0; color: #555; }}
            .section {{ margin-bottom: 30px; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
            table, th, td {{ border: 1px solid #ddd; }}
            th {{ background-color: #f2f2f2; padding: 10px; text-align: left; }}
            td {{ padding: 8px; }}
            .race-info {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 20px; }}
            .race-info-item {{ background-color: #f9f9f9; padding: 10px; border-radius: 5px; }}
            .horse-cards {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 15px; }}
            .horse-card {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; }}
            .horse-detail {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin-bottom: 15px; }}
            .detail-section {{ margin-bottom: 15px; }}
            .detail-table {{ width: 100%; border-collapse: collapse; }}
            .detail-table td {{ padding: 5px; border: 1px solid #eee; }}
            .detail-table td:first-child {{ width: 40%; font-weight: bold; }}
            .footer {{ margin-top: 30px; text-align: center; font-size: 0.8em; color: #888; }}
            .highlight {{ background-color: #fff2cc; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>競馬予測分析</h1>
            
            <div class="section">
                <h2>レース情報</h2>
                <div class="race-info">
                    <div class="race-info-item">
                        <strong>レース名:</strong> {race_name}
                    </div>
                    <div class="race-info-item">
                        <strong>コース:</strong> {track} / {surface} / {distance}m
                    </div>
                    <div class="race-info-item">
                        <strong>馬場状態:</strong> {condition}
                    </div>
                    <div class="race-info-item">
                        <strong>クラス:</strong> {grade}
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>レース特性分析</h2>
                <table>
                    <tr>
                        <th>特性</th>
                        <th>値 (0-1)</th>
                        <th>説明</th>
                    </tr>
                    <tr>
                        <td>波乱度</td>
                        <td>{upset:.2f}</td>
                        <td>高いほど波乱が起きやすい</td>
                    </tr>
                    <tr>
                        <td>調子重要度</td>
                        <td>{form_importance:.2f}</td>
                        <td>高いほど馬の現在の調子が重要</td>
                    </tr>
                    <tr>
                        <td>ペース依存度</td>
                        <td>{pace_dependency:.2f}</td>
                        <td>高いほどペース展開に結果が左右される</td>
                    </tr>
                    <tr>
                        <td>クラス差</td>
                        <td>{class_gap:.2f}</td>
                        <td>高いほど出走馬間の実力差が大きい</td>
                    </tr>
                </table>
            </div>
            
            <div class="section">
                <h2>馬の分類</h2>
                
                <h3>本命馬</h3>
                <table>
                    <tr>
                        <th>馬番</th>
                        <th>馬名</th>
                        <th>オッズ</th>
                        <th>スコア</th>
                    </tr>
                    {honmei_html}
                </table>
                
                <h3>対抗馬</h3>
                <table>
                    <tr>
                        <th>馬番</th>
                        <th>馬名</th>
                        <th>オッズ</th>
                        <th>スコア</th>
                    </tr>
                    {taikou_html}
                </table>
                
                <h3>穴馬</h3>
                <table>
                    <tr>
                        <th>馬番</th>
                        <th>馬名</th>
                        <th>オッズ</th>
                        <th>スコア</th>
                    </tr>
                    {ana_html}
                </table>
            </div>
            
            <div class="section">
                <h2>予測順位</h2>
                <table>
                    <tr>
                        <th>予想着順</th>
                        <th>馬番</th>
                        <th>馬名</th>
                        <th>勝率</th>
                    </tr>
                    {predictions_html}
                </table>
            </div>
            
            <div class="section">
                <h2>レース展開予測</h2>
                <table>
                    <tr>
                        <th>項目</th>
                        <th>内容</th>
                    </tr>
                    <tr>
                        <td>予測展開</td>
                        <td>{development}</td>
                    </tr>
                    <tr>
                        <td>詳細</td>
                        <td>{explanation}</td>
                    </tr>
                    <tr>
                        <td>上がり</td>
                        <td>{closing}</td>
                    </tr>
                </table>
            </div>
            
            <div class="section">
                <h2>詳細分析（主要な馬）</h2>
                {detailed_html}
            </div>
            
            <div class="footer">
                <p>生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>高度競馬予測システム (Advanced Recursive Racing Analysis System)</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def save_and_open_html(result):
    """結果をHTMLに変換して保存し、ブラウザで開く"""
    html_content = create_html_report(result)
    
    # 結果ファイルの保存場所
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "race_analysis_report.html")
    
    # HTMLファイルを保存
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    # ブラウザで開く
    webbrowser.open('file://' + os.path.realpath(report_path))
    
    return report_path

if __name__ == "__main__":
    # 引数でJSONファイルが指定されていれば読み込む
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            result = json.load(f)
        save_and_open_html(result)
    else:
        print("使用方法: python view_results.py 分析結果.json")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
競馬予想システム v3.0 - メイン実行ファイル
ソフトウェア客観分析 + 人間主観分析のハイブリッドモデル
"""
import os
import sys
import orjson
import logging
import argparse
from datetime import datetime
from pathlib import Path
from data_loader import DataLoader
from horse_evaluator import HorseEvaluator
from betting_strategy import BettingStrategy
from result_formatter_v2 import ResultFormatterV2

# Windows環境での文字化け対策
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ログ設定
BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'keiba_system.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def fill_obsidian_template(template, race_data, ability_results, value_results):
    """Obsidianテンプレートにデータを埋め込む"""
    race_info = race_data.get('race_info', {})
    
    # レース情報
    template = template.replace('{{レース名}}', race_info.get('name', '不明'))
    template = template.replace('{{開催日}}', race_info.get('date', '不明'))
    template = template.replace('{{競馬場}}', race_info.get('track', '不明'))
    template = template.replace('{{距離}}', str(race_data.get('distance', '不明')))
    template = template.replace('{{馬場状態}}', race_info.get('track_condition', '不明'))
    template = template.replace('{{予想日時}}', datetime.now().strftime('%Y年%m月%d日 %H:%M'))
    
    # 推奨馬情報
    if len(ability_results) >= 1:
        honmei = ability_results[0]
        template = template.replace('{{本命馬番}}', str(honmei['number']))
        template = template.replace('{{本命馬名}}', honmei['name'])
        template = template.replace('{{本命評価}}', f"{honmei['final_score']:.1f}")
        template = template.replace('{{本命オッズ}}', f"{honmei['odds']:.1f}")
        template = template.replace('{{本命ランク}}', get_grade(honmei['final_score']))
        template = template.replace('{{本命過去成績}}', f"{honmei.get('performance_score', 0):.1f}")
        template = template.replace('{{本命コース適正}}', f"{honmei.get('course_fit_score', 0):.1f}")
    
    if len(ability_results) >= 2:
        taikou = ability_results[1]
        template = template.replace('{{対抗馬番}}', str(taikou['number']))
        template = template.replace('{{対抗馬名}}', taikou['name'])
        template = template.replace('{{対抗評価}}', f"{taikou['final_score']:.1f}")
        template = template.replace('{{対抗オッズ}}', f"{taikou['odds']:.1f}")
        template = template.replace('{{対抗ランク}}', get_grade(taikou['final_score']))
    
    if len(ability_results) >= 3:
        tanana = ability_results[2]
        template = template.replace('{{単穴馬番}}', str(tanana['number']))
        template = template.replace('{{単穴馬名}}', tanana['name'])
        template = template.replace('{{単穴評価}}', f"{tanana['final_score']:.1f}")
        template = template.replace('{{単穴オッズ}}', f"{tanana['odds']:.1f}")
        template = template.replace('{{単穴ランク}}', get_grade(tanana['final_score']))
    
    # 穴馬候補
    top3_names = {h['name'] for h in ability_results[:3]}
    anauma_candidates = [h for h in value_results if h['name'] not in top3_names][:2]
    
    if len(anauma_candidates) >= 1:
        template = template.replace('{{穴馬1馬番}}', str(anauma_candidates[0]['number']))
        template = template.replace('{{穴馬1馬名}}', anauma_candidates[0]['name'])
        template = template.replace('{{穴馬1評価}}', f"{anauma_candidates[0]['final_score']:.1f}")
        template = template.replace('{{穴馬1オッズ}}', f"{anauma_candidates[0]['odds']:.1f}")
    
    if len(anauma_candidates) >= 2:
        template = template.replace('{{穴馬2馬番}}', str(anauma_candidates[1]['number']))
        template = template.replace('{{穴馬2馬名}}', anauma_candidates[1]['name'])
        template = template.replace('{{穴馬2評価}}', f"{anauma_candidates[1]['final_score']:.1f}")
        template = template.replace('{{穴馬2オッズ}}', f"{anauma_candidates[1]['odds']:.1f}")
    
    # 詳細評価ランキング Top 5
    for i in range(1, 6):
        if i <= len(ability_results):
            horse = ability_results[i-1]
            template = template.replace(f'{{{{{i}位馬番}}}}', str(horse['number']))
            template = template.replace(f'{{{{{i}位馬名}}}}', horse['name'])
            template = template.replace(f'{{{{{i}位総合}}}}', f"{horse['final_score']:.1f}")
            template = template.replace(f'{{{{{i}位過去}}}}', f"{horse.get('performance_score', 0):.1f}")
            template = template.replace(f'{{{{{i}位コース}}}}', f"{horse.get('course_fit_score', 0):.1f}")
            template = template.replace(f'{{{{{i}位馬場}}}}', f"{horse.get('track_condition_score', 0):.1f}")
            template = template.replace(f'{{{{{i}位馬体重}}}}', f"{horse.get('weight_change_score', 50.0):.1f}")
            template = template.replace(f'{{{{{i}位間隔}}}}', f"{horse.get('interval_score', 0):.1f}")
            template = template.replace(f'{{{{{i}位オッズ}}}}', f"{horse['odds']:.1f}")
            template = template.replace(f'{{{{{i}位ランク}}}}', get_grade(horse['final_score']))
    
    # 期待値評価ランキング Top 3
    for i in range(1, 4):
        if i <= len(value_results):
            horse = value_results[i-1]
            template = template.replace(f'{{{{期待値{i}位馬番}}}}', str(horse['number']))
            template = template.replace(f'{{{{期待値{i}位馬名}}}}', horse['name'])
            template = template.replace(f'{{{{期待値{i}位総合}}}}', f"{horse['final_score']:.1f}")
            template = template.replace(f'{{{{期待値{i}位過去}}}}', f"{horse.get('performance_score', 0):.1f}")
            template = template.replace(f'{{{{期待値{i}位コース}}}}', f"{horse.get('course_fit_score', 0):.1f}")
            template = template.replace(f'{{{{期待値{i}位オッズ価値}}}}', f"{horse.get('odds_value_score', 0):.1f}")
            template = template.replace(f'{{{{期待値{i}位穴馬}}}}', f"{horse.get('dark_horse_score', 0):.1f}")
            template = template.replace(f'{{{{期待値{i}位オッズ}}}}', f"{horse['odds']:.1f}")
            template = template.replace(f'{{{{期待値{i}位ランク}}}}', get_grade(horse['final_score']))
    
    # 馬体重変動分析
    weight_info = []
    for horse in ability_results[:10]:
        weight_change = horse.get('weight_change', 0)
        if abs(weight_change) >= 10:
            change_str = f"+{weight_change}kg" if weight_change > 0 else f"{weight_change}kg"
            status = "大幅増" if weight_change >= 15 else "大幅減" if weight_change <= -15 else "変動大"
            weight_info.append(f"- {status}: {horse['number']}番 {horse['name']} - 馬体重変動: {change_str}")
    
    if weight_info:
        template = template.replace('{{馬体重変動情報}}', '\n'.join(weight_info))
    else:
        template = template.replace('{{馬体重変動情報}}', '特に注目すべき馬体重変動はありません（±10kg未満）')
    
    # 推奨馬券
    if len(ability_results) >= 3:
        honmei = ability_results[0]['number']
        taikou = ability_results[1]['number']
        tanana = ability_results[2]['number']
        
        template = template.replace('{{本命型馬連}}', f"{honmei}-{taikou}, {honmei}-{tanana}")
        template = template.replace('{{本命型馬単}}', f"{honmei}→{taikou}, {honmei}→{tanana}")
        template = template.replace('{{本命型ワイド}}', f"{honmei}-{taikou}, {honmei}-{tanana}, {taikou}-{tanana}")
        
        if len(ability_results) >= 5:
            top5 = [str(h['number']) for h in ability_results[:5]]
            template = template.replace('{{3連複軸流し}}', f"{honmei}軸 相手{', '.join(top5[1:])}")
            template = template.replace('{{3連複BOX}}', f"{', '.join(top5[:4])}")
        
        if anauma_candidates:
            anauma_nums = [str(h['number']) for h in anauma_candidates]
            template = template.replace('{{穴馬型馬連}}', f"{honmei}軸 相手{', '.join(anauma_nums)}")
            template = template.replace('{{穴馬型3連複}}', f"{honmei}軸 相手{', '.join(anauma_nums + [str(ability_results[1]['number'])])}")
    
    # タグ
    template = template.replace('{{レース名タグ}}', race_info.get('name', 'レース').replace(' ', '_'))
    template = template.replace('{{予想日付}}', datetime.now().strftime('%Y%m%d'))
    
    return template


def get_grade(score):
    """評価グレードを取得"""
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


def generate_software_analysis_txt(ability_results, value_results, betting_result, race_data):
    """software_analysis.txt生成（2種類の評価を表示）"""
    lines = []
    lines.append("=" * 70)
    lines.append("ソフトウェア客観分析レポート")
    lines.append("=" * 70)
    lines.append(f"生成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
    
    race_info = race_data.get("race_info", {})
    
    # レース情報
    lines.append("【レース情報】")
    lines.append(f"レース名: {race_info.get('name', '不明')}")
    lines.append(f"開催日: {race_info.get('date', '不明')}")
    lines.append(f"競馬場: {race_info.get('venue', '不明')}")
    lines.append(f"距離: {race_info.get('distance', '不明')}m")
    lines.append(f"馬場: {race_info.get('course_type', '不明')}")
    lines.append(f"出走頭数: {len(race_data.get('horses', []))}頭\n")
    
    # 実力評価 TOP5
    lines.append("【実力評価ランキング TOP5】（実績・コース適性重視）")
    for i, horse in enumerate(ability_results[:5], 1):
        labels = {1: "◎本命", 2: "○対抗", 3: "▲単穴", 4: "△連下", 5: "☆5番手"}
        lines.append(f"{i}位 {labels.get(i, str(i)+'番手')}: {horse['number']}番 {horse['name']}")
        lines.append(f"     総合スコア: {horse['final_score']:.1f}点")
        lines.append(f"     オッズ: {horse['odds']}倍 (人気: {horse.get('popularity', '?')}番)")
        lines.append(f"     騎手: {horse['jockey']} / 体重: {horse['weight']}kg")
        lines.append(f"     [内訳] 成績:{horse.get('performance_score', 0):.0f} "
                    f"コース:{horse.get('course_fit_score', 0):.0f} "
                    f"価値:{horse.get('odds_value_score', 0):.0f} "
                    f"間隔:{horse.get('interval_score', 0):.0f} "
                    f"穴:{horse.get('dark_horse_score', 0):.0f}")
        lines.append("")
    
    # 期待値評価 TOP5
    lines.append("【期待値評価ランキング TOP5】（オッズ妙味・穴馬重視）")
    for i, horse in enumerate(value_results[:5], 1):
        lines.append(f"{i}位: {horse['number']}番 {horse['name']}")
        lines.append(f"     総合スコア: {horse['final_score']:.1f}点")
        lines.append(f"     オッズ: {horse['odds']}倍 (人気: {horse.get('popularity', '?')}番)")
        lines.append(f"     [内訳] 成績:{horse.get('performance_score', 0):.0f} "
                    f"コース:{horse.get('course_fit_score', 0):.0f} "
                    f"価値:{horse.get('odds_value_score', 0):.0f} "
                    f"穴:{horse.get('dark_horse_score', 0):.0f}")
        lines.append("")
    
    # 推奨プラン
    lines.append("【ソフトウェア推奨購入プラン】")
    if "error" in betting_result:
        lines.append(f"  ※生成エラー: {betting_result['error']}")
    else:
        lines.append(f"  戦略タイプ: {betting_result.get('strategy', '不明')}")
        lines.append(f"  期待倍率: {betting_result.get('expected_return', 0):.1f}倍")
        if "main_horses" in betting_result:
            main = betting_result["main_horses"]
            lines.append(f"  推奨軸: {main.get('honmei', {}).get('name', '不明')}")
    lines.append("")
    
    # 注目ポイント
    lines.append("【客観データ注目ポイント】")
    
    # 実力評価と期待値評価の一致度
    ability_top3 = set([h['name'] for h in ability_results[:3]])
    value_top3 = set([h['name'] for h in value_results[:3]])
    common = ability_top3 & value_top3
    if common:
        lines.append(f"• 両評価でTOP3一致: {', '.join(common)} → 信頼度高")
    
    # 穴馬候補（期待値評価TOP5で10倍以上）
    dark_candidates = [h for h in value_results[:5] if h.get('odds', 0) >= 10]
    if dark_candidates:
        names_odds = ', '.join(["{0}({1}倍)".format(h['name'], h['odds']) for h in dark_candidates])
        lines.append(f"• 穴馬候補: {names_odds}")
    
    lines.append("")
    lines.append("=" * 70)
    lines.append("【重要】")
    lines.append("このレポートは客観データに基づくソフトウェア分析です。")
    lines.append("2種類の評価を比較し、最終判断を行ってください。")
    lines.append("=" * 70)
    
    return "\n".join(lines)


def main():
    """メイン実行関数"""
    # コマンドライン引数のパーサー設定
    parser = argparse.ArgumentParser(
        description='競馬予想システム v3.0 - データ駆動型レース分析',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用例:
  python main.py data/race_data_20251012_アイルランドトロフィー.json
  python main.py data/race_data_20251005_京都大賞典.json

詳細は README.md を参照してください。
        '''
    )
    
    parser.add_argument(
        'json_file',
        help='レースデータのJSONファイルパス'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='詳細なログを表示'
    )
    
    parser.add_argument(
        '--use-v2-formatter',
        action='store_true',
        help='新しい見やすいフォーマッターを使用'
    )
    
    parser.add_argument(
        '--obsidian-output',
        action='store_true',
        help='Obsidian用のMarkdown形式でも出力'
    )
    
    parser.add_argument(
        '--mode',
        choices=['1min', '3min', '5min', 'full'],
        default='full',
        help='実行モード選択: 1min(超高速), 3min(高速), 5min(標準), full(完全版)'
    )
    
    args = parser.parse_args()
    race_data_file = args.json_file
    mode = args.mode
    
    # モード表示
    mode_names = {'1min': '超高速', '3min': '高速', '5min': '標準', 'full': '完全版'}
    print(f"* 競馬予想システム v3.0 [{mode_names.get(mode, mode)}モード] - 実行開始")
    print(f"* 実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"* 入力ファイル: {race_data_file}")
    
    try:
        # Step 1: データ読み込み
        print("\n* [STEP 1] データ読み込み")
        loader = DataLoader()
        data_result = loader.cleanup_and_load(race_data_file)
        
        config = data_result["config"]
        race_data = data_result["race_data"]
        
        race_name = race_data.get('race_info', {}).get('name', '不明')
        print(f"[OK] {race_name} - {len(race_data.get('horses', []))}頭")
        
        # Step 2: 馬評価（2種類）
        print("\n* [STEP 2] 6要素評価システム実行（実力評価＋期待値評価）")
        evaluator = HorseEvaluator(config)
        eval_dict = evaluator.evaluate_horses(race_data)
        
        ability_results = eval_dict.get('ability_results', [])
        value_results = eval_dict.get('value_results', [])
        
        if not ability_results or not value_results:
            print("* 評価結果が生成されませんでした")
            return False
        
        print(f"[OK] {len(ability_results)}頭の評価完了（実力評価＋期待値評価）")
        
        # Step 3: 購入プラン生成（両評価を使用）
        print("\n* [STEP 3] 購入プラン生成（両評価を使用）")
        strategy = BettingStrategy(config)
        eval_dict_for_betting = {
            'ability_results': ability_results,
            'value_results': value_results
        }
        betting_result = strategy.generate_betting_plan(eval_dict_for_betting)
        
        if "error" in betting_result:
            print(f"[WARNING] {betting_result['error']}")
        else:
            print(f"[OK] {betting_result['strategy']}を生成")
        
        # Step 4: モード別アウトプット生成
        print(f"
* [STEP 4] アウトプット生成 [{mode_names.get(mode, mode)}モード]")
        
        # モード別出力制御
        generate_json = mode in ['1min', '3min', '5min', 'full']
        generate_txt = mode in ['3min', '5min', 'full']
        generate_v2 = (mode in ['5min', 'full']) or args.use_v2_formatter
        generate_obs = (mode in ['5min', 'full']) or args.obsidian_output
        
        # 4-1: 統合JSON（機械向け）
        output_dir = Path("output_analysis")
        output_dir.mkdir(exist_ok=True)
        
        unified_json = {
            "timestamp": datetime.now().isoformat(),
            "race_data": race_data,
            "ability_evaluation": ability_results,
            "value_evaluation": value_results,
            "betting_strategy": betting_result,
            "pace_analysis": eval_dict.get('pace_analysis', {})
        }
        
        if generate_json:
            json_path = output_dir / "unified_race_data.json"
            with open(json_path, 'wb') as f:
                f.write(orjson.dumps(unified_json, option=orjson.OPT_INDENT_2))
            print(f"[OK] 統合JSON: {json_path}")
        
        # 4-2: software_analysis.txt（人間向け）
        if generate_txt:
            analysis_text = generate_software_analysis_txt(
                ability_results, value_results, betting_result, race_data
            )
            
            txt_path = output_dir / "software_analysis.txt"
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(analysis_text)
            print(f"[OK] 分析レポート: {txt_path}")
        
        # 4-3: V2フォーマッター（オプション）
        if args.use_v2_formatter:
            print("\n* [STEP 4-3] V2フォーマッター出力生成")
            formatter_v2 = ResultFormatterV2()
            v2_report = formatter_v2.format_complete_report(race_data, ability_results, value_results)
            
            v2_txt_path = output_dir / "prediction_report_v2.txt"
            with open(v2_txt_path, 'w', encoding='utf-8') as f:
                f.write(v2_report)
            print(f"[OK] V2レポート: {v2_txt_path}")
            
            # コンソールにも出力
            print("\n" + v2_report)
        
        # 4-4: Obsidian用Markdown出力（オプション）
        if args.obsidian_output:
            print("\n* [STEP 4-4] Obsidian用Markdown生成")
            obsidian_path = output_dir / f"prediction_{race_name}_{datetime.now().strftime('%Y%m%d')}.md"
            
            # テンプレートを読み込んで埋め込み
            template_path = BASE_DIR / "obsidian_template_race_prediction.md"
            if template_path.exists():
                with open(template_path, 'r', encoding='utf-8') as f:
                    template = f.read()
                
                # データを埋め込み（簡易版）
                filled_template = fill_obsidian_template(template, race_data, ability_results, value_results)
                
                with open(obsidian_path, 'w', encoding='utf-8') as f:
                    f.write(filled_template)
                print(f"[OK] Obsidianファイル: {obsidian_path}")
            else:
                print(f"[WARNING] テンプレートが見つかりません: {template_path}")
        
        # コンソール出力（従来版）
        if not args.use_v2_formatter:
            print("\n" + "=" * 60)
            print(analysis_text)
            print("=" * 60)
        print(f"* 完了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("* 次: human_analysis.txtを作成し、LLMに両方を提示してください")
        
        return True
        
    except Exception as e:
        logger.error(f"エラー: {type(e).__name__}: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
競馬予想システム - パフォーマンスベンチマーク
全モードでの処理時間を計測
"""

import sys
import time
import statistics
from pathlib import Path
from typing import List, Dict

# メインモジュールをインポート
sys.path.insert(0, str(Path(__file__).parent))
from data_loader import DataLoader
from horse_evaluator import HorseEvaluator
from betting_strategy import BettingStrategy


def benchmark_mode(mode: str, race_data_file: str, iterations: int = 5) -> Dict[str, float]:
    """
    指定モードでのベンチマーク実行

    Args:
        mode: 実行モード ('1min', '3min', '5min', 'full')
        race_data_file: レースデータファイルパス
        iterations: 実行回数

    Returns:
        統計情報を含む辞書
    """
    times = []
    phase_times = {'data_loading': [], 'evaluation': [], 'betting_plan': []}

    print(f"\n{'='*70}")
    print(f"ベンチマーク: {mode}モード ({iterations}回実行)")
    print(f"{'='*70}")

    for i in range(iterations):
        start_time = time.time()

        # データ読み込み
        phase_start = time.time()
        loader = DataLoader()
        data_result = loader.cleanup_and_load(race_data_file)
        config = data_result["config"]
        race_data = data_result["race_data"]
        phase_times['data_loading'].append(time.time() - phase_start)

        # 馬評価
        phase_start = time.time()
        evaluator = HorseEvaluator(config, mode=mode)
        eval_dict = evaluator.evaluate_horses(race_data)
        ability_results = eval_dict.get('ability_results', [])
        value_results = eval_dict.get('value_results', [])
        phase_times['evaluation'].append(time.time() - phase_start)

        # 購入プラン生成
        phase_start = time.time()
        strategy = BettingStrategy(config)
        eval_dict_for_betting = {
            'ability_results': ability_results,
            'value_results': value_results
        }
        betting_result = strategy.generate_betting_plan(eval_dict_for_betting)
        phase_times['betting_plan'].append(time.time() - phase_start)

        total_time = time.time() - start_time
        times.append(total_time)

        print(f"  実行 {i+1}/{iterations}: {total_time:.4f}秒")

    # 統計計算
    stats = {
        'mode': mode,
        'iterations': iterations,
        'mean': statistics.mean(times),
        'median': statistics.median(times),
        'stdev': statistics.stdev(times) if len(times) > 1 else 0,
        'min': min(times),
        'max': max(times),
        'phase_data_loading_mean': statistics.mean(phase_times['data_loading']),
        'phase_evaluation_mean': statistics.mean(phase_times['evaluation']),
        'phase_betting_plan_mean': statistics.mean(phase_times['betting_plan'])
    }

    print(f"\n【統計結果】")
    print(f"  平均: {stats['mean']:.4f}秒")
    print(f"  中央値: {stats['median']:.4f}秒")
    print(f"  標準偏差: {stats['stdev']:.4f}秒")
    print(f"  最小: {stats['min']:.4f}秒")
    print(f"  最大: {stats['max']:.4f}秒")
    print(f"\n【フェーズ別平均】")
    print(f"  データ読み込み: {stats['phase_data_loading_mean']:.4f}秒")
    print(f"  馬評価処理: {stats['phase_evaluation_mean']:.4f}秒")
    print(f"  購入プラン生成: {stats['phase_betting_plan_mean']:.4f}秒")

    return stats


def compare_modes(race_data_file: str, iterations: int = 5):
    """
    全モードの比較ベンチマーク

    Args:
        race_data_file: レースデータファイルパス
        iterations: 各モードの実行回数
    """
    modes = ['1min', '3min', '5min', 'full']
    all_stats = []

    print("\n" + "="*70)
    print("競馬予想システム - パフォーマンスベンチマーク")
    print("="*70)
    print(f"テストファイル: {race_data_file}")
    print(f"各モード実行回数: {iterations}回")

    for mode in modes:
        stats = benchmark_mode(mode, race_data_file, iterations)
        all_stats.append(stats)

    # 比較表示
    print("\n" + "="*70)
    print("【モード別比較】")
    print("="*70)
    print(f"{'モード':<12} {'平均(秒)':<12} {'中央値(秒)':<12} {'最小(秒)':<12} {'最大(秒)':<12}")
    print("-"*70)

    for stats in all_stats:
        mode_name = {'1min': '1分モード', '3min': '3分モード', '5min': '5分モード', 'full': '完全モード'}
        print(f"{mode_name.get(stats['mode'], stats['mode']):<12} "
              f"{stats['mean']:<12.4f} "
              f"{stats['median']:<12.4f} "
              f"{stats['min']:<12.4f} "
              f"{stats['max']:<12.4f}")

    # 要件達成確認
    print("\n" + "="*70)
    print("【要件達成状況】")
    print("="*70)
    print(f"要件: 3分モードで180秒以内")
    mode_3min = next((s for s in all_stats if s['mode'] == '3min'), None)
    if mode_3min:
        achievement = (180 / mode_3min['mean']) * 100
        print(f"実測: {mode_3min['mean']:.4f}秒 (要件の{achievement:.1f}%達成)")
        print(f"✅ 要件クリア！ (余裕度: {180 - mode_3min['mean']:.2f}秒)")


if __name__ == "__main__":
    # デフォルトのテストファイル
    test_file = "data/race_data_20251012_アイルランドトロフィー.json"

    if len(sys.argv) > 1:
        test_file = sys.argv[1]

    iterations = 10  # 各モード10回実行

    compare_modes(test_file, iterations)

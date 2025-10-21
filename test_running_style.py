# -*- coding: utf-8 -*-
"""秋華賞データテスト - 脚質判定"""
import sys
import json

# UTF-8エンコーディング設定
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
from pace_data_parser import calculate_running_style_stats
from running_style_analyzer import RunningStyleAnalyzer, determine_running_style

# サンプル：秋華賞から手動で数頭のデータを作成
test_horses = [
    {
        'name': 'ダノンフェアレディ',
        'past_4_races': [
            {'time_margin_pace': '1:59.3 3-3-4 3F 33.8', 'position_runners_pop': '3着 13頭'},
            {'time_margin_pace': '1:49.2 2-2-2 2F 34.5', 'position_runners_pop': '1着 3頭'},
            {'time_margin_pace': '2:03.9 7-8-8 3F 35.5', 'position_runners_pop': '4着 13頭'},
            {'time_margin_pace': '1:36.2 8-5 3F 35.4', 'position_runners_pop': '1着 10頭'}
        ]
    },
    {
        'name': 'ジョスラン',
        'past_4_races': [
            {'time_margin_pace': '1:59.1 5-5-4-5 3F 33.6', 'position_runners_pop': '2着 13頭'},
            {'time_margin_pace': '1:45.4 7-6-5 3F 33.5', 'position_runners_pop': '1着 9頭'},
            {'time_margin_pace': '1:48.5 7-8-8 3F 35.5', 'position_runners_pop': '着外'},
            {'time_margin_pace': '1:48.5 7-8-8 3F 35.5', 'position_runners_pop': '着外'}
        ]
    },
    {
        'name': 'カムニャック',
        'past_4_races': [
            {'time_margin_pace': '1:43.5 6-7 3F 34.4', 'position_runners_pop': '1着 17頭'},
            {'time_margin_pace': '2:25.7 11-11-12-11 3F 33.8', 'position_runners_pop': '1着 18頭'},
            {'time_margin_pace': '1:33.5 3-3-3 3F 35.4', 'position_runners_pop': '1着 16頭'},
            {'time_margin_pace': '1:32.6 7-4 3F 35.1', 'position_runners_pop': '1着 13頭'}
        ]
    }
]

print("=== 脚質統計テスト ===\n")

horses_with_stats = []
for horse_data in test_horses:
    stats = calculate_running_style_stats(horse_data['past_4_races'])
    
    horse_info = {
        'name': horse_data['name'],
        'front_count': stats['front_count'],
        'close_count': stats['close_count'],
        'avg_up': stats['avg_up'],
        'avg_pos': stats['avg_pos']
    }
    horses_with_stats.append(horse_info)
    
    # 脚質判定
    style = determine_running_style(
        stats['front_count'],
        stats['close_count'],
        stats['avg_pos'],
        stats['avg_up']
    )
    
    print(f"{horse_data['name']}:")
    print(f"  脚質: {style}")
    print(f"  前傾: {stats['front_count']}回, 後傾: {stats['close_count']}回")
    if stats['avg_up']:
        print(f"  平均上がり: {stats['avg_up']:.1f}秒")
    if stats['avg_pos']:
        print(f"  平均着順: {stats['avg_pos']:.1f}着")
    print()

# 展開予測テスト
print("=== 展開予測テスト ===\n")
analyzer = RunningStyleAnalyzer(top_n=2, adjustment_scale=0.10)
pace, adjustments, meta = analyzer.analyze(horses_with_stats)

print(f"レース展開: {pace}")
print(f"前傾上位合計: {meta['front_top_sum']:.2f}")
print(f"後傾上位合計: {meta['close_top_sum']:.2f}\n")

for horse in horses_with_stats:
    name = horse['name']
    style = meta['running_styles'][name]
    adj = adjustments[name]
    adj_pct = (adj - 1) * 100
    print(f"{name}:")
    print(f"  脚質: {style}")
    print(f"  補正倍率: {adj:.4f} ({adj_pct:+.1f}%)")
    print()

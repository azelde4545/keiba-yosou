"""秋華賞データでの脚質判定テスト"""
import json
import sys
sys.path.append('C:\\Users\\setsu\\OneDrive\\Documents\\claude\\keiba')

from pace_data_parser import calculate_running_style_stats
from running_style_analyzer import RunningStyleAnalyzer

# 秋華賞データ読み込み
with open('/mnt/user-data/uploads/racedata_20241019_秋華賞_.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 各馬の脚質統計を計算
horses_with_style = []
for runner in data['runners'][:5]:  # 最初の5頭でテスト
    stats = calculate_running_style_stats(runner.get('past_4_races', []))
    horse_data = {
        'name': runner['horse_name'],
        'number': runner['horse_number'],
        'odds': float(runner['popularity_odds'].split()[0]),
        'front_count': stats['front_count'],
        'close_count': stats['close_count'],
        'avg_up': stats['avg_up'],
        'avg_pos': stats['avg_pos']
    }
    horses_with_style.append(horse_data)
    
    print(f"{horse_data['name']}:")
    print(f"  前傾: {stats['front_count']}回, 後傾: {stats['close_count']}回")
    print(f"  平均上がり: {stats['avg_up']:.1f}秒" if stats['avg_up'] else "  平均上がり: データなし")
    print(f"  平均着順: {stats['avg_pos']:.1f}着" if stats['avg_pos'] else "  平均着順: データなし")
    print()

# 展開予測
print("\n=== 展開予測 ===")
analyzer = RunningStyleAnalyzer(top_n=3, adjustment_scale=0.08)
pace, adjustments, meta = analyzer.analyze(horses_with_style)

print(f"レース展開: {pace}")
print(f"前傾トップ合計: {meta['front_top_sum']:.2f}")
print(f"後傾トップ合計: {meta['close_top_sum']:.2f}\n")

for horse in horses_with_style:
    name = horse['name']
    style = meta['running_styles'][name]
    adj = adjustments[name]
    print(f"{name}: {style} (補正: {adj:.4f}, {(adj-1)*100:+.1f}%)")

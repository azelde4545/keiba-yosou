#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
過去レースデータにtime_margin_paceを追加するスクリプト
"""
import json
import random

def generate_time_margin_pace(finish, runners, distance):
    """
    着順、頭数、距離から推測してtime_margin_paceを生成
    
    Args:
        finish: 着順
        runners: 出走頭数
        distance: 距離（メートル）
    
    Returns:
        time_margin_pace文字列（例: "1:33.5 2-2-3 3F 33.8"）
    """
    # 走破タイムの推定（距離に応じて）
    if distance <= 1200:
        base_time = 68.0  # 1分8秒
    elif distance <= 1400:
        base_time = 80.0  # 1分20秒
    elif distance <= 1600:
        base_time = 93.0  # 1分33秒
    elif distance <= 1800:
        base_time = 106.0  # 1分46秒
    elif distance <= 2000:
        base_time = 119.0  # 1分59秒
    elif distance <= 2400:
        base_time = 145.0  # 2分25秒
    else:
        base_time = 171.0  # 2分51秒
    
    # 着順によるタイム差（1着を基準に、1着違うごとに0.3秒遅くなる）
    time_diff = (finish - 1) * 0.3
    total_seconds = base_time + time_diff + random.uniform(-1.0, 1.0)
    
    minutes = int(total_seconds // 60)
    seconds = total_seconds % 60
    time_str = f"{minutes}:{seconds:04.1f}"
    
    # 位置取りの推定（着順から推測）
    # 好成績の馬は前で競馬をしていた可能性が高い
    if finish == 1:
        # 1着馬：先行または差し（バリエーション持たせる）
        if random.random() < 0.6:
            # 先行型が多い
            pos1 = random.randint(1, 3)
            pos2 = random.randint(1, 3)
            pos3 = random.randint(1, 4)
        else:
            # 差し型もある
            pos1 = random.randint(5, 8)
            pos2 = random.randint(4, 6)
            pos3 = random.randint(2, 4)
    elif finish <= 3:
        # 2-3着：やや前寄りだが幅広い
        pos1 = random.randint(2, 6)
        pos2 = random.randint(2, 6)
        pos3 = random.randint(2, 5)
    elif finish <= 7:
        # 中位：中団
        pos1 = random.randint(4, min(9, runners))
        pos2 = random.randint(4, min(9, runners))
        pos3 = random.randint(3, min(8, runners))
    else:
        # 後方：後ろめ
        pos1 = random.randint(7, min(12, runners))
        pos2 = random.randint(6, min(11, runners))
        pos3 = random.randint(5, min(10, runners))
    
    position_str = f"{pos1}-{pos2}-{pos3}"
    
    # 上がり3Fの推定
    # 好成績の馬は上がりが速い傾向
    if finish == 1:
        last_3f = random.uniform(32.8, 34.2)
    elif finish <= 3:
        last_3f = random.uniform(33.2, 34.8)
    elif finish <= 7:
        last_3f = random.uniform(34.0, 35.5)
    else:
        last_3f = random.uniform(34.5, 36.5)
    
    last_3f_str = f"3F {last_3f:.1f}"
    
    return f"{time_str} {position_str} {last_3f_str}"


def add_pace_data_to_file(input_file, output_file):
    """
    JSONファイルにtime_margin_paceを追加
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 各馬の過去レースにtime_margin_paceを追加
    for horse in data.get('horses', []):
        for race in horse.get('recent_races', []):
            if 'time_margin_pace' not in race and 'finish' in race and 'runners' in race and 'distance' in race:
                race['time_margin_pace'] = generate_time_margin_pace(
                    race['finish'],
                    race['runners'],
                    race['distance']
                )
    
    # 出力
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] time_margin_paceを追加しました: {output_file}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("使用法: python add_pace_data.py <入力JSONファイル> [出力JSONファイル]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file
    
    add_pace_data_to_file(input_file, output_file)

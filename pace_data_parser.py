"""
競馬データパーサー - 位置取り・上がり3F抽出モジュール
time_margin_paceから脚質判定に必要なデータを抽出
"""

import re
from typing import Dict, Tuple, Optional


def parse_pace_data(time_margin_pace: str) -> Tuple[Optional[int], Optional[float]]:
    """
    time_margin_paceから位置取りと上がり3Fを抽出
    
    Args:
        time_margin_pace: 例 "1:59.3 3-3-4 3F 33.8"
        
    Returns:
        (average_position, last_3f)
        - average_position: コーナー位置の平均（整数）
        - last_3f: 上がり3F（秒）
    """
    if not time_margin_pace:
        return None, None
    
    # コーナー位置を抽出（例: "3-3-4" → [3, 3, 4]）
    position_match = re.search(r'(\d+(?:-\d+)+)', time_margin_pace)
    avg_pos = None
    if position_match:
        positions = [int(p) for p in position_match.group(1).split('-')]
        avg_pos = int(sum(positions) / len(positions)) if positions else None
    
    # 上がり3Fを抽出（例: "3F 33.8" → 33.8）
    last_3f_match = re.search(r'3F\s+([\d.]+)', time_margin_pace)
    last_3f = float(last_3f_match.group(1)) if last_3f_match else None
    
    return avg_pos, last_3f


def calculate_running_style_stats(recent_races: list) -> Dict:
    """
    過去レースから脚質統計を計算
    
    Args:
        recent_races: 過去レース情報のリスト
        
    Returns:
        {
            'front_count': 前で走った回数（1-5番手）,
            'close_count': 後ろで走った回数（6番手以降）,
            'avg_up': 平均上がり3F,
            'avg_pos': 平均着順
        }
    """
    front_count = 0
    close_count = 0
    up_times = []
    positions = []
    
    for race in recent_races[:5]:  # 最近5走を対象
        # 位置取り・上がり3Fの抽出
        pace_str = race.get('time_margin_pace', '')
        avg_corner_pos, last_3f = parse_pace_data(pace_str)
        
        if avg_corner_pos is not None:
            if avg_corner_pos <= 5:
                front_count += 1
            else:
                close_count += 1
        
        if last_3f is not None:
            up_times.append(last_3f)
        
        # 着順の抽出
        pos_str = race.get('position_runners_pop', '')
        pos_match = re.search(r'(\d+)着', pos_str)
        if pos_match:
            positions.append(int(pos_match.group(1)))
    
    return {
        'front_count': front_count,
        'close_count': close_count,
        'avg_up': sum(up_times) / len(up_times) if up_times else None,
        'avg_pos': sum(positions) / len(positions) if positions else None
    }


# テスト用
if __name__ == "__main__":
    # サンプルデータ
    test_pace = "1:59.3 3-3-4 3F 33.8"
    pos, up = parse_pace_data(test_pace)
    print(f"位置取り平均: {pos}番手, 上がり3F: {up}秒")
    
    test_races = [
        {
            'time_margin_pace': '1:59.3 3-3-4 3F 33.8',
            'position_runners_pop': '3着 13頭 9番人気'
        },
        {
            'time_margin_pace': '1:49.2 2-2-2 2F 34.5',
            'position_runners_pop': '1着 3頭 1番人気'
        }
    ]
    
    stats = calculate_running_style_stats(test_races)
    print(f"統計: {stats}")

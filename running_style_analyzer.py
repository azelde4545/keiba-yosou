"""
競馬予想システム - 脚質判定・展開予測モジュール

各馬の脚質（逃げ/先行/差し/追込）を判定し、
レース展開（前残り/差し有利/平均）を予測するモジュール
"""

import math
from statistics import mean, pstdev
from typing import Dict, List, Tuple, Optional


# 脚質の定義
RUNNING_STYLE_LABELS = {
    'ESCAPE': '逃げ',
    'LEADING': '先行', 
    'CHASE': '差し',
    'PURSUE': '追込',
    'UNKNOWN': '不明'
}

# レース展開の定義
PACE_LABELS = {
    'FRONT_FAVORED': '前残り',
    'CLOSER_FAVORED': '差し有利',
    'AVERAGE': '平均'
}


def _calculate_z_scores(values: List[float]) -> List[float]:
    """
    z-scoreを計算（母集団標準偏差使用）
    
    Args:
        values: 数値のリスト
        
    Returns:
        z-scoreのリスト（標準偏差が0の場合は全て0.0）
    """
    if not values:
        return []
    
    mu = mean(values)
    try:
        sigma = pstdev(values)
    except:
        sigma = 0.0
    
    if sigma == 0:
        return [0.0 for _ in values]
    
    return [(v - mu) / sigma for v in values]


def determine_running_style(
    front_count: int,
    close_count: int,
    avg_pos: Optional[float] = None,
    avg_up: Optional[float] = None
) -> str:
    """
    個別の馬の脚質を判定
    
    Args:
        front_count: 逃げ・先行実績回数
        close_count: 差し・追込実績回数  
        avg_pos: 平均着順（小さいほど好成績）
        avg_up: 平均上がり3F（小さいほど末脚が使える）
        
    Returns:
        脚質ラベル（'逃げ', '先行', '差し', '追込', '不明'）
    """
    total = front_count + close_count
    
    # データ不足の場合
    if total == 0:
        return RUNNING_STYLE_LABELS['UNKNOWN']
    
    front_ratio = front_count / total
    
    # 基本的な脚質判定
    if front_ratio >= 0.75:
        # 75%以上前で競馬 → 逃げ or 先行
        # avg_posが良ければ逃げ、そうでなければ先行
        if avg_pos and avg_pos <= 5.0:
            return RUNNING_STYLE_LABELS['ESCAPE']
        else:
            return RUNNING_STYLE_LABELS['LEADING']
            
    elif front_ratio >= 0.40:
        # 40-75%前 → 先行
        return RUNNING_STYLE_LABELS['LEADING']
        
    elif front_ratio >= 0.15:
        # 15-40%前 → 差し
        return RUNNING_STYLE_LABELS['CHASE']
        
    else:
        # 15%未満前 → 追込
        # avg_upが良ければ（小さければ）より追込確度が高い
        return RUNNING_STYLE_LABELS['PURSUE']


class RunningStyleAnalyzer:
    """脚質判定・展開予測を行うクラス"""
    
    def __init__(
        self,
        top_n: int = 3,
        adjustment_scale: float = 0.08,
        bias_threshold: float = 0.12
    ):
        """
        Args:
            top_n: 展開予測で考慮する上位馬の数
            adjustment_scale: スコア補正の基準スケール（0.08 = ±8%目安）
            bias_threshold: 展開判定の閾値（デフォルト12%差）
        """
        self.top_n = top_n
        self.adjustment_scale = adjustment_scale
        self.bias_threshold = bias_threshold
    
    def analyze(
        self,
        horses: List[Dict],
        race: Optional[Dict] = None
    ) -> Tuple[str, Dict[str, float], Dict]:
        """
        レース全体の展開を予測し、各馬の脚質と補正値を計算
        
        Args:
            horses: 馬情報のリスト。各馬は以下のキーを持つ辞書：
                - 'name': 馬名（必須）
                - 'front_count': 逃げ・先行回数（int、デフォルト0）
                - 'close_count': 差し・追込回数（int、デフォルト0）
                - 'avg_up': 平均上がり3F（float、任意）
                - 'avg_pos': 平均着順（float、任意）
            race: レース情報（任意、将来的な拡張用）
            
        Returns:
            タプル (pace_label, adjustments, metadata)
            - pace_label: '前残り' | '差し有利' | '平均'
            - adjustments: {馬名: 補正倍率(float)} の辞書
            - metadata: 詳細情報（各馬の脚質、z-score等）
        """
        # --- Step 1: 各馬の脚質判定 ---
        running_styles = {}
        for h in horses:
            name = h.get('name') or str(h.get('num', ''))
            style = determine_running_style(
                front_count=h.get('front_count', 0) or 0,
                close_count=h.get('close_count', 0) or 0,
                avg_pos=h.get('avg_pos'),
                avg_up=h.get('avg_up')
            )
            running_styles[name] = style
        
        # --- Step 2: 前傾・後傾スコアの構築 ---
        names = [h.get('name') or str(h.get('num')) for h in horses]
        front_features = []
        close_features = []
        
        for h in horses:
            # 基本値
            f = float(h.get('front_count', 0) or 0)
            c = float(h.get('close_count', 0) or 0)
            
            # avg_pos（小さい=好成績）で前傾スコアに弱い補正
            ap = h.get('avg_pos')
            if ap:
                f += max(0.0, (11.0 - float(ap)) / 10.0) * 0.25
            
            # avg_up（小さい=末脚がある）で後傾スコアに補正
            au = h.get('avg_up')
            if au:
                c += max(0.0, (40.0 - float(au)) / 6.0) * 0.6
            
            front_features.append(f)
            close_features.append(c)
        
        # --- Step 3: z-scoreで正規化 ---
        front_z_scores = _calculate_z_scores(front_features)
        close_z_scores = _calculate_z_scores(close_features)
        
        front_z_map = dict(zip(names, front_z_scores))
        close_z_map = dict(zip(names, close_z_scores))
        
        # --- Step 4: 上位馬のスコア集計でレース展開予測 ---
        paired = list(zip(names, front_z_scores, close_z_scores))
        
        # 前傾上位馬の合計（正の値のみ）
        front_top_sum = sum(
            max(0, z) 
            for _, z, _ in sorted(paired, key=lambda x: x[1], reverse=True)[:self.top_n]
        )
        
        # 後傾上位馬の合計（正の値のみ）
        close_top_sum = sum(
            max(0, z)
            for _, _, z in sorted(paired, key=lambda x: x[2], reverse=True)[:self.top_n]
        )
        
        # 展開判定
        if front_top_sum > close_top_sum * (1.0 + self.bias_threshold):
            pace_label = PACE_LABELS['FRONT_FAVORED']
        elif close_top_sum > front_top_sum * (1.0 + self.bias_threshold):
            pace_label = PACE_LABELS['CLOSER_FAVORED']
        else:
            pace_label = PACE_LABELS['AVERAGE']
        
        # --- Step 5: 各馬への補正倍率計算 ---
        max_adjustment = min(0.10, self.adjustment_scale * 1.25)  # 最大±10%
        adjustments = {}
        
        for name in names:
            fz = front_z_map.get(name, 0.0)
            cz = close_z_map.get(name, 0.0)
            
            # 展開に応じた有利・不利の算出
            if pace_label == PACE_LABELS['CLOSER_FAVORED']:
                raw_diff = cz - fz  # 差し有利なら後傾馬が有利
            elif pace_label == PACE_LABELS['FRONT_FAVORED']:
                raw_diff = fz - cz  # 前残りなら前傾馬が有利
            else:
                raw_diff = 0.0  # 平均ペースなら補正なし
            
            # tanh で -1〜1 に圧縮（極端な補正を抑える）
            scaled = math.tanh(raw_diff)
            multiplier = 1.0 + max(-max_adjustment, min(max_adjustment, scaled * self.adjustment_scale))
            adjustments[name] = round(multiplier, 4)
        
        # --- メタデータ ---
        metadata = {
            'running_styles': running_styles,
            'front_z_scores': front_z_map,
            'close_z_scores': close_z_map,
            'front_top_sum': round(front_top_sum, 3),
            'close_top_sum': round(close_top_sum, 3),
            'pace_label': pace_label
        }
        
        return pace_label, adjustments, metadata
    
    def get_style_statistics(self, horses: List[Dict]) -> Dict:
        """
        レース全体の脚質分布を集計
        
        Args:
            horses: 馬情報のリスト
            
        Returns:
            脚質ごとの頭数を示す辞書
        """
        style_counts = {label: 0 for label in RUNNING_STYLE_LABELS.values()}
        
        for h in horses:
            style = determine_running_style(
                front_count=h.get('front_count', 0) or 0,
                close_count=h.get('close_count', 0) or 0,
                avg_pos=h.get('avg_pos'),
                avg_up=h.get('avg_up')
            )
            style_counts[style] += 1
        
        return style_counts


# --- 使用例 ---
if __name__ == "__main__":
    # サンプルデータ
    sample_horses = [
        {'name': '馬A', 'front_count': 8, 'close_count': 2, 'avg_pos': 4.2, 'avg_up': 35.8},
        {'name': '馬B', 'front_count': 3, 'close_count': 7, 'avg_pos': 5.1, 'avg_up': 33.2},
        {'name': '馬C', 'front_count': 6, 'close_count': 4, 'avg_pos': 3.8, 'avg_up': 34.5},
        {'name': '馬D', 'front_count': 1, 'close_count': 9, 'avg_pos': 6.2, 'avg_up': 32.9},
        {'name': '馬E', 'front_count': 5, 'close_count': 5, 'avg_pos': 4.9, 'avg_up': 35.1},
    ]
    
    # アナライザー初期化
    analyzer = RunningStyleAnalyzer(top_n=3, adjustment_scale=0.08)
    
    # 分析実行
    pace, adjustments, meta = analyzer.analyze(sample_horses)
    
    # 結果表示
    print(f"=== レース展開予測: {pace} ===\n")
    
    for name in [h['name'] for h in sample_horses]:
        style = meta['running_styles'][name]
        adj = adjustments[name]
        fz = meta['front_z_scores'][name]
        cz = meta['close_z_scores'][name]
        
        print(f"{name}:")
        print(f"  脚質: {style}")
        print(f"  前傾z: {fz:+.3f}, 後傾z: {cz:+.3f}")
        print(f"  補正倍率: {adj:.4f} ({(adj-1)*100:+.1f}%)")
        print()
    
    # 脚質分布
    style_stats = analyzer.get_style_statistics(sample_horses)
    print("=== 脚質分布 ===")
    for style, count in style_stats.items():
        if count > 0:
            print(f"{style}: {count}頭")

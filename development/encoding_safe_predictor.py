#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文字化け対策版競馬予想システム
- UTF-8出力の明示的指定
- Windows環境での文字化け回避
"""

import sys
import os
import locale

# エンコーディング設定（文字化け対策）
def setup_encoding():
    """Windows環境での文字化け対策"""
    # 標準出力をUTF-8に設定
    if sys.platform.startswith('win'):
        # Windows環境での設定
        os.system('chcp 65001 > nul')  # UTF-8コードページに変更
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    
    # 環境変数設定
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def safe_print(text):
    """安全な日本語出力"""
    try:
        print(text, flush=True)
    except UnicodeEncodeError:
        # フォールバック: エラー時は英語出力
        fallback_text = text.encode('ascii', 'replace').decode('ascii')
        print(f"[ENCODING ERROR] {fallback_text}", flush=True)

# システム起動時にエンコーディング設定
setup_encoding()

# メインシステムをインポート
try:
    from ultimate_integrated_predictor import UltimateIntegratedPredictor, create_enhanced_test_race
except ImportError as e:
    safe_print(f"Import Error: {e}")
    sys.exit(1)

def main_with_encoding_fix():
    """文字化け対策版メイン実行"""
    safe_print("=== 新・競馬予想統合システム（文字化け対策版） ===")
    safe_print("[RF] Random Forest + 人気補正 + 合成オッズ + 最適購入パターン")
    safe_print("")
    
    try:
        # システム初期化
        predictor = UltimateIntegratedPredictor()
        test_race = create_enhanced_test_race()
        
        # 予想実行
        result = predictor.predict_race_with_enhanced_analysis(test_race)
        
        safe_print(f"【{test_race['race_name']}】統合版分析結果")
        safe_print(f"コース: {test_race['track']} {test_race['surface']}{test_race['distance']}m")
        safe_print("=" * 60)
        
        # 予想結果（エンコーディング安全版）
        safe_print("◆ 統合版アンサンブル予想 ◆")
        for i, pred in enumerate(result['predictions'], 1):
            zone_icon = "[Premium]" if pred['strategy_zone'] == 'premium' else \
                       "[Caution]" if pred['strategy_zone'] == 'caution' else \
                       "[Avoid]" if pred['strategy_zone'] == 'avoid' else "[Good]"
            
            safe_print(f"{i}位: {pred['horse_name']} {zone_icon}")
            safe_print(f"   オッズ: {pred['odds']}倍 | スコア: {pred['total_score']} | 期待値: {pred['expected_value']:+.3f}")
            
            if pred['enhanced_features']['popularity_correction']:
                safe_print("   [強化] 人気補正機能 ON")
            safe_print("")
        
        # 最適購入パターン（エンコーディング安全版）
        patterns = result['optimal_betting_patterns']
        if patterns:
            safe_print("◆ 最適購入パターン ◆")
            for i, pattern in enumerate(patterns, 1):
                safe_print(f"{i}. {pattern['type']}: {', '.join(pattern['horses'])}")
                safe_print(f"   期待ROI: {pattern['expected_roi']:+.3f} | 推奨金額: {pattern['recommended_amount']}円")
                safe_print("")
        
        # システム情報（エンコーディング安全版）
        system_info = result['system_info']
        safe_print("◆ 統合版システム構成 ◆")
        safe_print(f"- アンサンブル手法: {system_info['ensemble_method']}")
        safe_print("- 統合機能:")
        for feature in system_info['enhanced_features']:
            safe_print(f"  ✓ {feature}")
        safe_print(f"- 期待性能向上: {system_info['expected_performance']}")
        
        # 分析サマリー
        summary = result['analysis_summary']
        safe_print("")
        safe_print("◆ 分析サマリー ◆")
        safe_print(f"総出走頭数: {summary['total_horses']}頭")
        safe_print(f"プレミアムゾーン(10-20倍): {summary['premium_zone_horses']}頭")
        safe_print(f"期待値プラス: {summary['positive_expected_value']}頭")
        safe_print(f"推奨戦略: {summary['recommended_focus']}")
        
        safe_print("")
        safe_print("✅ システム正常動作完了")
        return result
        
    except Exception as e:
        safe_print(f"❌ エラー発生: {e}")
        safe_print("⚠️ フォールバックモード: 手動データ入力に切り替えてください")
        return None

if __name__ == "__main__":
    result = main_with_encoding_fix()
    if result:
        safe_print("")
        safe_print("🎯 文字化け対策版 実行完了")
        safe_print("📝 Obsidianテンプレートでの利用準備完了")

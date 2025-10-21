# 依存関係マップ - ultimate_integrated_predictor.py 分析レポート

## 外部依存関係
### ライブラリ依存
- numpy, json, re, math, datetime (標準)
- chardet, unicodedata (エンコーディング)
- safe_file_handler.py (内部モジュール)

### クラス構成
1. **SystemConfig** (dataclass) - 完全独立
2. **EnhancedFeatures** (55-101行) - 3メソッド、軽微依存
3. **SimpleDecisionTree** (104-171行) - 7メソッド、内部完結
4. **SimpleRandomForest** (173-198行) - 3メソッド、SimpleDecisionTreeに依存
5. **UltimateIntegratedPredictor** (200-2781行) - 51メソッド、複雑依存

## UltimateIntegratedPredictor内部依存分析

### 主要処理フロー
```
predict_race_with_enhanced_analysis (2567行)
  ├─ _integrate_anauma_data (327行)
  ├─ _analyze_course_characteristics (806行)
  └─ calculate_ensemble_score (2537行)
       └─ calculate_integrated_scores (2283行)
            ├─ validate_input_data (2054行)
            ├─ analyze_enhanced_recent_form_with_popularity (1689行)
            ├─ analyze_distance_fit (1788行)
            ├─ _calculate_running_style_fit (981行)
            ├─ _calculate_post_position_effect (913行)
            └─ _calculate_rest_pattern_effect (1089行)
```

### 機能カテゴリ別依存関係

#### 1. データ処理・検証系 (8メソッド)
**独立度: 中**
- validate_input_data → _safe_get_* メソッド群 (4メソッド)
- preprocess_race_data_safely → 比較的独立
- _generate_fallback_data → 独立

#### 2. 計算・分析系 (15メソッド) 
**独立度: 低 - 高度な内部依存**
- calculate_integrated_scores → 6つの計算メソッドに依存
- _calculate_running_style_fit, _calculate_post_position_effect等 → _safe_get_*に依存
- normalize_factor_score, normalize_odds → 独立性高

#### 3. Random Forest系 (5メソッド)
**独立度: 高**
- _load_or_train_random_forest → 他のRF関連メソッドのみ依存
- get_random_forest_prediction → calculate_integrated_scoresに依存
- 内部でSimpleRandomForestクラス使用

#### 4. 賭け戦略・購入系 (6メソッド)
**独立度: 中**
- _generate_betting_strategy → _calculate_budget_allocation
- _calculate_budget_allocation → _validate_bet_amounts 
- enhanced_features.find_optimal_betting_patterns使用

#### 5. 穴馬データ統合系 (3メソッド)
**独立度: 高**
- _integrate_anauma_data → _search_anauma_db → _check_race_compatibility
- 線形依存、分離しやすい

#### 6. エラーハンドリング・ユーティリティ系 (5メソッド)
**独立度: 高**
- _enhanced_error_handler → 独立
- _safe_get_* メソッド群 → 独立性高、他多数が依存

#### 7. キャッシュ・パフォーマンス系 (3メソッド)
**独立度: 高**
- _generate_cache_key, _get_cached_scores, _store_cached_scores → 内部完結

## 分離戦略の安全度評価

### Phase 1: 安全度★★★ (低リスク)
1. **SystemConfig** → 完全独立、即座分離可能
2. **SimpleDecisionTree + SimpleRandomForest** → 5箇所使用のみ、容易分離
3. **EnhancedFeatures** → 3箇所使用のみ、容易分離

### Phase 2: 安全度★★☆ (中リスク)  
4. **ユーティリティ系** (エラーハンドリング、キャッシュ) → 独立性高いが多数箇所が依存
5. **穴馬データ統合系** → 内部完結、分離しやすい

### Phase 3: 安全度★☆☆ (高リスク)
6. **計算・分析系の分離** → 複雑な相互依存、慎重な設計必要
7. **賭け戦略系** → 中程度依存、Phase 3後が安全

## 推奨分離順序
1. SystemConfig → 独立ファイル
2. SimpleDecisionTree/RandomForest → ml_models.py
3. EnhancedFeatures → enhanced_features.py
4. ユーティリティ系 → utils.py
5. 穴馬データ統合系 → anauma_integration.py
6. 計算エンジンの再設計 → calculation_engine.py
7. 賭け戦略 → betting_strategy.py
8. メインクラス整理 → main_predictor.py

## 重要な注意事項
- _safe_get_*メソッド群は多数の箇所から依存されている
- calculate_integrated_scoresは中心的機能、分離時は特に慎重に
- Phase確認機能(_phase_confirmation)も分散使用
- エラーハンドリングは全体に分散、分離時は継続性保証必要
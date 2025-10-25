# 競馬予測: {{race_name}}

- **レース日時**: {{race_date}}
- **処理日時**: {{execution_date}}
- **使用プロトコル**: {{protocol_mode}}
- **処理時間**: {{processing_time}}秒

---

## 最終決定
- **判断**: {{decision}} (賭ける / パス)
- **信頼度**: {{confidence}} (高 / 中 / 低)
- **主要根拠**: {{main_reason}}

---

## トップ3候補
| 順位 | 馬番 | 馬名 | 評価スコア |
|:---:|:---:|:---|:---:|
| 1 | {{horse1_number}} | {{horse1_name}} | {{horse1_score}} |
| 2 | {{horse2_number}} | {{horse2_name}} | {{horse2_score}} |
| 3 | {{horse3_number}} | {{horse3_name}} | {{horse3_score}} |

---

## 主要評価因子 ({{protocol_mode}}モード)
- **過去成績スコア**: {{past_performance_avg}}
- **コース適性**: {{course_fit_avg}}
- **オッズ価値**: {{odds_value_avg}}
{% if protocol_mode != "1分モード" %}
- **馬場状態**: {{track_condition_avg}}
- **前走間隔**: {{interval_avg}}
- **馬体重変動**: {{weight_change_avg}}
{% endif %}
{% if protocol_mode == "5分モード" %}
- **穴馬要素**: {{dark_horse_avg}}
- **脚質展開**: {{pace_analysis}}
{% endif %}

---

## 購入プラン
{{betting_plan}}

---

## レース展開予想
{{pace_prediction}}

---

## 🏁 結果（レース後に記入）
- **実際の着順**:
- **配当**:
- **的中状況**:
- **振り返り**:

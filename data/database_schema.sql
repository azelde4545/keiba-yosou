-- 穴馬候補データベース スキーマ
-- 実力があるが明確な敗因で負けた馬を1レースから1-2頭抽出してデータベース化

CREATE TABLE IF NOT EXISTS dark_horse_candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- 基本情報
    horse_name TEXT NOT NULL,           -- 馬名
    race_name TEXT NOT NULL,            -- レース名
    race_date TEXT NOT NULL,            -- レース日（YYYY-MM-DD形式）
    race_venue TEXT NOT NULL,           -- 競馬場名
    distance INTEGER NOT NULL,          -- 距離（メートル）
    horse_number INTEGER,               -- 馬番
    finish_position INTEGER,            -- 着順
    odds REAL,                          -- オッズ
    
    -- 実力フィルター結果（3条件のうち1つ以上クリア判定）
    condition_a_passed INTEGER,        -- 同クラス以上3着以内実績（1=クリア、0=未達）
    condition_b_passed INTEGER,        -- オッズ10倍以下（1=クリア、0=未達）
    condition_c_passed INTEGER,        -- 複勝率10%以上（1=クリア、0=未達）
    
    -- 敗因フィルター結果（4項目以上+条件不適合1項目以上）
    defeat_factors_count INTEGER,      -- 該当敗因項目数
    defeat_factors_detail TEXT,        -- 該当項目の詳細（JSON形式）
    condition_mismatch_included INTEGER, -- 条件不適合含むか（1=含む、0=含まない）
    
    -- メタデータ
    evaluation_score INTEGER,          -- 総合評価点（該当項目数×20等）
    evaluation_reason TEXT,            -- 登録理由の要約
    recommended_conditions TEXT,       -- 推奨参戦条件（距離、馬場状態等）
    registration_date TEXT,            -- 登録日時（YYYY-MM-DD HH:MM:SS形式）
    used_flag INTEGER DEFAULT 0,      -- 予想で活用済みフラグ（0=未使用、1=使用済み）
    
    -- 重複防止制約
    UNIQUE(horse_name, race_date)
);

-- インデックス作成（検索パフォーマンス向上）
CREATE INDEX IF NOT EXISTS idx_horse_name ON dark_horse_candidates(horse_name);
CREATE INDEX IF NOT EXISTS idx_race_date ON dark_horse_candidates(race_date);
CREATE INDEX IF NOT EXISTS idx_race_venue ON dark_horse_candidates(race_venue);
CREATE INDEX IF NOT EXISTS idx_distance ON dark_horse_candidates(distance);
CREATE INDEX IF NOT EXISTS idx_evaluation_score ON dark_horse_candidates(evaluation_score);
CREATE INDEX IF NOT EXISTS idx_used_flag ON dark_horse_candidates(used_flag);
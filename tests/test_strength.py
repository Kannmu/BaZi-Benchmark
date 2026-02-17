from bazibench.core.strength import analyze_strength


def test_strength_strong_case():
    pillars = {
        "year_stem": "甲",
        "month_stem": "乙",
        "day_stem": "甲",
        "hour_stem": "乙",
        "year_branch": "寅",
        "month_branch": "寅",
        "day_branch": "卯",
        "hour_branch": "寅",
    }
    result = analyze_strength(pillars)
    assert result["level"] in {"身强", "身偏强"}


def test_strength_weak_case():
    pillars = {
        "year_stem": "庚",
        "month_stem": "辛",
        "day_stem": "甲",
        "hour_stem": "庚",
        "year_branch": "申",
        "month_branch": "酉",
        "day_branch": "申",
        "hour_branch": "酉",
    }
    result = analyze_strength(pillars)
    assert result["level"] in {"身弱", "中和"}

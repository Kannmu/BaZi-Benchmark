from bazibench.core.ten_gods import ten_god, analyze_ten_gods


def test_ten_god_mapping():
    assert ten_god("甲", "甲") == "比肩"
    assert ten_god("甲", "乙") == "劫财"
    assert ten_god("甲", "壬") == "偏印"
    assert ten_god("甲", "癸") == "正印"
    assert ten_god("甲", "丙") == "食神"
    assert ten_god("甲", "丁") == "伤官"
    assert ten_god("甲", "戊") == "偏财"
    assert ten_god("甲", "己") == "正财"
    assert ten_god("甲", "庚") == "七杀"
    assert ten_god("甲", "辛") == "正官"


def test_ten_gods_distribution():
    pillars = {
        "year_stem": "甲",
        "month_stem": "丙",
        "day_stem": "甲",
        "hour_stem": "辛",
    }
    analysis = analyze_ten_gods(pillars)
    assert len(analysis["gods"]) == 4

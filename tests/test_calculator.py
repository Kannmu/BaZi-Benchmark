from datetime import datetime

from bazibench.core.calculator import BaZiCalculator


def test_base_day_ganzhi():
    calc = BaZiCalculator()
    dt = datetime(1900, 1, 31, 23, 0)
    result = calc.calculate(dt)
    assert result["day"] == "甲子"
    assert result["hour"] == "甲子"


def test_day_increment():
    calc = BaZiCalculator()
    dt = datetime(1900, 2, 1, 12, 0)
    result = calc.calculate(dt)
    assert result["day"] == "乙丑"


def test_year_pillar_with_lichun():
    calc = BaZiCalculator()
    dt = datetime(2000, 2, 10, 10, 0)
    result = calc.calculate(dt)
    assert result["year"] == "辛巳"


def test_month_pillar_basic():
    calc = BaZiCalculator()
    dt = datetime(2000, 3, 10, 10, 0)
    result = calc.calculate(dt)
    assert result["month"] == "辛卯"

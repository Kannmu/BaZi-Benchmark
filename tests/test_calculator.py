from datetime import datetime
from bazibench.core.calculator import BaZiCalculator

def test_base_day_ganzhi():
    calc = BaZiCalculator()
    # 1900-01-31 12:00 (Noon)
    # lunar_python says 1900-01-31 is JiaChen day
    dt = datetime(1900, 1, 31, 12, 0)
    result = calc.calculate(dt)
    assert result["day"] == "甲辰"
    assert result["hour"] == "庚午"

def test_day_increment():
    calc = BaZiCalculator()
    # 1900-02-01 12:00 (Next day)
    # Expect YiSi (JiaChen -> YiSi)
    dt = datetime(1900, 2, 1, 12, 0)
    result = calc.calculate(dt)
    assert result["day"] == "乙巳"

def test_year_pillar_with_lichun():
    calc = BaZiCalculator()
    # 2000-02-10 (After LiChun Feb 4)
    # Year 2000 is GengChen (Dragon)
    dt = datetime(2000, 2, 10, 10, 0)
    result = calc.calculate(dt)
    assert result["year"] == "庚辰"

def test_month_pillar_basic():
    calc = BaZiCalculator()
    # 2000-03-10 (After JingZhe Mar 5)
    # Month is JiMao
    dt = datetime(2000, 3, 10, 10, 0)
    result = calc.calculate(dt)
    assert result["month"] == "己卯"

def test_true_solar_time_adjustment():
    calc = BaZiCalculator()
    # Test True Solar Time effect
    # Location: Urumqi (87.6E). Beijing Time 12:00.
    # Offset: (87.6 - 120) * 4 = -129.6 minutes (~ -2h 10m).
    # Local Mean Time approx 09:50.
    # If Hour Pillar changes boundary (e.g. 11:00 -> 09:00), pillar changes.
    # Let's test a time near 11:00 (Wu hour start).
    # If we use Beijing Time 12:00 at 87.6E, it should be Si hour (09:00-11:00) instead of Wu hour (11:00-13:00).
    
    dt = datetime(2024, 6, 1, 12, 0) # Summer
    
    # Without location (default 120E): 12:00 -> Wu hour
    res_default = calc.calculate(dt, longitude=120.0)
    # Wu hour is 7th branch -> "午"
    assert "午" in res_default["hour"]
    
    # With Urumqi location (87.6E): ~09:50 -> Si hour
    res_west = calc.calculate(dt, longitude=87.6)
    # Si hour is 6th branch -> "巳"
    assert "巳" in res_west["hour"]

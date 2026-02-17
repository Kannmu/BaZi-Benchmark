from datetime import datetime

from bazibench.core.calculator import BaZiCalculator
from bazibench.core.wuxing import analyze_wuxing


def test_wuxing_counts_and_missing():
    calc = BaZiCalculator()
    result = calc.calculate(datetime(1900, 1, 31, 23, 0))
    analysis = analyze_wuxing(result)
    assert "counts" in analysis
    assert "missing" in analysis
    assert isinstance(analysis["missing"], list)

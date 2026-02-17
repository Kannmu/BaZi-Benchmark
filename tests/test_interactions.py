from bazibench.core.interactions import analyze_interactions


def test_interactions_basic():
    branches = ["子", "丑", "午", "申", "辰", "寅"]
    result = analyze_interactions(branches)
    assert ("子", "丑") in result["liuhe"]
    assert ("子", "午") in result["liuchong"]
    assert ("申", "子", "辰") in result["sanhe"]


def test_interactions_xing_and_self():
    branches = ["寅", "巳", "申", "辰", "辰"]
    result = analyze_interactions(branches)
    assert ("寅", "巳", "申") in result["xing"]
    assert "辰" in result["self_xing"]

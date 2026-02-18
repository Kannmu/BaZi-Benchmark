"""十神计算。"""

from __future__ import annotations

from collections import Counter

from .constants import STEM_INFO, SHENG, KE


def ten_god(day_stem: str, target_stem: str) -> str:
    day_info = STEM_INFO[day_stem]
    target_info = STEM_INFO[target_stem]
    day_element = day_info["wuxing"]
    target_element = target_info["wuxing"]
    same_polarity = day_info["yinyang"] == target_info["yinyang"]

    if day_element == target_element:
        return "比肩" if same_polarity else "劫财"

    if SHENG[target_element] == day_element:
        return "偏印" if same_polarity else "正印"

    if SHENG[day_element] == target_element:
        return "食神" if same_polarity else "伤官"

    if KE[day_element] == target_element:
        return "偏财" if same_polarity else "正财"

    if KE[target_element] == day_element:
        return "七杀" if same_polarity else "正官"

    raise ValueError("无法识别十神关系")


def analyze_ten_gods(pillars: dict) -> dict:
    day_stem = pillars["day_stem"]
    stems = [
        pillars["year_stem"],
        pillars["month_stem"],
        pillars["day_stem"],
        pillars["hour_stem"],
    ]

    gods = [ten_god(day_stem, stem) for stem in stems]
    return {
        "gods": gods,
        "counts": dict(Counter(gods)),
    }

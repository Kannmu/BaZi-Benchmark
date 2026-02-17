"""日主强弱分析。"""

from __future__ import annotations

from .constants import STEM_INFO, BRANCH_INFO, SHENG, KE


def _relation(day_element: str, target_element: str) -> str:
    if day_element == target_element:
        return "same"
    if SHENG[target_element] == day_element:
        return "supported"
    if SHENG[day_element] == target_element:
        return "drain"
    if KE[target_element] == day_element:
        return "controlled"
    if KE[day_element] == target_element:
        return "controls"
    return "other"


def analyze_strength(pillars: dict) -> dict:
    day_stem = pillars["day_stem"]
    day_element = STEM_INFO[day_stem]["wuxing"]
    month_branch = pillars["month_branch"]
    month_element = BRANCH_INFO[month_branch]["wuxing"]

    score = 0.0

    month_rel = _relation(day_element, month_element)
    if month_rel == "same":
        score += 2.0
    elif month_rel == "supported":
        score += 1.0
    elif month_rel in {"controlled", "controls", "drain"}:
        score -= 1.0

    stems = [
        pillars["year_stem"],
        pillars["month_stem"],
        pillars["day_stem"],
        pillars["hour_stem"],
    ]
    for stem in stems:
        rel = _relation(day_element, STEM_INFO[stem]["wuxing"])
        if rel == "same":
            score += 1.0
        elif rel == "supported":
            score += 0.5
        elif rel in {"controlled", "controls", "drain"}:
            score -= 0.5

    branches = [
        pillars["year_branch"],
        pillars["month_branch"],
        pillars["day_branch"],
        pillars["hour_branch"],
    ]
    for branch in branches:
        for hidden in BRANCH_INFO[branch]["hidden_stems"]:
            rel = _relation(day_element, STEM_INFO[hidden]["wuxing"])
            if rel == "same":
                score += 1.0
            elif rel == "supported":
                score += 0.5
            elif rel in {"controlled", "controls", "drain"}:
                score -= 0.5

    if score >= 3.0:
        level = "身强"
    elif score >= 1.5:
        level = "身偏强"
    elif score >= -1.0:
        level = "中和"
    else:
        level = "身弱"

    return {"score": round(score, 2), "level": level}

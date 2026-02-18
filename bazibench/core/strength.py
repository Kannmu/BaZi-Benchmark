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

    # 1. Month Command (得令) - High Weight (approx 40%)
    month_rel = _relation(day_element, month_element)
    if month_rel == "same":
        score += 4.0
    elif month_rel == "supported":
        score += 3.0
    else:
        score -= 2.0

    # 2. Stems (得势) - Exclude Day Stem itself
    stems = [
        pillars["year_stem"],
        pillars["month_stem"],
        pillars["hour_stem"],
    ]
    for stem in stems:
        rel = _relation(day_element, STEM_INFO[stem]["wuxing"])
        if rel == "same":
            score += 1.0
        elif rel == "supported":
            score += 0.5
        else:
            score -= 0.5

    # 3. Branches (得地) - Hidden Stems
    branches = [
        pillars["year_branch"],
        pillars["month_branch"],
        pillars["day_branch"],
        pillars["hour_branch"],
    ]
    for branch in branches:
        hidden_stems = BRANCH_INFO[branch]["hidden_stems"]
        for i, hidden in enumerate(hidden_stems):
            # First hidden stem is Main Qi (本气), others are Residual (中气/余气)
            weight = 1.0 if i == 0 else 0.4
            
            rel = _relation(day_element, STEM_INFO[hidden]["wuxing"])
            if rel == "same":
                score += 1.0 * weight
            elif rel == "supported":
                score += 0.5 * weight
            else:
                score -= 0.5 * weight

    # Adjusted Thresholds based on new scoring
    if score >= 6.0:
        level = "身强"
    elif score >= 2.0:
        level = "身偏强"
    elif score >= -2.0:
        level = "中和"
    else:
        level = "身弱"

    return {"score": round(score, 2), "level": level}

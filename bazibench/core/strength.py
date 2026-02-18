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

# Approximate weights for hidden stems (Main Qi, Middle Qi, Residual Qi)
# Based on common sub-qi duration
HIDDEN_WEIGHTS = {
    "子": [1.0],          # 癸
    "丑": [0.6, 0.3, 0.1], # 己, 癸, 辛
    "寅": [0.6, 0.2, 0.2], # 甲, 丙, 戊
    "卯": [1.0],          # 乙
    "辰": [0.6, 0.3, 0.1], # 戊, 乙, 癸
    "巳": [0.6, 0.2, 0.2], # 丙, 戊, 庚
    "午": [0.7, 0.3],     # 丁, 己
    "未": [0.6, 0.3, 0.1], # 己, 丁, 乙
    "申": [0.6, 0.2, 0.2], # 庚, 壬, 戊
    "酉": [1.0],          # 辛
    "戌": [0.6, 0.3, 0.1], # 戊, 辛, 丁
    "亥": [0.7, 0.3],     # 壬, 甲
}

def analyze_strength(pillars: dict) -> dict:
    day_stem = pillars["day_stem"]
    day_element = STEM_INFO[day_stem]["wuxing"]
    month_branch = pillars["month_branch"]
    month_element = BRANCH_INFO[month_branch]["wuxing"]

    score = 0.0

    # 1. Month Command (得令) - High Weight
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

    # 3. Branches (得地) - Hidden Stems with specific weights
    branches = [
        pillars["year_branch"],
        pillars["month_branch"],
        pillars["day_branch"],
        pillars["hour_branch"],
    ]
    
    # Month branch is already counted in "Month Command" (得令), 
    # but usually in strength calculation, the month branch is counted TWICE or has a base score.
    # The previous logic counted month branch again in the loop. 
    # Current logic: Month Command gives base score (+4/+3/-2).
    # Then we check all branches for root support (得地).
    
    for branch in branches:
        hidden_stems = BRANCH_INFO[branch]["hidden_stems"]
        weights = HIDDEN_WEIGHTS.get(branch, [1.0] * len(hidden_stems))
        
        for i, hidden in enumerate(hidden_stems):
            w = weights[i] if i < len(weights) else 0.4
            
            rel = _relation(day_element, STEM_INFO[hidden]["wuxing"])
            if rel == "same":
                score += 1.0 * w
            elif rel == "supported":
                score += 0.5 * w
            else:
                score -= 0.5 * w

    # Adjusted Thresholds based on new scoring
    if score >= 4.0:
        level = "身强"
    elif score >= 1.0:
        level = "身偏强"
    elif score >= -1.0:
        level = "中和"
    else:
        level = "身弱"

    return {"score": round(score, 2), "level": level}

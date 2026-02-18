"""五行分析。"""

from __future__ import annotations

from collections import Counter

from .constants import STEM_INFO, BRANCH_INFO, WUXING, SHENG, KE


def analyze_wuxing(pillars: dict) -> dict:
    stems = [
        pillars["year_stem"],
        pillars["month_stem"],
        pillars["day_stem"],
        pillars["hour_stem"],
    ]
    branches = [
        pillars["year_branch"],
        pillars["month_branch"],
        pillars["day_branch"],
        pillars["hour_branch"],
    ]

    counts = Counter()
    all_elements = set()
    
    for stem in stems:
        wx = STEM_INFO[stem]["wuxing"]
        counts[wx] += 1
        all_elements.add(wx)
        
    for branch in branches:
        wx = BRANCH_INFO[branch]["wuxing"]
        counts[wx] += 1
        all_elements.add(wx)
        # Check hidden stems for existence (to avoid false "missing")
        for hidden in BRANCH_INFO[branch]["hidden_stems"]:
            all_elements.add(STEM_INFO[hidden]["wuxing"])

    missing = [e for e in WUXING if e not in all_elements]

    return {
        "counts": dict(counts),
        "missing": missing,
        "sheng": SHENG.copy(),
        "ke": KE.copy(),
    }

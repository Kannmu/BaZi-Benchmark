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
    for stem in stems:
        counts[STEM_INFO[stem]["wuxing"]] += 1
    for branch in branches:
        counts[BRANCH_INFO[branch]["wuxing"]] += 1

    missing = [e for e in WUXING if counts[e] == 0]

    return {
        "counts": dict(counts),
        "missing": missing,
        "sheng": SHENG.copy(),
        "ke": KE.copy(),
    }

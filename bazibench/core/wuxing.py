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
    
    # Count Heavenly Stems
    for stem in stems:
        wx = STEM_INFO[stem]["wuxing"]
        counts[wx] += 1
        all_elements.add(wx)
        
    # Count Earthly Branches (Hidden Stems included)
    for branch in branches:
        # Instead of just counting the branch's main wuxing, we count the hidden stems
        hidden_stems = BRANCH_INFO[branch]["hidden_stems"]
        for hidden in hidden_stems:
            wx = STEM_INFO[hidden]["wuxing"]
            counts[wx] += 1
            all_elements.add(wx)

    missing = [e for e in WUXING if e not in all_elements]

    return {
        "counts": dict(counts),
        "missing": missing,
        "sheng": SHENG.copy(),
        "ke": KE.copy(),
    }

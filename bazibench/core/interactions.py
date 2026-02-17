"""刑冲合害分析。"""

from __future__ import annotations

from collections import Counter

from .constants import LIU_HE, LIU_CHONG, SAN_HE, XING, SELF_XING


def analyze_interactions(branches: list[str]) -> dict:
    branch_set = set(branches)
    counts = Counter(branches)

    liuhe = [pair for pair in LIU_HE if set(pair).issubset(branch_set)]
    liuchong = [pair for pair in LIU_CHONG if set(pair).issubset(branch_set)]
    sanhe = [group for group in SAN_HE if set(group).issubset(branch_set)]
    xing = []
    for group in XING:
        if set(group).issubset(branch_set):
            xing.append(group)
        elif len(group) == 2 and set(group).issubset(branch_set):
            xing.append(group)

    self_xing = [b for b in SELF_XING if counts[b] >= 2]

    return {
        "liuhe": liuhe,
        "liuchong": liuchong,
        "sanhe": sanhe,
        "xing": xing,
        "self_xing": self_xing,
    }

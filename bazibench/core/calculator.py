"""四柱排盘计算。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date

from .constants import TIANGAN, DIZHI, WU_HU_DUN, WU_SHU_DUN

BASE_DAY = date(1900, 1, 31)  # 甲子日


@dataclass(frozen=True)
class BaZiPillar:
    stem: str
    branch: str

    @property
    def ganzhi(self) -> str:
        return f"{self.stem}{self.branch}"


class BaZiCalculator:
    def __init__(self) -> None:
        pass

    def calculate(self, dt: datetime) -> dict:
        year_pillar = self._year_pillar(dt)
        month_pillar = self._month_pillar(dt, year_pillar.stem)
        day_pillar = self._day_pillar(dt)
        hour_pillar = self._hour_pillar(dt, day_pillar.stem)

        return {
            "year": year_pillar.ganzhi,
            "month": month_pillar.ganzhi,
            "day": day_pillar.ganzhi,
            "hour": hour_pillar.ganzhi,
            "year_stem": year_pillar.stem,
            "year_branch": year_pillar.branch,
            "month_stem": month_pillar.stem,
            "month_branch": month_pillar.branch,
            "day_stem": day_pillar.stem,
            "day_branch": day_pillar.branch,
            "hour_stem": hour_pillar.stem,
            "hour_branch": hour_pillar.branch,
        }

    def _year_pillar(self, dt: datetime) -> BaZiPillar:
        y = dt.year
        if (dt.month, dt.day) < (2, 4):
            y -= 1
        stem = TIANGAN[(y - 3) % 10]
        branch = DIZHI[(y - 3) % 12]
        return BaZiPillar(stem, branch)

    def _month_pillar(self, dt: datetime, year_stem: str) -> BaZiPillar:
        m = dt.month
        if (dt.month, dt.day) < (2, 4):
            m = 1
        month_branches = [
            None,
            "丑",
            "寅",
            "卯",
            "辰",
            "巳",
            "午",
            "未",
            "申",
            "酉",
            "戌",
            "亥",
            "子",
        ]
        month_branch = month_branches[m]
        month_branch_index = DIZHI.index(month_branch)

        start_stem = WU_HU_DUN[year_stem]
        start_index = TIANGAN.index(start_stem)
        stem_index = (start_index + (month_branch_index - 2)) % 10
        month_stem = TIANGAN[stem_index]
        return BaZiPillar(month_stem, month_branch)

    def _day_pillar(self, dt: datetime) -> BaZiPillar:
        delta = (dt.date() - BASE_DAY).days
        stem = TIANGAN[delta % 10]
        branch = DIZHI[delta % 12]
        return BaZiPillar(stem, branch)

    def _hour_pillar(self, dt: datetime, day_stem: str) -> BaZiPillar:
        hour_branch_index = ((dt.hour + 1) // 2) % 12
        hour_branch = DIZHI[hour_branch_index]

        start_stem = WU_SHU_DUN[day_stem]
        start_index = TIANGAN.index(start_stem)
        hour_stem = TIANGAN[(start_index + hour_branch_index) % 10]
        return BaZiPillar(hour_stem, hour_branch)

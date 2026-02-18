"""四柱排盘计算。"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict

from lunar_python import Solar

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

    def _get_solar(self, dt: datetime, longitude: float = 120.0) -> Solar:
        """
        根据时间和经度获取True Solar Time对应的Solar对象。
        """
        # 1. 计算真太阳时 (True Solar Time)
        # 1.1 平太阳时 (Local Mean Time)
        offset_minutes = (longitude - 120.0) * 4
        
        # 1.2 真太阳时均时差 (Equation of Time)
        day_of_year = dt.timetuple().tm_yday
        B = 360 * (day_of_year - 81) / 365
        B_rad = math.radians(B)
        eot = 9.87 * math.sin(2 * B_rad) - 7.53 * math.cos(B_rad) - 1.5 * math.sin(B_rad)
        
        total_offset_minutes = offset_minutes + eot
        true_solar_time = dt + timedelta(minutes=total_offset_minutes)
        
        return Solar.fromYmdHms(
            true_solar_time.year, 
            true_solar_time.month, 
            true_solar_time.day, 
            true_solar_time.hour, 
            true_solar_time.minute, 
            true_solar_time.second
        )

    def calculate(self, dt: datetime, longitude: float = 120.0, latitude: float = 30.0) -> dict:
        """
        计算八字四柱。
        
        Args:
            dt: datetime对象 (Clock Time)
            longitude: 经度，默认120.0 (北京时间基准)
            latitude: 纬度，默认30.0 (目前用于真太阳时计算的预留)
            
        Returns:
            dict: 包含四柱信息的字典
        """
        solar = self._get_solar(dt, longitude)
        lunar = solar.getLunar()
        bazi = lunar.getEightChar()
        
        # 3. 提取结果
        year_ganzhi = bazi.getYear()
        month_ganzhi = bazi.getMonth()
        day_ganzhi = bazi.getDay()
        hour_ganzhi = bazi.getTime()
        
        return {
            "year": year_ganzhi,
            "month": month_ganzhi,
            "day": day_ganzhi,
            "hour": hour_ganzhi,
            "year_stem": year_ganzhi[0],
            "year_branch": year_ganzhi[1],
            "month_stem": month_ganzhi[0],
            "month_branch": month_ganzhi[1],
            "day_stem": day_ganzhi[0],
            "day_branch": day_ganzhi[1],
            "hour_stem": hour_ganzhi[0],
            "hour_branch": hour_ganzhi[1],
        }

    def calculate_dayun(self, dt: datetime, gender: int, longitude: float = 120.0) -> List[Dict]:
        """
        计算大运。
        
        Args:
            dt: 出生时间
            gender: 性别 (1男, 0女)
            longitude: 经度
            
        Returns:
            List[Dict]: 大运列表，包含 start_age, start_year, ganzhi
        """
        solar = self._get_solar(dt, longitude)
        lunar = solar.getLunar()
        bazi = lunar.getEightChar()
        yun = bazi.getYun(gender)
        da_yun_list = yun.getDaYun()
        
        result = []
        # lunar_python的大运列表第0个通常是起运前，跳过
        for dy in da_yun_list[1:]:
             result.append({
                 "start_year": dy.getStartYear(),
                 "start_age": dy.getStartAge(),
                 "ganzhi": dy.getGanZhi()
             })
        return result

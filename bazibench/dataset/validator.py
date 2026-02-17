"""数据验证器。"""

from typing import List, Dict, Any
from .schema import BaziSample
from ..core.constants import TIANGAN, DIZHI, WUXING

class BaziValidator:
    def __init__(self):
        pass

    def validate_sample(self, sample: BaziSample) -> List[str]:
        """验证单个样本，返回错误列表"""
        errors = []
        
        # 1. 验证干支合法性
        chart = sample.ground_truth.chart
        for stem in [chart.year_stem, chart.month_stem, chart.day_stem, chart.hour_stem]:
            if stem not in TIANGAN:
                errors.append(f"Invalid stem: {stem}")
        for branch in [chart.year_branch, chart.month_branch, chart.day_branch, chart.hour_branch]:
            if branch not in DIZHI:
                errors.append(f"Invalid branch: {branch}")
        
        # 2. 验证五行总数
        wuxing = sample.ground_truth.wuxing
        total_count = sum(wuxing.counts.values())
        if total_count != 8:
            errors.append(f"Total wuxing count must be 8, got {total_count}")
        
        # 3. 验证十神数量
        ten_gods = sample.ground_truth.ten_gods
        if len(ten_gods.gods) != 4:
            errors.append(f"Ten gods count must be 4, got {len(ten_gods.gods)}")
            
        # 4. 验证强弱分值范围 (大约 -5 到 15 之间)
        strength = sample.ground_truth.strength
        if not (-10.0 <= strength.score <= 20.0):
             errors.append(f"Strength score out of reasonable range: {strength.score}")

        return errors

    def validate_batch(self, samples: List[BaziSample]) -> Dict[str, List[str]]:
        """批量验证样本"""
        results = {}
        for sample in samples:
            errors = self.validate_sample(sample)
            if errors:
                results[sample.id] = errors
        return results

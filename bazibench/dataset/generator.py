"""数据集生成器。"""

import random
import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from ..core.calculator import BaZiCalculator
from ..core.wuxing import analyze_wuxing
from ..core.ten_gods import analyze_ten_gods
from ..core.strength import analyze_strength
from ..core.interactions import analyze_interactions
from .schema import (
    BaziSample,
    BaziInput,
    BaziAnalysis,
    BaziChart,
    WuxingAnalysis,
    TenGodsAnalysis,
    StrengthAnalysis,
    InteractionsAnalysis
)


class BaziDatasetGenerator:
    def __init__(self, seed: int = 42):
        self.calculator = BaZiCalculator()
        random.seed(seed)

    def generate_random_date(self, start_year: int = 1950, end_year: int = 2030) -> datetime:
        """生成随机日期"""
        start_date = datetime(start_year, 1, 1)
        end_date = datetime(end_year, 12, 31)
        delta = end_date - start_date
        random_days = random.randrange(delta.days)
        random_seconds = random.randrange(24 * 60 * 60)
        return start_date + timedelta(days=random_days, seconds=random_seconds)

    def analyze(self, dt: datetime) -> BaziAnalysis:
        """对指定日期进行全量八字分析"""
        chart_data = self.calculator.calculate(dt)
        wuxing_data = analyze_wuxing(chart_data)
        ten_gods_data = analyze_ten_gods(chart_data)
        strength_data = analyze_strength(chart_data)
        
        branches = [
            chart_data["year_branch"],
            chart_data["month_branch"],
            chart_data["day_branch"],
            chart_data["hour_branch"]
        ]
        interactions_data = analyze_interactions(branches)

        return BaziAnalysis(
            chart=BaziChart(
                year=chart_data["year"],
                month=chart_data["month"],
                day=chart_data["day"],
                hour=chart_data["hour"],
                year_stem=chart_data["year_stem"],
                year_branch=chart_data["year_branch"],
                month_stem=chart_data["month_stem"],
                month_branch=chart_data["month_branch"],
                day_stem=chart_data["day_stem"],
                day_branch=chart_data["day_branch"],
                hour_stem=chart_data["hour_stem"],
                hour_branch=chart_data["hour_branch"]
            ),
            wuxing=WuxingAnalysis(
                counts=wuxing_data["counts"],
                missing=wuxing_data["missing"],
                sheng=wuxing_data["sheng"],
                ke=wuxing_data["ke"]
            ),
            ten_gods=TenGodsAnalysis(
                gods=ten_gods_data["gods"],
                counts=ten_gods_data["counts"]
            ),
            strength=StrengthAnalysis(
                score=strength_data["score"],
                level=strength_data["level"]
            ),
            interactions=InteractionsAnalysis(
                liuhe=interactions_data["liuhe"],
                liuchong=interactions_data["liuchong"],
                sanhe=interactions_data["sanhe"],
                xing=interactions_data["xing"],
                self_xing=interactions_data["self_xing"]
            )
        )

    def generate_sample(self, task_type: str = "chart") -> BaziSample:
        """生成单个测试样本"""
        dt = self.generate_random_date()
        analysis = self.analyze(dt)
        
        sample_id = str(uuid.uuid4())
        input_data = BaziInput(
            year=dt.year,
            month=dt.month,
            day=dt.day,
            hour=dt.hour,
            minute=dt.minute
        )

        instruction = ""
        expected_output = ""
        difficulty = 1
        tags = [task_type]

        if task_type == "chart":
            instruction = f"请根据公历 {dt.year}年{dt.month}月{dt.day}日 {dt.hour}时 排出八字四柱。"
            expected_output = (
                f"年柱: {analysis.chart.year}\n"
                f"月柱: {analysis.chart.month}\n"
                f"日柱: {analysis.chart.day}\n"
                f"时柱: {analysis.chart.hour}"
            )
            difficulty = 2
        
        elif task_type == "wuxing":
            instruction = f"请分析该八字的五行个数与缺失：{analysis.chart.year} {analysis.chart.month} {analysis.chart.day} {analysis.chart.hour}"
            counts_str = ", ".join([f"{k}: {v}" for k, v in analysis.wuxing.counts.items()])
            missing_str = ", ".join(analysis.wuxing.missing) if analysis.wuxing.missing else "无"
            expected_output = f"五行统计: {counts_str}\n缺失五行: {missing_str}"
            difficulty = 2

        elif task_type == "ten_gods":
            instruction = f"请列出该八字的十神（年/月/日/时）：{analysis.chart.year} {analysis.chart.month} {analysis.chart.day} {analysis.chart.hour}"
            expected_output = " ".join(analysis.ten_gods.gods)
            difficulty = 3
            
        elif task_type == "strength":
            instruction = f"请判断该八字日主的强弱：{analysis.chart.year} {analysis.chart.month} {analysis.chart.day} {analysis.chart.hour}"
            expected_output = f"得分: {analysis.strength.score}, 判定: {analysis.strength.level}"
            difficulty = 4

        return BaziSample(
            id=sample_id,
            input=input_data,
            ground_truth=analysis,
            instruction=instruction,
            expected_output=expected_output,
            difficulty=difficulty,
            tags=tags,
            meta={"created_at": datetime.now().isoformat()}
        )

    def generate_batch(self, count: int, task_types: Optional[List[str]] = None) -> List[BaziSample]:
        """批量生成样本"""
        if task_types is None:
            task_types = ["chart", "wuxing", "ten_gods", "strength"]
        
        samples = []
        for _ in range(count):
            task_type = random.choice(task_types)
            samples.append(self.generate_sample(task_type))
        return samples

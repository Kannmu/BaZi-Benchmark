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
    InteractionsAnalysis,
    DaYunAnalysis,
    UsefulGodAnalysis
)


class BaziDatasetGenerator:
    def __init__(self, seed: int = 42):
        self.calculator = BaZiCalculator()
        self.rng = random.Random(seed)

    def generate_random_date(self, start_year: int = 1950, end_year: int = 2030) -> datetime:
        """生成随机日期"""
        start_date = datetime(start_year, 1, 1)
        end_date = datetime(end_year, 12, 31)
        delta = end_date - start_date
        random_days = self.rng.randrange(delta.days)
        random_seconds = self.rng.randrange(24 * 60 * 60)
        return start_date + timedelta(days=random_days, seconds=random_seconds)

    def analyze(self, dt: datetime, gender: int = 1, longitude: float = 120.0, latitude: float = 30.0, utc_offset: float = 8.0) -> BaziAnalysis:
        """对指定日期进行全量八字分析"""
        combined_data = self.calculator.calculate_with_dayun(dt, gender, longitude, latitude, utc_offset)
        chart_data = combined_data["chart"]
        da_yun_list = combined_data["dayun"]
        
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
        
        # Simple Useful God Heuristic
        # Strength Thresholds: >= 1.0 Strong, >= -1.0 Neutral, < -1.0 Weak
        score = strength_data["score"]
        if score < -1.0:
             ug_type = "印比 (生扶)"
             reason = "日主偏弱，宜用印星生身或比劫帮身"
             # Tiao Hou (Basic)
             month_branch = chart_data["month_branch"]
             if month_branch in ["亥", "子", "丑"] and "火" not in wuxing_data["counts"]: # Winter needs Fire
                 reason += "；生于冬月，需火调候暖局"
        elif score >= 1.0:
             ug_type = "克泄耗 (抑制)"
             reason = "日主偏强，宜用官杀克制、食伤泄秀或财星耗身"
        else:
             ug_type = "中和"
             reason = "日主中和，需视具体组合而定"

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
                sanhui=interactions_data["sanhui"],
                xing=interactions_data["xing"],
                self_xing=interactions_data["self_xing"],
                liuhai=interactions_data["liuhai"]
            ),
            da_yun=DaYunAnalysis(
                gender=gender,
                pillars=da_yun_list
            ),
            useful_god=UsefulGodAnalysis(
                god=ug_type,
                reason=reason
            )
        )

    def generate_sample(self, task_type: str = "chart") -> BaziSample:
        """生成单个测试样本"""
        dt = self.generate_random_date()
        gender = self.rng.choice([0, 1])
        # Default to Beijing
        longitude = 120.0
        latitude = 30.0
        utc_offset = 8.0
        
        analysis = self.analyze(dt, gender, longitude, latitude, utc_offset)
        
        sample_id = str(uuid.uuid4())
        input_data = BaziInput(
            year=dt.year,
            month=dt.month,
            day=dt.day,
            hour=dt.hour,
            minute=dt.minute,
            gender=gender,
            longitude=longitude,
            latitude=latitude,
            utc_offset=utc_offset
        )

        instruction = ""
        expected_output = ""
        difficulty = 1
        tags = [task_type]
        evaluation_type = "exact_match"
        
        gender_str = "男" if gender == 1 else "女"

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
            instruction = f"请分析该八字的五行个数与缺失（注意：必须计算地支藏干，天干和地支藏干一起统计）：{analysis.chart.year} {analysis.chart.month} {analysis.chart.day} {analysis.chart.hour}"
            counts_str = ", ".join([f"{k}: {v}" for k, v in analysis.wuxing.counts.items()])
            missing_str = ", ".join(analysis.wuxing.missing) if analysis.wuxing.missing else "无"
            expected_output = f"五行统计: {counts_str}\n缺失五行: {missing_str}"
            difficulty = 3

        elif task_type == "ten_gods":
            instruction = f"请列出该八字天干的十神（按年干/月干/日干/时干顺序，只输出十神名称，用空格分隔）：{analysis.chart.year} {analysis.chart.month} {analysis.chart.day} {analysis.chart.hour}"
            expected_output = " ".join(analysis.ten_gods.gods)
            difficulty = 3
            
        elif task_type == "strength":
            instruction = f"请判断该八字日主的强弱（身强/身弱/中和）。请严格按以下格式输出结果：\n得分: <数值>\n判定: <身强/身弱/中和>\n八字为：{analysis.chart.year} {analysis.chart.month} {analysis.chart.day} {analysis.chart.hour}"
            expected_output = f"得分: {analysis.strength.score}, 判定: {analysis.strength.level}"
            difficulty = 4

        elif task_type == "interactions":
            instruction = f"请分析该八字地支的刑冲合害关系。请直接输出JSON格式结果，包含键：liuhe, liuchong, sanhe, sanhui, xing, self_xing, liuhai。值为空列表则不输出该键。例如：{{\"liuchong\": [[\"寅\", \"申\"]]}}。地支：{analysis.chart.year_branch} {analysis.chart.month_branch} {analysis.chart.day_branch} {analysis.chart.hour_branch}"
            
            # Construct JSON-like expected output
            output_dict = {}
            if analysis.interactions.liuhe: output_dict["liuhe"] = analysis.interactions.liuhe
            if analysis.interactions.liuchong: output_dict["liuchong"] = analysis.interactions.liuchong
            if analysis.interactions.sanhe: output_dict["sanhe"] = analysis.interactions.sanhe
            if analysis.interactions.sanhui: output_dict["sanhui"] = analysis.interactions.sanhui
            if analysis.interactions.xing: output_dict["xing"] = analysis.interactions.xing
            if analysis.interactions.self_xing: output_dict["self_xing"] = analysis.interactions.self_xing
            if analysis.interactions.liuhai: output_dict["liuhai"] = analysis.interactions.liuhai
            
            import json
            expected_output = json.dumps(output_dict, ensure_ascii=False)
            difficulty = 4
            evaluation_type = "partial_match"

        elif task_type == "da_yun":
            # Current year range for Liu Nian
            current_year = datetime.now().year
            years = [current_year, current_year + 1, current_year + 2]
            
            instruction = f"请排出该{gender_str}命的大运（前3步），并推算{years[0]}-{years[2]}年的流年干支：{dt.year}年{dt.month}月{dt.day}日 {dt.hour}时生。"
            
            dys = analysis.da_yun.pillars
            if len(dys) >= 3:
                dys = dys[:3]
            dy_lines = [f"{d['start_age']}岁起运: {d['ganzhi']}" for d in dys]
            
            ln_lines = []
            for y in years:
                ln_ganzhi = self.calculator.calculate_liunian(y)
                ln_lines.append(f"{y}年: {ln_ganzhi}")
            
            expected_output = "大运:\n" + ("\n".join(dy_lines) if dy_lines else "无大运数据") + "\n\n流年:\n" + "\n".join(ln_lines)
            difficulty = 5

        elif task_type == "useful_god":
            instruction = f"请判断该八字的日主强弱并建议喜用神：{analysis.chart.year} {analysis.chart.month} {analysis.chart.day} {analysis.chart.hour}"
            expected_output = f"日主{analysis.strength.level}，建议用神：{analysis.useful_god.god}，理由：{analysis.useful_god.reason}"
            difficulty = 5

        elif task_type == "comprehensive":
            instruction = f"请对该{gender_str}命进行综合八字分析：{dt.year}年{dt.month}月{dt.day}日 {dt.hour}时。\n请从以下几个方面进行分析：\n1. 四柱排盘\n2. 五行旺衰\n3. 日主强弱\n4. 用神建议\n5. 性格简评"
            
            # Simple personality heuristic based on Day Master
            dm = analysis.chart.day_stem
            personality = "性格特征需结合全局分析。"
            if dm in ["甲", "乙"]: personality = "仁慈正直，有进取心。"
            elif dm in ["丙", "丁"]: personality = "热情礼貌，急躁冲动。"
            elif dm in ["戊", "己"]: personality = "忠诚守信，稳重踏实。"
            elif dm in ["庚", "辛"]: personality = "刚毅果断，讲义气。"
            elif dm in ["壬", "癸"]: personality = "聪明智慧，善于变化。"
            
            expected_output = (
                f"1. 四柱: {analysis.chart.year} {analysis.chart.month} {analysis.chart.day} {analysis.chart.hour}\n"
                f"2. 五行: {analysis.wuxing.counts}\n"
                f"3. 强弱: {analysis.strength.level} (得分: {analysis.strength.score})\n"
                f"4. 用神: {analysis.useful_god.god}\n"
                f"5. 性格: {personality}"
            )
            difficulty = 5

        return BaziSample(
            id=sample_id,
            input=input_data,
            ground_truth=analysis,
            instruction=instruction,
            expected_output=expected_output,
            difficulty=difficulty,
            tags=tags,
            evaluation_type=evaluation_type,
            meta={"created_at": datetime.now().isoformat()}
        )

    def generate_batch(self, count: int, task_types: Optional[List[str]] = None) -> List[BaziSample]:
        """批量生成样本"""
        if task_types is None:
            task_types = ["chart", "wuxing", "ten_gods", "strength", "interactions", "da_yun", "useful_god", "comprehensive"]
        
        samples = []
        for _ in range(count):
            task_type = self.rng.choice(task_types)
            samples.append(self.generate_sample(task_type))
        return samples

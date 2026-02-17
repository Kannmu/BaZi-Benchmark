"""数据格式定义。"""

from __future__ import annotations

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class BaziChart(BaseModel):
    """八字四柱排盘结果"""
    year: str = Field(..., description="年柱干支")
    month: str = Field(..., description="月柱干支")
    day: str = Field(..., description="日柱干支")
    hour: str = Field(..., description="时柱干支")
    year_stem: str = Field(..., description="年干")
    year_branch: str = Field(..., description="年支")
    month_stem: str = Field(..., description="月干")
    month_branch: str = Field(..., description="月支")
    day_stem: str = Field(..., description="日干")
    day_branch: str = Field(..., description="日支")
    hour_stem: str = Field(..., description="时干")
    hour_branch: str = Field(..., description="时支")


class WuxingAnalysis(BaseModel):
    """五行分析结果"""
    counts: Dict[str, int] = Field(..., description="五行计数")
    missing: List[str] = Field(..., description="缺失五行")
    sheng: Dict[str, str] = Field(..., description="相生关系")
    ke: Dict[str, str] = Field(..., description="相克关系")


class TenGodsAnalysis(BaseModel):
    """十神分析结果"""
    gods: List[str] = Field(..., description="四柱天干十神(年/月/日/时)")
    counts: Dict[str, int] = Field(..., description="十神计数")


class StrengthAnalysis(BaseModel):
    """日主强弱分析结果"""
    score: float = Field(..., description="强弱得分")
    level: str = Field(..., description="强弱评级")


class InteractionsAnalysis(BaseModel):
    """刑冲合害分析结果"""
    liuhe: List[List[str]] = Field(..., description="六合")
    liuchong: List[List[str]] = Field(..., description="六冲")
    sanhe: List[List[str]] = Field(..., description="三合")
    xing: List[List[str]] = Field(..., description="相刑")
    self_xing: List[str] = Field(..., description="自刑")


class BaziAnalysis(BaseModel):
    """完整的八字分析结果"""
    chart: BaziChart
    wuxing: WuxingAnalysis
    ten_gods: TenGodsAnalysis
    strength: StrengthAnalysis
    interactions: InteractionsAnalysis


class BaziInput(BaseModel):
    """八字输入参数"""
    year: int = Field(..., description="公历年份")
    month: int = Field(..., description="公历月份")
    day: int = Field(..., description="公历日期")
    hour: int = Field(..., description="公历小时")
    minute: int = Field(0, description="公历分钟")


class BaziSample(BaseModel):
    """测试样本"""
    id: str = Field(..., description="样本ID")
    input: BaziInput = Field(..., description="输入参数")
    ground_truth: BaziAnalysis = Field(..., description="标准分析结果")
    instruction: str = Field(..., description="测试指令/问题")
    expected_output: str = Field(..., description="期望输出/参考答案")
    difficulty: int = Field(..., description="难度等级(1-5)")
    tags: List[str] = Field(default_factory=list, description="标签")
    meta: Dict[str, Any] = Field(default_factory=dict, description="元数据")

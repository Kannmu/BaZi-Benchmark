import pytest
import os
import json
from unittest.mock import MagicMock
from bazibench.evaluation.evaluator import Evaluator
from bazibench.models.base import ModelBase
from bazibench.dataset.schema import BaziSample, BaziInput, BaziAnalysis, BaziChart, WuxingAnalysis, TenGodsAnalysis, StrengthAnalysis, InteractionsAnalysis

class MockModel(ModelBase):
    def __init__(self, name="mock-model"):
        super().__init__(name)
        
    def generate(self, prompt: str, **kwargs) -> str:
        # 简单返回一个可以被 exact match 的 JSON
        return '{"result": "mock"}'

def test_evaluator_integration(tmp_path):
    # 构造完整的 BaziSample 对象需要很多嵌套对象，这里简化处理
    # 为了测试方便，我们只关注 evaluation 流程，不需要真实的八字数据
    # 但是 schema 校验很严格，我们需要构造合法的对象
    
    dummy_chart = BaziChart(
        year="甲子", month="乙丑", day="丙寅", hour="丁卯",
        year_stem="甲", year_branch="子",
        month_stem="乙", month_branch="丑",
        day_stem="丙", day_branch="寅",
        hour_stem="丁", hour_branch="卯"
    )
    dummy_wuxing = WuxingAnalysis(counts={}, missing=[], sheng={}, ke={})
    dummy_ten_gods = TenGodsAnalysis(gods=[], counts={})
    dummy_strength = StrengthAnalysis(score=0.0, level="neutral")
    dummy_interactions = InteractionsAnalysis(liuhe=[], liuchong=[], sanhe=[], xing=[], self_xing=[])
    
    dummy_analysis = BaziAnalysis(
        chart=dummy_chart,
        wuxing=dummy_wuxing,
        ten_gods=dummy_ten_gods,
        strength=dummy_strength,
        interactions=dummy_interactions
    )

    samples = [
        BaziSample(
            id="test_001",
            input=BaziInput(year=2024, month=1, day=1, hour=0),
            ground_truth=dummy_analysis, # 这个字段在 schema 中是 BaziAnalysis 类型，但在 evaluator 中主要用 expected_output 来评分
            instruction="测试指令",
            expected_output='{"result": "mock"}',
            difficulty=1,
            tags=["test"],
            evaluation_type="exact_match"
        ),
        BaziSample(
            id="test_002",
            input=BaziInput(year=2024, month=1, day=1, hour=0),
            ground_truth=dummy_analysis,
            instruction="测试指令2",
            expected_output='{"result": "mock"}',
            difficulty=2,
            tags=["test"],
            evaluation_type="exact_match"
        )
    ]
    
    # 准备模型和评估器
    model = MockModel()
    output_dir = str(tmp_path / "results")
    evaluator = Evaluator(model, output_dir)
    
    # 运行评估
    results = evaluator.evaluate(samples, batch_size=1)
    
    # 验证结果
    assert len(results) == 2
    assert results[0]["score"] == 1.0
    assert results[1]["score"] == 1.0
    
    # 验证文件输出
    result_file = os.path.join(output_dir, "mock-model_results.jsonl")
    assert os.path.exists(result_file)
    
    metrics_file = os.path.join(output_dir, "mock-model_metrics.json")
    assert os.path.exists(metrics_file)
    
    with open(metrics_file, "r") as f:
        metrics = json.load(f)
        assert metrics["overall"]["accuracy"] == 1.0
        assert metrics["by_difficulty"]["1"]["accuracy"] == 1.0

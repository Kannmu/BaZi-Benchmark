import pytest
import os
import json
from bazibench.models.base import ModelBase
from bazibench.evaluation.evaluator import Evaluator
from bazibench.dataset.schema import BaziSample, BaziInput, BaziAnalysis, BaziChart, WuxingAnalysis, TenGodsAnalysis, StrengthAnalysis, InteractionsAnalysis

class MockModel(ModelBase):
    def generate(self, prompt: str, **kwargs) -> str:
        return "This is a mock response."

@pytest.fixture
def sample_data():
    return BaziSample(
        id="test_001",
        input=BaziInput(year=2024, month=1, day=1, hour=12),
        ground_truth=BaziAnalysis(
            chart=BaziChart(
                year="甲辰", month="丙寅", day="甲子", hour="庚午",
                year_stem="甲", year_branch="辰",
                month_stem="丙", month_branch="寅",
                day_stem="甲", day_branch="子",
                hour_stem="庚", hour_branch="午"
            ),
            wuxing=WuxingAnalysis(
                counts={"木": 2, "火": 2, "土": 1, "金": 1, "水": 2},
                missing=[],
                sheng={},
                ke={}
            ),
            ten_gods=TenGodsAnalysis(gods=[], counts={}),
            strength=StrengthAnalysis(score=0.5, level="Balanced"),
            interactions=InteractionsAnalysis(
                liuhe=[], liuchong=[], sanhe=[], sanhui=[], xing=[], self_xing=[], liuhai=[]
            )
        ),
        instruction="Analyze this bazi.",
        expected_output="Analysis...",
        difficulty=1,
        tags=["test"]
    )

def test_evaluator(tmp_path, sample_data):
    model = MockModel("mock-model")
    output_dir = tmp_path / "results"
    evaluator = Evaluator(model, str(output_dir))
    
    results = evaluator.evaluate([sample_data])
    
    assert len(results) == 1
    assert results[0]["model_output"] == "This is a mock response."
    assert results[0]["sample_id"] == "test_001"
    
    # Check if file was created
    result_file = output_dir / "mock-model_results.jsonl"
    assert result_file.exists()
    
    with open(result_file, "r") as f:
        line = f.readline()
        saved_result = json.loads(line)
        assert saved_result["sample_id"] == "test_001"

"""测试数据集生成器。"""

import pytest
from datetime import datetime
from bazibench.dataset.generator import BaziDatasetGenerator
from bazibench.dataset.schema import BaziSample, BaziAnalysis

def test_generator_initialization():
    generator = BaziDatasetGenerator()
    assert generator.calculator is not None

def test_generate_random_date():
    generator = BaziDatasetGenerator()
    dt = generator.generate_random_date(2020, 2021)
    assert 2020 <= dt.year <= 2021

def test_analyze():
    generator = BaziDatasetGenerator()
    dt = datetime(2024, 2, 4, 12, 0)  # 立春附近
    analysis = generator.analyze(dt)
    assert isinstance(analysis, BaziAnalysis)
    assert analysis.chart.year_stem is not None
    assert analysis.wuxing.counts is not None

def test_generate_sample_chart():
    generator = BaziDatasetGenerator()
    sample = generator.generate_sample("chart")
    assert isinstance(sample, BaziSample)
    assert "排出八字四柱" in sample.instruction
    assert sample.difficulty == 2
    assert sample.tags == ["chart"]

def test_generate_sample_wuxing():
    generator = BaziDatasetGenerator()
    sample = generator.generate_sample("wuxing")
    assert "五行个数" in sample.instruction
    assert "五行统计" in sample.expected_output

def test_generate_batch():
    generator = BaziDatasetGenerator()
    samples = generator.generate_batch(5)
    assert len(samples) == 5
    for sample in samples:
        assert isinstance(sample, BaziSample)

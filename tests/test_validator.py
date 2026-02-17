"""测试数据验证器。"""

import pytest
from datetime import datetime
from bazibench.dataset.generator import BaziDatasetGenerator
from bazibench.dataset.validator import BaziValidator

def test_validator_initialization():
    validator = BaziValidator()
    assert validator is not None

def test_validate_sample():
    generator = BaziDatasetGenerator()
    sample = generator.generate_sample("chart")
    
    validator = BaziValidator()
    errors = validator.validate_sample(sample)
    assert len(errors) == 0

def test_validate_batch():
    generator = BaziDatasetGenerator()
    samples = generator.generate_batch(5)
    
    validator = BaziValidator()
    results = validator.validate_batch(samples)
    assert len(results) == 0

def test_validate_invalid_sample():
    generator = BaziDatasetGenerator()
    sample = generator.generate_sample("chart")
    
    # 手动制造错误
    sample.ground_truth.chart.year_stem = "Invalid"
    
    validator = BaziValidator()
    errors = validator.validate_sample(sample)
    assert len(errors) > 0
    assert "Invalid stem" in errors[0]

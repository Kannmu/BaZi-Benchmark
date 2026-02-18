"""
BaZiBench: A comprehensive benchmark for Large Language Models on BaZi (Chinese Four Pillars) analysis.
"""

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from .core.calculator import BaZiCalculator
from .dataset.generator import BaziDatasetGenerator
from .dataset.schema import BaziSample, BaziAnalysis
from .evaluation.evaluator import Evaluator
from .models.registry import ModelRegistry

__version__ = "0.1.0"
__all__ = [
    "BaZiCalculator",
    "BaziDatasetGenerator",
    "BaziSample",
    "BaziAnalysis",
    "Evaluator",
    "ModelRegistry"
]

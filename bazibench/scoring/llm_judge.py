from typing import Any, Dict
from .base import BaseScorer
from ..models.base import ModelBase
import re

class LLMJudgeScorer(BaseScorer):
    """使用 LLM 进行评分"""
    
    def __init__(self, judge_model: ModelBase):
        self.judge_model = judge_model
        
    def score(self, ground_truth: Any, response: Any) -> float:
        """
        使用 LLM 评估回答质量
        """
        prompt = self._build_judge_prompt(ground_truth, response)
        try:
            judge_response = self.judge_model.generate(prompt)
            return self._parse_judge_score(judge_response)
        except Exception as e:
            print(f"LLM Judge scoring failed: {e}")
            return 0.0
        
    def _build_judge_prompt(self, ground_truth: Any, response: Any) -> str:
        return f"""你是一个公正的八字命理评判专家。请评估以下模型回答的准确性。

标准答案 (Ground Truth):
{ground_truth}

模型回答 (Model Response):
{response}

请根据以下标准给出 0 到 10 之间的评分（支持一位小数）：
- 10分：完全正确，逻辑清晰，包含所有关键信息。
- 8-9分：核心结论正确，细节有轻微偏差或遗漏。
- 6-7分：部分正确，主要结论基本符合，但有明显错误。
- 4-5分：包含一些正确信息，但核心结论错误。
- 1-3分：大部分错误，逻辑混乱。
- 0分：完全错误或未回答。

请按以下格式直接输出评分，不要包含其他无关内容：
评分: <分数>
理由: <简短理由>
"""

    def _parse_judge_score(self, response: str) -> float:
        """解析 LLM 返回的分数"""
        # 匹配 "评分: 8.5" 或 "Score: 8.5"
        match = re.search(r"(?:评分|Score):\s*(\d+(?:\.\d+)?)", response, re.IGNORECASE)
        if match:
            score = float(match.group(1))
            # 归一化到 0-1
            return min(max(score / 10.0, 0.0), 1.0)
            
        # 尝试直接匹配数字
        match = re.search(r"^(\d+(?:\.\d+)?)$", response.strip())
        if match:
             score = float(match.group(1))
             return min(max(score / 10.0, 0.0), 1.0)
             
        return 0.0

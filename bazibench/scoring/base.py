from abc import ABC, abstractmethod
from typing import Any, Dict, Union, List

class BaseScorer(ABC):
    """评分器基类"""
    
    @abstractmethod
    def score(self, ground_truth: Any, response: Any) -> float:
        """
        计算得分
        
        Args:
            ground_truth: 标准答案
            response: 模型输出
            
        Returns:
            float: 0.0 到 1.0 之间的分数
        """
        pass

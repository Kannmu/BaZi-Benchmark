import json
import re
from typing import Any, Dict, Union, List
from .base import BaseScorer
from .exact_match import ExactMatchScorer

class PartialMatchScorer(ExactMatchScorer):
    """部分匹配评分器"""
    
    def score(self, ground_truth: Any, response: Any) -> float:
        parsed_response = self._parse_response(response)
        parsed_ground_truth = self._parse_response(ground_truth)
        
        if parsed_response is None:
            return 0.0
            
        if isinstance(parsed_ground_truth, dict):
            if not isinstance(parsed_response, dict):
                return 0.0
                
            correct_count = 0
            total_count = len(parsed_ground_truth)
            
            for key, value in parsed_ground_truth.items():
                if key in parsed_response and parsed_response[key] == value:
                    correct_count += 1
            
            return correct_count / total_count if total_count > 0 else 0.0
            
        elif isinstance(parsed_ground_truth, list):
             if not isinstance(parsed_response, list):
                 return 0.0
             
             # 计算交集大小
             try:
                 intersection = len(set(parsed_ground_truth) & set(parsed_response))
                 return intersection / len(parsed_ground_truth) if parsed_ground_truth else 0.0
             except TypeError:
                 return 1.0 if parsed_response == parsed_ground_truth else 0.0
             
        else:
            return 1.0 if str(parsed_response).strip() == str(parsed_ground_truth).strip() else 0.0

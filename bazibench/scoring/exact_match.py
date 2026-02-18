import json
import re
from typing import Any, Dict, Union, List
from .base import BaseScorer

class ExactMatchScorer(BaseScorer):
    """精确匹配评分器"""
    
    def score(self, ground_truth: Any, response: Any) -> float:
        parsed_response = self._parse_response(response)
        parsed_ground_truth = self._parse_response(ground_truth)
        
        if parsed_response is None:
            return 0.0
            
        if isinstance(parsed_ground_truth, dict):
            if not isinstance(parsed_response, dict):
                return 0.0
            
            # 检查所有键值对是否完全匹配
            if len(parsed_ground_truth) != len(parsed_response):
                return 0.0
                
            for key, value in parsed_ground_truth.items():
                if key not in parsed_response or parsed_response[key] != value:
                    return 0.0
            return 1.0
            
        elif isinstance(parsed_ground_truth, list):
            if not isinstance(parsed_response, list):
                return 0.0
            
            if len(parsed_ground_truth) != len(parsed_response):
                return 0.0
            
            # 简单比较列表内容（顺序敏感）
            return 1.0 if parsed_response == parsed_ground_truth else 0.0
            
        else:
            return 1.0 if str(parsed_response).strip() == str(parsed_ground_truth).strip() else 0.0

    def _parse_response(self, response: Any) -> Any:
        """从模型输出中提取并解析 JSON"""
        if not isinstance(response, str):
            return response
            
        # 尝试提取 JSON 代码块
        json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # 尝试直接解析
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
            
        return response.strip()

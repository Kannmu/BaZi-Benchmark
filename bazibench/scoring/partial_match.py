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
            
            for key, gt_value in parsed_ground_truth.items():
                if key not in parsed_response:
                    continue
                    
                resp_value = parsed_response[key]
                
                # Special handling for interactions (lists of lists)
                if isinstance(gt_value, list) and isinstance(resp_value, list):
                    score = self._match_interactions(key, gt_value, resp_value)
                    correct_count += score
                
                # Soft matching for strings (strength, useful_god)
                elif self._match_value(key, gt_value, resp_value):
                    correct_count += 1
                    
                # Standard equality check for other types
                elif gt_value == resp_value:
                    correct_count += 1
            
            return correct_count / total_count if total_count > 0 else 0.0
            
        elif isinstance(parsed_ground_truth, list):
             if not isinstance(parsed_response, list):
                 return 0.0
             
             return self._match_interactions("list", parsed_ground_truth, parsed_response)
             
        else:
            return 1.0 if str(parsed_response).strip() == str(parsed_ground_truth).strip() else 0.0

    def _match_interactions(self, key: str, gt_list: List, resp_list: List) -> float:
        """Handle interactions matching with normalization"""
        if not gt_list:
            return 1.0 if not resp_list else 0.0
            
        # Normalize function
        def normalize(item):
            if isinstance(item, list):
                # Recursively normalize list items in case of nested structures
                return tuple(sorted(normalize(i) for i in item))
            if isinstance(item, dict):
                # Convert dict to sorted tuple of items
                return tuple(sorted((k, normalize(v)) for k, v in item.items()))
            return item
            
        # Special handling for self_xing: ["午"] vs [["午", "午"]]
        if key == "self_xing":
            norm_gt = set()
            for x in gt_list:
                if isinstance(x, (list, tuple)) and len(x) == 2 and x[0] == x[1]:
                    norm_gt.add(x[0])
                elif isinstance(x, str):
                    norm_gt.add(x)
                else:
                    norm_gt.add(normalize(x))
            
            norm_resp = set()
            for x in resp_list:
                if isinstance(x, (list, tuple)) and len(x) == 2 and x[0] == x[1]:
                    norm_resp.add(x[0])
                elif isinstance(x, str):
                    norm_resp.add(x)
                else:
                    try:
                        norm_resp.add(normalize(x))
                    except TypeError:
                        pass # Ignore unhashable items that we can't normalize
        else:
            norm_gt = set(normalize(x) for x in gt_list)
            norm_resp = set()
            for x in resp_list:
                try:
                    norm_resp.add(normalize(x))
                except TypeError:
                    pass

            
        if not norm_gt:
            return 0.0
            
        match_count = len(norm_gt.intersection(norm_resp))
        return match_count / len(norm_gt)

    def _match_value(self, key: str, gt_val: Any, resp_val: Any) -> bool:
        """Soft match for values"""
        if gt_val == resp_val:
            return True
            
        if isinstance(gt_val, str) and isinstance(resp_val, str):
            # Strength
            if key == "level":
                map_val = {
                    "身强": ["强", "身旺", "旺", "偏强"], 
                    "身弱": ["弱", "偏弱"], 
                    "中和": []
                }
                if gt_val in map_val:
                    if resp_val in map_val[gt_val]: return True
                    if resp_val == gt_val.replace("身", ""): return True
            
            # Useful God
            if key == "useful_god":
                # Keywords: 印, 比, 官, 杀, 食, 伤, 财
                keywords = ["印", "比", "官", "杀", "食", "伤", "财"]
                gt_kws = {k for k in keywords if k in gt_val}
                resp_kws = {k for k in keywords if k in resp_val}
                
                # If we found keywords in GT, check if they exist in Resp
                if gt_kws:
                    # Require at least one matching keyword, or all?
                    # Usually "印比" means both are good.
                    # If model says "印", it's partially correct.
                    # But boolean return here implies full correctness for this key.
                    # Let's require subset or high overlap.
                    if gt_kws.issubset(resp_kws):
                        return True
                    # Relaxed: if intersection is not empty? No, "印" vs "财" is bad.
                    # "印比" vs "印" -> OK?
                    if len(gt_kws.intersection(resp_kws)) >= len(gt_kws) * 0.5:
                         return True
                         
        return False

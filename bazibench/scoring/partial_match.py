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
            
        return self._recursive_score(parsed_ground_truth, parsed_response)

    def _recursive_score(self, gt: Any, resp: Any) -> float:
        if isinstance(gt, dict):
            # Special handling for strength if resp is string
            if isinstance(resp, str) and ("level" in gt or "score" in gt):
                # Try to extract level from string
                extracted_level = self._extract_level_from_text(resp)
                if extracted_level and "level" in gt:
                    # Construct a temporary dict for comparison
                    resp = {"level": extracted_level}
                else:
                    return 0.0

            if not isinstance(resp, dict):
                return 0.0
                
            correct_count = 0.0
            total_count = len(gt)
            
            for key, gt_val in gt.items():
                # Key normalization (e.g. wood -> 木)
                resp_key = key
                if key not in resp:
                    # check aliases
                    aliases = {
                        "木": "wood", "火": "fire", "土": "earth", "金": "metal", "水": "water",
                        "wood": "木", "fire": "火", "earth": "土", "metal": "金", "water": "水"
                    }
                    if aliases.get(key) in resp:
                        resp_key = aliases[key]
                    else:
                        continue # Key missing, 0 points for this key
                
                resp_val = resp[resp_key]
                
                # Recursive step
                if isinstance(gt_val, dict):
                     correct_count += self._recursive_score(gt_val, resp_val)
                elif isinstance(gt_val, list):
                     correct_count += self._match_interactions(key, gt_val, resp_val)
                else:
                     # Value matching
                     if self._match_value(key, gt_val, resp_val):
                         correct_count += 1
                     elif gt_val == resp_val:
                         correct_count += 1
            
            return correct_count / total_count if total_count > 0 else 0.0
            
        elif isinstance(gt, list):
             if not isinstance(resp, list):
                 return 0.0
             
             return self._match_interactions("list", gt, resp)
             
        else:
            return 1.0 if str(resp).strip() == str(gt).strip() else 0.0

    def _extract_level_from_text(self, text: str) -> Union[str, None]:
        if "身强" in text or "身旺" in text or "偏强" in text:
            return "身强"
        if "身弱" in text or "偏弱" in text:
            return "身弱"
        if "中和" in text:
            return "中和"
        return None

    def _match_interactions(self, key: str, gt_list: List, resp_list: List) -> float:
        """Handle interactions matching with normalization"""
        if not gt_list:
            return 1.0 if not resp_list else 0.0
            
        # Special handling for Useful God / Unfavorable elements (Loose matching)
        if key in ["god", "unfavorable", "useful_god", "missing"]:
            def normalize_loose(item):
                if not isinstance(item, str): return str(item)
                item = item.strip()
                # Wuxing
                if "木" in item: return "木"
                if "火" in item: return "火"
                if "土" in item: return "土"
                if "金" in item: return "金"
                if "水" in item: return "水"
                # Ten Gods (Grouped)
                if "印" in item or "枭" in item: return "印"
                if "官" in item or "杀" in item: return "官杀"
                if "财" in item: return "财"
                if "食" in item or "伤" in item: return "食伤"
                if "比" in item or "劫" in item: return "比劫"
                return item

            norm_gt = set(normalize_loose(x) for x in gt_list)
            norm_resp = set(normalize_loose(x) for x in resp_list)
            
            if not norm_gt:
                return 0.0
            
            match_count = len(norm_gt.intersection(norm_resp))
            return match_count / len(norm_gt)

        # Normalize function for strict matching
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
            
        # Float comparison with tolerance
        if isinstance(gt_val, (int, float)) and isinstance(resp_val, (int, float)):
             if abs(gt_val - resp_val) < 0.1: # Tolerance
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

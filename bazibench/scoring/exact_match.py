import json
import re
from typing import Any, Dict, Union, List
from .base import BaseScorer

class ExactMatchScorer(BaseScorer):
    """精确匹配评分器 - 支持智能文本匹配"""
    
    def score(self, ground_truth: Any, response: Any) -> float:
        parsed_response = self._parse_response(response)
        parsed_ground_truth = self._parse_response(ground_truth)
        
        if parsed_response is None:
            return 0.0
            
        if isinstance(parsed_ground_truth, dict):
            if not isinstance(parsed_response, dict):
                return 0.0
            
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
            
            return 1.0 if parsed_response == parsed_ground_truth else 0.0
            
        else:
            return self._text_match(str(parsed_ground_truth), str(parsed_response))

    def _text_match(self, ground_truth: str, response: str) -> float:
        """智能文本匹配"""
        ground_truth = ground_truth.strip()
        response = response.strip()
        
        if ground_truth == response:
            return 1.0
        
        if self._extract_wuxing_counts(ground_truth) and self._extract_wuxing_counts(response):
            gt_counts = self._extract_wuxing_counts(ground_truth)
            resp_counts = self._extract_wuxing_counts(response)
            if gt_counts == resp_counts:
                missing_gt = self._extract_missing_wuxing(ground_truth)
                missing_resp = self._extract_missing_wuxing(response)
                if missing_gt == missing_resp:
                    return 1.0
                return 0.7
            
            missing_gt = self._extract_missing_wuxing(ground_truth)
            missing_resp = self._extract_missing_wuxing(response)
            if missing_gt == missing_resp:
                common_elements = set(gt_counts.keys()) & set(resp_counts.keys())
                if common_elements:
                    total_diff = sum(abs(gt_counts.get(k, 0) - resp_counts.get(k, 0)) for k in ['金', '木', '水', '火', '土'])
                    max_diff = 8
                    similarity = max(0, 1 - total_diff / max_diff)
                    return max(0.3, similarity)
            
            return 0.0
        
        if self._extract_ten_gods(ground_truth):
            gt_gods = self._extract_ten_gods(ground_truth)
            resp_gods = self._extract_ten_gods(response)
            if gt_gods and gt_gods == resp_gods:
                return 1.0
            if gt_gods and resp_gods:
                match_count = sum(1 for g in gt_gods if g in resp_gods)
                return match_count / len(gt_gods) if gt_gods else 0.0
        
        if self._extract_strength(ground_truth):
            gt_strength = self._extract_strength(ground_truth)
            resp_strength = self._extract_strength(response)
            if gt_strength and gt_strength in resp_strength:
                gt_score = self._extract_strength_score(ground_truth)
                resp_score = self._extract_strength_score(response)
                if gt_score is not None and resp_score is not None:
                    if abs(gt_score - resp_score) < 0.5:
                        return 1.0
                    elif abs(gt_score - resp_score) < 1.0:
                        return 0.7
                return 0.8
            return 0.0
        
        if self._extract_bazi_chart(ground_truth):
            gt_chart = self._extract_bazi_chart(ground_truth)
            resp_chart = self._extract_bazi_chart(response)
            if gt_chart and gt_chart == resp_chart:
                return 1.0
            if gt_chart and resp_chart:
                match_count = sum(1 for g in gt_chart if g in resp_chart)
                return match_count / len(gt_chart) if gt_chart else 0.0
        
        return 1.0 if ground_truth in response else 0.0

    def _extract_wuxing_counts(self, text: str) -> Dict[str, int]:
        """提取五行计数"""
        counts = {}
        # Remove markdown bold/italic markers for easier matching
        clean_text = text.replace("**", "").replace("__", "")
        
        patterns = [
            (r'金[：:]\s*(\d+)', '金'),
            (r'木[：:]\s*(\d+)', '木'),
            (r'水[：:]\s*(\d+)', '水'),
            (r'火[：:]\s*(\d+)', '火'),
            (r'土[：:]\s*(\d+)', '土'),
            (r'金(\d+)', '金'),
            (r'木(\d+)', '木'),
            (r'水(\d+)', '水'),
            (r'火(\d+)', '火'),
            (r'土(\d+)', '土'),
        ]
        for pattern, element in patterns:
            match = re.search(pattern, clean_text)
            if match:
                counts[element] = int(match.group(1))
        return counts

    def _extract_missing_wuxing(self, text: str) -> List[str]:
        """提取缺失五行"""
        clean_text = text.replace("**", "").replace("__", "")
        if '无' in clean_text or '俱全' in clean_text or '没有缺失' in clean_text or '五行俱全' in clean_text:
            return []
        match = re.search(r'缺失[五行]*[：:]\s*([^\n，。]+)', clean_text)
        if match:
            missing_str = match.group(1)
            return [w for w in ['金', '木', '水', '火', '土'] if w in missing_str]
        return []

    def _extract_ten_gods(self, text: str) -> List[str]:
        """提取十神"""
        gods = ['比肩', '劫财', '食神', '伤官', '偏财', '正财', '七杀', '正官', '偏印', '正印']
        found = []
        for god in gods:
            if god in text:
                found.append(god)
        return found

    def _extract_strength(self, text: str) -> str:
        """提取强弱判断"""
        text = text.replace("身旺", "身强").replace("偏强", "身强").replace("偏弱", "身弱")
        if '身强' in text:
            return '身强'
        elif '身弱' in text:
            return '身弱'
        elif '中和' in text:
            return '中和'
        return ''

    def _extract_strength_score(self, text: str) -> float:
        """提取强弱得分"""
        clean_text = text.replace("**", "").replace("__", "")
        match = re.search(r'得分[：:]\s*([+-]?\d+\.?\d*)', clean_text)
        if match:
            return float(match.group(1))
        return None

    def _extract_bazi_chart(self, text: str) -> List[str]:
        """提取八字四柱"""
        # Allow arbitrary text between pillars, but capture the 4 pillars in order
        pattern = r'([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]).*?' \
                 r'([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]).*?' \
                 r'([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]).*?' \
                 r'([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])'
        
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return [match.group(i) for i in range(1, 5)]
        return []

    def _parse_response(self, response: Any) -> Any:
        """从模型输出中提取并解析 JSON"""
        if not isinstance(response, str):
            return response
            
        json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
            
        return response.strip()

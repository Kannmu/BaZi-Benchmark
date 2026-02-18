import pytest
import json
from bazibench.scoring import ExactMatchScorer, PartialMatchScorer

class TestScorers:
    def test_exact_match_scorer(self):
        scorer = ExactMatchScorer()
        
        # 字符串匹配
        assert scorer.score("A", "A") == 1.0
        assert scorer.score("A", "B") == 0.0
        
        # 字典匹配
        truth = {"a": 1, "b": 2}
        assert scorer.score(truth, '{"a": 1, "b": 2}') == 1.0
        assert scorer.score(truth, '{"a": 1, "b": 3}') == 0.0
        assert scorer.score(truth, '{"a": 1}') == 0.0
        
        # JSON 块提取
        response = "Here is the json:\n```json\n{\"a\": 1, \"b\": 2}\n```"
        assert scorer.score(truth, response) == 1.0
        
    def test_partial_match_scorer(self):
        scorer = PartialMatchScorer()
        
        # 字典部分匹配
        truth = {"a": 1, "b": 2, "c": 3}
        assert scorer.score(truth, '{"a": 1, "b": 2, "c": 3}') == 1.0
        assert abs(scorer.score(truth, '{"a": 1, "b": 2, "c": 4}') - 2/3) < 1e-6
        assert abs(scorer.score(truth, '{"a": 1}') - 1/3) < 1e-6
        
        # 列表部分匹配
        truth_list = ["A", "B", "C"]
        assert scorer.score(truth_list, '["A", "B", "C"]') == 1.0
        # set intersection may vary if order doesn't matter, but list comparison assumes order matters? 
        # Wait, PartialMatchScorer for list uses set intersection: len(set(ground_truth) & set(parsed_response))
        assert abs(scorer.score(truth_list, '["A", "B"]') - 2/3) < 1e-6
        assert abs(scorer.score(truth_list, '["A", "D"]') - 1/3) < 1e-6

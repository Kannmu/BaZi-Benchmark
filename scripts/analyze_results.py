#!/usr/bin/env python
import json
import sys

results_file = sys.argv[1] if len(sys.argv) > 1 else "data/results/xiaomi_mimo-v2-flash-free_results.jsonl"

with open(results_file, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if i >= 5:
            break
        data = json.loads(line)
        print(f'=== 样本 {i+1} ===')
        print(f'标签: {data["tags"]}')
        print(f'期望: {data["expected_output"]}')
        print(f'得分: {data["score"]}')
        print()

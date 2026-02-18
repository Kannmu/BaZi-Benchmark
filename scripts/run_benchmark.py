#!/usr/bin/env python
"""
BaZiBench 评估运行脚本

用法:
    python scripts/run_benchmark.py --model xiaomi/mimo-v2-flash-free --samples 30
    python scripts/run_benchmark.py --model xiaomi/mimo-v2-flash-free --input data/samples/bazi_benchmark_v1.jsonl
"""

import os
import sys
import json
import random
import argparse
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from bazibench.models import ModelRegistry
from bazibench.evaluation import Evaluator
from bazibench.dataset.schema import BaziSample


def load_samples(file_path: str, limit: int = None, random_sample: int = None) -> list:
    """加载样本数据"""
    samples = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    samples.append(BaziSample.model_validate_json(line))
                except Exception:
                    try:
                        samples.append(BaziSample.parse_raw(line))
                    except Exception:
                        continue
    
    if random_sample and random_sample < len(samples):
        random.seed(42)
        samples = random.sample(samples, random_sample)
    elif limit:
        samples = samples[:limit]
    
    return samples


def main():
    parser = argparse.ArgumentParser(description="BaZiBench 评估脚本")
    parser.add_argument("--model", type=str, required=True, help="模型名称")
    parser.add_argument("--input", type=str, default=None, help="输入数据文件路径")
    parser.add_argument("--samples", type=int, default=100, help="随机抽取的样本数量")
    parser.add_argument("--limit", type=int, default=None, help="限制样本数量(从头部开始)")
    parser.add_argument("--batch-size", type=int, default=1, help="并发数")
    parser.add_argument("--output-dir", type=str, default=None, help="输出目录")
    parser.add_argument("--config", type=str, default=None, help="模型配置文件路径")
    parser.add_argument("--judge-model", type=str, default="qwen/qwen3.5-plus", help="评判模型名称")
    
    args = parser.parse_args()
    
    config_path = args.config or str(project_root / "data" / "configs" / "models.yaml")
    registry = ModelRegistry(config_path)
    
    input_path = args.input or str(project_root / "data" / "samples" / "bazi_benchmark.jsonl")
    
    if not os.path.exists(input_path):
        print(f"错误: 数据文件不存在: {input_path}")
        sys.exit(1)
    
    print(f"加载数据: {input_path}")
    samples = load_samples(input_path, limit=args.limit, random_sample=args.samples)
    print(f"加载样本数: {len(samples)}")
    
    output_dir = args.output_dir or str(project_root / "data" / "results")
    
    print(f"\n初始化模型: {args.model}")
    try:
        model = registry.get_model(args.model)
    except Exception as e:
        print(f"模型初始化失败: {e}")
        sys.exit(1)
        
    judge_model = None
    try:
        judge_model = registry.get_model(args.judge_model)
        print(f"初始化评判模型: {args.judge_model}")
    except Exception as e:
        print(f"评判模型初始化失败: {e}，将不使用 LLM Judge")
    
    print(f"输出目录: {output_dir}")
    print(f"并发数: {args.batch_size}")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    evaluator = Evaluator(model=model, output_dir=output_dir, judge_model=judge_model)
    
    results = evaluator.evaluate(samples, batch_size=args.batch_size)
    
    print("-" * 50)
    print(f"评估完成: {len(results)} 个样本")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    metrics_path = os.path.join(output_dir, f"{args.model.replace('/', '_')}_metrics.json")
    if os.path.exists(metrics_path):
        with open(metrics_path, "r", encoding="utf-8") as f:
            metrics = json.load(f)
        
        print("\n=== 评估指标 ===")
        if "overall" in metrics:
            print(f"总体准确率: {metrics['overall'].get('accuracy', 0):.4f}")
            print(f"标准差: {metrics['overall'].get('std', 0):.4f}")
            print(f"样本总数: {metrics['overall'].get('total_samples', 0)}")
        
        if "by_difficulty" in metrics and metrics["by_difficulty"]:
            print("\n按难度分布:")
            for diff, data in sorted(metrics["by_difficulty"].items()):
                print(f"  难度 {diff}: 准确率 {data.get('accuracy', 0):.4f} ({data.get('count', 0)} 样本)")
        
        if "by_tag" in metrics and metrics["by_tag"]:
            print("\n按标签分布:")
            for tag, data in sorted(metrics["by_tag"].items()):
                print(f"  {tag}: 准确率 {data.get('accuracy', 0):.4f} ({data.get('count', 0)} 样本)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBenchmark interrupted by user. Exiting...")
        sys.exit(1)

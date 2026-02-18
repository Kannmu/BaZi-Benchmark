"""生成标准数据集。"""

import json
import os
import random
import multiprocessing as mp
from functools import partial
from tqdm import tqdm
from bazibench.dataset.generator import BaziDatasetGenerator
from bazibench.dataset.validator import BaziValidator

def _generate_batch_worker(args):
    """批量生成工作函数，返回序列化后的JSON字符串列表"""
    task_types, batch_size, base_seed = args
    generator = BaziDatasetGenerator(seed=base_seed)
    validator = BaziValidator()
    
    valid_samples = []
    errors_count = 0
    for i in range(batch_size):
        task_type = random.Random(base_seed + i).choice(task_types)
        try:
            sample = generator.generate_sample(task_type)
            errors = validator.validate_sample(sample)
            if not errors:
                valid_samples.append(sample.model_dump_json())
            else:
                errors_count += 1
        except Exception as e:
            errors_count += 1
    return valid_samples, errors_count

def main():
    output_dir = "data/samples"
    os.makedirs(output_dir, exist_ok=True)
    
    task_types = ["chart", "wuxing", "ten_gods", "strength", "interactions", "da_yun", "useful_god", "comprehensive"]
    total_samples = 1000
    
    num_workers = max(1, mp.cpu_count() - 1)
    print(f"Using {num_workers} workers for parallel generation...")
    
    valid_samples = []
    total_errors = 0
    
    print(f"Generating {total_samples} samples...")
    
    batch_size = 50
    num_batches = (total_samples + batch_size - 1) // batch_size
    
    with mp.Pool(processes=num_workers) as pool:
        batch_args = [
            (task_types, batch_size, 2024 + i * 1000)
            for i in range(num_batches)
        ]
        
        with tqdm(total=total_samples) as pbar:
            for samples_json, errors_count in pool.imap_unordered(_generate_batch_worker, batch_args):
                total_errors += errors_count
                for sample_json in samples_json:
                    if len(valid_samples) < total_samples:
                        valid_samples.append(sample_json)
                        pbar.update(1)
    
    print(f"Total validation errors: {total_errors}")
    valid_samples = valid_samples[:total_samples]
    
    output_file = os.path.join(output_dir, "bazi_benchmark.jsonl")
    with open(output_file, "w", encoding="utf-8") as f:
        for sample_json in valid_samples:
            f.write(sample_json + "\n")
            
    print(f"Successfully generated {len(valid_samples)} samples to {output_file}")
    
    stats = {}
    for sample_json in valid_samples:
        sample = json.loads(sample_json)
        tag = sample["tags"][0]
        stats[tag] = stats.get(tag, 0) + 1
        
    print("Sample distribution:")
    for tag, count in stats.items():
        print(f"  {tag}: {count}")

if __name__ == "__main__":
    main()

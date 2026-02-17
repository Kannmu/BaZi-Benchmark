"""生成初始数据集。"""

import json
import os
import random
from tqdm import tqdm
from bazibench.dataset.generator import BaziDatasetGenerator
from bazibench.dataset.validator import BaziValidator

def main():
    output_dir = "data/samples"
    os.makedirs(output_dir, exist_ok=True)
    
    generator = BaziDatasetGenerator(seed=2024)
    validator = BaziValidator()
    
    task_types = ["chart", "wuxing", "ten_gods", "strength"]
    total_samples = 1000
    
    valid_samples = []
    
    print(f"Generating {total_samples} samples...")
    
    # 使用tqdm显示进度
    with tqdm(total=total_samples) as pbar:
        while len(valid_samples) < total_samples:
            task_type = random.choice(task_types)
            try:
                sample = generator.generate_sample(task_type)
                errors = validator.validate_sample(sample)
                
                if not errors:
                    valid_samples.append(sample)
                    pbar.update(1)
                else:
                    # 如果有错误，可以在这里记录或忽略
                    pass
            except Exception as e:
                print(f"Error generating sample: {e}")
                continue
    
    # 保存为JSONL格式
    output_file = os.path.join(output_dir, "bazi_benchmark_v1.jsonl")
    with open(output_file, "w", encoding="utf-8") as f:
        for sample in valid_samples:
            f.write(sample.model_dump_json() + "\n")
            
    print(f"Successfully generated {len(valid_samples)} samples to {output_file}")
    
    # 简单的统计
    stats = {}
    for s in valid_samples:
        tag = s.tags[0]
        stats[tag] = stats.get(tag, 0) + 1
        
    print("Sample distribution:")
    for tag, count in stats.items():
        print(f"  {tag}: {count}")

if __name__ == "__main__":
    main()

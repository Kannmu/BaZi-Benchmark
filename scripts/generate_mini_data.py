"""生成迷你数据集。"""

import os
import random
from tqdm import tqdm
from bazibench.dataset.generator import BaziDatasetGenerator
from bazibench.dataset.validator import BaziValidator

def main():
    output_dir = "data/samples"
    os.makedirs(output_dir, exist_ok=True)
    
    generator = BaziDatasetGenerator(seed=2025) # New seed
    validator = BaziValidator()
    
    task_types = ["chart", "wuxing", "ten_gods", "strength"]
    total_samples = 50 # Small scale
    
    valid_samples = []
    
    print(f"Generating {total_samples} samples...")
    
    with tqdm(total=total_samples) as pbar:
        while len(valid_samples) < total_samples:
            task_type = random.choice(task_types)
            try:
                sample = generator.generate_sample(task_type)
                errors = validator.validate_sample(sample)
                
                if not errors:
                    valid_samples.append(sample)
                    pbar.update(1)
            except Exception as e:
                print(f"Error generating sample: {e}")
                continue
    
    output_file = os.path.join(output_dir, "bazi_benchmark_mini.jsonl")
    with open(output_file, "w", encoding="utf-8") as f:
        for sample in valid_samples:
            f.write(sample.model_dump_json() + "\n")
            
    print(f"Successfully generated {len(valid_samples)} samples to {output_file}")

if __name__ == "__main__":
    main()


import os
import json
import argparse
from tqdm import tqdm
from bazibench.dataset.generator import BaziDatasetGenerator

def generate_gold_standard(output_dir: str, samples_per_task: int = 100, seed: int = 2024):
    """
    Generate a static gold standard dataset for benchmarking.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    generator = BaziDatasetGenerator(seed=seed)
    
    tasks = [
        "chart", "wuxing", "ten_gods", "strength", 
        "interactions", "pattern", "da_yun", 
        "useful_god", "comprehensive"
    ]
    
    total_samples = 0
    
    print(f"Generating gold standard dataset in {output_dir}...")
    
    for task in tqdm(tasks, desc="Generating tasks"):
        samples = []
        for _ in range(samples_per_task):
            sample = generator.generate_sample(task_type=task)
            # Add a 'gold' tag
            sample.tags.append("gold_standard")
            samples.append(sample.model_dump())
            
        filename = f"{task}.jsonl"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            for s in samples:
                f.write(json.dumps(s, ensure_ascii=False) + "\n")
        
        total_samples += len(samples)
        
    print(f"Successfully generated {total_samples} samples across {len(tasks)} tasks.")
    print(f"Data saved to: {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Gold Standard Dataset")
    parser.add_argument("--output", type=str, default="bazibench/dataset/static", help="Output directory")
    parser.add_argument("--samples", type=int, default=50, help="Samples per task")
    parser.add_argument("--seed", type=int, default=8888, help="Random seed")
    
    args = parser.parse_args()
    
    generate_gold_standard(args.output, args.samples, args.seed)

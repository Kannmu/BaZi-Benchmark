import json
import random
import os

def main():
    input_file = "data/samples/bazi_benchmark.jsonl"
    output_file = "data/samples/bazi_benchmark_test_20.jsonl"
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    print(f"Reading from {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Total samples: {len(lines)}")
    
    if len(lines) < 20:
        print(f"Warning: Only {len(lines)} samples found. Extracting all.")
        samples = lines
    else:
        # Use a fixed seed for reproducibility
        random.seed(42)
        samples = random.sample(lines, 20)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(samples)
    
    print(f"Extracted {len(samples)} samples to {output_file}")

if __name__ == "__main__":
    main()

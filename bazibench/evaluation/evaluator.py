import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional, Union
from tqdm import tqdm
from ..models.base import ModelBase
from ..dataset.schema import BaziSample

class Evaluator:
    def __init__(self, model: ModelBase, output_dir: str):
        self.model = model
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self._lock = threading.Lock()
        
    def evaluate(self, samples: Union[List[BaziSample], str], batch_size: int = 1) -> List[Dict]:
        """
        Evaluate the model on a list of samples or a file path to samples.
        Supports resume functionality and concurrency.
        
        Args:
            samples: List of BaziSample objects or path to jsonl file
            batch_size: Number of concurrent threads
            
        Returns:
            List of evaluation results
        """
        if isinstance(samples, str):
            # Load samples from file
            loaded_samples = []
            with open(samples, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        try:
                            loaded_samples.append(BaziSample.model_validate_json(line))
                        except AttributeError:
                            loaded_samples.append(BaziSample.parse_raw(line))
            samples_to_eval = loaded_samples
        else:
            samples_to_eval = samples
            
        results = []
        output_path = os.path.join(self.output_dir, f"{self.model.model_name}_results.jsonl")
        
        # Resume logic: Read existing results
        completed_ids = set()
        if os.path.exists(output_path):
            print(f"Found existing results at {output_path}, checking for resume...")
            try:
                with open(output_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            try:
                                data = json.loads(line)
                                if "sample_id" in data:
                                    completed_ids.add(data["sample_id"])
                                    results.append(data)
                            except json.JSONDecodeError:
                                continue
            except Exception as e:
                print(f"Error reading existing results: {e}")
        
        # Filter samples
        samples_to_process = [s for s in samples_to_eval if s.id not in completed_ids]
        print(f"Total samples: {len(samples_to_eval)}, Completed: {len(completed_ids)}, Remaining: {len(samples_to_process)}")
        
        if not samples_to_process:
            print("All samples already evaluated.")
            return results
        
        # Define processing function
        def process_sample(sample):
            # Construct prompt
            prompt = sample.instruction
            
            # Generate response
            try:
                response = self.model.generate(prompt)
            except Exception as e:
                response = f"Error: {str(e)}"
            
            # Create result object
            result = {
                "sample_id": sample.id,
                "input": sample.input.model_dump() if hasattr(sample.input, 'model_dump') else sample.input.dict(),
                "instruction": sample.instruction,
                "expected_output": sample.expected_output,
                "model_output": response,
                "difficulty": sample.difficulty,
                "tags": sample.tags
            }
            
            # Thread-safe write
            with self._lock:
                with open(output_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(result, ensure_ascii=False) + "\n")
            
            return result

        # Run with ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            futures = [executor.submit(process_sample, sample) for sample in samples_to_process]
            
            for future in tqdm(as_completed(futures), total=len(samples_to_process), desc=f"Evaluating {self.model.model_name}"):
                try:
                    res = future.result()
                    results.append(res)
                except Exception as e:
                    print(f"Task failed: {e}")
            
        return results

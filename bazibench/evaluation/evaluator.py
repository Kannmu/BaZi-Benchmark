import json
import os
from typing import List, Dict, Any, Optional, Union
from tqdm import tqdm
from ..models.base import ModelBase
from ..dataset.schema import BaziSample

class Evaluator:
    def __init__(self, model: ModelBase, output_dir: str):
        self.model = model
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def evaluate(self, samples: Union[List[BaziSample], str], batch_size: int = 1) -> List[Dict]:
        """
        Evaluate the model on a list of samples or a file path to samples.
        Supports resume functionality.
        
        Args:
            samples: List of BaziSample objects or path to jsonl file
            batch_size: Batch size for evaluation (currently only 1 is supported)
            
        Returns:
            List of evaluation results
        """
        if isinstance(samples, str):
            # Load samples from file
            loaded_samples = []
            with open(samples, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        # Pydantic v2 uses model_validate_json, v1 uses parse_raw
                        # Trying compatible way
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
        
        for sample in tqdm(samples_to_process, desc=f"Evaluating {self.model.model_name}"):
            # Construct prompt
            prompt = sample.instruction
            
            # Generate response
            # Note: Retry logic should be handled inside model.generate or here
            # Ideally inside model to handle specific API errors
            try:
                response = self.model.generate(prompt)
            except Exception as e:
                response = f"Error: {str(e)}"
            
            # Create result object
            # Convert pydantic models to dict
            result = {
                "sample_id": sample.id,
                "input": sample.input.model_dump() if hasattr(sample.input, 'model_dump') else sample.input.dict(),
                "instruction": sample.instruction,
                "expected_output": sample.expected_output,
                "model_output": response,
                "difficulty": sample.difficulty,
                "tags": sample.tags
            }
            results.append(result)
            
            # Save intermediate results (append mode)
            with open(output_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(result, ensure_ascii=False) + "\n")
            
        return results

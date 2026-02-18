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
        
        # Clear existing file if we are starting a new evaluation
        # Or should we append? Let's clear for now to avoid duplicates if run multiple times.
        if os.path.exists(output_path):
             # Maybe backup? Or just overwrite.
             # Let's overwrite for this run.
             open(output_path, "w").close()
        
        for sample in tqdm(samples_to_eval, desc=f"Evaluating {self.model.model_name}"):
            # Construct prompt
            prompt = sample.instruction
            
            # Generate response
            response = self.model.generate(prompt)
            
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

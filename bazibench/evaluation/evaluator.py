import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional, Union
from tqdm import tqdm
from ..models.base import ModelBase
from ..dataset.schema import BaziSample
from ..scoring import ExactMatchScorer, PartialMatchScorer, LLMJudgeScorer

# Try to import numpy, if not available, use simple python implementation
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

class Evaluator:
    def __init__(self, model: ModelBase, output_dir: str, judge_model: Optional[ModelBase] = None):
        self.model = model
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self._lock = threading.Lock()
        
        self.scorers = {
            'exact_match': ExactMatchScorer(),
            'partial_match': PartialMatchScorer(),
        }
        
        if judge_model:
            self.scorers['llm_judge'] = LLMJudgeScorer(judge_model)
        
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
        safe_model_name = self.model.model_name.replace("/", "_")
        output_path = os.path.join(self.output_dir, f"{safe_model_name}_results.jsonl")
        
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
            # Still calculate metrics for all results
            metrics = self._calculate_metrics(results)
            self._save_metrics(metrics)
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
            
            # Determine scorer
            eval_type = getattr(sample, 'evaluation_type', 'exact_match')
            
            # Heuristic for old data or missing evaluation_type
            if not eval_type or eval_type not in self.scorers:
                if "comprehensive" in sample.tags and "llm_judge" in self.scorers:
                     eval_type = 'llm_judge'
                elif any(tag in sample.tags for tag in ["ten_gods", "interactions", "wuxing", "strength"]):
                     eval_type = 'partial_match'
                else:
                     eval_type = 'exact_match'
            
            scorer = self.scorers.get(eval_type, self.scorers['exact_match'])
            
            try:
                score = scorer.score(sample.expected_output, response)
            except Exception as e:
                print(f"Scoring failed for sample {sample.id}: {e}")
                score = 0.0

            # Create result object
            result = {
                "sample_id": sample.id,
                "input": sample.input.model_dump() if hasattr(sample.input, 'model_dump') else sample.input.dict(),
                "instruction": sample.instruction,
                "expected_output": sample.expected_output,
                "model_output": response,
                "score": score,
                "evaluation_type": eval_type,
                "difficulty": sample.difficulty,
                "tags": sample.tags
            }
            
            # Thread-safe write
            with self._lock:
                with open(output_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(result, ensure_ascii=False) + "\n")
            
            return result

        # Run with ThreadPoolExecutor
        executor = ThreadPoolExecutor(max_workers=batch_size)
        futures = []
        try:
            futures = [executor.submit(process_sample, sample) for sample in samples_to_process]
            
            for future in tqdm(as_completed(futures), total=len(samples_to_process), desc=f"Evaluating {self.model.model_name}"):
                try:
                    res = future.result()
                    results.append(res)
                except Exception as e:
                    print(f"Task failed: {e}")
        except KeyboardInterrupt:
            print(f"\nEvaluating {self.model.model_name} interrupted. Cancelling pending tasks...")
            # Cancel all pending futures
            for f in futures:
                f.cancel()
            # Shutdown without waiting
            executor.shutdown(wait=False)
            raise
        finally:
            # Ensure executor is properly cleaned up
            # Since we cancelled pending tasks, this will only wait for currently running threads
            executor.shutdown(wait=True)
            
        # Calculate and save metrics
        metrics = self._calculate_metrics(results)
        self._save_metrics(metrics)
            
        return results

    def _save_metrics(self, metrics: Dict):
        safe_model_name = self.model.model_name.replace("/", "_")
        metrics_path = os.path.join(self.output_dir, f"{safe_model_name}_metrics.json")
        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)

    def _calculate_metrics(self, results: List[Dict]) -> Dict:
        """Calculate statistics metrics"""
        if not results:
            return {}
            
        scores = [r.get("score", 0.0) for r in results]
        total_samples = len(results)
        
        if HAS_NUMPY:
            mean_score = float(np.mean(scores))
            std_score = float(np.std(scores))
        else:
            mean_score = sum(scores) / total_samples if total_samples > 0 else 0.0
            # Simple std calculation
            variance = sum((x - mean_score) ** 2 for x in scores) / total_samples if total_samples > 0 else 0.0
            std_score = variance ** 0.5
            
        metrics = {
            "overall": {
                "accuracy": mean_score,
                "std": std_score,
                "total_samples": total_samples
            },
            "by_difficulty": {},
            "by_tag": {}
        }
        
        # Metrics by difficulty
        difficulties = set(r.get("difficulty", 0) for r in results)
        for diff in sorted(list(difficulties)):
            diff_results = [r for r in results if r.get("difficulty") == diff]
            diff_scores = [r.get("score", 0.0) for r in diff_results]
            
            if HAS_NUMPY:
                diff_mean = float(np.mean(diff_scores))
            else:
                diff_mean = sum(diff_scores) / len(diff_scores) if diff_scores else 0.0
                
            metrics["by_difficulty"][str(diff)] = {
                "accuracy": diff_mean,
                "count": len(diff_results)
            }
            
        # Metrics by tag
        all_tags = set()
        for r in results:
            if r.get("tags"):
                for tag in r.get("tags"):
                    all_tags.add(tag)
            
        for tag in sorted(list(all_tags)):
            tag_results = [r for r in results if tag in r.get("tags", [])]
            tag_scores = [r.get("score", 0.0) for r in tag_results]
            
            if HAS_NUMPY:
                tag_mean = float(np.mean(tag_scores))
            else:
                tag_mean = sum(tag_scores) / len(tag_scores) if tag_scores else 0.0
                
            metrics["by_tag"][tag] = {
                "accuracy": tag_mean,
                "count": len(tag_results)
            }
            
        return metrics

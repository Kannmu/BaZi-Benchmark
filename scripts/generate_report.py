
import os
import json
import glob
from collections import defaultdict
from typing import Dict, List, Any
import datetime
import argparse

def load_results(results_dir: str) -> Dict[str, List[Dict]]:
    """Load all results from jsonl files."""
    results = {}
    if not os.path.exists(results_dir):
        print(f"Results directory {results_dir} does not exist.")
        return {}
        
    files = glob.glob(os.path.join(results_dir, "*_results.jsonl"))
    print(f"Found {len(files)} result files in {results_dir}")
    
    for f in files:
        model_name = os.path.basename(f).replace("_results.jsonl", "")
        data = []
        with open(f, "r", encoding="utf-8") as file:
            for line in file:
                if not line.strip(): continue
                try:
                    data.append(json.loads(line))
                except:
                    continue
        results[model_name] = data
    return results

def calculate_metrics(results: List[Dict]) -> Dict[str, Dict[str, float]]:
    """Calculate metrics by task type."""
    metrics = defaultdict(lambda: {"total": 0, "correct": 0, "score_sum": 0.0})
    
    for r in results:
        task_type = "unknown"
        if "tags" in r and r["tags"]:
            task_type = r["tags"][0]
        
        score = r.get("score", 0.0)
        metrics[task_type]["total"] += 1
        metrics[task_type]["score_sum"] += score
        if score >= 0.99: # Treat almost 1.0 as correct
            metrics[task_type]["correct"] += 1
            
        # Overall
        metrics["overall"]["total"] += 1
        metrics["overall"]["score_sum"] += score
        if score >= 0.99:
            metrics["overall"]["correct"] += 1
            
    final_metrics = {}
    for task, data in metrics.items():
        if data["total"] > 0:
            final_metrics[task] = {
                "accuracy": data["correct"] / data["total"],
                "avg_score": data["score_sum"] / data["total"],
                "count": data["total"]
            }
    return final_metrics

def generate_markdown_report(all_metrics: Dict[str, Dict]):
    """Generate a markdown report."""
    report = f"# BaZiBench Evaluation Report\n\n"
    report += f"**Generated at:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    # Leaderboard
    report += "## 🏆 Leaderboard\n\n"
    report += "Models ranked by Overall Average Score.\n\n"
    report += "| Rank | Model | Overall Score | Accuracy | Samples |\n"
    report += "|------|-------|---------------|----------|---------|\n"
    
    sorted_models = sorted(all_metrics.items(), key=lambda x: x[1].get("overall", {}).get("avg_score", 0), reverse=True)
    
    for i, (model, metrics) in enumerate(sorted_models):
        overall = metrics.get("overall", {"avg_score": 0, "accuracy": 0, "count": 0})
        rank = i + 1
        if i == 0: rank = "🥇"
        elif i == 1: rank = "🥈"
        elif i == 2: rank = "🥉"
        
        report += f"| {rank} | **{model}** | {overall['avg_score']:.4f} | {overall['accuracy']:.2%} | {overall['count']} |\n"
        
    report += "\n## 📊 Detailed Task Analysis\n\n"
    
    # Task breakdown
    all_tasks = set()
    for m in all_metrics.values():
        all_tasks.update(m.keys())
    if "overall" in all_tasks: all_tasks.remove("overall")
    sorted_tasks = sorted(list(all_tasks))
    
    for task in sorted_tasks:
        report += f"### {task.replace('_', ' ').title()}\n\n"
        report += "| Model | Score | Accuracy | Count |\n"
        report += "|-------|-------|----------|-------|\n"
        
        # Sort models by this task score
        task_sorted_models = sorted(all_metrics.items(), key=lambda x: x[1].get(task, {}).get("avg_score", 0), reverse=True)
        
        for model, metrics in task_sorted_models:
            if task in metrics:
                m = metrics[task]
                report += f"| {model} | {m['avg_score']:.4f} | {m['accuracy']:.2%} | {m['count']} |\n"
        report += "\n"
        
    return report

def main():
    parser = argparse.ArgumentParser(description="Generate Evaluation Report")
    parser.add_argument("--results-dir", type=str, default="data/results", help="Directory containing result jsonl files")
    parser.add_argument("--output", type=str, default="REPORT.md", help="Output markdown file")
    
    args = parser.parse_args()
    
    print(f"Loading results from {args.results_dir}...")
    results = load_results(args.results_dir)
    
    if not results:
        print("No results found.")
        return
        
    all_metrics = {}
    for model, res in results.items():
        print(f"Processing {model} ({len(res)} samples)...")
        all_metrics[model] = calculate_metrics(res)
        
    report = generate_markdown_report(all_metrics)
    
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(report)
        
    print(f"Report generated at: {args.output}")

if __name__ == "__main__":
    main()

# BaZiBench

A comprehensive benchmark for evaluating Large Language Models on BaZi (Chinese Four Pillars) analysis tasks.

## Overview

BaZiBench is a specialized benchmark designed to evaluate the complex reasoning capabilities of Large Language Models through the lens of traditional Chinese BaZi (八字) analysis. BaZi, also known as the Four Pillars of Destiny, is a sophisticated system of Chinese astrology that requires multi-step logical reasoning, pattern recognition, and comprehensive analytical skills.

### Why BaZiBench?

- **Complex Reasoning Challenge**: BaZi analysis involves multi-dimensional reasoning including Five Elements (五行) interactions, Ten Gods (十神) relationships, and intricate symbolic calculations.
- **Anti-Gaming Design**: Due to the niche nature of BaZi analysis, model developers are unlikely to specifically fine-tune models for this task.
- **Cultural Heritage Preservation**: Explores how well modern AI systems can understand and reason about traditional Chinese cultural knowledge systems.

## Update Highlights (Optimization)

- **Static Gold Standard Dataset**: Reproducible benchmark located in `bazibench/dataset/static/`.
- **Enhanced Task Coverage**: Added `Pattern Recognition` (格局) and improved `Useful God` (用神) logic.
- **Robust Evaluation**: New `ResultExtractor` handles markdown and loose JSON formats.
- **Reporting**: Automated Markdown report generation with `scripts/generate_report.py`.

## Project Structure

```
BaZiBench/
├── bazibench/                 # Main package
│   ├── core/                  # Core calculation modules
│   │   ├── calculator.py      # BaZi chart calculation
│   │   ├── constants.py       # Tiangan/Dizhi constants
│   │   ├── wuxing.py          # Five Elements analysis
│   │   ├── ten_gods.py        # Ten Gods analysis
│   │   ├── strength.py        # Day Master strength evaluation
│   │   ├── interactions.py    # Earthly Branches interactions
│   │   ├── pattern.py         # Pattern recognition (New)
│   ├── dataset/               # Dataset management
│   │   ├── static/            # Static Gold Standard datasets
│   │   ├── generator.py       # Data generation logic
│   │   ├── schema.py          # Data models (Pydantic)
│   ├── evaluation/            # Evaluation logic
│   │   ├── evaluator.py       # Main evaluator
│   │   ├── extractors.py      # Result extraction (New)
│   ├── scoring/               # Scoring mechanisms
│   │   ├── exact_match.py     # Exact match scorer
│   │   ├── partial_match.py   # Partial match scorer
│   │   ├── llm_judge.py       # LLM-based judge
│   ├── reporting/             # Reporting tools
├── scripts/                   # Utility scripts
│   ├── generate_gold_standard.py # Generate static dataset
│   ├── generate_report.py     # Generate evaluation report
│   ├── run_benchmark.py       # Main entry point
├── data/                      # Data storage
│   ├── configs/               # Configuration files
│   ├── samples/               # Dynamic samples
│   └── results/               # Evaluation results
```

## Quick Start

### 1. Installation

```bash
git clone https://github.com/Kannmu/BaZi-Benchmark.git
cd BaZiBench
conda create -n BaZiBench python==3.12
conda activate BaZiBench
pip install -r requirements.txt
```

### 2. Generate/Use Gold Standard Dataset

The static dataset is pre-generated in `bazibench/dataset/static/`. You can regenerate it using:
```bash
python scripts/generate_gold_standard.py --output bazibench/dataset/static --samples 50
```

### 3. Run Benchmark

```bash
# Evaluate on specific task from static set
python scripts/run_benchmark.py --model xiaomi/mimo-v2-flash-free --input bazibench/dataset/static/chart.jsonl

# Or run on dynamic samples
python scripts/run_benchmark.py --model xiaomi/mimo-v2-flash-free --samples 20
```

### 4. Generate Report

```bash
python scripts/generate_report.py --results-dir data/results --output REPORT.md
```

## Task Types

| Task Type | Description | Difficulty |
|-----------|-------------|------------|
| `chart` | Calculate Four Pillars (年月日时) from birth datetime | ★★☆☆☆ |
| `wuxing` | Analyze Five Elements distribution and relationships | ★★☆☆☆ |
| `ten_gods` | Determine Ten Gods (十神) relationships | ★★★☆☆ |
| `strength` | Evaluate Day Master (日主) strength | ★★★☆☆ |
| `interactions` | Analyze Xing-Chong-He-Hai (刑冲合害) interactions | ★★★★☆ |
| `pattern` | Identify BaZi Patterns (格局) | ★★★★★ |
| `da_yun` | Calculate Da Yun (大运) periods | ★★★☆☆ |
| `useful_god` | Determine Useful God (用神) | ★★★★☆ |
| `comprehensive` | Complete BaZi analysis | ★★★★★ |

## Configuration

### Dataset Configuration (`data/configs/dataset.yaml`)

```yaml
generation:
  total_samples: 1000
  batch_size: 50
  base_seed: 2024
  num_workers: 6

task_types:
  - chart
  - wuxing
  - ten_gods
  - strength
  - interactions
  - pattern
  - da_yun
  - useful_god
  - comprehensive

date_range:
  start_year: 1950
  end_year: 2030

location:
  longitude: 120.0
  latitude: 30.0
  utc_offset: 8.0
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [lunar_python](https://github.com/6tail/lunar-python) for BaZi calculation algorithms
- The traditional Chinese metaphysics community for preserving this knowledge

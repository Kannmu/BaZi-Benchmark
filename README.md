# BaZiBench

A comprehensive benchmark for evaluating Large Language Models on BaZi (Chinese Four Pillars) analysis tasks.

## Overview

BaZiBench is a specialized benchmark designed to evaluate the complex reasoning capabilities of Large Language Models through the lens of traditional Chinese BaZi (八字) analysis. BaZi, also known as the Four Pillars of Destiny, is a sophisticated system of Chinese astrology that requires multi-step logical reasoning, pattern recognition, and comprehensive analytical skills.

### Why BaZiBench?

- **Complex Reasoning Challenge**: BaZi analysis involves multi-dimensional reasoning including Five Elements (五行) interactions, Ten Gods (十神) relationships, and intricate symbolic calculations, making it an ideal testbed for evaluating LLM reasoning capabilities.

- **Anti-Gaming Design**: Due to the niche nature of BaZi analysis, model developers are unlikely to specifically fine-tune models for this task, ensuring the evaluation results reflect genuine reasoning abilities rather than memorization or task-specific optimization.

- **Cultural Heritage Preservation**: This benchmark also serves to explore how well modern AI systems can understand and reason about traditional Chinese cultural knowledge systems.

## Features

- **Multiple Task Types**: Supports 8 different analysis tasks including chart calculation, Five Elements analysis, Ten Gods analysis, strength evaluation, interactions analysis, Da Yun (大运) calculation, Useful God (用神) determination, and comprehensive analysis.

- **Flexible Model Support**: Compatible with OpenAI, Anthropic, and any OpenAI-compatible API endpoints.

- **Multiple Scoring Methods**: Includes exact match, partial match, and LLM-based evaluation scoring mechanisms.

- **Resume & Concurrency**: Supports evaluation resumption and concurrent processing for efficiency.

- **Comprehensive Validation**: Built-in data validation ensures benchmark quality and consistency.

## Installation

### Prerequisites

- Python 3.10+
- Miniconda (recommended)

### Setup

```bash
# Clone the repository
git clone https://github.com/Kannmu/BaZi-Benchmark.git
cd BaZiBench

# Create conda environment
conda create -n BaZiBench python==3.12
conda activate BaZiBench

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```env
ZENMUX_API_KEY=your_api_key_here
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

## Quick Start

### 1. Generate Benchmark Dataset

```bash
python scripts/generate_data.py
```

This will generate a benchmark dataset based on the configuration in `data/configs/dataset.yaml`.

### 2. Run Evaluation

```bash
# Basic usage
python scripts/run_benchmark.py --model xiaomi/mimo-v2-flash-free

# With sample limit for testing
python scripts/run_benchmark.py --model xiaomi/mimo-v2-flash-free --samples 30

# With concurrent processing
python scripts/run_benchmark.py --model xiaomi/mimo-v2-flash-free --batch-size 4
```

### 3. View Results

Results are saved in `data/results/`:
- `{model_name}_results.jsonl`: Detailed results for each sample
- `{model_name}_metrics.json`: Aggregated metrics and statistics

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
│   │   └── interactions.py    # Xing-Chong-He-Hai analysis
│   ├── dataset/               # Dataset generation and validation
│   │   ├── generator.py       # Sample generation
│   │   ├── schema.py          # Data models
│   │   └── validator.py       # Data validation
│   ├── evaluation/            # Evaluation framework
│   │   └── evaluator.py       # Main evaluator
│   ├── models/                # Model interfaces
│   │   ├── base.py            # Abstract base class
│   │   ├── openai_model.py    # OpenAI integration
│   │   ├── anthropic_model.py # Anthropic integration
│   │   └── registry.py        # Model registry
│   ├── scoring/               # Scoring mechanisms
│   │   ├── base.py            # Scorer base class
│   │   ├── exact_match.py     # Exact match scoring
│   │   ├── partial_match.py   # Partial match scoring
│   │   └── llm_judge.py       # LLM-based evaluation
│   └── utils/
│       └── logger.py          # Logging utilities
├── data/
│   ├── configs/               # Configuration files
│   │   ├── dataset.yaml       # Dataset generation config
│   │   └── models.yaml        # Model configuration
│   ├── samples/               # Generated benchmark samples
│   └── results/               # Evaluation results
├── scripts/                   # Executable scripts
│   ├── generate_data.py       # Dataset generation script
│   ├── run_benchmark.py       # Main evaluation script
│   └── extract_samples.py     # Sample extraction utility
└── tests/                     # Test suite
```

## Task Types

| Task Type | Description | Difficulty |
|-----------|-------------|------------|
| `chart` | Calculate Four Pillars (年月日时) from birth datetime | ★★☆☆☆ |
| `wuxing` | Analyze Five Elements distribution and relationships | ★★☆☆☆ |
| `ten_gods` | Determine Ten Gods (十神) relationships | ★★★☆☆ |
| `strength` | Evaluate Day Master (日主) strength | ★★★☆☆ |
| `interactions` | Analyze Xing-Chong-He-Hai (刑冲合害) interactions | ★★★★☆ |
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

### Model Configuration (`data/configs/models.yaml`)

```yaml
providers:
  zenmux:
    type: openai_compatible
    base_url: "https://zenmux.ai/api/v1"
    api_key_env: "ZENMUX_API_KEY"

models:
  - name: "xiaomi/mimo-v2-flash-free"
    provider: "zenmux"
  
  - name: "qwen/qwen3.5-plus"
    provider: "zenmux"
```

## API Usage

```python
from bazibench import BaZiCalculator, BaziDatasetGenerator, Evaluator, ModelRegistry

# Calculate BaZi chart
calculator = BaZiCalculator()
from datetime import datetime
chart = calculator.calculate(datetime(1990, 5, 15, 10, 30))
print(chart)

# Generate samples
generator = BaziDatasetGenerator(seed=42)
sample = generator.generate_sample("wuxing")

# Run evaluation
registry = ModelRegistry("data/configs/models.yaml")
model = registry.get_model("xiaomi/mimo-v2-flash-free")
evaluator = Evaluator(model=model, output_dir="data/results")
results = evaluator.evaluate(samples)
```

## Scoring Methods

### Exact Match
For tasks with deterministic answers (e.g., chart calculation), exact string matching is used.

### Partial Match
For tasks with multiple valid components (e.g., Five Elements analysis), partial credit is awarded based on correct elements identified.

### LLM Judge
For subjective tasks (e.g., comprehensive analysis), an LLM-based evaluator assesses response quality.

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_calculator.py

# Run with coverage
pytest tests/ --cov=bazibench
```

### Adding New Models

1. Create a new model class inheriting from `ModelBase`
2. Implement the `generate()` method
3. Register the model in `models.yaml`

```python
from bazibench.models.base import ModelBase

class MyCustomModel(ModelBase):
    def generate(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        # Your implementation
        return response
```

<!-- ## Citation

If you use BaZiBench in your research, please cite:

```bibtex
@misc{bazibench2024,
  title={BaZiBench: A Benchmark for Evaluating LLMs on Chinese BaZi Analysis},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/BaZiBench}
}
``` -->

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [lunar_python](https://github.com/6tail/lunar-python) for BaZi calculation algorithms
- The traditional Chinese metaphysics community for preserving this knowledge

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

#!/bin/bash

# Trap SIGINT and SIGTERM to exit immediately
trap "echo 'Script interrupted by user'; exit 1" INT TERM

# Source environment variables for API keys
if [ -f ~/.zshrc ]; then
    source ~/.zshrc
fi

# Define python executable path
PYTHON_EXEC="/Users/kannmu/miniconda3/envs/BaZiBench/bin/python"

# Models list
models=(
    # "xiaomi/mimo-v2-flash-free"
    # "qwen/qwen3.5-plus"
    "minimax/minimax-m2.5"
    # "moonshotai/kimi-k2.5"
    # "z-ai/glm-5"
)

# Run benchmark for each model
for model in "${models[@]}"; do
    echo "========================================"
    echo "Starting benchmark for model: $model"
    echo "========================================"
    
    $PYTHON_EXEC scripts/run_benchmark.py --model "$model" --input data/dataset/full_benchmark.jsonl --batch-size 5
    
    if [ $? -eq 0 ]; then
        echo "Successfully finished benchmark for model: $model"
    else
        echo "Failed benchmark for model: $model"
    fi
    echo ""
done

echo "========================================"
echo "Generating final report..."
echo "========================================"
$PYTHON_EXEC scripts/generate_report.py


#!/bin/bash

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
    "moonshotai/kimi-k2.5"
    "z-ai/glm-5"
)

# Run benchmark for each model
for model in "${models[@]}"; do
    echo "========================================"
    echo "Starting benchmark for model: $model"
    echo "========================================"
    
    $PYTHON_EXEC scripts/run_benchmark.py --model "$model"
    
    if [ $? -eq 0 ]; then
        echo "Successfully finished benchmark for model: $model"
    else
        echo "Failed benchmark for model: $model"
    fi
    echo ""
done

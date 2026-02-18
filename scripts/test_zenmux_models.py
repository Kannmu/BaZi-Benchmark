import os
import sys
import yaml
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from bazibench.models import ModelRegistry

def main():
    # Load configuration
    config_path = project_root / "data" / "configs" / "models.yaml"
    registry = ModelRegistry(str(config_path))
    
    # Load models
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        
    models_to_test = [m["name"] for m in config.get("models", [])]
    
    print(f"Testing {len(models_to_test)} models from ZenMux...")
    
    for model_name in models_to_test:
        print(f"\n--- Testing Model: {model_name} ---")
        try:
            # Create model instance
            # The registry handles API key and Base URL resolution from config
            model = registry.get_model(model_name)
            
            # Generate response
            response = model.generate("Hello, please introduce yourself briefly.")
            
            print(f"Response:\n{response}")
            
        except Exception as e:
            print(f"Error testing {model_name}: {e}")

if __name__ == "__main__":
    main()

import os
import yaml
from typing import Dict, Any, Optional
from .base import ModelBase
from .openai_model import OpenAIModel
from .anthropic_model import AnthropicModel

class ModelRegistry:
    """
    Registry for managing and loading models from configuration.
    """
    
    def __init__(self, config_path: str = "data/configs/models.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not os.path.exists(self.config_path):
            return {"providers": {}, "models": []}
            
        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
            
    def get_model(self, model_name: str, **kwargs) -> ModelBase:
        """
        Get a model instance by name.
        
        Args:
            model_name: Name of the model (as defined in config or provider/model format)
            **kwargs: Additional arguments to pass to model constructor
            
        Returns:
            Instance of ModelBase
        """
        # Find model definition in config
        model_config = next((m for m in self.config.get("models", []) if m["name"] == model_name), None)
        
        if model_config:
            provider_name = model_config.get("provider")
            provider_config = self.config.get("providers", {}).get(provider_name, {})
            
            # Prepare configuration for model constructor
            # 1. Start with model config
            final_kwargs = model_config.copy()
            final_kwargs.pop("name", None)
            final_kwargs.pop("provider", None)
            
            # 2. Update with passed kwargs (highest priority)
            final_kwargs.update(kwargs)
            
            # Determine model type
            provider_type = provider_config.get("type", "openai")
            
            # Extract specific args
            api_key = final_kwargs.pop("api_key", None)
            base_url = final_kwargs.pop("base_url", None)
            
            # Resolve API Key from env if not provided
            if not api_key:
                api_key_env = provider_config.get("api_key_env")
                if api_key_env:
                    api_key = os.environ.get(api_key_env)
            
            # Resolve Base URL if not provided
            if not base_url:
                base_url = provider_config.get("base_url")
                
            if provider_type == "openai_compatible" or provider_type == "openai":
                return OpenAIModel(
                    model_name=model_name,
                    api_key=api_key,
                    base_url=base_url,
                    **final_kwargs
                )
            elif provider_type == "anthropic":
                return AnthropicModel(
                    model_name=model_name,
                    api_key=api_key,
                    **final_kwargs
                )
            else:
                raise ValueError(f"Unsupported provider type: {provider_type}")
                
        else:
            # If not in config, try to infer from name or use default OpenAI
            # For now, let's assume if it contains '/', it might be custom, otherwise default
            # But safe fallback is to try OpenAI default
            return OpenAIModel(model_name=model_name, **kwargs)

    def list_models(self):
        """List all configured models."""
        return [m["name"] for m in self.config.get("models", [])]

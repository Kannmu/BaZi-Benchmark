from typing import Optional, Dict, Any
import os
from .base import ModelBase

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

class AnthropicModel(ModelBase):
    """
    Anthropic model implementation.
    """
    
    def __init__(self, model_name: str, api_key: Optional[str] = None, **kwargs):
        super().__init__(model_name, **kwargs)
        if Anthropic is None:
            raise ImportError("Anthropic package is not installed. Please install it via 'pip install anthropic'.")

        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        
        client_args = {}
        if self.api_key:
            client_args["api_key"] = self.api_key
            
        self.client = Anthropic(**client_args)

    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        # Merge default config with run-time kwargs
        generation_params = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.config.get("temperature", 0.7),
            "max_tokens": self.config.get("max_tokens", 1024),
        }
        
        if system_prompt:
            generation_params["system"] = system_prompt
            
        # Update with kwargs passed to generate
        generation_params.update(kwargs)
            
        try:
            response = self.client.messages.create(**generation_params)
            return response.content[0].text
        except Exception as e:
            return f"Error: {str(e)}"

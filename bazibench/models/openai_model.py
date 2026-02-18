from typing import Optional, Dict, Any
import os
from .base import ModelBase

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class OpenAIModel(ModelBase):
    """
    OpenAI model implementation.
    Supports OpenAI API and compatible APIs (e.g. DeepSeek, Qwen).
    """
    
    def __init__(self, model_name: str, api_key: Optional[str] = None, base_url: Optional[str] = None, **kwargs):
        """
        Initialize OpenAI model.
        
        Args:
            model_name: The name of the model to use.
            api_key: OpenAI API key. If not provided, will look for OPENAI_API_KEY env var.
            base_url: OpenAI Base URL. If not provided, will look for OPENAI_BASE_URL env var.
            **kwargs: Configuration for the model (temperature, etc.) and client.
        """
        super().__init__(model_name, **kwargs)
        if OpenAI is None:
            raise ImportError("OpenAI package is not installed. Please install it via 'pip install openai'.")
            
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.base_url = base_url or os.environ.get("OPENAI_BASE_URL")
        
        # Separate client args from generation config
        client_args = {}
        if self.api_key:
            client_args["api_key"] = self.api_key
        if self.base_url:
            client_args["base_url"] = self.base_url
            
        # Initialize client
        self.client = OpenAI(**client_args)

    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        # Merge default config with run-time kwargs
        # self.config contains kwargs passed to __init__
        generation_params = {
            "model": self.model_name,
            "messages": messages,
            "temperature": self.config.get("temperature", 0.7),
        }
        
        # Update with kwargs passed to generate
        generation_params.update(kwargs)
        
        try:
            response = self.client.chat.completions.create(**generation_params)
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"

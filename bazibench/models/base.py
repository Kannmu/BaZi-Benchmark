from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class ModelBase(ABC):
    """
    Abstract base class for all models in BaZiBench.
    """
    
    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name
        self.config = kwargs

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """
        Generate a response from the model.
        
        Args:
            prompt: The user prompt.
            system_prompt: Optional system prompt.
            **kwargs: Additional generation parameters (temperature, max_tokens, etc.)
            
        Returns:
            The generated text response.
        """
        pass
    
    def get_token_count(self, text: str) -> int:
        """
        Estimate the token count for a given text.
        Default implementation returns length / 4.
        """
        return len(text) // 4

from typing import Optional, Dict, Any
import os
import logging
from .base import ModelBase
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception, before_sleep_log

try:
    from openai import OpenAI
    import openai
except ImportError:
    OpenAI = None
    openai = None

# Setup logger
logger = logging.getLogger("bazibench.models.openai")

def _should_retry_exception(exception: BaseException) -> bool:
    """
    Determine if an exception should be retried.
    """
    if openai is None:
        return True # Should not happen if class is initialized
        
    # If it's an OpenAI API error
    if isinstance(exception, openai.APIError):
        # Do NOT retry these errors
        if isinstance(exception, (
            openai.AuthenticationError,
            openai.BadRequestError,
            openai.NotFoundError,
            openai.PermissionDeniedError,
            openai.UnprocessableEntityError
        )):
            return False
        # Retry others (RateLimit, Timeout, InternalServer, Connection)
        return True
        
    # Retry standard network errors if they occur outside openai package
    return True

class OpenAIModel(ModelBase):
    """
    OpenAI model implementation.
    Supports OpenAI API and compatible APIs (e.g. DeepSeek, Qwen).
    """
    
    def __init__(self, model_name: str, api_key: Optional[str] = None, base_url: Optional[str] = None, timeout: int = 300, **kwargs):
        """
        Initialize OpenAI model.
        
        Args:
            model_name: The name of the model to use.
            api_key: OpenAI API key. If not provided, will look for OPENAI_API_KEY env var.
            base_url: OpenAI Base URL. If not provided, will look for OPENAI_BASE_URL env var.
            timeout: Request timeout in seconds. Default is 300s (5 mins) for reasoning models.
            **kwargs: Configuration for the model (temperature, etc.) and client.
        """
        super().__init__(model_name, **kwargs)
        if OpenAI is None:
            raise ImportError("OpenAI package is not installed. Please install it via 'pip install openai'.")
            
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.base_url = base_url or os.environ.get("OPENAI_BASE_URL")
        self.timeout = timeout
        
        # Separate client args from generation config
        client_args = {
            "timeout": self.timeout
        }
        if self.api_key:
            client_args["api_key"] = self.api_key
        if self.base_url:
            client_args["base_url"] = self.base_url
            
        # Initialize client
        self.client = OpenAI(**client_args)

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_exception(_should_retry_exception),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
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
        
        # Handle max_tokens and max_completion_tokens
        # Priority: kwargs > config > default
        # If max_completion_tokens is set (for reasoning models), we prefer it over max_tokens
        max_completion_tokens = self.config.get("max_completion_tokens")
        max_tokens = self.config.get("max_tokens", 4096)

        if max_completion_tokens:
            generation_params["max_completion_tokens"] = max_completion_tokens
        else:
            generation_params["max_tokens"] = max_tokens
        
        # Update with kwargs passed to generate
        generation_params.update(kwargs)
        
        try:
            # Direct call, letting tenacity handle exceptions
            response = self.client.chat.completions.create(**generation_params)
            
            # Extract content
            message = response.choices[0].message
            content = message.content

            # Check for truncation
            if hasattr(response.choices[0], "finish_reason") and response.choices[0].finish_reason == "length":
                logger.warning(f"Model {self.model_name} response truncated due to length limit.")

            # Log reasoning if available (for debugging/analysis purposes)
            # OpenAI python client might hide extra fields, check if we can access it
            reasoning = None
            if hasattr(message, "reasoning_content") and message.reasoning_content:
                reasoning = message.reasoning_content
                logger.info(f"Model {self.model_name} provided reasoning_content (length: {len(reasoning)})")
            elif hasattr(message, "reasoning") and message.reasoning:
                reasoning = message.reasoning
                logger.info(f"Model {self.model_name} provided reasoning (length: {len(message.reasoning) if message.reasoning else 0})")
            elif hasattr(message, "model_extra") and message.model_extra and "reasoning" in message.model_extra:
                reasoning = message.model_extra.get("reasoning")
                if reasoning:
                    logger.info(f"Model {self.model_name} provided reasoning (length: {len(reasoning)})")
            elif hasattr(message, "_previous") and "reasoning" in message._previous:
                 # Pydantic v1 fallback for extra fields
                 reasoning = message._previous.get("reasoning")
                 if reasoning:
                     logger.info(f"Model {self.model_name} provided reasoning (length: {len(reasoning)})")
            
            # Fallback for models that put everything in reasoning (like Minimax m2.5 sometimes)
            if not content and reasoning:
                logger.warning(f"Model {self.model_name} returned empty content but has reasoning. Using reasoning as content.")
                content = reasoning
                 
            return content
        except Exception as e:
            logger.error(f"Error generating response from {self.model_name}: {e}")
            raise

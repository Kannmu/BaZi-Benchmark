import pytest
from unittest.mock import MagicMock, patch
import os

# We need to make sure we don't need real API keys for tests
os.environ["OPENAI_API_KEY"] = "sk-dummy"
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-dummy"

from bazibench.models.openai_model import OpenAIModel
from bazibench.models.anthropic_model import AnthropicModel

@patch("bazibench.models.openai_model.OpenAI")
def test_openai_model_init(mock_openai):
    model = OpenAIModel("gpt-4o", api_key="sk-test")
    assert model.model_name == "gpt-4o"
    mock_openai.assert_called_once()

@patch("bazibench.models.anthropic_model.Anthropic")
def test_anthropic_model_init(mock_anthropic):
    model = AnthropicModel("claude-3-opus", api_key="sk-ant-test")
    assert model.model_name == "claude-3-opus"
    mock_anthropic.assert_called_once()
    
@patch("bazibench.models.openai_model.OpenAI")
def test_openai_generate(mock_openai):
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Hello"))]
    mock_client.chat.completions.create.return_value = mock_response
    
    model = OpenAIModel("gpt-4o", api_key="sk-test")
    response = model.generate("Hi")
    
    assert response == "Hello"
    mock_client.chat.completions.create.assert_called_once()
    
@patch("bazibench.models.anthropic_model.Anthropic")
def test_anthropic_generate(mock_anthropic):
    mock_client = MagicMock()
    mock_anthropic.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Hello")]
    mock_client.messages.create.return_value = mock_response
    
    model = AnthropicModel("claude-3-opus", api_key="sk-ant-test")
    response = model.generate("Hi")
    
    assert response == "Hello"
    mock_client.messages.create.assert_called_once()

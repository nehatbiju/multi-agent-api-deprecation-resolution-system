
"""Tests for LLM client"""
from llm_client import get_openai_response

def test_openai_response():
    """Test that OpenAI response works"""
    response = get_openai_response("Hello")
    assert isinstance(response, str)

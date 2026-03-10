"""Chat agent using OpenAI"""
from llm_client import get_openai_response

class ChatAgent:
    def __init__(self):
        self.model = "gemini-2.0-flash-exp-vision"
        self.temperature = 0.7
    
    def chat(self, user_input: str) -> str:
        """Chat with user"""
        return get_openai_response(user_input)
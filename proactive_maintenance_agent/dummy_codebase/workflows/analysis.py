"""Analysis workflow"""
from agents.chat_agent import ChatAgent

class AnalysisWorkflow:
    def __init__(self):
        self.agent = ChatAgent(model="gemini-2.0-flash-exp-vision")
        self.current_model = "gemini-2.0-flash-exp-vision"
    
    def analyze_text(self, text: str) -> str:
        """Analyze text using ChatAgent"""
        return self.agent.chat(f"Analyze: {text}")
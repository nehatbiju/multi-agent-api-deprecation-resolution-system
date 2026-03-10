"""Model configuration schema"""

class ModelConfig:
    """Configuration for LLM models"""
    def __init__(self):
        self.model_id = "gemini-2.0-flash-exp-vision"
        self.provider = "google"
        self.version = "2.0"
        self.deprecated = False
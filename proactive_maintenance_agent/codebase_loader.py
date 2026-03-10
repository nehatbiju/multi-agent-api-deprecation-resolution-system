# codebase_loader.py

"""
Creates a dummy Python codebase with 8 files.
All files contain references to the deprecated API: "gpt-4-turbo-preview"
"""

class CodebaseLoader:
    """Holds all dummy files that use the deprecated API"""
    
    DUMMY_CODEBASE = {
        # FILE 1: Direct reference in main LLM client
        "llm_client.py": '''
"""Main LLM client for OpenAI"""
from openai import OpenAI

def get_openai_response(prompt: str) -> str:
    """Get response from OpenAI using GPT-4 turbo preview"""
    client = OpenAI(api_key="sk-xxx")
    
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=2048
    )
    
    return response.choices[0].message.content
''',

        # FILE 2: Variable reference in agent
        "agents/chat_agent.py": '''
"""Chat agent using OpenAI"""
from llm_client import get_openai_response

class ChatAgent:
    def __init__(self):
        self.model = "gpt-4-turbo-preview"
        self.temperature = 0.7
    
    def chat(self, user_input: str) -> str:
        """Chat with user"""
        return get_openai_response(user_input)
''',

        # FILE 3: Config file reference
        "config/models.json": '''
{
  "primary_model": "gpt-4-turbo-preview",
  "backup_model": "gpt-4",
  "temperature": 0.7
}
''',

        # FILE 4: Constant reference
        "utils/constants.py": '''
"""Constants for the application"""

OPENAI_MODEL = "gpt-4-turbo-preview"
OPENAI_BACKUP = "gpt-4"
DEFAULT_TEMPERATURE = 0.7
''',

        # FILE 5: Indirect reference
        "workflows/analysis.py": '''
"""Analysis workflow"""
from agents.chat_agent import ChatAgent
from utils.constants import OPENAI_MODEL

class AnalysisWorkflow:
    def __init__(self):
        self.agent = ChatAgent()
        self.current_model = OPENAI_MODEL
    
    def analyze_text(self, text: str) -> str:
        """Analyze text using ChatAgent"""
        return self.agent.chat(f"Analyze: {text}")
''',

        # FILE 6: YAML config file
        "config/openai_config.yaml": '''
openai:
  model: "gpt-4-turbo-preview"
  endpoint: "https://api.openai.com/v1"
  timeout: 30
''',

        # FILE 7: Test file
        "tests/test_llm.py": '''
"""Tests for LLM client"""
from llm_client import get_openai_response

def test_openai_response():
    """Test that OpenAI response works"""
    response = get_openai_response("Hello")
    assert isinstance(response, str)
''',

        # FILE 8: Model config
        "schemas/model_config.py": '''
"""Model configuration schema"""

class ModelConfig:
    """Configuration for LLM models"""
    def __init__(self):
        self.model_id = "gpt-4-turbo-preview"
        self.provider = "openai"
        self.version = "preview"
        self.deprecated = True
'''
    }

    @staticmethod
    def create_dummy_codebase(output_dir: str = "./dummy_codebase") -> str:
        """
        Create all 8 dummy files in a directory
        
        Args:
            output_dir: Directory to create files in
        
        Returns:
            Path to created directory
        """
        import os
        
        # Create directories
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(f"{output_dir}/agents", exist_ok=True)
        os.makedirs(f"{output_dir}/config", exist_ok=True)
        os.makedirs(f"{output_dir}/utils", exist_ok=True)
        os.makedirs(f"{output_dir}/workflows", exist_ok=True)
        os.makedirs(f"{output_dir}/tests", exist_ok=True)
        os.makedirs(f"{output_dir}/schemas", exist_ok=True)
        
        # Create all files WITH UTF-8 ENCODING
        for filepath, content in CodebaseLoader.DUMMY_CODEBASE.items():
            full_path = f"{output_dir}/{filepath}"
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"OK Created: {filepath}")
        
        print(f"\nOK Dummy codebase created in: {output_dir}")
        return output_dir

    @staticmethod
    def get_dummy_codebase_dict() -> dict:
        """Get dummy codebase as dictionary (for in-memory use)"""
        return CodebaseLoader.DUMMY_CODEBASE


# Run this file directly to create the dummy codebase
if __name__ == "__main__":
    CodebaseLoader.create_dummy_codebase()
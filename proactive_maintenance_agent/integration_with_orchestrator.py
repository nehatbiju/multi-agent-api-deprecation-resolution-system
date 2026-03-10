# integration_with_orchestrator.py

"""
Integration layer for RAG Agent
Provides interface for Gowtham to use the RAG search
"""

import json
import os
from rag_agent import RAGAgent
from codebase_loader import CodebaseLoader


class RAGIntegration:
    """
    High-level interface for using RAG Agent
    This is what Gowtham will import and use
    """
    
    def __init__(self):
        """Initialize RAG for integration"""
        self.rag_agent = RAGAgent()
        self.codebase_dir = None
        self.is_initialized = False
    
    def initialize(self, codebase_dir: str = "./dummy_codebase") -> None:
        """
        Initialize RAG with codebase
        
        Args:
            codebase_dir: Path to codebase directory
        """
        print("\n" + "=" * 60)
        print("🚀 INITIALIZING RAG FOR GOWTHAM")
        print("=" * 60 + "\n")
        
        # Get dummy codebase
        dummy_codebase = CodebaseLoader.get_dummy_codebase_dict()
        
        # Load into RAG
        self.rag_agent.load_codebase(dummy_codebase)
        
        # Generate embeddings
        self.rag_agent.embed_codebase()
        
        self.codebase_dir = codebase_dir
        self.is_initialized = True
        
        print("✅ RAG initialized and ready for Gowtham\n")
    
    def find_deprecated_code(self, deprecation_info: dict) -> dict:
        """
        Main function Gowtham will call
        
        Args:
            deprecation_info: From Mate 2's deprecation_payload.json
            {
                "deprecation_info": {
                    "old_api_name": "gpt-4-turbo-preview",
                    "new_api_name": "gpt-4.1",
                    "provider": "OpenAI"
                }
            }
        
        Returns:
            affected_files.json structure
            {
                "files_found": 8,
                "affected_files": [...]
            }
        """
        if not self.is_initialized:
            raise RuntimeError("RAG not initialized. Call initialize() first.")
        
        # Run full search pipeline
        results = self.rag_agent.full_search_pipeline(
            deprecation_info['deprecation_info']
        )
        
        return results

    def get_file_content(self, filepath: str) -> str:
        """
        Get content of a specific file (for Gowtham)
        
        Args:
            filepath: Path to file (e.g., "llm_client.py")
        
        Returns:
            File content as string
        """
        if filepath not in self.rag_agent.codebase_files:
            raise FileNotFoundError(f"File not found: {filepath}")
        
        return self.rag_agent.codebase_files[filepath]
    
    def save_results(
        self,
        results: dict,
        output_file: str = "affected_files.json"
    ) -> None:
        """
        Save results to JSON file
        
        Args:
            results: Results from find_deprecated_code()
            output_file: Output filename
        """
        self.rag_agent.save_results(results, output_file)


# Example usage (for testing, Gowtham will use this)
def example_usage():
    """Example of how Gowtham will use RAG"""
    
    print("=" * 60)
    print("EXAMPLE: HOW GOWTHAM WILL USE YOUR RAG AGENT")
    print("=" * 60 + "\n")
    
    # 1. Initialize RAG
    rag = RAGIntegration()
    rag.initialize()
    
    # 2. Load deprecation info from Mate 2
    with open("deprecation_payload.json", 'r') as f:
        deprecation = json.load(f)
    
    # 3. Find affected files
    print("Finding affected files...")
    results = rag.find_deprecated_code(deprecation)
    
    # 4. Use the results
    print(f"\nGowtham sees: {results['files_found']} files to update")
    
    for file_info in results['affected_files']:
        filepath = file_info['filepath']
        confidence = file_info['confidence']
        
        # 5. Get file content for code generation
        content = rag.get_file_content(filepath)
        
        print(f"\nFile: {filepath} (confidence: {confidence})")
        print(f"Content preview: {content[:100]}...")
        
        # Now Gowtham would generate new code for this file
    
    # 6. Save results
    rag.save_results(results)
    
    print("\n" + "=" * 60)
    print("✅ RAG INTEGRATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    example_usage()
# rag_agent.py

"""
RAG (Retrieval Augmented Generation) Agent
Semantic search engine to find deprecated API usage in codebase
"""

import chromadb
from sentence_transformers import SentenceTransformer
import json
from typing import List, Dict, Optional


class RAGAgent:
    """
    Semantic code search engine using ChromaDB + embeddings
    Finds files using deprecated APIs even with indirect references
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize RAG Agent
        
        Args:
            model_name: HuggingFace model for embeddings
                - all-MiniLM-L6-v2: Fast, good for code (recommended)
                - all-mpnet-base-v2: Slower but more accurate
        """
        print("🤖 Initializing RAG Agent...")
        
        # Create ChromaDB client (in-memory)
        self.client = chromadb.Client()
        
        # Create collection for codebase
        self.collection = self.client.get_or_create_collection(
            name="codebase",
            metadata={"hnsw:space": "cosine"}  # Cosine similarity for better results
        )
        
        # Load embedding model
        print(f"📥 Loading embedding model: {model_name}")
        self.embedding_model = SentenceTransformer(model_name)
        
        # Store files for reference
        self.codebase_files = {}
        
        print("✅ RAG Agent initialized\n")
    
    def load_codebase(self, codebase_dict: Dict[str, str]) -> None:
        """
        Load codebase from dictionary
        
        Args:
            codebase_dict: Dict of {filepath: code_content}
        """
        print(f"📂 Loading {len(codebase_dict)} files...")
        
        self.codebase_files = codebase_dict
        
        print(f"✅ Loaded {len(self.codebase_files)} files\n")
    
    def embed_codebase(self) -> None:
        """
        Generate embeddings for all files and store in ChromaDB
        Embeddings = converting code to numbers the search engine understands
        """
        print(f"🔄 Generating embeddings for {len(self.codebase_files)} files...")
        print("   (This takes 30 seconds first time, then fast...)\n")
        
        for filepath, content in self.codebase_files.items():
            # Convert code to embedding (384-dimensional vector)
            embedding = self.embedding_model.encode(content)
            
            # Store in ChromaDB
            self.collection.upsert(
                ids=[filepath],
                embeddings=[embedding.tolist()],
                metadatas={"file": filepath},
                documents=[content]
            )
            
            print(f"   ✅ Embedded: {filepath}")
        
        print(f"\n✅ All files embedded and stored in ChromaDB\n")
    
    def search_deprecated_code(
        self,
        query: str,
        threshold: float = 0.6,
        top_k: int = 10
    ) -> List[Dict]:
        """
        Search for deprecated code using semantic similarity
        
        Args:
            query: What to search for (e.g., "gpt-4-turbo-preview")
            threshold: Minimum confidence score (0-1)
            top_k: Max results to return
        
        Returns:
            List of matching files with confidence scores
        """
        print(f"\n🔍 Searching for: '{query}'")
        print(f"   Threshold: {threshold} | Top-K: {top_k}\n")
        
        # Generate embedding for search query
        query_embedding = self.embedding_model.encode(query)
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k
        )
        
        # Parse results
        matched_files = {}
        
        if results['ids'] and len(results['ids']) > 0:
            for file_id, distance, content in zip(
                results['ids'][0],
                results['distances'][0],
                results['documents'][0]
            ):
                # Convert distance to confidence score (0-1)
                # Distance ranges 0-2, where 0 = perfect match, 2 = no match
                confidence = 1 - (distance / 2)
                
                # Only include if above threshold
                if confidence >= threshold:
                    if file_id not in matched_files:
                        matched_files[file_id] = {
                            "filepath": file_id,
                            "confidence": round(confidence, 3),
                            "file_content": self.codebase_files[file_id]
                        }
                        print(f"   ✅ Found: {file_id} (confidence: {confidence:.1%})")
        
        print(f"\n✅ Found {len(matched_files)} files\n")
        return list(matched_files.values())
    
    def extract_affected_files(
        self,
        search_results: List[Dict]
    ) -> Dict:
        """
        Format search results as JSON output
        
        Args:
            search_results: Results from search_deprecated_code()
        
        Returns:
            Formatted dict ready for Gowtham
        """
        print("📋 Extracting and formatting results...\n")
        
        affected_files = []
        
        for result in search_results:
            affected_files.append({
                "filepath": result["filepath"],
                "confidence": result["confidence"],
                "file_content": result["file_content"]
            })
        
        # Sort by confidence (highest first)
        affected_files.sort(key=lambda x: x["confidence"], reverse=True)
        
        return {
            "files_found": len(affected_files),
            "affected_files": affected_files
        }
    
    def full_search_pipeline(
        self,
        deprecation_info: Dict
    ) -> Dict:
        """
        Complete search process from deprecation info to affected files
        
        Args:
            deprecation_info: From Mate 2's deprecation_payload.json
            {
                "old_api_name": "gpt-4-turbo-preview",
                "provider": "OpenAI",
                ...
            }
        
        Returns:
            Formatted output for Gowtham
        """
        print("=" * 60)
        print("🔄 FULL SEARCH PIPELINE STARTED")
        print("=" * 60 + "\n")
        
        # Extract key info
        old_api_name = deprecation_info.get('old_api_name')
        provider = deprecation_info.get('provider', 'Unknown')
        
        print(f"Provider: {provider}")
        print(f"Deprecated API: {old_api_name}\n")
        
        # Create multiple search queries (finds more matches)
        queries = [
            f"code using {old_api_name}",
            f"model = {old_api_name}",
            f"\"{old_api_name}\"",
            f"model_name={old_api_name}",
            f"model: {old_api_name}"
        ]
        
        all_results = {}
        
        # Search with each query
        for query in queries:
            print(f"Query: {query}")
            results = self.search_deprecated_code(query, threshold=0.6)
            
            # Combine results (avoid duplicates)
            for result in results:
                filepath = result['filepath']
                if filepath not in all_results:
                    all_results[filepath] = result
                else:
                    # If found multiple times, average confidence
                    all_results[filepath]['confidence'] = (
                        all_results[filepath]['confidence'] + result['confidence']
                    ) / 2
        
        # Format final output
        formatted = self.extract_affected_files(list(all_results.values()))
        
        print("=" * 60)
        print(f"✅ SEARCH COMPLETE: Found {formatted['files_found']} files")
        print("=" * 60 + "\n")
        
        return formatted


    
    def save_results(
        self,
        results: Dict,
        output_file: str = "affected_files.json"
    ) -> None:
        """
        Save results to JSON file for Gowtham
        
        Args:
            results: Results dict from full_search_pipeline()
            output_file: Output filename
        """
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"💾 Saved to: {output_file}\n")
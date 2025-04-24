"""
Vector search implementation for Jester's knowledge base.
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import faiss
import os
from dotenv import load_dotenv

load_dotenv()

class JesterVectorSearch:
    def __init__(self, index_path: str = "data/vector/faiss_index", 
                 chunks_path: str = "data/vector/chunks.json",
                 model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the vector search with specified paths and model.
        
        Args:
            index_path: Path to store/load the FAISS index
            chunks_path: Path to store/load the chunks metadata
            model_name: Name of the sentence transformer model to use
        """
        self.model = SentenceTransformer(model_name)
        self.index_path = Path(index_path)
        self.chunks_path = Path(chunks_path)
        
        # Create parent directories if they don't exist
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.chunks_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize or load index and chunks
        self._load_or_create_index()

    def _load_or_create_index(self):
        """Load existing index and chunks or create new ones."""
        if self.index_path.exists() and self.chunks_path.exists():
            self.index = faiss.read_index(str(self.index_path))
            with open(self.chunks_path, 'r') as f:
                self.chunks = json.load(f)
        else:
            # Create a new index with dimensions matching the model
            self.index = faiss.IndexFlatL2(self.model.get_sentence_embedding_dimension())
            self.chunks = []
            self._save_state()

    def search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Search for similar content using the query."""
        if len(self.chunks) == 0:
            return []
        
        # Encode query
        query_embedding = self.model.encode([query])[0]
        
        # Search the index
        distances, indices = self.index.search(
            query_embedding.reshape(1, -1).astype('float32'), 
            k
        )
        
        # Get results
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.chunks):  # Ensure index is valid
                chunk = self.chunks[idx].copy()
                chunk['similarity'] = float(1.0 / (1.0 + distance))  # Convert distance to similarity
                results.append(chunk)
        
        return results

    def add_chunk(self, text: str, metadata: Optional[Dict[str, Any]] = None):
        """Add a single text chunk to the vector store."""
        # Encode text
        embedding = self.model.encode([text])[0]
        
        # Add to FAISS index
        self.index.add(np.array([embedding]).astype('float32'))
        
        # Store text and metadata
        self.chunks.append({
            "text": text,
            "metadata": metadata or {}
        })
        
        # Save updates
        self._save_state()
        
    def batch_add_chunks(self, texts: List[str], metadata_list: Optional[List[Dict[str, Any]]] = None):
        """Add multiple chunks efficiently."""
        if metadata_list is None:
            metadata_list = [{} for _ in texts]
            
        # Encode all texts
        embeddings = self.model.encode(texts)
        
        # Add to FAISS index
        self.index.add(embeddings.astype('float32'))
        
        # Store texts and metadata
        for text, metadata in zip(texts, metadata_list):
            self.chunks.append({
                "text": text,
                "metadata": metadata
            })
            
        # Save updates
        self._save_state()
        
    def _save_state(self):
        """Save index and chunks to disk."""
        # Save FAISS index
        faiss.write_index(self.index, str(self.index_path))
        
        # Save chunks
        with open(self.chunks_path, 'w') as f:
            json.dump(self.chunks, f)

    def initialize_with_research(self, research_file: str):
        """Initialize the knowledge base with research documents."""
        with open(research_file, 'r') as f:
            content = f.read()
            
        # Split into meaningful chunks
        chunks = self._chunk_text(content)
        
        # Add chunks to knowledge base
        self.batch_add_chunks(
            chunks,
            [{"type": "research", "source": research_file} for _ in chunks]
        )
        
    def _chunk_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Split text into chunks while preserving context."""
        # Split by double newlines to preserve paragraph structure
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = []
        current_size = 0
        
        for para in paragraphs:
            para_size = len(para)
            if current_size + para_size > chunk_size and current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_size = 0
            current_chunk.append(para)
            current_size += para_size
            
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
            
        return chunks 
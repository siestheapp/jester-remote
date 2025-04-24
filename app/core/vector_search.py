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
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.vector_dir = Path("data/vector")
        self.vector_dir.mkdir(parents=True, exist_ok=True)
        self.research_file = self.vector_dir / "research_embeddings.npz"
        self.research_metadata_file = self.vector_dir / "research_metadata.json"
        self.embeddings = None
        self.metadata = []
        self._load_existing_data()

    def _load_existing_data(self):
        """Load existing embeddings and metadata if they exist."""
        if self.research_file.exists() and self.research_metadata_file.exists():
            # Load embeddings
            data = np.load(str(self.research_file))
            self.embeddings = data['embeddings']
            
            # Load metadata
            with open(self.research_metadata_file, 'r') as f:
                self.metadata = json.load(f)

    def initialize_with_research(self, research_text: str):
        """Initialize the vector search with research document text."""
        # Split the text into chunks (paragraphs)
        chunks = [chunk.strip() for chunk in research_text.split('\n\n') if chunk.strip()]
        
        # Create embeddings
        self.embeddings = self.model.encode(chunks)
        
        # Create metadata
        self.metadata = [{"text": chunk, "type": "research"} for chunk in chunks]
        
        # Save embeddings and metadata
        np.savez(str(self.research_file), embeddings=self.embeddings)
        with open(self.research_metadata_file, 'w') as f:
            json.dump(self.metadata, f)
        
        print(f"Saved {len(chunks)} research chunks to vector store")

    def search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Search for similar content using the query."""
        if self.embeddings is None or len(self.metadata) == 0:
            return []
        
        # Encode query
        query_embedding = self.model.encode([query])[0]
        
        # Calculate similarities
        similarities = np.dot(self.embeddings, query_embedding)
        
        # Get top k results
        top_k_indices = np.argsort(similarities)[-k:][::-1]
        
        results = []
        for idx in top_k_indices:
            result = self.metadata[idx].copy()
            result['similarity'] = float(similarities[idx])
            results.append(result)
        
        return results

    def initialize_with_research(self, research_file: str):
        """
        Initialize the knowledge base with research documents.
        Chunks the document and adds it to the vector store.
        """
        with open(research_file, 'r') as f:
            content = f.read()
            
        # Split into meaningful chunks (e.g., by sections or paragraphs)
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
        # Create parent directories if they don't exist
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.chunks_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, str(self.index_path))
        
        # Save chunks
        with open(self.chunks_path, 'w') as f:
            json.dump(self.chunks, f) 
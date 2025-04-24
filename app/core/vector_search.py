import faiss
import numpy as np
import json
import os
from typing import List, Dict, Any
import openai
from dotenv import load_dotenv
import tiktoken

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
ENCODER = tiktoken.get_encoding("cl100k_base")

class JesterVectorSearch:
    def __init__(self, index_path: str = "data/processed/faiss_index", chunks_path: str = "data/processed/chunks.json"):
        self.index_path = index_path
        self.chunks_path = chunks_path
        self.index = None
        self.chunks = None
        self._load_or_create_index()

    def _load_or_create_index(self):
        """Load existing index and chunks or create new ones."""
        if os.path.exists(self.index_path) and os.path.exists(self.chunks_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.chunks_path, 'r') as f:
                self.chunks = json.load(f)
        else:
            # Create a new index with 1536 dimensions (OpenAI's text-embedding-3-small)
            self.index = faiss.IndexFlatL2(1536)
            self.chunks = []
            self._save_index()

    def _save_index(self):
        """Save the current index and chunks to disk."""
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.chunks_path, 'w') as f:
            json.dump(self.chunks, f)

    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for a text using OpenAI's API."""
        response = openai.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return np.array(response.data[0].embedding).astype('float32')

    def add_chunk(self, text: str, metadata: Dict[str, Any] = None):
        """Add a new text chunk to the index."""
        embedding = self.embed_text(text)
        self.index.add(embedding.reshape(1, -1))
        chunk_data = {
            "text": text,
            "metadata": metadata or {}
        }
        self.chunks.append(chunk_data)
        self._save_index()

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar chunks using the query."""
        query_embedding = self.embed_text(query)
        distances, indices = self.index.search(query_embedding.reshape(1, -1), k)
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.chunks):  # Ensure index is valid
                chunk = self.chunks[idx]
                results.append({
                    "text": chunk["text"],
                    "metadata": chunk["metadata"],
                    "distance": float(distance)
                })
        return results

    def batch_add_chunks(self, texts: List[str], metadata_list: List[Dict[str, Any]] = None):
        """Add multiple chunks at once."""
        if metadata_list is None:
            metadata_list = [{} for _ in texts]
        
        embeddings = []
        for text in texts:
            embedding = self.embed_text(text)
            embeddings.append(embedding)
        
        embeddings_array = np.array(embeddings)
        self.index.add(embeddings_array)
        
        for text, metadata in zip(texts, metadata_list):
            self.chunks.append({
                "text": text,
                "metadata": metadata
            })
        
        self._save_index() 
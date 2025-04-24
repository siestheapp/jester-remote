import os
import faiss
import numpy as np
import json
import openai
from dotenv import load_dotenv
import tiktoken


load_dotenv("config.env")
openai.api_key = os.getenv("OPENAI_API_KEY")
ENCODER = tiktoken.get_encoding("cl100k_base")

# Embed the user query using OpenAI
def embed_query(query):
    response = openai.embeddings.create(
        model="text-embedding-3-small",
        input=[query]
    )
    return np.array(response.data[0].embedding).astype("float32")

# Load FAISS index and chunks
def load_index_and_chunks():
    index = faiss.read_index("a3_knowledge.index")
    with open("faiss_chunks.json", "r") as f:
        chunks = json.load(f)
    return index, chunks

# Perform similarity search
def retrieve_relevant_chunks(query, top_k=5):
    index, chunks = load_index_and_chunks()
    embedded_query = embed_query(query).reshape(1, -1)
    distances, indices = index.search(embedded_query, top_k)
    return [chunks[i] for i in indices[0]]

# Run it standalone
if __name__ == "__main__":
    user_query = input("🔍 Enter your question for A3: ")
    results = retrieve_relevant_chunks(user_query)

    print("\n🧠 Most Relevant Research Chunks:\n")
    for i, chunk in enumerate(results, 1):
        print(f"[{i}] {chunk}\n")

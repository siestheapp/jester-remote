import os
import json
import faiss
import openai
import numpy as np
from dotenv import load_dotenv
from typing import List
import tiktoken

load_dotenv("config.env")
openai.api_key = os.getenv("OPENAI_API_KEY")

ENCODER = tiktoken.get_encoding("cl100k_base")

# Step 1: Load and chunk the text
def chunk_text(text: str, max_tokens=300) -> List[str]:
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""

    for para in paragraphs:
        if len(ENCODER.encode(current + para)) < max_tokens:
            current += "\n\n" + para
        else:
            chunks.append(current.strip())
            current = para

    if current:
        chunks.append(current.strip())
    return chunks

# Step 2: Embed using OpenAI
def embed_chunks(chunks: List[str]) -> List[List[float]]:
    response = openai.embeddings.create(
        model="text-embedding-3-small",
        input=chunks
    )
    return [r.embedding for r in response.data]

# Step 3: Main logic
if __name__ == "__main__":
    path = "knowledge/menswear_research_deepresearch.txt"
    with open(path, "r") as f:
        text = f.read()

    chunks = chunk_text(text)
    vectors = embed_chunks(chunks)

    index = faiss.IndexFlatL2(len(vectors[0]))
    index.add(np.array(vectors).astype("float32"))

    # Save index and chunks for lookup
    faiss.write_index(index, "a3_knowledge.index")
    with open("faiss_chunks.json", "w") as f:
        json.dump(chunks, f, indent=2)

    print(f"✅ Embedded and saved {len(chunks)} chunks to FAISS.")

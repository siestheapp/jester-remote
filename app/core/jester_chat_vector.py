import streamlit as st
import numpy as np
import faiss
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI()

# Load FAISS index and chunks
index = faiss.read_index("jester_knowledge.index")
with open("data/processed/faiss_chunks.json", "r") as f:
    chunks = json.load(f)

def get_relevant_chunks(query, k=3):
    """Get the k most relevant chunks for a query."""
    # Get query embedding
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )
    query_embedding = np.array(response.data[0].embedding).reshape(1, -1)
    
    # Search FAISS index
    D, I = index.search(query_embedding, k)
    return [chunks[i] for i in I[0]]

# Streamlit UI
st.set_page_config(page_title="💬 Jester Chat + Research Brain", layout="wide")
st.title("🧠 Jester Chat – Embedded Size Guide Research")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat input
user_input = st.chat_input("Ask Jester a question about fit logic, category mapping, or edge cases...")

if user_input:
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Get relevant chunks
    relevant_chunks = get_relevant_chunks(user_input)
    chunk_context = "\n\n".join(relevant_chunks)
    
    # Prepare system message
    system_message = (
        "You are Jester, an AI trained on menswear size guide standardization. "
        "Use the following research context to inform your response, but speak naturally:\n\n"
        f"{chunk_context}"
    )
    
    # Get completion from OpenAI
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_input}
    ]
    
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=messages
    )
    
    assistant_response = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

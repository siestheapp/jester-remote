import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load API key from .env
load_dotenv("config.env")

# Page config
st.set_page_config(page_title="Jester Chat", layout="wide")
st.title("💬 Jester Chat Assistant")

# Initialize OpenAI client
client = OpenAI()

# System prompt
SYSTEM_PROMPT = (
    "You are Jester, an AI assistant helping design and normalize clothing size guides. "
    "You help standardize size measurements across different brands and categories."
)

# Chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
user_prompt = st.chat_input("Ask Jester about size guide structure, fit zones, or schema design...")

# Process input
if user_prompt:
    # Show user message
    st.chat_message("user").write(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    # Call GPT-4 Turbo
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=st.session_state.messages,
        max_tokens=1000,
        temperature=0.7
    )

    assistant_reply = response.choices[0].message.content
    st.chat_message("assistant").write(assistant_reply)
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

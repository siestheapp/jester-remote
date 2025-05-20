import streamlit as st
import os
from dotenv import load_dotenv
from app.core.jester_chat import JesterChat
from app.services.size_service import SizeService
from app.db.database import AsyncSessionLocal, init_db
import json

# Set page config first
st.set_page_config(
    page_title="Jester - Size Guide Analysis Assistant",
    page_icon="🧠",
    layout="wide"
)

# Initialize session state
if "jester" not in st.session_state:
    st.session_state.jester = JesterChat()

if "current_step" not in st.session_state:
    st.session_state.current_step = "chat"

if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize chat with a welcome message
st.session_state.messages.append({
    "role": "assistant",
    "content": "Hi there! I'm here to help you with size guides. What would you like to know?"
})

# Load environment variables and check API key
load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    st.error("OpenAI API key not found in .env file")
    st.stop()

# Title
st.title("Jester - Size Guide Analysis Assistant")

def process_metadata_submission():
    """Handle metadata form submission and transition to chat."""
    metadata = {
        "brand": st.session_state.get("brand", ""),
        "gender": st.session_state.get("gender", ""),
        "header": st.session_state.get("header", ""),
        "source_url": st.session_state.get("source_url", ""),
        "unit": st.session_state.get("unit", ""),
        "scope": st.session_state.get("scope", "")
    }
    
    # Store metadata and move to chat step
    st.session_state.metadata = metadata
    st.session_state.current_step = "chat"
    
    # Determine if any metadata was provided
    has_metadata = any(value.strip() for value in metadata.values())
    
    if has_metadata:
        # If metadata was provided, ask for confirmation
        initial_message = f"""Hello! I've received the following size guide information:

{metadata['brand'] and f"Brand: {metadata['brand']}" or ""}
{metadata['gender'] and f"Gender: {metadata['gender']}" or ""}
{metadata['header'] and f"Size Guide Header: {metadata['header']}" or ""}
{metadata['source_url'] and f"Source URL: {metadata['source_url']}" or ""}
{metadata['unit'] and f"Unit of Measurement: {metadata['unit']}" or ""}
{metadata['scope'] and f"Size Guide Scope: {metadata['scope']}" or ""}

How can I assist you with this size guide?"""
    else:
        initial_message = """I'm here to help with your size guide! Please provide some details:

1. The brand name
2. The type of clothing
3. Any specific measurements you need help with

What would you like to know?"""
    
    st.session_state.messages = [
        {"role": "assistant", "content": initial_message}
    ]

# Remove the metadata step since we're not using it anymore
if st.session_state.current_step == "chat":
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Your response..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Process the message using the JesterChat class
        response = st.session_state.jester.process_message(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        
    # Add a "Clear Chat" button
    if st.sidebar.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Chat Interface Step
elif st.session_state.current_step == "chat":
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Your response..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Process the message using the JesterChat class
        response = st.session_state.jester.process_message(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Add a "Start Over" button
    if st.sidebar.button("Start Over"):
        st.session_state.current_step = "metadata"
        st.session_state.uploaded_image = None
        st.session_state.metadata = None
        st.session_state.messages = []
        st.rerun()

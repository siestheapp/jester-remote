import streamlit as st
import os
from dotenv import load_dotenv
from app.core.jester_chat import JesterChat
from app.core.vision import process_size_guide_image
from app.services.size_service import SizeService
from app.db.database import AsyncSessionLocal, init_db
import json
import asyncio
import nest_asyncio
import warnings
import tempfile

# Suppress specific warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, module="torch")

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Load environment variables
load_dotenv()
print("✅ .env loaded?", os.path.exists(".env"))
print("✅ API KEY FOUND?", bool(os.getenv("OPENAI_API_KEY")))

# Set page config
st.set_page_config(
    page_title="Jester - Size Guide Analysis Assistant",
    page_icon="🧠",
    layout="wide"
)

# Initialize Jester in session state if not already present
if "jester" not in st.session_state:
    st.session_state.jester = JesterChat()

if "current_step" not in st.session_state:
    st.session_state.current_step = "metadata"

if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None

if "metadata" not in st.session_state:
    st.session_state.metadata = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# Title
st.title("Jester - Size Guide Analysis Assistant")

def save_uploaded_file(uploaded_file):
    """Save uploaded file to temp directory and return the path."""
    if uploaded_file is None:
        return None
    
    # Create uploads directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)
    
    # Save file to uploads directory
    file_path = os.path.join("uploads", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

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

Does this information look correct? Once you confirm, I'll analyze the size guide image and help structure the data appropriately."""
    else:
        # If no metadata was provided, start with image analysis
        initial_message = """Hello! I'll help you analyze this size guide. Let me take a look at the image first, and then I'll ask you some questions about it."""
    
    st.session_state.messages = [
        {"role": "assistant", "content": initial_message}
    ]

# Metadata Collection Step
if st.session_state.current_step == "metadata":
    st.header("📋 Size Guide Information (Optional)")
    st.info("You can fill in these details now, or let me analyze the image first and I'll ask you questions about it.")
    
    # Create columns for form fields
    col1, col2 = st.columns(2)
    
    with col1:
        # Brand input
        st.text_input("Brand (e.g., Banana Republic)", key="brand")
        
        # Gender selection
        st.selectbox("Gender", 
                    ["", "Men's", "Women's", "Unisex"],
                    key="gender")
        
        # Size Guide Header
        st.text_input("Size Guide Header (e.g., Shirts & Sweaters)", 
                     key="header")
    
    with col2:
        # Source URL
        st.text_input("Source URL (where the size guide was found)", 
                     key="source_url")
        
        # Unit of Measurement
        st.radio("Unit of Measurement", 
                ["", "inches", "centimeters"],
                key="unit")
        
        # Size Guide Scope
        st.selectbox("Size Guide Scope",
                    [
                        "",
                        "This specific item only",
                        "A category (e.g., Tops, Outerwear)",
                        "All clothing for this gender",
                        "All clothing (brand-wide)"
                    ],
                    help="How widely applicable is this size guide?",
                    key="scope")
    
    st.header("📤 Upload Size Guide")
    uploaded_file = st.file_uploader("Upload a size guide image", 
                                   type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        st.session_state.uploaded_image = uploaded_file
        st.image(uploaded_file, caption="Uploaded Size Guide")
    
    # Submit button
    if st.button("Submit and Start Analysis"):
        if not uploaded_file:
            st.error("Please upload a size guide image")
        else:
            process_metadata_submission()
            st.rerun()

# Chat Interface Step
elif st.session_state.current_step == "chat":
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Show 'Jester is typing...' if waiting for assistant response
    if st.session_state.get("pending_assistant_response", False):
        with st.chat_message("assistant"):
            st.write("Jester is typing...")

    # Chat input
    prompt = st.chat_input("Your response...")
    if prompt:
        # Add user message and set pending flag
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.pending_assistant_response = True
        st.rerun()

    # If pending assistant response, process it now
    if st.session_state.get("pending_assistant_response", False):
        # Only process if the last message is from the user
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
            prompt = st.session_state.messages[-1]["content"]
            # Ensure metadata is a dict
            metadata = st.session_state.metadata if st.session_state.metadata is not None else {}
            # If this is the first response and metadata was provided
            if len(st.session_state.messages) == 2 and any(metadata.values()):
                if "yes" in prompt.lower():
                    # Save uploaded file and process the image with provided metadata
                    with st.spinner("Analyzing size guide image..."):
                        file_path = save_uploaded_file(st.session_state.uploaded_image)
                        if file_path:
                            try:
                                analysis_result = process_size_guide_image(
                                    image_path=file_path,
                                    metadata=metadata
                                )
                                analysis_message = f"""Thank you for confirming. I've analyzed the size guide image and here's what I found:\n\n{analysis_result}\n\nWould you like me to proceed with storing this data in the standardized format? I can explain any adjustments I'm planning to make."""
                                st.session_state.messages.append({"role": "assistant", "content": analysis_message})
                            except Exception as e:
                                st.error(f"Error processing image: {str(e)}")
                        else:
                            st.error("Failed to process the uploaded file.")
                else:
                    correction_message = "I understand the information needs correction. Please let me know what needs to be changed, and I'll update it accordingly."
                    st.session_state.messages.append({"role": "assistant", "content": correction_message})
            else:
                # Handle the case where no metadata was provided or we're past the initial confirmation
                if len(st.session_state.messages) == 2:
                    # First response when no metadata was provided - analyze image
                    with st.spinner("Analyzing size guide image..."):
                        file_path = save_uploaded_file(st.session_state.uploaded_image)
                        if file_path:
                            try:
                                analysis_result = process_size_guide_image(
                                    image_path=file_path,
                                    metadata={}  # Empty metadata
                                )
                                analysis_message = f"""I've taken a look at the size guide. Here's what I can see:\n\n{analysis_result}\n\nLet me ask you a few questions to help categorize this properly:\n1. This appears to be from which brand?\n2. Is this for men's, women's, or unisex clothing?\n3. What type of clothing does this size guide cover?"""
                                st.session_state.messages.append({"role": "assistant", "content": analysis_message})
                            except Exception as e:
                                st.error(f"Error processing image: {str(e)}")
                        else:
                            st.error("Failed to process the uploaded file.")
                else:
                    # Get Jester's response for other messages
                    response = st.session_state.jester.get_response(
                        prompt,
                        st.session_state.messages
                    )
                    st.session_state.messages.append({"role": "assistant", "content": response})
            # Reset pending flag and rerun to show new assistant message
            st.session_state.pending_assistant_response = False
            st.rerun()

    # Add a "Start Over" button
    if st.sidebar.button("Start Over"):
        st.session_state.current_step = "metadata"
        st.session_state.uploaded_image = None
        st.session_state.metadata = None
        st.session_state.messages = []
        st.session_state.pending_assistant_response = False
        st.rerun()

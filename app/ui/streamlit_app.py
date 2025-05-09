"""
Streamlit UI for the Jester application.
This module provides the web interface for the application.
"""

import streamlit as st
import os
from dotenv import load_dotenv
import json
import asyncio
import nest_asyncio
import warnings

# Import core functionality directly
from app.core.jester_chat import JesterChat
from app.core.vision import process_size_guide_image
from app.services.size_service import SizeService
from app.db.database import AsyncSessionLocal, init_db
from app.config import config

# Suppress specific warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, module="torch")

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Load environment variables
load_dotenv()

# Initialize the chat interface
st.set_page_config(page_title="Jester - Size Guide Analysis", layout="wide")
st.title("🧠 Jester - Size Guide Analysis Assistant")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "jester" not in st.session_state:
    st.session_state.jester = JesterChat()
if "db_initialized" not in st.session_state:
    st.session_state.db_initialized = False
if "current_step" not in st.session_state:
    st.session_state.current_step = "upload"
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "proposed_ingestion" not in st.session_state:
    st.session_state.proposed_ingestion = None
if "metadata" not in st.session_state:
    st.session_state.metadata = {}

# Initialize database if needed
if not st.session_state.db_initialized:
    try:
        asyncio.run(init_db())
        st.session_state.db_initialized = True
    except Exception as e:
        st.error(f"Database initialization error: {str(e)}")

# Step 1: Upload and Initial Metadata
if st.session_state.current_step == "upload":
    st.header("📄 Upload Size Guide")
    
    # Essential metadata first
    brand = st.text_input("Brand (e.g., Banana Republic)")
    gender = st.selectbox("Gender", options=["", "Men", "Women", "Unisex"])
    
    # File upload
    uploaded_file = st.file_uploader("Upload a size guide image", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Size Guide", use_container_width=True)
        
        if st.button("Begin Analysis", disabled=not (brand and gender)):
            if not brand or not gender:
                st.warning("⚠️ Please provide the brand and gender before proceeding.")
            else:
                with st.spinner("Processing size guide..."):
                    # Save the uploaded file
                    file_path = os.path.join(config.UPLOADS_DIR, uploaded_file.name)
                    os.makedirs(config.UPLOADS_DIR, exist_ok=True)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Store initial metadata
                    st.session_state.metadata = {
                        'brand': brand,
                        'gender': gender,
                        'file_path': file_path
                    }
                    
                    # Process the image
                    st.session_state.analysis_result = process_size_guide_image(file_path)
                    st.session_state.current_step = "analysis"
                    st.rerun()

# Step 2: AI Analysis and Additional Information
elif st.session_state.current_step == "analysis":
    st.header("🔍 Size Guide Analysis")
    
    # Display the uploaded image for reference
    if 'file_path' in st.session_state.metadata:
        st.image(st.session_state.metadata['file_path'], caption="Uploaded Size Guide", width=400)
    
    # Display AI's analysis and request for additional information
    st.write("### Jester's Analysis")
    
    # Show the initial analysis
    with st.expander("📊 Initial Data Extraction", expanded=True):
        st.json(st.session_state.analysis_result)
    
    # Additional metadata collection based on AI analysis
    st.write("### Additional Information Needed")
    
    # Collect additional metadata based on the analysis
    size_guide_header = st.text_input("Size Guide Header/Category", 
                                    help="What type of clothing does this size guide cover?")
    unit = st.radio("Unit of Measurement", 
                    options=["inches", "centimeters"],
                    horizontal=True)
    scope = st.selectbox("Size Guide Scope",
                        options=["This specific item only", 
                                "A category (e.g., Tops, Outerwear)", 
                                "All clothing for this gender"])
    source_url = st.text_input("Source URL (optional)",
                              help="Where was this size guide found?")
    
    if st.button("Generate Ingestion Proposal"):
        # Update metadata with additional information
        st.session_state.metadata.update({
            'size_guide_header': size_guide_header,
            'unit': unit,
            'scope': scope,
            'source_url': source_url
        })
        
        # Prepare the ingestion proposal
        async def prepare_ingestion():
            async with AsyncSessionLocal() as session:
                size_service = SizeService(session)
                proposal = await size_service.prepare_ingestion_proposal(
                    st.session_state.analysis_result,
                    st.session_state.metadata
                )
                return proposal
        
        with st.spinner("Preparing ingestion proposal..."):
            st.session_state.proposed_ingestion = asyncio.run(prepare_ingestion())
            st.session_state.current_step = "approval"
            st.rerun()

# Step 3: Review and Approval
elif st.session_state.current_step == "approval":
    st.header("✅ Review and Approve Ingestion")
    
    # Display the proposed database operations
    st.write("### Proposed Database Operations")
    st.json(st.session_state.proposed_ingestion)
    
    # Approval buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👍 Approve and Ingest"):
            async def execute_ingestion():
                async with AsyncSessionLocal() as session:
                    size_service = SizeService(session)
                    result = await size_service.execute_ingestion(
                        st.session_state.proposed_ingestion
                    )
                    return result
            
            with st.spinner("Ingesting data..."):
                result = asyncio.run(execute_ingestion())
                if result['success']:
                    st.success("✅ Size guide successfully ingested!")
                    # Reset the state for next upload
                    st.session_state.current_step = "upload"
                    st.session_state.analysis_result = None
                    st.session_state.proposed_ingestion = None
                    st.session_state.metadata = {}
                else:
                    st.error(f"❌ Error during ingestion: {result['error']}")
    
    with col2:
        if st.button("👎 Reject and Revise"):
            st.session_state.current_step = "analysis"
            st.rerun()

# Footer with step indicator
st.markdown("---")
st.write(f"Current step: {st.session_state.current_step}")

# Right column for chat interface
with col2:
    st.header("💬 Chat with Jester")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about size guides, measurements, or standardization..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get response from Jester
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.jester.get_response(
                    prompt,
                    chat_history=st.session_state.messages[:-1]  # Exclude the current message
                )
                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response}) 
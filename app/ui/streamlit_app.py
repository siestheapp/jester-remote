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
from pathlib import Path
from datetime import datetime
import requests
import re
import io
from PIL import Image as PILImage, UnidentifiedImageError

# Import core functionality
from app.core.jester_chat import JesterChat
from app.services.size_service import SizeService
from app.db.database import AsyncSessionLocal, init_db
from app.config import config

# Suppress specific warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, module="torch")
nest_asyncio.apply()
load_dotenv()

# Page config
st.set_page_config(page_title="Jester - Size Guide Analysis", layout="wide")
st.title("🧠 Jester - Size Guide Analysis Assistant")

# Session state
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

# Initialize DB
if not st.session_state.db_initialized:
    try:
        asyncio.run(init_db())
        st.session_state.db_initialized = True
    except Exception as e:
        st.error(f"Database initialization error: {str(e)}")

# Step 1: Upload and Initial Metadata
if st.session_state.current_step == "upload":
    st.header("📄 Upload Size Guide")

    # Optional metadata
    brand = st.text_input("Brand (optional)")
    gender = st.selectbox("Gender (optional)", options=["", "Men", "Women", "Unisex"])
    size_guide_header = st.text_input("Size Guide Header (optional)")
    source_url = st.text_input("Source URL (optional)")
    unit = st.radio("Unit of Measurement (optional)", options=["", "inches", "centimeters"], horizontal=True)
    scope = st.selectbox("Size Guide Scope (optional)", options=["", "This specific item only", "A category (e.g., Tops, Outerwear)", "All clothing for this gender"])

    uploaded_file = st.file_uploader("Upload a size guide image", type=["jpg", "jpeg", "png"])

    st.info("You can upload a size guide image without filling in metadata. Metadata is optional and can be added later.")

    if uploaded_file:
        file_bytes = uploaded_file.getvalue()
        safe_filename = re.sub(r"[^\w_.-]", "_", uploaded_file.name)

        st.image(uploaded_file, caption="Uploaded Size Guide", use_container_width=True)
        st.write(f"File name: {uploaded_file.name}")
        st.write(f"File type: {uploaded_file.type}")
        st.write(f"File size: {uploaded_file.size} bytes")

        if uploaded_file.size < 5000:
            st.warning("⚠️ This image looks very small. If you dragged a screenshot thumbnail, try uploading from Finder instead.")

        # Validate the image
        try:
            img = PILImage.open(io.BytesIO(file_bytes))
            img.verify()
        except UnidentifiedImageError as e:
            st.error(f"❌ Uploaded file is not a valid image. Try uploading from Finder instead of dragging a screenshot thumbnail.")
            st.stop()

        if st.button("Submit and Continue to Chat"):
            try:
                files = {
                    "file": (safe_filename, io.BytesIO(file_bytes), uploaded_file.type or "image/png")
                }

                data = {
                    "brand": brand,
                    "gender": gender,
                    "size_guide_header": size_guide_header,
                    "source_url": source_url,
                    "unit_of_measurement": unit,
                    "size_guide_scope": scope
                }
                data = {k: v for k, v in data.items() if v}

                response = requests.post(
                    "http://localhost:8000/api/process-size-guide",
                    files=files,
                    data=data
                )

                if response.status_code == 200:
                    result = response.json()
                    st.session_state.analysis_result = result["data"]
                    st.session_state.metadata = {
                        'brand': brand,
                        'gender': gender,
                        'size_guide_header': size_guide_header,
                        'source_url': source_url,
                        'unit': unit,
                        'scope': scope,
                        'file_path': result["data"]["metadata"]["source_image"]
                    }
                    st.session_state.current_step = "chat"
                    st.rerun()
                else:
                    st.error(f"Error processing image: {response.status_code} - {response.text}")
                    st.stop()

            except Exception as e:
                st.error(f"Unexpected error during upload: {str(e)}")
                st.stop()


# Step 2: Chat interface after upload
elif st.session_state.current_step == "chat":
    st.header("💬 Chat with Jester about your Size Guide")
    if 'file_path' in st.session_state.metadata:
        st.image(st.session_state.metadata['file_path'], caption="Uploaded Size Guide", width=400)
    st.info("You can chat with Jester about the uploaded size guide, measurements, or standardization.")
    col1, col2 = st.columns([2, 1])
    with col2:
        st.subheader("Chat")
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        if prompt := st.chat_input("Ask about size guides, measurements, or standardization..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = st.session_state.jester.get_response(
                        prompt,
                        chat_history=st.session_state.messages[:-1]
                    )
                    st.write(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
    # Button to proceed to analysis
    if st.button("Continue to Analysis"):
        st.session_state.current_step = "analysis"
        st.rerun()

# Step 3: AI Analysis and Additional Information
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

# Step 4: Review and Approval
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
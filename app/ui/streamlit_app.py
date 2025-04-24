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

# Create two columns for the layout
col1, col2 = st.columns([1, 2])

# Left column for metadata and upload
with col1:
    st.header("📄 Size Guide Information")
    
    # Metadata inputs
    brand = st.text_input("Brand (e.g., Banana Republic)")
    gender = st.selectbox("Gender", options=["", "Men", "Women", "Unisex"])
    size_guide_header = st.text_input("Size Guide Header (e.g., Shirts & Sweaters)")
    source_url = st.text_input("Source URL (where the size guide was found)")
    unit = st.radio("Unit of Measurement", options=["", "inches", "centimeters"], horizontal=True)
    scope = st.selectbox(
        "Size Guide Scope",
        options=["", "This specific item only", "A category (e.g., Tops, Outerwear)", "All clothing for this gender"]
    )
    
    # File upload section
    st.header("📁 Upload Size Guide")
    uploaded_file = st.file_uploader("Upload a size guide image", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        # Display the uploaded image
        st.image(uploaded_file, caption="Uploaded Size Guide", use_container_width=True)
        
        if st.button("🚀 Process Size Guide"):
            if not brand or not gender or not unit or not scope:
                st.warning("⚠️ Please fill in all required metadata fields.")
            else:
                with st.spinner("Processing size guide..."):
                    # Save the uploaded file
                    file_path = os.path.join(config.UPLOADS_DIR, uploaded_file.name)
                    os.makedirs(config.UPLOADS_DIR, exist_ok=True)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Process the image
                    result = process_size_guide_image(file_path)
                    
                    # Prepare metadata
                    metadata = {
                        'brand': brand,
                        'gender': gender,
                        'size_guide_header': size_guide_header,
                        'source_url': source_url,
                        'unit': unit,
                        'scope': scope
                    }
                    
                    # Add metadata to the result
                    result['metadata'].update(metadata)
                    
                    # Initialize database if needed
                    if not st.session_state.db_initialized:
                        try:
                            asyncio.run(init_db())
                            st.session_state.db_initialized = True
                        except Exception as e:
                            st.error(f"Database initialization error: {str(e)}")
                            st.warning("The app will continue, but database features may be limited.")
                    
                    # Store in database
                    async def store_in_db():
                        async with AsyncSessionLocal() as session:
                            size_service = SizeService(session)
                            db_result = await size_service.process_size_guide(file_path, metadata)
                            return db_result
                    
                    # Run the async function
                    try:
                        db_result = asyncio.run(store_in_db())
                        
                        if db_result['success']:
                            # Add the processed data to the knowledge base
                            st.session_state.jester.add_to_knowledge_base(
                                json.dumps(result, indent=2),
                                metadata=result['metadata']
                            )
                            
                            st.success(f"✅ Size guide processed and stored in database! (ID: {db_result['size_guide_id']})")
                            
                            # Display the extracted data
                            st.subheader("📊 Extracted Size Chart")
                            st.json(result)
                        else:
                            st.error(f"❌ Error storing in database: {db_result['error']}")
                    except Exception as e:
                        st.error(f"❌ Error storing in database: {str(e)}")
                        st.warning("The app will continue, but database features may be limited.")

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
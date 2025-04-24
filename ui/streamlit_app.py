import streamlit as st
import base64
import json
import os
import sys
import pandas as pd
from app.core.vision import run_vision_prompt
from app.utils.vector_mapper import match_to_standard
from app.services.ingestion_service import IngestService
from app.services.size_service import SizeService
from app.utils.vector_mapper import VectorMapper

st.set_page_config(page_title="Jester Ingestor", layout="wide")
st.title("🧠 Jester - Clothing Size Guide Ingestor")

# --- Metadata Inputs ---
st.subheader("📄 Provide Metadata (optional but recommended)")
brand = st.text_input("Brand (e.g., Banana Republic)")
gender = st.selectbox("Gender", options=["", "Men", "Women", "Unisex"])
size_guide_header = st.text_input("Size Guide Header (e.g., Shirts & Sweaters, Apparel)")
source_url = st.text_input("Source URL (where the screenshot was taken)")
unit = st.radio("Unit of Measurement", options=["", "inches", "centimeters"], horizontal=True)
scope = st.selectbox(
    "📐 Size Guide Scope",
    options=["", "This specific item only", "A category (e.g., Tops, Outerwear)", "All clothing for this gender"]
)

# --- File Uploader ---
st.subheader("📤 Upload a size guide image")
uploaded_file = st.file_uploader("Upload JPG, JPEG, or PNG", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
    image_path = f"uploads/{uploaded_file.name}"

    with open(image_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if st.button("🚀 Submit for Analysis"):
        if not brand or not gender or not unit or not scope:
            st.warning("⚠️ Metadata incomplete. Please fill in all required fields.")
            st.stop()

        with st.spinner("Running GPT-4 Vision..."):
            gpt_output = run_vision_prompt(image_path)

        try:
            json_start = gpt_output.index("{")
            json_end = gpt_output.rindex("}") + 1
            json_str = gpt_output[json_start:json_end]
            parsed = json.loads(json_str)
            st.success("✅ GPT extracted size guide successfully.")
        except (json.JSONDecodeError, ValueError):
            st.error("❌ GPT output was not valid JSON. Please review the raw output:")
            st.text(gpt_output)
            st.stop()

        # Show extracted size chart
        st.subheader("📏 Extracted Size Chart")
        st.json(parsed)

        # Show collected metadata
        st.subheader("🧾 Metadata Summary")
        st.write({
            "Brand": brand,
            "Gender": gender,
            "Size Guide Header": size_guide_header,
            "Source URL": source_url,
            "Unit": unit,
            "Scope": scope
        })

        st.success("✅ No follow-up questions. Ready to convert to SQL.")

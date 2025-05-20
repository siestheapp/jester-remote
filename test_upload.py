import streamlit as st
uploaded_file = st.file_uploader("Upload a file", type=["jpg", "jpeg", "png"])
if uploaded_file:
    st.image(uploaded_file)
    st.write("File uploaded successfully!") 
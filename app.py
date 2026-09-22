import streamlit as st
from pypdf import PdfReader

st.title("مساعد المنهج العراقي")

uploaded_file = st.file_uploader("ارفعي ملف PDF", type=["pdf"])

if uploaded_file:
    reader = PdfReader(uploaded_file)
    st.success(f"عدد الصفحات: {len(reader.pages)}")

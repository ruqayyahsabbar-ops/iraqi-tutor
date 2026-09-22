import streamlit as st
from pdf2image import convert_from_bytes
import pytesseract

st.title("اختبار OCR")

pdf_file = st.file_uploader("ارفعي كتاب PDF", type=["pdf"])

if pdf_file:
    pdf_bytes = pdf_file.read()

    images = convert_from_bytes(pdf_bytes, first_page=1, last_page=1)

    st.image(images[0], caption="الصفحة الأولى")

    text = pytesseract.image_to_string(images[0], lang="ara+eng")

    st.text_area("النص المستخرج", text, height=300)

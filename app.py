import streamlit as st
from pypdf import PdfReader

st.set_page_config(
    page_title="مساعد المنهج العراقي",
    page_icon="📚"
)

st.title("📚 مساعد المنهج العراقي")

pdf_file = st.file_uploader(
    "ارفعي الكتاب بصيغة PDF",
    type=["pdf"]
)

if pdf_file:
    reader = PdfReader(pdf_file)

    st.success(f"تم رفع الكتاب بنجاح — عدد الصفحات: {len(reader.pages)}")

    search = st.text_input(
        "🔍 ابحثي داخل الكتاب:",
        placeholder="مثال: الخلية"
    )

    if search.strip():

        results = []

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""

            if search.strip().lower() in text.lower():
                results.append((page_number, text))

        if results:
            st.success(f"وجدت الكلمة في {len(results)} صفحة")

            for page_number, text in results:
                st.subheader(f"📄 الصفحة {page_number}")

                st.text_area(
                    "النص:",
                    text,
                    height=250,
                    key=f"page_{page_number}"
                )

        else:
            st.warning("لم يتم العثور على هذه الكلمة داخل الكتاب.")

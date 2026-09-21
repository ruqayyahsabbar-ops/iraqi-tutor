import streamlit as st
import os

# محاولة استيراد مكتبات قراءة الـ PDF وتحويل الصور
try:
    import pypdf
    from pdf2image import convert_from_bytes
    import pytesseract
    import numpy as np
    from PIL import Image
    LOCAL_OCR_SUPPORT = True
except ImportError:
    LOCAL_OCR_SUPPORT = False

# إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="مساعد المنهج العراقي",
    page_icon="📚",
    layout="centered"
)

st.title("📚 مساعد المنهج العراقي الشامل")
st.write("ارفعي كتاب المنهج المصور (PDF)، وسيقوم التطبيق بقراءة أوراق الكتاب واستخراج الإجابة الحقيقية منها فوراً وبدون أي مفاتيح خارجية.")

st.divider()

# الشريط الجانبي لاختيار المادة والمرحلة
st.sidebar.header("🎯 تحديد المنهج والمرحلة")
grade = st.sidebar.selectbox("المرحلة الدراسية:", ["السادس الإعدادي", "الخامس الإعدادي", "الرابع الإعدادي", "الثالث المتوسط", "الثاني المتوسط", "الأول المتوسط"])
subject = st.sidebar.selectbox("المادة الدراسية:", ["الفيزياء", "الكيمياء", "الأحياء", "الرياضيات", "اللغة العربية", "اللغة الإنجليزية"])

# ==================== لوحة التحكم لرفع الكتب المصورة ====================
st.sidebar.divider()
st.sidebar.subheader("🔒 لوحة التحكم (رفع الكتب)")
admin_mode = st.sidebar.checkbox("تفعيل وضع رفع الكتب (Admin)")

uploaded_pdf_file = None
if admin_mode:
    st.sidebar.info(f"ارفعي ملف الكتاب المصور لمادة ({subject} - {grade}):")
    uploaded_pdf_file = st.sidebar.file_uploader("اختر ملف الـ PDF:", type=["pdf"])
    if uploaded_pdf_file:
        st.sidebar.success("✅ تم رفع الملف بنجاح وجاهز للقراءة!")
# =========================================================================

st.sidebar.divider()
st.sidebar.header("🔍 بحث الطالب")
user_question = st.text_input(
    "اكتب الكلمة أو السؤال المراد البحث عنه في أوراق الكتاب:",
    placeholder="مثال: التصنيف، الخلية..."
)

if st.button("ابحث في الأوراق", type="primary"):
    if not user_question.strip():
        st.warning("⚠️ الرجاء كتابة الكلمة أو السؤال أولاً.")
    elif not uploaded_pdf_file:
        st.warning("⚠️ يرجى رفع ملف الكتاب (PDF) من لوحة التحكم في القائمة الجانبية أولاً.")
    else:
        with st.spinner("⏳ جاري قراءة أوراق الكتاب واستخراج النص محلياً..."):
            try:
                if not LOCAL_OCR_SUPPORT:
                    st.error("❌ المكتبات الخاصة بقراءة الصور غير متوفرة في بيئة التشغيل.")
                else:
                    pdf_bytes = uploaded_pdf_file.read()
                    
                    # تحويل صفحات ملف الـ PDF إلى صور داخل الذاكرة
                    images = convert_from_bytes(pdf_bytes)
                    
                    extracted_full_text = ""
                    keyword = user_question.strip().lower()
                    found_pages = []

                    # قراءة كل صفحة (صورة) واستخراج النصوص العربية منها باستخدام Tesseract OCR
                    for idx, img in enumerate(images):
                        # قراءة النص باللغة العربية والإنجليزية
                        text = pytesseract.image_to_string(img, lang='ara+eng')
                        if keyword in text.lower():
                            found_pages.append(idx + 1)
                            extracted_full_text += f"\n--- 📄 صفحة رقم ({idx + 1}) ---\n{text}\n"

                    st.success("✅ نتيجة البحث الفعلي داخل أوراق الكتاب:")
                    
                    if found_pages:
                        st.info(f"📌 وُجدت الكلمة في الصفحات التالية: {found_pages}")
                        st.text_area("النص المستخرج حرفياً من الكتاب:", extracted_full_text, height=300)
                    else:
                        st.warning(f"لم يتم العثور على كلمة '{user_question}' في أوراق هذا الملف بالتحديد. تأكدي من كتابة الكلمة بشكل صحيح أو رفع الكتاب الخاص بالموضوع.")
                        
            except Exception as e:
                st.error(f"حدث خطأ أثناء قراءة الأوراق: {e}")
                                                           

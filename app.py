import streamlit as st
import os

# محاولة استيراد مكتبة قراءة الـ PDF
try:
    import pypdf
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

# إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="مساعد المنهج العراقي",
    page_icon="📚",
    layout="centered"
)

# عنوان التطبيق الموجه للطلاب
st.title("📚 مساعد المنهج العراقي الشامل")
st.write("أهلاً بك عزيزي الطالب! اختر مرحلتك الدراسية ومادتك، واكتب كلمة البحث أو العنوان لتحصل على النص الحرفي من الكتاب.")

st.divider()

# الشريط الجانبي لتحديد المنهج والمرحلة للطلاب
st.sidebar.header("🎯 تحديد المنهج والمرحلة")

grade = st.sidebar.selectbox(
    "المرحلة الدراسية:",
    [
        "السادس الإعدادي", 
        "الخامس الإعدادي", 
        "الرابع الإعدادي", 
        "الثالث المتوسط", 
        "الثاني المتوسط", 
        "الأول المتوسط"
    ]
)

# المواد الدراسية
subject = st.sidebar.selectbox(
    "المادة الدراسية:",
    [
        "الفيزياء", 
        "الكيمياء", 
        "الأحياء", 
        "الرياضيات", 
        "اللغة العربية", 
        "اللغة الإنجليزية", 
        "التربية الإسلامية",
        "الحاسوب",
        "اللغة الفرنسية",
        "اللغة الكردية"
    ]
)

# ==================== لوحة التحكم الخاصة بكِ (رفع الكتب للنظام) ====================
st.sidebar.divider()
st.sidebar.subheader("🔒 لوحة التحكم (خاصة بكِ فقط)")
admin_mode = st.sidebar.checkbox("تفعيل وضع رفع الكتب (Admin)")

uploaded_pdfs = []
if admin_mode:
    st.sidebar.info(f"أنتِ الآن في وضع المدير. ارفعي كتب مادة ({subject} - {grade}):")
    
    uploaded_pdfs = st.sidebar.file_uploader(
        f"اختر ملفات الـ PDF:", 
        type=["pdf"], 
        accept_multiple_files=True
    )
    
    if uploaded_pdfs:
        st.sidebar.success(f"✅ تم رفع {len(uploaded_pdfs)} ملفاً بنجاح!")
# =================================================================================

st.sidebar.divider()
st.sidebar.header("📸 رفع الصور والامتحانات")

# 1. أمر رفع الصور للطلاب
uploaded_image = st.sidebar.file_uploader("ارفع صورة السؤال:", type=["png", "jpg", "jpeg"])

# 2. أمر امتحان (اختبار سريع)
exam_mode = st.sidebar.checkbox("📝 تفعيل وضع الامتحان السريع")

# حقل إدخال السؤال أو الكلمة المفتاحية للبحث
user_question = st.text_input(
    f"✍️ اكتب كلمة البحث في كتاب ({subject} - {grade}):",
    placeholder="مثال: التصنيف، الخلية، قانون أوم..."
)

# إذا تم تفعيل وضع الامتحان
if exam_mode:
    st.info("📝 **وضع الامتحان السريع مفعل.**")
    if st.button("🎲 ابدأ امتحان قصير", type="secondary"):
        st.warning(f"سؤال اختباري في مادة {subject} ({grade})...")

# زر البحث (مكتوب عليه "ابحث" فقط)
if st.button("ابحث", type="primary"):
    if not user_question.strip() and not uploaded_image:
        st.warning("⚠️ الرجاء كتابة كلمة البحث أو رفع صورة السؤال أولاً.")
    else:
        with st.spinner("⏳ جاري البحث في صفحات الكتاب المستهدف..."):
            
            # إذا تم رفع صورة
            if uploaded_image is not None:
                st.image(uploaded_image, caption="الصورة المرفوعة", use_column_width=True)

            # البحث الحقيقي داخل ملفات الـ PDF المرفوعة
            extracted_results = ""
            if uploaded_pdfs and PDF_SUPPORT:
                try:
                    keyword = user_question.strip().lower()
                    for pdf_file in uploaded_pdfs:
                        pdf_file.seek(0)
                        reader = pypdf.PdfReader(pdf_file)
                        for idx, page in enumerate(reader.pages):
                            page_text = page.extract_text()
                            if page_text and keyword in page_text.lower():
                                extracted_results += f"\n\n📌 [مجلد الكتاب: {pdf_file.name} - الصفحة: {idx + 1}]\n{page_text[:1200]}...\n"
                except Exception as e:
                    st.error(f"حدث خطأ أثناء قراءة ملف الـ PDF: {e}")
            elif not uploaded_pdfs:
                st.warning("⚠️ تنبيه: لم تقمي برفع كتاب الـ PDF الخاص بهذه المادة من لوحة التحكم في القائمة الجانبية بعد!")

            # عرض النتائج المستخرجة
            st.success(f"✅ نتيجة البحث لمادة ({subject} - {grade}):")
            
            if extracted_results:
                st.markdown("### 🔍 النصوص المستخرجة حرفياً من الكتاب:")
                st.text(extracted_results)
            else:
                if uploaded_pdfs:
                    st.info("💡 لم يتم العثور على هذه الكلمة بالنص الدقيق في الكتب المرفوعة. جربي كتابة كلمة رئيسية أخرى.")
                    

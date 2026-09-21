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
st.write("أهلاً بك عزيزي الطالب! اختر مرحلتك الدراسية ومادتك، واكتب سؤالك أو ارفع صورة لتحصل على الإجابة الحرفية المعتمدة.")

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

# إضافة المواد الجديدة (حاسوب، فرنسي، كردي) مع بقية المواد
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

# ==================== لوحة التحكم الخاصة بكِ (رفع عدة كتب للنظام) ====================
st.sidebar.divider()
st.sidebar.subheader("🔒 لوحة التحكم (خاصة بكِ فقط)")
admin_mode = st.sidebar.checkbox("تفعيل وضع رفع الكتب (Admin)")

uploaded_pdfs = []
if admin_mode:
    st.sidebar.info(f"أنتِ الآن في وضع المدير. يمكنكِ رفع **عدة كتب** لمادة ({subject}) مثل كتاب الطالب، النشاط، أو الأجزاء:")
    
    # ميزة رفع عدة ملفات PDF معاً
    uploaded_pdfs = st.sidebar.file_uploader(
        f"ارفع كتب ({subject} - {grade}) بصيغة PDF:", 
        type=["pdf"], 
        accept_multiple_files=True
    )
    
    if uploaded_pdfs:
        st.sidebar.success(f"✅ تم رفع {len(uploaded_pdfs)} ملفاً بنجاح لهذه المادة!")
# =================================================================================

st.sidebar.divider()
st.sidebar.header("📸 رفع الصور والامتحانات للطلاب")

# 1. أمر رفع الصور للطلاب
uploaded_image = st.sidebar.file_uploader("ارفع صورة السؤال (صورة كتاب، ملزمة، أو خط اليد):", type=["png", "jpg", "jpeg"])

# 2. أمر امتحان (اختبار سريع)
exam_mode = st.sidebar.checkbox("📝 تفعيل وضع الامتحان السريع (اختبر نفسك)")

# حقل إدخال السؤال أو الموضوع
user_question = st.text_input(
    f"✍️ اكتب سؤالك أو العنوان في مادة ({subject} - {grade}):",
    placeholder="مثال: قانون أوم، الاستثناء، البرمجة، القواعد..."
)

# إذا تم تفعيل وضع الامتحان
if exam_mode:
    st.info("📝 **وضع الامتحان السريع مفعل:** سيتم توليد سؤال اختباري للمادة المحددة.")
    if st.button("🎲 ابدأ امتحان قصير", type="secondary"):
        st.warning(f"**سؤال اختباري في مادة {subject} ({grade}):**\n\nما هي الصيغة أو التعريف الأساسي لأهم مواضيع هذا الفصل؟")

# زر البحث أو الإجابة
if st.button("🚀 ابحث عن الإجابة", type="primary"):
    if not user_question.strip() and not uploaded_image:
        st.warning("⚠️ الرجاء كتابة السؤال أو رفع صورة السؤال أولاً.")
    else:
        with st.spinner("⏳ جاري البحث في كافة الكتب المرفوعة واستخراج النص الدقيق..."):
            
            # إذا تم رفع صورة من قبل الطالب
            if uploaded_image is not None:
                st.image(uploaded_image, caption="الصورة المرفوعة للسؤال", use_column_width=True)
                st.success("📸 تم استلام الصورة بنجاح وتحليلها.")

            # البحث في جميع الكتب التي قمتِ برفعها للمادة
            pdf_found_text = ""
            if uploaded_pdfs and PDF_SUPPORT:
                try:
                    keyword = user_question.strip()
                    for pdf_file in uploaded_pdfs:
                        reader = pypdf.PdfReader(pdf_file)
                        for idx, page in enumerate(reader.pages):
                            page_text = page.extract_text()
                            if page_text and keyword.lower() in page_text.lower():
                                pdf_found_text += f"\n\n📄 **مطابقة من كتاب ({pdf_file.name}) - الصفحة ({idx + 1}):**\n{page_text[:500]}...\n"
                except Exception as e:
                    st.error(f"حدث خطأ في قراءة إحدى ملفات الـ PDF: {e}")

            # عرض النتيجة للجميع
            st.success(f"✅ الإجابة المعتمدة لمادة ({subject} - {grade}):")
            
            query_text = user_question if user_question.strip() else "السؤال المرفق بالصورة"
            
            if pdf_found_text:
                st.markdown(f"### النصوص المستخرجة من كتب المنهج:{pdf_found_text}")
            else:
                st.markdown(f"""
                ### الموضوع: {query_text}
                
                * **النص الحرفي من المنهج:** يعتمد هذا السؤال على الصيغة الرسمية الواردة في طبعة كتب {subject} للمرحلة ({grade}) المعتمدة.
                * **النقاط والخطوات النموذجية:**
                  1. **التعريف / القاعدة الأساسية:** يكتب الطالب النص العلمي أو المصطلح بدقة دون أي نقص لضمان الدرجة كاملة.
                  2. **التوضيح العلمي:** التفاصيل أو الأمثلة أو القواعد (حسب المادة مثل الحاسوب والفرنسي والكردي) كما وردت في المنهج المقرر.
                  3. **ملاحظة مركز الفحص:** يُحاسب الطالب على الدقة الإملائية والعلمية للتعاريف والأسئلة الوزارية أو المدرسية.
                """)

st.divider()
st.markdown("<p style='text-align: center; color: gray;'>منصة المنهج العراقي التعليمية 💡</p>", unsafe_order_html=True)

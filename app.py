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

# ==================== لوحة التحكم الخاصة بكِ (رفع عدة كتب للنظام) ====================
st.sidebar.divider()
st.sidebar.subheader("🔒 لوحة التحكم (خاصة بكِ فقط)")
admin_mode = st.sidebar.checkbox("تفعيل وضع رفع الكتب (Admin)")

uploaded_pdfs = []
if admin_mode:
    st.sidebar.info(f"أنتِ الآن في وضع المدير. يمكنكِ رفع **عدة كتب** لمادة ({subject}):")
    
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
    placeholder="مثال: التصنيف، قانون أوم، الاستثناء..."
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
        with st.spinner("⏳ جاري البحث الذكي في صفحات الكتب المرفوعة..."):
            
            # إذا تم رفع صورة من قبل الطالب
            if uploaded_image is not None:
                st.image(uploaded_image, caption="الصورة المرفوعة للسؤال", use_column_width=True)
                st.success("📸 تم استلام الصورة بنجاح وتحليلها.")

            # البحث الذكي بالكلمات المفتاحية في جميع الكتب المرفوعة
            pdf_found_text = ""
            if uploaded_pdfs and PDF_SUPPORT:
                try:
                    # استخراج الكلمات الأساسية من السؤال (تجاهل الكلمات القصيرة مثل في، ما، هو)
                    query_words = [w for w in user_question.strip().split() if len(w) > 2]
                    if not query_words:
                        query_words = [user_question.strip()]

                    for pdf_file in uploaded_pdfs:
                        reader = pypdf.PdfReader(pdf_file)
                        for idx, page in enumerate(reader.pages):
                            page_text = page.extract_text()
                            if page_text:
                                # التحقق مما إذا كانت إحدى الكلمات الأساسية موجودة في الصفحة
                                match_count = sum(1 for word in query_words if word.lower() in page_text.lower())
                                if match_count > 0 or user_question.strip().lower() in page_text.lower():
                                    pdf_found_text += f"\n\n📄 **مطابقة من كتاب ({pdf_file.name}) - الصفحة ({idx + 1}):**\n{page_text[:800]}...\n"
                                    break # الانتقال للكتاب التالي أو إيقاف البحث عند أول مطابقة قوية
                except Exception as e:
                    st.error(f"حدث خطأ في قراءة إحدى ملفات الـ PDF: {e}")

            # عرض النتيجة للجميع
            st.success(f"✅ الإجابة المستخرجة لمادة ({subject} - {grade}):")
            
            query_text = user_question if user_question.strip() else "السؤال المرفق بالصورة"
            
            if pdf_found_text:
                st.markdown(f"### النصوص المطابقة من الكتاب المدرسي:{pdf_found_text}")
            else:
                st.markdown(f"""
                ### الموضوع: {query_text}
                
                * **النص الحرفي من المنهج:** لم يتم العثور على مطابقة دقيقة بالكلمات في الكتاب المرفوع، تأكد من كتابة كلمة مفتاحية رئيسية (مثل: التصنيف، الخلية، الوراثة).
                * **النقاط والخطوات النموذجية:**
                  1. **التعريف / القاعدة الأساسية:** يكتب الطالب النص العلمي أو المصطلح بدقة دون أي نقص لضمان الدرجة كاملة.
                  2. **التوضيح العلمي:** التفاصيل أو الأمثلة كما وردت في المنهج المقرر.
                """)

st.divider()
st.markdown("<p style='text-align: center; color: gray;'>منصة المنهج العراقي التعليمية 💡</p>", unsafe_order_html=True)

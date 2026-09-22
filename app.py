import streamlit as st
from groq import Groq

# =========================
# إعداد الصفحة
# =========================

st.set_page_config(
    page_title="مساعد المنهج العراقي",
    page_icon="📚",
    layout="wide"
)

# =========================
# Groq
# =========================

client = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)

# =========================
# تنسيق الواجهة
# =========================

st.markdown("""
<style>

.main-title{
    text-align:center;
    font-size:42px;
    font-weight:bold;
    margin-bottom:5px;
}

.subtitle{
    text-align:center;
    color:gray;
    margin-bottom:30px;
}

.answer-box{
    padding:20px;
    border-radius:15px;
    border:1px solid #dddddd;
    background:#f8f9fa;
}

</style>
""", unsafe_allow_html=True)

# =========================
# العنوان
# =========================

st.markdown(
    '<div class="main-title">📚 مساعد المنهج العراقي</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">اسألي أي سؤال دراسي واحصلي على شرح مبسط</div>',
    unsafe_allow_html=True
)

# =========================
# القائمة الجانبية
# =========================

with st.sidebar:

    st.header("🎓 المساعد الدراسي")

    st.info(
        """
يمكنكِ السؤال عن:

• الأحياء
• الكيمياء
• الفيزياء
• الرياضيات
• اللغة العربية
• اللغة الإنجليزية
"""
    )

# =========================
# السؤال
# =========================

question = st.text_area(
    "💬 اكتبي سؤالك:",
    placeholder="مثال: ما هو النظام البيئي؟",
    height=150
)

# =========================
# زر الإجابة
# =========================

if st.button("🚀 الحصول على الإجابة"):

    if not question.strip():

        st.warning("✏️ اكتبي سؤالًا أولًا.")

    else:

        with st.spinner("⏳ جاري إعداد الإجابة..."):

            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {
                        "role": "system",
                        "content": """
أنت مساعد دراسي للطلاب.

اشرح بطريقة مبسطة وواضحة.
استخدم العربية الفصحى السهلة.
رتب الإجابة بعناوين ونقاط.
إذا كان السؤال علمياً فاذكر التعريف والشرح.
"""
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ]
            )

            answer = response.choices[0].message.content

        st.success("✅ تم إنشاء الإجابة")

        st.markdown("## 📖 الإجابة")

        st.markdown(
            f"""
            <div class="answer-box">
            {answer}
            </div>
            """,
            unsafe_allow_html=True
        )
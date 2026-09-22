import streamlit as st
from groq import Groq
from datetime import date

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

TODAY = str(date.today())

if "day" not in st.session_state:
    st.session_state.day = TODAY

if "questions_count" not in st.session_state:
    st.session_state.questions_count = 0

if st.session_state.day != TODAY:
    st.session_state.day = TODAY
    st.session_state.questions_count = 0

# =========================
# الذاكرة
# =========================

if "history" not in st.session_state:
    st.session_state.history = []

# =========================
# تنسيق
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
    margin-bottom:25px;
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
    '<div class="subtitle">اسألي أي سؤال دراسي واحصلي على شرح مبسط واختبارات ومراجعة</div>',
    unsafe_allow_html=True
)

# =========================
# القائمة الجانبية
# =========================

with st.sidebar:

    st.header("🎓 المساعد الدراسي")

    subject = st.selectbox(
        "📚 اختاري المادة",
        [
            "عام",
            "الأحياء",
            "الكيمياء",
            "الفيزياء",
            "الرياضيات",
            "اللغة العربية",
            "اللغة الإنجليزية"
        ]
    )

    st.divider()

    remaining = 15 - st.session_state.questions_count

    st.markdown("### 📊 الاستخدام اليومي")
    st.write(f"المتبقي اليوم: {remaining}")

    st.markdown("### 🕒 آخر الأسئلة")

    if st.session_state.history:
        for q in st.session_state.history[-5:][::-1]:
            st.write("•", q)

    else:
        st.write("لا توجد أسئلة بعد")

    st.divider()

    if st.button("🗑️ مسح السجل"):

        st.session_state.history = []

        if "last_answer" in st.session_state:
            del st.session_state["last_answer"]

        st.rerun()


st.markdown("### ⚡ أسئلة سريعة")

c1, c2 = st.columns(2)

with c1:

    if st.button("🌍 ما هو النظام البيئي؟"):
        st.session_state["quick_question"] = "ما هو النظام البيئي؟"

with c2:

    if st.button("🌱 اشرح التمثيل الضوئي"):
        st.session_state["quick_question"] = "اشرح عملية التمثيل الضوئي"

default_question = st.session_state.get("quick_question", "")

# =========================
# السؤال
# =========================

question = st.text_area(
    "💬 اكتبي سؤالك:",
    value=default_question,
    placeholder="مثال: ما هو النظام البيئي؟",
    height=150
)


# =========================
# الحصول على الإجابة
# =========================

if st.button("🚀 الحصول على الإجابة"):

    if question.strip():

        with st.spinner("⏳ جاري إعداد الإجابة..."):
if st.session_state.questions_count >= 15:
    st.error("🚫 وصلتِ إلى الحد اليومي (15 سؤالاً)")
    st.stop()
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {
                        "role": "system",
                        "content": f"""
أنت مساعد دراسي متخصص في مادة {subject}.

- أجب بالعربية.
- استخدم لغة سهلة.
- ابدأ بتعريف مختصر.
- ثم شرح مبسط.
- ثم نقاط مهمة.
- اجعل الإجابة مناسبة لطلاب المدارس.
- صحح الأخطاء الإملائية البسيطة إن وجدت.
"""
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ]
            )

            answer = response.choices[0].message.content

        st.session_state["last_answer"] = answer
st.session_state.questions_count += 1
st.session_state.history.append(question)

        st.success("✅ تم إنشاء الإجابة")

        st.markdown("## 📖 الإجابة")

        st.write(answer)

st.markdown("### 📋 نسخة قابلة للنسخ")

st.text_area(
    "",
    answer,
    height=220
)

    else:

        st.warning("✏️ اكتبي سؤالاً أولاً.")

# =========================
# الميزات الإضافية
# =========================

if "last_answer" in st.session_state:

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        if st.button("📝 إنشاء اختبار"):

            with st.spinner("جاري إنشاء الاختبار..."):

                quiz = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {
                            "role": "system",
                            "content": """
أنشئ 5 أسئلة اختيار من متعدد.

لكل سؤال:
A)
B)
C)
D)

ثم اكتب الإجابات الصحيحة في النهاية.
"""
                        },
                        {
                            "role": "user",
                            "content": st.session_state["last_answer"]
                        }
                    ]
                )

            st.markdown("## 📝 الاختبار")

            st.write(
                quiz.choices[0].message.content
            )

    with col2:

        if st.button("📚 تلخيص"):

            with st.spinner("جاري التلخيص..."):

                summary = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {
                            "role": "system",
                            "content": """
لخص الموضوع.

اكتب:

📌 التعريف

📌 أهم النقاط

📌 ما يجب حفظه
"""
                        },
                        {
                            "role": "user",
                            "content": st.session_state["last_answer"]
                        }
                    ]
                )

            st.markdown("## 📚 الملخص")

            st.write(
                summary.choices[0].message.content
            )

    st.divider()

    col3, col4 = st.columns(2)

    with col3:

        if st.button("🧒 شرح أبسط"):

            with st.spinner("جاري تبسيط الشرح..."):

                easy = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {
                            "role": "system",
                            "content": """
اشرح الموضوع لطفل بعمر 12 سنة.

استخدم كلمات سهلة جداً.
"""
                        },
                        {
                            "role": "user",
                            "content": st.session_state["last_answer"]
                        }
                    ]
                )

            st.markdown("## 🧒 الشرح المبسط")

            st.write(
                easy.choices[0].message.content
            )

    with col4:

        if st.button("🎯 أسئلة مشابهة"):

            with st.spinner("جاري إنشاء الأسئلة..."):

                practice = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {
                            "role": "system",
                            "content": """
أنشئ 10 أسئلة تدريبية مشابهة للموضوع.

لا تكتب الإجابات.
"""
                        },
                        {
                            "role": "user",
                            "content": st.session_state["last_answer"]
                        }
                    ]
                )

            st.markdown("## 🎯 أسئلة تدريبية")

            st.write(
                practice.choices[0].message.content
            )
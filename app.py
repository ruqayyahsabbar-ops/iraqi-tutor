
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

client = Groq(api_key=st.secrets["GROQ_API_KEY"])
MODEL = "openai/gpt-oss-120b"
TODAY = str(date.today())

# =========================
# الذاكرة داخل الجلسة
# =========================

if "day" not in st.session_state:
    st.session_state.day = TODAY

if "questions_count" not in st.session_state:
    st.session_state.questions_count = 0

if st.session_state.day != TODAY:
    st.session_state.day = TODAY
    st.session_state.questions_count = 0

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""

if "quick_question" not in st.session_state:
    st.session_state.quick_question = ""

if "feature_results" not in st.session_state:
    st.session_state.feature_results = {}

# =========================
# تعليمات المساعد
# =========================

SYSTEM_PROMPT = """
أنت مساعد المنهج العراقي.

القواعد:

- أجب عن أسئلة المنهج العراقي والمواد الدراسية فقط.
- يمكنك الإجابة عن أسئلة تساعد الطالب على الدراسة مثل:
  • طرق المذاكرة
  • طرق الحفظ
  • تنظيم الوقت
  • الاستعداد للامتحانات
  • تحسين اللغة الإنجليزية
  • مهارات التعلم

- إذا كان السؤال خارج الدراسة والتعليم فاعتذر بلطف وقل:
"عذراً، أنا مخصص للمساعدة في الدراسة والمنهج العراقي فقط."

- استخدم لغة عربية سهلة وواضحة.
- اشرح المفاهيم بطريقة مبسطة تناسب الطلاب.
- لا تنسخ الكتاب حرفياً.
- حافظ على المعنى العلمي الصحيح.
- لا تضف تفاصيل جامعية أو معلومات متقدمة غير ضرورية.

إذا كان السؤال علمياً أو من المنهج:
رتب الإجابة بالشكل التالي:

📌 التعريف

📖 الشرح المبسط

📝 أهم النقاط

أما إذا كان السؤال عن الدراسة أو الحفظ أو تنظيم الوقت
أو الامتحانات أو التركيز أو تطوير اللغة الإنجليزية:

- لا تستخدم التعريف.
- تحدث بلطف وبأسلوب مشجع.
- قدم نصائح عملية ومباشرة.
- اجعل الإجابة سهلة الفهم.
"""

# =========================
# تنسيق الواجهة
# =========================

st.markdown("""
<style>
.main-title {
    text-align: center;
    font-size: 38px;
    font-weight: bold;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    color: gray;
    margin-bottom: 25px;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="main-title">📚 مساعد المنهج العراقي</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">مساعدك الدراسي من الأول المتوسط إلى السادس الإعدادي</div>',
    unsafe_allow_html=True
)

# =========================
# القائمة الجانبية
# =========================


with st.sidebar:

    st.header("🎓 المساعد الدراسي")

    # اختيار الصف
    grade = st.selectbox(
        "🎓 اختاري الصف الدراسي",
        [
            "الأول الابتدائي",
            "الثاني الابتدائي",
            "الثالث الابتدائي",
            "الرابع الابتدائي",
            "الخامس الابتدائي",
            "السادس الابتدائي",
            "الأول المتوسط",
            "الثاني المتوسط",
            "الثالث المتوسط",
            "الرابع الإعدادي",
            "الخامس الإعدادي",
            "السادس الإعدادي"
        ]
    )

    # اختيار الفرع
    branch = "غير محدد"

    if grade in [
        "الرابع الإعدادي",
        "الخامس الإعدادي",
        "السادس الإعدادي"
    ]:
        branch = st.selectbox(
            "🔬 اختاري الفرع الدراسي",
            ["العلمي", "الأدبي"]
        )

    # اختيار المادة
    subject = st.selectbox(
        "📚 اختاري المادة",
        [
            "عام",
            "التربية الإسلامية",
            "اللغة العربية",
            "اللغة الإنجليزية",
            "الرياضيات",
            "العلوم",
            "الأحياء",
            "الكيمياء",
            "الفيزياء",
            "الاجتماعيات",
            "التاريخ",
            "الجغرافية",
            "الاقتصاد",
            "الحاسوب"
        ]
    )

    st.divider()

    remaining = 15 - st.session_state.questions_count

    st.markdown("### 📊 الاستخدام اليومي")
    st.write(f"المتبقي اليوم: {remaining}")

    st.markdown("### 🕒 آخر الأسئلة")

    user_questions = [
        msg["content"]
        for msg in st.session_state.messages
        if msg["role"] == "user"
    ]

    if user_questions:
        for q in user_questions[-5:][::-1]:
            st.write("•", q)
    else:
        st.write("لا توجد أسئلة بعد")

    st.divider()

    if st.button("🗑️ مسح المحادثة", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_answer = ""
        st.session_state.feature_results = {}
        st.rerun()

# =========================
# الأسئلة السريعة
# =========================

st.markdown("### ⚡ أسئلة سريعة")

c1, c2 = st.columns(2)

with c1:
    if st.button("🌍 ما هو النظام البيئي؟"):
        st.session_state.quick_question = "ما هو النظام البيئي؟"

with c2:
    if st.button("🌱 اشرح التمثيل الضوئي"):
        st.session_state.quick_question = "اشرح عملية التمثيل الضوئي"

# =========================
# عرض المحادثة السابقة
# =========================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# =========================
# استقبال السؤال
# =========================

quick_question = st.session_state.quick_question
st.session_state.quick_question = ""

question = st.chat_input("اكتبي سؤالك الدراسي هنا...")

if quick_question:
    question = quick_question

# =========================
# معالجة السؤال
# =========================

if question:

    if not question.strip():
        st.warning("اكتبي سؤالاً أولاً.")

    elif st.session_state.questions_count >= 15:
        st.error("🚫 وصلتِ إلى الحد اليومي (15 سؤالاً).")

    else:

        conversation = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
                + f"\nالصف الدراسي: {grade}"
                + f"\nالفرع الدراسي: {branch}"
                + f"\nالمادة الدراسية: {subject}"
                + "\nراعِ مستوى الصف والفرع عند الشرح."
                + "\nلا تخلط بين مناهج الصفوف أو الفروع المختلفة."
            }
        ]

        conversation.extend(st.session_state.messages)

        conversation.append({
            "role": "user",
            "content": question
        })

        try:

            with st.spinner("⏳ جاري إعداد الإجابة..."):

                response = client.chat.completions.create(
                    model=MODEL,
                    messages=conversation
                )

                answer = response.choices[0].message.content

            st.session_state.messages.append({
                "role": "user",
                "content": question
            })

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer
            })

            st.session_state.last_answer = answer
            st.session_state.questions_count += 1
            st.session_state.feature_results = {}

            with st.chat_message("user"):
                st.markdown(question)

            with st.chat_message("assistant"):
                st.markdown(answer)

        except Exception as e:
            st.error(
                "حدث خطأ أثناء إعداد الإجابة. "
                "تحققي من الاتصال وحاولي مرة أخرى."
            )

 

=========================
# الميزات الإضافية
# =========================

if st.session_state.last_answer:

    st.divider()
    st.markdown("### ✨ أدوات المراجعة")

    col1, col2 = st.columns(2)

    with col1:

        if st.button("📝 إنشاء اختبار", use_container_width=True):

            with st.spinner("جاري إنشاء الاختبار..."):

                try:

                    result = client.chat.completions.create(
                        model=MODEL,
                        messages=[
                            {
                                "role": "system",
                                "content": """
إذا كان النص موضوعاً علمياً أو دراسياً
من المنهج العراقي، أنشئ 5 أسئلة اختيار من متعدد.

أما إذا كان نصيحة دراسية فاكتب فقط:

هذه الإجابة عبارة عن نصيحة دراسية،
لذلك لا يمكن إنشاء اختبار لها.

لكل سؤال اكتب:
A)
B)
C)
D)

ثم اكتب الإجابات الصحيحة في النهاية.
"""
                            },
                            {
                                "role": "user",
                                "content": st.session_state.last_answer
                            }
                        ]
                    )

                    st.session_state.feature_results["quiz"] = (
                        result.choices[0].message.content
                    )

                except Exception:
                    st.error("حدث خطأ أثناء إنشاء الاختبار.")

    with col2:

        if st.button("📚 تلخيص", use_container_width=True):

            with st.spinner("جاري التلخيص..."):

                try:

                    result = client.chat.completions.create(
                        model=MODEL,
                        messages=[
                            {
                                "role": "system",
                                "content": """
إذا كان النص موضوعاً دراسياً أو علمياً فقم بتلخيصه.

أما إذا كان نصيحة دراسية فاكتب فقط:

هذه الإجابة عبارة عن نصيحة دراسية،
لذلك لا يمكن تلخيصها.
"""
                            },
                            {
                                "role": "user",
                                "content": st.session_state.last_answer
                            }
                        ]
                    )

                    st.session_state.feature_results["summary"] = (
                        result.choices[0].message.content
                    )

                except Exception:
                    st.error("حدث خطأ أثناء التلخيص.")

    col3, col4 = st.columns(2)

    with col3:

        if st.button("🧒 شرح أبسط", use_container_width=True):

            with st.spinner("جاري تبسيط الشرح..."):

                try:

                    result = client.chat.completions.create(
                        model=MODEL,
                        messages=[
                            {
                                "role": "system",
                                "content": """
اشرح الموضوع لطفل بعمر 12 سنة.
استخدم كلمات سهلة جداً.
حافظ على المعنى العلمي الصحيح.
"""
                            },
                            {
                                "role": "user",
                                "content": st.session_state.last_answer
                            }
                        ]
                    )

                    st.session_state.feature_results["easy"] = (
                        result.choices[0].message.content
                    )

                except Exception:
                    st.error("حدث خطأ أثناء تبسيط الشرح.")

    with col4:

        if st.button("🎯 أسئلة مشابهة", use_container_width=True):

            with st.spinner("جاري إنشاء الأسئلة..."):

                try:

                    result = client.chat.completions.create(
                        model=MODEL,
                        messages=[
                            {
                                "role": "system",
                                "content": """
إذا كان النص موضوعاً علمياً أو دراسياً
فأنشئ 10 أسئلة تدريبية مشابهة.

أما إذا كان نصيحة دراسية فاكتب فقط:

هذه الإجابة عبارة عن نصيحة دراسية،
لذلك لا يمكن إنشاء أسئلة مشابهة لها.
"""
                            },
                            {
                                "role": "user",
                                "content": st.session_state.last_answer
                            }
                        ]
                    )

                    st.session_state.feature_results["practice"] = (
                        result.choices[0].message.content
                    )

                except Exception:
                    st.error("حدث خطأ أثناء إنشاء الأسئلة.")

# =========================
# عرض نتائج أدوات المراجعة
# =========================

feature_titles = {
    "quiz": "📝 الاختبار",
    "summary": "📚 الملخص",
    "easy": "🧒 الشرح المبسط",
    "practice": "🎯 الأسئلة التدريبية"
}

for key, title in feature_titles.items():

    if key in st.session_state.feature_results:

        st.markdown(f"## {title}")

        st.markdown(
            st.session_state.feature_results[key]
        )

# =========================
# الملاحظات والاقتراحات
# =========================

st.divider()

st.link_button(
    "💡 إرسال ملاحظة أو اقتراح",
    "https://docs.google.com/forms/d/e/1FAIpQLSfAqyQPLVLQHM6nxyjR6M5k0VWttnohPVSH5ktaojDK7vhMIQ/viewform?usp=publish-editor"
)

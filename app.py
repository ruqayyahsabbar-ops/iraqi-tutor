import streamlit as st
import google.generativeai as genai
import PIL.Image

# إعدادات الصفحة
st.set_page_config(
    page_title="مساعد المنهج العراقي",
    page_icon="📚",
    layout="centered"
)

# قراءة المفتاح من الـ Secrets بأمان
if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ الرجاء تعيين مفتاح GEMINI_API_KEY في إعدادات Secrets على Streamlit.")

# استخدام الموديل المدعوم والسريع
model_name = 'gemini-3.6-flash'

# عنوان التطبيق
st.title("📚 مساعد المنهج العراقي الذكي")
st.write("أهلاً بكِ! أنا مساعدكِ الذكي لجميع المواد الدراسية للمنهج العراقي.")

st.divider()

# منطقة إدخال السؤال النصي
user_question = st.text_input("✍️", placeholder="اكتب سؤالك الدراسي هنا...")

# ميزة رفع الصور
uploaded_image = st.file_uploader("📷 ارفع صورة المسألة أو الصفحة الدراسية (اختياري)", type=["jpg", "jpeg", "png"])

# زر إرسال السؤال
if st.button("🚀 إرسال", type="primary"):
    if not user_question.strip() and not uploaded_image:
        st.warning("⚠️ الرجاء كتابة سؤالك أولاً أو إرفاق صورة قبل الضغط على الزر.")
    else:
        with st.spinner("⏳ جاري الإجابة..."):
            try:
                model = genai.GenerativeModel(model_name)
                
                if uploaded_image is not None:
                    image = PIL.Image.open(uploaded_image)
                    prompt_text = user_question.strip() if user_question.strip() else "اشرح هذه الصورة الدراسية بالتفصيل"
                    response = model.generate_content([prompt_text, image])
                else:
                    prompt_text = f"أنت أستاذ عراقي ذكي ومساند لوزارة التربية العراقية. اشرح الموضوع بوضوح، وفي نهاية شرحك، اقترح على الطالب باختصار شديد إجراء امتحان قصير (3 أسئلة) حول ما شرحته للتو.\n\nالسؤال: {user_question}"
                    response = model.generate_content(prompt_text)
                
                st.session_state["last_explanation"] = response.text
                st.success("💡 إليك الإجابة النموذجية:")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"حدث خطأ: {e}")

# ميزة الامتحانات التفاعلية التلقائية
if "last_explanation" in st.session_state:
    st.divider()
    st.subheader("📝 اختبار قصير فوري")
    st.write("هل ترغبين باختبار نفسكِ حول الموضوع الذي تم شرحه للتو؟")
    
    if st.button("💡 نعم، ابدأ الامتحان القصير"):
        with st.spinner("⏳ جاري إعداد الأسئلة..."):
            try:
                quiz_model = genai.GenerativeModel(model_name)
                quiz_prompt = f"بناءً على الشرح التالي الذي قدمناه للتو، اصنع امتحان قصير من 3 أسئلة اختيار من متعدد أو أسئلة قصيرة للطالب، واجعل الأسئلة واضحة:\n\n{st.session_state['last_explanation']}"
                
                quiz_response = quiz_model.generate_content(quiz_prompt)
                st.markdown("### أسئلة الاختبار:")
                st.markdown(quiz_response.text)
            except Exception as e:
                st.error(f"حدث خطأ أثناء توليد الامتحان: {e}")

# ذيل الصفحة
st.divider()
st.markdown("<p style='text-align: center; color: gray;'>مصممة بملكة البرمجة 💡</p>", unsafe_allow_html=True)

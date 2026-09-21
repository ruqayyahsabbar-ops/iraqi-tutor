import streamlit as st
import google.generativeai as genai
import PIL.Image

# إعدادات الصفحة
st.set_page_config(
    page_title="مساعد المنهج العراقي",
    page_icon="📚",
    layout="centered"
)

# الشريط الجانبي لإدخال المفتاح بأمان
st.sidebar.header("⚙️ إعدادات الاتصال")
api_key_input = st.sidebar.text_input("أدخل مفتاح Gemini API هنا:", type="password")

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
    if not api_key_input:
        st.error("⚠️ الرجاء إدخال مفتاح الـ API في الشريط الجانبي أولاً!")
    elif not user_question.strip() and not uploaded_image:
        st.warning("⚠️ الرجاء كتابة سؤالك أولاً أو إرفاق صورة قبل الضغط على الزر.")
    else:
        with st.spinner("⏳ جاري الإجابة..."):
            try:
                # إعداد المكتبة الرسمية بالمفتاح المُدخل
                genai.configure(api_key=api_key_input)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt_text = f"أنت أستاذ عراقي ذكي ومساند لوزارة التربية العراقية. اشرح الموضوع بوضوح، وفي نهاية شرحك، اقترح على الطالب باختصار شديد إجراء امتحان قصير (3 أسئلة) حول ما شرحته للتو.\n\nالسؤال: {user_question}"
                
                if uploaded_image:
                    image = PIL.Image.open(uploaded_image)
                    response = model.generate_content([prompt_text, image])
                else:
                    response = model.generate_content(prompt_text)
                
                answer = response.text
                
                if answer:
                    st.success("💡 إليك الإجابة النموذجية:")
                    st.markdown(answer)
            except Exception as e:
                st.error(f"حدث خطأ في الاتصال: {e}")

# ذيل الصفحة
st.divider()
st.markdown("<p style='text-align: center; color: gray;'>مصممة بملكة البرمجة 💡</p>", unsafe_allow_html=True)

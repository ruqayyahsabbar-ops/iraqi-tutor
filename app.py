import streamlit as st
import google.generativeai as genai
import PIL.Image

# إعدادات الصفحة
st.set_page_config(
    page_title="مساعد المنهج العراقي",
    page_icon="📚",
    layout="centered"
)

# ضعي أحد مفاتيح أختكِ الجديدة هنا للتجربة المباشرة
API_KEY = "AQ.Ab8RN6J5QzzPXz-DoVz3w2tk0YlN62HTw7n0w0G1yt7GujucVw"

# استخدام نموذج gemini-1.5-flash الأثبت والأكثر استقراراً حالياً
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

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
                # هنا سيظهر الخطأ الحقيقي بالكامل لنعرف سببه بدقة
                st.error(f"⚠️ تفاصيل الخطأ الفعلي: {e}")

# ذيل الصفحة
st.divider()
st.markdown("<p style='text-align: center; color: gray;'>مصممة بملكة البرمجة 💡</p>", unsafe_allow_html=True)

import streamlit as st
import google.generativeai as genai
import PIL.Image

# إعدادات الصفحة
st.set_page_config(
    page_title="مساعد المنهج العراقي",
    page_icon="📚",
    layout="centered"
)

# التحقق من مفتاح API من إعدادات Secrets في Streamlit
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ الرجاء تعيين مفتاح GEMINI_API_KEY في إعدادات Secrets على منصة Streamlit.")

# عنوان التطبيق
st.title("📚 مساعد المنهج العراقي الذكي")
st.write("أهلاً بكِ! أنا مساعدكِ الذكي لمساعدة لجميع المواد الدراسية للمنهج العراقي.")

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
        with st.spinner("... جاري التفكير والبحث في المنهج الدراسي"):
            try:
                # استخدام النموذج المستقر والمدعم لل النصوص
                model = genai.GenerativeModel('gemini-pro')
                
                # تجهيز محتوى الطلب (Prompt)
                prompt_text = "أنت أستاذ عراقي ذكي ومساند لوزارة التربية العراقية. اشرح الموضوع بوضوح، وفي نهاية شرحك، اقترح على الطالب باختصار شديد إجراء امتحان قصير (3 أسئلة) حول ما شرحته للتو.\n\nالسؤال: " + user_question
                
                # إذا كانت هناك صورة مرفوعة، نستخدم نموذج يدعم الصور مثل gemini-pro-vision أو نمررها بالطريقة المتوافقة
                if uploaded_image is not None:
                    image = PIL.Image.open(uploaded_image)
                    # لضمان عدم حدوث خطأ مع الصور، سنستخدم النموذج المخصص للرؤية إذا تطلب الأمر، أو نمرر الصورة مع gemini-pro
                    vision_model = genai.GenerativeModel('gemini-pro-vision')
                    response = vision_model.generate_content([user_question if user_question else "اشرح هذه الصورة الدراسية", image])
                else:
                    response = model.generate_content(prompt_text)
                
                # حفظ الإجابة في الجلسة لاستخدامها في الامتحان
                st.session_state["last_explanation"] = response.text
                
                st.success("💡 إليك الإجابة النموذجية:")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"حدث خطأ أثناء الاتصال بالمنصة: {e}")

# ميزة الامتحانات التفاعلية التلقائية بناءً على الشرح السابق
if "last_explanation" in st.session_state:
    st.divider()
    st.subheader("📝 اختبار قصير فوري")
    st.write("هل ترغبين باختبار نفسكِ حول الموضوع الذي تم شرحه للتو؟")
    
    if st.button("💡 نعم، ابدأ الامتحان القصير"):
        with st.spinner("جاري إعداد الأسئلة..."):
            try:
                quiz_model = genai.GenerativeModel('gemini-pro')
                quiz_prompt = f"بناءً على الشرح التالي الذي قدمناه للتو، اصنع امتحان قصير من 3 أسئلة اختيار من متعدد أو أسئلة قصيرة للطالب، واجعل الأسئلة واضحة:\n\n{st.session_state['last_explanation']}"
                
                quiz_response = quiz_model.generate_content(quiz_prompt)
                st.markdown("### أسئلة الاختبار:")
                st.markdown(quiz_response.text)
            except Exception as e:
                st.error(f"حدث خطأ أثناء توليد الامتحان: {e}")

# ذيل الصفحة
st.divider()
st.markdown("<p style='text-align: center; color: gray;'>مصممة بملكة البرمجة 💡</p>", unsafe_allow_html=True)
                

import streamlit as st
import google.generativeai as genai
import PIL.Image

# إعدادات الصفحة
st.set_page_config(
    page_title="مساعد المنهج العراقي",
    page_icon="📚",
    layout="centered"
)

# جلب المفاتيح المتعددة من الـ Secrets بأمان
def get_api_keys():
    keys = []
    for i in range(1, 6):
        key_name = "GEMINI_API_KEY" if i == 1 else f"GEMINI_API_KEY_{i}"
        if key_name in st.secrets and st.secrets[key_name]:
            keys.append(st.secrets[key_name])
    return keys

# دالة التدوير السريع باستخدام النموذج المحدث والمدعوم
def generate_with_rotation(prompt_or_contents):
    keys = get_api_keys()
    
    if not keys:
        st.error("⚠️ الرجاء تعيين مفاتيح الـ API في إعدادات Secrets.")
        return None

    # استخدام أحدث نموذج فلاش مدعوم وسريع
    model_name = 'gemini-2.5-flash'

    for key in keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt_or_contents)
            return response
        except Exception as e:
            error_str = str(e)
            # إذا نفد رصيد المفتاح الحالي، انتقل للمفتاح التالي فوراً
            if "429" in error_str or "quota" in error_str.lower():
                continue
            else:
                # إذا ظهر خطأ آخر غير النفاد، جرب المفتاح التالي أو أظهر الخطأ إذا انتهت المفاتيح
                if key == keys[-1]:
                    raise e
                continue
                
    st.error("⚠️ عذراً، ضغط شديد مؤقت على جميع المفاتيح. يرجى الانتظار ثوانٍ معدودة والمحاولة.")
    return None

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
                    content_payload = [prompt_text, image]
                else:
                    content_payload = f"أنت أستاذ عراقي ذكي ومساند لوزارة التربية العراقية. اشرح الموضوع بوضوح، وفي نهاية شرحك، اقترح على الطالب باختصار شديد إجراء امتحان قصير (3 أسئلة) حول ما شرحته للتو.\n\nالسؤال: {user_question}"
                
                response = generate_with_rotation(content_payload)
                
                if response:
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
                quiz_prompt = f"بناءً على الشرح التالي الذي قدمناه للتو، اصنع امتحان قصير من 3 أسئلة اختيار من متعدد أو أسئلة قصيرة للطالب، واجعل الأسئلة واضحة:\n\n{st.session_state['last_explanation']}"
                
                quiz_response = generate_with_rotation(quiz_prompt)
                if quiz_response:
                    st.markdown("### أسئلة الاختبار:")
                    st.markdown(quiz_response.text)
            except Exception as e:
                st.error(f"حدث خطأ أثناء توليد الامتحان: {e}")

# ذيل الصفحة
st.divider()
st.markdown("<p style='text-align: center; color: gray;'>مصممة بملكة البرمجة 💡</p>", unsafe_allow_html=True)
        

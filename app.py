import streamlit as st
import google.generativeai as genai
import PIL.Image

# إعدادات الصفحة
st.set_page_config(
    page_title="مساعد المنهج العراقي",
    page_icon="📚",
    layout="centered"
)

# قائمة المفاتيح المتعددة في الخلفية (نظام التدوير التلقائي للثلاثة مفاتيح)
def get_api_keys():
    keys = []
    # البحث عن المفاتيح المخزنة في Streamlit Secrets (يدعم حتى 5 مفاتيح)
    for i in range(1, 6):
        key_name = "GEMINI_API_KEY" if i == 1 else f"GEMINI_API_KEY_{i}"
        if key_name in st.secrets and st.secrets[key_name]:
            keys.append(st.secrets[key_name])
    return keys

# دالة ذكية لاختيار مفتاح يعمل تلقائياً والتبديل عند الحاجة
def generate_with_rotation(prompt_or_contents, model_name='gemini-3.6-flash'):
    keys = get_api_keys()
    
    if not keys:
        st.error("⚠️ الرجاء تعيين مفاتيح الـ API في إعدادات Secrets.")
        return None

    # تجربة المفاتيح تباعاً إذا فشل أحدها بسبب نفاد الحصة (429)
    for idx, key in enumerate(keys):
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt_or_contents)
            return response
        except Exception as e:
            error_str = str(e)
            # إذا كان الخطأ بسبب نفاد الحصة (429)، ننتقل للمفتاح التالي فوراً
            if "429" in error_str or "quota" in error_str.lower():
                continue
            else:
                # إذا كان خطأ آخر، نعرضه للمستخدم
                raise e
                
    # إذا نفدت جميع المفاتيح في نفس اللحظة
    st.error("⚠️ تم استنفاد الحد الأقصى لجميع المفاتيح المؤقتة حالياً. يرجى الانتظار قليلاً ثم المحاولة.")
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
        with st.spinner("... جاري التفكير والبحث في المنهج الدراسي"):
            try:
                # تجهيز المحتوى بناءً على وجود صورة أو نص
                if uploaded_image is not None:
                    image = PIL.Image.open(uploaded_image)
                    prompt_text = user_question.strip() if user_question.strip() else "اشرح هذه الصورة الدراسية بالتفصيل"
                    content_payload = [prompt_text, image]
                else:
                    content_payload = f"أنت أستاذ عراقي ذكي ومساند لوزارة التربية العراقية. اشرح الموضوع بوضوح، وفي نهاية شرحك، اقترح على الطالب باختصار شديد إجراء امتحان قصير (3 أسئلة) حول ما شرحته للتو.\n\nالسؤال: {user_question}"
                
                # استخدام نظام التدوير الذكي للمفاتيح الثلاثة
                response = generate_with_rotation(content_payload)
                
                if response:
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

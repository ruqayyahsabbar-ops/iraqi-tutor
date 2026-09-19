import streamlit as st
import google.generativeai as genai

# إعدادات الصفحة
st.set_page_config(
    page_title="مساعد المنهج العراقي",
    page_icon="📚",
    layout="centered"
)

# التحقق من وجود مفتاح الـ API وسحبه من الأسرار بأمان
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("الرجاء إضافة مفتاح GEMINI_API_KEY في إعدادات Secrets على منصة Streamlit.")

# عنوان التطبيق
st.title("📚 مساعد المنهج العراقي الذكي")
st.write("أهلاً بك يا بطل! أنا مساعدك الذكي المخصص للإجابة بدقة على جميع أسئلة المنهج الدراسي العراقي.")

# صندوق إدخال السؤال
st.divider()
user_question = st.text_input("اكتب سؤالك الدراسي هنا:", placeholder="مثلاً: اشرح قانون أوم في الفيزياء، أو ما هي أهم أحداث ثورة العشرين...")

# زر إرسال السؤال والاتصال بالذكاء الاصطناعي
if st.button("اسأل المساعد", type="primary"):
    if not user_question.strip():
        st.warning("الرجاء كتابة سؤالك أولاً قبل الضغط على الزر.")
    else:
        with st.spinner("جاري التفكير والبحث في المنهج الدراسي..."):
            try:
                # تهيئة النموذج مع توجيهه ليكون متخصصاً بالمنهج العراقي
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction="أنت مساعد تعليمي ذكي ومتخصص حصرياً في المنهج الدراسي العراقي لجميع المراحل (الابتدائية، المتوسطة، الإعدادية). قدم إجابات علمية دقيقة، واضحة، ومنظمة، ومطابقة للمناهج المقررة في وزارة التربية العراقية."
                )
                
                # إرسال السؤال للنموذج واستقبال الإجابة
                response = model.generate_content(user_question)
                
                # عرض الإجابة
                st.success("إليك الإجابة النموذجية:")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"حدث خطأ أثناء الاتصال بالمساعد: {e}")

# تذيل الصفحة
st.divider()
st.markdown("<p style='text-align: center; color: gray;'>تم تطوير هذا التطبيق خصيصاً لطلبة العراق 🇮🇶</p>", unsafe_allow_html=True)

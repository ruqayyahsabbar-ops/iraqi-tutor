import streamlit as st
import google.generativeai as genai

# إعدادات الصفحة
st.set_page_config(
    page_title="مساعد المنهج العراقي الذكي",
    page_icon="📚",
    layout="centered"
)

# عنوان التطبيق
st.title("📚 مساعد المنهج العراقي الذكي")
st.write("أهلاً بكِ! هذا المساعد متصل بالذكاء الاصطناعي لجلب النصوص الحرفية والوزارية المعتمدة للمنهج العراقي.")

st.divider()

# منطقة إدخال السؤال الدراسي
user_question = st.text_input("✍️ اكتب سؤالك الدراسي أو عنوان الموضوع هنا (مثل: شرح قانون أوم):", placeholder="اكتب السؤال هنا...")

# زر إرسال السؤال
if st.button("🚀 توليد الإجابة الحرفية من المنهج", type="primary"):
    if not user_question.strip():
        st.warning("⚠️ الرجاء كتابة سؤالك الدراسي أولاً قبل الضغط على الزر.")
    else:
        with st.spinner("⏳ جاري الاتصال بالذكاء الاصطناعي وجلب النص الحرفي للمنهج العراقي..."):
            try:
                # سحب مفتاح الـ API الصحيح (الذي يبدأ بـ AIzaSy) من إعدادات Secrets
                gemini_api_key = st.secrets.get("GEMINI_API_KEY", "")
                
                if not gemini_api_key:
                    st.error("⚠️ تنبيه: يرجى إضافة مفتاح `GEMINI_API_KEY` في إعدادات Secrets الخاصة بـ Streamlit أولاً.")
                else:
                    # تفعيل المفتاح والاتصال بمكتبة جيميناي الرسمية
                    genai.configure(api_key=gemini_api_key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    # توجيه دقيق للذكاء الاصطناعي ليلتزم حصراً بالمنهج العراقي وبشكل حرفي
                    prompt_text = f"""
                    أنت أستاذ ومساعد خبير في المنهج الدراسي العراقي لوزارة التربية.
                    المطلوب منك إعطاء النص العلمي أو القانون أو التعريف **حرفياً** تماماً كما ورد في كتاب المنهج العراقي الرسمي. لا تقم بالتلخيص المخل، بل أعط النص الدقيق المعتمد في المدارس العراقية للسؤال التالي:
                    
                    {user_question}
                    """
                    
                    response = model.generate_content(prompt_text)
                    answer = response.text
                    
                    if answer:
                        st.success("💡 النص الحرفي والوزاري المستخرج من المنهج العراقي:")
                        st.markdown(answer)
                    else:
                        st.warning("⚠️ لم يتم استرجاع إجابة، يرجى المحاولة مرة أخرى.")
                        
            except Exception as e:
                st.error(f"حدث خطأ في الاتصال: {e}")
                st.info("تأكدِ أن المفتاح المخزن في Secrets هو مفتاح Gemini API الصحيح (يبدأ بـ AQ).")

# ذيل الصفحة
st.divider()
st.markdown("<p style='text-align: center; color: gray;'>مصممة بملكة البرمجة 💡</p>", unsafe_allow_html=True)

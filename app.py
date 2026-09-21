import streamlit as st
import google.generativeai as genai
import PIL.Image

# إعدادات الصفحة
st.set_page_config(
    page_title="مساعد المنهج العراقي الذكي",
    page_icon="📚",
    layout="centered"
)

# الشريط الجانبي لإدخال المفتاح الحقيقي بأمان
st.sidebar.header("⚙️ إعدادات الاتصال الذكي")
st.sidebar.markdown("أدخلي مفتاح Gemini API الحقيقي (يبدأ بـ AIzaSy):")
api_key_input = st.sidebar.text_input("مفتاح الـ API:", type="password")

# عنوان التطبيق
st.title("📚 مساعد المنهج العراقي الذكي")
st.write("أهلاً بكِ! أنا مساعدكِ الذكي لجلب النصوص الحرفية والشروحات الدقيقة من المناهج المقررة لوزارة التربية العراقية.")

st.divider()

# منطقة إدخال السؤال
user_question = st.text_input("✍️ اكتب سؤالك الدراسي هنا (مثل: شرح قانون أوم):", placeholder="اكتب السؤال هنا...")

# ميزة رفع الصور (للأسئلة المصورة)
uploaded_image = st.file_uploader("📷 أو ارفع صورة المسألة أو الصفحة الدراسية (اختياري):", type=["jpg", "jpeg", "png"])

# زر إرسال السؤال
if st.button("🚀 توليد الإجابة الحرفية", type="primary"):
    if not api_key_input:
        st.error("⚠️ الرجاء إدخال مفتاح الـ API الصحيح في الشريط الجانبي (Sidebar) أولاً!")
    elif not user_question.strip() and not uploaded_image:
        st.warning("⚠️ الرجاء كتابة سؤالك الدراسي أو إرفاق صورة قبل الضغط على الزر.")
    else:
        with st.spinner("⏳ جاري البحث في المنهج العراقي وإعداد الإجابة الدقيقة..."):
            try:
                # تفعيل المفتاح المدخل
                genai.configure(api_key=api_key_input)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # توجيه ذكي للذكاء الاصطناعي ليلتزم بنصوص المنهج العراقي حرفياً
                system_prompt = """
                أنت أستاذ ومساعد خبير في المنهج الدراسي العراقي لوزارة التربية. 
                عندما يطرح الطالب سؤالاً، يجب عليك:
                1. تقديم النص العلمي أو القانون أو التعريف **حرفياً** كما ورد في كتاب المنهج العراقي الرسمي.
                2. شرح الخطوات بأسلوب تربوي مبسط ومناسب للطلاب.
                3. ذكر رقم الفصل أو السياق الوزاري إن أمكن.
                """
                
                full_prompt = f"{system_prompt}\n\nسؤال الطالب: {user_question}"
                
                if uploaded_image:
                    image = PIL.Image.open(uploaded_image)
                    response = model.generate_content([full_prompt, image])
                else:
                    response = model.generate_content(full_prompt)
                
                answer = response.text
                
                if answer:
                    st.success("💡 الإجابة النموذجية من المنهج العراقي:")
                    st.markdown(answer)
                    
            except Exception as e:
                st.error(f"حدث خطأ في الاتصال أو المفتاح: {e}")
                st.info("تأكد أن المفتاح الذي أدخلته في الشريط الجانبي هو مفتاح API صالح ويبدأ بـ AIzaSy.")

# ذيل الصفحة
st.divider()
st.markdown("<p style='text-align: center; color: gray;'>مصممة بملكة البرمجة 💡</p>", unsafe_allow_html=True)

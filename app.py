import streamlit as st
import requests
import json
import PIL.Image
import io

# إعدادات الصفحة
st.set_page_config(
    page_title="مساعد المنهج العراقي",
    page_icon="📚",
    layout="centered"
)

# الرمز الخاص بكِ
TOKEN = "AQ.Ab8RN6KV-Cw9PBQnvA4FBixA0S00uRKe9MYnweo1UvOTH4_BQQ"

def call_gemini_rest(prompt_text):
    # رابط الاتصال المباشر لخدمة جيميناي
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt_text}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            res_json = response.json()
            return res_json['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"خطأ في الاتصال (رمز الاستجابة {response.status_code}): {response.text}"
    except Exception as e:
        return f"حدث خطأ: {e}"

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
            prompt_text = f"أنت أستاذ عراقي ذكي ومساند لوزارة التربية العراقية. اشرح الموضوع بوضوح، وفي نهاية شرحك، اقترح على الطالب باختصار شديد إجراء امتحان قصير (3 أسئلة) حول ما شرحته للتو.\n\nالسؤال: {user_question}"
            
            answer = call_gemini_rest(prompt_text)
            
            if answer:
                st.session_state["last_explanation"] = answer
                st.success("💡 إليك الإجابة النموذجية:")
                st.markdown(answer)

# ذيل الصفحة
st.divider()
st.markdown("<p style='text-align: center; color: gray;'>مصممة بملكة البرمجة 💡</p>", unsafe_allow_html=True)
    

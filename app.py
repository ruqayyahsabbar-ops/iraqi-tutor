import streamlit as st
from pathlib import Path
from pypdf import PdfReader
import re

# =========================
# إعداد الصفحة
# =========================

st.set_page_config(
    page_title="مساعد المنهج العراقي",
    page_icon="📚",
    layout="wide"
)

# =========================
# معلومات الصفوف والمواد
# =========================

GRADES = {
    "الأول المتوسط": {
        "folder": "grade7",
        "subjects": {
            "📖 اللغة العربية": "arabic.pdf",
            "🇬🇧 اللغة الإنجليزية": "english.pdf",
            "➗ الرياضيات": "math.pdf",
            "🧪 العلوم": "science.pdf",
        }
    },

    "الثاني المتوسط": {
        "folder": "grade8",
        "subjects": {
            "📖 اللغة العربية": "arabic.pdf",
            "🇬🇧 اللغة الإنجليزية": "english.pdf",
            "➗ الرياضيات": "math.pdf",
            "🧪 العلوم": "science.pdf",
        }
    },

    "الثالث المتوسط": {
        "folder": "grade9",
        "subjects": {
            "📖 اللغة العربية": "arabic.pdf",
            "🇬🇧 اللغة الإنجليزية": "english.pdf",
            "➗ الرياضيات": "math.pdf",
            "🧪 العلوم": "science.pdf",
        }
    },

    "الرابع العلمي": {
        "folder": "grade10_scientific",
        "subjects": {
            "🧬 الأحياء": "biology.pdf",
            "🧪 الكيمياء": "chemistry.pdf",
            "⚡ الفيزياء": "physics.pdf",
            "➗ الرياضيات": "math.pdf",
            "📖 اللغة العربية": "arabic.pdf",
            "🇬🇧 اللغة الإنجليزية": "english.pdf",
        }
    },

    "الخامس العلمي": {
        "folder": "grade11_scientific",
        "subjects": {
            "🧬 الأحياء": "biology.pdf",
            "🧪 الكيمياء": "chemistry.pdf",
            "⚡ الفيزياء": "physics.pdf",
            "➗ الرياضيات": "math.pdf",
            "📖 اللغة العربية": "arabic.pdf",
            "🇬🇧 اللغة الإنجليزية": "english.pdf",
        }
    },

    "السادس العلمي": {
        "folder": "grade12_scientific",
        "subjects": {
            "🧬 الأحياء": "biology.pdf",
            "🧪 الكيمياء": "chemistry.pdf",
            "⚡ الفيزياء": "physics.pdf",
            "➗ الرياضيات": "math.pdf",
            "📖 اللغة العربية": "arabic.pdf",
            "🇬🇧 اللغة الإنجليزية": "english.pdf",
        }
    },
}

# =========================
# تنسيق بسيط
# =========================

st.markdown(
    """
    <style>
    .main-title {
        text-align: center;
        font-size: 38px;
        font-weight: bold;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #777;
        font-size: 17px;
        margin-bottom: 30px;
    }

    .result-box {
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin-bottom: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# العنوان
# =========================

st.markdown(
    '<div class="main-title">📚 مساعد المنهج العراقي</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">ابحثي داخل كتب المنهج العراقي بسهولة</div>',
    unsafe_allow_html=True
)

# =========================
# القائمة الجانبية
# =========================

with st.sidebar:

    st.header("📚 المنهج الدراسي")

    grade = st.selectbox(
        "اختاري الصف",
        list(GRADES.keys())
    )

    subjects = GRADES[grade]["subjects"]

    subject = st.selectbox(
        "اختاري المادة",
        list(subjects.keys())
    )

    st.divider()

    st.markdown("### 📌 الصف المختار")
    st.write(grade)

    st.markdown("### 📖 المادة")
    st.write(subject)

# =========================
# تحديد ملف الكتاب
# =========================

book_path = Path("ocr-result.pdf")

# =========================
# التحقق من وجود الكتاب
# =========================

if not book_path.exists():

    st.info("📚 لم يتم العثور على ملف الكتاب.")

    st.stop()
# =========================
# قراءة الكتاب
# =========================

@st.cache_data
def extract_book(path):

    reader = PdfReader(path)

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text() or ""

        pages.append({
            "page": page_number,
            "text": text
        })

    return pages


pages = extract_book(str(book_path))

# =========================
# معلومات الكتاب
# =========================

st.success(
    f"📗 تم فتح كتاب {subject} — عدد الصفحات: {len(pages)}"
)
# =========================
# المساعد الدراسي
# =========================

st.subheader("🎓 المساعد الدراسي")

question = st.text_input(
    "اكتبي سؤالك:",
    placeholder="مثال: ما هو التنوع الأحيائي؟"
)

if question.strip():

    words = [
        word.strip()
        for word in re.findall(r'\w+', question.lower())
        if len(word) > 2
    ]

    best_page = None
    best_score = 0

    for item in pages:

        text = item["text"].lower()

        score = 0

        for word in words:

            if word in text:
                score += 1

        if score > best_score:
            best_score = score
            best_page = item

    if best_page:

        full_text = best_page["text"]

        answer = full_text[:700]

        st.success("✅ تم العثور على إجابة محتملة")

        st.markdown("## 📖 الجواب")

        st.markdown(
            f"""
            <div style="
                padding:15px;
                border-radius:12px;
                background:#f8f9fa;
                border:1px solid #ddd;
            ">
            {answer}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"📄 الصفحة: {best_page['page']}"
        )

    else:

        st.warning(
            "لم أتمكن من العثور على إجابة مناسبة داخل الكتاب."
        )

else:

    st.info(
        "💬 اكتبي سؤالاً من المنهج ليتم البحث عن الإجابة."
    )
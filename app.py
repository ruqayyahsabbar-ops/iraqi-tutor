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

folder = GRADES[grade]["folder"]
filename = subjects[subject]

book_path = Path("books") / folder / filename

# =========================
# التحقق من وجود الكتاب
# =========================

if not book_path.exists():

    st.info(
        f"""
        📚 كتاب **{subject}** للصف **{grade}**
        
        لم تتم إضافته إلى المشروع بعد.
        
        عندما تضيفين ملف الكتاب إلى مجلد:
        
        `books/{folder}/`
        
        وتسمينه:
        
        `{filename}`
        
        سيظهر هنا تلقائياً.
        """
    )

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
# البحث
# =========================

st.subheader("🔍 البحث داخل الكتاب")

search = st.text_input(
    "اكتبي الكلمة أو العبارة التي تريدين البحث عنها:",
    placeholder="مثال: التنوع الاحيائي"
)

# =========================
# تنفيذ البحث
# =========================

if search.strip():

    search_text = search.strip().lower()

    results = []

    for item in pages:

        text = item["text"]

        if search_text in text.lower():

            results.append(item)

    # =====================
    # النتائج
    # =====================

    if results:

        st.success(
            f"وجدت العبارة في {len(results)} صفحة 📚"
        )

        for result in results:

            st.markdown(
                f"### 📄 الصفحة {result['page']}"
            )

            st.text_area(
                "النص الموجود في الصفحة:",
                result["text"],
                height=250,
                key=f"result_{result['page']}"
            )

            st.divider()

    else:

        st.warning(
            "لم يتم العثور على هذه الكلمة أو العبارة داخل الكتاب."
        )

else:

    st.info(
        "✏️ اكتبي كلمة أو عبارة للبحث داخل الكتاب."
    )

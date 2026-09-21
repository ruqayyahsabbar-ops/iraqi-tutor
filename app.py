import streamlit as st
import os
import json
import re
import hashlib

# =========================
# محاولة استيراد المكتبات
# =========================
try:
    import pytesseract
    from pdf2image import convert_from_bytes
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


# =========================
# إعداد الصفحة
# =========================
st.set_page_config(
    page_title="مساعد المنهج العراقي",
    page_icon="📚",
    layout="centered"
)


# =========================
# المجلدات والملفات
# =========================
BOOKS_DIR = "books"
DATABASE_FILE = "books.json"

os.makedirs(BOOKS_DIR, exist_ok=True)


# =========================
# تحميل قاعدة البيانات
# =========================
def load_database():
    if os.path.exists(DATABASE_FILE):
        try:
            with open(DATABASE_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception:
            return {}

    return {}


books_db = load_database()


# =========================
# حفظ قاعدة البيانات
# =========================
def save_database():
    with open(DATABASE_FILE, "w", encoding="utf-8") as file:
        json.dump(
            books_db,
            file,
            ensure_ascii=False,
            indent=4
        )


# =========================
# تنظيف اسم الملف
# =========================
def safe_filename(text):
    text = re.sub(r'[\\/*?:"<>|]', "_", text)
    text = text.replace(" ", "_")
    return text


# =========================
# استخراج نص صفحة PDF
# =========================
def extract_page_text(image):
    try:
        text = pytesseract.image_to_string(
            image,
            lang="ara+eng"
        )

        return text.strip()

    except Exception as error:
        return f"حدث خطأ أثناء قراءة الصفحة: {error}"


# =========================
# البحث في النص
# =========================
def search_text(text, question):
    """
    بحث بسيط ومرن داخل النص.
    يبحث عن السؤال كاملًا أولًا،
    ثم عن الكلمات المهمة الموجودة فيه.
    """

    text_lower = text.lower()
    question_lower = question.lower().strip()

    # البحث عن السؤال كاملًا
    if question_lower in text_lower:
        return True, 100

    # تقسيم السؤال إلى كلمات
    words = re.findall(r"\S+", question_lower)

    # حذف الكلمات القصيرة جدًا
    words = [word for word in words if len(word) >= 3]

    if not words:
        return False, 0

    found = 0

    for word in words:
        if word in text_lower:
            found += 1

    percentage = int((found / len(words)) * 100)

    # إذا وجد 40% أو أكثر من الكلمات
    if percentage >= 40:
        return True, percentage

    return False, percentage


# =========================
# البحث داخل الكتاب
# =========================
def search_book(pdf_path, question):

    if not os.path.exists(pdf_path):
        return []

    with open(pdf_path, "rb") as file:
        pdf_bytes = file.read()

    try:
        images = convert_from_bytes(
            pdf_bytes,
            dpi=180
        )
    except Exception as error:
        raise Exception(
            f"تعذر تحويل PDF إلى صور: {error}"
        )

    results = []

    progress = st.progress(0)

    total_pages = len(images)

    for index, image in enumerate(images):

        page_number = index + 1

        text = extract_page_text(image)

        if text:

            found, score = search_text(
                text,
                question
            )

            if found:

                results.append({
                    "page": page_number,
                    "text": text,
                    "score": score
                })

        progress.progress(
            int((page_number / total_pages) * 100)
        )

    progress.empty()

    # ترتيب النتائج حسب قوة التطابق
    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results


# =========================
# العنوان
# =========================
st.title("📚 مساعد المنهج العراقي الشامل")

st.write(
    "ارفعي كتاب المنهج العراقي بصيغة PDF، "
    "وسيتمكن الطالب من البحث داخل صفحات الكتاب."
)

st.divider()


# =====================================================
# الشريط الجانبي
# =====================================================

st.sidebar.header("🎯 تحديد المنهج")

grade = st.sidebar.selectbox(
    "المرحلة الدراسية:",
    [
        "السادس الإعدادي",
        "الخامس الإعدادي",
        "الرابع الإعدادي",
        "الثالث المتوسط",
        "الثاني المتوسط",
        "الأول المتوسط"
    ]
)

subject = st.sidebar.selectbox(
    "المادة الدراسية:",
    [
        "الفيزياء",
        "الكيمياء",
        "الأحياء",
        "الرياضيات",
        "اللغة العربية",
        "اللغة الإنجليزية"
    ]
)


# المفتاح الخاص بالكتاب
book_key = f"{grade}_{subject}"


# =====================================================
# لوحة الإدارة
# =====================================================

st.sidebar.divider()

st.sidebar.subheader("🔒 لوحة التحكم")

admin_mode = st.sidebar.checkbox(
    "تفعيل وضع رفع الكتب"
)


if admin_mode:

    st.sidebar.info(
        f"📖 الكتاب الحالي:\n{subject} - {grade}"
    )

    uploaded_pdf = st.sidebar.file_uploader(
        "اختر كتاب PDF:",
        type=["pdf"]
    )

    if uploaded_pdf:

        st.sidebar.success(
            "✅ تم اختيار الكتاب بنجاح!"
        )

        if st.sidebar.button(
            "💾 حفظ الكتاب",
            type="primary"
        ):

            try:

                # اسم الملف
                filename = safe_filename(
                    f"{grade}_{subject}.pdf"
                )

                filepath = os.path.join(
                    BOOKS_DIR,
                    filename
                )

                # حفظ PDF
                with open(
                    filepath,
                    "wb"
                ) as file:

                    file.write(
                        uploaded_pdf.getbuffer()
                    )

                # حفظ معلومات الكتاب
                books_db[book_key] = {
                    "grade": grade,
                    "subject": subject,
                    "filename": filename,
                    "filepath": filepath,
                    "status": "saved"
                }

                save_database()

                st.sidebar.success(
                    "✅ تم حفظ الكتاب بنجاح!"
                )

                st.sidebar.info(
                    "📚 أصبح الكتاب متاحًا للبحث."
                )

            except Exception as error:

                st.sidebar.error(
                    f"❌ حدث خطأ أثناء الحفظ:\n{error}"
                )


# =====================================================
# حالة الكتاب
# =====================================================

st.sidebar.divider()
st.sidebar.subheader("📚 حالة الكتاب")

if book_key in books_db:

    saved_book = books_db[book_key]

    saved_path = saved_book.get(
        "filepath",
        ""
    )

    if os.path.exists(saved_path):

        st.sidebar.success(
            "🟢 الكتاب موجود وجاهز للبحث"
        )

    else:

        st.sidebar.warning(
            "🟡 الكتاب مسجل ولكن الملف غير موجود"
        )

else:

    st.sidebar.warning(
        "🔴 لا يوجد كتاب محفوظ لهذه المادة"
    )


# =====================================================
# البحث
# =====================================================

st.divider()

st.header("🔍 البحث داخل الكتاب")

user_question = st.text_input(
    "اكتب السؤال أو الكلمة التي تريد البحث عنها:",
    placeholder="مثال: ما هي وظائف الميتوكندريا؟"
)


search_button = st.button(
    "🔎 ابحث في الكتاب",
    type="primary"
)


# =====================================================
# تنفيذ البحث
# =====================================================

if search_button:

    # التحقق من السؤال
    if not user_question.strip():

        st.warning(
            "⚠️ اكتبي السؤال أولًا."
        )

    # التحقق من وجود الكتاب
    elif book_key not in books_db:

        st.error(
            "❌ لا يوجد كتاب محفوظ لهذه المرحلة والمادة."
        )

        st.info(
            "فعّلي وضع رفع الكتب من القائمة الجانبية "
            "وارفعي الكتاب أولًا."
        )

    else:

        book_info = books_db[book_key]

        pdf_path = book_info.get(
            "filepath",
            ""
        )

        if not os.path.exists(pdf_path):

            st.error(
                "❌ ملف الكتاب غير موجود."
            )

        elif not OCR_AVAILABLE:

            st.error(
                "❌ مكتبات OCR غير مثبتة."
            )

            st.code(
                "pip install streamlit pytesseract pdf2image pillow"
            )

        else:

            st.info(
                f"📖 جاري البحث في كتاب "
                f"{subject} - {grade}..."
            )

            try:

                results = search_book(
                    pdf_path,
                    user_question
                )

                st.divider()

                if results:

                    st.success(
                        f"✅ تم العثور على {len(results)} صفحة مرتبطة بالبحث."
                    )

                    # عرض أفضل 10 نتائج
                    for result in results[:10]:

                        page = result["page"]
                        score = result["score"]
                        text = result["text"]

                        with st.expander(
                            f"📄 صفحة {page} — تطابق {score}%"
                        ):

                            st.text_area(
                                "النص المستخرج من الصفحة:",
                                text,
                                height=300,
                                key=f"page_{page}_{hash(text)}"
                            )

                else:

                    st.warning(
                        "لم يتم العثور على نتيجة مطابقة داخل الكتاب."
                    )

                    st.write(
                        "جربي كتابة جزء أقصر من السؤال، "
                        "أو كلمة أساسية مثل: الخلية، الميتوكندريا، "
                        "الضغط، الحركة..."
                    )

            except Exception as error:

                st.error(
                    f"❌ حدث خطأ أثناء البحث:\n{error}"
                )


# =====================================================
# معلومات أسفل الصفحة
# =====================================================

st.divider()

st.caption(
    "📚 مساعد المنهج العراقي — البحث يتم داخل الكتب المرفوعة."
)import streamlit as st
import os
import json
import re
import hashlib

# =========================
# محاولة استيراد المكتبات
# =========================
try:
    import pytesseract
    from pdf2image import convert_from_bytes
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


# =========================
# إعداد الصفحة
# =========================
st.set_page_config(
    page_title="مساعد المنهج العراقي",
    page_icon="📚",
    layout="centered"
)


# =========================
# المجلدات والملفات
# =========================
BOOKS_DIR = "books"
DATABASE_FILE = "books.json"

os.makedirs(BOOKS_DIR, exist_ok=True)


# =========================
# تحميل قاعدة البيانات
# =========================
def load_database():
    if os.path.exists(DATABASE_FILE):
        try:
            with open(DATABASE_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception:
            return {}

    return {}


books_db = load_database()


# =========================
# حفظ قاعدة البيانات
# =========================
def save_database():
    with open(DATABASE_FILE, "w", encoding="utf-8") as file:
        json.dump(
            books_db,
            file,
            ensure_ascii=False,
            indent=4
        )


# =========================
# تنظيف اسم الملف
# =========================
def safe_filename(text):
    text = re.sub(r'[\\/*?:"<>|]', "_", text)
    text = text.replace(" ", "_")
    return text


# =========================
# استخراج نص صفحة PDF
# =========================
def extract_page_text(image):
    try:
        text = pytesseract.image_to_string(
            image,
            lang="ara+eng"
        )

        return text.strip()

    except Exception as error:
        return f"حدث خطأ أثناء قراءة الصفحة: {error}"


# =========================
# البحث في النص
# =========================
def search_text(text, question):
    """
    بحث بسيط ومرن داخل النص.
    يبحث عن السؤال كاملًا أولًا،
    ثم عن الكلمات المهمة الموجودة فيه.
    """

    text_lower = text.lower()
    question_lower = question.lower().strip()

    # البحث عن السؤال كاملًا
    if question_lower in text_lower:
        return True, 100

    # تقسيم السؤال إلى كلمات
    words = re.findall(r"\S+", question_lower)

    # حذف الكلمات القصيرة جدًا
    words = [word for word in words if len(word) >= 3]

    if not words:
        return False, 0

    found = 0

    for word in words:
        if word in text_lower:
            found += 1

    percentage = int((found / len(words)) * 100)

    # إذا وجد 40% أو أكثر من الكلمات
    if percentage >= 40:
        return True, percentage

    return False, percentage


# =========================
# البحث داخل الكتاب
# =========================
def search_book(pdf_path, question):

    if not os.path.exists(pdf_path):
        return []

    with open(pdf_path, "rb") as file:
        pdf_bytes = file.read()

    try:
        images = convert_from_bytes(
            pdf_bytes,
            dpi=180
        )
    except Exception as error:
        raise Exception(
            f"تعذر تحويل PDF إلى صور: {error}"
        )

    results = []

    progress = st.progress(0)

    total_pages = len(images)

    for index, image in enumerate(images):

        page_number = index + 1

        text = extract_page_text(image)

        if text:

            found, score = search_text(
                text,
                question
            )

            if found:

                results.append({
                    "page": page_number,
                    "text": text,
                    "score": score
                })

        progress.progress(
            int((page_number / total_pages) * 100)
        )

    progress.empty()

    # ترتيب النتائج حسب قوة التطابق
    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results


# =========================
# العنوان
# =========================
st.title("📚 مساعد المنهج العراقي الشامل")

st.write(
    "ارفعي كتاب المنهج العراقي بصيغة PDF، "
    "وسيتمكن الطالب من البحث داخل صفحات الكتاب."
)

st.divider()


# =====================================================
# الشريط الجانبي
# =====================================================

st.sidebar.header("🎯 تحديد المنهج")

grade = st.sidebar.selectbox(
    "المرحلة الدراسية:",
    [
        "السادس الإعدادي",
        "الخامس الإعدادي",
        "الرابع الإعدادي",
        "الثالث المتوسط",
        "الثاني المتوسط",
        "الأول المتوسط"
    ]
)

subject = st.sidebar.selectbox(
    "المادة الدراسية:",
    [
        "الفيزياء",
        "الكيمياء",
        "الأحياء",
        "الرياضيات",
        "اللغة العربية",
        "اللغة الإنجليزية"
    ]
)


# المفتاح الخاص بالكتاب
book_key = f"{grade}_{subject}"


# =====================================================
# لوحة الإدارة
# =====================================================

st.sidebar.divider()

st.sidebar.subheader("🔒 لوحة التحكم")

admin_mode = st.sidebar.checkbox(
    "تفعيل وضع رفع الكتب"
)


if admin_mode:

    st.sidebar.info(
        f"📖 الكتاب الحالي:\n{subject} - {grade}"
    )

    uploaded_pdf = st.sidebar.file_uploader(
        "اختر كتاب PDF:",
        type=["pdf"]
    )

    if uploaded_pdf:

        st.sidebar.success(
            "✅ تم اختيار الكتاب بنجاح!"
        )

        if st.sidebar.button(
            "💾 حفظ الكتاب",
            type="primary"
        ):

            try:

                # اسم الملف
                filename = safe_filename(
                    f"{grade}_{subject}.pdf"
                )

                filepath = os.path.join(
                    BOOKS_DIR,
                    filename
                )

                # حفظ PDF
                with open(
                    filepath,
                    "wb"
                ) as file:

                    file.write(
                        uploaded_pdf.getbuffer()
                    )

                # حفظ معلومات الكتاب
                books_db[book_key] = {
                    "grade": grade,
                    "subject": subject,
                    "filename": filename,
                    "filepath": filepath,
                    "status": "saved"
                }

                save_database()

                st.sidebar.success(
                    "✅ تم حفظ الكتاب بنجاح!"
                )

                st.sidebar.info(
                    "📚 أصبح الكتاب متاحًا للبحث."
                )

            except Exception as error:

                st.sidebar.error(
                    f"❌ حدث خطأ أثناء الحفظ:\n{error}"
                )


# =====================================================
# حالة الكتاب
# =====================================================

st.sidebar.divider()
st.sidebar.subheader("📚 حالة الكتاب")

if book_key in books_db:

    saved_book = books_db[book_key]

    saved_path = saved_book.get(
        "filepath",
        ""
    )

    if os.path.exists(saved_path):

        st.sidebar.success(
            "🟢 الكتاب موجود وجاهز للبحث"
        )

    else:

        st.sidebar.warning(
            "🟡 الكتاب مسجل ولكن الملف غير موجود"
        )

else:

    st.sidebar.warning(
        "🔴 لا يوجد كتاب محفوظ لهذه المادة"
    )


# =====================================================
# البحث
# =====================================================

st.divider()

st.header("🔍 البحث داخل الكتاب")

user_question = st.text_input(
    "اكتب السؤال أو الكلمة التي تريد البحث عنها:",
    placeholder="مثال: ما هي وظائف الميتوكندريا؟"
)


search_button = st.button(
    "🔎 ابحث في الكتاب",
    type="primary"
)


# =====================================================
# تنفيذ البحث
# =====================================================

if search_button:

    # التحقق من السؤال
    if not user_question.strip():

        st.warning(
            "⚠️ اكتبي السؤال أولًا."
        )

    # التحقق من وجود الكتاب
    elif book_key not in books_db:

        st.error(
            "❌ لا يوجد كتاب محفوظ لهذه المرحلة والمادة."
        )

        st.info(
            "فعّلي وضع رفع الكتب من القائمة الجانبية "
            "وارفعي الكتاب أولًا."
        )

    else:

        book_info = books_db[book_key]

        pdf_path = book_info.get(
            "filepath",
            ""
        )

        if not os.path.exists(pdf_path):

            st.error(
                "❌ ملف الكتاب غير موجود."
            )

        elif not OCR_AVAILABLE:

            st.error(
                "❌ مكتبات OCR غير مثبتة."
            )

            st.code(
                "pip install streamlit pytesseract pdf2image pillow"
            )

        else:

            st.info(
                f"📖 جاري البحث في كتاب "
                f"{subject} - {grade}..."
            )

            try:

                results = search_book(
                    pdf_path,
                    user_question
                )

                st.divider()

                if results:

                    st.success(
                        f"✅ تم العثور على {len(results)} صفحة مرتبطة بالبحث."
                    )

                    # عرض أفضل 10 نتائج
                    for result in results[:10]:

                        page = result["page"]
                        score = result["score"]
                        text = result["text"]

                        with st.expander(
                            f"📄 صفحة {page} — تطابق {score}%"
                        ):

                            st.text_area(
                                "النص المستخرج من الصفحة:",
                                text,
                                height=300,
                                key=f"page_{page}_{hash(text)}"
                            )

                else:

                    st.warning(
                        "لم يتم العثور على نتيجة مطابقة داخل الكتاب."
                    )

                    st.write(
                        "جربي كتابة جزء أقصر من السؤال، "
                        "أو كلمة أساسية مثل: الخلية، الميتوكندريا، "
                        "الضغط، الحركة..."
                    )

            except Exception as error:

                st.error(
                    f"❌ حدث خطأ أثناء البحث:\n{error}"
                )


# =====================================================
# معلومات أسفل الصفحة
# =====================================================

st.divider()

st.caption(
    "📚 مساعد المنهج العراقي — البحث يتم داخل الكتب المرفوعة."
)import streamlit as st
import os
import json
import re
import hashlib

# =========================
# محاولة استيراد المكتبات
# =========================
try:
    import pytesseract
    from pdf2image import convert_from_bytes
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


# =========================
# إعداد الصفحة
# =========================
st.set_page_config(
    page_title="مساعد المنهج العراقي",
    page_icon="📚",
    layout="centered"
)


# =========================
# المجلدات والملفات
# =========================
BOOKS_DIR = "books"
DATABASE_FILE = "books.json"

os.makedirs(BOOKS_DIR, exist_ok=True)


# =========================
# تحميل قاعدة البيانات
# =========================
def load_database():
    if os.path.exists(DATABASE_FILE):
        try:
            with open(DATABASE_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception:
            return {}

    return {}


books_db = load_database()


# =========================
# حفظ قاعدة البيانات
# =========================
def save_database():
    with open(DATABASE_FILE, "w", encoding="utf-8") as file:
        json.dump(
            books_db,
            file,
            ensure_ascii=False,
            indent=4
        )


# =========================
# تنظيف اسم الملف
# =========================
def safe_filename(text):
    text = re.sub(r'[\\/*?:"<>|]', "_", text)
    text = text.replace(" ", "_")
    return text


# =========================
# استخراج نص صفحة PDF
# =========================
def extract_page_text(image):
    try:
        text = pytesseract.image_to_string(
            image,
            lang="ara+eng"
        )

        return text.strip()

    except Exception as error:
        return f"حدث خطأ أثناء قراءة الصفحة: {error}"


# =========================
# البحث في النص
# =========================
def search_text(text, question):
    """
    بحث بسيط ومرن داخل النص.
    يبحث عن السؤال كاملًا أولًا،
    ثم عن الكلمات المهمة الموجودة فيه.
    """

    text_lower = text.lower()
    question_lower = question.lower().strip()

    # البحث عن السؤال كاملًا
    if question_lower in text_lower:
        return True, 100

    # تقسيم السؤال إلى كلمات
    words = re.findall(r"\S+", question_lower)

    # حذف الكلمات القصيرة جدًا
    words = [word for word in words if len(word) >= 3]

    if not words:
        return False, 0

    found = 0

    for word in words:
        if word in text_lower:
            found += 1

    percentage = int((found / len(words)) * 100)

    # إذا وجد 40% أو أكثر من الكلمات
    if percentage >= 40:
        return True, percentage

    return False, percentage


# =========================
# البحث داخل الكتاب
# =========================
def search_book(pdf_path, question):

    if not os.path.exists(pdf_path):
        return []

    with open(pdf_path, "rb") as file:
        pdf_bytes = file.read()

    try:
        images = convert_from_bytes(
            pdf_bytes,
            dpi=180
        )
    except Exception as error:
        raise Exception(
            f"تعذر تحويل PDF إلى صور: {error}"
        )

    results = []

    progress = st.progress(0)

    total_pages = len(images)

    for index, image in enumerate(images):

        page_number = index + 1

        text = extract_page_text(image)

        if text:

            found, score = search_text(
                text,
                question
            )

            if found:

                results.append({
                    "page": page_number,
                    "text": text,
                    "score": score
                })

        progress.progress(
            int((page_number / total_pages) * 100)
        )

    progress.empty()

    # ترتيب النتائج حسب قوة التطابق
    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results


# =========================
# العنوان
# =========================
st.title("📚 مساعد المنهج العراقي الشامل")

st.write(
    "ارفعي كتاب المنهج العراقي بصيغة PDF، "
    "وسيتمكن الطالب من البحث داخل صفحات الكتاب."
)

st.divider()


# =====================================================
# الشريط الجانبي
# =====================================================

st.sidebar.header("🎯 تحديد المنهج")

grade = st.sidebar.selectbox(
    "المرحلة الدراسية:",
    [
        "السادس الإعدادي",
        "الخامس الإعدادي",
        "الرابع الإعدادي",
        "الثالث المتوسط",
        "الثاني المتوسط",
        "الأول المتوسط"
    ]
)

subject = st.sidebar.selectbox(
    "المادة الدراسية:",
    [
        "الفيزياء",
        "الكيمياء",
        "الأحياء",
        "الرياضيات",
        "اللغة العربية",
        "اللغة الإنجليزية"
    ]
)


# المفتاح الخاص بالكتاب
book_key = f"{grade}_{subject}"


# =====================================================
# لوحة الإدارة
# =====================================================

st.sidebar.divider()

st.sidebar.subheader("🔒 لوحة التحكم")

admin_mode = st.sidebar.checkbox(
    "تفعيل وضع رفع الكتب"
)


if admin_mode:

    st.sidebar.info(
        f"📖 الكتاب الحالي:\n{subject} - {grade}"
    )

    uploaded_pdf = st.sidebar.file_uploader(
        "اختر كتاب PDF:",
        type=["pdf"]
    )

    if uploaded_pdf:

        st.sidebar.success(
            "✅ تم اختيار الكتاب بنجاح!"
        )

        if st.sidebar.button(
            "💾 حفظ الكتاب",
            type="primary"
        ):

            try:

                # اسم الملف
                filename = safe_filename(
                    f"{grade}_{subject}.pdf"
                )

                filepath = os.path.join(
                    BOOKS_DIR,
                    filename
                )

                # حفظ PDF
                with open(
                    filepath,
                    "wb"
                ) as file:

                    file.write(
                        uploaded_pdf.getbuffer()
                    )

                # حفظ معلومات الكتاب
                books_db[book_key] = {
                    "grade": grade,
                    "subject": subject,
                    "filename": filename,
                    "filepath": filepath,
                    "status": "saved"
                }

                save_database()

                st.sidebar.success(
                    "✅ تم حفظ الكتاب بنجاح!"
                )

                st.sidebar.info(
                    "📚 أصبح الكتاب متاحًا للبحث."
                )

            except Exception as error:

                st.sidebar.error(
                    f"❌ حدث خطأ أثناء الحفظ:\n{error}"
                )


# =====================================================
# حالة الكتاب
# =====================================================

st.sidebar.divider()
st.sidebar.subheader("📚 حالة الكتاب")

if book_key in books_db:

    saved_book = books_db[book_key]

    saved_path = saved_book.get(
        "filepath",
        ""
    )

    if os.path.exists(saved_path):

        st.sidebar.success(
            "🟢 الكتاب موجود وجاهز للبحث"
        )

    else:

        st.sidebar.warning(
            "🟡 الكتاب مسجل ولكن الملف غير موجود"
        )

else:

    st.sidebar.warning(
        "🔴 لا يوجد كتاب محفوظ لهذه المادة"
    )


# =====================================================
# البحث
# =====================================================

st.divider()

st.header("🔍 البحث داخل الكتاب")

user_question = st.text_input(
    "اكتب السؤال أو الكلمة التي تريد البحث عنها:",
    placeholder="مثال: ما هي وظائف الميتوكندريا؟"
)


search_button = st.button(
    "🔎 ابحث في الكتاب",
    type="primary"
)


# =====================================================
# تنفيذ البحث
# =====================================================

if search_button:

    # التحقق من السؤال
    if not user_question.strip():

        st.warning(
            "⚠️ اكتبي السؤال أولًا."
        )

    # التحقق من وجود الكتاب
    elif book_key not in books_db:

        st.error(
            "❌ لا يوجد كتاب محفوظ لهذه المرحلة والمادة."
        )

        st.info(
            "فعّلي وضع رفع الكتب من القائمة الجانبية "
            "وارفعي الكتاب أولًا."
        )

    else:

        book_info = books_db[book_key]

        pdf_path = book_info.get(
            "filepath",
            ""
        )

        if not os.path.exists(pdf_path):

            st.error(
                "❌ ملف الكتاب غير موجود."
            )

        elif not OCR_AVAILABLE:

            st.error(
                "❌ مكتبات OCR غير مثبتة."
            )

            st.code(
                "pip install streamlit pytesseract pdf2image pillow"
            )

        else:

            st.info(
                f"📖 جاري البحث في كتاب "
                f"{subject} - {grade}..."
            )

            try:

                results = search_book(
                    pdf_path,
                    user_question
                )

                st.divider()

                if results:

                    st.success(
                        f"✅ تم العثور على {len(results)} صفحة مرتبطة بالبحث."
                    )

                    # عرض أفضل 10 نتائج
                    for result in results[:10]:

                        page = result["page"]
                        score = result["score"]
                        text = result["text"]

                        with st.expander(
                            f"📄 صفحة {page} — تطابق {score}%"
                        ):

                            st.text_area(
                                "النص المستخرج من الصفحة:",
                                text,
                                height=300,
                                key=f"page_{page}_{hash(text)}"
                            )

                else:

                    st.warning(
                        "لم يتم العثور على نتيجة مطابقة داخل الكتاب."
                    )

                    st.write(
                        "جربي كتابة جزء أقصر من السؤال، "
                        "أو كلمة أساسية مثل: الخلية، الميتوكندريا، "
                        "الضغط، الحركة..."
                    )

            except Exception as error:

                st.error(
                    f"❌ حدث خطأ أثناء البحث:\n{error}"
                )


# =====================================================
# معلومات أسفل الصفحة
# =====================================================

st.divider()

st.caption(
    "📚 مساعد المنهج العراقي — البحث يتم داخل الكتب المرفوعة."
    )

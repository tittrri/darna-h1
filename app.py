import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# 1. إعدادات الصفحة والتصميم العربي
st.set_page_config(page_title="عمارة H1 - عين الجرادة", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans Arabic', sans-serif;
        direction: rtl;
        text-align: right;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. تهيئة Firebase بطريقة ذكية
@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        try:
            key_dict = dict(st.secrets["firebase_service_account"])
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error(f"خطأ في المفاتيح: {e}")
            return None
    
    # محاولة الاتصال بالقاعدة المخصصة، وإذا فشلت نستخدم الافتراضية تلقائياً
    try:
        return firestore.client(database="ai-studio-02f6fc2f-3933-4b87-b122-a21a9e98dba8")
    except:
        return firestore.client()

db = init_firebase()

# 3. عرض المحتوى (الذي سيعكس عملك في AI Studio)
st.title("🏢 عمارة H1 - عين الجرادة")
st.write("نظام إدارة السكان التفاعلي")

if db:
    tab1, tab2 = st.tabs(["📢 الإعلانات", "📝 إرسال شكوى"])
    
    with tab1:
        st.header("آخر الأخبار والإعلانات")
        try:
            # هذا الجزء سيسحب الإعلانات التي كتبتها سيدي في Firestore
            docs = db.collection("announcements").stream()
            for doc in docs:
                data = doc.to_dict()
                st.info(f"**{data.get('title', '')}**: {data.get('content', '')}")
        except:
            st.warning("يرجى التأكد من إضافة الإعلانات في لوحة تحكم Firebase.")

    with tab2:
        st.header("صندوق الشكاوي")
        with st.form("complaint_form"):
            title = st.text_input("الموضوع")
            desc = st.text_area("التفاصيل")
            if st.form_submit_button("إرسال") and title and desc:
                db.collection("complaints").add({"title": title, "desc": desc})
                st.success("تم الاستلام سيدي.")

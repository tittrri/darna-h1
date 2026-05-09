import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json

# إعداد الصفحة
st.set_page_config(page_title="H1 - عين الجرادة", layout="centered")

# تنسيق CSS احترافي (الذي صممته في البداية)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans Arabic', sans-serif;
        direction: rtl;
        text-align: right;
    }
    .main-container {
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# تهيئة Firebase
@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        try:
            # استخدام Secrets من Streamlit مباشرة
            key_dict = dict(st.secrets["firebase_service_account"])
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error(f"فشل الاتصال بالقاعدة: {e}")
            return None
    # الاتصال بقاعدة البيانات الخاصة بك سيدي
    return firestore.client(database="ai-studio-02f6fc2f-3933-4b87-b122-a21a9e98dba8")

db = init_firebase()

# الواجهة الرئيسية
st.title("🏢 عمارة H1 - عين الجرادة")
st.write("مرحباً بك في نظام إدارة السكان")

tab1, tab2 = st.tabs(["📢 الإعلانات", "📝 إرسال شكوى"])

with tab1:
    st.header("آخر الإعلانات")
    if db:
        try:
            docs = db.collection("announcements").order_by("createdAt", direction=firestore.Query.DESCENDING).stream()
            found = False
            for doc in docs:
                found = True
                data = doc.to_dict()
                with st.container():
                    st.markdown(f"""
                    <div style="background: white; padding: 15px; border-radius: 10px; border-right: 5px solid #064e3b; margin-bottom: 10px;">
                        <h4>{data.get('title', 'بدون عنوان')}</h4>
                        <p>{data.get('content', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)
            if not found:
                st.info("لا توجد إعلانات حالياً.")
        except Exception as e:
            st.error("تأكد من وجود مجموعة 'announcements' في Firestore.")

with tab2:
    st.header("تقديم شكوى أو اقتراح")
    with st.form("complaint_form"):
        title = st.text_input("موضوع الشكوى")
        email = st.text_input("بريدك الإلكتروني")
        description = st.text_area("التفاصيل")
        submitted = st.form_submit_button("إرسال")
        
        if submitted and title and description:
            if db:
                db.collection("complaints").add({
                    "title": title,
                    "description": description,
                    "userEmail": email,
                    "status": "pending",
                    "createdAt": firestore.SERVER_TIMESTAMP
                })
                st.success("تم إرسال شكواك بنجاح.")

# القائمة الجانبية
st.sidebar.image("https://img.icons8.com/clouds/100/apartment.png")
st.sidebar.markdown("### تواصل مع الإدارة")
st.sidebar.info("هاتف: 0555-XX-XX-XX")
st.sidebar.write("v1.0 إصدار التجربة")

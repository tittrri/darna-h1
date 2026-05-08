import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
from datetime import datetime

# إعداد الصفحة وتصميم CSS مخصص لمحاكاة Frosted Glass
st.set_page_config(page_title="H1 عين الجرادة - إدارة العمارة", layout="centered")

# تصميم CSS مخصص باللغة العربية
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans Arabic', sans-serif;
        direction: rtl;
        text-align: right;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f0f4f8 0%, #e0e7ff 100%);
    }
    
    .main-container {
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.4);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
    }
    
    .announcement-card {
        background: rgba(255, 255, 255, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .stButton>button {
        background-color: #059669;
        color: white;
        border-radius: 12px;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #047857;
        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# تهيئة Firebase
@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        # قراءة مفتاح Firebase من الأسرار (Secrets)
        try:
            key_dict = json.loads(st.secrets["firebase_service_account"])
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error(f"حدث خطأ في الاتصال بـ Firebase: {e}")
            return None
    return firestore.client()

db = init_firebase()

# الواجهة الرئيسية
st.title("🏙️ عمارة H1 عين الجرادة")
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
                        <div class="announcement-card">
                            <h3 style="margin-top:0; color:#064e3b;">{data.get('title', 'بدون عنوان')}</h3>
                            <p style="color:#1e293b;">{data.get('content', '')}</p>
                            <small style="color:#64748b;">📅 {data.get('createdAt').strftime('%Y-%m-%d') if data.get('createdAt') else ''}</small>
                        </div>
                    """, unsafe_allow_html=True)
            if not found:
                st.info("لا توجد إعلانات حالياً.")
        except Exception as e:
            st.error("تعذر جلب الإعلانات. تأكد من إعداد Firebase Secrets.")

with tab2:
    st.header("تقديم شكوى أو اقتراح")
    with st.form("complaint_form", clear_on_submit=True):
        title = st.text_input("موضوع الشكوى")
        email = st.text_input("بريدك الإلكتروني")
        description = st.text_area("تفاصيل الشكوى")
        submitted = st.form_submit_button("إرسال الشكوى")
        
        if submitted:
            if title and description and email:
                if db:
                    db.collection("complaints").add({
                        "title": title,
                        "description": description,
                        "userEmail": email,
                        "status": "pending",
                        "createdAt": firestore.SERVER_TIMESTAMP
                    })
                    st.success("تم إرسال شكواك بنجاح. سنقوم بمراجعتها قريباً.")
                else:
                    st.error("فشل الاتصال بقاعدة البيانات.")
            else:
                st.warning("يرجى ملء جميع الحقول.")

st.sidebar.image("https://img.icons8.com/clouds/100/apartment.png", width=100)
st.sidebar.markdown("### تواصل مع الإدارة")
st.sidebar.info("هاتف: 0555-XX-XX-XX")
st.sidebar.markdown("---")
st.sidebar.write("إصدار التجربة v1.0")


import streamlit as st
import pandas as pd
from app import create_app, db
from models.user import User
from models.schedule import Schedule, Group
from models.room import Room
from models.notification import Notification
from werkzeug.security import check_password_hash

# Config
st.set_page_config(page_title="UnivScheduler (Python Only)", page_icon="🏫", layout="wide")

# Init Flask App Context
app = create_app()

# Session State for Login
if 'user_not_logged' not in st.session_state:
    st.session_state.user_not_logged = True
if 'logged_user' not in st.session_state:
    st.session_state.logged_user = None

def login(email, password):
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            return {"id": user.id, "username": user.username, "role": user.role, "email": user.email, "group_id": user.group_id}
    return None

# Custom CSS for that "Professional Blue" feel inside Streamlit
st.markdown("""
<style>
    .stApp { background-color: #f0f9ff; }
    .stSidebar { background-color: #ffffff; border-right: 1px solid #cbd5e1; }
    h1, h2, h3 { color: #0284c7; }
    .stButton>button { background-color: #0284c7; color: white; border-radius: 8px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# LOGIN SCREEN
if st.session_state.user_not_logged:
    st.title("🔐 University Portal Login")
    st.markdown("Access your dashboard (Python Only Version)")
    
    email = st.text_input("Email", value="admin@univ.ma")
    password = st.text_input("Password", type="password", value="admin123")
    if st.button("Login"):
        user_data = login(email, password)
        if user_data:
            st.session_state.logged_user = user_data
            st.session_state.user_not_logged = False
            st.rerun()
        else:
            st.error("Invalid credentials")

else:
    user = st.session_state.logged_user
    with st.sidebar:
        st.title(f"👤 {user['username']}")
        st.markdown(f"**Role:** {user['role'].upper()}")
        if st.button("Logout"):
            st.session_state.user_not_logged = True
            st.session_state.logged_user = None
            st.rerun()
            
    # --- DASHBOARD LOGIC ---
    if user['role'] == 'student':
        st.header("🎓 Student Dashboard")
        t1, t2 = st.tabs(["Schedule", "Notifications"])
        with t1:
            with app.app_context():
                scheds = Schedule.query.filter_by(group_id=user['group_id']).all()
                df = pd.DataFrame([{
                    "Day": s.day_of_week, 
                    "Time": s.start_time.strftime('%H:%M'), 
                    "Course": s.course_name, 
                    "Room": "Room " + str(s.room_id)
                } for s in scheds])
                st.dataframe(df, use_container_width=True)
        with t2:
            with app.app_context():
                notifs = Notification.query.filter_by(user_id=user['id']).all()
                for n in notifs: st.info(f"**{n.title}**: {n.message}")

    elif user['role'] == 'teacher':
        st.header("👨‍🏫 Teacher Dashboard")
        t1, t2 = st.tabs(["My Classes", "Notifications"])
        with t1:
            with app.app_context():
                scheds = Schedule.query.filter_by(teacher_id=user['id']).all()
                st.table(pd.DataFrame([{
                    "Day": s.day_of_week, 
                    "Time": s.start_time.strftime('%H:%M'), 
                    "Course": s.course_name
                } for s in scheds]))
        with t2:
             with app.app_context():
                notifs = Notification.query.filter_by(user_id=user['id']).all()
                for n in notifs: st.info(f"**{n.title}**: {n.message}")

    elif user['role'] == 'admin':
        st.header("🛡️ Admin Panel")
        col1, col2 = st.columns(2)
        with app.app_context():
            col1.metric("Users", User.query.count())
            col2.metric("Rooms", Room.query.count())
            st.subheader("Master Schedule")
            all_s = Schedule.query.all()
            st.dataframe(pd.DataFrame([{
                "Course": s.course_name, "Day": s.day_of_week, "Teacher": s.teacher_id
            } for s in all_s]))

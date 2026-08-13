import os
import sqlite3
import cv2
import numpy as np
from PIL import Image
import streamlit as st
from tensorflow import keras

# Set page config
st.set_page_config(page_title="DeepFake Face Classification", layout="wide")

# ---------------- DATABASE SETUP ----------------
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS users
(id INTEGER PRIMARY KEY, name TEXT, city TEXT, email TEXT UNIQUE, mobile TEXT, password TEXT)
''')
conn.commit()

# Admin credentials
ADMIN_EMAIL = 'admin@admin.com'
ADMIN_PASS = 'admin123'

# Initialize session states
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = ""

# ---------------- CACHED MODEL LOADING ----------------
@st.cache_resource
def load_deepfake_model():
    model_path = "Deep_model.keras"
    if not os.path.exists(model_path):
        import gdown
        gdown.download(
            id="1MvQFRlMsv6BJh94y_7vpNMnJ_YJqI_PK",
            output=model_path,
            quiet=False
        )
    return keras.models.load_model(model_path)


# ---------------- CUSTOM CSS ----------------
st.markdown(
    '''
    <style>
    .stApp {
        background-color: #0b0e14;
        color: #e1e2e4;
    }
    h1, h2, h3 {
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }
    .stButton > button {
        background-color: #00d2ff;
        color: #0b0e14;
        font-weight: bold;
        border-radius: 4px;
        border: none;
    }
    .stButton > button:hover {
        background-color: #00a8cc;
    }
    .feature-card {
        background-color: #191c22;
        padding: 24px;
        border-radius: 8px;
        border: 1px solid rgba(133, 142, 161, 0.2);
        text-align: center;
    }
    .feature-icon {
        font-size: 2rem;
        color: #00d2ff;
        margin-bottom: 12px;
    }
    </style>
    ''',
    unsafe_allow_html=True
)

# ---------------- NAVIGATION ----------------
menu = st.sidebar.selectbox("Navigate", ["Home", "Register", "Login"])

if st.session_state['logged_in']:
    st.sidebar.markdown(f"**Logged in as:** {st.session_state['user_role'].capitalize()}")
    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.session_state['user_role'] = None
        st.session_state['user_name'] = ""
        st.rerun()

# ---------------- HOME PAGE ----------------
if menu == 'Home':
    st.title('DeepFake Face Classification')
    st.markdown('DETECT WHETHER A FACE IMAGE IS REAL OR DEEPFAKE USING ADVANCED DEEP LEARNING TECHNIQUES')

    if os.path.exists('screen.png'):
        st.image('screen.png', caption='VERTEX_SCANNING: NEURAL ARCHITECTURE VISUALIZATION', width=900)

    st.markdown('<br>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('''
            <div class="feature-card">
                <div class="feature-icon">🧠</div>
                <h4>Deep Learning</h4>
                <p><small>Built with CNNs for accurate DeepFake detection</small></p>
            </div>
        ''', unsafe_allow_html=True)

    with col2:
        st.markdown('''
            <div class="feature-card">
                <div class="feature-icon">🔍</div>
                <h4>Image Analysis</h4>
                <p><small>Advanced preprocessing and feature extraction</small></p>
            </div>
        ''', unsafe_allow_html=True)

    with col3:
        st.markdown('''
            <div class="feature-card">
                <div class="feature-icon">🛡️</div>
                <h4>High Accuracy</h4>
                <p><small>Trained on diverse datasets for reliable classification</small></p>
            </div>
        ''', unsafe_allow_html=True)

    with col4:
        st.markdown('''
            <div class="feature-card">
                <div class="feature-icon">⚡</div>
                <h4>Real-time Prediction</h4>
                <p><small>Optimized pipeline for instant results</small></p>
            </div>
        ''', unsafe_allow_html=True)

# ---------------- REGISTER PAGE ----------------
elif menu == "Register":
    st.title("User Registration")

    with st.form("register_form"):
        name = st.text_input("Name")
        city = st.text_input("City")
        email = st.text_input("Email")
        mobile = st.text_input("Mobile")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Register")

        if submitted:
            if not all([name, city, email, mobile, password, confirm_password]):
                st.error("Please fill in all fields.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            else:
                try:
                    c.execute(
                        "INSERT INTO users (name, city, email, mobile, password) VALUES (?, ?, ?, ?, ?)",
                        (name, city, email, mobile, password)
                    )
                    conn.commit()
                    st.success("Registered successfully! Please navigate to Login.")
                except sqlite3.IntegrityError:
                    st.error("Email already registered.")

# ---------------- LOGIN & DASHBOARD PAGE ----------------
elif menu == "Login":
    if not st.session_state['logged_in']:
        st.subheader('Authentication')

        login_email = st.text_input('Email Address')
        login_password = st.text_input('Password / Access Key', type='password')

        if st.button('Authorize Access'):
            if login_email == ADMIN_EMAIL and login_password == ADMIN_PASS:
                st.session_state['logged_in'] = True
                st.session_state['user_role'] = 'admin'
                st.rerun()
            else:
                c.execute('SELECT * FROM users WHERE email=? AND password=?', (login_email, login_password))
                user = c.fetchone()
                if user:
                    st.session_state['logged_in'] = True
                    st.session_state['user_role'] = 'user'
                    st.session_state['user_name'] = user[1]
                    st.rerun()
                else:
                    st.error('Access Denied: Invalid Credentials')

    # ADMIN DASHBOARD
    elif st.session_state['user_role'] == 'admin':
        st.title("Admin Panel - User Management")

        c.execute("SELECT id, name, city, email, mobile FROM users")
        users = c.fetchall()

        if not users:
            st.info("No registered users found.")

        for user in users:
            user_id, name, city, email, mobile = user
            col_info, col_btn = st.columns([4, 1])
            with col_info:
                st.write(f"**{name}** | {email} | {city} | {mobile}")
            with col_btn:
                if st.button(f"Delete", key=f"del_{user_id}"):
                    c.execute("DELETE FROM users WHERE id=?", (user_id,))
                    conn.commit()
                    st.success(f"User {email} deleted.")
                    st.rerun()

    # USER DASHBOARD
    elif st.session_state['user_role'] == 'user':
        st.title(f"Welcome, {st.session_state['user_name']}!")
        st.subheader("DeepFake Image Detection")
        st.write("Upload an image to predict whether it is Real or Fake.")

        # Load machine learning model
        with st.spinner("Loading Detection Model..."):
            model = load_deepfake_model()

        uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

        if uploaded_file is not None:
            image = Image.open(uploaded_file).convert("RGB")
            st.image(image, caption="Uploaded Image", use_container_width=True)

            file_bytes = np.frombuffer(uploaded_file.getvalue(), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            if img is not None:
                img = cv2.resize(img, (64, 64))
                img = img.astype("float32") / 255.0

                # Predict
                predictions = model.predict(img.reshape(1, 64, 64, 3))
                prd = np.argmax(predictions, axis=1)[0]

                classes = ["Real", "Fake"]
                result = classes[prd]

                if result.lower() == "real":
                    st.success(f"Prediction: **{result}**")
                else:
                    st.error(f"Prediction: **{result}**")

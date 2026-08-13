import streamlit as st
import cv2
import numpy as np
from tensorflow import keras
from PIL import Image
import os
import sqlite3
import hashlib
import time

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="DeepGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 10% 10%, rgba(99,102,241,0.15), transparent 30%),
        radial-gradient(circle at 90% 20%, rgba(168,85,247,0.12), transparent 30%),
        #070b16;
    color: white;
}

/* Main container */

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1250px;
}

/* Headers */

.main-title {
    font-size: 48px;
    font-weight: 800;
    text-align: center;
    margin-bottom: 5px;
    background: linear-gradient(90deg, #8b5cf6, #3b82f6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle {
    text-align: center;
    color: #a7b0c0;
    font-size: 17px;
    margin-bottom: 40px;
}

/* Cards */

.card {
    background: rgba(20, 27, 45, 0.78);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 25px;
    margin-bottom: 20px;
    box-shadow: 0 15px 45px rgba(0,0,0,0.25);
}

.feature-card {
    background: rgba(20, 27, 45, 0.65);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 18px;
    padding: 25px;
    text-align: center;
    height: 170px;
}

.feature-icon {
    font-size: 38px;
}

.feature-title {
    font-size: 19px;
    font-weight: 700;
    margin-top: 10px;
}

.feature-text {
    color: #9ca7ba;
    font-size: 14px;
    margin-top: 7px;
}

/* Prediction */

.real-result {
    background: rgba(34,197,94,0.12);
    border: 1px solid rgba(34,197,94,0.35);
    border-radius: 20px;
    padding: 30px;
    text-align: center;
}

.fake-result {
    background: rgba(239,68,68,0.12);
    border: 1px solid rgba(239,68,68,0.35);
    border-radius: 20px;
    padding: 30px;
    text-align: center;
}

.result-title {
    font-size: 38px;
    font-weight: 800;
}

.confidence {
    font-size: 20px;
    margin-top: 10px;
}

/* Buttons */

.stButton > button {
    width: 100%;
    border-radius: 12px;
    padding: 12px;
    font-weight: 700;
    border: none;
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    color: white;
    transition: 0.2s;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(99,102,241,0.35);
}

/* Inputs */

.stTextInput input,
.stTextInput textarea {
    border-radius: 10px;
}

/* Sidebar */

section[data-testid="stSidebar"] {
    background: #0b1020;
    border-right: 1px solid rgba(255,255,255,0.08);
}

.sidebar-title {
    font-size: 24px;
    font-weight: 800;
    text-align: center;
    margin-bottom: 25px;
}

/* Hide Streamlit branding */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# DATABASE
# ============================================================

DB_NAME = "users.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username, email, password):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (
                username,
                email,
                hash_password(password)
            )
        )

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


def login_user(email, password):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT username FROM users WHERE email=? AND password=?",
        (
            email,
            hash_password(password)
        )
    )

    user = cursor.fetchone()

    conn.close()

    return user[0] if user else None


# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "page" not in st.session_state:
    st.session_state.page = "Login"

if "history" not in st.session_state:
    st.session_state.history = []


# ============================================================
# DATABASE INIT
# ============================================================

init_db()


# ============================================================
# MODEL DOWNLOAD
# ============================================================

@st.cache_resource
def load_model():

    if not os.path.exists("Deepfake_model.keras"):

        import gdown

        gdown.download(
            id="1MvQFRlMsv6BJh94y_7vpNMnJ_YJqI_PK",
            output="Deepfake_model.keras",
            quiet=False
        )

    return keras.models.load_model("Deepfake_model.keras")


# ============================================================
# LOGIN PAGE
# ============================================================

def login_page():

    st.markdown(
        '<div class="main-title">🛡️ DeepGuard AI</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">AI-Powered DeepFake Detection System</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 1.2, 1])

    with col2:

        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.markdown("## 🔐 Welcome Back")
        st.write("Login to access the DeepFake Detection Dashboard.")

        email = st.text_input(
            "Email",
            placeholder="Enter your email"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password"
        )

        st.write("")

        if st.button("🚀 Login"):

            if not email or not password:

                st.error("Please enter email and password.")

            else:

                username = login_user(email, password)

                if username:

                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.page = "Dashboard"

                    st.success("Login successful!")

                    time.sleep(0.5)
                    st.rerun()

                else:

                    st.error("Invalid email or password.")

        st.write("")

        if st.button("📝 Create New Account"):

            st.session_state.page = "Register"
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# REGISTRATION PAGE
# ============================================================

def registration_page():

    st.markdown(
        '<div class="main-title">🛡️ DeepGuard AI</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Create your account</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 1.2, 1])

    with col2:

        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.markdown("## 📝 Register")

        username = st.text_input(
            "Username",
            placeholder="Choose a username"
        )

        email = st.text_input(
            "Email",
            placeholder="Enter your email"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Create a password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Re-enter your password"
        )

        st.write("")

        if st.button("✨ Create Account"):

            if not username or not email or not password:

                st.error("Please fill all fields.")

            elif password != confirm_password:

                st.error("Passwords do not match.")

            elif len(password) < 6:

                st.error("Password must contain at least 6 characters.")

            else:

                success = register_user(
                    username,
                    email,
                    password
                )

                if success:

                    st.success(
                        "Account created successfully! Please login."
                    )

                    time.sleep(1)

                    st.session_state.page = "Login"
                    st.rerun()

                else:

                    st.error(
                        "Username or email already exists."
                    )

        st.write("")

        if st.button("⬅️ Back to Login"):

            st.session_state.page = "Login"
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

def sidebar():

    with st.sidebar:

        st.markdown(
            '<div class="sidebar-title">🛡️ DeepGuard AI</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f"👤 **{st.session_state.username}**"
        )

        st.divider()

        if st.button("🏠 Dashboard"):
            st.session_state.page = "Dashboard"
            st.rerun()

        if st.button("🔍 Detect DeepFake"):
            st.session_state.page = "Detect"
            st.rerun()

        if st.button("📊 History"):
            st.session_state.page = "History"
            st.rerun()

        st.divider()

        if st.button("🚪 Logout"):

            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.page = "Login"

            st.rerun()


# ============================================================
# DASHBOARD
# ============================================================

def dashboard():

    st.markdown(
        f'<div class="main-title">Welcome, {st.session_state.username}! 👋</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Analyze images using our AI-powered DeepFake detection model.</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <div class="feature-title">AI Detection</div>
            <div class="feature-text">
                Detect manipulated images using a trained deep learning model.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <div class="feature-title">Fast Analysis</div>
            <div class="feature-text">
                Get predictions within seconds after uploading an image.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:

        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Confidence Score</div>
            <div class="feature-text">
                View the model's confidence for Real and Fake predictions.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.write("")

    st.markdown("## 🚀 Start Detection")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("""
        <div class="card">
            <h3>🔍 DeepFake Detection</h3>
            <p>
            Upload an image and let our AI model determine
            whether it appears to be real or manipulated.
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔍 Analyze Image"):

            st.session_state.page = "Detect"
            st.rerun()

    with col2:

        st.markdown("""
        <div class="card">
            <h3>📜 Prediction History</h3>
            <p>
            Review the images analyzed during your current session
            and their prediction results.
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("📊 View History"):

            st.session_state.page = "History"
            st.rerun()


# ============================================================
# DETECTION PAGE
# ============================================================

def detection_page():

    st.markdown(
        '<div class="main-title">🔍 DeepFake Detection</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Upload an image and let AI analyze it.</div>',
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader(
        "📁 Choose an image",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file is None:

        st.markdown("""
        <div class="card" style="text-align:center;">
            <h2>📸 Upload an Image</h2>
            <p>
            Supported formats: JPG, JPEG and PNG
            </p>
        </div>
        """, unsafe_allow_html=True)

        return

    image = Image.open(uploaded_file).convert("RGB")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### 🖼️ Uploaded Image")

        st.image(
            image,
            use_container_width=True
        )

    with col2:

        st.markdown("### 🤖 AI Analysis")

        analyze = st.button(
            "🚀 Analyze Image"
        )

        if analyze:

            with st.spinner("🧠 AI is analyzing the image..."):

                try:

                    model = load_model()

                    file_bytes = np.frombuffer(
                        uploaded_file.getvalue(),
                        dtype=np.uint8
                    )

                    img = cv2.imdecode(
                        file_bytes,
                        cv2.IMREAD_COLOR
                    )

                    if img is None:

                        st.error(
                            "Unable to read the uploaded image."
                        )

                        return

                    img = cv2.resize(
                        img,
                        (64, 64)
                    )

                    img = img.astype(
                        "float32"
                    ) / 255.0

                    prediction = model.predict(
                        img.reshape(1, 64, 64, 3),
                        verbose=0
                    )[0]

                    prd = np.argmax(prediction)

                    classes = [
                        "Real",
                        "Fake"
                    ]

                    result = classes[prd]

                    confidence = float(
                        prediction[prd] * 100
                    )

                    real_probability = float(
                        prediction[0] * 100
                    )

                    fake_probability = float(
                        prediction[1] * 100
                    )

                    # Save history

                    st.session_state.history.append({

                        "Image": uploaded_file.name,

                        "Result": result,

                        "Confidence": confidence

                    })

                    if result == "Real":

                        st.markdown(
                            f"""
                            <div class="real-result">
                                <div class="result-title">
                                    ✅ REAL
                                </div>
                                <div class="confidence">
                                    Confidence: {confidence:.2f}%
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    else:

                        st.markdown(
                            f"""
                            <div class="fake-result">
                                <div class="result-title">
                                    ⚠️ FAKE
                                </div>
                                <div class="confidence">
                                    Confidence: {confidence:.2f}%
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    st.write("")

                    st.markdown("### 📊 Prediction Probability")

                    st.progress(
                        real_probability / 100,
                        text=f"Real: {real_probability:.2f}%"
                    )

                    st.progress(
                        fake_probability / 100,
                        text=f"Fake: {fake_probability:.2f}%"
                    )

                except Exception as e:

                    st.error(
                        f"Prediction error: {str(e)}"
                    )


# ============================================================
# HISTORY PAGE
# ============================================================

def history_page():

    st.markdown(
        '<div class="main-title">📊 Prediction History</div>',
        unsafe_allow_html=True
    )

    if not st.session_state.history:

        st.info(
            "No predictions have been made yet."
        )

        return

    for i, item in enumerate(
        reversed(st.session_state.history),
        start=1
    ):

        result = item["Result"]

        if result == "Real":

            icon = "✅"

        else:

            icon = "⚠️"

        st.markdown(
            f"""
            <div class="card">

            <h3>
            {icon} {item["Result"]}
            </h3>

            <p>
            <b>Image:</b> {item["Image"]}
            </p>

            <p>
            <b>Confidence:</b> {item["Confidence"]:.2f}%
            </p>

            </div>
            """,
            unsafe_allow_html=True
        )

    if st.button("🗑️ Clear History"):

        st.session_state.history = []

        st.rerun()


# ============================================================
# APP ROUTING
# ============================================================

if not st.session_state.logged_in:

    if st.session_state.page == "Register":

        registration_page()

    else:

        login_page()

else:

    sidebar()

    if st.session_state.page == "Dashboard":

        dashboard()

    elif st.session_state.page == "Detect":

        detection_page()

    elif st.session_state.page == "History":

        history_page()
import streamlit as st
import sqlite3
import cv2
import numpy as np
from tensorflow import keras
from PIL import Image
import os
import base64

# Initialize database
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
(id INTEGER PRIMARY KEY, name TEXT, city TEXT, email TEXT UNIQUE, mobile TEXT, password TEXT)''')
conn.commit()

# Admin credentials
ADMIN_EMAIL = 'admin@admin.com'
ADMIN_PASS = 'admin123'

# Sidebar menu
menu = st.sidebar.selectbox("Navigate", ["Home", "Register", "Login"])

# Home page
# ---------------- CUSTOM CSS ----------------

st.markdown(
    '''
    <style>
    /* Main Background and Text */
    .stApp {
        background-color: #0b0e14;
        color: #e1e2e4;
    }
    /* Typography */
    h1, h2, h3 {
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }
    /* Buttons */
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
    /* Feature Cards */
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
    /* Status Bar */
    .status-bar {
        font-family: 'Courier New', monospace;
        font-size: 0.8rem;
        color: #858ea1;
        padding-top: 20px;
        margin-top: 40px;
    }

    /* Floating Image - Fixed Corner Overlay */
    .floating-img {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 120px;
        z-index: 9999;
        animation: floatY 3s ease-in-out infinite;
        filter: drop-shadow(0 0 12px rgba(0, 210, 255, 0.4));
    }

    /* Floating Image - Inline Bobbing Effect */
    .floating-inline {
        animation: floatY 3s ease-in-out infinite;
        border-radius: 8px;
    }

    /* Shared bobbing keyframes */
    @keyframes floatY {
        0%   { transform: translatey(0px); }
        50%  { transform: translatey(-15px); }
        100% { transform: translatey(0px); }
    }
    </style>
    ''',
    unsafe_allow_html=True
)

# ---------------- LOGIN AUTHENTICATION ----------------

if menu == 'Login' and not st.session_state.get('logged_in'):

    st.subheader('Authentication')

    login_email = st.text_input('Email Address')
    login_password = st.text_input('Access Key', type='password')

    if st.button('Authorize Access'):

        if login_email == ADMIN_EMAIL and login_password == ADMIN_PASS:

            st.session_state['logged_in'] = True
            st.session_state['user_role'] = 'admin'

            st.success('Admin Login Successful')

        else:

            c.execute(
                'SELECT * FROM users WHERE email=? AND password=?',
                (login_email, login_password)
            )

            user = c.fetchone()

            if user:

                st.session_state['logged_in'] = True
                st.session_state['user_role'] = 'user'
                st.session_state['user_name'] = user[1]

                st.success('User Login Successful')

            else:

                st.error('Access Denied: Invalid Credentials')

# ---------------- HOME PAGE ----------------

if menu == 'Home':

    st.title('DeepFake Face Classification')

    st.markdown(
        'DETECT WHETHER A FACE IMAGE IS REAL OR DEEPFAKE USING ADVANCED DEEP LEARNING TECHNIQUES'
    )

def get_base64(path):
    if not os.path.exists(path):
        st.error(f"Image not found at: {path}")
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

img_b64 = get_base64("image2.jpg")

if img_b64:
    # Fixed corner floating image
    st.markdown(
        f'<img src="data:image/png;base64,{img_b64}" class="floating-inline" width="200">',
        unsafe_allow_html=True
    )
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            '''
            <div class="feature-card">
                <div class="feature-icon">🧠</div>
                <h4>Deep Learning</h4>
                <p><small>Built with CNNs for accurate DeepFake detection</small></p>
            </div>
            ''',
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            '''
            <div class="feature-card">
                <div class="feature-icon">🔍</div>
                <h4>Image Analysis</h4>
                <p><small>Advanced preprocessing and feature extraction</small></p>
            </div>
            ''',
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            '''
            <div class="feature-card">
                <div class="feature-icon">🛡️</div>
                <h4>High Accuracy</h4>
                <p><small>Trained on diverse datasets for reliable classification</small></p>
            </div>
            ''',
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            '''
            <div class="feature-card">
                <div class="feature-icon">⚡</div>
                <h4>Real-time Prediction</h4>
                <p><small>Optimized pipeline for instant results</small></p>
            </div>
            ''',
            unsafe_allow_html=True
        )

# Register page
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
                    st.success("Registered successfully! Please log in.")
                except sqlite3.IntegrityError:
                    st.error("Email already registered.")

# Sidebar login
if menu == "Login":
    st.sidebar.markdown("### User/Admin Login")
    login_email = st.sidebar.text_input("Email")
    login_password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.checkbox("Login"):

        if login_email == ADMIN_EMAIL and login_password == ADMIN_PASS:
            st.success("Logged in as Admin!")
            st.title("Admin Panel - User Management")

            c.execute("SELECT id, name, city, email, mobile FROM users")
            users = c.fetchall()

            for user in users:
                user_id, name, city, email, mobile = user
                st.write(f"**{name}** | {email} | {city} | {mobile}")

                if st.button(f"Delete {email}", key=user_id):
                    c.execute("DELETE FROM users WHERE id=?", (user_id,))
                    conn.commit()
                    st.success(f"User {email} deleted.")
                    st.experimental_rerun()

        else:
            c.execute(
                "SELECT * FROM users WHERE email=? AND password=?",
                (login_email, login_password)
            )
            user = c.fetchone()

            if user:
                st.success("Logged in as User!")
                st.title("User Dashboard")

                # Download model if not exists
                if not os.path.exists("Deep_model.keras"):
                    import gdown

                    gdown.download(
                        id="1MvQFRlMsv6BJh94y_7vpNMnJ_YJqI_PK",
                        output="Deep_model.keras",
                        quiet=False
                    )

                # Load the trained model
                model = keras.models.load_model("Deep_model.keras")

                # Streamlit App
                st.title("DeepFake Image Detection")
                st.write("Upload an image to predict whether it is Real or Fake.")

                # Upload image
                uploaded_file = st.file_uploader(
                    "Choose an image",
                    type=["jpg", "jpeg", "png"]
                )

                if uploaded_file is not None:
                    # Open image with PIL
                    image = Image.open(uploaded_file).convert("RGB")

                    # Display image
                    st.image(image, caption="Uploaded Image", use_container_width=True)

                    # Read image for OpenCV
                    file_bytes = np.frombuffer(uploaded_file.getvalue(), dtype=np.uint8)
                    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

                    # Check if image is loaded correctly
                    if img is not None:
                        # Resize image
                        img = cv2.resize(img, (64, 64))
                        img = img.astype("float32") / 255.0

                        # Prediction
                        prd = np.argmax(
                            model.predict(img.reshape(1, 64, 64, 3)),
                            axis=1
                        )[0]

                        # Class names
                        classes = ["real", "fake"]

                        # Show result
                        st.success(classes[prd])

            else:
                st.error("Invalid credentials.")

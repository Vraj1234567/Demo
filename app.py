```python
import streamlit as st
import sqlite3
import cv2
import numpy as np
from tensorflow import keras
from PIL import Image
import os
import base64


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="DeepGuard | DeepFake Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# DATABASE
# =========================================================

conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    city TEXT,
    email TEXT UNIQUE,
    mobile TEXT,
    password TEXT
)
""")

conn.commit()


# =========================================================
# ADMIN CREDENTIALS
# =========================================================

ADMIN_EMAIL = "admin@admin.com"
ADMIN_PASS = "admin123"


# =========================================================
# SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "user_role" not in st.session_state:
    st.session_state["user_role"] = None

if "user_name" not in st.session_state:
    st.session_state["user_name"] = None


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* =====================================================
       GLOBAL
       ===================================================== */

    .stApp {
        background:
            radial-gradient(
                circle at 15% 15%,
                rgba(0, 210, 255, 0.08),
                transparent 30%
            ),
            radial-gradient(
                circle at 85% 85%,
                rgba(0, 120, 255, 0.06),
                transparent 30%
            ),
            #080b11;

        color: #e8edf3;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1250px;
    }


    /* =====================================================
       SIDEBAR
       ===================================================== */

    section[data-testid="stSidebar"] {
        background: #0d1118;
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: white;
    }


    /* =====================================================
       HEADINGS
       ===================================================== */

    h1, h2, h3, h4 {
        color: #ffffff !important;
        font-family: "Inter", sans-serif;
    }

    h1 {
        font-weight: 800;
        letter-spacing: -1px;
    }


    /* =====================================================
       BUTTONS
       ===================================================== */

    .stButton > button {
        width: 100%;
        border: 1px solid rgba(0, 210, 255, 0.25);
        border-radius: 8px;

        background: linear-gradient(
            135deg,
            #00d2ff,
            #0099cc
        );

        color: #061017;
        font-weight: 700;

        padding: 0.55rem 1rem;

        transition:
            transform 0.2s ease,
            box-shadow 0.2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);

        box-shadow:
            0 8px 25px rgba(
                0,
                210,
                255,
                0.18
            );
    }


    /* =====================================================
       HERO SECTION
       ===================================================== */

    .hero {
        position: relative;

        padding: 55px 45px;

        border-radius: 20px;

        background:
            linear-gradient(
                135deg,
                rgba(0, 210, 255, 0.10),
                rgba(17, 24, 39, 0.75)
            );

        border: 1px solid
            rgba(0, 210, 255, 0.15);

        box-shadow:
            0 20px 60px
            rgba(0, 0, 0, 0.25);

        overflow: hidden;
    }

    .hero::after {
        content: "";

        position: absolute;

        width: 220px;
        height: 220px;

        right: -80px;
        top: -80px;

        border-radius: 50%;

        background:
            rgba(0, 210, 255, 0.08);
    }

    .hero-tag {
        display: inline-block;

        padding: 6px 12px;

        border-radius: 20px;

        background:
            rgba(0, 210, 255, 0.10);

        border: 1px solid
            rgba(0, 210, 255, 0.20);

        color: #00d2ff;

        font-size: 0.8rem;

        font-weight: 700;

        margin-bottom: 15px;
    }

    .hero-title {
        font-size: 3.2rem;

        font-weight: 800;

        line-height: 1.1;

        margin-bottom: 15px;

        color: white;
    }

    .hero-title span {
        color: #00d2ff;
    }

    .hero-description {
        max-width: 700px;

        color: #9ca8b8;

        font-size: 1.05rem;

        line-height: 1.7;
    }


    /* =====================================================
       FEATURE CARDS
       ===================================================== */

    .feature-card {
        height: 100%;

        padding: 25px;

        border-radius: 14px;

        background:
            rgba(20, 25, 34, 0.85);

        border: 1px solid
            rgba(255,255,255,0.06);

        transition:
            transform 0.25s ease,
            border-color 0.25s ease,
            background 0.25s ease;
    }

    .feature-card:hover {
        transform: translateY(-5px);

        border-color:
            rgba(0, 210, 255, 0.30);

        background:
            rgba(24, 31, 42, 0.95);
    }

    .feature-icon {
        width: 48px;
        height: 48px;

        display: flex;

        align-items: center;
        justify-content: center;

        border-radius: 12px;

        background:
            rgba(0, 210, 255, 0.10);

        font-size: 1.5rem;

        margin-bottom: 18px;
    }

    .feature-title {
        color: white;

        font-size: 1.05rem;

        font-weight: 700;

        margin-bottom: 8px;
    }

    .feature-text {
        color: #8d99a9;

        font-size: 0.88rem;

        line-height: 1.6;
    }


    /* =====================================================
       SECTION HEADER
       ===================================================== */

    .section-header {
        margin-top: 40px;
        margin-bottom: 20px;
    }

    .section-label {
        color: #00d2ff;

        font-size: 0.75rem;

        font-weight: 700;

        letter-spacing: 1.5px;

        text-transform: uppercase;
    }

    .section-title {
        color: white;

        font-size: 1.8rem;

        font-weight: 750;

        margin-top: 4px;
    }


    /* =====================================================
       AUTH CARD
       ===================================================== */

    .auth-header {
        text-align: center;

        margin-bottom: 25px;
    }

    .auth-icon {
        width: 60px;
        height: 60px;

        margin: 0 auto 15px auto;

        display: flex;

        align-items: center;
        justify-content: center;

        border-radius: 16px;

        background:
            rgba(0, 210, 255, 0.10);

        border: 1px solid
            rgba(0, 210, 255, 0.20);

        font-size: 1.7rem;
    }


    /* =====================================================
       INPUT FIELDS
       ===================================================== */

    div[data-baseweb="input"] {
        background-color: #111720 !important;

        border-radius: 8px !important;

        border: 1px solid
            rgba(255,255,255,0.07) !important;
    }

    div[data-baseweb="input"]:focus-within {
        border-color:
            rgba(0, 210, 255, 0.50) !important;
    }


    /* =====================================================
       UPLOAD BOX
       ===================================================== */

    [data-testid="stFileUploader"] {
        background:
            rgba(17, 23, 32, 0.8);

        border-radius: 14px;

        border: 1px dashed
            rgba(0, 210, 255, 0.30);

        padding: 10px;
    }


    /* =====================================================
       DASHBOARD CARD
       ===================================================== */

    .dashboard-card {
        padding: 28px;

        border-radius: 16px;

        background:
            rgba(17, 23, 32, 0.85);

        border: 1px solid
            rgba(255,255,255,0.06);

        margin-bottom: 20px;
    }


    /* =====================================================
       RESULT CARD
       ===================================================== */

    .result-card {
        margin-top: 20px;

        padding: 28px;

        border-radius: 16px;

        text-align: center;

        background:
            linear-gradient(
                135deg,
                rgba(0, 210, 255, 0.08),
                rgba(17, 23, 32, 0.9)
            );

        border: 1px solid
            rgba(0, 210, 255, 0.20);
    }

    .result-label {
        color: #8d99a9;

        font-size: 0.8rem;

        text-transform: uppercase;

        letter-spacing: 1.5px;
    }

    .result-value {
        color: #00d2ff;

        font-size: 2.3rem;

        font-weight: 800;

        margin-top: 8px;
    }


    /* =====================================================
       ADMIN USER CARD
       ===================================================== */

    .user-card {
        padding: 20px;

        border-radius: 12px;

        background:
            #111720;

        border: 1px solid
            rgba(255,255,255,0.06);

        margin-bottom: 10px;
    }


    /* =====================================================
       INFO BAR
       ===================================================== */

    .info-bar {
        display: flex;

        align-items: center;

        gap: 10px;

        padding: 12px 15px;

        margin-bottom: 20px;

        border-radius: 8px;

        background:
            rgba(0, 210, 255, 0.06);

        border: 1px solid
            rgba(0, 210, 255, 0.12);

        color: #9ca8b8;

        font-size: 0.85rem;
    }


    /* =====================================================
       FOOTER
       ===================================================== */

    .footer {
        text-align: center;

        color: #596575;

        font-size: 0.75rem;

        margin-top: 60px;

        padding-top: 20px;

        border-top: 1px solid
            rgba(255,255,255,0.05);
    }


    /* =====================================================
       HIDE STREAMLIT DEFAULT ELEMENTS
       ===================================================== */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

if not st.session_state["logged_in"]:

    menu = st.sidebar.selectbox(
        "Navigate",
        ["Home", "Register", "Login"]
    )

else:

    if st.session_state["user_role"] == "admin":

        menu = st.sidebar.selectbox(
            "Navigate",
            ["Home", "Admin Panel"]
        )

    else:

        menu = st.sidebar.selectbox(
            "Navigate",
            ["Home", "Dashboard"]
        )

    st.sidebar.divider()

    st.sidebar.caption(
        f"Logged in as: {st.session_state['user_name']}"
    )

    if st.sidebar.button("Logout"):

        st.session_state["logged_in"] = False
        st.session_state["user_role"] = None
        st.session_state["user_name"] = None

        st.rerun()


# =========================================================
# HOME PAGE
# =========================================================

if menu == "Home":

    # -----------------------------------------------------
    # HERO
    # -----------------------------------------------------

    st.markdown(
        """
        <div class="hero">

            <div class="hero-tag">
                AI-POWERED MEDIA FORENSICS
            </div>

            <div class="hero-title">
                Detect <span>DeepFakes</span><br>
                with Deep Learning
            </div>

            <div class="hero-description">
                Analyze facial images using a trained deep learning
                model to identify whether the image is authentic
                or artificially generated.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


    # -----------------------------------------------------
    # Image
    # -----------------------------------------------------

    def get_base64(path):

        if not os.path.exists(path):
            return None

        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()


    img_b64 = get_base64("image2.jpg")

    if img_b64:

        st.markdown(
            f"""
            <div style="
                text-align:center;
                margin-top:30px;
                margin-bottom:30px;
            ">

                <img
                    src="data:image/png;base64,{img_b64}"
                    width="210"
                    style="
                        border-radius:14px;
                        border:1px solid
                        rgba(0,210,255,0.20);
                        box-shadow:
                        0 10px 40px
                        rgba(0,210,255,0.08);
                    "
                >

            </div>
            """,
            unsafe_allow_html=True
        )


    # -----------------------------------------------------
    # Features
    # -----------------------------------------------------

    st.markdown(
        """
        <div class="section-header">

            <div class="section-label">
                CORE CAPABILITIES
            </div>

            <div class="section-title">
                Built for reliable image analysis
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.markdown(
            """
            <div class="feature-card">

                <div class="feature-icon">
                    🧠
                </div>

                <div class="feature-title">
                    Deep Learning
                </div>

                <div class="feature-text">
                    CNN-based analysis designed to identify
                    visual patterns associated with DeepFakes.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with col2:

        st.markdown(
            """
            <div class="feature-card">

                <div class="feature-icon">
                    🔍
                </div>

                <div class="feature-title">
                    Image Analysis
                </div>

                <div class="feature-text">
                    Images are resized and normalized before
                    being processed by the detection model.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with col3:

        st.markdown(
            """
            <div class="feature-card">

                <div class="feature-icon">
                    🛡️
                </div>

                <div class="feature-title">
                    Reliable Detection
                </div>

                <div class="feature-text">
                    A trained classification model provides
                    a straightforward real or fake prediction.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with col4:

        st.markdown(
            """
            <div class="feature-card">

                <div class="feature-icon">
                    ⚡
                </div>

                <div class="feature-title">
                    Fast Prediction
                </div>

                <div class="feature-text">
                    Upload an image and receive the model's
                    classification within seconds.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    # -----------------------------------------------------
    # Footer
    # -----------------------------------------------------

    st.markdown(
        """
        <div class="footer">
            DeepGuard • DeepFake Face Classification System
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# REGISTER PAGE
# =========================================================

elif menu == "Register":

    st.markdown(
        """
        <div class="auth-header">

            <div class="auth-icon">
                👤
            </div>

            <h1>Create Account</h1>

            <p style="color:#8d99a9;">
                Register to access the DeepFake detection system.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    with st.form("register_form"):

        col1, col2 = st.columns(2)

        with col1:

            name = st.text_input(
                "Full Name",
                placeholder="Enter your name"
            )

            email = st.text_input(
                "Email",
                placeholder="example@email.com"
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Create a password"
            )


        with col2:

            city = st.text_input(
                "City",
                placeholder="Enter your city"
            )

            mobile = st.text_input(
                "Mobile",
                placeholder="Enter mobile number"
            )

            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="Re-enter password"
            )


        st.write("")

        submitted = st.form_submit_button(
            "Create Account"
        )


        if submitted:

            if not all([
                name,
                city,
                email,
                mobile,
                password,
                confirm_password
            ]):

                st.error(
                    "Please fill in all fields."
                )

            elif password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            else:

                try:

                    c.execute(
                        """
                        INSERT INTO users
                        (name, city, email, mobile, password)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            name,
                            city,
                            email,
                            mobile,
                            password
                        )
                    )

                    conn.commit()

                    st.success(
                        "Account created successfully. "
                        "You can now log in."
                    )

                except sqlite3.IntegrityError:

                    st.error(
                        "This email is already registered."
                    )


# =========================================================
# LOGIN PAGE
# =========================================================

elif menu == "Login":

    st.markdown(
        """
        <div class="auth-header">

            <div class="auth-icon">
                🔐
            </div>

            <h1>Welcome Back</h1>

            <p style="color:#8d99a9;">
                Sign in to access DeepGuard.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        login_email = st.text_input(
            "Email Address",
            placeholder="Enter your email"
        )

        login_password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password"
        )

        st.write("")

        if st.button(
            "Sign In"
        ):

            # -------------------------------------------------
            # ADMIN LOGIN
            # -------------------------------------------------

            if (
                login_email == ADMIN_EMAIL
                and login_password == ADMIN_PASS
            ):

                st.session_state["logged_in"] = True
                st.session_state["user_role"] = "admin"
                st.session_state["user_name"] = "Administrator"

                st.success(
                    "Administrator access granted."
                )

                st.rerun()


            # -------------------------------------------------
            # USER LOGIN
            # -------------------------------------------------

            else:

                c.execute(
                    """
                    SELECT *
                    FROM users
                    WHERE email = ?
                    AND password = ?
                    """,
                    (
                        login_email,
                        login_password
                    )
                )

                user = c.fetchone()


                if user:

                    st.session_state["logged_in"] = True
                    st.session_state["user_role"] = "user"
                    st.session_state["user_name"] = user[1]

                    st.success(
                        "Login successful."
                    )

                    st.rerun()

                else:

                    st.error(
                        "Invalid email or password."
                    )


# =========================================================
# ADMIN PANEL
# =========================================================

elif menu == "Admin Panel":

    if (
        st.session_state["logged_in"]
        and st.session_state["user_role"] == "admin"
    ):

        st.markdown(
            """
            <div class="section-header">

                <div class="section-label">
                    ADMINISTRATION
                </div>

                <div class="section-title">
                    User Management
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


        c.execute(
            """
            SELECT id, name, city, email, mobile
            FROM users
            """
        )

        users = c.fetchall()


        # -----------------------------------------------------
        # User Count
        # -----------------------------------------------------

        st.markdown(
            f"""
            <div class="info-bar">
                👥
                <span>
                    <strong>{len(users)}</strong>
                    registered user(s)
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )


        if not users:

            st.info(
                "No registered users found."
            )

        else:

            for user in users:

                user_id, name, city, email, mobile = user

                col1, col2 = st.columns(
                    [5, 1]
                )


                with col1:

                    st.markdown(
                        f"""
                        <div class="user-card">

                            <strong style="color:white;">
                                {name}
                            </strong>

                            <br><br>

                            <span style="color:#8d99a9;">
                                📧 {email}
                                &nbsp;&nbsp;
                                📍 {city}
                                &nbsp;&nbsp;
                                📱 {mobile}
                            </span>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )


                with col2:

                    st.write("")

                    if st.button(
                        "Delete",
                        key=f"delete_{user_id}"
                    ):

                        c.execute(
                            """
                            DELETE FROM users
                            WHERE id = ?
                            """,
                            (user_id,)
                        )

                        conn.commit()

                        st.success(
                            f"{email} deleted."
                        )

                        st.rerun()


    else:

        st.error(
            "Unauthorized access."
        )


# =========================================================
# USER DASHBOARD
# =========================================================

elif menu == "Dashboard":

    if (
        st.session_state["logged_in"]
        and st.session_state["user_role"] == "user"
    ):

        # -----------------------------------------------------
        # Dashboard Header
        # -----------------------------------------------------

        st.markdown(
            f"""
            <div class="section-header">

                <div class="section-label">
                    AI DETECTION SYSTEM
                </div>

                <div class="section-title">
                    Welcome, {st.session_state["user_name"]}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


        # -----------------------------------------------------
        # Model Download
        # -----------------------------------------------------

        if not os.path.exists(
            "Deep_model.keras"
        ):

            import gdown

            with st.spinner(
                "Preparing DeepFake detection model..."
            ):

                gdown.download(
                    id="1MvQFRlMsv6BJh94y_7vpNMnJ_YJqI_PK",
                    output="Deep_model.keras",
                    quiet=False
                )


        # -----------------------------------------------------
        # Load Model
        # -----------------------------------------------------

        try:

            model = keras.models.load_model(
                "Deep_model.keras"
            )

        except Exception as e:

            st.error(
                f"Unable to load model: {e}"
            )

            st.stop()


        # -----------------------------------------------------
        # Detection Card
        # -----------------------------------------------------

        st.markdown(
            """
            <div class="dashboard-card">

                <h3>
                    🔎 Image Verification
                </h3>

                <p style="color:#8d99a9;">
                    Upload a facial image and the trained
                    deep learning model will classify it as
                    Real or DeepFake.
                </p>

            </div>
            """,
            unsafe_allow_html=True
        )


        # -----------------------------------------------------
        # File Upload
        # -----------------------------------------------------

        uploaded_file = st.file_uploader(
            "Upload image",
            type=[
                "jpg",
                "jpeg",
                "png"
            ],
            help="Supported formats: JPG, JPEG and PNG"
        )


        if uploaded_file is not None:

            col1, col2 = st.columns(
                [1.1, 0.9]
            )


            # -------------------------------------------------
            # Image Preview
            # -------------------------------------------------

            with col1:

                image = Image.open(
                    uploaded_file
                ).convert("RGB")

                st.image(
                    image,
                    caption="Uploaded Image",
                    use_container_width=True
                )


            # -------------------------------------------------
            # Prediction
            # -------------------------------------------------

            with col2:

                st.markdown(
                    """
                    <div class="dashboard-card">

                        <h3>
                            AI Analysis
                        </h3>

                        <p style="color:#8d99a9;">
                            The image will be resized and
                            normalized before classification.
                        </p>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


                if st.button(
                    "Analyze Image"
                ):

                    with st.spinner(
                        "Analyzing image..."
                    ):

                        # Read image
                        file_bytes = np.frombuffer(
                            uploaded_file.getvalue(),
                            dtype=np.uint8
                        )

                        img = cv2.imdecode(
                            file_bytes,
                            cv2.IMREAD_COLOR
                        )


                        if img is not None:

                            # Resize
                            img = cv2.resize(
                                img,
                                (64, 64)
                            )

                            # Normalize
                            img = img.astype(
                                "float32"
                            ) / 255.0


                            # Prediction
                            prediction = model.predict(
                                img.reshape(
                                    1,
                                    64,
                                    64,
                                    3
                                ),
                                verbose=0
                            )


                            # Get class
                            prd = np.argmax(
                                prediction,
                                axis=1
                            )[0]


                            classes = [
                                "real",
                                "fake"
                            ]


                            result = classes[prd]


                            # ---------------------------------
                            # Result
                            # ---------------------------------

                            if result == "real":

                                st.markdown(
                                    """
                                    <div class="result-card">

                                        <div class="result-label">
                                            Detection Result
                                        </div>

                                        <div
                                            class="result-value"
                                        >
                                            ✓ REAL
                                        </div>

                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

                            else:

                                st.markdown(
                                    """
                                    <div class="result-card">

                                        <div class="result-label">
                                            Detection Result
                                        </div>

                                        <div
                                            class="result-value"
                                        >
                                            ⚠ DEEPFAKE
                                        </div>

                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )


                        else:

                            st.error(
                                "Unable to read the uploaded image."
                            )


    else:

        st.error(
            "Unauthorized access."
        )
```

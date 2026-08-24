import streamlit as st
import sqlite3
import cv2
import numpy as np
from tensorflow import keras
from PIL import Image
import os
import base64
import time

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="DeepFake Face Classification",
    page_icon="🕵️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# DATABASE INITIALIZATION
# =========================================================

conn = sqlite3.connect(
    "users.db",
    check_same_thread=False
)

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
# SIDEBAR NAVIGATION
# =========================================================

menu = st.sidebar.selectbox(
    "Navigate",
    ["Home", "Register", "Login"]
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* =====================================================
       MAIN BACKGROUND
       ===================================================== */

    .stApp {
        background: linear-gradient(
            -45deg,
            #0b0e14,
            #10131c,
            #0b0e14,
            #0d1420
        );

        background-size: 400% 400%;

        animation:
            gradientShift 18s ease infinite;

        color: #e1e2e4;
    }

    @keyframes gradientShift {

        0% {
            background-position: 0% 50%;
        }

        50% {
            background-position: 100% 50%;
        }

        100% {
            background-position: 0% 50%;
        }

    }


    /* =====================================================
       FADE ANIMATION
       ===================================================== */

    section.main > div {

        animation:
            fadeInUp 0.7s ease-out;

    }

    @keyframes fadeInUp {

        0% {
            opacity: 0;
            transform: translateY(18px);
        }

        100% {
            opacity: 1;
            transform: translateY(0);
        }

    }


    /* =====================================================
       TYPOGRAPHY
       ===================================================== */

    h1,
    h2,
    h3 {

        color: #ffffff;

        font-family:
            'Inter',
            sans-serif;

    }


    h1 {

        background:
            linear-gradient(
                90deg,
                #00d2ff,
                #7b61ff,
                #00d2ff
            );

        background-size: 200% auto;

        -webkit-background-clip: text;

        -webkit-text-fill-color: transparent;

        animation:
            shine 4s linear infinite;

    }

    @keyframes shine {

        to {
            background-position: 200% center;
        }

    }


    /* =====================================================
       BUTTONS
       ===================================================== */

    .stButton > button {

        background-color: #00d2ff;

        color: #0b0e14;

        font-weight: bold;

        border-radius: 4px;

        border: none;

        transition:
            all 0.25s ease;

        box-shadow:
            0 0 0 rgba(
                0,
                210,
                255,
                0
            );

    }


    .stButton > button:hover {

        background-color: #00a8cc;

        transform:
            translateY(-2px)
            scale(1.03);

        box-shadow:
            0 6px 18px
            rgba(
                0,
                210,
                255,
                0.35
            );

    }


    .stButton > button:active {

        transform:
            translateY(0)
            scale(0.98);

    }


    /* =====================================================
       TEXT INPUT
       ===================================================== */

    .stTextInput > div > div > input {

        transition:
            box-shadow 0.25s ease,
            border-color 0.25s ease;

    }


    .stTextInput > div > div > input:focus {

        box-shadow:
            0 0 0 2px
            rgba(
                0,
                210,
                255,
                0.35
            );

    }


    /* =====================================================
       FEATURE CARDS
       ===================================================== */

    .feature-card {

        background-color: #191c22;

        padding: 24px;

        border-radius: 8px;

        border:
            1px solid
            rgba(
                133,
                142,
                161,
                0.2
            );

        text-align: center;

        transition:
            transform 0.3s ease,
            box-shadow 0.3s ease,
            border-color 0.3s ease;

        animation:
            fadeInUp 0.6s ease-out both;

    }


    .feature-card:hover {

        transform:
            translateY(-6px);

        box-shadow:
            0 10px 24px
            rgba(
                0,
                210,
                255,
                0.18
            );

        border-color:
            rgba(
                0,
                210,
                255,
                0.5
            );

    }


    .feature-icon {

        font-size: 2rem;

        color: #00d2ff;

        margin-bottom: 12px;

        display: inline-block;

        animation:
            floatY 3s ease-in-out infinite;

    }


    /* =====================================================
       RESULT BADGES
       ===================================================== */

    .result-badge {

        display: inline-block;

        padding:
            14px 28px;

        border-radius: 999px;

        font-size: 1.3rem;

        font-weight: 700;

        letter-spacing: 0.05em;

        text-transform: uppercase;

        animation:
            popIn
            0.4s
            cubic-bezier(
                0.34,
                1.56,
                0.64,
                1
            );

        margin-top: 10px;

    }


    .result-real {

        background:
            rgba(
                0,
                230,
                140,
                0.15
            );

        color: #00e68c;

        border:
            1px solid #00e68c;

        box-shadow:
            0 0 20px
            rgba(
                0,
                230,
                140,
                0.25
            );

    }


    .result-fake {

        background:
            rgba(
                255,
                77,
                109,
                0.15
            );

        color: #ff4d6d;

        border:
            1px solid #ff4d6d;

        box-shadow:
            0 0 20px
            rgba(
                255,
                77,
                109,
                0.25
            );

    }


    @keyframes popIn {

        0% {

            opacity: 0;

            transform:
                scale(0.7);

        }

        100% {

            opacity: 1;

            transform:
                scale(1);

        }

    }


    /* =====================================================
       CONFIDENCE BAR
       ===================================================== */

    .conf-track {

        width: 100%;

        height: 10px;

        border-radius: 6px;

        background:
            rgba(
                133,
                142,
                161,
                0.2
            );

        overflow: hidden;

        margin-top: 14px;

    }


    .conf-fill {

        height: 100%;

        border-radius: 6px;

        background:
            linear-gradient(
                90deg,
                #00d2ff,
                #7b61ff
            );

        width: 0%;

        animation:
            fillBar 1s ease-out forwards;

    }


    @keyframes fillBar {

        to {
            width: var(--target-width);
        }

    }


    /* =====================================================
       STATUS BAR
       ===================================================== */

    .status-bar {

        font-family:
            'Courier New',
            monospace;

        font-size: 0.8rem;

        color: #858ea1;

        padding-top: 20px;

        margin-top: 40px;

        border-top:
            1px dashed
            rgba(
                133,
                142,
                161,
                0.25
            );

        animation:
            fadeInUp 0.8s ease-out;

    }


    .status-dot {

        display: inline-block;

        width: 8px;

        height: 8px;

        border-radius: 50%;

        background: #00e68c;

        margin-right: 6px;

        box-shadow:
            0 0 8px #00e68c;

        animation:
            pulseDot
            1.6s
            ease-in-out
            infinite;

    }


    @keyframes pulseDot {

        0%,
        100% {
            opacity: 1;
        }

        50% {
            opacity: 0.3;
        }

    }


    /* =====================================================
       FLOATING IMAGE
       ===================================================== */

    .floating-inline {

        animation:
            floatY
            3s
            ease-in-out
            infinite;

        border-radius: 8px;

        transition:
            filter 0.3s ease;

        filter:
            drop-shadow(
                0 0 10px
                rgba(
                    0,
                    210,
                    255,
                    0.35
                )
            );

    }


    .floating-inline:hover {

        filter:
            drop-shadow(
                0 0 18px
                rgba(
                    0,
                    210,
                    255,
                    0.6
                )
            );

    }


    @keyframes floatY {

        0% {
            transform:
                translatey(0px);
        }

        50% {
            transform:
                translatey(-15px);
        }

        100% {
            transform:
                translatey(0px);
        }

    }


    /* =====================================================
       UPLOADED IMAGE
       ===================================================== */

    div[data-testid="stImage"] img {

        border-radius: 10px;

        border:
            1px solid
            rgba(
                0,
                210,
                255,
                0.25
            );

        transition:
            box-shadow 0.3s ease;

    }


    div[data-testid="stImage"] img:hover {

        box-shadow:
            0 0 24px
            rgba(
                0,
                210,
                255,
                0.3
            );

    }


    /* =====================================================
       LOGIN CARD
       ===================================================== */

    .login-card {

        background:
            rgba(
                25,
                28,
                34,
                0.95
            );

        padding: 35px;

        border-radius: 14px;

        border:
            1px solid
            rgba(
                0,
                210,
                255,
                0.25
            );

        box-shadow:
            0 15px 40px
            rgba(
                0,
                0,
                0,
                0.4
            );

    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# BASE64 IMAGE FUNCTION
# =========================================================

def get_base64(path):

    if not os.path.exists(path):

        st.error(
            f"Image not found at: {path}"
        )

        return None

    with open(path, "rb") as f:

        return base64.b64encode(
            f.read()
        ).decode()


# =========================================================
# HOME PAGE
# =========================================================

if menu == "Home":

    st.title(
        "DeepFake Face Classification"
    )

    st.markdown(
        """
        **DETECT WHETHER A FACE IMAGE IS REAL OR
        DEEPFAKE USING ADVANCED DEEP LEARNING TECHNIQUES**
        """
    )

    img_b64 = get_base64(
        "image2.jpg"
    )

    if img_b64:

        st.markdown(
            f"""
            <img
                src="data:image/png;base64,{img_b64}"
                class="floating-inline"
                width="200"
            >
            """,
            unsafe_allow_html=True
        )

        col1, col2, col3, col4 = st.columns(4)

        # -----------------------------------------------------
        # CARD 1
        # -----------------------------------------------------

        with col1:

            st.markdown(
                """
                <div class="feature-card">

                    <div class="feature-icon">
                        🧠
                    </div>

                    <h4>
                        Deep Learning
                    </h4>

                    <p>
                        <small>
                        Built with CNNs for accurate
                        DeepFake detection
                        </small>
                    </p>

                </div>
                """,
                unsafe_allow_html=True
            )

        # -----------------------------------------------------
        # CARD 2
        # -----------------------------------------------------

        with col2:

            st.markdown(
                """
                <div class="feature-card">

                    <div class="feature-icon">
                        🔍
                    </div>

                    <h4>
                        Image Analysis
                    </h4>

                    <p>
                        <small>
                        Advanced preprocessing and
                        feature extraction
                        </small>
                    </p>

                </div>
                """,
                unsafe_allow_html=True
            )

        # -----------------------------------------------------
        # CARD 3
        # -----------------------------------------------------

        with col3:

            st.markdown(
                """
                <div class="feature-card">

                    <div class="feature-icon">
                        🛡️
                    </div>

                    <h4>
                        High Accuracy
                    </h4>

                    <p>
                        <small>
                        Trained on diverse datasets
                        for reliable classification
                        </small>
                    </p>

                </div>
                """,
                unsafe_allow_html=True
            )

        # -----------------------------------------------------
        # CARD 4
        # -----------------------------------------------------

        with col4:

            st.markdown(
                """
                <div class="feature-card">

                    <div class="feature-icon">
                        ⚡
                    </div>

                    <h4>
                        Real-time Prediction
                    </h4>

                    <p>
                        <small>
                        Optimized pipeline for
                        instant results
                        </small>
                    </p>

                </div>
                """,
                unsafe_allow_html=True
            )

        # -----------------------------------------------------
        # STATUS
        # -----------------------------------------------------

        st.markdown(
            """
            <div class="status-bar">

                <span class="status-dot"></span>

                System online —
                model ready for inference

            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# REGISTER PAGE
# =========================================================

elif menu == "Register":

    st.title(
        "User Registration"
    )

    with st.form(
        "register_form"
    ):

        name = st.text_input(
            "Name"
        )

        city = st.text_input(
            "City"
        )

        email = st.text_input(
            "Email"
        )

        mobile = st.text_input(
            "Mobile"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password"
        )

        submitted = st.form_submit_button(
            "Register"
        )

        if submitted:

            # -------------------------------------------------
            # EMPTY FIELD CHECK
            # -------------------------------------------------

            if not all(
                [
                    name,
                    city,
                    email,
                    mobile,
                    password,
                    confirm_password
                ]
            ):

                st.error(
                    "Please fill in all fields."
                )

            # -------------------------------------------------
            # PASSWORD CHECK
            # -------------------------------------------------

            elif password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            # -------------------------------------------------
            # REGISTER USER
            # -------------------------------------------------

            else:

                try:

                    with st.spinner(
                        "Creating your account..."
                    ):

                        time.sleep(0.4)

                        c.execute(
                            """
                            INSERT INTO users
                            (
                                name,
                                city,
                                email,
                                mobile,
                                password
                            )
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
                        "Registered successfully! "
                        "Please log in."
                    )

                    st.balloons()

                except sqlite3.IntegrityError:

                    st.error(
                        "Email already registered."
                    )


# =========================================================
# LOGIN PAGE
# =========================================================

elif menu == "Login":

    # =====================================================
    # NOT LOGGED IN
    # =====================================================

    if not st.session_state.get(
        "logged_in",
        False
    ):

        # -------------------------------------------------
        # CENTER LOGIN
        # -------------------------------------------------

        left, center, right = st.columns(
            [1, 2, 1]
        )

        with center:

            st.markdown(
                """
                <div style="
                    text-align:center;
                    padding:
                    25px 0 15px 0;
                ">

                    <div style="
                        font-size:3.5rem;
                        margin-bottom:10px;
                    ">
                        🕵️‍♂️
                    </div>

                    <h1 style="
                        margin-bottom:5px;
                    ">
                        Authentication
                    </h1>

                    <p style="
                        color:#858ea1;
                        font-size:0.95rem;
                    ">
                        Login to access
                        DeepFake Detection
                    </p>

                </div>
                """,
                unsafe_allow_html=True
            )

            # -------------------------------------------------
            # LOGIN CARD START
            # -------------------------------------------------

            st.markdown(
                """
                <div class="login-card">
                """,
                unsafe_allow_html=True
            )

            login_email = st.text_input(
                "Email Address",
                placeholder="Enter your email"
            )

            login_password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password"
            )

            login_button = st.button(
                "🔐  Authorize Access",
                use_container_width=True
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )

            # =================================================
            # AUTHENTICATION
            # =================================================

            if login_button:

                with st.spinner(
                    "Verifying credentials..."
                ):

                    time.sleep(0.4)

                # -------------------------------------------------
                # ADMIN LOGIN
                # -------------------------------------------------

                if (
                    login_email == ADMIN_EMAIL
                    and
                    login_password == ADMIN_PASS
                ):

                    st.session_state[
                        "logged_in"
                    ] = True

                    st.session_state[
                        "user_role"
                    ] = "admin"

                    st.session_state[
                        "user_name"
                    ] = "Administrator"

                    st.success(
                        "Admin Login Successful"
                    )

                    time.sleep(0.5)

                    st.rerun()

                # -------------------------------------------------
                # USER LOGIN
                # -------------------------------------------------

                else:

                    c.execute(
                        """
                        SELECT *
                        FROM users
                        WHERE email=?
                        AND password=?
                        """,
                        (
                            login_email,
                            login_password
                        )
                    )

                    user = c.fetchone()

                    if user:

                        st.session_state[
                            "logged_in"
                        ] = True

                        st.session_state[
                            "user_role"
                        ] = "user"

                        st.session_state[
                            "user_name"
                        ] = user[1]

                        st.success(
                            "User Login Successful"
                        )

                        time.sleep(0.5)

                        st.rerun()

                    else:

                        st.error(
                            "Access Denied: "
                            "Invalid Credentials"
                        )


    # =====================================================
    # LOGGED IN
    # =====================================================

    else:

        # -----------------------------------------------------
        # LOGOUT
        # -----------------------------------------------------

        if st.button(
            "Logout"
        ):

            st.session_state[
                "logged_in"
            ] = False

            st.session_state[
                "user_role"
            ] = None

            st.session_state[
                "user_name"
            ] = None

            st.rerun()

        # =====================================================
        # ADMIN PANEL
        # =====================================================

        if (
            st.session_state[
                "user_role"
            ] == "admin"
        ):

            st.success(
                "Logged in as Admin!"
            )

            st.title(
                "Admin Panel - User Management"
            )

            c.execute(
                """
                SELECT
                    id,
                    name,
                    city,
                    email,
                    mobile
                FROM users
                """
            )

            users = c.fetchall()

            if not users:

                st.info(
                    "No registered users found."
                )

            else:

                for user in users:

                    (
                        user_id,
                        name,
                        city,
                        email,
                        mobile
                    ) = user

                    st.markdown(
                        f"""
                        <div
                            class="feature-card"
                            style="
                                text-align:left;
                                margin-bottom:10px;
                            "
                        >

                            <h4>
                                {name}
                            </h4>

                            <p>

                                📧 {email}
                                <br>

                                🌆 {city}
                                <br>

                                📱 {mobile}

                            </p>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    if st.button(
                        f"Delete {email}",
                        key=f"delete_{user_id}"
                    ):

                        c.execute(
                            """
                            DELETE FROM users
                            WHERE id=?
                            """,
                            (user_id,)
                        )

                        conn.commit()

                        st.success(
                            f"User {email} deleted."
                        )

                        st.rerun()


        # =====================================================
        # USER DASHBOARD
        # =====================================================

        elif (
            st.session_state[
                "user_role"
            ] == "user"
        ):

            st.success(
                f"Welcome, "
                f"{st.session_state['user_name']}!"
            )

            st.title(
                "User Dashboard"
            )

            st.divider()

            # -------------------------------------------------
            # DOWNLOAD MODEL
            # -------------------------------------------------

            if not os.path.exists(
                "Deep_model.keras"
            ):

                import gdown

                with st.spinner(
                    "Downloading DeepFake "
                    "detection model..."
                ):

                    gdown.download(
                        id=(
                            "1MvQFRlMsv6BJh94y_7vpNMnJ_YJqI_PK"
                        ),
                        output="Deep_model.keras",
                        quiet=False
                    )

            # -------------------------------------------------
            # LOAD MODEL
            # -------------------------------------------------

            with st.spinner(
                "Loading DeepFake model..."
            ):

                model = keras.models.load_model(
                    "Deep_model.keras"
                )

            # -------------------------------------------------
            # DETECTION
            # -------------------------------------------------

            st.title(
                "DeepFake Image Detection"
            )

            st.write(
                "Upload an image to predict "
                "whether it is Real or Fake."
            )

            uploaded_file = st.file_uploader(
                "Choose an image",
                type=[
                    "jpg",
                    "jpeg",
                    "png"
                ]
            )

            # -------------------------------------------------
            # IMAGE UPLOAD
            # -------------------------------------------------

            if uploaded_file is not None:

                image = Image.open(
                    uploaded_file
                ).convert("RGB")

                st.image(
                    image,
                    caption="Uploaded Image",
                    use_container_width=True
                )

                # -------------------------------------------------
                # OPENCV
                # -------------------------------------------------

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

                    # -------------------------------------------------
                    # MODEL PREDICTION
                    # -------------------------------------------------

                    with st.spinner(
                        "Analyzing facial features..."
                    ):

                        preds = model.predict(
                            img.reshape(
                                1,
                                64,
                                64,
                                3
                            ),
                            verbose=0
                        )

                    prd = np.argmax(
                        preds,
                        axis=1
                    )[0]

                    confidence = (
                        float(
                            np.max(preds)
                        ) * 100
                    )

                    classes = [
                        "real",
                        "fake"
                    ]

                    predicted_class = (
                        classes[prd]
                    )

                    # -------------------------------------------------
                    # REAL RESULT
                    # -------------------------------------------------

                    if predicted_class == "real":

                        st.markdown(
                            f"""
                            <div
                                class="
                                result-badge
                                result-real
                                "
                            >
                                ✅ REAL
                            </div>

                            <div
                                class="conf-track"
                            >

                                <div
                                    class="conf-fill"
                                    style="
                                    --target-width:
                                    {confidence:.1f}%;
                                    "
                                >
                                </div>

                            </div>

                            <p style="
                                color:#858ea1;
                                margin-top:6px;
                            ">

                                Confidence:
                                {confidence:.1f}%

                            </p>
                            """,
                            unsafe_allow_html=True
                        )

                    # -------------------------------------------------
                    # FAKE RESULT
                    # -------------------------------------------------

                    else:

                        st.markdown(
                            f"""
                            <div
                                class="
                                result-badge
                                result-fake
                                "
                            >
                                ⚠️ DEEPFAKE
                            </div>

                            <div
                                class="conf-track"
                            >

                                <div
                                    class="conf-fill"
                                    style="
                                    --target-width:
                                    {confidence:.1f}%;
                                    "
                                >
                                </div>

                            </div>

                            <p style="
                                color:#858ea1;
                                margin-top:6px;
                            ">

                                Confidence:
                                {confidence:.1f}%

                            </p>
                            """,
                            unsafe_allow_html=True
                        )

                else:

                    st.error(
                        "Unable to read "
                        "the uploaded image."
                    )

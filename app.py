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
    page_title="DeepFake Face Classification",
    page_icon="🛡️",
    layout="wide"
)


# =========================================================
# DATABASE
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
# BASE64 IMAGE FUNCTION
# =========================================================

def get_base64(path):

    if not os.path.exists(path):
        return None

    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    '''
    <style>

    /* =====================================================
       MAIN BACKGROUND AND TEXT
       ===================================================== */

    .stApp {
        background-color: #0b0e14;
        color: #e1e2e4;
    }


    /* =====================================================
       TYPOGRAPHY
       ===================================================== */

    h1, h2, h3 {
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }


    h4 {
        color: #ffffff;
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
    }


    .stButton > button:hover {
        background-color: #00a8cc;
        color: #0b0e14;
    }


    /* =====================================================
       FEATURE CARDS
       ===================================================== */

    .feature-card {
        background-color: #191c22;

        padding: 24px;

        border-radius: 8px;

        border: 1px solid
        rgba(133, 142, 161, 0.2);

        text-align: center;

        min-height: 190px;

        transition:
            transform 0.2s ease,
            border-color 0.2s ease;
    }


    .feature-card:hover {
        transform: translateY(-5px);

        border-color:
        rgba(0, 210, 255, 0.45);
    }


    .feature-icon {
        font-size: 2rem;

        color: #00d2ff;

        margin-bottom: 12px;
    }


    /* =====================================================
       STATUS BAR
       ===================================================== */

    .status-bar {
        font-family: 'Courier New', monospace;

        font-size: 0.8rem;

        color: #858ea1;

        padding-top: 20px;

        margin-top: 40px;
    }


    /* =====================================================
       FLOATING IMAGE - FIXED CORNER
       ===================================================== */

    .floating-img {

        position: fixed;

        bottom: 20px;

        right: 20px;

        width: 120px;

        z-index: 9999;

        animation:
        floatY 3s ease-in-out infinite;

        filter:
        drop-shadow(
            0 0 12px
            rgba(0, 210, 255, 0.4)
        );
    }


    /* =====================================================
       FLOATING IMAGE - INLINE
       ===================================================== */

    .floating-inline {

        animation:
        floatY 3s ease-in-out infinite;

        border-radius: 8px;

        filter:
        drop-shadow(
            0 0 15px
            rgba(0, 210, 255, 0.35)
        );
    }


    /* =====================================================
       FLOATING ANIMATION
       ===================================================== */

    @keyframes floatY {

        0% {
            transform: translateY(0px);
        }

        50% {
            transform: translateY(-15px);
        }

        100% {
            transform: translateY(0px);
        }

    }


    /* =====================================================
       HERO SECTION
       ===================================================== */

    .hero-box {

        background-color: #11151d;

        border: 1px solid
        rgba(0, 210, 255, 0.15);

        border-radius: 12px;

        padding: 35px;

        margin-bottom: 25px;

        text-align: center;
    }


    .hero-tag {

        color: #00d2ff;

        font-size: 0.75rem;

        font-weight: bold;

        letter-spacing: 2px;

        margin-bottom: 12px;
    }


    .hero-title {

        color: #ffffff;

        font-size: 2.8rem;

        font-weight: 800;

        line-height: 1.2;

        margin-bottom: 15px;
    }


    .hero-title span {

        color: #00d2ff;
    }


    .hero-description {

        color: #858ea1;

        font-size: 1rem;

        line-height: 1.6;

        max-width: 700px;

        margin: auto;
    }


    /* =====================================================
       AUTHENTICATION CARD
       ===================================================== */

    .auth-card {

        background-color: #191c22;

        border: 1px solid
        rgba(133, 142, 161, 0.2);

        border-radius: 10px;

        padding: 25px;

        margin-bottom: 20px;
    }


    /* =====================================================
       DASHBOARD CARD
       ===================================================== */

    .dashboard-card {

        background-color: #191c22;

        border: 1px solid
        rgba(133, 142, 161, 0.2);

        border-radius: 10px;

        padding: 25px;

        margin-bottom: 20px;
    }


    /* =====================================================
       RESULT CARD
       ===================================================== */

    .result-card {

        background-color: #191c22;

        border: 1px solid
        rgba(0, 210, 255, 0.25);

        border-radius: 10px;

        padding: 25px;

        text-align: center;

        margin-top: 20px;
    }


    .result-title {

        color: #858ea1;

        font-size: 0.8rem;

        letter-spacing: 2px;

        text-transform: uppercase;
    }


    .result-value {

        color: #00d2ff;

        font-size: 2.2rem;

        font-weight: bold;

        margin-top: 8px;
    }


    /* =====================================================
       USER CARD
       ===================================================== */

    .user-card {

        background-color: #191c22;

        border: 1px solid
        rgba(133, 142, 161, 0.2);

        border-radius: 8px;

        padding: 18px;

        margin-bottom: 10px;
    }


    /* =====================================================
       FOOTER
       ===================================================== */

    .footer {

        text-align: center;

        color: #555e6d;

        font-size: 0.75rem;

        margin-top: 50px;

        padding-top: 20px;

        border-top:
        1px solid
        rgba(133, 142, 161, 0.1);
    }

    </style>
    ''',
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

if not st.session_state["logged_in"]:

    menu = st.sidebar.selectbox(
        "Navigate",
        [
            "Home",
            "Register",
            "Login"
        ]
    )

else:

    if st.session_state["user_role"] == "admin":

        menu = st.sidebar.selectbox(
            "Navigate",
            [
                "Home",
                "Admin Panel"
            ]
        )

    else:

        menu = st.sidebar.selectbox(
            "Navigate",
            [
                "Home",
                "Dashboard"
            ]
        )


    st.sidebar.divider()

    st.sidebar.write(
        f"Logged in as: **{st.session_state['user_name']}**"
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
        '''
        <div class="hero-box">

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
        ''',
        unsafe_allow_html=True
    )


    # -----------------------------------------------------
    # HOME IMAGE
    # -----------------------------------------------------

    image_path = os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)
        ),
        "image2.jpg"
    )


    img_b64 = get_base64(image_path)


    if img_b64:

        st.markdown(
            f'''
            <div style="
                display:flex;
                justify-content:center;
                align-items:center;
                margin:30px 0 40px 0;
            ">

                <img
                    src="data:image/jpeg;base64,{img_b64}"
                    class="floating-inline"
                    width="200"
                >

            </div>
            ''',
            unsafe_allow_html=True
        )

    else:

        st.error(
            "image2.jpg not found. "
            "Please put image2.jpg in the same "
            "folder as app.py."
        )


    # -----------------------------------------------------
    # FEATURES
    # -----------------------------------------------------

    st.markdown(
        """
        <div style="
            text-align:center;
            margin-bottom:25px;
        ">

            <div style="
                color:#00d2ff;
                font-size:0.75rem;
                font-weight:bold;
                letter-spacing:2px;
            ">
                CORE FEATURES
            </div>

            <h2>
                Intelligent DeepFake Detection
            </h2>

        </div>
        """,
        unsafe_allow_html=True
    )


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.markdown(
            '''
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
                        DeepFake detection.
                    </small>
                </p>

            </div>
            ''',
            unsafe_allow_html=True
        )


    with col2:

        st.markdown(
            '''
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
                        feature extraction.
                    </small>
                </p>

            </div>
            ''',
            unsafe_allow_html=True
        )


    with col3:

        st.markdown(
            '''
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
                        for reliable classification.
                    </small>
                </p>

            </div>
            ''',
            unsafe_allow_html=True
        )


    with col4:

        st.markdown(
            '''
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
                        instant results.
                    </small>
                </p>

            </div>
            ''',
            unsafe_allow_html=True
        )


    # -----------------------------------------------------
    # STATUS BAR
    # -----------------------------------------------------

    st.markdown(
        '''
        <div class="status-bar">

            SYSTEM STATUS:
            <span style="color:#00d2ff;">
                ● ONLINE
            </span>

            &nbsp;&nbsp;|&nbsp;&nbsp;

            AI ENGINE:
            <span style="color:#00d2ff;">
                READY
            </span>

            &nbsp;&nbsp;|&nbsp;&nbsp;

            MODEL:
            <span style="color:#00d2ff;">
                CNN
            </span>

        </div>
        ''',
        unsafe_allow_html=True
    )


    # -----------------------------------------------------
    # FOOTER
    # -----------------------------------------------------

    st.markdown(
        '''
        <div class="footer">

            DeepFake Face Classification System
            • AI/ML Project

        </div>
        ''',
        unsafe_allow_html=True
    )


# =========================================================
# REGISTER PAGE
# =========================================================

elif menu == "Register":

    st.title("Create Your Account")

    st.write(
        "Register to access the DeepFake detection system."
    )


    with st.form("register_form"):

        col1, col2 = st.columns(2)


        with col1:

            name = st.text_input(
                "Name",
                placeholder="Enter your name"
            )

            email = st.text_input(
                "Email",
                placeholder="Enter your email"
            )

            password = st.text_input(
                "Password",
                type="password"
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
                type="password"
            )


        submitted = st.form_submit_button(
            "Register"
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
                        "Registration successful! "
                        "Please login."
                    )

                except sqlite3.IntegrityError:

                    st.error(
                        "Email already registered."
                    )


# =========================================================
# LOGIN PAGE
# =========================================================

elif menu == "Login":

    col1, col2, col3 = st.columns(
        [1, 2, 1]
    )


    with col2:

        st.markdown(
            '''
            <div style="
                text-align:center;
                margin-bottom:25px;
            ">

                <div style="
                    font-size:2.5rem;
                ">
                    🔐
                </div>

                <h1>
                    Login
                </h1>

                <p style="
                    color:#858ea1;
                ">
                    Access the DeepFake Detection System
                </p>

            </div>
            ''',
            unsafe_allow_html=True
        )


        login_email = st.text_input(
            "Email Address"
        )


        login_password = st.text_input(
            "Password",
            type="password"
        )


        if st.button(
            "Login"
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
                    "Admin login successful."
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

                    st.session_state["logged_in"] = True

                    st.session_state["user_role"] = "user"

                    st.session_state["user_name"] = user[1]

                    st.success(
                        "User login successful."
                    )

                    st.rerun()

                else:

                    st.error(
                        "Invalid credentials."
                    )


# =========================================================
# ADMIN PANEL
# =========================================================

elif menu == "Admin Panel":

    if (
        st.session_state["logged_in"]
        and
        st.session_state["user_role"] == "admin"
    ):

        st.title(
            "Admin Panel"
        )

        st.write(
            "Manage registered users."
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
                "No registered users."
            )


        else:

            for user in users:

                user_id, name, city, email, mobile = user


                col1, col2 = st.columns(
                    [5, 1]
                )


                with col1:

                    st.markdown(
                        f'''
                        <div class="user-card">

                            <strong>
                                {name}
                            </strong>

                            <br>

                            <span style="
                                color:#858ea1;
                            ">
                                Email: {email}
                                <br>
                                City: {city}
                                <br>
                                Mobile: {mobile}
                            </span>

                        </div>
                        ''',
                        unsafe_allow_html=True
                    )


                with col2:

                    if st.button(
                        "Delete",
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
                            "User deleted."
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
        and
        st.session_state["user_role"] == "user"
    ):

        st.title(
            f"Welcome, {st.session_state['user_name']} 👋"
        )


        st.write(
            "Upload a face image to detect whether "
            "it is Real or DeepFake."
        )


        # -----------------------------------------------------
        # DOWNLOAD MODEL
        # -----------------------------------------------------

        if not os.path.exists(
            "Deep_model.keras"
        ):

            import gdown


            with st.spinner(
                "Downloading DeepFake model..."
            ):

                gdown.download(
                    id="1MvQFRlMsv6BJh94y_7vpNMnJ_YJqI_PK",
                    output="Deep_model.keras",
                    quiet=False
                )


        # -----------------------------------------------------
        # LOAD MODEL
        # -----------------------------------------------------

        try:

            model = keras.models.load_model(
                "Deep_model.keras"
            )

        except Exception as e:

            st.error(
                f"Error loading model: {e}"
            )

            st.stop()


        # -----------------------------------------------------
        # UPLOAD IMAGE
        # -----------------------------------------------------

        uploaded_file = st.file_uploader(
            "Choose an image",
            type=[
                "jpg",
                "jpeg",
                "png"
            ]
        )


        if uploaded_file is not None:

            col1, col2 = st.columns(2)


            # -------------------------------------------------
            # IMAGE PREVIEW
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
            # PREDICTION
            # -------------------------------------------------

            with col2:

                st.markdown(
                    """
                    <div class="dashboard-card">

                        <h3>
                            AI Image Analysis
                        </h3>

                        <p style="
                            color:#858ea1;
                        ">
                            The image will be resized
                            to 64 × 64 pixels and
                            analyzed by the CNN model.
                        </p>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


                if st.button(
                    "Analyze Image"
                ):

                    with st.spinner(
                        "Analyzing..."
                    ):

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
                            img = (
                                img.astype(
                                    "float32"
                                )
                                / 255.0
                            )


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


                            # -------------------------------------------------
                            # RESULT
                            # -------------------------------------------------

                            st.markdown(
                                f"""
                                <div class="result-card">

                                    <div class="result-title">
                                        Detection Result
                                    </div>

                                    <div class="result-value">
                                        {result.upper()}
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

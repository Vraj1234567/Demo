import streamlit as st
import sqlite3
import cv2
import numpy as np
from tensorflow import keras
from PIL import Image
import os
import base64


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

    /* Floating Image */
    .floating-inline {
        animation: floatY 3s ease-in-out infinite;
        border-radius: 8px;
    }

    /* Floating Animation */
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

    # Logout button
    if st.sidebar.button("Logout"):

        st.session_state["logged_in"] = False
        st.session_state["user_role"] = None
        st.session_state["user_name"] = None

        st.rerun()


# =========================================================
# HOME PAGE
# =========================================================

if menu == "Home":

    st.title("DeepFake Face Classification")

    st.markdown(
        """
        **DETECT WHETHER A FACE IMAGE IS REAL OR DEEPFAKE
        USING ADVANCED DEEP LEARNING TECHNIQUES**
        """
    )

    # -----------------------------------------------------
    # Base64 Image Function
    # -----------------------------------------------------

    def get_base64(path):

        if not os.path.exists(path):
            st.error(f"Image not found at: {path}")
            return None

        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    # Load image
    img_b64 = get_base64("image2.jpg")

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

    # -----------------------------------------------------
    # Feature Cards
    # -----------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    # Feature 1
    with col1:

        st.markdown(
            """
            <div class="feature-card">

                <div class="feature-icon">
                    🧠
                </div>

                <h4>Deep Learning</h4>

                <p>
                    <small>
                    Built with CNNs for accurate DeepFake detection
                    </small>
                </p>

            </div>
            """,
            unsafe_allow_html=True
        )

    # Feature 2
    with col2:

        st.markdown(
            """
            <div class="feature-card">

                <div class="feature-icon">
                    🔍
                </div>

                <h4>Image Analysis</h4>

                <p>
                    <small>
                    Advanced preprocessing and feature extraction
                    </small>
                </p>

            </div>
            """,
            unsafe_allow_html=True
        )

    # Feature 3
    with col3:

        st.markdown(
            """
            <div class="feature-card">

                <div class="feature-icon">
                    🛡️
                </div>

                <h4>High Accuracy</h4>

                <p>
                    <small>
                    Trained on diverse datasets for reliable classification
                    </small>
                </p>

            </div>
            """,
            unsafe_allow_html=True
        )

    # Feature 4
    with col4:

        st.markdown(
            """
            <div class="feature-card">

                <div class="feature-icon">
                    ⚡
                </div>

                <h4>Real-time Prediction</h4>

                <p>
                    <small>
                    Optimized pipeline for instant results
                    </small>
                </p>

            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# REGISTER PAGE
# =========================================================

elif menu == "Register":

    st.title("User Registration")

    with st.form("register_form"):

        name = st.text_input("Name")

        city = st.text_input("City")

        email = st.text_input("Email")

        mobile = st.text_input("Mobile")

        password = st.text_input(
            "Password",
            type="password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password"
        )

        submitted = st.form_submit_button("Register")

        if submitted:

            # Check empty fields
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

            # Check password
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
                        "Registered successfully! Please log in."
                    )

                except sqlite3.IntegrityError:

                    st.error(
                        "Email already registered."
                    )


# =========================================================
# LOGIN PAGE
# =========================================================

elif menu == "Login":

    st.title("Authentication")

    st.write(
        "Login as User or Administrator"
    )

    login_email = st.text_input(
        "Email Address"
    )

    login_password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

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
                "Admin Login Successful"
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
                    "User Login Successful"
                )

                st.rerun()

            else:

                st.error(
                    "Access Denied: Invalid Credentials"
                )


# =========================================================
# ADMIN PANEL
# =========================================================

elif menu == "Admin Panel":

    # Security check
    if (
        st.session_state["logged_in"]
        and st.session_state["user_role"] == "admin"
    ):

        st.title(
            "Admin Panel - User Management"
        )

        st.write(
            "Welcome, Administrator!"
        )

        st.divider()

        # Get users
        c.execute(
            """
            SELECT id, name, city, email, mobile
            FROM users
            """
        )

        users = c.fetchall()

        if not users:

            st.info(
                "No registered users found."
            )

        else:

            st.subheader(
                f"Registered Users: {len(users)}"
            )

            for user in users:

                user_id, name, city, email, mobile = user

                # User information
                col1, col2 = st.columns([4, 1])

                with col1:

                    st.write(
                        f"**Name:** {name}"
                    )

                    st.write(
                        f"**Email:** {email}"
                    )

                    st.write(
                        f"**City:** {city}"
                    )

                    st.write(
                        f"**Mobile:** {mobile}"
                    )

                with col2:

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
                            f"User {email} deleted."
                        )

                        st.rerun()

                st.divider()

    else:

        st.error(
            "Unauthorized access."
        )


# =========================================================
# USER DASHBOARD
# =========================================================

elif menu == "Dashboard":

    # Security check
    if (
        st.session_state["logged_in"]
        and st.session_state["user_role"] == "user"
    ):

        st.title(
            "User Dashboard"
        )

        st.write(
            f"Welcome, **{st.session_state['user_name']}**!"
        )

        st.divider()

        # -------------------------------------------------
        # Download Model
        # -------------------------------------------------

        if not os.path.exists(
            "Deep_model.keras"
        ):

            import gdown

            st.info(
                "Downloading DeepFake detection model..."
            )

            gdown.download(
                id="1MvQFRlMsv6BJh94y_7vpNMnJ_YJqI_PK",
                output="Deep_model.keras",
                quiet=False
            )

        # -------------------------------------------------
        # Load Model
        # -------------------------------------------------

        try:

            model = keras.models.load_model(
                "Deep_model.keras"
            )

        except Exception as e:

            st.error(
                f"Unable to load model: {e}"
            )

            st.stop()

        # -------------------------------------------------
        # DeepFake Detection
        # -------------------------------------------------

        st.subheader(
            "DeepFake Image Detection"
        )

        st.write(
            "Upload an image to predict whether it is Real or Fake."
        )

        # Image uploader
        uploaded_file = st.file_uploader(
            "Choose an image",
            type=[
                "jpg",
                "jpeg",
                "png"
            ]
        )

        if uploaded_file is not None:

            # ---------------------------------------------
            # Display Uploaded Image
            # ---------------------------------------------

            image = Image.open(
                uploaded_file
            ).convert("RGB")

            st.image(
                image,
                caption="Uploaded Image",
                use_container_width=True
            )

            # ---------------------------------------------
            # Convert Image for OpenCV
            # ---------------------------------------------

            file_bytes = np.frombuffer(
                uploaded_file.getvalue(),
                dtype=np.uint8
            )

            img = cv2.imdecode(
                file_bytes,
                cv2.IMREAD_COLOR
            )

            # ---------------------------------------------
            # Check Image
            # ---------------------------------------------

            if img is not None:

                # Resize image
                img = cv2.resize(
                    img,
                    (64, 64)
                )

                # Normalize image
                img = img.astype(
                    "float32"
                ) / 255.0

                # -----------------------------------------
                # Prediction
                # -----------------------------------------

                prediction = model.predict(
                    img.reshape(
                        1,
                        64,
                        64,
                        3
                    ),
                    verbose=0
                )

                # Get predicted class
                prd = np.argmax(
                    prediction,
                    axis=1
                )[0]

                # -----------------------------------------
                # Class Names
                # -----------------------------------------

                classes = [
                    "real",
                    "fake"
                ]

                result = classes[prd]

                # -----------------------------------------
                # Display Result
                # -----------------------------------------

                st.subheader(
                    "Prediction Result"
                )

                if result == "real":

                    st.success(
                        "REAL IMAGE"
                    )

                else:

                    st.error(
                        "DEEPFAKE IMAGE"
                    )

            else:

                st.error(
                    "Unable to read the uploaded image."
                )

    else:

        st.error(
            "Unauthorized access."
        )

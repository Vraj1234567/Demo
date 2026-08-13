import streamlit as st
import sqlite3
import cv2
import numpy as np
from tensorflow import keras
from PIL import Image
import os


# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="DeepFake Face Classification",
    page_icon="🔍",
    layout="wide"
)


# =========================================================
# DATABASE INITIALIZATION
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
# LOAD / DOWNLOAD DEEPFAKE MODEL
# =========================================================
@st.cache_resource
def load_model():

    model_path = "Deepfake_model.keras"

    if not os.path.exists(model_path):

        import gdown

        gdown.download(
            id="1MvQFRlMsv6BJh94y_7vpNMnJ_YJqI_PK",
            output=model_path,
            quiet=False
        )

    model = keras.models.load_model(model_path)

    return model


# Load model
model = load_model()


# =========================================================
# SESSION STATE
# =========================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_type" not in st.session_state:
    st.session_state.user_type = None

if "user_email" not in st.session_state:
    st.session_state.user_email = None


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🔍 DeepFake Detection")

if st.session_state.logged_in:

    st.sidebar.success(
        f"Logged in as {st.session_state.user_type}"
    )

    menu = st.sidebar.selectbox(
        "Navigate",
        ["Dashboard", "Logout"]
    )

else:

    menu = st.sidebar.selectbox(
        "Navigate",
        ["Home", "Register", "Login"]
    )


# =========================================================
# HOME PAGE
# =========================================================

if menu == "Home":

    st.title("🔍 DeepFake Face Classification")

    st.write(
        """
        Welcome to the DeepFake Face Classification System.

        This application uses a trained Deep Learning model
        to classify an uploaded face image as:

        - 🟢 Real
        - 🔴 Fake
        """
    )

    # Display project image if available
    if os.path.exists("image2.jpg"):
        st.image(
            "image2.jpg",
            width=600
        )

    st.subheader("How it works")

    st.write(
        """
        1. Register an account.
        2. Login using your credentials.
        3. Upload a face image.
        4. The trained CNN model processes the image.
        5. The system predicts whether the image is Real or Fake.
        """
    )


# =========================================================
# REGISTER PAGE
# =========================================================

elif menu == "Register":

    st.title("📝 User Registration")

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
                        "Registered successfully! Please login."
                    )

                except sqlite3.IntegrityError:

                    st.error(
                        "Email already registered."
                    )


# =========================================================
# LOGIN PAGE
# =========================================================

elif menu == "Login":

    st.title("🔐 Login")

    login_email = st.text_input(
        "Email"
    )

    login_password = st.text_input(
        "Password",
        type="password"
    )

    login_button = st.button(
        "Login"
    )

    if login_button:

        # -------------------------------------------------
        # ADMIN LOGIN
        # -------------------------------------------------

        if (
            login_email == ADMIN_EMAIL
            and login_password == ADMIN_PASS
        ):

            st.session_state.logged_in = True
            st.session_state.user_type = "Admin"
            st.session_state.user_email = login_email

            st.success(
                "Logged in successfully as Admin!"
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

                st.session_state.logged_in = True
                st.session_state.user_type = "User"
                st.session_state.user_email = login_email

                st.success(
                    "Logged in successfully!"
                )

                st.rerun()

            else:

                st.error(
                    "Invalid email or password."
                )


# =========================================================
# USER DASHBOARD
# =========================================================

elif menu == "Dashboard":

    # =====================================================
    # ADMIN DASHBOARD
    # =====================================================

    if st.session_state.user_type == "Admin":

        st.title("👨‍💼 Admin Panel")

        st.subheader("User Management")

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

            for user in users:

                user_id, name, city, email, mobile = user

                st.markdown("---")

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
                            "DELETE FROM users WHERE id = ?",
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

    elif st.session_state.user_type == "User":

        st.title("👤 User Dashboard")

        st.write(
            f"Welcome, **{st.session_state.user_email}**!"
        )

        st.subheader(
            "🔍 DeepFake Image Detection"
        )

        st.write(
            "Upload an image to predict whether it is Real or Fake."
        )

        uploaded_file = st.file_uploader(
            "Choose an image",
            type=["jpg", "jpeg", "png"]
        )

        if uploaded_file is not None:

            # -------------------------------------------------
            # OPEN IMAGE USING PIL
            # -------------------------------------------------

            image = Image.open(
                uploaded_file
            ).convert("RGB")

            # Display image
            st.image(
                image,
                caption="Uploaded Image",
                use_container_width=True
            )

            # -------------------------------------------------
            # READ IMAGE USING OPENCV
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

                # -------------------------------------------------
                # PREPROCESS IMAGE
                # -------------------------------------------------

                img = cv2.resize(
                    img,
                    (64, 64)
                )

                img = img.astype(
                    "float32"
                ) / 255.0

                # -------------------------------------------------
                # MODEL PREDICTION
                # -------------------------------------------------

                prediction = model.predict(
                    img.reshape(
                        1,
                        64,
                        64,
                        3
                    ),
                    verbose=0
                )

                prd = np.argmax(
                    prediction,
                    axis=1
                )[0]

                # Class names
                classes = [
                    "Real",
                    "Fake"
                ]

                result = classes[prd]

                # -------------------------------------------------
                # DISPLAY RESULT
                # -------------------------------------------------

                st.subheader("Prediction Result")

                if result == "Real":

                    st.success(
                        "✅ The image is classified as REAL."
                    )

                else:

                    st.error(
                        "⚠️ The image is classified as FAKE."
                    )

                # Display confidence
                confidence = float(
                    np.max(prediction)
                ) * 100

                st.write(
                    f"Confidence: **{confidence:.2f}%**"
                )


# =========================================================
# LOGOUT
# =========================================================

elif menu == "Logout":

    st.session_state.logged_in = False
    st.session_state.user_type = None
    st.session_state.user_email = None

    st.success(
        "You have been logged out successfully."
    )

    st.rerun()
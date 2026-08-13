import streamlit as st
import cv2
import sqlite3
import numpy as np
from tensorflow import keras
from PIL import Image
import os

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
if menu == "Home":
    st.title("DeepFake Face Classification")
    st.image("image2.jpg", width=600)
    
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
                    c.execute("INSERT INTO users (name, city, email, mobile, password) VALUES (?, ?, ?, ?, ?)",
                              (name, city, email, mobile, password))
                    conn.commit()
                    st.success("Registered successfully! Please log in.")
                except sqlite3.IntegrityError:
                    st.error("Email already registered.")
# Sidebar login
if menu == "Login":
    st.sidebar.markdown("### User/Admin Login")
    login_email = st.sidebar.text_input("Email")
    login_password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
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
            c.execute("SELECT * FROM users WHERE email=? AND password=?", (login_email, login_password))
            user = c.fetchone()
            if user:
                st.success("Logged in as User!")
                st.title("User Dashboard")
                uploaded_file = st.file_uploader("Upload an image", type=['jpg', 'jpeg', 'png'])
                if uploaded_file is not None:
                    with open("temp_img.jpg", "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    st.image(uploaded_file, caption="Uploaded Image")

            else:
                st.error("Invalid credentials.")
# ----------------------
# Download model if not exists
# ----------------------
if not os.path.exists("Deepfake_model.keras"):
    import gdown

    gdown.download(  # noqa: E402
        id="1MvQFRlMsv6BJh94y_7vpNMnJ_YJqI_PK",
        output="Deepfake_model.keras",
        quiet=False
    )

# ----------------------
# Load the trained model
# ----------------------
model = keras.models.load_model("Deepfake_model.keras")

# ----------------------
# Streamlit App
# ----------------------
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

  

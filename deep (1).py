import streamlit as st
import cv2
import numpy as np
from tensorflow import keras
from PIL import Image
import os

# ----------------------
# Download model if not exists
# ----------------------
if not os.path.exists("Deep_model.keras"):
    import gdown

    gdown.download(  # noqa: E402
        id="1MvQFRlMsv6BJh94y_7vpNMnJ_YJqI_PK",
        output="Deep_model.keras",
        quiet=False
    )

# ----------------------
# Load the trained model
# ----------------------
model = keras.models.load_model("Deep_model.keras")

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

  

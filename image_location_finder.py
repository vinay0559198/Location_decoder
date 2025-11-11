import streamlit as st
import requests
import base64

# Replace this with your actual key
API_KEY = r"Google_api_key"
VISION_URL = f"https://vision.googleapis.com/v1/images:annotate?key={API_KEY}"
GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"

st.set_page_config(page_title="Image Location Finder", layout="centered")
st.title("📍 Image Location Finder")
st.write("Upload an image, and we’ll try to find the location or give a best guess using Google APIs.")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image_data = uploaded_file.read()
    
    #  Image Preview
    st.image(uploaded_file, caption="Uploaded Image Preview", width=300)

    
    image_base64 = base64.b64encode(image_data).decode("utf-8")

    # Step 1: Vision Request
    request_body = {
        "requests": [
            {
                "image": {"content": image_base64},
                "features": [
                    {"type": "LANDMARK_DETECTION", "maxResults": 1},
                    {"type": "WEB_DETECTION", "maxResults": 3},
                    {"type": "LABEL_DETECTION", "maxResults": 3}
                ]
            }
        ]
    }

    st.info("Analyzing image with Google Vision API...")
    response = requests.post(VISION_URL, json=request_body)
    result = response.json()

    try:
        landmark = result["responses"][0]["landmarkAnnotations"][0]
        desc = landmark["description"]
        lat = landmark["locations"][0]["latLng"]["latitude"]
        lng = landmark["locations"][0]["latLng"]["longitude"]
        score = round(landmark["score"] * 100, 2)

        # Step 2: Reverse Geocode
        geocode_params = {"latlng": f"{lat},{lng}", "key": API_KEY}
        geo_resp = requests.get(GEOCODE_URL, params=geocode_params)
        address = geo_resp.json()["results"][0]["formatted_address"]

        st.success(f"📍 Detected: **{desc}**")
        st.write(f"📌 Address: {address}")
        st.write(f" Coordinates: `{lat}, {lng}`")
        st.write(f" Confidence: {score}%")
        st.components.v1.iframe(f"https://www.google.com/maps?q={lat},{lng}&output=embed", height=500)

    except Exception:
        # Fallback: Web detection
        web_detected = result["responses"][0].get("webDetection", {})
        if "bestGuessLabels" in web_detected:
            guess = web_detected["bestGuessLabels"][0]["label"]
            st.warning("❌ Coordinates not found.")
            st.info(f" Best Guess: **{guess}**")
        elif "labelAnnotations" in result["responses"][0]:
            labels = [l["description"] for l in result["responses"][0]["labelAnnotations"]]
            st.warning("❌ Location not detected.")
            st.info(" Image Tags: " + ", ".join(labels))
        else:
            st.error("❌ Could not find any location or labels.")
            st.code(result)


from model import analyze_image
import requests
import streamlit as st
from PIL import Image
import cv2
import numpy as np
import folium
from streamlit_folium import st_folium
from streamlit_javascript import st_javascript
from ultralytics import YOLO

# ==============================
# ⚙️ CONFIGURATION
# ==============================
st.set_page_config(page_title="Playground Safety App", layout="wide")

# ------------------------------
# 🧭 PAGE STATE MANAGEMENT
# ------------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

def go_to_scanner():
    st.session_state.page = "scanner"

def go_to_evaluation():
    st.session_state.page = "evaluation"

def go_to_image_analysis():
    st.session_state.page = "image_analysis"

# ------------------------------
# 💅 GLOBAL STYLING
# ------------------------------
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 1000px;
        margin: auto;
    }
    h1, h2, h3, h4 { color: #003366; }
    button[kind="primary"] {
        background-color: #007BFF !important;
        color: white !important;
        border-radius: 10px !important;
    }
    .stSuccess, .stWarning, .stInfo, .stError {
        border-radius: 10px;
        padding: 0.5rem 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------------
# 🏞️ APP HEADER BANNER
# ------------------------------
st.markdown("""
    <style>
    .block-container {
        padding-top: 3rem !important;
    }
    .app-banner {
        background-color: #007BFF;
        color: white;
        text-align: center;
        padding: 1rem 1.5rem;
        margin-top: 1rem;
        margin-bottom: 2rem;
        border-radius: 12px;
        font-size: 1.5rem;
        font-weight: 600;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
    }
    </style>

    <div class="app-banner">
        🏞️ Playground Safety Checker — Helping Communities Stay Safe
    </div>
""", unsafe_allow_html=True)

# ------------------------------
# 🏠 LANDING PAGE
# ------------------------------
if st.session_state.page == "home":
    st.markdown("""<div style="color:gray;font-size:0.9rem;margin-top:1rem;">🏠 Home</div>""", unsafe_allow_html=True)

    st.title("Welcome!")
    st.markdown("""
        This app helps you **find, inspect, and evaluate playgrounds** in your area.  
        <br>
        🧭 **Find** nearby playgrounds on an interactive map.  
        📸 **Upload** playground photos to detect safety issues using AI.  
        🧠 **Take** a short quiz to assess playground safety manually.  
        <br><br>
        Click below to begin checking playgrounds near you!
    """, unsafe_allow_html=True)

    
    st.button("🚀 Check out a Playground Near You", type="primary", on_click=go_to_scanner)
    banner = Image.open("boy-playing-at-playground_1741623809.png")
    st.image(banner, caption="Ensuring safer playgrounds for everyone", use_container_width=True)
    st.stop()


# ------------------------------
# 🗺️ MAP SECTION — FIND PLAYGROUND
# ------------------------------
if st.session_state.page == "scanner":
    st.markdown("""<div style="color:gray;font-size:0.9rem;margin-bottom:0.5rem;">🏠 Home ➜ 📍 Map</div>""", unsafe_allow_html=True)
    st.markdown("#### <span style='color:#00509E'>📍 Find Nearby Playgrounds</span>", unsafe_allow_html=True)

    address = st.text_input("Enter your address (leave blank to auto-detect by IP):", placeholder="e.g., 1600 Pennsylvania Ave NW, Washington DC")

    def get_location_by_ip():
        try:
            r = requests.get("https://ipinfo.io/json", timeout=5)
            data = r.json()
            loc = data.get("loc", "")
            if loc:
                lat, lon = loc.split(",")
                return float(lat), float(lon)
        except:
            pass
        return 41.8781, -87.6298  # Default fallback: Chicago

    # 🌐 LOCATION RESOLUTION
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    radius = 1000  # in meters

    if address.strip():
        geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_API_KEY}"
        resp = requests.get(geocode_url)
        data = resp.json()

        if data.get("status") == "OK":
            loc = data["results"][0]["geometry"]["location"]
            user_lat, user_lng = loc["lat"], loc["lng"]
            formatted_address = data["results"][0]["formatted_address"]
            st.success(f"✅ Found location: {formatted_address}")
        else:
            st.warning("⚠️ Could not find that address. Using IP-based location instead.")
            user_lat, user_lng = get_location_by_ip()
            st.info(f"🌐 Using approximate IP-based location: ({user_lat:.4f}, {user_lng:.4f})")
    else:
        user_lat, user_lng = get_location_by_ip()
        st.info(f"🌐 Using approximate IP-based location: ({user_lat:.4f}, {user_lng:.4f})")

    # 🗺️ FETCH NEARBY PLAYGROUNDS
    url = (
        f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
        f"location={user_lat},{user_lng}"
        f"&radius={radius}"
        f"&type=park"
        f"&keyword=playground"
        f"&key={GOOGLE_API_KEY}"
    )

    response = requests.get(url)
    data = response.json()

    playgrounds = []
    if data.get("results"):
        for place in data["results"]:
            name = place["name"]
            lat = place["geometry"]["location"]["lat"]
            lng = place["geometry"]["location"]["lng"]
            playgrounds.append({"name": name, "lat": lat, "lng": lng})
    else:
        st.warning("No playgrounds found nearby. Showing a sample location.")
        playgrounds = [{"name": "Sample Park", "lat": user_lat + 0.002, "lng": user_lng - 0.001}]

    # 🗺️ MAP DISPLAY
    st.subheader("🗺️ Interactive Playground Map")

    m = folium.Map(location=[user_lat, user_lng], zoom_start=14, tiles=None)
    folium.TileLayer(
        tiles='https://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
        attr='Google',
        name='Google Maps',
        max_zoom=20,
        subdomains=['mt0', 'mt1', 'mt2', 'mt3']
    ).add_to(m)

    # Add user marker
    folium.Marker([user_lat, user_lng], tooltip="You are here", icon=folium.Icon(color="blue", icon="user")).add_to(m)

    # Add playground pins
    for p in playgrounds:
        folium.Marker(
            [p["lat"], p["lng"]],
            tooltip=p["name"],
            popup=f"<b>{p['name']}</b>",
            icon=folium.Icon(color="green", icon="cloud")
        ).add_to(m)

    map_output = st_folium(m, width=800, height=500, key="main_map")

    selected = None
    if map_output and map_output.get("last_object_clicked"):
        clicked_lat = map_output["last_object_clicked"]["lat"]
        clicked_lng = map_output["last_object_clicked"]["lng"]
        selected = min(playgrounds, key=lambda p: (p["lat"] - clicked_lat) ** 2 + (p["lng"] - clicked_lng) ** 2)
        st.markdown(f"<h4 style='text-align:center;color:#007BFF;'>🎯 Selected playground: <b>{selected['name']}</b></h4>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:gray;'>Click below to begin image-based safety analysis.</p>", unsafe_allow_html=True)
    else:
        st.info("👆 Click on a pin to select a playground.")

    if selected:
        if st.button("➡️ Proceed to Image Analysis", use_container_width=True, type="primary"):
            st.session_state.page = "image_analysis"
            st.session_state.selected_playground = selected
            st.rerun()

    st.stop()


# ------------------------------
# 🧪 IMAGE ANALYSIS + QUIZ PAGE
# ------------------------------
if st.session_state.page == "image_analysis":
    selected = st.session_state.get("selected_playground", {"name": "Unknown"})
    st.markdown(f"""
        <div style="color:gray;font-size:0.9rem;margin-bottom:0.5rem;">
            🏠 Home ➜ 📍 Map ➜ 🧪 Image Analysis
        </div>
    """, unsafe_allow_html=True)

    st.header(f"🧪 Playground Image Analysis — {selected['name']}")
    st.write("Upload a playground photo to analyze safety using the AI model, then complete the safety quiz below.")

    # ------------------------------
    # 📸 IMAGE UPLOAD & AI ANALYSIS
    # ------------------------------
    uploaded_file = st.file_uploader("📸 Upload a playground image", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Playground", use_container_width=True)

        with st.spinner("Analyzing image..."):
            annotated, hazards, score = analyze_image(image)

        show_annotated = st.checkbox("Show annotated hazard overlay", value=True)
        if show_annotated:
            st.image(annotated, caption="Annotated Analysis Result", use_container_width=True)

        st.markdown(f"### AI Safety Score: **{score:.1f}/100**")

        if hazards:
            st.markdown("### Detected Hazards:")
            st.write(", ".join(hazards))
        else:
            st.success("✅ No hazards detected!")

        if score > 70:
            st.success("✅ Playground looks safe.")
        elif score > 40:
            st.warning("⚠️ Moderate risk detected.")
        else:
            st.error("🚨 High risk detected!")
    else:
        st.info("📥 Please upload a playground image to begin AI analysis.")

    # ------------------------------
    # 🧠 SAFETY QUIZ SECTION
    # ------------------------------
    st.markdown("#### <span style='color:#FF7A00'>🧠 Safety Quiz</span>", unsafe_allow_html=True)

    if "quiz_started" not in st.session_state:
        st.session_state.quiz_started = False

    # Start quiz button
    if not st.session_state.quiz_started:
        if st.button("Start Quiz?"):
            st.session_state.quiz_started = True

    if st.session_state.quiz_started:
        st.header("Playground Safety Quiz")
        broken_bolts = st.radio("Broken or missing bolts/screws?", ("No", "Yes"))
        cracks = st.radio("Cracks in slides/climbers?", ("No", "Yes"))
        unstable_structures = st.radio("Leaning or unstable equipment?", ("No", "Yes"))

        # Material
        rust = st.radio("Rust or corrosion?", ("No", "Yes"))
        splinters = st.radio("Wood splinters?", ("No", "Yes"))
        worn_out_parts = st.radio("Worn-out plastic/rubber parts?", ("No", "Yes"))

        # Environmental
        slippery = st.radio("Slippery surfaces?", ("No", "Yes"))
        debris = st.radio("Rocks, glass, or trash?", ("No", "Yes"))
        poor_drainage = st.radio("Puddles or poor drainage?", ("No", "Yes"))

        # Mechanical
        creaky = st.radio("Creaky/loose swings or hinges?", ("No", "Yes"))
        exposed_springs = st.radio("Exposed springs or moving parts?", ("No", "Yes"))

        # Cleanliness/maintenance
        overgrown_plants = st.radio("Overgrown plants or weeds?", ("No", "Yes"))
        vandalism = st.radio("Graffiti/vandalism affecting safety?", ("No", "Yes"))

        # Compute score
        score_quiz = 100
        hazards_quiz = [
            broken_bolts, cracks, unstable_structures, rust, splinters, worn_out_parts,
            slippery, debris, poor_drainage, creaky, exposed_springs, overgrown_plants, vandalism
        ]
        weights_quiz = [10, 10, 10, 8, 5, 7, 8, 7, 5, 6, 6, 3, 5]

        for h, w in zip(hazards_quiz, weights_quiz):
            if h == "Yes":
                score_quiz -= w

        st.write(f"### Manual Safety Score: {score_quiz}/100")

        if score_quiz > 70:
            st.success("✅ Playground looks relatively safe!")
        elif score_quiz > 40:
            st.warning("⚠️ Moderate risk detected. Caution advised.")
        else:
            st.error("🚨 High risk detected! Supervision and repairs needed.")

    # ------------------------------
    # 🌈 FOOTER
    # ------------------------------
    st.markdown("""
        <hr>
        <div style='text-align:center; color:gray; font-size:0.85rem;'>
            Made with love by PlaySafe foundation • Data sourced from Google Maps
        </div>
    """, unsafe_allow_html=True)
    
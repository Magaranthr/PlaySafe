import requests
import streamlit as st
from PIL import Image
import cv2
import numpy as np
import folium
from streamlit_folium import st_folium
from streamlit_javascript import st_javascript


#find loc
st.set_page_config(page_title="Playground Safety App", layout="wide")
st.title("🏞️ Playground Safety Checker")

js_code = """
new Promise((resolve) => {
  if (!navigator.geolocation) { resolve(null); } 
  else {
    navigator.geolocation.getCurrentPosition(
      (pos) => { resolve({lat: pos.coords.latitude, lng: pos.coords.longitude}); },
      (err) => { resolve(null); },
      { enableHighAccuracy: true, timeout:10000 }
    );
  }
});
"""
coords = st_javascript(js_code, key="geo")

# --- Step 2: Fallback to IP geolocation ---
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
    return 41.8781, -87.6298  # default fallback: Chicago

if coords:
    user_lat, user_lng = coords['lat'], coords['lng']
    st.success(f"Using precise browser location: ({user_lat:.4f}, {user_lng:.4f})")
else:
    user_lat, user_lng = get_location_by_ip()
    st.warning(f"Using approximate IP-based location: ({user_lat:.4f}, {user_lng:.4f})")

# --- Get nearby playgrounds from Google Places API ---
GOOGLE_API_KEY = "AIzaSyDh4JMRxsZNf6sUhKIt5cC316sSjMfYFVU"
radius = 2000  # in meters
place_type = "playground"

url = (
    f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
    f"location={user_lat},{user_lng}&radius={radius}&keyword={place_type}&key={GOOGLE_API_KEY}"
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
    st.warning("No playgrounds found nearby. Showing sample locations.")
    playgrounds = [
        {"name": "Sample Park", "lat": user_lat + 0.002, "lng": user_lng - 0.001},
    ]

# --- Map setup ---
m = folium.Map(location=[user_lat, user_lng], zoom_start=14, tiles=None)
folium.TileLayer(
    tiles='https://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
    attr='Google',
    name='Google Maps',
    max_zoom=20,
    subdomains=['mt0', 'mt1', 'mt2', 'mt3']
).add_to(m)

# Add user location marker
folium.Marker(
    [user_lat, user_lng],
    tooltip="You are here",
    icon=folium.Icon(color="blue", icon="user")
).add_to(m)

# Add playgrounds from API
for p in playgrounds:
    folium.Marker(
        [p["lat"], p["lng"]],
        tooltip=p["name"],
        icon=folium.Icon(color="green", icon="cloud"),
    ).add_to(m)

st_folium(m, width=800, height=500)

#quiz
st.title("Playground Safety Scanner & Quiz")


uploaded_file = st.file_uploader("Upload a playground image (optional)", type=["jpg","jpeg","png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Playground", use_column_width=True)
    cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    st.write("Image uploaded — ready for analysis (future ML integration).")
else:
    st.write("No image uploaded — you can still complete the quiz.")

start_quiz = st.button("Start Quiz?")

if start_quiz:
    st.write("Answer the questions about the playground hazards:")

    # Structural
    broken_bolts = st.radio("Broken or missing bolts/screws?", ("No","Yes"))
    cracks = st.radio("Cracks in slides/climbers?", ("No","Yes"))
    unstable_structures = st.radio("Leaning or unstable equipment?", ("No","Yes"))
    
    # Material
    rust = st.radio("Rust or corrosion?", ("No","Yes"))
    splinters = st.radio("Wood splinters?", ("No","Yes"))
    worn_out_parts = st.radio("Worn-out plastic/rubber parts?", ("No","Yes"))
    
    # Environmental
    slippery = st.radio("Slippery surfaces?", ("No","Yes"))
    debris = st.radio("Rocks, glass, or trash?", ("No","Yes"))
    poor_drainage = st.radio("Puddles or poor drainage?", ("No","Yes"))
    
    # Mechanical
    creaky = st.radio("Creaky/loose swings or hinges?", ("No","Yes"))
    exposed_springs = st.radio("Exposed springs or moving parts?", ("No","Yes"))
    
    # Cleanliness/maintenance
    overgrown_plants = st.radio("Overgrown plants or weeds?", ("No","Yes"))
    vandalism = st.radio("Graffiti/vandalism affecting safety?", ("No","Yes"))
    
    # Compute danger score
    score = 100
    hazards = [broken_bolts, cracks, unstable_structures, rust, splinters, worn_out_parts,
            slippery, debris, poor_drainage, creaky, exposed_springs, overgrown_plants, vandalism]
    weights = [10,10,10,8,5,7,8,7,5,6,6,3,5]  # example weight per hazard
    for h, w in zip(hazards, weights):
        if h == "Yes":
            score -= w

    st.write(f"Safety Score: {score}/100")

    if score > 70:
        st.warning("Playground looks relatively safe!")
    elif score > 40:
        st.info("Moderate risk detected. Caution advised.")
    else:
        st.success("High risk detected! Supervision and repairs needed.")
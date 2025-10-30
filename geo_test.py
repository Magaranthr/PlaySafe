import streamlit as st
from streamlit_javascript import st_javascript
import json

st.title("🏞️ Playground Safety Checker")

result = st_javascript("""
new Promise((resolve) => {
  if (!navigator.geolocation) {
    resolve(JSON.stringify({error: "not_supported"}));
  } else {
    navigator.geolocation.getCurrentPosition(
      (pos) => resolve(JSON.stringify({
        lat: pos.coords.latitude,
        lng: pos.coords.longitude
      })),
      (err) => resolve(JSON.stringify({error: err.message})),
      {enableHighAccuracy: true, timeout:10000}
    );
  }
});
""")

user_lat, user_lng = 41.8781, -87.6298  # default fallback (Chicago)

if result:
    try:
        data = json.loads(result)
        if "lat" in data and "lng" in data:
            user_lat, user_lng = data["lat"], data["lng"]
            st.success(f"✅ Using precise browser location: ({user_lat:.4f}, {user_lng:.4f})")
        else:
            st.warning(f"⚠️ Location error: {data.get('error', 'Unknown')}")
    except Exception as e:
        st.warning(f"⚠️ Could not parse location: {e}")
else:
    st.warning("⚠️ No location data received (permission blocked or denied).")

st.write("Current coordinates:", user_lat, user_lng)
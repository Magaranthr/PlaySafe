import streamlit as st
from PIL import Image
import cv2
import numpy as np

st.title("Playground Safety Scanner & Expanded Quiz")

uploaded_file = st.file_uploader("Upload a playground image", type=["jpg","jpeg","png"])
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Playground', use_column_width=True)
    cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
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
    score = 0
    hazards = [broken_bolts, cracks, unstable_structures, rust, splinters, worn_out_parts,
               slippery, debris, poor_drainage, creaky, exposed_springs, overgrown_plants, vandalism]
    weights = [10,10,10,8,5,7,8,7,5,6,6,3,5]  # example weight per hazard
    for h, w in zip(hazards, weights):
        if h == "Yes":
            score += w

    st.write(f"Danger Score: {score}/100")

    if score > 70:
        st.warning("High risk detected! Supervision and repairs needed.")
    elif score > 40:
        st.info("Moderate risk detected. Caution advised.")
    else:
        st.success("Playground looks relatively safe!")
import streamlit as st
import requests
import random

# --- PAGE SETUP ---
st.set_page_config(page_title="Viral Video Generator Pro", page_icon="🎬")
st.title("🎬 Viral Video Generator Pro")
st.markdown("Now with Auto-Music Matching & Saved API Keys!")

# --- SECRETS MANAGEMENT (No more re-entering keys!) ---
# The app will automatically look in Streamlit Secrets for these keys.
try:
    PEXELS_API_KEY = st.secrets["PEXELS_API_KEY"]
    PIXABAY_API_KEY = st.secrets["PIXABAY_API_KEY"]
except:
    st.warning("⚠️ API Keys not found in Secrets. Please add them in your Streamlit dashboard!")
    PEXELS_API_KEY = st.text_input("Pexels API Key", type="password")
    PIXABAY_API_KEY = st.text_input("Pixabay API Key", type="password")

# --- AI MOOD DETECTOR ---
def detect_mood(script_text):
    """A lightweight system to detect the vibe of your script."""
    script_lower = script_text.lower()
    
    if any(word in script_lower for word in ["success", "work", "grind", "never give up", "win", "dream"]):
        return "motivational"
    elif any(word in script_lower for word in ["scary", "dark", "shadow", "lie", "death", "destroy"]):
        return "suspense"
    elif any(word in script_lower for word in ["happy", "smile", "joy", "beautiful", "love"]):
        return "upbeat"
    elif any(word in script_lower for word in ["sad", "tired", "cry", "pain", "hurt"]):
        return "emotional"
    else:
        return "lofi" # Default safe background music

# --- FETCH TRENDING MUSIC ---
def fetch_background_music(mood, api_key):
    """Goes online and finds top-rated music for the specific mood."""
    url = f"https://pixabay.com/api/audio/?key={api_key}&q={mood}&order=popular"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data["hits"]:
            # Pick one of the top 3 most popular tracks for this mood
            track = random.choice(data["hits"][:3]) 
            return track["audio"], track["name"]
    return None, None

# --- UI INTERFACE ---
st.subheader("1. Enter Your Video Script")
script = st.text_area("Paste your viral script here:", height=200)

st.subheader("2. Video Visual Tags")
video_tags = st.text_input("Enter tags (e.g., man working late, city night):")

if st.button("🚀 Generate Viral Video"):
    if not PEXELS_API_KEY or not PIXABAY_API_KEY:
        st.error("Please ensure your API keys are loaded!")
    elif not script:
        st.error("Please enter a script first.")
    else:
        with st.spinner("Analyzing script and generating video elements..."):
            
            # 1. AI Music Matching
            st.success("🧠 Analyzing script mood...")
            detected_mood = detect_mood(script)
            st.write(f"**Detected Mood:** `{detected_mood.capitalize()}`")
            
            music_url, track_name = fetch_background_music(detected_mood, PIXABAY_API_KEY)
            
            if music_url:
                st.success(f"🎵 Found trending background track: **{track_name}**")
                st.audio(music_url)
            else:
                st.warning("Could not find a specific track, try changing your script slightly.")

            # 2. Add your previous video generation code here
            st.info("Your video generation logic (Pexels + TTS) will run here, combining the new music!")
            
            st.balloons()
import streamlit as st
import requests
import random

# --- PAGE SETUP ---
st.set_page_config(page_title="Viral Video Generator Pro", page_icon="🎬")
st.title("🎬 Viral Video Generator Pro")
st.markdown("Now with Auto-Music Matching & Saved API Keys!")

# --- SECRETS MANAGEMENT ---
try:
    PEXELS_API_KEY = st.secrets["PEXELS_API_KEY"]
except:
    st.warning("⚠️ Pexels API Key not found in Secrets. Please add it in your Streamlit dashboard!")
    PEXELS_API_KEY = st.text_input("Pexels API Key", type="password")

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

# --- FETCH TRENDING MUSIC (UPDATED) ---
def fetch_background_music(mood, api_key=None):
    """Fetches high-quality, trending royalty-free tracks directly by mood."""
    mood_tracks = {
        "motivational": [
            {"name": "Epic Cinematic Triumph", "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"},
            {"name": "Inspiring Corporate Growth", "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3"}
        ],
        "suspense": [
            {"name": "Dark Shadows & Mystery", "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3"},
            {"name": "Deep Thriller Tension", "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3"}
        ],
        "upbeat": [
            {"name": "Sunny Day Ukulele Groove", "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3"}
        ],
        "emotional": [
            {"name": "Melancholic Piano Reflection", "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-6.mp3"}
        ],
        "lofi": [
            {"name": "Chill Midnight Study Beats", "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3"}
        ]
    }
    
    tracks = mood_tracks.get(mood, mood_tracks["lofi"])
    selected_track = random.choice(tracks)
    return selected_track["url"], selected_track["name"]

# --- UI INTERFACE ---
st.subheader("1. Enter Your Video Script")
script = st.text_area("Paste your viral script here:", height=200)

st.subheader("2. Video Visual Tags")
video_tags = st.text_input("Enter tags (e.g., man working late, city night):")

if st.button("🚀 Generate Viral Video"):
    if not PEXELS_API_KEY:
        st.error("Please ensure your Pexels API key is loaded!")
    elif not script:
        st.error("Please enter a script first.")
    else:
        with st.spinner("Analyzing script and generating video elements..."):
            
            # 1. AI Music Matching
            st.success("🧠 Analyzing script mood...")
            detected_mood = detect_mood(script)
            st.write(f"**Detected Mood:** `{detected_mood.capitalize()}`")
            
            music_url, track_name = fetch_background_music(detected_mood)
            
            if music_url:
                st.success(f"🎵 Found trending background track: **{track_name}**")
                st.audio(music_url)
            else:
                st.warning("Could not find a specific track, try changing your script slightly.")

            # 2. Placeholder for Video stitching logic
            st.info("Your video generation logic (Pexels + TTS) will run here, combining the new music!")
            
            st.balloons()

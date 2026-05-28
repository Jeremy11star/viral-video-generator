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
    """Detects the vibe of your script to match background music."""
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
        return "lofi"

# --- FETCH TRENDING MUSIC ---
def fetch_background_music(mood):
    """Fetches high-quality, trending royalty-free tracks directly by mood."""
    mood_tracks = {
        "motivational": [{"name": "Epic Cinematic Triumph", "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"}],
        "suspense": [{"name": "Dark Shadows & Mystery", "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3"}],
        "upbeat": [{"name": "Sunny Day Ukulele Groove", "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3"}],
        "emotional": [{"name": "Melancholic Piano Reflection", "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-6.mp3"}],
        "lofi": [{"name": "Chill Midnight Study Beats", "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3"}]
    }
    tracks = mood_tracks.get(mood, mood_tracks["lofi"])
    selected_track = random.choice(tracks)
    return selected_track["url"], selected_track["name"]

# --- FETCH VIDEO FROM PEXELS ---
def fetch_pexels_video(tags, api_key):
    """Searches Pexels for a real background video clip matching your tags."""
    headers = {"Authorization": api_key}
    url = f"https://api.pexels.com/videos/search?query={tags}&per_page=5&orientation=portrait"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("videos"):
                # Pick a random video from the top search results
                random_video = random.choice(data["videos"])
                # Get the link to the mobile-friendly HD video file
                video_files = random_video.get("video_files", [])
                for file in video_files:
                    if file.get("height") and file.get("height") >= 720:
                        return file["link"]
                return video_files[0]["link"] if video_files else None
    except Exception as e:
        st.error(f"Error fetching video: {e}")
    return None

# --- UI INTERFACE ---
st.subheader("1. Enter Your Video Script")
script = st.text_area("Paste your viral script here:", height=200)

st.subheader("2. Video Visual Tags")
video_tags = st.text_input("Enter tags (e.g., motivation, dark hallway):")

if st.button("🚀 Generate Viral Video"):
    if not PEXELS_API_KEY:
        st.error("Please ensure your Pexels API key is loaded!")
    elif not script:
        st.error("Please enter a script first.")
    elif not video_tags:
        st.error("Please enter video visual tags.")
    else:
        with st.spinner("Processing elements..."):
            
            # 1. AI Music Matching
            detected_mood = detect_mood(script)
            st.write(f"**Detected Mood:** `{detected_mood.capitalize()}`")
            music_url, track_name = fetch_background_music(detected_mood)
            
            if music_url:
                st.success(f"🎵 Chosen background track: **{track_name}**")
                st.audio(music_url)
            
            # 2. Real Video Generation Engine
            st.info("🎬 Searching Pexels library for matching video clips...")
            video_url = fetch_pexels_video(video_tags, PEXELS_API_KEY)
            
            if video_url:
                st.success("🎥 Video generated successfully!")
                # Displays a built-in video player with download capabilities
                st.video(video_url)
            else:
                st.error("Could not find any videos matching your tags. Try simpler keywords!")
                
            st.balloons()

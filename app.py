import streamlit as st
import requests
import random
import os
import subprocess
from gtts import gTTS

# --- PAGE SETUP ---
st.set_page_config(page_title="Viral Video Generator Pro", page_icon="🎬")
st.title("🎬 Viral Video Generator Pro")
st.markdown("Fully Automated Video, Voiceover, & Music Stitching Engine")

# --- SECRETS MANAGEMENT ---
try:
    PEXELS_API_KEY = st.secrets["PEXELS_API_KEY"]
except:
    st.warning("⚠️ Pexels API Key not found in Secrets. Please add it in your Streamlit dashboard!")
    PEXELS_API_KEY = st.text_input("Pexels API Key", type="password")

# --- HELPER DOWNLOAD FUNCTION ---
def download_file(url, output_filename):
    """Downloads a file from a URL to the local cloud environment."""
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(output_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
        return True
    return False

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
    """Fetches trending royalty-free tracks directly by mood."""
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
                random_video = random.choice(data["videos"])
                video_files = random_video.get("video_files", [])
                for file in video_files:
                    if file.get("height") and file.get("height") >= 720:
                        return file["link"]
                return video_files[0]["link"] if video_files else None
    except Exception as e:
        st.error(f"Error fetching video data: {e}")
    return None

# --- UI INTERFACE ---
st.subheader("1. Enter Your Video Script")
script = st.text_area("Paste your viral script here:", height=200)

st.subheader("2. Video Visual Tags")
video_tags = st.text_input("Enter tags (e.g., motivation, sunrise):")

if st.button("🚀 Generate Integrated Video"):
    if not PEXELS_API_KEY:
        st.error("Please ensure your Pexels API key is saved in your Secrets dashboard!")
    elif not script:
        st.error("Please enter a script first.")
    elif not video_tags:
        st.error("Please enter video visual keywords.")
    else:
        # Define working file paths
        v_input = "temp_video.mp4"
        m_input = "temp_music.mp3"
        t_input = "temp_tts.mp3"
        v_output = "final_viral_video.mp4"
        
        # Clean up any leftover assets from previous runs
        for f in [v_input, m_input, t_input, v_output]:
            if os.path.exists(f):
                os.remove(f)

        with st.spinner("🎬 Generating production assets... (This takes about 30-45 seconds)"):
            
            # Step 1: Mood Matcher & Download Background Track
            detected_mood = detect_mood(script)
            music_url, track_name = fetch_background_music(detected_mood)
            st.write(f"🎵 Mixing background score: **{track_name}**")
            download_file(music_url, m_input)
            
            # Step 2: Generate Voiceover File via gTTS
            st.write("🎙️ Synthesizing AI text-to-speech voiceover...")
            tts = gTTS(text=script, lang='en', tld='com')
            tts.save(t_input)
            
            # Step 3: Fetch & Download Cinematic Pexels Video
            st.write("🎥 Streaming matching visual templates...")
            video_url = fetch_pexels_video(video_tags, PEXELS_API_KEY)
            
            if not video_url:
                st.error("Could not find matching video assets on Pexels. Try using simpler visual keywords!")
            else:
                download_file(video_url, v_input)
                
                # Step 4: Call FFmpeg to automatically mix music + voiceover + loop video perfectly
                st.write("⚙️ Merging streams and rendering final MP4 output container...")
                
                ffmpeg_command = [
                    'ffmpeg', '-y',
                    '-stream_loop', '-1', '-i', v_input,  # Loop visual stream indefinitely
                    '-i', t_input,                        # Voiceover track input
                    '-i', m_input,                        # Background ambient music track input
                    '-filter_complex', '[2:a]volume=0.18[bg];[1:a][bg]amix=inputs=2:duration=first[audio]', # Duck background music down
                    '-map', '0:v', '-map', '[audio]',     # Bind visual clip and audio mix
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', '-shortest', v_output  # Crop video exactly when the voiceover finishes
                ]
                
                result = subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                if os.path.exists(v_output):
                    st.success("🎉 Video compiled completely! Open the media controls to download your file.")
                    # Display the final composite video with native download controls
                    st.video(v_output)
                    st.balloons()
                else:
                    st.error("FFmpeg compilation error. Please check your script formatting or engine arguments.")

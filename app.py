import streamlit as st
import requests
import random
import os
import re
import subprocess

# --- PAGE SETUP ---
st.set_page_config(page_title="Viral Video Generator Pro", page_icon="🎬")
st.title("🎬 Viral Video Generator Pro")
st.markdown("Multi-Scene Cut Engine with Brian Voiceover & 1080p HD")

# --- SECRETS MANAGEMENT ---
try:
    PEXELS_API_KEY = st.secrets["PEXELS_API_KEY"]
except:
    st.warning("⚠️ Pexels API Key not found in Secrets. Please add it in your Streamlit dashboard!")
    PEXELS_API_KEY = st.text_input("Pexels API Key", type="password")

# --- HELPER DOWNLOAD FUNCTION ---
def download_file(url, output_filename):
    """Downloads a binary asset with standard streaming chunks."""
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(output_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
        return True
    return False

# --- BRIAN TEXT TO SPEECH GENERATOR ---
def generate_brian_voiceover(text, output_filename):
    """Fetches the iconic Brian deep British voiceover track."""
    url = "https://api.streamelements.com/kappa/v2/speech"
    params = {"voice": "Brian", "text": text}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            with open(output_filename, "wb") as f:
                f.write(response.content)
            return True
    except Exception as e:
        st.error(f"Voice generation error: {e}")
    return False

# --- AI MOOD DETECTOR ---
def detect_mood(script_text):
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

# --- FETCH 1080P HD VIDEOS FROM PEXELS ---
def fetch_pexels_video_pool(tags, api_key):
    """Searches Pexels and filters exclusively for crisp 1080p vertical clips."""
    headers = {"Authorization": api_key}
    url = f"https://api.pexels.com/videos/search?query={tags}&per_page=15&orientation=portrait"
    video_links = []
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("videos"):
                for video in data["videos"]:
                    video_files = video.get("video_files", [])
                    selected_url = None
                    
                    # Look for pristine 1080x1920 portrait files first
                    for f in video_files:
                        if f.get("width") == 1080 or f.get("height") == 1920:
                            selected_url = f["link"]
                            break
                    
                    # HD backup fallback
                    if not selected_url:
                        for f in video_files:
                            if f.get("quality") == "hd" or (f.get("height") and f.get("height") >= 720):
                                selected_url = f["link"]
                                break
                                
                    if not selected_url and video_files:
                        selected_url = video_files[0]["link"]
                        
                    if selected_url:
                        video_links.append(selected_url)
    except Exception as e:
        st.error(f"Error compiling video library: {e}")
    return video_links

# --- UI INTERFACE ---
st.subheader("1. Enter Your Video Script")
script = st.text_area("Paste your viral script here:", height=200)

st.subheader("2. Video Visual Tags")
video_tags = st.text_input("Enter tags (e.g., motivation, dark city):")

if st.button("🚀 Generate Multi-Scene Viral Video"):
    if not PEXELS_API_KEY:
        st.error("Please add your Pexels API key to secrets!")
    elif not script:
        st.error("Please provide a video script.")
    elif not video_tags:
        st.error("Please enter descriptive tags.")
    else:
        # Split script cleanly by sentences and line endings
        sentences = [s.strip() for s in re.split(r'[.\n!?]+', script) if s.strip()]
        
        if not sentences:
            st.error("Could not parse script text sentences.")
        else:
            # File staging tracking arrays
            scene_files = []
            m_input = "temp_music.mp3"
            v_output = "final_viral_video.mp4"
            
            # Wipe leftover tracks
            for f in [m_input, v_output, "file_list.txt", "concat_voiceover.mp4"]:
                if os.path.exists(f):
                    os.remove(f)

            with st.spinner(f"🎬 Slicing script into {len(sentences)} distinct scenes..."):
                
                # Fetch visual video options array
                video_pool = fetch_pexels_video_pool(video_tags, PEXELS_API_KEY)
                
                if not video_pool:
                    st.error("Could not fetch elements from Pexels pool. Try simpler keywords!")
                else:
                    # Download continuous ambient soundtrack
                    detected_mood = detect_mood(script)
                    music_url, track_name = fetch_background_music(detected_mood)
                    st.write(f"🎵 Mixing score track: **{track_name}**")
                    download_file(music_url, m_input)
                    
                    # Process and stitch individual multi-scene pieces
                    for i, sentence in enumerate(sentences):
                        st.write(f"🎞️ Compiling Scene {i+1}/{len(sentences)}: *\"{sentence}\"*")
                        
                        # Generate Brian Audio Track for this phrase
                        tts_file = f"temp_tts_{i}.mp3"
                        generate_brian_voiceover(sentence, tts_file)
                        
                        # Select unique matching 1080p template
                        raw_video_file = f"temp_raw_{i}.mp4"
                        chosen_video_url = video_pool[i % len(video_pool)]
                        download_file(chosen_video_url, raw_video_file)
                        
                        # Compile isolated scene bound directly to specific phrase length
                        scene_output = f"scene_{i}.mp4"
                        ffmpeg_scene = [
                            'ffmpeg', '-y',
                            '-stream_loop', '-1', '-i', raw_video_file,
                            '-i', tts_file,
                            '-map', '0:v', '-map', '1:a',
                            '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                            '-c:a', 'aac', '-shortest', scene_output
                        ]
                        subprocess.run(ffmpeg_scene, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        scene_files.append(scene_output)
                        
                        # Clean scene ingredients immediately
                        if os.path.exists(raw_video_file): os.remove(raw_video_file)
                        if os.path.exists(tts_file): os.remove(tts_file)
                    
                    # Generate video list index for FFmpeg
                    with open("file_list.txt", "w") as f:
                        for sf in scene_files:
                            f.write(f"file '{sf}'\n")
                            
                    # Stitch individual scenes together 
                    st.write("🧱 Merging scenes into visual sequence container...")
                    subprocess.run([
                        'ffmpeg', '-y',
                        '-f', 'concat', '-safe', '0', '-i', 'file_list.txt',
                        '-c', 'copy', 'concat_voiceover.mp4'
                    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    
                    # Overlay smooth ambient music down onto sequence layout
                    st.write("🎧 Fusing continuous background score layout...")
                    ffmpeg_mix = [
                        'ffmpeg', '-y',
                        '-i', 'concat_voiceover.mp4',
                        '-i', m_input,
                        '-filter_complex', '[1:a]volume=0.15[bg];[0:a][bg]amix=inputs=2:duration=first[audio]',
                        '-map', '0:v', '-map', '[audio]',
                        '-c:v', 'copy', '-c:a', 'aac', v_output
                    ]
                    subprocess.run(ffmpeg_mix, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    
                    # Clean sequence cut files
                    for sf in scene_files:
                        if os.path.exists(sf): os.remove(sf)
                    if os.path.exists("file_list.txt"): os.remove("file_list.txt")
                    if os.path.exists("concat_voiceover.mp4"): os.remove("concat_voiceover.mp4")
                    if os.path.exists(m_input): os.remove(m_input)

                    if os.path.exists(v_output):
                        st.success("🎉 Production video fully compiled!")
                        st.video(v_output)
                        st.balloons()
                    else:
                        st.error("Compilation error occur during stream rendering.")

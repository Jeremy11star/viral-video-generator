import streamlit as st
import requests
import os
import re
import subprocess

# --- PAGE SETUP ---
st.set_page_config(page_title="Viral Video Generator Pro", page_icon="🎬")
st.title("🎬 Viral Video Generator Pro")

# --- SECRETS MANAGEMENT ---
try:
    PEXELS_API_KEY = st.secrets["PEXELS_API_KEY"]
except:
    PEXELS_API_KEY = st.text_input("Pexels API Key", type="password")

def download_file(url, output_filename):
    try:
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200:
            with open(output_filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=512*1024): # Smaller chunks to save RAM
                    if chunk: f.write(chunk)
            return True
    except:
        return False
    return False

def generate_brian_voiceover(text, output_filename):
    url = "https://api.streamelements.com/kappa/v2/speech"
    params = {"voice": "Brian", "text": text}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            with open(output_filename, "wb") as f:
                f.write(response.content)
            return True
    except:
        return False

# --- CORE GENERATOR ---
st.subheader("1. Enter Your Video Script")
script = st.text_area("Script:", height=150)
video_tags = st.text_input("Tags (e.g., motivation):")

if st.button("🚀 Generate Video"):
    if not script or not video_tags or not PEXELS_API_KEY:
        st.error("Missing input or API key!")
    else:
        sentences = [s.strip() for s in re.split(r'[.\n!?]+', script) if s.strip()]
        scene_files = []
        
        with st.spinner("Processing scenes (this might take a minute)..."):
            # Fetch just 3-4 scenes to save memory
            headers = {"Authorization": PEXELS_API_KEY}
            url = f"https://api.pexels.com/videos/search?query={video_tags}&per_page=4&orientation=portrait"
            data = requests.get(url, headers=headers).json()
            video_pool = [v["video_files"][0]["link"] for v in data.get("videos", [])[:4]]
            
            if not video_pool:
                st.error("Pexels error. Try different tags.")
            else:
                for i, sentence in enumerate(sentences[:4]): # Limit to first 4 sentences to prevent crashing
                    tts = f"tts_{i}.mp3"
                    raw = f"raw_{i}.mp4"
                    scene = f"scene_{i}.mp4"
                    
                    generate_brian_voiceover(sentence, tts)
                    download_file(video_pool[i % len(video_pool)], raw)
                    
                    # Light memory command: -crf 28 (lower quality) + -preset superfast
                    cmd = [
                        'ffmpeg', '-y', '-stream_loop', '-1', '-i', raw, '-i', tts,
                        '-filter_complex', '[0:v]scale=720:1280[v]', # Downscale to 720p for memory
                        '-map', '[v]', '-map', '1:a', '-c:v', 'libx264', '-crf', '28', 
                        '-preset', 'superfast', '-c:a', 'aac', '-shortest', scene
                    ]
                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    scene_files.append(scene)
                    if os.path.exists(raw): os.remove(raw)
                    if os.path.exists(tts): os.remove(tts)

                # Final stitch
                with open("list.txt", "w") as f:
                    for s in scene_files: f.write(f"file '{s}'\n")
                
                subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', 'list.txt', '-c', 'copy', 'final.mp4'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                if os.path.exists("final.mp4"):
                    st.success("🎉 Success!")
                    st.video("final.mp4")
                else:
                    st.error("Failed to compile. The server ran out of memory.")

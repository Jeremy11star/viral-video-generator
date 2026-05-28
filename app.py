import streamlit as st
import requests
import os
import re
import subprocess

st.set_page_config(page_title="Viral Video Generator", page_icon="🎬")
st.title("🎬 Viral Video Generator (720p HD Optimized)")

# --- SECRETS ---
try:
    PEXELS_API_KEY = st.secrets["PEXELS_API_KEY"]
except:
    PEXELS_API_KEY = st.text_input("Pexels API Key", type="password")

def download_file(url, output_filename):
    try:
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200:
            with open(output_filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=512*1024):
                    if chunk: f.write(chunk)
            return True
    except: return False
    return False

# --- UI & LOGIC ---
script = st.text_area("Script:", height=100)
video_tags = st.text_input("Tags:")

if st.button("🚀 Generate (720p Optimized)"):
    if not script or not video_tags or not PEXELS_API_KEY:
        st.error("Missing input or API key!")
    else:
        sentences = [s.strip() for s in re.split(r'[.\n!?]+', script) if s.strip()]
        scene_files = []
        
        with st.spinner("Compiling video..."):
            # Fetch 3 scenes max to keep RAM low
            headers = {"Authorization": PEXELS_API_KEY}
            url = f"https://api.pexels.com/videos/search?query={video_tags}&per_page=3&orientation=portrait"
            data = requests.get(url, headers=headers).json()
            video_pool = [v["video_files"][0]["link"] for v in data.get("videos", [])[:3]]
            
            for i, sentence in enumerate(sentences[:3]):
                tts, raw, scene = f"tts_{i}.mp3", f"raw_{i}.mp4", f"scene_{i}.mp4"
                
                # Fetch TTS
                res = requests.get("https://api.streamelements.com/kappa/v2/speech", params={"voice": "Brian", "text": sentence})
                with open(tts, "wb") as f: f.write(res.content)
                download_file(video_pool[i % len(video_pool)], raw)
                
                # 720p scaling (720x1280) is the key to preventing the crash
                cmd = [
                    'ffmpeg', '-y', '-stream_loop', '-1', '-i', raw, '-i', tts,
                    '-filter_complex', '[0:v]scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2[v]',
                    '-map', '[v]', '-map', '1:a', '-c:v', 'libx264', '-crf', '28', 
                    '-preset', 'veryfast', '-c:a', 'aac', '-shortest', scene
                ]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                scene_files.append(scene)
                
            # Stitch
            with open("list.txt", "w") as f:
                for s in scene_files: f.write(f"file '{s}'\n")
            
            subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', 'list.txt', '-c', 'copy', 'final.mp4'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            if os.path.exists("final.mp4"):
                st.success("🎉 Video Ready!")
                st.video("final.mp4")
            else:
                st.error("Failed to compile. Try an even shorter script.")

import google.generativeai as genai
import json
import os
import streamlit as st
from gtts import gTTS
from moviepy.editor import AudioFileClip, ImageClip

# Menarik API Key dari brankas rahasia Streamlit
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# ... (sisa kode di bawahnya tetap sama) ...

def split_script_to_json(raw_script, base_character):
    """Memecah naskah menjadi segmen 8 detik & injeksi prompt sinematik"""
    prompt = f"""
    Pecah naskah ini menjadi segmen-segmen video untuk algoritma media sosial.
    ATURAN:
    1. Durasi tiap segmen HARUS diformat untuk tepat 8 detik saat dibaca (sekitar 15-20 kata).
    2. Buat instruksi 'cinematic_prompt' tingkat Hollywood (lensa, pencahayaan, depth of field) yang mengikutsertakan karakter dasar: "{base_character}".
    3. Output HANYA JSON array: [{{"order": 1, "text": "...", "prompt": "..."}}]
    Naskah: {raw_script}
    """
    response = model.generate_content(prompt)
    clean_json = response.text.replace("```json\n", "").replace("\n```", "").strip()
    return json.loads(clean_json)

def generate_voiceover(text, segment_id):
    """Menghasilkan audio menggunakan Google TTS (Gratis/Lean)"""
    os.makedirs('assets/audio', exist_ok=True)
    file_path = f"assets/audio/seg_{segment_id}.mp3"
    tts = gTTS(text=text, lang='id', slow=False)
    tts.save(file_path)
    return file_path

def simulate_image_generation(prompt, segment_id):
    """
    (Placeholder) Di sini Anda memanggil API Image Generator (Midjourney/Flux).
    Untuk sementara, kita asumsikan file gambar sudah tersedia.
    """
    os.makedirs('assets/images', exist_ok=True)
    # Anda akan mengganti ini dengan request.post ke API pilihan
    file_path = f"assets/images/placeholder.jpg" 
    return file_path

def compile_video_segment(image_path, audio_path, segment_id):
    """Menggabungkan Gambar dan Audio menjadi Video MP4 (MVP Mode)"""
    os.makedirs('assets/video', exist_ok=True)
    out_path = f"assets/video/final_seg_{segment_id}.mp4"
    
    audio = AudioFileClip(audio_path)
    # Gambar statis menyesuaikan durasi audio persis (format UGC cepat)
    image = ImageClip(image_path).set_duration(audio.duration) 
    
    video = image.set_audio(audio)
    video.write_videofile(out_path, fps=24, codec="libx264", audio_codec="aac")
    return out_path

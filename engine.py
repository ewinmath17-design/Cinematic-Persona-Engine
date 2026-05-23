import google.generativeai as genai
import json
import os
import streamlit as st
from gtts import gTTS
from moviepy.editor import AudioFileClip, ImageClip

# Menarik API Key dari brankas rahasia Streamlit
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# Menggunakan model terbaru yang paling stabil di ekosistem API
model = genai.GenerativeModel('gemini-pro')

def split_script_to_json(raw_script, base_character):
    """Memecah naskah menjadi segmen 8 detik & injeksi prompt sinematik"""
    prompt = f"""
    Pecah naskah ini menjadi segmen-segmen video untuk algoritma media sosial.
    ATURAN:
    1. Durasi tiap segmen HARUS diformat untuk tepat 8 detik saat dibaca (sekitar 15-20 kata).
    2. Buat instruksi 'cinematic_prompt' tingkat Hollywood (lensa, pencahayaan, depth of field) yang mengikutsertakan karakter dasar: "{base_character}".
    3. Output HANYA JSON array murni tanpa format markdown: [{{"order": 1, "text": "...", "prompt": "..."}}]
    
    Naskah: {raw_script}
    """
    
    response = model.generate_content(prompt)
    
    # Membersihkan format markdown yang kadang ditambahkan oleh AI
    clean_json = response.text.replace("```json\n", "").replace("\n```", "").replace("```", "").strip()
    
    try:
        return json.loads(clean_json)
    except json.JSONDecodeError:
        # Failsafe agar aplikasi web tidak crash jika format AI meleset sedikit
        return [{"order": 1, "text": "Maaf, terjadi kesalahan format dari AI. Silakan coba lagi.", "prompt": "Error processing prompt."}]

def generate_voiceover(text, segment_id):
    """Menghasilkan audio menggunakan Google TTS (MVP/Lean)"""
    os.makedirs('assets/audio', exist_ok=True)
    file_path = f"assets/audio/seg_{segment_id}.mp3"
    
    tts = gTTS(text=text, lang='id', slow=False)
    tts.save(file_path)
    return file_path

def simulate_image_generation(prompt, segment_id):
    """
    Placeholder untuk API Image Generator sesungguhnya (Midjourney/Flux).
    Otomatis membuat gambar warna solid sementara agar MoviePy bisa melakukan render.
    """
    os.makedirs('assets/images', exist_ok=True)
    file_path = f"assets/images/placeholder.jpg" 
    
    # Failsafe: Buat gambar dummy 9:16 (Tiktok/Reels) jika file belum ada
    if not os.path.exists(file_path):
        from PIL import Image
        img = Image.new('RGB', (1080, 1920), color = (25, 25, 25))
        img.save(file_path)

    return file_path

def compile_video_segment(image_path, audio_path, segment_id):
    """Menggabungkan Gambar statis dan Audio menjadi Video MP4"""
    os.makedirs('assets/video', exist_ok=True)
    out_path = f"assets/video/final_seg_{segment_id}.mp4"
    
    audio = AudioFileClip(audio_path)
    
    # Menyamakan durasi gambar persis dengan panjang durasi voiceover
    image = ImageClip(image_path).set_duration(audio.duration) 
    
    video = image.set_audio(audio)
    video.write_videofile(out_path, fps=24, codec="libx264", audio_codec="aac", logger=None)
    
    # Membersihkan memori sistem setelah render
    audio.close()
    video.close()
    
    return out_path

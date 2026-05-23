import google.generativeai as genai
import json
import os
import streamlit as st
from gtts import gTTS
from moviepy.editor import AudioFileClip, ImageClip

# Menarik API Key dari brankas rahasia Streamlit
api_key = st.secrets.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# ==========================================
# SMART AUTO-DETECT (ANTI-404 & ANTI-429)
# ==========================================
def get_best_free_model():
    try:
        # Menarik daftar mesin yang aktif diizinkan untuk API Key ini
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Secara otomatis mencari varian 'flash' berapapun versinya (Ini adalah jalur gratis/Free Tier)
        for m in available_models:
            if 'flash' in m.lower():
                return m
                
        # Fallback jika tidak ada tulisan flash, ambil model pertama yang tersedia
        if available_models:
            return available_models[0]
            
        return 'models/gemini-1.0-pro'
    except Exception:
        return 'models/gemini-1.0-pro'

# Inisialisasi model secara otomatis sesuai hasil deteksi
best_model_name = get_best_free_model()
model = genai.GenerativeModel(best_model_name)

# ==========================================
# CORE LOGIC PRODUKSI VIDEO
# ==========================================
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
    
    try:
        response = model.generate_content(prompt)
        clean_json = response.text.replace("```json\n", "").replace("\n```", "").replace("```", "").strip()
        return json.loads(clean_json)
    except Exception as e:
        st.error(f"Gagal memproses naskah dengan Google AI. Detail Error: {str(e)}")
        return []

def generate_voiceover(text, segment_id):
    """Menghasilkan audio menggunakan Google TTS"""
    os.makedirs('assets/audio', exist_ok=True)
    file_path = f"assets/audio/seg_{segment_id}.mp3"
    
    tts = gTTS(text=text, lang='id', slow=False)
    tts.save(file_path)
    return file_path

def simulate_image_generation(prompt, segment_id):
    """Membuat gambar layar hitam sebagai placeholder agar engine video bisa merender."""
    os.makedirs('assets/images', exist_ok=True)
    file_path = f"assets/images/placeholder_seg_{segment_id}.jpg" 
    
    if not os.path.exists(file_path):
        from PIL import Image
        img = Image.new('RGB', (1080, 1920), color=(15, 15, 15))
        img.save(file_path)

    return file_path

def compile_video_segment(image_path, audio_path, segment_id):
    """Menggabungkan Gambar dan Audio menjadi Video MP4"""
    os.makedirs('assets/video', exist_ok=True)
    out_path = f"assets/video/final_seg_{segment_id}.mp4"
    
    audio = AudioFileClip(audio_path)
    image = ImageClip(image_path).set_duration(audio.duration) 
    
    video = image.set_audio(audio)
    video.write_videofile(out_path, fps=24, codec="libx264", audio_codec="aac", logger=None)
    
    audio.close()
    video.close()
    
    return out_path

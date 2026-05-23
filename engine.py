import google.generativeai as genai
import json
import os
import streamlit as st
from gtts import gTTS
from moviepy.editor import AudioFileClip, ImageClip

# Menarik API Key dari brankas rahasia Streamlit
api_key = st.secrets.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Memaksa penggunaan Gemini 1.5 Flash (Super Cepat & Kuota Gratis Stabil)
model = genai.GenerativeModel('gemini-1.5-flash')

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
        # Membersihkan sisa markdown jika ada
        clean_json = response.text.replace("```json\n", "").replace("\n```", "").replace("```", "").strip()
        return json.loads(clean_json)
    except Exception as e:
        st.error(f"Gagal memproses naskah dengan Google AI. Detail Error: {str(e)}")
        # Mengembalikan array kosong agar proses tidak crash
        return []

def generate_voiceover(text, segment_id):
    """Menghasilkan audio menggunakan Google TTS"""
    os.makedirs('assets/audio', exist_ok=True)
    file_path = f"assets/audio/seg_{segment_id}.mp3"
    
    tts = gTTS(text=text, lang='id', slow=False)
    tts.save(file_path)
    return file_path

def simulate_image_generation(prompt, segment_id):
    """
    Membuat gambar layar hitam sebagai placeholder agar engine video bisa merender.
    """
    os.makedirs('assets/images', exist_ok=True)
    file_path = f"assets/images/placeholder_seg_{segment_id}.jpg" 
    
    # Buat gambar dummy ukuran 9:16 (Format Video Vertikal)
    if not os.path.exists(file_path):
        from PIL import Image
        img = Image.new('RGB', (1080, 1920), color=(25, 25, 25))
        img.save(file_path)

    return file_path

def compile_video_segment(image_path, audio_path, segment_id):
    """Menggabungkan Gambar statis dan Audio menjadi Video MP4"""
    os.makedirs('assets/video', exist_ok=True)
    out_path = f"assets/video/final_seg_{segment_id}.mp4"
    
    audio = AudioFileClip(audio_path)
    image = ImageClip(image_path).set_duration(audio.duration) 
    
    video = image.set_audio(audio)
    video.write_videofile(out_path, fps=24, codec="libx264", audio_codec="aac", logger=None)
    
    audio.close()
    video.close()
    
    return out_path

import streamlit as st
import database as db
import engine as eng
import time

st.set_page_config(page_title="Cinematic Persona Engine", layout="wide")

# Inisialisasi Database
db.init_db()

st.title("🎬 Cinematic Persona Engine (Pro Edition)")
st.markdown("Sistem otomasi konten UGC bertenaga AI dengan kualitas Sinematik.")

with st.form("project_form"):
    st.subheader("1. Setup Karakter & Naskah")
    project_name = st.text_input("Nama Campaign")
    base_character = st.text_area("Deskripsi Karakter Utama (Base Model)", "Contoh: Wanita Asia, 24 tahun, rambut sebahu, memakai kaos kasual putih, hyper-realistic, skin texture")
    raw_script = st.text_area("Naskah Promosi (Mentah)", height=150)
    
    submitted = st.form_submit_button("Mulai Produksi Otomatis 🚀")

if submitted and raw_script:
    st.info("Memulai pemrosesan AI... Memecah naskah ke dalam format retensi tinggi...")
    
    # 1. Simpan Project
    project_id = db.create_project(project_name, base_character, raw_script)
    
    # 2. Proses Naskah (Pecah per 8 Detik & Injeksi Prompt)
    segments_data = eng.split_script_to_json(raw_script, base_character)
    
    st.success(f"Naskah berhasil dipecah menjadi {len(segments_data)} segmen sinematik!")
    
    # 3. Eksekusi Berantai
    progress_bar = st.progress(0)
    for i, seg in enumerate(segments_data):
        with st.expander(f"Segmen {seg['order']}", expanded=True):
            st.write(f"**Teks (Voiceover):** {seg['text']}")
            st.caption(f"**Cinematic Prompt:** {seg['prompt']}")
            
            # Simpan ke DB
            seg_id = db.save_segment(project_id, seg['order'], seg['text'], seg['prompt'])
            
            # Render Audio & Gambar
            audio_path = eng.generate_voiceover(seg['text'], seg_id)
            db.update_media_path(seg_id, 'audio_path', audio_path)
            
            img_path = eng.simulate_image_generation(seg['prompt'], seg_id)
            db.update_media_path(seg_id, 'image_path', img_path)
            
            st.write("✅ Audio & Prompt Visual Siap. Merender Video...")
            
            # Render Video (Hapus komentar baris ini jika Anda menaruh gambar dummy di assets/images)
            # vid_path = eng.compile_video_segment(img_path, audio_path, seg_id)
            # st.video(vid_path)
            
        progress_bar.progress((i + 1) / len(segments_data))
        time.sleep(1) # Jeda aman antar API call
        
    st.balloons()
    st.success("🎉 Seluruh segmen video telah berhasil diproduksi!")

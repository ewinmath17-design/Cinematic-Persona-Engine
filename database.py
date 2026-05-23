import sqlite3
import datetime

def init_db():
    conn = sqlite3.connect('cinematic_engine.db')
    c = conn.cursor()
    
    # Tabel Projects
    c.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT,
            base_character TEXT,
            raw_script TEXT,
            created_at TIMESTAMP
        )
    ''')
    
    # Tabel Segments
    c.execute('''
        CREATE TABLE IF NOT EXISTS segments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            order_index INTEGER,
            voiceover_text TEXT,
            cinematic_prompt TEXT,
            audio_path TEXT,
            image_path TEXT,
            video_path TEXT,
            FOREIGN KEY(project_id) REFERENCES projects(id)
        )
    ''')
    conn.commit()
    conn.close()

def create_project(name, character, script):
    conn = sqlite3.connect('cinematic_engine.db')
    c = conn.cursor()
    c.execute("INSERT INTO projects (project_name, base_character, raw_script, created_at) VALUES (?, ?, ?, ?)",
              (name, character, script, datetime.datetime.now()))
    project_id = c.lastrowid
    conn.commit()
    conn.close()
    return project_id

def save_segment(project_id, order, text, prompt):
    conn = sqlite3.connect('cinematic_engine.db')
    c = conn.cursor()
    c.execute("INSERT INTO segments (project_id, order_index, voiceover_text, cinematic_prompt) VALUES (?, ?, ?, ?)",
              (project_id, order, text, prompt))
    segment_id = c.lastrowid
    conn.commit()
    conn.close()
    return segment_id

def update_media_path(segment_id, column, path):
    conn = sqlite3.connect('cinematic_engine.db')
    c = conn.cursor()
    c.execute(f"UPDATE segments SET {column} = ? WHERE id = ?", (path, segment_id))
    conn.commit()
    conn.close()

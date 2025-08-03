import sqlite3
import os
import pickle
import cv2

DB_NAME = "faces.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS faces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    encoding BLOB,
                    is_child INTEGER,
                    parent_id INTEGER,
                    child_id INTEGER
                )''')
    conn.commit()
    conn.close()

def save_face(name, encoding, is_child=False, related_id=None, image=None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    enc_blob = pickle.dumps(encoding)
    if is_child:
        c.execute("INSERT INTO faces (name, encoding, is_child, parent_id) VALUES (?, ?, ?, ?)",
                  (name, enc_blob, 1, related_id))
    else:
        c.execute("INSERT INTO faces (name, encoding, is_child, child_id) VALUES (?, ?, ?, ?)",
                  (name, enc_blob, 0, related_id))
    conn.commit()
    conn.close()
     # Сохраняем изображение, если передано
    if image is not None:
        folder = "Faces/children" if is_child else "Faces/adults"
        os.makedirs(folder, exist_ok=True)
        filename = f"{folder}/{name}_{c.lastrowid}.jpg"
        cv2.imwrite(filename, image)

def get_all_faces():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, name, is_child, parent_id, child_id FROM faces")
    rows = c.fetchall()
    conn.close()
    return rows

def delete_face(face_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT is_child FROM faces WHERE id = ?", (face_id,))
    result = c.fetchone()
    if not result:
        return None
    c.execute("DELETE FROM faces WHERE id = ?", (face_id,))
    conn.commit()
    conn.close()
    return result

def get_faces_encodings():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, name, encoding FROM faces")
    rows = c.fetchall()
    conn.close()
    return [(row[0], row[1], pickle.loads(row[2])) for row in rows]

def get_related_by_id(face_id, role='child'):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    if role == 'child':
        c.execute("SELECT name FROM faces WHERE parent_id = ?", (face_id,))
    elif role == 'parent':
        c.execute("""
            SELECT f2.name FROM faces f1
            JOIN faces f2 ON f1.parent_id = f2.id
            WHERE f1.id = ?
        """, (face_id,))
    else:
        conn.close()
        return []

    results = c.fetchall()
    conn.close()
    return [row[0] for row in results] if results else []


def link_faces(parent_id, child_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute('UPDATE faces SET parent_id = ? WHERE id = ? AND is_child = 1', (parent_id, child_id))
        c.execute('UPDATE faces SET child_id = ? WHERE id = ? AND is_child = 0', (child_id, parent_id))
        conn.commit()
    finally:
        conn.close()

def get_face_by_id(face_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, name, is_child FROM faces WHERE id = ?", (face_id,))
    result = c.fetchone()
    conn.close()
    return result


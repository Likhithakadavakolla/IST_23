import os
import sqlite3

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'instance', 'edureach.db')

conn = sqlite3.connect(db_path)
try:
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(progress)")
    cols = {row[1] for row in cur.fetchall()}

    to_add = []
    if 'video_progress' not in cols:
        to_add.append(("video_progress", "TEXT"))
    if 'score' not in cols:
        to_add.append(("score", "FLOAT DEFAULT 0.0"))
    if 'completed' not in cols:
        to_add.append(("completed", "BOOLEAN DEFAULT 0"))
    if 'completed_at' not in cols:
        to_add.append(("completed_at", "DATETIME"))

    for name, sqltype in to_add:
        stmt = f"ALTER TABLE progress ADD COLUMN {name} {sqltype}"
        print(f"Applying: {stmt}")
        cur.execute(stmt)
    if to_add:
        conn.commit()
        print("Progress table updated: " + ", ".join(name for name, _ in to_add))
    else:
        print("Progress table already up to date.")
finally:
    conn.close()

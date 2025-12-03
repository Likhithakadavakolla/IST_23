import os
import sqlite3
import sys

# Use app config to locate the DB path
try:
    from app import app
except Exception as e:
    print(f"Error importing app to read config: {e}")
    sys.exit(1)

uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///edureach.db')
if not uri.startswith('sqlite:///'):
    print(f"Unsupported DB URI for this quick migration: {uri}")
    sys.exit(1)

rel_path = uri.replace('sqlite:///', '', 1)
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = rel_path if os.path.isabs(rel_path) else os.path.join(base_dir, rel_path)

# If not found at base_dir, try Flask instance path (Flask often stores SQLite here)
if not os.path.exists(db_path):
    instance_path = getattr(app, 'instance_path', None)
    if instance_path:
        candidate = rel_path if os.path.isabs(rel_path) else os.path.join(instance_path, rel_path)
        if os.path.exists(candidate):
            db_path = candidate

if not os.path.exists(db_path):
    print(f"Database file not found at {db_path}. If this is expected, start the app once to create it.")
    sys.exit(1)

print(f"Using database: {db_path}")

conn = sqlite3.connect(db_path)
try:
    cur = conn.cursor()

    # Get existing columns on 'course'
    cur.execute("PRAGMA table_info(course)")
    cols = {row[1] for row in cur.fetchall()}  # row[1] is column name

    to_add = []
    if 'class_level' not in cols:
        to_add.append(("class_level", "VARCHAR(20)"))
    if 'video_data' not in cols:
        to_add.append(("video_data", "TEXT"))

    if not to_add:
        print("No changes needed: required columns already present.")
    else:
        for name, sqltype in to_add:
            stmt = f"ALTER TABLE course ADD COLUMN {name} {sqltype}"
            print(f"Applying: {stmt}")
            cur.execute(stmt)
        conn.commit()
        print("Migration complete: columns added -> " + ", ".join(name for name, _ in to_add))

finally:
    conn.close()

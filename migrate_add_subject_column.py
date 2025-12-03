import os
import sys
import sqlite3

try:
    from app import app
except Exception as e:
    print(f"Error importing app: {e}")
    sys.exit(1)

uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///instance/edureach.db')
if not uri.startswith('sqlite:///'):
    print(f"Unsupported DB URI: {uri}")
    sys.exit(1)

rel_path = uri.replace('sqlite:///', '', 1)
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = rel_path if os.path.isabs(rel_path) else os.path.join(base_dir, rel_path)
if not os.path.exists(db_path):
    instance_path = getattr(app, 'instance_path', None)
    if instance_path:
        candidate = rel_path if os.path.isabs(rel_path) else os.path.join(instance_path, os.path.basename(rel_path))
        if os.path.exists(candidate):
            db_path = candidate

if not os.path.exists(db_path):
    print(f"Database file not found at {db_path}")
    sys.exit(1)

print(f"Using database: {db_path}")

conn = sqlite3.connect(db_path)
try:
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(course)")
    cols = {row[1] for row in cur.fetchall()}
    to_add = []
    if 'subject' not in cols:
        to_add.append(("subject", "VARCHAR(50) DEFAULT ''"))
    if to_add:
        for name, sqltype in to_add:
            stmt = f"ALTER TABLE course ADD COLUMN {name} {sqltype}"
            print(f"Applying: {stmt}")
            cur.execute(stmt)
        conn.commit()
        print("Migration complete: added " + ", ".join(name for name, _ in to_add))
    else:
        print("No migration needed.")
finally:
    conn.close()

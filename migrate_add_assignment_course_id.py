import os
import sqlite3

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'instance', 'edureach.db')

conn = sqlite3.connect(db_path)
try:
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(assignment)")
    cols = {row[1] for row in cur.fetchall()}
    to_add = []
    if 'course_id' not in cols:
        to_add.append(("course_id", "INTEGER"))
    for name, sqltype in to_add:
        stmt = f"ALTER TABLE assignment ADD COLUMN {name} {sqltype}"
        print(f"Applying: {stmt}")
        cur.execute(stmt)
    if to_add:
        conn.commit()
        print("Migration complete: added " + ", ".join(n for n, _ in to_add))
    else:
        print("No migration needed (assignment.course_id exists).")
finally:
    conn.close()

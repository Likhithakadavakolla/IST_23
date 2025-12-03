import re
import json
import os
import sqlite3

# Mapping pasted from user (titles and URLs)
LINKS = {
  "9th": {
    "Physics": [
      {"title": "Motion and Speed", "url": "https://www.youtube.com/watch?v=9TaYb9bm2xg"},
      {"title": "Newton’s Laws of Motion", "url": "https://www.youtube.com/watch?v=83yFHYsJd-0"},
      {"title": "Gravitation and Free Fall", "url": "https://www.youtube.com/watch?v=RCz7nT8rZ8s"},
      {"title": "Work, Energy, and Power", "url": "https://www.youtube.com/watch?v=XK_xG2QyaHQ"},
      {"title": "Sound – Properties and Applications", "url": "https://www.youtube.com/watch?v=G1zwP1LIm-E"},
      {"title": "Light – Reflection and Refraction", "url": "https://www.youtube.com/watch?v=hgsx7mtZcJ0"},
      {"title": "Pressure in Fluids", "url": "https://www.youtube.com/watch?v=FwniY0bQhWk"},
      {"title": "Heat and Temperature", "url": "https://www.youtube.com/watch?v=5ImdPXt9gSI"},
      {"title": "Force and Friction", "url": "https://www.youtube.com/watch?v=GbnAi4-XqAo"},
      {"title": "Electricity – Basics", "url": "https://www.youtube.com/watch?v=f4kDgE7YoIU"}
    ],
    "Chemistry": [
      {"title": "Matter – Properties and States", "url": "https://www.youtube.com/watch?v=GZn3s7YDZ_8"},
      {"title": "Elements, Compounds & Mixtures", "url": "https://www.youtube.com/watch?v=Wc1R24h0jLk"},
      {"title": "Atomic Structure – Introduction", "url": "https://www.youtube.com/watch?v=hhdXvY5DPOQ"},
      {"title": "Chemical Reactions – Types", "url": "https://www.youtube.com/watch?v=AtR2bCpI0sA"},
      {"title": "Periodic Table – Basics", "url": "https://www.youtube.com/watch?v=YsfG2XnLdAY"},
      {"title": "Acids, Bases & Salts", "url": "https://www.youtube.com/watch?v=bwYcK08zFhM"},
      {"title": "Metals and Non-Metals", "url": "https://www.youtube.com/watch?v=Kp_Ty7bYcY0"},
      {"title": "Carbon and Its Compounds", "url": "https://www.youtube.com/watch?v=45VdXYwFgBM"},
      {"title": "Water – Properties & Importance", "url": "https://www.youtube.com/watch?v=2CaWOVl7goM"},
      {"title": "Air – Composition and Reactions", "url": "https://www.youtube.com/watch?v=NmV6MZ7EFiM"}
    ],
    "Mathematics": [
      {"title": "Number Systems", "url": "https://www.youtube.com/watch?v=zA0YaoWzx8E"},
      {"title": "Polynomials", "url": "https://www.youtube.com/watch?v=TKjKpPRNbU4"},
      {"title": "Linear Equations in Two Variables", "url": "https://www.youtube.com/watch?v=0Tq0-rwF3mU"},
      {"title": "Coordinate Geometry", "url": "https://www.youtube.com/watch?v=MMgQNNz2UQ0"},
      {"title": "Probability – Basics", "url": "https://www.youtube.com/watch?v=_6FzBZUthVQ"},
      {"title": "Statistics – Mean, Median, Mode", "url": "https://www.youtube.com/watch?v=Kvhv1YK09bk"},
      {"title": "Surface Area and Volume", "url": "https://www.youtube.com/watch?v=h64PB1zuUrc"},
      {"title": "Triangles – Properties", "url": "https://www.youtube.com/watch?v=gYhRrM7iHgY"},
      {"title": "Circles – Theorems", "url": "https://www.youtube.com/watch?v=xK1XcO9JQqQ"},
      {"title": "Geometry – Constructions", "url": "https://www.youtube.com/watch?v=cdLifIs-hmc"}
    ]
  },
  "10th": {
    "Physics": [
      {"title": "Electricity – Ohm’s Law", "url": "https://www.youtube.com/watch?v=czRjzW0jIBg"},
      {"title": "Magnetic Effects of Electric Current", "url": "https://www.youtube.com/watch?v=QxWmUBKqQ6E"},
      {"title": "Light – Reflection", "url": "https://www.youtube.com/watch?v=R1J89S0s_yA"},
      {"title": "Light – Refraction", "url": "https://www.youtube.com/watch?v=2r3leWQZJH0"},
      {"title": "Human Eye and Colourful World", "url": "https://www.youtube.com/watch?v=YzU6V0AosP0"},
      {"title": "Sources of Energy", "url": "https://www.youtube.com/watch?v=EpGJ5YJTUAs"},
      {"title": "Work, Power and Energy", "url": "https://www.youtube.com/watch?v=Y35iS3sFw3c"},
      {"title": "Current and Circuits", "url": "https://www.youtube.com/watch?v=Uv6rG02WnSg"},
      {"title": "Domestic Electric Circuits", "url": "https://www.youtube.com/watch?v=3cPb8jLJqDQ"},
      {"title": "Sources of Light", "url": "https://www.youtube.com/watch?v=fh7S3Onm1Jo"}
    ],
    "Chemistry": [
      {"title": "Chemical Reactions and Equations", "url": "https://www.youtube.com/watch?v=bbh1GUpc3R4"},
      {"title": "Acids, Bases and Salts", "url": "https://www.youtube.com/watch?v=UedkDq8hRRo"},
      {"title": "Metals and Non-Metals", "url": "https://www.youtube.com/watch?v=Wj0Af7V74jw"},
      {"title": "Carbon and Its Compounds", "url": "https://www.youtube.com/watch?v=8P4n59fVXy0"},
      {"title": "Periodic Classification of Elements", "url": "https://www.youtube.com/watch?v=zIkqt0GxXwY"},
      {"title": "Redox Reactions", "url": "https://www.youtube.com/watch?v=9YpuHbD6MGo"},
      {"title": "Chemical Bonding", "url": "https://www.youtube.com/watch?v=fMQXbU2f3Yc"},
      {"title": "Solutions", "url": "https://www.youtube.com/watch?v=nmcUesZ2-4g"},
      {"title": "Electrolysis", "url": "https://www.youtube.com/watch?v=5LL5kVQHkpQ"},
      {"title": "Types of Fuels", "url": "https://www.youtube.com/watch?v=f6M7t6zAqQY"}
    ],
    "Mathematics": [
      {"title": "Real Numbers", "url": "https://www.youtube.com/watch?v=Opz_qfLwSpQ"},
      {"title": "Polynomials", "url": "https://www.youtube.com/watch?v=1x8lYx5n4tE"},
      {"title": "Pair of Linear Equations", "url": "https://www.youtube.com/watch?v=ZqHf1iWj91U"},
      {"title": "Quadratic Equations", "url": "https://www.youtube.com/watch?v=wd9GEzv0zvA"},
      {"title": "Arithmetic Progressions", "url": "https://www.youtube.com/watch?v=9Jv1o2B4ApU"},
      {"title": "Triangles – Similarity", "url": "https://www.youtube.com/watch?v=bWk6AEGJzPg"},
      {"title": "Coordinate Geometry", "url": "https://www.youtube.com/watch?v=2pU2P6KgC50"},
      {"title": "Trigonometry – Introduction", "url": "https://www.youtube.com/watch?v=6tJrkjr6hxY"},
      {"title": "Applications of Trigonometry", "url": "https://www.youtube.com/watch?v=REHj5uf3H5M"},
      {"title": "Probability & Statistics", "url": "https://www.youtube.com/watch?v=hKf3jsuN7VU"}
    ]
  }
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'instance', 'edureach.db')

# Helpers

def to_embed(url: str) -> str:
    m = re.search(r"v=([A-Za-z0-9_-]{6,})", url)
    if m:
        return f"https://www.youtube.com/embed/{m.group(1)}"
    m = re.search(r"youtu\.be/([A-Za-z0-9_-]{6,})", url)
    if m:
        return f"https://www.youtube.com/embed/{m.group(1)}"
    return url

_norm_map = {
    '–': '-',
    '—': '-',
    '&': 'and',
}

def normalize_title(s: str) -> str:
    s = s.lower().strip()
    for k, v in _norm_map.items():
        s = s.replace(k, v)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\b(the|and|of|in|to|for|with)\b", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Load all courses
cur.execute("SELECT id, name, class_level, subject, description, video_data FROM course")
rows = cur.fetchall()

courses = []
for rid, name, cls, subj, desc, vdata in rows:
    courses.append({
        'id': rid,
        'name': name or '',
        'class_level': cls or '',
        'subject': subj or '',
        'description': desc or '',
        'video_data': vdata,
        '_norm': normalize_title(name or '')
    })

updated = 0
unmatched = []

for cls_level, subjects in LINKS.items():
    for subject, items in subjects.items():
        for item in items:
            title = item['title']
            url = item['url']
            norm = normalize_title(title)

            # Try to find exact within same class+subject first
            matches = [c for c in courses if c['class_level'] == cls_level and c['subject'] == subject and c['_norm'] == norm]

            # If not found, allow fuzzy: same class+subject and contained words
            if not matches:
                matches = [c for c in courses if c['class_level'] == cls_level and c['subject'] == subject and (norm in c['_norm'] or c['_norm'] in norm)]

            # Special case: 9th Physics "Motion and Speed – Introduction" vs "Motion and Speed"
            if not matches and cls_level == '9th' and subject == 'Physics' and 'motion and speed' in norm:
                matches = [c for c in courses if c['class_level'] == '9th' and c['subject'] == 'Physics' and 'motion and speed introduction' in c['_norm']]

            if not matches:
                unmatched.append((cls_level, subject, title))
                continue

            # Use the first match (should be unique per our seed)
            course = matches[0]
            embed = to_embed(url)
            video_json = json.dumps([{ 'title': title, 'description': f"{subject} - {title}", 'url': embed }])
            cur.execute("UPDATE course SET video_data = ? WHERE id = ?", (video_json, course['id']))
            updated += 1

conn.commit()
conn.close()

print(f"Updated {updated} course videos.")
if unmatched:
    print("Could not match the following titles (consider adding/renaming these courses):")
    for cls, subj, t in unmatched:
        print(f" - {cls} / {subj}: {t}")

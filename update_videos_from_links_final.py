import os, sqlite3, json, re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'instance', 'edureach.db')

# Helper: convert YouTube to embed if it's a direct link
YT_ID = re.compile(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{6,})")

def to_embed(url: str) -> str:
    m = YT_ID.search(url or '')
    if not m:
        return ''
    return f"https://www.youtube.com/embed/{m.group(1)}"

# New mapping from the user
LINKS = {
  "9th": {
    "Physics": [
      {"title": "Motion and Speed – Introduction", "url": "https://youtu.be/S9Z1a3sZfHY"},
      {"title": "Newton’s Laws of Motion", "url": "https://youtu.be/BCnWQrXoHeo"},
      {"title": "Gravitation and Free Fall", "url": "https://youtu.be/6mFGzESlmxI"},
      {"title": "Work, Energy, and Power", "url": "https://youtu.be/w4QFJb9a8vo"},
      {"title": "Sound – Properties and Applications", "url": "https://youtu.be/-_xZZt99MzY"},
      {"title": "Light – Reflection and Refraction", "url": "https://youtu.be/--tPQ4iui1c"},
      {"title": "Pressure in Fluids", "url": "https://youtu.be/Cvp6mLWbgaM"},
      {"title": "Heat and Temperature", "url": "https://youtu.be/LL54E5CzQ-A"},
      {"title": "Force and Friction", "url": "https://youtu.be/n2gQs1mcZHA"},
      {"title": "Electricity – Basics", "url": "https://youtu.be/CIv6vu9d73c"}
    ],
    "Chemistry": [
      {"title": "Matter – Properties and States", "url": "https://youtu.be/mpufi-1voVo"},
      {"title": "Elements, Compounds & Mixtures", "url": "https://youtu.be/neOmNQrz88M"},
      {"title": "Atomic Structure – Introduction", "search_url": "https://www.youtube.com/results?search_query=Class+9+Chemistry+Atomic+Structure+Introduction"},
      {"title": "Chemical Reactions – Types", "search_url": "https://www.youtube.com/results?search_query=Class+9+Chemistry+Chemical+Reactions+Types"},
      {"title": "Periodic Table – Basics", "search_url": "https://www.youtube.com/results?search_query=Class+9+Chemistry+Periodic+Table+Basics"},
      {"title": "Acids, Bases & Salts", "search_url": "https://www.youtube.com/results?search_query=Class+9+Chemistry+Acids+Bases+and+Salts"},
      {"title": "Metals and Non-Metals", "search_url": "https://www.youtube.com/results?search_query=Class+9+Chemistry+Metals+and+Non%2DMetals"},
      {"title": "Carbon and Its Compounds", "search_url": "https://www.youtube.com/results?search_query=Class+9+Chemistry+Carbon+and+Its+Compounds"},
      {"title": "Water – Properties & Importance", "search_url": "https://www.youtube.com/results?search_query=Class+9+Chemistry+Water+Properties+and+Importance"},
      {"title": "Air – Composition and Reactions", "search_url": "https://www.youtube.com/results?search_query=Class+9+Chemistry+Air+Composition+and+Reactions"}
    ],
    "Mathematics": [
      {"title": "Number Systems", "url": "https://youtu.be/TRhJ_tjJUdU"},
      {"title": "Polynomials – Basics", "url": "https://youtu.be/xmJjQ3KyTdw"},
      {"title": "Linear Equations in Two Variables", "search_url": "https://www.youtube.com/results?search_query=Class+9+Mathematics+Linear+Equations+in+Two+Variables"},
      {"title": "Coordinate Geometry – Introduction", "search_url": "https://www.youtube.com/results?search_query=Class+9+Mathematics+Coordinate+Geometry+Introduction"},
      {"title": "Probability – Basics", "search_url": "https://www.youtube.com/results?search_query=Class+9+Mathematics+Probability+Basics"},
      {"title": "Statistics – Mean, Median, Mode", "search_url": "https://www.youtube.com/results?search_query=Class+9+Mathematics+Statistics+Mean+Median+Mode"},
      {"title": "Surface Area and Volume", "search_url": "https://www.youtube.com/results?search_query=Class+9+Mathematics+Surface+Area+and+Volume"},
      {"title": "Triangles – Properties", "search_url": "https://www.youtube.com/results?search_query=Class+9+Mathematics+Triangles+Properties"},
      {"title": "Circles – Theorems", "search_url": "https://www.youtube.com/results?search_query=Class+9+Mathematics+Circles+Theorems"},
      {"title": "Geometry – Constructions", "search_url": "https://www.youtube.com/results?search_query=Class+9+Mathematics+Geometry+Constructions"}
    ]
  },
  "10th": {
    "Physics": [
      {"title": "Electricity – Ohm’s Law", "url": "https://youtu.be/oFTj9LWkmm8"},
      {"title": "Magnetic Effects of Electric Current", "url": "https://youtu.be/hUIw4H_kt50"},
      {"title": "Light – Reflection", "search_url": "https://www.youtube.com/results?search_query=Class+10+Physics+Light+Reflection"},
      {"title": "Light – Refraction", "search_url": "https://www.youtube.com/results?search_query=Class+10+Physics+Light+Refraction"},
      {"title": "Human Eye and the Colourful World", "search_url": "https://www.youtube.com/results?search_query=Class+10+Physics+Human+Eye+and+the+Colourful+World"},
      {"title": "Sources of Energy", "search_url": "https://www.youtube.com/results?search_query=Class+10+Physics+Sources+of+Energy"},
      {"title": "Work, Power, Energy (Advanced)", "search_url": "https://www.youtube.com/results?search_query=Class+10+Physics+Work+Power+Energy+advanced"},
      {"title": "Sound – Wave Nature", "search_url": "https://www.youtube.com/results?search_query=Class+10+Physics+Sound+Wave+Nature"},
      {"title": "Modern Physics – Atoms & Nuclei", "search_url": "https://www.youtube.com/results?search_query=Class+10+Physics+Modern+Physics+Atoms+and+Nuclei"},
      {"title": "Motion – Graphs & Equations", "search_url": "https://www.youtube.com/results?search_query=Class+10+Physics+Motion+Graphs+and+Equations"}
    ],
    "Chemistry": [
      {"title": "Chemical Reactions and Equations", "url": "https://youtu.be/AEyJ0MpddzQ"},
      {"title": "Acids, Bases & Salts (Detailed)", "url": "https://youtu.be/zv1-ZuLSskQ"},
      {"title": "Metals and Non-Metals (Extraction & Properties)", "search_url": "https://www.youtube.com/results?search_query=Class+10+Chemistry+Metals+and+Non%2DMetals+Extraction+and+Properties"},
      {"title": "Carbon Compounds (Hydrocarbons, Functional Groups)", "search_url": "https://www.youtube.com/results?search_query=Class+10+Chemistry+Carbon+Compounds+Hydrocarbons+Functional+Groups"},
      {"title": "Periodic Classification of Elements", "search_url": "https://www.youtube.com/results?search_query=Class+10+Chemistry+Periodic+Classification+of+Elements"},
      {"title": "Chemical Bonding", "search_url": "https://www.youtube.com/results?search_query=Class+10+Chemistry+Chemical+Bonding"},
      {"title": "Electrolysis", "search_url": "https://www.youtube.com/results?search_query=Class+10+Chemistry+Electrolysis"},
      {"title": "Water Chemistry", "search_url": "https://www.youtube.com/results?search_query=Class+10+Chemistry+Water+Chemistry"},
      {"title": "Industrial Chemistry (Cement, Fertilizers, etc.)", "search_url": "https://www.youtube.com/results?search_query=Class+10+Chemistry+Industrial+Chemistry+Cement+Fertilizers"},
      {"title": "Environmental Chemistry", "search_url": "https://www.youtube.com/results?search_query=Class+10+Chemistry+Environmental+Chemistry"}
    ],
    "Mathematics": [
      {"title": "Real Numbers", "url": "https://youtu.be/AFOnjvjU-Ck"},
      {"title": "Polynomials (Advanced)", "url": "https://youtu.be/OnbcKzlWNeE"},
      {"title": "Pair of Linear Equations in Two Variables", "search_url": "https://www.youtube.com/results?search_query=Class+10+Mathematics+Pair+of+Linear+Equations+in+Two+Variables"},
      {"title": "Quadratic Equations", "search_url": "https://www.youtube.com/results?search_query=Class+10+Mathematics+Quadratic+Equations"},
      {"title": "Arithmetic Progressions", "search_url": "https://www.youtube.com/results?search_query=Class+10+Mathematics+Arithmetic+Progressions"},
      {"title": "Circles – Tangents", "search_url": "https://www.youtube.com/results?search_query=Class+10+Mathematics+Circles+Tangents"},
      {"title": "Constructions – Advanced", "search_url": "https://www.youtube.com/results?search_query=Class+10+Mathematics+Constructions+Advanced"},
      {"title": "Trigonometry – Basics", "search_url": "https://www.youtube.com/results?search_query=Class+10+Mathematics+Trigonometry+Basics"},
      {"title": "Applications of Trigonometry", "search_url": "https://www.youtube.com/results?search_query=Class+10+Mathematics+Applications+of+Trigonometry"},
      {"title": "Statistics & Probability", "search_url": "https://www.youtube.com/results?search_query=Class+10+Mathematics+Statistics+and+Probability"}
    ]
  }
}

# Normalize utility for matching course titles
REP = {
    '–': '-',
    '—': '-',
}

def norm(s: str) -> str:
    s = (s or '').strip()
    for k, v in REP.items():
        s = s.replace(k, v)
    return s

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("SELECT id, name, class_level, subject FROM course")
rows = cur.fetchall()

# Build lookup: {(class, subject, normalized_name): id}
lookup = {}
for cid, name, cls, subj in rows:
    lookup[(cls, subj, norm(name))] = cid

updated, missing = 0, []
for cls, subjects in LINKS.items():
    for subj, items in subjects.items():
        for it in items:
            title = it['title']
            key = (cls, subj, norm(title))
            cid = lookup.get(key)
            if not cid:
                # try case-insensitive subject match
                cid = next((id_ for (c,s,n), id_ in lookup.items() if c==cls and s.lower()==subj.lower() and n==norm(title)), None)
            if not cid:
                missing.append((cls, subj, title))
                continue
            url = it.get('url', '')
            search_url = it.get('search_url', '')
            embed = to_embed(url) if url else ''
            video = [{
                'title': title,
                'description': f"{subj} - {title}",
                'url': embed,
                'search_url': search_url
            }]
            cur.execute("UPDATE course SET video_data = ? WHERE id = ?", (json.dumps(video), cid))
            updated += 1

conn.commit()
conn.close()

print(f"Updated {updated} courses.")
if missing:
    print("Missing matches for:")
    for m in missing:
        print(" - ", m)

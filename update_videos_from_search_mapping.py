import json
import os
import sqlite3
import re

# New mapping with YouTube search URLs and recommended channels
MAPPING = {
  "9th": {
    "Physics": [
      {"title": "Motion and Speed", "youtube_search": "https://www.youtube.com/results?search_query=Motion+and+speed+class+9+physics+Khan+Academy", "recommended_channel": "Khan Academy / Class 9 tutorials"},
      {"title": "Newton's Laws of Motion", "youtube_search": "https://www.youtube.com/results?search_query=Newton%27s+laws+of+motion+class+9+physics+Khan+Academy", "recommended_channel": "Khan Academy"},
      {"title": "Gravitation and Free Fall", "youtube_search": "https://www.youtube.com/results?search_query=Gravitation+free+fall+class+9+physics+BYJU%27S", "recommended_channel": "BYJU'S / NCERT solutions"},
      {"title": "Work, Energy, and Power", "youtube_search": "https://www.youtube.com/results?search_query=Work+energy+power+class+9+physics+Khan+Academy", "recommended_channel": "Khan Academy"},
      {"title": "Sound – Properties & Applications", "youtube_search": "https://www.youtube.com/results?search_query=Sound+properties+class+9+physics+lecture", "recommended_channel": "FuseSchool / Class 9 lectures"},
      {"title": "Light – Reflection and Refraction", "youtube_search": "https://www.youtube.com/results?search_query=Reflection+refraction+class+9+physics+video", "recommended_channel": "Khan Academy / BYJU'S"},
      {"title": "Pressure in Fluids", "youtube_search": "https://www.youtube.com/results?search_query=Pressure+in+fluids+class+9+physics+video", "recommended_channel": "NCERT/CBSE tutorial channels"},
      {"title": "Heat and Temperature", "youtube_search": "https://www.youtube.com/results?search_query=Heat+and+temperature+class+9+physics+video", "recommended_channel": "Khan Academy"},
      {"title": "Force and Friction", "youtube_search": "https://www.youtube.com/results?search_query=Force+and+friction+class+9+physics+video", "recommended_channel": "Class 9 physics playlists"},
      {"title": "Electricity – Basics", "youtube_search": "https://www.youtube.com/results?search_query=Electricity+basics+class+9+physics+video", "recommended_channel": "Khan Academy / Simple Science channels"}
    ],
    "Chemistry": [
      {"title": "Matter – Properties and States", "youtube_search": "https://www.youtube.com/results?search_query=Matter+properties+states+class+9+chemistry+video", "recommended_channel": "Khan Academy / NCERT"},
      {"title": "Elements, Compounds & Mixtures", "youtube_search": "https://www.youtube.com/results?search_query=Elements+compounds+mixtures+class+9+chemistry+video", "recommended_channel": "BYJU'S / Examrace"},
      {"title": "Atomic Structure – Introduction", "youtube_search": "https://www.youtube.com/results?search_query=Atomic+structure+class+9+chemistry+video", "recommended_channel": "Khan Academy"},
      {"title": "Chemical Reactions – Types", "youtube_search": "https://www.youtube.com/results?search_query=Chemical+reactions+types+class+9+chemistry+video", "recommended_channel": "Class 9 chemistry playlists"},
      {"title": "Periodic Table – Basics", "youtube_search": "https://www.youtube.com/results?search_query=Periodic+table+basics+class+9+chemistry+video", "recommended_channel": "Khan Academy"},
      {"title": "Acids, Bases & Salts", "youtube_search": "https://www.youtube.com/results?search_query=Acids+bases+salts+class+9+chemistry+video", "recommended_channel": "BYJU'S / Khan Academy"},
      {"title": "Metals and Non-Metals", "youtube_search": "https://www.youtube.com/results?search_query=Metals+and+non-metals+class+9+chemistry+video", "recommended_channel": "NCERT/CBSE tutorial channels"},
      {"title": "Carbon and Its Compounds", "youtube_search": "https://www.youtube.com/results?search_query=Carbon+and+its+compounds+class+9+chemistry+video", "recommended_channel": "Class 9 chemistry playlists"},
      {"title": "Water – Properties & Importance", "youtube_search": "https://www.youtube.com/results?search_query=Water+properties+class+9+chemistry+video", "recommended_channel": "Educational channels"},
      {"title": "Air – Composition and Reactions", "youtube_search": "https://www.youtube.com/results?search_query=Air+composition+class+9+chemistry+video", "recommended_channel": "NCERT / Science channels"}
    ],
    "Mathematics": [
      {"title": "Number Systems", "youtube_search": "https://www.youtube.com/results?search_query=Number+systems+class+9+maths+video", "recommended_channel": "Maths teacher channels / Khan Academy"},
      {"title": "Polynomials – Basics", "youtube_search": "https://www.youtube.com/results?search_query=Polynomials+class+9+maths+video", "recommended_channel": "Maths tutorial channels"},
      {"title": "Linear Equations in Two Variables", "youtube_search": "https://www.youtube.com/results?search_query=Linear+equations+in+two+variables+class+9+maths+video", "recommended_channel": "NCERT/Maths playlists"},
      {"title": "Coordinate Geometry – Introduction", "youtube_search": "https://www.youtube.com/results?search_query=Coordinate+geometry+class+9+maths+video", "recommended_channel": "Maths teacher channels"},
      {"title": "Probability – Basics", "youtube_search": "https://www.youtube.com/results?search_query=Probability+class+9+maths+video", "recommended_channel": "Khan Academy / Maths channels"},
      {"title": "Statistics – Mean Median Mode", "youtube_search": "https://www.youtube.com/results?search_query=Mean+median+mode+class+9+maths+video", "recommended_channel": "Maths tutorial channels"},
      {"title": "Surface Area and Volume", "youtube_search": "https://www.youtube.com/results?search_query=Surface+area+volume+class+9+maths+video", "recommended_channel": "NCERT / tutorial channels"},
      {"title": "Triangles – Properties", "youtube_search": "https://www.youtube.com/results?search_query=Triangles+properties+class+9+maths+video", "recommended_channel": "Maths channels"},
      {"title": "Circles – Theorems", "youtube_search": "https://www.youtube.com/results?search_query=Circles+theorems+class+9+maths+video", "recommended_channel": "Maths tutorials"},
      {"title": "Geometry – Constructions", "youtube_search": "https://www.youtube.com/results?search_query=Constructions+class+9+maths+video", "recommended_channel": "Construction tutorials"}
    ]
  },
  "10th": {
    "Physics": [
      {"title": "Electricity – Ohm's Law", "youtube_search": "https://www.youtube.com/results?search_query=Ohm%27s+law+class+10+physics+video+Khan+Academy", "recommended_channel": "Khan Academy"},
      {"title": "Magnetic Effects of Electric Current", "youtube_search": "https://www.youtube.com/results?search_query=Magnetic+effects+of+electric+current+class+10+video", "recommended_channel": "Class 10 physics playlists"},
      {"title": "Light – Reflection", "youtube_search": "https://www.youtube.com/results?search_query=Reflection+of+light+class+10+physics+video", "recommended_channel": "Khan Academy / Physics channels"},
      {"title": "Light – Refraction", "youtube_search": "https://www.youtube.com/results?search_query=Refraction+of+light+class+10+physics+video", "recommended_channel": "Khan Academy / BYJU'S"},
      {"title": "Human Eye and the Colourful World", "youtube_search": "https://www.youtube.com/results?search_query=Human+eye+colourful+world+class+10+video", "recommended_channel": "NCERT / Science channels"},
      {"title": "Sources of Energy", "youtube_search": "https://www.youtube.com/results?search_query=Sources+of+energy+class+10+physics+video", "recommended_channel": "Educational channels"},
      {"title": "Work, Power and Energy (Advanced)", "youtube_search": "https://www.youtube.com/results?search_query=Work+power+energy+class+10+physics+video", "recommended_channel": "Khan Academy"},
      {"title": "Sound – Wave Nature", "youtube_search": "https://www.youtube.com/results?search_query=Sound+wave+nature+class+10+physics+video", "recommended_channel": "Physics tutorial channels"},
      {"title": "Atoms & Nuclei (Modern Physics)", "youtube_search": "https://www.youtube.com/results?search_query=Atoms+and+nuclei+class+10+physics+video", "recommended_channel": "NCERT / Science channels"},
      {"title": "Motion – Graphs & Equations", "youtube_search": "https://www.youtube.com/results?search_query=Motion+graphs+equations+class+10+physics+video", "recommended_channel": "Khan Academy / Physics channels"}
    ],
    "Chemistry": [
      {"title": "Chemical Reactions and Equations", "youtube_search": "https://www.youtube.com/results?search_query=Chemical+reactions+and+equations+class+10+chemistry+video", "recommended_channel": "Khan Academy / BYJU'S"},
      {"title": "Acids, Bases & Salts (Detailed)", "youtube_search": "https://www.youtube.com/results?search_query=Acids+bases+salts+class+10+chemistry+video", "recommended_channel": "BYJU'S / Examrace"},
      {"title": "Metals and Non-Metals (Extraction & Properties)", "youtube_search": "https://www.youtube.com/results?search_query=Metals+and+non-metals+class+10+chemistry+video", "recommended_channel": "NCERT tutorials"},
      {"title": "Carbon Compounds (Hydrocarbons)", "youtube_search": "https://www.youtube.com/results?search_query=Carbon+compounds+hydrocarbons+class+10+chemistry+video", "recommended_channel": "Chemistry tutorial channels"},
      {"title": "Periodic Classification of Elements", "youtube_search": "https://www.youtube.com/results?search_query=Periodic+classification+class+10+chemistry+video", "recommended_channel": "Khan Academy / NCERT"},
      {"title": "Chemical Bonding", "youtube_search": "https://www.youtube.com/results?search_query=Chemical+bonding+class+10+chemistry+video", "recommended_channel": "Chemistry channels"},
      {"title": "Electrolysis", "youtube_search": "https://www.youtube.com/results?search_query=Electrolysis+class+10+chemistry+video", "recommended_channel": "NCERT / tutorial channels"},
      {"title": "Water Chemistry", "youtube_search": "https://www.youtube.com/results?search_query=Water+chemistry+class+10+video", "recommended_channel": "Educational channels"},
      {"title": "Industrial Chemistry (Cement, Fertilizers)", "youtube_search": "https://www.youtube.com/results?search_query=Industrial+chemistry+class+10+video", "recommended_channel": "Industry+education channels"},
      {"title": "Environmental Chemistry", "youtube_search": "https://www.youtube.com/results?search_query=Environmental+chemistry+class+10+video", "recommended_channel": "Science channels"}
    ],
    "Mathematics": [
      {"title": "Real Numbers", "youtube_search": "https://www.youtube.com/results?search_query=Real+numbers+class+10+maths+video", "recommended_channel": "Maths tutorial channels"},
      {"title": "Polynomials (Advanced)", "youtube_search": "https://www.youtube.com/results?search_query=Polynomials+class+10+maths+video", "recommended_channel": "Maths channels"},
      {"title": "Pair of Linear Equations in Two Variables", "youtube_search": "https://www.youtube.com/results?search_query=Pair+of+linear+equations+class+10+maths+video", "recommended_channel": "NCERT / tutorial channels"},
      {"title": "Quadratic Equations", "youtube_search": "https://www.youtube.com/results?search_query=Quadratic+equations+class+10+maths+video", "recommended_channel": "Maths tutorial channels"},
      {"title": "Arithmetic Progressions", "youtube_search": "https://www.youtube.com/results?search_query=Arithmetic+progressions+class+10+maths+video", "recommended_channel": "Maths channels"},
      {"title": "Circles – Tangents", "youtube_search": "https://www.youtube.com/results?search_query=Circles+tangents+class+10+maths+video", "recommended_channel": "Maths tutorial channels"},
      {"title": "Constructions – Advanced", "youtube_search": "https://www.youtube.com/results?search_query=Geometrical+constructions+class+10+maths+video", "recommended_channel": "Construction tutorials"},
      {"title": "Trigonometry – Basics", "youtube_search": "https://www.youtube.com/results?search_query=Trigonometry+class+10+maths+video", "recommended_channel": "Khan Academy / Maths channels"},
      {"title": "Applications of Trigonometry", "youtube_search": "https://www.youtube.com/results?search_query=Applications+of+trigonometry+class+10+video", "recommended_channel": "Maths tutorial channels"},
      {"title": "Statistics & Probability", "youtube_search": "https://www.youtube.com/results?search_query=Statistics+and+probability+class+10+maths+video", "recommended_channel": "Maths channels"}
    ]
  }
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'instance', 'edureach.db')

# Simple normalizer to match course names
import re

def normalize(s: str) -> str:
    s = s.lower().strip()
    s = s.replace('–', '-').replace('—', '-')
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("SELECT id, name, class_level, subject FROM course")
rows = cur.fetchall()

courses = [{
    'id': r[0],
    'name': r[1],
    'class_level': r[2],
    'subject': r[3],
    'norm': normalize(r[1] or '')
} for r in rows]

updated = 0
unmatched = []

for cls, subjects in MAPPING.items():
    for subj, items in subjects.items():
        for item in items:
            title = item['title']
            search_url = item['youtube_search']
            rec = item.get('recommended_channel', '')
            normTitle = normalize(title)
            # prefer exact class + subject + normalized title
            match = next((c for c in courses if c['class_level']==cls and c['subject']==subj and c['norm']==normTitle), None)
            if not match:
                # fallback contains
                match = next((c for c in courses if c['class_level']==cls and c['subject']==subj and (normTitle in c['norm'] or c['norm'] in normTitle)), None)
            if not match:
                unmatched.append((cls, subj, title))
                continue
            video = [{
                'title': title,
                'description': f"{subj} - {title}",
                'url': '',
                'search_url': search_url,
                'recommended_channel': rec
            }]
            cur.execute("UPDATE course SET video_data = ? WHERE id = ?", (json.dumps(video), match['id']))
            updated += 1

conn.commit()
conn.close()

print(f"Updated {updated} courses with YouTube search links.")
if unmatched:
    print("Unmatched titles:")
    for u in unmatched:
        print(" - ", u)

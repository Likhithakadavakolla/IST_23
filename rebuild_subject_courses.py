import os, sqlite3, json, re
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'instance', 'edureach.db')

YT_ID = re.compile(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{6,})")

def to_embed(url: str) -> str:
    if not url:
        return ''
    m = YT_ID.search(url)
    if not m:
        return ''
    return f"https://www.youtube.com/embed/{m.group(1)}"

COURSES = {
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

def rebuild():
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        # Clean existing data (progress -> assignment -> course)
        cur.execute('DELETE FROM progress')
        cur.execute('DELETE FROM assignment')
        cur.execute('DELETE FROM course')
        
        # Insert 6 subject courses with 10 lessons each
        for cls, subjects in COURSES.items():
            for subj, lessons in subjects.items():
                videos = []
                for l in lessons:
                    url = l.get('url', '')
                    search_url = l.get('search_url', '')
                    embed = to_embed(url) if url else ''
                    videos.append({
                        'title': l['title'],
                        'description': f"{subj} - {l['title']}",
                        'url': embed,
                        'search_url': search_url
                    })
                description = f"Curated {subj} topics for {cls} class"
                cur.execute(
                    'INSERT INTO course (name, class_level, subject, description, video_data, created_at) VALUES (?,?,?,?,?,?)',
                    (subj, cls, subj, description, json.dumps(videos), datetime.utcnow().isoformat())
                )
        conn.commit()
        print('Rebuilt subject-level courses with 10 lessons each.')
    finally:
        conn.close()

if __name__ == '__main__':
    rebuild()

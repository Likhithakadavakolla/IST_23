import os, sqlite3, json, datetime

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'instance', 'edureach.db')

courses_per_class = {
    '9th': {
        'Physics': [
            'Motion and Speed – Introduction',
            'Newton’s Laws of Motion',
            'Gravitation and Free Fall',
            'Work, Energy, and Power',
            'Sound – Properties and Applications',
            'Light – Reflection and Refraction',
            'Pressure in Fluids',
            'Heat and Temperature',
            'Force and Friction',
            'Electricity – Basics'
        ],
        'Chemistry': [
            'Matter – Properties and States',
            'Elements, Compounds & Mixtures',
            'Atomic Structure – Introduction',
            'Chemical Reactions – Types',
            'Periodic Table – Basics',
            'Acids, Bases & Salts',
            'Metals and Non-Metals',
            'Carbon and Its Compounds',
            'Water – Properties & Importance',
            'Air – Composition and Reactions'
        ],
        'Mathematics': [
            'Number Systems',
            'Polynomials – Basics',
            'Linear Equations in Two Variables',
            'Coordinate Geometry – Introduction',
            'Probability – Basics',
            'Statistics – Mean, Median, Mode',
            'Surface Area and Volume',
            'Triangles – Properties',
            'Circles – Theorems',
            'Geometry – Constructions'
        ]
    },
    '10th': {
        'Physics': [
            'Electricity – Ohm’s Law',
            'Magnetic Effects of Electric Current',
            'Light – Reflection',
            'Light – Refraction',
            'Human Eye and the Colourful World',
            'Sources of Energy',
            'Work, Power, Energy (Advanced)',
            'Sound – Wave Nature',
            'Modern Physics – Atoms & Nuclei',
            'Motion – Graphs & Equations'
        ],
        'Chemistry': [
            'Chemical Reactions and Equations',
            'Acids, Bases & Salts (Detailed)',
            'Metals and Non-Metals (Extraction & Properties)',
            'Carbon Compounds (Hydrocarbons, Functional Groups)',
            'Periodic Classification of Elements',
            'Chemical Bonding',
            'Electrolysis',
            'Water Chemistry',
            'Industrial Chemistry (Cement, Fertilizers, etc.)',
            'Environmental Chemistry'
        ],
        'Mathematics': [
            'Real Numbers',
            'Polynomials (Advanced)',
            'Pair of Linear Equations in Two Variables',
            'Quadratic Equations',
            'Arithmetic Progressions',
            'Circles – Tangents',
            'Constructions – Advanced',
            'Trigonometry – Basics',
            'Applications of Trigonometry',
            'Statistics & Probability'
        ]
    }
}

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Clean tables
cur.execute('DELETE FROM progress')
cur.execute('DELETE FROM course')

now = datetime.datetime.utcnow().isoformat()

for class_level, subjects in courses_per_class.items():
    for subject, topics in subjects.items():
        for topic in topics:
            desc = f"{subject} - {topic}"
            video_data = json.dumps([{'title': topic, 'description': desc, 'url': ''}])
            cur.execute(
                'INSERT INTO course (name, class_level, subject, description, video_data, created_at) VALUES (?,?,?,?,?,?)',
                (topic, class_level, subject, desc, video_data, now)
            )

conn.commit()
conn.close()
print('Reseeded (sqlite): 30 courses per class into instance/edureach.db')

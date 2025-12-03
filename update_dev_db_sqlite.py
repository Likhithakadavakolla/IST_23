import os, sqlite3, json

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'instance', 'edureach_dev.db')

courses_data = [
    {
        'name': 'Physics',
        'class_level': '9th',
        'description': 'Curated Physics topics for 9th class',
        'videos': [
            {'title': 'Motion and Speed – Introduction', 'description': 'Introduction to motion and speed', 'url': ''},
            {'title': 'Newton’s Laws of Motion', 'description': 'Overview of Newton’s laws', 'url': ''},
            {'title': 'Gravitation and Free Fall', 'description': 'Basics of gravitation and free fall', 'url': ''},
            {'title': 'Work, Energy, and Power', 'description': 'Understanding work, energy, and power', 'url': ''},
            {'title': 'Sound – Properties and Applications', 'description': 'Properties of sound and applications', 'url': ''},
            {'title': 'Light – Reflection and Refraction', 'description': 'Reflection and refraction of light', 'url': ''},
            {'title': 'Pressure in Fluids', 'description': 'Concept of pressure in fluids', 'url': ''},
            {'title': 'Heat and Temperature', 'description': 'Difference between heat and temperature', 'url': ''},
            {'title': 'Force and Friction', 'description': 'Force and the role of friction', 'url': ''},
            {'title': 'Electricity – Basics', 'description': 'Basic ideas of electricity', 'url': ''}
        ]
    },
    {
        'name': 'Physics',
        'class_level': '10th',
        'description': 'Curated Physics topics for 10th class',
        'videos': [
            {'title': 'Electricity – Ohm’s Law', 'description': 'Understanding Ohm’s Law', 'url': ''},
            {'title': 'Magnetic Effects of Electric Current', 'description': 'Magnetic effects and applications', 'url': ''},
            {'title': 'Light – Reflection', 'description': 'Reflection of light', 'url': ''},
            {'title': 'Light – Refraction', 'description': 'Refraction of light', 'url': ''},
            {'title': 'Human Eye and the Colourful World', 'description': 'Structure and functioning of the eye', 'url': ''},
            {'title': 'Sources of Energy', 'description': 'Conventional and non-conventional energy', 'url': ''},
            {'title': 'Work, Power, Energy (Advanced)', 'description': 'Advanced concepts of work, power, energy', 'url': ''},
            {'title': 'Sound – Wave Nature', 'description': 'Wave nature of sound', 'url': ''},
            {'title': 'Modern Physics – Atoms & Nuclei', 'description': 'Basics of atoms and nuclei', 'url': ''},
            {'title': 'Motion – Graphs & Equations', 'description': 'Graphs and equations of motion', 'url': ''}
        ]
    },
    {
        'name': 'Chemistry',
        'class_level': '9th',
        'description': 'Curated Chemistry topics for 9th class',
        'videos': [
            {'title': 'Matter – Properties and States', 'description': 'States and properties of matter', 'url': ''},
            {'title': 'Elements, Compounds & Mixtures', 'description': 'Differences and examples', 'url': ''},
            {'title': 'Atomic Structure – Introduction', 'description': 'Basics of atomic structure', 'url': ''},
            {'title': 'Chemical Reactions – Types', 'description': 'Overview of reaction types', 'url': ''},
            {'title': 'Periodic Table – Basics', 'description': 'Basics of periodic classification', 'url': ''},
            {'title': 'Acids, Bases & Salts', 'description': 'Properties and reactions', 'url': ''},
            {'title': 'Metals and Non-Metals', 'description': 'Extraction and properties', 'url': ''},
            {'title': 'Carbon and Its Compounds', 'description': 'Carbon compounds overview', 'url': ''},
            {'title': 'Water – Properties & Importance', 'description': 'Water properties and importance', 'url': ''},
            {'title': 'Air – Composition and Reactions', 'description': 'Composition of air and reactions', 'url': ''}
        ]
    },
    {
        'name': 'Chemistry',
        'class_level': '10th',
        'description': 'Curated Chemistry topics for 10th class',
        'videos': [
            {'title': 'Chemical Reactions and Equations', 'description': 'Writing and balancing equations', 'url': ''},
            {'title': 'Acids, Bases & Salts (Detailed)', 'description': 'Detailed properties and uses', 'url': ''},
            {'title': 'Metals and Non-Metals (Extraction & Properties)', 'description': 'Extraction and properties', 'url': ''},
            {'title': 'Carbon Compounds (Hydrocarbons, Functional Groups)', 'description': 'Hydrocarbons and functional groups', 'url': ''},
            {'title': 'Periodic Classification of Elements', 'description': 'Trends and periodicity', 'url': ''},
            {'title': 'Chemical Bonding', 'description': 'Types of chemical bonds', 'url': ''},
            {'title': 'Electrolysis', 'description': 'Electrolytic processes', 'url': ''},
            {'title': 'Water Chemistry', 'description': 'Properties and treatment', 'url': ''},
            {'title': 'Industrial Chemistry (Cement, Fertilizers, etc.)', 'description': 'Industrial processes overview', 'url': ''},
            {'title': 'Environmental Chemistry', 'description': 'Pollution and green chemistry', 'url': ''}
        ]
    },
    {
        'name': 'Mathematics',
        'class_level': '9th',
        'description': 'Curated Mathematics topics for 9th class',
        'videos': [
            {'title': 'Number Systems', 'description': 'Number system basics', 'url': ''},
            {'title': 'Polynomials – Basics', 'description': 'Introduction to polynomials', 'url': ''},
            {'title': 'Linear Equations in Two Variables', 'description': 'Concepts and solutions', 'url': ''},
            {'title': 'Coordinate Geometry – Introduction', 'description': 'Basics of coordinate geometry', 'url': ''},
            {'title': 'Probability – Basics', 'description': 'Intro to probability', 'url': ''},
            {'title': 'Statistics – Mean, Median, Mode', 'description': 'Central tendency measures', 'url': ''},
            {'title': 'Surface Area and Volume', 'description': 'SA and volume of solids', 'url': ''},
            {'title': 'Triangles – Properties', 'description': 'Properties of triangles', 'url': ''},
            {'title': 'Circles – Theorems', 'description': 'Important circle theorems', 'url': ''},
            {'title': 'Geometry – Constructions', 'description': 'Basic constructions', 'url': ''}
        ]
    },
    {
        'name': 'Mathematics',
        'class_level': '10th',
        'description': 'Curated Mathematics topics for 10th class',
        'videos': [
            {'title': 'Real Numbers', 'description': 'Euclidean division and properties', 'url': ''},
            {'title': 'Polynomials (Advanced)', 'description': 'Advanced polynomial concepts', 'url': ''},
            {'title': 'Pair of Linear Equations in Two Variables', 'description': 'Pair of linear equations', 'url': ''},
            {'title': 'Quadratic Equations', 'description': 'Methods and applications', 'url': ''},
            {'title': 'Arithmetic Progressions', 'description': 'AP formulas and sums', 'url': ''},
            {'title': 'Circles – Tangents', 'description': 'Tangent properties', 'url': ''},
            {'title': 'Constructions – Advanced', 'description': 'Advanced constructions', 'url': ''},
            {'title': 'Trigonometry – Basics', 'description': 'Trigonometric ratios', 'url': ''},
            {'title': 'Applications of Trigonometry', 'description': 'Heights and distances', 'url': ''},
            {'title': 'Statistics & Probability', 'description': 'Data handling and probability', 'url': ''}
        ]
    }
]

conn = sqlite3.connect(db_path)
cur = conn.cursor()
for info in courses_data:
    cur.execute(
        "UPDATE course SET description = ?, video_data = ? WHERE name = ? AND class_level = ?",
        (info['description'], json.dumps(info['videos']), info['name'], info['class_level'])
    )
conn.commit()
conn.close()
print("Updated edureach_dev.db course descriptions and videos.")
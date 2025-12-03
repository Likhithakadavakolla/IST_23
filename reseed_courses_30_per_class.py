from app import app, db, Course
import json

def add_course(name, subject, class_level, description):
    return Course(
        name=name,
        subject=subject,
        class_level=class_level,
        description=description,
        video_data=json.dumps([{
            'title': name,
            'description': description,
            'url': ''
        }])
    )

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

if __name__ == '__main__':
    with app.app_context():
        # Remove existing courses and related progress
        db.session.execute(db.text('DELETE FROM progress'))
        db.session.execute(db.text('DELETE FROM course'))
        
        # Create 30 courses per class (10 per subject)
        for class_level, subjects in courses_per_class.items():
            for subject, topics in subjects.items():
                for topic in topics:
                    desc = f"{subject} - {topic}"
                    db.session.add(add_course(topic, subject, class_level, desc))
        db.session.commit()
        print('Reseeded courses: 30 per class (9th and 10th).')

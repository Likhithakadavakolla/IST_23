from app import app, db, Course, Assignment
from datetime import datetime

# Idempotent seeding: ensure 10 assignments per course.
# Generates simple placeholder questions per assignment.

TEMPLATE_QUESTIONS = [
    "Q1: Summarize today's topic in your own words.",
    "Q2: List 3 key terms and define them.",
    "Q3: Solve an example related to this topic.",
    "Q4: Describe a real-life application.",
    "Q5: Pose one question you still have."
]

NUM_ASSIGNMENTS = 10

def build_questions_text():
    return "|".join(TEMPLATE_QUESTIONS)

if __name__ == "__main__":
    with app.app_context():
        courses = Course.query.all()
        total_created = 0
        for course in courses:
            existing = Assignment.query.filter_by(course_id=course.id).count()
            to_create = max(0, NUM_ASSIGNMENTS - existing)
            for i in range(existing + 1, existing + 1 + to_create):
                a = Assignment(
                    course_id=course.id,
                    title=f"{course.name} - Assignment {i}",
                    description=f"Assessment for {course.name} ({course.class_level} {course.subject}).",
                    questions=build_questions_text(),
                    created_at=datetime.utcnow()
                )
                db.session.add(a)
                total_created += 1
        db.session.commit()
        print(f"Created {total_created} assignments (ensured {NUM_ASSIGNMENTS} per course).")

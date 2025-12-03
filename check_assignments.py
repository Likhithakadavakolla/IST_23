from app import app, db, Assignment
import json

with app.app_context():
    assignments = Assignment.query.all()
    print(f'Total assignments: {len(assignments)}')
    
    for a in assignments[:5]:
        print(f'\nID: {a.id}')
        print(f'Title: {a.title}')
        print(f'Course ID: {a.course_id}')
        print(f'Questions length: {len(a.questions or "")}')
        
        try:
            if a.questions:
                parsed = json.loads(a.questions)
                print(f'Question count: {len(parsed) if isinstance(parsed, list) else "N/A"}')
                if isinstance(parsed, list) and len(parsed) > 0:
                    print(f'First question: {parsed[0]}')
        except Exception as e:
            print(f'Error parsing questions: {e}')

from app import app, db, Assignment, Student
from flask_login import login_user
import json

with app.app_context():
    # Get first assignment
    assignment = Assignment.query.first()
    if assignment:
        print(f'Testing assignment: {assignment.title}')
        print(f'Assignment ID: {assignment.id}')
        
        # Try to parse questions
        try:
            questions = json.loads(assignment.questions)
            print(f'Number of questions: {len(questions)}')
            print(f'\nFirst 3 questions:')
            for i, q in enumerate(questions[:3]):
                print(f'\nQuestion {i+1}:')
                print(f'  Q: {q.get("q", "N/A")}')
                print(f'  Options: {q.get("options", {})}')
                print(f'  Answer: {q.get("answer", "N/A")}')
        except Exception as e:
            print(f'Error: {e}')
    else:
        print('No assignments found!')

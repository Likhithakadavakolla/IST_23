from app import app, db, Assignment, Course

with app.app_context():
    assignments = Assignment.query.all()
    print(f'Total assignments in DB: {len(assignments)}')
    
    for a in assignments:
        print(f'\nID: {a.id}')
        print(f'Title: {a.title}')
        print(f'Description: {a.description}')
        print(f'Course ID: {a.course_id}')
        
        if a.course_id:
            course = Course.query.get(a.course_id)
            if course:
                print(f'Course: {course.name}')
                print(f'Class: {course.class_level}')
                print(f'Subject: {course.subject}')
            else:
                print(f'Course not found!')
        else:
            print('No course linked')

from app import app, db, Assignment, Progress

target_title = '9th Class Physics – 30 MCQs'

if __name__ == '__main__':
    with app.app_context():
        to_keep = Assignment.query.filter_by(title=target_title).all()
        keep_ids = {a.id for a in to_keep}
        removed = 0
        removed_progress = 0
        # Delete progress for assignments we will remove
        if keep_ids:
            doomed_progress = Progress.query.filter(Progress.assignment_id.isnot(None)).filter(~Progress.assignment_id.in_(keep_ids)).all()
        else:
            doomed_progress = Progress.query.filter(Progress.assignment_id.isnot(None)).all()
        for p in doomed_progress:
            db.session.delete(p)
            removed_progress += 1
        # Delete assignments not in keep set
        if keep_ids:
            doomed = Assignment.query.filter(~Assignment.id.in_(keep_ids)).all()
        else:
            doomed = Assignment.query.all()
        for a in doomed:
            db.session.delete(a)
            removed += 1
        db.session.commit()
        print(f"Removed {removed} assignments and {removed_progress} related progress rows. Kept {len(keep_ids)} assignment(s).")

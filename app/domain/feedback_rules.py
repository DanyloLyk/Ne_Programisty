from app.models.feedback import Feedback
from .. import db 

def get_feedbacks():
    """Отримати всі відгуки (об'єкти)"""
    try:
        # Сортуємо: нові зверху
        return Feedback.query.order_by(Feedback.id.desc()).all()
    except Exception:
        return []

def get_feedback_by_id(feedback_id):
    return Feedback.query.get(feedback_id)

def add_feedback(title, description, user_id):
    try:
        new_feedback = Feedback(
            title=title,
            description=description,
            user_id=user_id 
        )
        db.session.add(new_feedback)
        db.session.commit()
        return new_feedback, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)

def delete_feedback_by_id(feedback_id):
    feedback = Feedback.query.get(feedback_id)
    if not feedback:
        return False
        
    try:
        db.session.delete(feedback)
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False

def edit_feedback_by_id(feedback_id, title=None, description=None):
    feedback = Feedback.query.get(feedback_id)
    if not feedback:
        return None, "Відгук не знайдено"
    
    try:
        if title: feedback.title = title
        if description: feedback.description = description
        
        db.session.commit()
        return feedback, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)
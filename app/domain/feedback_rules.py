from app.models.feedback import Feedback

def get_feedbacks():
    """Отримати всі відгуки"""
    try:
        # Сортуємо: нові зверху (desc)
        feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()
        return [f.to_dict() for f in feedbacks]
    except Exception as e:
        print(f"Error getting feedbacks: {e}")
        return []

def get_feedback_by_id(feedback_id):
    """Отримати один відгук"""
    try:
        return Feedback.query.get(feedback_id)
    except Exception as e:
        print(f"Error getting feedback {feedback_id}: {e}")
        return None

def add_feedback(title, description, user_id):
    """
    Створення нового відгуку.
    Важливо: приймаємо user_id, бо відгук має належати комусь.
    """
    try:
        new_feedback = Feedback(
            title=title,
            description=description,
            user_id=user_id 
        )
        db.session.add(new_feedback)
        db.session.commit()
        return new_feedback
    except Exception as e:
        db.session.rollback()
        print(f"Error adding feedback: {e}")
        return None

def delete_feedback_by_id(feedback_id):
    """Видалення відгуку"""
    try:
        feedback = Feedback.query.get(feedback_id)
        if not feedback:
            return False 
        
        db.session.delete(feedback)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        return False

def edit_feedback_by_id(feedback_id, title=None, description=None):
    """
    Оновлення відгуку.
    Міняємо тільки заголовок або текст. Автор (user_id) зазвичай не змінюється.
    """
    try:
        feedback = Feedback.query.get(feedback_id)
        if not feedback:
            return None
        
        if title: 
            feedback.title = title
        if description: 
            feedback.description = description
        
        db.session.commit()
        return feedback
    except Exception as e:
        db.session.rollback()
        return None
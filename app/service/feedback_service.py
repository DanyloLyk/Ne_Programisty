from requests import get
from ..domain.feedback_rules import (get_feedbacks, get_feedback_by_id, add_feedback,delete_feedback_by_id,edit_feedback_by_id)
from ..models.feedback import Feedback
from .. import db


class FeedbackService:
    @staticmethod
    def get_all_feedbacks_service():
        """Отримати список всіх відгуків"""
        return get_feedbacks()

    @staticmethod
    def get_feedback_by_id_service(feedback_id):
        """Отримати один відгук"""
        feedback = get_feedback_by_id(feedback_id)
        if not feedback:
            return None, "Feedback not found"
        return feedback, None

    @staticmethod
    def create_feedback_service(data, user_id):
        """
        Валідація та створення відгуку.
        user_id ми отримуємо окремо (зазвичай з current_user), 
        бо не можна дати користувачу вписати чужий ID в JSON.
        """
        title = data.get('title')
        description = data.get('description')

        # Перевірка 
        if not title or len(title) < 3:
            return None, "Title is too short (min 3 chars)"
        if not description or len(description) < 5:
            return None, "Description is too short (min 5 chars)"
        if len(description) > 300:
            return None, "Description is too long (max 300 chars)"
        if not user_id:
            return None, "User ID is required"

        new_feedback = add_feedback(title, description, user_id)
        
        if new_feedback:
            return new_feedback, None
        else:
            return None, "Database error during creation"

    @staticmethod
    def update_feedback_service(feedback_id, data):
        """Оновлення відгуку"""
        existing = get_feedback_by_id(feedback_id)
        if not existing:
            return None, "Feedback not found"
        # Валідація нових даних (якщо вони передані)
        if 'title' in data and len(data['title']) < 3:
             return None, "Title is too short"
             
        if 'description' in data and len(data['description']) < 5:
             return None, "Description is too short"

        updated_feedback = edit_feedback_by_id(
            feedback_id,
            title=data.get('title'),
            description=data.get('description')
        )
        return updated_feedback, None

    @staticmethod
    def delete_feedback_service(feedback_id):
        """Видалення відгуку"""
        result = delete_feedback_by_id(feedback_id)
        if result:
            return True, "Deleted successfully"
        return False, "Feedback not found or database error"
from ..domain import feedback_rules

class FeedbackService:
    @staticmethod
    def get_all_feedbacks_service():
        return feedback_rules.get_feedbacks()

    @staticmethod
    def get_feedback_by_id_service(feedback_id):
        feedback = feedback_rules.get_feedback_by_id(feedback_id)
        if not feedback:
            return None, "Feedback not found"
        return feedback, None

    @staticmethod
    def create_feedback_service(data, user_id):
        title = data.get('title')
        description = data.get('description')

        # Валідація
        if not title or len(title) < 3:
            return None, "Заголовок занадто короткий (мін. 3 символи)"
        if not description or len(description) < 5:
            return None, "Текст відгуку занадто короткий"
        if not user_id:
            return None, "Необхідна авторизація"

        return feedback_rules.add_feedback(title, description, user_id)

    @staticmethod
    def update_feedback_service(feedback_id, data):
        # Валідація при оновленні
        if 'title' in data and len(data['title']) < 3:
             return None, "Заголовок занадто короткий"
             
        if 'description' in data and len(data['description']) < 5:
             return None, "Текст відгуку занадто короткий"

        return feedback_rules.edit_feedback_by_id(
            feedback_id,
            title=data.get('title'),
            description=data.get('description')
        )

    @staticmethod
    def delete_feedback_service(feedback_id):
        result = feedback_rules.delete_feedback_by_id(feedback_id)
        if result:
            return True, "Відгук успішно видалено"
        return False, "Відгук не знайдено"
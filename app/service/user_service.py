from ..models.user import User
from ..domain import user_rules

class UserService:
    @staticmethod
    def get_all_users() -> list[User]:
        return user_rules.get_users()
    
    @staticmethod
    def get_user_by_id(user_id: int) -> User | None:
        return user_rules.get_user_by_id(user_id)
    
    @staticmethod
    def authorize_user(username: str, password: str) -> User | None:
        """
        Перевіряє облікові дані.
        """
        user = user_rules.get_user_by_username(username)
        if user and user.check_password(password):
            return user
        return None

    @staticmethod
    def registration(nickname: str, email: str, password: str, password_confirm: str):
        """
        Returns: (User, None) або (None, error_message)
        """
        if not nickname or not email or not password:
            return None, "Всі поля є обов'язковими"
            
        return user_rules.add_user(nickname, email, password, password_confirm)

    @staticmethod
    def delete_user(user_id: int) -> bool:
        if not user_id:
            return False
        return user_rules.delete_user(user_id)
    
    @staticmethod
    def edit_user(user_id: int, nickname: str, email: str, status: str, privilege: str, password: str = None):
        """
        Returns: (User, None) або (None, error_message)
        """
        return user_rules.edit_user(user_id, nickname, email, status, privilege, password)
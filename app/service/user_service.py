from ..models.user import User
from ..domain.user_rules import add_user, get_user_by_id, get_users, delete_user, edit_user

class UserService:
    @staticmethod
    def get_all_users() -> list[User]:
        """
        Повертає список усіх користувачів.
        """
        return get_users()
    
    @staticmethod
    def get_user_by_id(user_id: int) -> User | None:
        """
        Повертає користувача за його ID.
        
        user_id: ID користувача
        """
        return get_user_by_id(user_id)
    
    @staticmethod
    def authorize_user(username: str, password: str) -> User | None:
        """
        Перевіряє облікові дані користувача, і повертає id користувача, якщо авторизація успішна.       
        Args:
            username: Ім'я користувача
            password: Пароль користувача
        
        Returns:
            User | None: Об'єкт користувача, якщо авторизація успішна, інакше None
        """
        user = User.query.filter_by(nickname=username).first()
        if user and user.check_password(password):
            return user
        return None

    @staticmethod
    def registration(nickname: str, email: str, password: str, password_confirm: str) -> User:
        """
        Створює нового користувача.
        
        Args:
            nickname: Ім'я користувача
            email: Електронна пошта користувача
            password: Пароль користувача
            password_confirm: Повторний пароль для підтвердження
        
        Returns:
            User | None: Реєстрація користувача або None, якщо реєстрація не вдалася
        """
        if not nickname or not email or not password or not password_confirm:
            return None
        else: 
            return add_user(nickname, email, password, password_confirm)

    @staticmethod
    def delete_user(user_id: int) -> bool:
        """
        Видаляє користувача за його ID.
        
        user_id: ID користувача
        """
        if get_user_by_id(user_id) is None:
            return False
        elif user_id is None:
            return False
        else:
            return delete_user(user_id)
    
    @staticmethod
    def edit_user(user_id: int, nickname: str, email: str, status: str, privilege: str, password: str = None) -> bool:
        """
        Редагує інформацію про користувача.
        
        user_id: ID користувача
        nickname: Ім'я користувача
        email: Електронна пошта користувача
        status: Статус користувача
        privilege: Привілеї користувача
        password: Новий пароль користувача (необов'язково)
        """
        if get_user_by_id(user_id) is None:
            return False
        else:
            return edit_user(user_id, nickname, email, status, privilege, password)
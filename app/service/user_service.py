from ..models.user import User

class UserService:
    @staticmethod
    def get_user_by_id(user_id: int) -> User | None:
        """
        Повертає користувача за його ID.
        
        user_id: ID користувача
        """
        return User.query.get(user_id)
    
    @staticmethod
    def check_user_credentials(username: str, password: str) -> bool:
        """
        Перевіряє облікові дані користувача.
        
        Args:
            username: Ім'я користувача
            password: Пароль користувача
        
        Returns:
            bool: True, якщо облікові дані вірні, інакше False
        """
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return True
        return False
    
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

from ..models.user import User
from ..domain import user_rules
from flask import url_for
from datetime import timedelta
from flask_jwt_extended import create_access_token, decode_token 

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
    
    @staticmethod
    def request_password_reset(email):
        user = user_rules.get_user_by_email(email)
        if not user:
            # З міркувань безпеки ми не кажемо "імейл не знайдено", 
            # щоб хакери не перевіряли базу. Кажемо "Якщо імейл є, ми відправили лист".
            # Але для тесту повернемо None, щоб ти бачив.
            return None, "Користувача з таким email не знайдено"

        # 1. Генеруємо токен, який живе 15 хвилин
        # Ми додаємо additional_claims={'type': 'reset'}, щоб відрізнити його від login-токена
        reset_token = create_access_token(
            identity=str(user.id), 
            expires_delta=timedelta(minutes=15),
            additional_claims={"purpose": "password_reset"} 
        )

        # 2. Формуємо посилання (уяви, що це посилання на твій фронтенд)
        # Наприклад: http://localhost:5000/reset-password?token=...
        reset_link = f"http://localhost:5000/reset-password?token={reset_token}"

        # 3. ІМІТАЦІЯ ВІДПРАВКИ ПОШТИ (щоб не налаштовувати SMTP зараз)
        print(f"\n{'='*30}")
        print(f"📧 EMAIL SIMULATION FOR: {email}")
        print(f"🔗 LINK: {reset_link}")
        print(f"🔑 TOKEN: {reset_token}")
        print(f"{'='*30}\n")

        return reset_token, None

    @staticmethod
    def reset_password_with_token(token, new_password, confirm_password):
        if new_password != confirm_password:
            return False, "Паролі не співпадають"

        try:
            # 1. Розшифровуємо токен вручну
            decoded_token = decode_token(token)
            
            # 2. Перевіряємо, чи це токен саме для скидання пароля
            if decoded_token.get("purpose") != "password_reset":
                return False, "Невірний тип токена. Це не токен скидання пароля."

            user_id = decoded_token["sub"] # 'sub' це identity (id юзера)
            
            # 3. Оновлюємо пароль
            success = user_rules.update_password(user_id, new_password)
            if success:
                return True, None
            else:
                return False, "Помилка бази даних"

        except Exception as e:
            # Токен прострочений або підроблений
            return False, f"Токен недійсний або прострочений: {str(e)}"
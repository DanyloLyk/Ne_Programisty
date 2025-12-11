from .. import db
from app.models.user import User
from sqlalchemy.exc import IntegrityError

def get_users():
    return User.query.all()

def get_user_by_id(user_id):
    return User.query.get(user_id)

def get_user_by_username(username):
    return User.query.filter_by(nickname=username).first()

def add_user(nickname, email, password, password_confirm):
    # 1. Валідація паролів
    if password != password_confirm:
        return None, "Паролі не співпадають"

    # 2. Перевірка на існування (email АБО nickname)
    existing_user = User.query.filter((User.email == email) | (User.nickname == nickname)).first()
    if existing_user:        
        return None, "Користувач з таким email або нікнеймом вже існує"

    try:
        new_user = User(nickname=nickname, email=email)
        new_user.set_password(password)  
        
        db.session.add(new_user)
        db.session.commit()
        
        return new_user, None
    except Exception as e:
        db.session.rollback()
        return None, f"Помилка бази даних: {str(e)}"

def delete_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return False
    
    try:
        db.session.delete(user)
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False
    
def edit_user(user_id, nickname, email, status, privilege, password=None):
    user = User.query.get(user_id)
    if user is None:
        return None, "Користувача не знайдено"
    
    # Перевірка унікальності нікнейму (якщо він змінюється)
    if nickname and nickname != user.nickname:
        if User.query.filter_by(nickname=nickname).first():
            return None, f"Нікнейм '{nickname}' вже зайнятий"

    # Оновлення полів
    if nickname: user.nickname = nickname
    if email: user.email = email
    if status: user.status = status
    if privilege: user.privilege = privilege

    if password:
        user.set_password(password)

    # Валідація рівнів (щоб не прописали неіснуючий статус)
    user.ensure_valid_levels()

    try:
        db.session.commit()
        return user, None # Повертаємо оновленого юзера
    except IntegrityError:
        db.session.rollback()
        return None, "Помилка: email або нікнейм вже зайняті"
    except Exception as e:
        db.session.rollback()
        return None, f"Системна помилка: {str(e)}"
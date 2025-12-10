from .. import db
from app.models.user import User
from flask import session

def get_users():
    return User.query.all()

def get_user_by_id(user_id):
    return User.query.get(user_id)

def check_password_for_confirmation(password, password_confirm):
    if password != password_confirm:
        return False
    return True


def add_user(nickname, email, password, password_confirm):
    if check_password_for_confirmation(password, password_confirm):
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:        
            return False
        new_user = User(nickname=nickname, email=email)
        new_user.set_password(password)  
        db.session.add(new_user)
        db.session.commit()

        session.permanent = True
        session['user_id'] = new_user.id
        session['user_nickname'] = new_user.nickname
        session['user_status'] = new_user.status 

        return new_user
    else:
        return False

def delete_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return False
    else:
        db.session.delete(user)
        db.session.commit()
        return True
    
def edit_user(user_id, nickname, email, status, privilege, password=None):
    
    user = User.query.get(user_id)

    if user is None:
        return False
    
    if nickname is not None:
        user.nickname = nickname

    if email is not None:
        user.email = email
    
    if status is not None:
        user.status = status

    if privilege is not None:
        user.privilege = privilege

    if user.password != password and password is not None:
        user.set_password(password)

    user.ensure_valid_levels()
    try:
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error editing user: {e}")
        return False
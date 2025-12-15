from app.models.desktop import Desktop
from .. import db

def get_desktops():
    """Повертає список словників для всіх товарів"""
    try:
        desktops = Desktop.query.all()
        # Повертаємо список словників, щоб сервіс міг зразу віддати JSON
        return [desktop.to_dict() for desktop in desktops] 
    except Exception as e:
        return []

def get_desktop_by_id(desktop_id):
    return Desktop.query.get(desktop_id)

def add_desktop(name, description, price, image):
    try:
        new_desktop = Desktop(
            name=name,
            description=description,
            price=price,
            image=image
        )
        db.session.add(new_desktop)
        db.session.commit()
        return new_desktop, None
    except Exception as e:
        db.session.rollback()
        return None, f"Помилка бази даних: {str(e)}"

def delete_desktop_by_id(desktop_id):
    desktop = Desktop.query.get(desktop_id)
    if not desktop:
        return False
    
    try:
        db.session.delete(desktop)
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False

def edit_desktop_by_id(desktop_id, name=None, description=None, price=None, image=None):
    desktop = Desktop.query.get(desktop_id)
    if not desktop:
        return None, "Товар не знайдено"

    try:
        if name: desktop.name = name
        if description: desktop.description = description
        if price: desktop.price = price
        if image: desktop.image = image
        
        db.session.commit()
        return desktop, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)




#def get_desktops_paginated(page: int, per_page: int) -> List[dict]: щоб не отримувати одразу на сторінку 1000 настолок(скоро)
    # Отримати, наприклад, тільки з 10-го по 20-й товар
    #pass
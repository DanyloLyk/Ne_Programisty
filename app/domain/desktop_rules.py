from app.models.desktop import Desktop
from .. import db

def get_desktops():
    """Отримати всі десктопи та перетворити їх у словники (JSON format)"""
    try:
        desktops = Desktop.query.all()
        return [desktop.to_dict() for desktop in desktops] 
    except Exception as e:
        print(f"Error getting desktops: {e}")
        return []

def get_desktop_by_id(desktop_id):
    """Отримати один десктоп або None, якщо не знайдено"""
    try:
        return Desktop.query.get(desktop_id)
    except Exception as e:
        print(f"Error getting desktop {desktop_id}: {e}")
        return None

def add_desktop(name, description, price, image):
    """Створення нового товару"""
    try:
        new_desktop = Desktop(
            name=name,
            description=description,
            price=price,
            image=image
        )
        db.session.add(new_desktop)
        db.session.commit()
        return new_desktop
    except Exception as e:
        db.session.rollback() # Відкочуємо зміни, якщо помилка
        print(f"Error adding desktop: {e}")
        return None



def delete_desktop_by_id(desktop_id):
    """Видалення товару"""
    try:
        desktop = Desktop.query.get(desktop_id)
        if not desktop:
            return False # Товар не знайдено
        
        db.session.delete(desktop)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        return False

def edit_desktop_by_id(desktop_id, name=None, description=None, price=None, image=None):
    """
    Оновлення товару.
    Ми використовуємо None за замовчуванням, щоб оновлювати тільки те, що передали.
    """
    try:
        desktop = Desktop.query.get(desktop_id)
        if not desktop:
            return None
        if name: desktop.name = name
        if description: desktop.description = description
        if price: desktop.price = price
        if image: desktop.image = image
        
        db.session.commit()
        return desktop
    except Exception as e:
        db.session.rollback()
        return None




#def get_desktops_paginated(page: int, per_page: int) -> List[dict]: щоб не отримувати одразу на сторінку 1000 настолок(скоро)
    # Отримати, наприклад, тільки з 10-го по 20-й товар
    #pass
from .. import db
from app.models.order import Order
from app.models.cart import CartItem
from app.models.user import User
from sqlalchemy.orm import joinedload

def get_all_orders():
    orders = Order.query.options(joinedload(Order.user)).order_by(Order.id.desc()).all()
    
    # Використовуємо наш оновлений метод to_dict()
    return [order.to_dict() for order in orders]


def get_order_by_id(order_id):
    return Order.query.get(order_id)

def get_user_orders(user_id):
    try:
        return Order.query.filter_by(user_id=user_id).all()
    except Exception:
        return []

def create_order_from_cart(user_id):
    # 1. Отримуємо юзера для знижки
    user = User.query.get(user_id)
    if not user:
        return None, "Користувача не знайдено"

    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    if not cart_items:
        return None, "Кошик порожній"

    try:
        # 2. Правильно беремо знижку з властивості об'єкта User
        discount = user.discount_multiplier 

        # 3. Створюємо замовлення (метод моделі Order)
        order = Order.add_order(user_id, cart_items, discount)
        
        db.session.add(order)
        
        # 4. Очищаємо кошик
        for item in cart_items:
            db.session.delete(item)
        
        db.session.commit()
        return order, None
        
    except ValueError as e:
        db.session.rollback()
        return None, str(e)
    except Exception as e:
        db.session.rollback()
        return None, f"Системна помилка: {str(e)}"

def delete_order_by_id(order_id):
    order = Order.query.get(order_id)
    if not order:
        return False
        
    try:
        db.session.delete(order)
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False
    
def update_order_status(order_id, status):
    order = Order.query.get(order_id)
    if not order:
        return None, "Замовлення не знайдено"
    
    try:
        # Валідацію статусу зробить модель (якщо там є @validates)
        # або ми це вже перевірили в сервісі
        order.status = status
        db.session.commit()
        return order, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)
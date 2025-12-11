from flask import jsonify
from .. import db
from app.models.order import Order
from app.models.cart import CartItem
from app.models.user import User

def get_all_orders():
    return Order.query.all()

def get_order(order_id):
    return Order.query.get(order_id)

def get_orders(user_id):
    return Order.query.filter_by(user_id=user_id).all()

def add_order(user_id):
    try:
        
        cart_items = CartItem.query.filter_by(user_id=user_id).all()
        
        if not cart_items or len(cart_items) == 0:
            return jsonify(message="Кошик порожній, неможливо створити замовлення"), 400
        
        privelege_user = User.query.get(user_id).privilege  
        discount = getattr(privelege_user, 'discount_multiplier', 1.0)

        order = Order.add_order(user_id, cart_items, discount)
        
        db.session.add(order)
        db.session.flush()  
        
        for cart_item in cart_items:
            db.session.delete(cart_item)
        
        db.session.commit()
    
        return order, None
        
    except ValueError as e:
        db.session.rollback()
        return None, f"Помилка даних: {str(e)}"
    except Exception as e:
        db.session.rollback()
        print(f"CRITICAL ERROR: {e}")
        return None, f"Системна помилка: {str(e)}"

def delete_order(order_id):
    order = Order.query.get(order_id)
    if order is None:
        return False
    else:
        db.session.delete(order)
        db.session.commit()
        return True
    
def edit_order(order_id, status=None):
    order = Order.query.get(order_id)

    if order is None:
        return False, f"Замовлення з id={order_id} не знайдено"
    
    if status is not None:
        order.status = status
    else:        
        return None, f"Cтатус замовлення не оновлено, зберігся поточний статус: {order.status}"

    try:
        db.session.commit()
        order = Order.query.get(order_id)
        return order, None
    except Exception as e:
        db.session.rollback()
        print(f"Error editing order: {e}")
        return None, f"Помилка при редагуванні замовлення: {str(e)}"
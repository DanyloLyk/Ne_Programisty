from flask import jsonify
from .. import db
from app.models.order import Order
from app.models.cart import CartItem
from app.models.user import User

def get_all_orders():
    return Order.query.all()

def get_order(user_id):
    return Order.query.get(user_id)

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
        
        order_id = order.id
        return True, order.to_dict(), order_id, 200
        
    except ValueError as e:
        db.session.rollback()
        print(f"ValueError при створенні замовлення: {e}")
        return jsonify(message=f"ValueError при створенні замовлення: {e}"), 400
    except Exception as e:
        db.session.rollback()
        print(f"Помилка при створенні замовлення: {e}")
        return jsonify(message=f"Помилка при створенні замовлення: {e}"), 500
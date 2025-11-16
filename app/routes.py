from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from .models.desktop import Desktop
from .models.cart import CartItem
from .models.order import Order
from . import db
from .utils import download_image

main = Blueprint('main', __name__)

# Константа для дефолтного користувача (оскільки система користувачів не реалізована)
DEFAULT_USER_ID = 1

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/news')
def news():
    return render_template('news.html')

@main.route('/contacts')
def contacts():
    return render_template('contacts.html')

@main.route('/catalog')
def catalog():
    db.session.commit()
    desktops = Desktop.query.all()
    # Використовуємо дефолтного користувача
    return render_template("catalog.html", desktops=desktops, user_id=DEFAULT_USER_ID)

@main.route('/cart')
def cart():
    db.session.commit()
    # Показуємо тільки товари дефолтного користувача
    cart_items = CartItem.query.filter_by(user_id=DEFAULT_USER_ID).all()
    
    # Конвертуємо об'єкти CartItem в словники для JSON серіалізації
    carts = []
    for item in cart_items:
        cart_dict = {
            'id': item.id,
            'user_id': item.user_id,
            'item_id': item.item_id,
            'quantity': item.quantity,
            'item': {
                'id': item.item.id,
                'name': item.item.name,
                'description': item.item.description,
                'price': item.item.price,
                'image': item.item.image
            } if item.item else None
        }
        carts.append(cart_dict)
    
    carts = carts if len(carts) != 0 else None
    return render_template('cart.html', carts=carts, isFooter=False, user_id=DEFAULT_USER_ID)

@main.route('/add_to_cart/<int:item_id>')
def add_to_cart(item_id):
    """
    Додає товар в кошик дефолтного користувача
    URL: /add_to_cart/<item_id>?quantity=1
    """
    try:
        # Використовуємо дефолтного користувача
        user_id = DEFAULT_USER_ID
        quantity = int(request.args.get('quantity', 1))
        
        # Перевіряємо, чи існує товар
        desktop = Desktop.query.get_or_404(item_id)
        
        # Перевіряємо, чи товар вже є в кошику користувача
        existing_item = CartItem.query.filter_by(
            user_id=user_id, 
            item_id=item_id
        ).first()
        
        if existing_item:
            # Якщо товар вже є, збільшуємо кількість
            existing_item.quantity += quantity
        else:
            # Якщо товару немає, створюємо новий запис
            new_cart_item = CartItem(
                user_id=user_id,
                item_id=item_id,
                quantity=quantity
            )
            db.session.add(new_cart_item)
        
        db.session.commit()
        # Повертаємо на каталог замість кошика
        return redirect(url_for('main.catalog'))
        
    except Exception as e:
        db.session.rollback()
        return redirect(url_for('main.catalog'))

@main.route('/remove_from_cart/<int:item_id>')
def remove_from_cart(item_id):
    """
    Видаляє товар з кошика дефолтного користувача
    URL: /remove_from_cart/<item_id>
    """
    try:
        # Використовуємо дефолтного користувача
        user_id = DEFAULT_USER_ID
        
        # Знаходимо товар в кошику
        cart_item = CartItem.query.filter_by(
            user_id=user_id,
            item_id=item_id
        ).first()
        
        if cart_item:
            db.session.delete(cart_item)
            db.session.commit()
        
        return redirect(url_for('main.cart'))
        
    except Exception as e:
        db.session.rollback()
        return redirect(url_for('main.cart'))

@main.route('/update_cart/<int:item_id>')
def update_cart(item_id):
    """
    Змінює кількість товару в кошику
    URL: /update_cart/<item_id>?action=increase або /update_cart/<item_id>?action=decrease
    """
    try:
        # Використовуємо дефолтного користувача
        user_id = DEFAULT_USER_ID
        action = request.args.get('action', 'increase')  # increase або decrease
        
        # Знаходимо товар в кошику
        cart_item = CartItem.query.filter_by(
            user_id=user_id,
            item_id=item_id
        ).first()
        
        if cart_item:
            if action == 'increase':
                # Збільшуємо кількість
                cart_item.quantity += 1
            elif action == 'decrease':
                # Зменшуємо кількість, але не менше 1
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                else:
                    # Якщо кількість 1, видаляємо товар
                    db.session.delete(cart_item)
            
            db.session.commit()
        
        return redirect(url_for('main.cart'))
        
    except Exception as e:
        db.session.rollback()
        return redirect(url_for('main.cart'))

@main.route('/checkout')
def checkout():
    """
    Сторінка підтвердження замовлення
    """
    db.session.commit()
    user_id = DEFAULT_USER_ID
    
    # Отримуємо кошик користувача
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    
    if not cart_items or len(cart_items) == 0:
        return redirect(url_for('main.cart'))
    
    # Конвертуємо об'єкти CartItem в словники для відображення
    carts = []
    total_amount = 0.0
    total_items = 0
    
    for item in cart_items:
        if not item.item:
            continue
        
        # Конвертуємо ціну в число, видаляючи пробіли
        price_str = str(item.item.price).replace(' ', '').replace(',', '.')
        price = float(price_str) if price_str else 0.0
        item_total = price * item.quantity
        total_amount += item_total
        total_items += item.quantity
        
        cart_dict = {
            'id': item.id,
            'user_id': item.user_id,
            'item_id': item.item_id,
            'quantity': item.quantity,
            'item': {
                'id': item.item.id,
                'name': item.item.name,
                'description': item.item.description,
                'price': price,
                'image': item.item.image
            },
            'total': item_total
        }
        carts.append(cart_dict)
    
    return render_template('checkout.html', 
                         carts=carts, 
                         total_amount=round(total_amount, 2),
                         total_items=total_items,
                         user_id=user_id,
                         isFooter=False)

@main.route('/add_order', methods=['POST'])
def add_order():
    """
    Створює замовлення з кошика дефолтного користувача
    """
    try:
        # Використовуємо дефолтного користувача
        user_id = DEFAULT_USER_ID
        
        # Отримуємо кошик користувача
        cart_items = CartItem.query.filter_by(user_id=user_id).all()
        
        if not cart_items or len(cart_items) == 0:
            return redirect(url_for('main.cart'))
        
        # Отримуємо discount з форми (якщо є)
        discount = float(request.form.get('discount', 1.0))
        
        # Створюємо замовлення
        order = Order.add_order(user_id, cart_items, discount)
        
        # Зберігаємо замовлення в БД
        db.session.add(order)
        db.session.flush()  # Отримуємо ID замовлення
        
        # Видаляємо товари з кошика після успішного створення замовлення
        for cart_item in cart_items:
            db.session.delete(cart_item)
        
        # Комітуємо всі зміни разом
        db.session.commit()
        
        # Перенаправляємо на сторінку успіху
        return redirect(url_for('main.order_success', order_id=order.id))
        
    except ValueError as e:
        db.session.rollback()
        print(f"ValueError при створенні замовлення: {e}")
        return redirect(url_for('main.cart'))
    except Exception as e:
        db.session.rollback()
        print(f"Помилка при створенні замовлення: {e}")
        import traceback
        traceback.print_exc()
        return redirect(url_for('main.cart'))

@main.route('/order_success/<int:order_id>')
def order_success(order_id):
    """
    Сторінка успішного оформлення замовлення
    """
    order = Order.query.get_or_404(order_id)
    return render_template('order_success.html', order=order, isFooter=False)
    

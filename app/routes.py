from functools import wraps
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash, g, abort
from .models.desktop import Desktop
from .models.cart import CartItem
from .models.order import Order
from . import db
from .models.feedback import Feedback
from .models.news import News, NewsImage
from app.utils import download_image
from .models.user import User
from sqlalchemy.orm import joinedload


main = Blueprint('main', __name__)


def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not getattr(g, 'current_user', None):
            flash('Увійдіть, щоб продовжити.', 'warning')
            return redirect(url_for('main.index'))
        return view_func(*args, **kwargs)

    return wrapper


def privilege_required(*allowed_statuses):
    """Decorator to require that current_user exists and has one of the allowed statuses.

    Usage: @privilege_required('Admin', 'Moder')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            user = getattr(g, 'current_user', None)
            print(f"DEBUG: privilege_required check for user: {user, user.status if user else None}, allowed_statuses: {allowed_statuses}")
            if not user:
                flash('Увійдіть, щоб продовжити.', 'warning')
                return redirect(url_for('main.index'))

            if user.status not in allowed_statuses:
                flash('Недостатньо прав для доступу до цієї сторінки.', 'danger')
                return redirect(url_for('main.index'))

            return view_func(*args, **kwargs)

        return wrapper

    return decorator


@main.before_app_request
def load_current_user():
    user_id = session.get('user_id')
    g.current_user = User.query.get(user_id) if user_id else None


@main.app_context_processor
def inject_current_user():
    return {'current_user': getattr(g, 'current_user', None)}

@main.route('/')
def index():
    # Показуємо головну сторінку та формуємо топ-3 найпопулярніших товарів
    try:
        # Збираємо всі замовлення та агрегуємо кількість придбаних одиниць по item_id
        counts = {}
        orders = Order.query.all()
        for order in orders:
            for it in (order.items or []):
                iid = it.get('item_id')
                qty = int(it.get('quantity', 0) or 0)
                if not iid:
                    continue
                counts[iid] = counts.get(iid, 0) + qty

        # Підбираємо дані по товарах
        popular = []
        for iid, total_qty in counts.items():
            product = Desktop.query.get(iid)
            if not product:
                continue
            # Приводимо ціну до float (як це робиться в інших місцях)
            try:
                price_str = str(product.price).replace(' ', '').replace(',', '.') if product.price is not None else '0'
                price = float(price_str) if price_str else 0.0
            except Exception:
                price = 0.0

            popular.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'image': product.image,
                'price': price,
                'bought_count': total_qty,
            })

        # Сортуємо та беремо топ-3
        popular_sorted = sorted(popular, key=lambda x: x['bought_count'], reverse=True)[:3]
    except Exception:
        popular_sorted = []
    return render_template('index.html', top_popular=popular_sorted)

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/news')
def news():
    all_news = News.query.all()
    return render_template('news.html', news=all_news)


@main.route('/contacts')
def contacts():
    return render_template('contacts.html')

@main.route('/feedback')
@login_required
def feedback():
    return render_template('feedback.html')


@main.route('/submit_feedback', methods=['POST'])
@login_required
def submit_feedback():
    try:
        import traceback
        data = request.get_json()
        title = data.get('title')
        description = data.get('description')

        if getattr(g, 'current_user', None):
            user_id = g.current_user.id
            print(f"DEBUG: Successfully retrieved user ID: {user_id}")
        else:
            print("DEBUG: Current user is NOT set or not authenticated.")
            return jsonify({'success': False, 'error': 'Користувач не авторизований для відправки.'}), 401

        if not title or not description:
            return jsonify({'success': False, 'error': "Заголовок та опис є обов'язковими."}), 400

        if len(title) > 100 or len(description) > 300:
            return jsonify({'success': False, 'error': 'Перевищено ліміт символів.'}), 400

        new_feedback = Feedback(
            title=title,
            description=description,
            user_id=user_id
        )
        db.session.add(new_feedback)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Відгук додано!'}), 201
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        print(f"Помилка при збереженні відгуку: {e}")
        return jsonify({'success': False, 'error': 'Внутрішня помилка сервера.'}), 500


@main.route('/catalog')
def catalog():
    desktops = Desktop.query.all()
    return render_template("catalog.html", desktops=desktops, user_id=session.get('user_id'))

@main.route('/cart')
@login_required
def cart():
    user = g.current_user
    cart_items = CartItem.query.filter_by(user_id=user.id).all()
    
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
                'price': float(str(item.item.price).replace(' ', '').replace(',', '.')) if item.item.price is not None else 0.0,
                'image': item.item.image
            } if item.item else None
        }
        carts.append(cart_dict)
    
    # Ensure we pass a JSON-serializable empty list (not `None`) to the template
    # so `JSON.parse('{{ carts | tojson | safe }}')` in the template won't throw.
    carts = carts if len(carts) != 0 else []
    # Передаємо інформацію про знижку користувача (множник)
    discount_multiplier = getattr(user, 'discount_multiplier', 1.0)
    discount_percent = getattr(user, 'discount_percent', 0)
    # Також збираємо простий список замовлень користувача для відображення в кошику
    try:
        user_orders = Order.query.filter_by(user_id=user.id).order_by(Order.id.desc()).all()
    except Exception:
        user_orders = []

    orders_summary = []
    for order in user_orders:
        items_summary = []
        for it in (order.items or []):
            try:
                # намагаємось знайти назву та ціну товару по item_id
                product = Desktop.query.get(it.get('item_id'))
                name = product.name if product else f"Товар #{it.get('item_id')}"
                price_str = str(product.price).replace(' ', '').replace(',', '.') if product and product.price is not None else '0'
                price = float(price_str) if price_str else 0.0
            except Exception:
                name = f"Товар #{it.get('item_id')}"
                price = 0.0

            items_summary.append({
                'item_id': it.get('item_id'),
                'name': name,
                'quantity': it.get('quantity'),
                'price': price,
            })

        orders_summary.append({
            'id': order.id,
            'status': order.status,
            'total_amount': order.total_amount,
            'order_items': items_summary,
        })

    return render_template('cart.html', carts=carts, isFooter=False, user_id=user.id,
                           discount_multiplier=discount_multiplier,
                           discount_percent=discount_percent,
                           orders=orders_summary)

@main.route('/add_to_cart/<int:item_id>')
@login_required
def add_to_cart(item_id):
    """
    Додає товар в кошик дефолтного користувача
    URL: /add_to_cart/<item_id>?quantity=1
    """
    try:
        user_id = g.current_user.id
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
@login_required
def remove_from_cart(item_id):
    """
    Видаляє товар з кошика дефолтного користувача
    URL: /remove_from_cart/<item_id>
    """
    try:
        user_id = g.current_user.id
        
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
@login_required
def update_cart(item_id):
    """
    Змінює кількість товару в кошику
    URL: /update_cart/<item_id>?action=increase або /update_cart/<item_id>?action=decrease
    """
    try:
        user_id = g.current_user.id
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
@login_required
def checkout():
    """
    Сторінка підтвердження замовлення
    """
    user_id = g.current_user.id
    
    # Отримуємо кошик користувача
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    
    if not cart_items or len(cart_items) == 0:
        return redirect(url_for('main.cart'))
    
    # Конвертуємо об'єкти CartItem в словники для відображення
    carts = []
    total_amount = 0.0
    total_items = 0

    # Отримуємо множник знижки для поточного користувача
    discount_multiplier = getattr(g.current_user, 'discount_multiplier', 1.0)
    discount_percent = getattr(g.current_user, 'discount_percent', 0)

    for item in cart_items:
        if not item.item:
            continue

        # Конвертуємо ціну в число, видаляючи пробіли
        price_str = str(item.item.price).replace(' ', '').replace(',', '.')
        price = float(price_str) if price_str else 0.0
        item_total = price * item.quantity
        # Сума з урахуванням знижки
        item_total_discounted = item_total * discount_multiplier

        total_amount += item_total_discounted
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
            'total': round(item_total_discounted, 2),
            'original_total': round(item_total, 2)
        }
        carts.append(cart_dict)

    return render_template('checkout.html', 
                         carts=carts, 
                         total_amount=round(total_amount, 2),
                         total_items=total_items,
                         user_id=user_id,
                         discount_multiplier=discount_multiplier,
                         discount_percent=discount_percent,
                         isFooter=False)

@main.route('/add_order', methods=['POST'])
@login_required
def add_order():
    """
    Створює замовлення з кошика дефолтного користувача
    """
    try:
        user_id = g.current_user.id
        
        # Отримуємо кошик користувача
        cart_items = CartItem.query.filter_by(user_id=user_id).all()
        
        if not cart_items or len(cart_items) == 0:
            return redirect(url_for('main.cart'))
        
        # Використовуємо множник знижки, що відповідає привілеям користувача
        discount = getattr(g.current_user, 'discount_multiplier', 1.0)

        # Створюємо замовлення з урахуванням знижки
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
@login_required
def order_success(order_id):
    """
    Сторінка успішного оформлення замовлення
    """
    order = Order.query.filter_by(id=order_id, user_id=g.current_user.id).first()
    if not order:
        abort(404)
    return render_template('order_success.html', order=order, isFooter=False)

# Реєстрація
@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nickname = request.form['name']
        email = request.form['email']
        password = request.form['password']
        password_confirm = request.form['confirm']

        # Перевірка паролів
        if password != password_confirm:
            flash("Паролі не співпадають!", "danger")
            return redirect(url_for('main.register'))

        # Перевірка на існуючий email
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Користувач з такою поштою вже існує!", "danger")
            return redirect(url_for('main.register'))

        # Створення нового користувача
        new_user = User(nickname=nickname, email=email)
        new_user.set_password(password)  # Хешуємо пароль перед збереженням
        db.session.add(new_user)
        db.session.commit()

        # Після успішної реєстрації, зберігаємо ID в сесії
        session.permanent = True
        session['user_id'] = new_user.id
        session['user_nickname'] = new_user.nickname
        session['user_status'] = new_user.status  # якщо статус є

        flash("Реєстрація успішна! Тепер ви можете увійти.", "success")
        return redirect(url_for('main.index'))  # Перенаправлення на головну сторінку

    return redirect(url_for('main.index'))

# Авторизація
@main.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("Користувача з такою поштою не знайдено", "danger")
        return redirect(url_for('main.index'))

    if not user.check_password(password):
        flash("Неправильний пароль", "danger")
        return redirect(url_for('main.index'))

    # Успішний вхід
    session.permanent = True
    session['user_id'] = user.id
    session['user_nickname'] = user.nickname
    session['user_status'] = user.status

    flash(f"Вітаю, {user.nickname}!", "success")
    return redirect(url_for('main.index'))


# Вихід
@main.route('/logout')
def logout():
    session.clear()  # Очищаємо сесію
    flash("Ви вийшли з системи", "info")
    return redirect(url_for('main.index'))  # Перенаправлення на головну сторінку
    
@main.route('/admin')
@privilege_required('Admin', 'Moder')
def admin():
    items = Desktop.query.all()   # список товарів
    news = News.query.all()       # список новин
    orders = Order.query.order_by(Order.id.desc()).all()                   # поки пусто
    users = User.query.all()      # список користувачів
    feedbacks = Feedback.query.options(joinedload(Feedback.user)).order_by(Feedback.id.desc()).all()
    return render_template(
        'admin.html',
        items=items,
        news=news,
        orders=orders,
        users=users,
        feedbacks=feedbacks,
        isFooter=False
    )

@main.route('/add_item', methods=['POST'])
def add_item():
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        price = float(data.get('price', 0))
        image_url = data.get('image')

        image_path = download_image(image_url)

        item = Desktop(name=name, description=description, price=price, image=image_path)
        db.session.add(item)
        db.session.commit()

        return jsonify(success=True)

    except Exception as e:
        db.session.rollback()
        print("Помилка при додаванні товару:", e)
        return jsonify(success=False, error=str(e))

@main.route('/get_item/<int:item_id>')
def get_item(item_id):
    item = Desktop.query.get_or_404(item_id)
    return jsonify(success=True, item={
        "name": item.name,
        "description": item.description,
        "price": item.price,
        "image": item.image
    })

@main.route('/edit_item/<int:item_id>', methods=['POST'])
def edit_item_post(item_id):
    try:
        data = request.get_json()
        item = Desktop.query.get_or_404(item_id)

        new_name = data.get('name')
        new_description = data.get('description')
        new_price = float(data.get('price', 0))
        new_image_url = data.get('image')

        item.name = new_name
        item.description = new_description
        item.price = new_price

        # Якщо URL змінено — качаємо нове зображення
        if new_image_url and new_image_url != item.image:
            try:
                new_image_path = download_image(new_image_url)
                item.image = new_image_path
            except Exception as img_err:
                print("Помилка при завантаженні нового зображення:", img_err)
                return jsonify(success=False, error="Не вдалося завантажити зображення")

        db.session.commit()
        return jsonify(success=True)

    except Exception as e:
        db.session.rollback()
        print("Помилка при редагуванні товару:", e)
        return jsonify(success=False, error=str(e))


@main.route('/delete_item/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    try:
        item = Desktop.query.get_or_404(item_id)

        db.session.delete(item)
        db.session.commit()

        return jsonify({"success": True}), 200

    except Exception as e:
        db.session.rollback()
        print("Помилка при видаленні:", e)
        return jsonify({"success": False, "error": str(e)}), 500


@main.route('/add_news', methods=['POST'])
def add_news():
    try:
        data = request.get_json()

        name = data.get('name')
        description = data.get('description')
        description_second = data.get('descriptionSecond')
        images = data.get('images', [])        # список URL

        news = News(
            name=name,
            description=description,
            descriptionSecond=description_second,
        )

        # Завантаження кожного зображення
        for url in images:
            img_path = download_image(url)
            news.images.append(NewsImage(img_url=img_path))

        db.session.add(news)
        db.session.commit()

        return jsonify(success=True)

    except Exception as e:
        db.session.rollback()
        print("Помилка при додаванні новини:", e)
        return jsonify(success=False, error=str(e))

@main.route('/get_news/<int:news_id>')
def get_news(news_id):
    news = News.query.get_or_404(news_id)
    return jsonify(success=True, news={
        "name": news.name,
        "description": news.description,
        "descriptionSecond": news.descriptionSecond,
        "images": [img.img_url for img in news.images]
    })

@main.route('/edit_news/<int:news_id>', methods=['POST'])
def edit_news_post(news_id):
    try:
        data = request.get_json()
        news = News.query.get_or_404(news_id)

        news.name = data.get('name')
        news.description = data.get('description')
        news.descriptionSecond = data.get('descriptionSecond')

        # Перезаписати список фото
        news.images.clear()
        for url in data.get('images', []):
            img_path = download_image(url)
            news.images.append(NewsImage(img_url=img_path))

        db.session.commit()
        return jsonify(success=True)

    except Exception as e:
        db.session.rollback()
        print("Помилка при редагуванні новини:", e)
        return jsonify(success=False, error=str(e))

@main.route('/delete_news/<int:news_id>', methods=['DELETE'])
def delete_news(news_id):
    try:
        news = News.query.get_or_404(news_id)
        db.session.delete(news)
        db.session.commit()

        return jsonify({"success": True}), 200

    except Exception as e:
        db.session.rollback()
        print("Помилка при видаленні:", e)
        return jsonify({"success": False, "error": str(e)}), 500

@main.route('/get_user/<int:user_id>')
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(success=True, user={
        "id": user.id,
        "nickname": user.nickname,
        "email": user.email,
        "status": user.status,
        "privilege": user.privilege
    })


@main.route('/get_user_orders_count/<int:user_id>')
def get_user_orders_count(user_id):
    try:
        # Ensure user exists
        user = User.query.get_or_404(user_id)
        cnt = Order.query.filter_by(user_id=user.id).count()
        return jsonify(success=True, count=cnt)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500


@main.route('/delete_user_force/<int:user_id>', methods=['DELETE'])
def delete_user_force(user_id):
    try:
        user = User.query.get_or_404(user_id)

        # Delete all orders belonging to this user first
        Order.query.filter_by(user_id=user.id).delete()

        # Now delete the user
        db.session.delete(user)
        db.session.commit()
        return jsonify(success=True)
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, error=str(e)), 500

@main.route('/edit_user/<int:user_id>', methods=['POST'])
def edit_user_post(user_id):
    try:
        data = request.get_json()
        user = User.query.get_or_404(user_id)

        user.nickname = data.get('nickname')
        user.email = data.get('email')
        user.status = data.get('status')
        user.privilege = data.get('privilege')

        if data.get('password'):
            user.set_password(data['password'])

        db.session.commit()
        return jsonify(success=True)

    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, error=str(e))

@main.route('/delete_user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user = User.query.get_or_404(user_id)

        # Якщо в цього користувача є замовлення, забороняємо видаляти
        existing_orders = Order.query.filter_by(user_id=user.id).count()
        if existing_orders > 0:
            return jsonify(success=False, error='Користувача неможливо видалити: є пов' + "яз" + 'ані замовлення.'), 400

        db.session.delete(user)
        db.session.commit()
        return jsonify(success=True)
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, error=str(e)), 500

@main.route('/get_order/<int:order_id>')
def get_order(order_id):
    order = Order.query.get_or_404(order_id)
    
    order_items = []
    for item in order.items:
        desktop = Desktop.query.get(item['item_id'])
        if not desktop:
            continue
        
        # Конвертуємо ціну в число
        price_str = str(desktop.price).replace(' ', '').replace(',', '.')
        try:
            price = float(price_str)
        except ValueError:
            price = 0.0
        
        count = item['quantity']
        discount = item['discount']
        total = round(price * count * discount, 2)

        order_items.append({
            "name": desktop.name,
            "count": count,
            "price": price,
            "sum": total
        })

    return jsonify(success=True, order={
        "id": order.id,
        "status": order.status,
        "total_sum": round(order.total_amount, 2),
        "user": {
            "id": order.user.id,
            "nickname": order.user.nickname,
            "email": order.user.email
        },
        "items": order_items
    })



@main.route('/update_order_status/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    try:
        data = request.get_json()
        new_status = data.get("status")

        order = Order.query.get_or_404(order_id)
        order.status = new_status

        db.session.commit()
        return jsonify(success=True)

    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, error=str(e))
    
@main.route('/delete_feedback/<int:feedback_id>', methods=['DELETE'])
def delete_feedback(feedback_id):
    try:
        fb = Feedback.query.get_or_404(feedback_id)
        db.session.delete(fb)
        db.session.commit()
        return jsonify(success=True)
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, error=str(e)), 500

def get_user_email_by_id(user_id):
    if not user_id:
        return None
    user = User.query.get(user_id)
    return user.email if user else None

def set_user_email_in_session(user_id):
    email = get_user_email_by_id(user_id)
    if email:
        session['user_email'] = email
    else:
        session.pop('user_email', None)
    return email

@main.route('/user_email/<int:user_id>')
def user_email_route(user_id):
    email = get_user_email_by_id(user_id)
    if email:
        return jsonify(success=True, email=email)
    return jsonify(success=False, error="User not found"), 404

@main.route('/api')
def api_template():
    """
    Сторінка замовлення
    """
    return render_template('api.html')
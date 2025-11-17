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


main = Blueprint('main', __name__)


def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not getattr(g, 'current_user', None):
            flash('Увійдіть, щоб продовжити.', 'warning')
            return redirect(url_for('main.index'))
        return view_func(*args, **kwargs)

    return wrapper


@main.before_app_request
def load_current_user():
    user_id = session.get('user_id')
    g.current_user = User.query.get(user_id) if user_id else None


@main.app_context_processor
def inject_current_user():
    return {'current_user': getattr(g, 'current_user', None)}

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/news')
def news():
    # --- ІНІЦІАЛІЗАЦІЯ ТІЛЬКИ ОДИН РАЗ ---
    #if not News.query.first():
    # --- seed_news_data()


    all_news = News.query.all()
    return render_template('news.html', news=all_news)

def seed_news_data():
    news_data = [
        News(
            name="Новинка: Гра “Стратегія 2025”",
            description="Випробуйте свої стратегічні навички у новій грі! \n Відкрийте для себе світ битв і дипломатії.",
            descriptionSecond=" Відкрийте для себе неймовірний світ “Стратегія 2025”! \n 🏰 Побудуйте власну імперію, використовуючи хитрість, стратегію та дипломатію 🤝. \n Кожна партія – нові виклики ⚔️ і можливість проявити свій стратегічний талант 🧠.",
            images=[
                NewsImage(img_url="images/news1.jpg"),
                NewsImage(img_url="images/news1-2.jpg"),
                NewsImage(img_url="images/news1-3.jpg"),
            ],
        ),
        News(
            name="Акція: -40% на популярні ігри",
            description="  Обмежений час! Знижки на топові \n настільні ігри цього тижня — поповніть колекцію за вигідною ціною.",
            descriptionSecond=" Поповніть колекцію настільних хітів зі знижкою 40% 🎉! \n “Catan”, “Ticket to Ride”, “Carcassonne” та інші стали ще доступнішими 🏷. \n Організовуйте вечори з друзями та сім’єю 👨‍👩‍👧‍👦. ",
            images=[
                NewsImage(img_url="images/news2.jpg"),
                NewsImage(img_url="images/news2-2.jpg"),
                NewsImage(img_url="images/news2-3.jpg"),
            ],
        ),
        News(
            name="Майстер-клас для гравців",
            description="Хочеш грати як професіонал? \n Приходь на наш безкоштовний майстер-клас і навчись новим тактикам!",
            descriptionSecond="Приходьте на живий майстер-клас 🎯. \n Отримайте поради від досвідчених геймерів, спробуйте нестандартні комбінації ходів 🔍 і відкрийте нові способи перемагати 🏆.",
            images=[
                NewsImage(img_url="images/news3.jpg"),
                NewsImage(img_url="images/news3-2.jpg"),
            ],
        ),
        News(
            name="Турнір з настільних ігор",
            description="Перевір свої стратегічні навички та виграй круті призи!",
            descriptionSecond="Щомісячний турнір для фанатів настільних ігор 🎲. \n Переможці отримають призи 🏆, сертифікати 📜 та бонуси 🎁.",
            images=[
                NewsImage(img_url="images/news4.jpg"),
                NewsImage(img_url="images/news4-2.jpg"),
            ],
        ),
        News(
            name="Нові настільні ігри у продажу",
            description="Нові пригоди та квести чекають на тебе!",
            descriptionSecond="Нові пригодницькі квести та кооперативні ігри вже чекають на тебе 🌟. \n Веселі вечори з друзями чи родиною 👨‍👩‍👧‍👦 гарантовані!",
            images=[
                NewsImage(img_url="images/news5.jpg"),
                NewsImage(img_url="images/news5-2.jpg"),
            ],
        ),
        News(
            name="Вечірка для геймерів",
            description="Приходь на тематичну вечірку та грай разом з іншими фанатами настільних ігор!",
            descriptionSecond="Приходь на тематичну вечірку у “Гральну Комору”! 🕹 \n Ігри, конкурси 🏆, призи 🎁 та весела компанія гарантовані 🤗. \n Випробуй свої навички в командних та індивідуальних турнірах ⚔️, отримай подарунки і нові знайомства 🤝.\n Це шанс провести час весело, активно та з користю 🎯, об’єднуючи геймерів у дружню спільноту!",
            images=[
                NewsImage(img_url="images/news6.jpg"),
                NewsImage(img_url="images/news6-2.jpg"),
                NewsImage(img_url="images/news6-3.jpg"),
            ],
        ),
    ]

    db.session.add_all(news_data)
    db.session.commit()
    print("✅ База новин заповнена.")


@main.route('/contacts')
def contacts():
    return render_template('contacts.html')

@main.route('/feedback')
def feedback():
    return render_template('feedback.html')


@main.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    try:
        # 1. Отримуємо JSON-дані, які надіслав JavaScript
        data = request.get_json()

        title = data.get('title')
        description = data.get('description')

        # 2. Валідація на стороні сервера (дуже важливо!)
        if not title or not description:
            # 'jsonify' створює JSON-відповідь, 400 - це код помилки "Bad Request"
            return jsonify({'success': False, 'error': 'Заголовок та опис є обов\'язковими.'}), 400

        if len(title) > 100 or len(description) > 300:
            return jsonify({'success': False, 'error': 'Перевищено ліміт символів.'}), 400

        # 3. Створюємо запис у БД
        new_feedback = Feedback(title=title, description=description)
        db.session.add(new_feedback)
        db.session.commit()

        # 4. Надсилаємо відповідь про успіх
        return jsonify({'success': True, 'message': 'Відгук додано!'}), 201

    except Exception as e:
        db.session.rollback()
        print(f"Помилка при збереженні відгуку: {e}")  # Логування помилки
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
    
    carts = carts if len(carts) != 0 else None
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
    error = None

    if not user:
        error = "Користувача з такою поштою не знайдено"
    elif not user.check_password(password):
        error = "Неправильний пароль"

    if error:
        # Передаємо помилку у шаблон
        return render_template("index.html", login_error=error, email=email)
    else:
        session.permanent = True
        session['user_id'] = user.id
        session['user_nickname'] = user.nickname
        session['user_status'] = user.status
        return redirect(url_for('main.index'))


# Вихід
@main.route('/logout')
def logout():
    session.clear()  # Очищаємо сесію
    flash("Ви вийшли з системи", "info")
    return redirect(url_for('main.index'))  # Перенаправлення на головну сторінку

@main.route("/test")
def test(): 
    print(session.get("user_id"))
    
@main.route('/admin')
def admin():
    items = Desktop.query.all()   # список товарів
    news = News.query.all()       # список новин
    orders = []                   # поки пусто
    users = []                    # поки пусто

    return render_template(
        'admin.html',
        items=items,
        news=news,
        orders=orders,
        users=users,
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

        item.name = data.get('name')
        item.description = data.get('description')
        item.price = float(data.get('price', 0))
        item.image = data.get('image')

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

@main.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    return f"Delete user {user_id} (ще не готово)"

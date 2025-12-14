from flask import Blueprint, render_template, jsonify, g, request, session, url_for
from functools import wraps
from app.models import cart
from app.models.user import User
from app.service.news_service import NewsService
from app.service.cart_service import CartService
from app.service.user_service import UserService
from app.service.desktop_service import DesktopService
from app.service.feedback_service import FeedbackService
from app.service.orders_service import OrdersService
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, current_user

api = Blueprint('api', __name__, url_prefix='/api/v1')
api_v2 = Blueprint('api_v2', __name__, url_prefix='/api/v2')

'''
@api.before_app_request
def load_current_user():
    user_id = session.get('user_id')
    g.current_user = UserService.get_user_by_id(user_id) if user_id else None
'''

def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = UserService.get_user_by_id(user_id)
        
        # Перевірка, чи юзер існує і чи він Адмін
        if not user or user.status != 'Admin':
            return jsonify(msg='Доступ заборонено! Тільки для адмінів!'), 403
            
        return fn(*args, **kwargs)
    return wrapper

'''
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.current_user:
            return jsonify({"message": "Неавторизований користувач"}), 401
        return f(*args, **kwargs)
    return decorated_function
''' 

# ==========================================
# ============== API VERSION 2 =============
# ==========================================

@api_v2.route("/", methods=["GET"])
def api_v2_index():
    """
    Статус API v2 (Health Check)
    ---
    tags:
      - General V2
    summary: Перевірка доступності версії API 2.0 (Beta)
    description: >
      Точка входу для нової версії API. 
      Використовується для моніторингу статусу та перевірки маршрутизації /api/v2/.
    responses:
        200:
            description: API V2 активне і працює стабільно
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: "Вітаємо в API версії 2.0!"
    """
    return jsonify({"message": "Вітаємо в API версії 2.0!"}), 200

@api_v2.route("/users", methods=["GET"])
def get_users_v2():
    """
    Оптимізований список користувачів (Lightweight)
    ---
    tags:
      - General V2
    summary: Отримати лише нікнейми користувачів
    description: >
      Експериментальний ендпоінт версії 2.0.
      На відміну від v1, повертає плоский список рядків (тільки нікнейми) замість повних об'єктів.
      Це зменшує обсяг переданих даних на 80% (корисно для мобільних мереж).
    responses:
        200:
            description: Успішне отримання списку
            schema:
              type: array
              items:
                type: string
              example: ["admin_cat", "lazy_max", "smart_sirozha", "padavan_dima"]
        500:
            description: Внутрішня помилка сервера
    """
    # У V2 ми вирішили повертати, наприклад, тільки імена, щоб економити трафік
    users = UserService.get_all_users()
    return jsonify([user.nickname for user in users]), 200

# ==========================================
# ============== API VERSION 1 =============
# ==========================================

# ----------------- Auth -----------------
@api.route("/auth/", methods=["POST"])
def autorize():
    """
    Авторизація користувача
    ---
    tags:
      - Auth
    summary: Вхід в систему та отримання JWT токена
    description: >
      Перевіряє логін та пароль користувача. Якщо дані вірні, повертає `access_token`, 
      який потрібно використовувати для доступу до захищених маршрутів.
    parameters:
      - in: body
        name: body
        required: true
        description: Облікові дані користувача
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: "cat"
              description: Нікнейм користувача
            password:
              type: string
              example: "123"
              description: Пароль користувача
    responses:
        200:
            description: Успішна авторизація
            schema:
              type: object
              properties:
                access_token:
                  type: string
                  description: JWT токен для авторизації (Bearer)
                message:
                  type: string
                  example: "Успішна авторизація"
        401:
            description: Помилка авторизації
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: "Невірні облікові дані"
    """
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    # Тут сервіс може повертати просто юзера, бо помилка одна - "невірні дані"
    user = UserService.authorize_user(username, password)
    
    if user:
        access_token = create_access_token(identity=str(user.id))
        return jsonify({"access_token": access_token, "message": "Успішна авторизація"}), 200
    else:
        return jsonify({"message": "Невірні облікові дані"}), 401

@api.route("/auth/forgot-password", methods=["POST"])
def forgot_password():
    """
    Запит на відновлення пароля
    ---
    tags:
      - Auth
    summary: Відправляє посилання для скидання пароля (поки що в консоль/відповідь)
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
          properties:
            email:
              type: string
              example: "cat@gmail.com"
    responses:
      200:
        description: Лист відправлено (або імітовано)
        schema:
          type: object
          properties:
            message:
              type: string
            debug_token:
              type: string
              description: Тільки для розробки! Видалити на проді.
      404:
        description: Email не знайдено
    """
    data = request.get_json()
    email = data.get("email")
    
    token, error = UserService.request_password_reset(email)
    
    if error:
        return jsonify({"message": error}), 404
        
    reset_link = request.host_url.rstrip('/') + url_for('main.reset_password_page', token=token)
    return jsonify({
        "message": "Посилання для скидання пароля відправлено на вашу електронну пошту.", 
        "reset_link": reset_link,
        "debug_token": token
    }), 200


@api.route("/auth/reset-password", methods=["POST"])
def reset_password():
    """
    Встановлення нового пароля
    ---
    tags:
      - Auth
    summary: Змінює пароль, використовуючи токен відновлення
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - token
            - new_password
            - confirm_password
          properties:
            token:
              type: string
              description: Токен, отриманий на попередньому кроці
            new_password:
              type: string
              description: Новий пароль
            confirm_password:
              type: string
    responses:
      200:
        description: Пароль успішно змінено
      400:
        description: Помилка (невірний токен або паролі)
    """
    data = request.get_json()
    token = data.get("token")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")
    
    if not token or not new_password:
        return jsonify({"message": "Відсутні дані"}), 400
        
    success, error = UserService.reset_password_with_token(token, new_password, confirm_password)
    
    if error:
        return jsonify({"message": error}), 400
        
    return jsonify({"message": "Пароль успішно змінено! Тепер ви можете увійти."}), 200

# ----------------- User -----------------
@api.route("/users/", methods=["GET"])
def get_users():
    """
    Отримати список усіх користувачів
    ---
    tags:
      - User
    summary: Повертає публічну інформацію про всіх користувачів
    responses:
        200:
            description: Список користувачів успішно отримано
            schema:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  nickname:
                    type: string
                  email:
                    type: string
                  status:
                    type: string
                  privilege:
                    type: string
                  discount_percent:
                    type: integer
        500:
            description: Внутрішня помилка сервера
    """ 
    users = UserService.get_all_users()
    users_list = []
    for user in users:
        users_list.append({
            "id": user.id,
            "nickname": user.nickname,
            "email": user.email,
            "status": user.status, 
            "privilege": user.privilege,
            "discount_percent": user.discount_percent
        })
    return jsonify(users_list), 200 

@api.route("/users/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id):
    """
    Отримати профіль користувача за ID
    ---
    tags:
      - User
    summary: Детальна інформація про конкретного користувача
    parameters:
      - name: user_id
        in: path
        required: true
        schema:
          type: integer
        description: Унікальний ID користувача
    responses:
        200:
            description: Користувача знайдено
            schema:
              type: object
              properties:
                id:
                  type: integer
                nickname:
                  type: string
                email:
                  type: string
                status:
                  type: string
        404:
            description: Користувача не знайдено
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: "Користувача не знайдено"
    security:
      - Bearer: []
    """ 
    user = UserService.get_user_by_id(user_id)
    if user:
        return jsonify({
            "id": user.id,
            "nickname": user.nickname,
            "email": user.email,
            "status": user.status
        }), 200
    else:
        return jsonify({"message": "Користувача не знайдено"}), 404
    

@api.route("/register/", methods=["POST"])
def registration():
    """
    Реєстрація нового користувача
    ---
    tags:
      - User
    summary: Створення нового акаунту
    description: >
      Реєструє нового користувача. Вимагає унікальний email та нікнейм.
      Паролі повинні співпадати.
    parameters:
      - in: body
        name: body
        required: true
        description: Дані для реєстрації
        schema:
          type: object
          required:
            - nickname
            - email
            - password
            - password_confirm
          properties:
            nickname:
              type: string
              description: Бажаний нікнейм (унікальний)
            email: 
              type: string
              format: email
              description: Електронна пошта (унікальна)
            password:
              type: string
              description: Пароль
            password_confirm:
              type: string
              description: Підтвердження паролю
    responses:
        200:
            description: Успішна реєстрація
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: "Успішна реєстрація"
        400:
            description: Помилка валідації або конфлікт даних
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: "Паролі не співпадають"
    """ 
    data = request.get_json()
    nickname = data.get("nickname")
    email = data.get("email")
    password = data.get("password")
    password_confirm = data.get("password_confirm")
    
    # Оновлений виклик сервісу (повертає user, error)
    user, error_message = UserService.registration(nickname, email, password, password_confirm)
    
    if error_message:
        # Повертаємо конкретну помилку (400 Bad Request)
        return jsonify({"message": error_message}), 400
        
    return jsonify({"message": "Успішна реєстрація"}), 200

@api.route("/user/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    """
    Видалити користувача (Тільки Адмін)
    ---
    tags:
      - User
    summary: Видалення користувача за його ID
    parameters:
      - name: user_id 
        in: path
        required: true
        schema:
          type: integer
        description: ID користувача для видалення
    responses:
        200:
            description: Успішне видалення
        403:
            description: Доступ заборонено (не адмін)
        404:
            description: Користувача не знайдено
    security:
      - Bearer: []
    """
    # Тут можна залишити як є, або теж переробити сервіс на повернення (bool, msg)
    success = UserService.delete_user(user_id)
    if success:
        return jsonify({"message": "Користувач успішно видалений"}), 200
    else:
        return jsonify({"message": "Користувача не знайдено"}), 404 
    

@api.route("/user/<int:user_id>", methods=["PATCH"])
@admin_required
def edit_user(user_id):
    """
    Редагувати дані користувача (Тільки Адмін)
    ---
    tags:
      - User
    summary: Оновлення інформації про користувача
    parameters:
      - name: user_id
        in: path
        required: true
        schema:
          type: integer
        description: ID користувача
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            nickname:
              type: string
            email: 
              type: string
            status:
              type: string
              enum: [User, Admin, Moder]
            privilege:
              type: string
              enum: [Default, Gold, Diamond, VIP]
            password:
              type: string
    responses:
        200:
            description: Інформація успішно оновлена
            schema:
              type: object
              properties:
                message:
                  type: string
                data:
                  type: object
                  description: Оновлений об'єкт користувача
        400:
            description: Помилка валідації (наприклад, нікнейм зайнятий)
        403:
            description: Доступ заборонено
        404:
            description: Користувача не знайдено
    security:
      - Bearer: []
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"message": "Немає даних для оновлення"}), 400

    # Викликаємо оновлений метод сервісу
    user, error_message = UserService.edit_user(
        user_id, 
        data.get("nickname"), 
        data.get("email"), 
        data.get("status"), 
        data.get("privilege"), 
        data.get("password")
    )
    
    if error_message:
        # Визначаємо код помилки: якщо "не знайдено" -> 404, інакше -> 400
        status_code = 404 if "не знайдено" in error_message.lower() else 400
        return jsonify({"message": error_message}), status_code
        
    return jsonify({"message": "Інформація про користувача успішно оновлена", "data": user.to_dict()}), 200
    
# ----------------- News -----------------
@api.route("/news", methods=['GET'])
def api_get_news():
    """
    Отримати список всіх новин
    ---
    tags:
      - News
    responses:
      200:
        description: Список новин успішно отримано
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              name:
                type: string
              description:
                type: string
              descriptionSecond:
                type: string
              images:
                type: array
                items:
                  type: string
    """
    news_items = NewsService.fetch_all_news()
    return jsonify(news_items), 200


@api.route("/news/<int:news_id>", methods=['GET'])
def api_get_news_by_id(news_id):
    """
    Отримати одну новину за ID
    ---
    tags:
      - News
    parameters:
      - name: news_id
        in: path
        required: true
        type: integer
        description: ID новини
    responses:
      200:
        description: Новина знайдена
      404:
        description: Новина не знайдена
    """
    news_item = NewsService.fetch_news_by_id(news_id)
    if not news_item:
        return jsonify({"message": "Новину не знайдено"}), 404
    return jsonify(news_item), 200


@api.route("/news/<int:news_id>", methods=['DELETE'])
@admin_required
def api_delete_news_by_id(news_id):
    """
    Видалити новину (Тільки Адмін)
    ---
    tags:
      - News
    parameters:
      - name: news_id
        in: path
        required: true
        type: integer
    responses:
      200:
        description: Новина успішно видалена
      404:
        description: Новина не знайдена
    security:
      - Bearer: []
    """
    success = NewsService.remove_news_by_id(news_id)
    if not success:
        return jsonify({"message": "Новину не знайдено або помилка видалення"}), 404
    return jsonify({"message": "Новину успішно видалено"}), 200

@api.route("/news/<int:news_id>", methods=['PATCH'])
@admin_required
def api_edit_news(news_id):
    """
    Редагувати новину (Тільки Адмін)
    ---
    tags:
      - News
    parameters:
      - name: news_id
        in: path
        required: true
        type: integer
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            description:
              type: string
            descriptionSecond:
              type: string
            image_urls:
              type: array
              items:
                type: string
    responses:
      200:
        description: Новина успішно оновлена
      400:
        description: Помилка оновлення
      404:
        description: Новина не знайдена
    security:
      - Bearer: []
    """
    data = request.get_json()
    
    updated_news, error = NewsService.update_news(
        news_id,
        name=data.get("name"),
        description=data.get("description"),
        descriptionSecond=data.get("descriptionSecond"),
        image_urls=data.get("image_urls", [])
    )
    
    if error:
        status_code = 404 if "не знайдено" in error else 400
        return jsonify({"message": error}), status_code
        
    # Тут ми вручну формуємо відповідь, бо to_dict може не бути в моделі News (або він повертає об'єкт)
    return jsonify({"message": "Новина успішно оновлена"}), 200


@api.route("/news", methods=['POST'])
@admin_required
def api_add_news():
    """
    Додати новину (Тільки Адмін)
    ---
    tags:
      - News
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - description
          properties:
            name:
              type: string
            description:
              type: string
            descriptionSecond:
              type: string
            image_urls:
              type: array
              items:
                type: string
    responses:
      201:
        description: Новина успішно додана
      400:
        description: Помилка додавання
    security:
      - Bearer: []
    """
    data = request.get_json()
    
    news, error = NewsService.create_news(
        name=data.get("name"),
        description=data.get("description"),
        descriptionSecond=data.get("descriptionSecond"),
        image_urls=data.get("image_urls", [])
    )
    
    if error:
        return jsonify({"message": error}), 400
        
    return jsonify({"message": "Новина створена", "id": news.id}), 201

# ----------------- Cart -----------------
@api.route("/cart", methods=["GET"])
@jwt_required()
def get_cart():
    """
    Отримати власний кошик (Детальні дані)
    ---
    tags:
      - Cart
    summary: Отримує деталізований список товарів (з ціною, назвою, тощо) у кошику поточного автентифікованого користувача.
    description: >
      Використовує ID користувача з JWT-токена. Завжди повертає повну інформацію про товари, включаючи їх назви та ціни.
    responses:
      200:
        description: Повертає деталізований список позицій кошика.
        schema:
          type: array
          items:
            type: object
            properties:
              item_id:
                type: integer
                format: int64
                description: Ідентифікатор товару.
              quantity:
                type: integer
                format: int32
                description: Кількість цього товару в кошику.
              name:
                type: string
                description: Назва товару.
              price:
                type: number
                format: float
                description: Ціна за одиницю товару.
              # ... інші деталі товару ...
      401:
        description: Користувач не авторизований.
        schema:
          type: object
          properties:
            error:
              type: string
              example: Користувач не авторизований
    security:
      - Bearer: []  
    """
    # Ми перевірили, що токен існує за допомогою @jwt_required(), але логіка все одно залишається:
    user_id = get_jwt_identity()
    
    # Викликаємо сервіс, який тепер повертає деталізовані дані
    cart_details = CartService.get_cart(user_id) 
    return jsonify(cart_details)

@api.route("/cart/<int:user_id>", methods=["GET"])
@admin_required # <-- Додано обов'язковий декоратор для безпеки
def get_cart_for_user(user_id):
    """
    Отримати детальний кошик для заданого користувача по ID
    ---
    tags:
      - Cart
    summary: Отримує деталізований список товарів у кошику вказаного користувача. Доступно лише адміністраторам.
    description: >
      Використовується адміністратором для перегляду кошика будь-якого користувача за його ID.
      Повертає повну інформацію про товари (детальний кошик).
    parameters:
      - in: path
        name: user_id
        required: true
        schema:
          type: integer
        description: ID користувача, детальний кошик якого потрібно отримати.
    responses:
      200:
        description: Повертає деталізований список позицій кошика.
        schema:
          type: array
          items:
            type: object
            properties:
              item_id:
                type: integer
                format: int64
                description: Ідентифікатор товару.
              quantity:
                type: integer
                format: int32
                description: Кількість цього товару в кошику.
              name:
                type: string
                description: Назва товару.
              price:
                type: number
                format: float
                description: Ціна за одиницю товару.
      401:
        description: Користувач не авторизований.
        schema:
          type: object
          properties:
            error:
              type: string
              example: Missing Authorization Header
      403:
        description: Доступ заборонено (Користувач не є адміністратором).
        schema:
          type: object
          properties:
            error:
              type: string
              example: Admin privileges required
    security:
      - Bearer: []
    """
    # Викликаємо сервіс, який тепер повертає деталізовані дані
    cart_details = CartService.get_cart(user_id) 
    return jsonify(cart_details)

@api.route("/cart", methods=["POST"])
@admin_required
def add_to_cart():
    """
    Додати товар до кошика
    ---
    tags:
      - Cart
    summary: Додає товар до кошика автентифікованого або вказаного користувача.
    description: >
      Якщо user_id передано в тілі запиту, товар додається до кошика цього користувача (потрібні права адміністратора). 
      Якщо user_id не передано, товар додається до кошика користувача, визначеного за JWT токеном (поточний автентифікований користувач).
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            user_id:
              type: integer
              format: int64
              description: >
                НЕОБОВ'ЯЗКОВЕ ПОЛЕ. Ідентифікатор користувача. 
                Використовується, якщо потрібно додати товар до кошика іншого користувача (зазвичай вимагає прав адміністратора). 
                Якщо не вказано, використовується ID автентифікованого користувача з токена.
            item_id:
              type: integer
              format: int64
              description: Ідентифікатор товару, який додається.
              required: true
            quantity:
              type: integer
              format: int32
              description: Кількість товару.
              default: 1
              required: true
          # Явно вказуємо, які поля є обов'язковими. user_id тут відсутній.
          required:
            - item_id
            - quantity
    responses:
      200:
        description: Успішно додано товар в кошик. Повертає деталі нової позиції кошика.
        schema:
          type: object
          properties:
            id:
              type: integer
            item_id:
              type: integer
            quantity:
              type: integer
            user_id:
              type: integer
      400:
        description: Недійсні дані або відсутність обов'язкових полів (item_id або quantity).
      401:
        description: Користувач не авторизований (відсутній JWT токен).
      403:
        description: Доступ заборонено (наприклад, якщо користувач без прав адміністратора намагається передати чужий user_id).
    security:
      - Bearer: []
    """
    data = request.get_json()
    if data.get("user_id") is None:
        user_id = get_jwt_identity()
    else:
        user_id = data.get("user_id")
    cart_item = CartService.add_item_to_cart(user_id=user_id, item_id=data.get("item_id"), quantity=data.get("quantity"))
    # Перетворюємо в dict, щоб Flask міг відправити JSON
    return jsonify({
        "id": cart_item.id,
        "item_id": cart_item.item_id,
        "quantity": cart_item.quantity,
        "user_id": cart_item.user_id
    })
    
@api.route("/cart", methods=["DELETE"])
@jwt_required()
def remove_from_cart():
    data = request.get_json()
    item_id = data.get("item_id")

    if item_id is None:
        return jsonify({"error": "Поле 'item_id' є обов'язковим."}), 400

    try:
        item_id = int(item_id)
    except ValueError:
        return jsonify({"error": "item_id має бути цілим числом."}), 400

    # user_id з JWT
    user_id = get_jwt_identity()
    if user_id is None:
        return jsonify({"error": "Користувач не авторизований."}), 401

    was_removed = CartService.remove_item_from_cart(user_id=user_id, item_id=item_id)

    if was_removed:
        return jsonify({"message": "Товар успішно видалено з кошика."}), 200
    else:
        return jsonify({"error": f"Товар з ID {item_id} не знайдено у вашому кошику."}), 404


@api.route("/cart/clear", methods=["DELETE"])
@jwt_required()
def clear_cart_endpoint():
    """
    Очистити весь кошик
    ---
    tags:
      - Cart
    summary: Повністю видаляє всі товари з кошика поточного автентифікованого користувача.
    description: Операція не вимагає тіла запиту, оскільки ідентифікатор користувача береться з JWT токена.
    parameters:
      # Параметри тіла запиту відсутні
      # - in: header
      #   name: Authorization
      #   required: true
      #   type: string
      #   description: Bearer Token
      []
    responses:
      200:
        description: Кошик користувача успішно очищено.
        schema:
          type: object
          properties:
            message:
              type: string
              example: Ваш кошик успішно очищено.
      401:
        description: Користувач не авторизований (відсутній або недійсний JWT токен).
    security:
      - Bearer: []
    """
    # 1. Отримання ID користувача з токена
    current_user_id = get_jwt_identity()
    
    # 2. Виклик сервісної функції
    # Припускаємо, що CartService - це клас, який містить clear_cart
    try:
        CartService.clear_cart(user_id=current_user_id)
        
        # 3. Успішна відповідь
        return jsonify({
            "message": "Ваш кошик успішно очищено.", 
            "user_id": current_user_id
        }), 200
        
    except Exception as e:
        # Обробка можливих помилок бази даних або сервісу
        print(f"Помилка при очищенні кошика користувача {current_user_id}: {e}")
        return jsonify({"error": "Не вдалося очистити кошик через внутрішню помилку сервера."}), 500

@api.route("/cart/quantity", methods=["PUT"])
@jwt_required()
def update_cart_item_quantity():
    """
    Оновити кількість товару в кошику
    ---
    tags:
      - Cart
    summary: Оновлює кількість конкретного товару в кошику поточного користувача.
    description: >
      Використовується для зміни кількості товару (item_id) у кошику користувача, 
      ідентифікатор якого береться з JWT-токена.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            item_id:
              type: integer
              format: int64
              description: Ідентифікатор товару, кількість якого потрібно змінити.
              required: true
            quantity:
              type: integer
              format: int32
              description: Нова кількість товару. Має бути > 0.
              required: true
          required:
            - item_id
            - quantity
    responses:
      200:
        description: Кількість товару успішно оновлено.
        schema:
          type: object
          properties:
            message:
              type: string
              example: Кількість товару успішно оновлено.
            item_id:
              type: integer
            quantity:
              type: integer
      400:
        description: Недійсні дані (наприклад, quantity < 1) або відсутність обов'язкових полів.
      401:
        description: Користувач не авторизований.
      404:
        description: Товар не знайдено в кошику користувача.
    security:
      - Bearer: []
    """
    data = request.get_json()

    # 1. Отримання ID користувача з токена
    current_user_id = get_jwt_identity()

    # 2. Отримання даних з тіла запиту
    item_id = data.get("item_id")
    quantity = data.get("quantity")
    
    # 3. Валідація вхідних даних
    if item_id is None or quantity is None:
        return jsonify({"error": "Поля 'item_id' та 'quantity' є обов'язковими."}), 400
        
    try:
        item_id = int(item_id)
        quantity = int(quantity)
    except ValueError:
        return jsonify({"error": "ID товару та кількість мають бути цілими числами."}), 400

    if quantity <= 0:
        # Якщо кількість <= 0, краще використати DELETE-запит, але для PUT-запиту це помилка
        return jsonify({"error": "Кількість повинна бути більше нуля. Для видалення використовуйте DELETE."}), 400

    # 4. Виклик сервісної функції
    # Припускаємо, що CartService - це клас, який містить update_item_quantity
    was_updated = CartService.update_item_quantity(
        user_id=current_user_id, 
        item_id=item_id, 
        quantity=quantity
    )

    # 5. Обробка результату
    if was_updated:
        return jsonify({
            "message": "Кількість товару успішно оновлено.", 
            "item_id": item_id, 
            "quantity": quantity
        }), 200
    else:
        # Якщо товар не знайдено в кошику
        return jsonify({"error": f"Товар з ID {item_id} не знайдено у вашому кошику."}), 404
    
####################################################
#################### DESKTOPS ######################
####################################################

@api.route("/desktops", methods=["GET"])
def get_all_desktops():
    """
    Отримати список всіх настолок
    ---
    tags:
      - Desktops
    summary: Публічний список усіх товарів
    responses:
      200:
        description: Список успішно отримано
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              name:
                type: string
              price:
                type: number
              image:
                type: string
    """
    # Сервіс повертає вже готовий список словників (завдяки rules)
    desktops = DesktopService.get_all_desktops_service()
    return jsonify(desktops), 200


@api.route("/desktops/<int:desktop_id>", methods=["GET"])
def get_desktop_by_id(desktop_id):
    """
    Отримати деталі однієї настолки
    ---
    tags:
      - Desktops
    parameters:
      - name: desktop_id
        in: path
        required: true
        type: integer
    responses:
      200:
        description: Знайдено
        schema:
          type: object
          properties:
            id:
              type: integer
            name:
              type: string
            description:
              type: string
            price:
              type: number
      404:
        description: Не знайдено
    """
    # Зверни увагу: я прибрав @jwt_required(), бо перегляд товарів зазвичай публічний
    desktop, error = DesktopService.get_desktop_details_service(desktop_id)
    
    if error:
        return jsonify({"message": error}), 404
        
    return jsonify(desktop.to_dict()), 200


@api.route("/desktops", methods=["POST"])
@admin_required
def add_desktop():
    """
    Додати настолку (Тільки Адмін)
    ---
    tags:
      - Desktops
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - price
          properties:
            name:
              type: string
            price:
              type: number
            description:
              type: string
            image:
              type: string
    responses:
      201:
        description: Створено успішно
      400:
        description: Помилка валідації
    security:
      - Bearer: []
    """
    data = request.get_json()
    
    new_desktop, error = DesktopService.create_desktop_service(data)
    
    if error:
        return jsonify({"message": error}), 400
        
    return jsonify(new_desktop.to_dict()), 201

@api.route("/desktops/<int:desktop_id>", methods=["PATCH"])
@admin_required
def edit_desktop_by_id(desktop_id):
    """
    Редагувати настолку (Тільки Адмін)
    ---
    tags:
      - Desktops
    parameters:
      - name: desktop_id
        in: path
        required: true
        type: integer
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            price:
              type: number
            description:
              type: string
            image:
              type: string
    responses:
      200:
        description: Оновлено успішно
      404:
        description: Не знайдено
    security:
      - Bearer: []
    """
    data = request.get_json()
    
    updated_desktop, error = DesktopService.update_desktop_service(desktop_id, data)
    
    if error:
        status_code = 404 if "not found" in error else 400
        return jsonify({"message": error}), status_code

    return jsonify(updated_desktop.to_dict()), 200

@api.route("/desktops/<int:desktop_id>", methods=["DELETE"])
@admin_required
def delete_desktop_by_id(desktop_id):
    """
    Видалити настолку (Тільки Адмін)
    ---
    tags:
      - Desktops
    parameters:
      - name: desktop_id
        in: path
        required: true
        type: integer
    responses:
      200:
        description: Видалено
      404:
        description: Не знайдено
    security:
      - Bearer: []
    """
    success, message = DesktopService.delete_desktop_service(desktop_id)
    
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"message": message}), 404


####################################################
#################### FEEDBACKS ######################
####################################################

@api.route("/feedbacks", methods=["GET"])
def get_all_feedbacks():
    """
    Отримати список всіх відгуків
    ---
    tags:
      - Feedbacks
    responses:
      200:
        description: Список успішно отримано
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              title:
                type: string
              description:
                type: string
              user_id:
                type: integer
    """
    feedbacks = FeedbackService.get_all_feedbacks_service()
    # Конвертуємо список об'єктів у список словників
    return jsonify([f.to_dict() for f in feedbacks]), 200


@api.route("/feedbacks/<int:feedback_id>", methods=["GET"])
def get_feedback_by_id(feedback_id):
    """
    Отримати один відгук по ID
    ---
    tags:
      - Feedbacks
    parameters:
      - name: feedback_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Знайдено
      404:
        description: Не знайдено
    """
    feedback, error = FeedbackService.get_feedback_by_id_service(feedback_id)
    
    if error:
        return jsonify({"message": error}), 404
        
    return jsonify(feedback.to_dict()), 200


@api.route("/feedbacks", methods=["POST"])
@jwt_required()
def add_feedback():
    """
    Залишити відгук (Авторизація)
    ---
    tags:
      - Feedbacks
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - title
            - description
          properties:
            title:
              type: string
            description:
              type: string
    responses:
      201:
        description: Відгук створено
      400:
        description: Помилка валідації
    security:
      - Bearer: []
    """
    data = request.get_json()
    
    # 👇 ФІКС: Беремо ID з токена, а не з current_user
    user_id = get_jwt_identity() 
    
    new_feedback, error = FeedbackService.create_feedback_service(data, user_id)
    
    if error:
        return jsonify({"message": error}), 400
        
    return jsonify(new_feedback.to_dict()), 201

@api.route("/feedbacks/user/<int:user_id>", methods=["POST"])
@admin_required
def add_feedback_by_user(user_id):
    """
    Залишити відгук (Тільки Адмін)
    ---
    tags:
      - Feedbacks
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID користувача, від імені якого створюється відгук
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - title
            - description
          properties:
            title:
              type: string
            description:
              type: string
    responses:
      201:
        description: Відгук створено
      400:
        description: Помилка валідації
    security:
      - Bearer: []
    """
    data = request.get_json()
    
    new_feedback, error = FeedbackService.create_feedback_service(data, user_id)
    
    if error:
        return jsonify({"message": error}), 400
        
    return jsonify(new_feedback.to_dict()), 201

@api.route("/feedbacks/<int:feedback_id>", methods=["PATCH"])
@jwt_required()
def edit_feedback_by_id(feedback_id):
    """
    Редагувати свій відгук
    ---
    tags:
      - Feedbacks
    parameters:
      - name: feedback_id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            title:
              type: string
            description:
              type: string
    responses:
      200:
        description: Оновлено
      404:
        description: Не знайдено
    security:
      - Bearer: []
    """
    data = request.get_json()
    
    # Тут в ідеалі треба перевірити, чи user_id з токена співпадає з автором відгуку
    # Але поки лишимо так для спрощення
    
    updated_feedback, error = FeedbackService.update_feedback_service(feedback_id, data)
    
    if error:
        status_code = 404 if "не знайдено" in error else 400
        return jsonify({"message": error}), status_code

    return jsonify(updated_feedback.to_dict()), 200


@api.route("/feedbacks/<int:feedback_id>", methods=["DELETE"])
@admin_required # Видаляти краще тільки адміну (або автору, але це складніше)
def delete_feedback_by_id(feedback_id):
    """
    Видалити відгук (Тільки Адмін)
    ---
    tags:
      - Feedbacks
    parameters:
      - name: feedback_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Видалено
      404:
        description: Не знайдено
    security:
      - Bearer: []
    """
    success, message = FeedbackService.delete_feedback_service(feedback_id)
    
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"message": message}), 404
          

# ----------------- Orders -----------------
@api.route("/orders/", methods=["GET"])
@admin_required # Це точно має бачити тільки адмін
def get_all_orders():
    """
    Отримати список усіх замовлень (Тільки Адмін)
    ---
    tags:
      - Orders
    responses:
        200:
            description: Список замовлень
    security:
      - Bearer: []
    """
    orders = OrdersService.get_all_orders()
    return jsonify(orders), 200

@api.route("/orders/my", methods=["GET"]) # Змінив URL, щоб не плутатись з ID
@jwt_required()
def get_my_orders():
    """
    Отримати історію своїх замовлень
    ---
    tags:
      - Orders
    responses:
        200:
            description: Список замовлень користувача
        404:
            description: Замовлень не знайдено
    security:
      - Bearer: []
    """
    user_id = get_jwt_identity()
    orders = OrdersService.get_orders(user_id)
    
    # Повертаємо пустий список, якщо нічого немає (це краще ніж 404 для списків)
    return jsonify(orders), 200
    
@api.route("/orders", methods=["POST"]) # RESTful: POST /orders
@jwt_required()
def add_order():
    """
    Створити замовлення з кошика
    ---
    tags:
      - Orders
    summary: Створює замовлення з товарів у кошику поточного користувача
    responses:
        201:
            description: Замовлення успішно створено
        400:
            description: Помилка (пустий кошик тощо)
    security:
      - Bearer: []
    """
    user_id = get_jwt_identity()
    
    order, error_message = OrdersService.add_order(user_id)
    
    if error_message:
        return jsonify({"message": error_message}), 400
        
    return jsonify({
        "message": "Замовлення успішно створено",
        "data": order.to_dict()
    }), 201
    
@api.route("/orders/<int:order_id>", methods=["PATCH"])
@admin_required
def update_order_status(order_id):
    """
    Оновити статус замовлення (Тільки Адмін)
    ---
    tags:
      - Orders
    parameters:
      - name: order_id
        in: path 
        required: true
        type: integer
        description: ID замовлення
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - status
          properties:
            status:
              type: string
              enum: [In process, Completed, Shipped, Cancelled]
    responses:
        200:
            description: Статус оновлено
        404:
            description: Замовлення не знайдено
    security:
      - Bearer: []
    """ 
    data = request.get_json()
    new_status = data.get("status")
    
    order, error_message = OrdersService.edit_status_order(order_id, new_status)
    
    if error_message:
        status_code = 404 if "не знайдено" in error_message else 400
        return jsonify({"message": error_message}), status_code
        
    return jsonify({"message": "Статус оновлено", "data": order.to_dict()}), 200
    
@api.route("/orders/<int:order_id>", methods=["DELETE"])
@admin_required
def delete_order(order_id):
    """
    Видалити замовлення (Тільки Адмін)
    ---
    tags:
      - Orders
    parameters:
      - name: order_id 
        in: path
        required: true
        type: integer
    responses:
        200:
            description: Видалено
        404:
            description: Не знайдено
    security:
      - Bearer: []
    """
    result = OrdersService.delete_order(order_id)

    if result:
        return jsonify({"message": "Замовлення успішно видалено"}), 200
    else:
        return jsonify({"message": "Замовлення не знайдено"}), 404
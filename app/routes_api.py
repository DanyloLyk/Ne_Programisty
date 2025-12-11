from flask import Blueprint, render_template, jsonify, g, request, session
from functools import wraps
from app.models import cart
from app.models.user import User
from app.service.news_service import NewsService
from app.service.cart_service import CartService
from app.service.user_service import UserService
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, current_user

api = Blueprint('api', __name__, url_prefix='/api/v1')


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

# ----------------- Auth -----------------
@api.route("/auth/", methods=["POST"])
def autorize():
    """
    Авторизація користувача
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            password:
              type: string
    responses:
        200:
            description: Успішна авторизація
        401:
            description: Невірні облікові дані
    """
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    user = UserService.authorize_user(username, password)
    if user:
        access_token = create_access_token(identity=str(user.id))
        return jsonify({"access_token": access_token, "message": "Успішна авторизація"}), 200
    else:
        return jsonify({"message": "Невірні облікові дані"}), 401

# ----------------- User -----------------
@api.route("/users/", methods=["GET"])
def get_users():
    """
    Отримати список усіх користувачів
    ---
    tags:
      - User
    responses:
        200:
            description: Список користувачів
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
    Отримати інформацію про користувача за його ID
    ---
    tags:
      - User
    parameters:
      - name: user_id
        in: path
        required: true
        schema:
          type: integer
        description: ID користувача
    responses:
        200:
            description: Інформація про користувача
        404:
            description: Користувача не знайдено
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
    Реєстрація користувача
    ---
    tags:
      - User
    parameters:
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
            password:
              type: string
            password_confirm:
              type: string
    responses:
        200:
            description: Успішна реєстрація
        400:
            description: Помилка реєстрації
    """ 

    data = request.get_json()
    nickname = data.get("nickname")
    email = data.get("email")
    password = data.get("password")
    password_confirm = data.get("password_confirm")
    
    user = UserService.registration(nickname, email, password, password_confirm)
    if user:
        return jsonify({"message": "Успішна реєстрація"}), 200
    else:
        return jsonify({"message": "Помилка реєстрації"}), 400

@api.route("/delete_user/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    """
    Видалити користувача за його ID
    ---
    tags:
      - User
    parameters:
      - name: user_id 
        in: path
        required: true
        schema:
          type: integer
        description: ID користувача
    responses:
        200:
            description: Користувач успішно видалений
        404:
            description: Користувача не знайдено
    security:
      - Bearer: []
    """
    success = UserService.delete_user(user_id)
    if success:
        return jsonify({"message": "Користувач успішно видалений"}), 200
    else:
        return jsonify({"message": "Користувача не знайдено"}), 404 
    

@api.route("/edit_user/<int:user_id>", methods=["PUT"])
@admin_required
def edit_user(user_id):
    """
    Редагувати інформацію про користувача
    ---
    tags:
      - User
    parameters:
      - in: path
        name: user_id
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
            privilege:
              type: string
            password:
              type: string
    responses:
        200:
            description: Інформація про користувача успішно оновлена
        400:
            description: Помилка оновлення інформації про користувача
    security:
      - Bearer: []
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"message": "Немає даних для оновлення"}), 400

    nickname = data.get("nickname") 
    email = data.get("email")
    status = data.get("status")
    privilege = data.get("privilege")
    password = data.get("password")
    user = UserService.get_user_by_id(user_id)
    success = UserService.edit_user(user_id, nickname, email, status, privilege, password)
    if success:
        return jsonify({"message": "Інформація про користувача успішно оновлена", "data": user.to_dict()}), 200
    else:
        return jsonify({"message": "Помилка оновлення інформації про користувача"}), 400
    
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
        description: Список новин
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 1
              name:
                type: string
                example: "Назва новини"
              description:
                type: string
                example: "Опис новини"
              descriptionSecond:
                type: string
                example: "Детальний опис"
              images:
                type: array
                items:
                  type: string
                  example: "https://example.com/image.jpg"
      """
    news_items = NewsService.fetch_all_news()
    return jsonify(news_items)


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
        schema:
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
        return jsonify({"error": "News item not found"}), 404
    return jsonify(news_item)


@api.route("/news_delete/<int:news_id>", methods=['DELETE'])
@admin_required
def api_delete_news_by_id(news_id):
    """
    Видалити новину за ID
    ---
    tags:
      - News
    parameters:
      - name: news_id
        in: path
        required: true
        schema:
          type: integer
        description: ID новини
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
        return jsonify({"error": "News item not found"}), 404
    return jsonify({"message": "News item deleted successfully"})

@api.route("/news_edit/<int:news_id>", methods=['PUT'])
@admin_required
def api_edit_news(news_id):
    """
    Редагувати новину за ID
    ---
    tags:
      - News
    parameters:
      - name: news_id
        in: path
        required: true
        schema:
          type: integer
        description: ID новини
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
      404:
        description: Новина не знайдена
    security:
      - Bearer: []
    """
    data = request.get_json()
    news_item = NewsService.update_news(
        news_id,
        name=data.get("name"),
        description=data.get("description"),
        descriptionSecond=data.get("descriptionSecond"),
        image_urls=data.get("image_urls", [])
    )
    if not news_item:
        return jsonify({"error": "Новину не знайдено"}), 404
    return jsonify({"message": "Новина успішно оновлено"}), 200


@api.route("/news_add", methods=['POST'])
@admin_required
def api_add_news():
    """
    Додати новину
    ---
    tags:
      - News
    parameters:
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
        description: Новина успішно додана
      400:
        description: Помилка додавання новини
    security:
      - Bearer: []
    """
    news=NewsService.create_news(
        name=request.json.get("name"),
        description=request.json.get("description"),
        descriptionSecond=request.json.get("descriptionSecond"),
        image_urls=request.json.get("image_urls", [])
    )
    return jsonify(created=news.id), 200

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
      Якщо `user_id` передано в тілі запиту, товар додається до кошика цього користувача (потрібні права адміністратора). 
      Якщо `user_id` **не** передано, товар додається до кошика користувача, визначеного за JWT токеном (поточний автентифікований користувач).
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
                **НЕОБОВ'ЯЗКОВЕ ПОЛЕ.** Ідентифікатор користувача. 
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
        description: Доступ заборонено (наприклад, якщо користувач без прав адміністратора намагається передати чужий `user_id`).
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
@admin_required
def remove_from_cart():
    """
    Видалити товар з кошика користувача
    ---
    tags:
      - Cart
    summary: Видаляє вказаний товар з кошика користувача. Доступно лише адміністраторам.
    description: >
      Використовується для видалення однієї позиції товару з кошика вказаного користувача.
      Обов'язково вимагає `user_id` та `item_id` у тілі запиту.
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
              description: Ідентифікатор користувача, з кошика якого потрібно видалити товар.
              required: true
            item_id:
              type: integer
              format: int64
              description: Ідентифікатор товару, який потрібно видалити.
              required: true
          required:
            - user_id
            - item_id
    responses:
      200:
        description: Товар успішно видалено з кошика.
        schema:
          type: object
          properties:
            message:
              type: string
              example: Товар успішно видалено з кошика.
      400:
        description: Недійсні дані або відсутність обов'язкових полів.
      401:
        description: Користувач не авторизований.
      403:
        description: Доступ заборонено (Користувач не є адміністратором).
      404:
        description: Товар не знайдено в кошику вказаного користувача.
    security:
      - Bearer: []
    """
    data = request.get_json()

    # 1. Перевірка обов'язкових полів
    user_id = data.get("user_id")
    item_id = data.get("item_id")
    
    if user_id is None or item_id is None:
        return jsonify({"error": "Поля 'user_id' та 'item_id' є обов'язковими."}), 400
    
    # 2. Виклик сервісної функції
    # Припускаємо, що CartService - це клас, який містить remove_item_from_cart
    try:
        user_id = int(user_id)
        item_id = int(item_id)
    except ValueError:
        return jsonify({"error": "ID користувача та товару мають бути цілими числами."}), 400
        
    was_removed = CartService.remove_item_from_cart(user_id=user_id, item_id=item_id)

    # 3. Обробка результату
    if was_removed:
        return jsonify({"message": "Товар успішно видалено з кошика.", "user_id": user_id, "item_id": item_id}), 200
    else:
        # Якщо товар не знайдено, повертаємо 404
        return jsonify({"error": f"Товар з ID {item_id} не знайдено в кошику користувача з ID {user_id}."}), 404

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
        return jsonify({"error": f"Товар з ID {item_id} не знайдено у вашому кошику."}),

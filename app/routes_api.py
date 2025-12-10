from flask import Blueprint, render_template, jsonify, g, request, session
from functools import wraps
from app.models import cart
from app.models.user import User
from app.service.news_service import NewsService
from app.service.cart_service import CartService
from app.service.user_service import UserService

api = Blueprint('api', __name__, url_prefix='/api/v1')


@api.before_app_request
def load_current_user():
    user_id = session.get('user_id')
    g.current_user = UserService.get_user_by_id(user_id) if user_id else None
    
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.current_user:
            return jsonify({"message": "Неавторизований користувач"}), 401
        return f(*args, **kwargs)
    return decorated_function
    
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
        session['user_id'] = user.id
        return jsonify({"message": "Успішна авторизація"}), 200
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
            "status": user.status
        })
    return jsonify(users_list), 200 

@api.route("/users/<int:user_id>", methods=["GET"])
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
@login_required
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
    """
    success = UserService.delete_user(user_id)
    if success:
        return jsonify({"message": "Користувач успішно видалений"}), 200
    else:
        return jsonify({"message": "Користувача не знайдено"}), 404 
    

@api.route("/edit_user/<int:user_id>", methods=["PUT"])
@login_required
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


@api.route("/news/<int:news_id>", methods=['DELETE'])
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
    """
    success = NewsService.remove_news_by_id(news_id)
    if not success:
        return jsonify({"error": "News item not found"}), 404
    return jsonify({"message": "News item deleted successfully"})

@api.route("/news/<int:news_id>", methods=['PUT'])
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


@api.route("/news", methods=['POST'])
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
@login_required
def get_cart():
    """
    Отримати корзину
    ---
    tags:
      - Cart
    responses:
      200:
        description: Повертає кошик користувача
      401:
        description: Користувач не авторизований
    """
    if not g.current_user:
        return jsonify({"error": "User not logged in"}), 401

    user_id = g.current_user.id
    cart_details = CartService.get_cart(user_id)
    return jsonify(cart_details)

@api.route("/cart/add", methods=["POST"])
@login_required
def add_to_cart():
    """
    Додати товар до корзини
    ---
    tags:
      - Cart
    parameters:
      - in: body
        name: body
        required: true
        schema:
          item_id:
            type: integer
        quantity:
            type: integer
    responses:
      200:
        description: Додає item_id в кошик current_user
    """
    data = request.get_json()
    cart_item = CartService.add_item_to_cart(user_id=g.current_user.id, item_id=data.get("item_id"), quantity=data.get("quantity"))
    # Перетворюємо в dict, щоб Flask міг відправити JSON
    return jsonify({
        "id": cart_item.id,
        "item_id": cart_item.item_id,
        "quantity": cart_item.quantity,
        "user_id": cart_item.user_id
    })


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
    
# ----------------- User -----------------
@api.route("/auth/", methods=["POST"])
def autorize():
    """
    Авторизація користувача
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


@api.route("/news", methods=['POST'])
def api_add_news():
    """
    Додати новину
    ---
    tags:
      - News
    parameters:
      - name: body
        in: body
    """
    user_id = g.current_user.id  # Припускаємо, що ідентифікатор користувача доступний через g.current_user
    cart_details = CartService.get_cart(user_id)
    return jsonify(cart_details)

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

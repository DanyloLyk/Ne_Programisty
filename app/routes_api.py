from flask import Blueprint, jsonify, g, request, session
from app.service.news_service import NewsService
from app.service.cart_service import CartService
from app.models.user import User

api = Blueprint('api', __name__, url_prefix='/api/v1')


@api.before_app_request
def load_current_user():
    user_id = session.get('user_id')
    g.current_user = User.query.get(user_id) if user_id else None


# ----------------- Cart -----------------
@api.route("/cart", methods=["GET"])
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
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: "Нова новина"
            description:
              type: string
              example: "Короткий опис"
            descriptionSecond:
              type: string
              example: "Детальний опис новини"
            image_urls:
              type: array
              items:
                type: string
              example: ["https://example.com/image1.jpg", "https://example.com/image2.jpg"]
    responses:
      201:
        description: Новина успішно створена
      400:
        description: Некоректні дані
    """
    data = request.json
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    name = data.get('name')
    description = data.get('description')
    descriptionSecond = data.get('descriptionSecond')
    image_urls = data.get('image_urls', [])

    new_news = NewsService.create_news(name, description, descriptionSecond, image_urls)

    return jsonify({
        "id": new_news.id,
        "name": new_news.name,
        "description": new_news.description,
        "descriptionSecond": new_news.descriptionSecond,
        "images": [img.img_url for img in new_news.images]
    }), 201

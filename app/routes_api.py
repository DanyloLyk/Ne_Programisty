from flask import Blueprint, render_template, jsonify, g, request, session
from app.models.user import User
from app.service.news_service import NewsService
from app.service.cart_service import CartService

api = Blueprint('api', __name__, url_prefix='/api/v1')

@api.before_app_request
def load_current_user():
    user_id = session.get('user_id')
    g.current_user = User.query.get(user_id) if user_id else None

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
    """
    print(g.current_user.id)
    user_id = g.current_user.id  # Припускаємо, що ідентифікатор користувача доступний через g.current_user
    cart_details = CartService.get_cart(user_id)
    return jsonify(cart_details)
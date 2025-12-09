from flask import render_template, jsonify, g, request
from app.service.news_service import NewsService
from app.service.cart_service import CartService
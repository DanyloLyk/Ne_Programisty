from datetime import timedelta
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/images')
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

    app.secret_key = 'a3f6d7e8b9d4c2f1e0b76b7885d0a741'  # Важливо для роботи сесій

    db.init_app(app)
    migrate.init_app(app, db)

    # Імпортуємо всі моделі перед створенням таблиць
    from app.models.desktop import Desktop
    from app.models.cart import CartItem
    from app.models.order import Order
    from app.models.news import News
    from app.models.user import User

    from app.routes import main
    app.register_blueprint(main)
    with app.app_context():
        db.create_all()

    return app

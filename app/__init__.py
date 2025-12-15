from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import os
from dotenv import load_dotenv

# Завантажуємо змінні з .env
load_dotenv()

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name=None):
    """
    Factory function для створення Flask додатку.
    Якщо config_name='testing', підключає тестову конфігурацію.
    """
    app = Flask(__name__, instance_relative_config=True)

    # Конфігурація через клас у config.py
    if config_name == "testing":
        app.config.from_object("config.TestingConfig")
    else:
        app.config.from_object("config.ProductionConfig")

    # DATABASE_PATH із .env або дефолт
    default_db_path = os.path.join(app.instance_path, "mydatabase.db")
    db_path = os.environ.get("DATABASE_PATH", default_db_path)

    if not db_path.startswith("sqlite"):
        if os.path.isabs(db_path):
            app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
        else:
            app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = db_path

    # Створюємо папку для бази, якщо її нема
    try:
        db_dir = os.path.dirname(db_path)
        os.makedirs(db_dir, exist_ok=True)
        print(f"📁 Database directory ready: {db_dir}")
    except OSError as e:
        print(f"❌ Error creating directory {db_dir}: {e}")

    # Основні налаштування
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static/images")
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev_secret_key")
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "dev_jwt_key")
    app.json.sort_keys = False

    # Swagger налаштування
    from flasgger import Swagger

    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Ne Programisty Shop API",
            "description": "Документація для найкращого магазину настільних ігор.",
            "version": "1.0.0"
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: 'Bearer {token}'"
            }
        }
    }

    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec_v1",
                "route": "/apispec_v1.json",
                "rule_filter": lambda rule: rule.rule.startswith("/api/v1"),
                "model_filter": lambda tag: True,
            },
            {
                "endpoint": "apispec_v2",
                "route": "/apispec_v2.json",
                "rule_filter": lambda rule: rule.rule.startswith("/api/v2"),
                "model_filter": lambda tag: True,
            },
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/",
    }

    Swagger(app, config=swagger_config, template=swagger_template)

    # Ініціалізація Flask-розширень
    db.init_app(app)
    migrate.init_app(app, db)
    JWTManager(app)

    # Імпортуємо моделі
    from .models.desktop import Desktop
    from .models.cart import CartItem
    from .models.order import Order
    from .models.news import News
    from .models.feedback import Feedback
    from .models.user import User

    # Імпортуємо blueprint-и
    from .routes import main
    from .routes_api import api, api_v2

    app.register_blueprint(main)
    app.register_blueprint(api)
    app.register_blueprint(api_v2)

    # Створюємо базу та сидимо дані
    with app.app_context():
        db.create_all()
        from app.seed_data import seed_data
        seed_data(db)

    return app


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
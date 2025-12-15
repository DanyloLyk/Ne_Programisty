from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import os
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    # instance_relative_config=True каже Flask'у, що конфіги можуть бути в папці instance
    app = Flask(__name__, instance_relative_config=True) 
    default_db_path = os.path.join(app.instance_path, 'mydatabase.db')    
    db_path = os.environ.get('DATABASE_PATH', default_db_path)
    
    if not db_path.startswith('sqlite'):
        if os.path.isabs(db_path):
            app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        else:
            app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = db_path

    try:
        db_dir = os.path.dirname(db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            print(f"📁 Created database directory: {db_dir}") # Для дебагу в логах
    except OSError as e:
        print(f"❌ Error creating directory {db_dir}: {e}")

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/images')
    app.config['JWT_SECRET_KEY'] = '7ca594aa165516b25042703fbc5f3f16'
    app.config['SECRET_KEY'] = 'your_secret_key_here'
    app.json.sort_keys = False
    app.config['SWAGGER'] = {
        'title': 'My API',
        'uiversion': 3,
        'sort_keys': False,
        # 'openapi': '3.0.2'  # якщо хочеш OpenAPI 3
    }
    
    jwt = JWTManager(app)
    db.init_app(app)
    migrate.init_app(app, db)

    from .models.desktop import Desktop
    from .models.cart import CartItem
    from .models.order import Order
    from .models.news import News
    from .models.feedback import Feedback
    from .models.user import User

    from .routes import main
    app.register_blueprint(main)
    
    from .routes_api import api, api_v2
    # Реєструємо blueprint з API
    app.register_blueprint(api)
    app.register_blueprint(api_v2)

    from flasgger import Swagger
    
    swagger_config = {
        'title': 'My API',
        'uiversion': 3,
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec_v1',
                "route": '/apispec_v1.json',
                "rule_filter": lambda rule: rule.rule.startswith("/api/v1"),  # 🔥 Фільтруємо тільки V1
                "model_filter": lambda tag: True,  # Включаємо всі моделі
                "title": "API V1 (Production)",
                "description": "Основна стабільна версія API для магазину.",
                "version": "1.0.0"
            },
            {
                "endpoint": 'apispec_v2',
                "route": '/apispec_v2.json',
                "rule_filter": lambda rule: rule.rule.startswith("/api/v2"),  # 🔥 Фільтруємо тільки V2
                "model_filter": lambda tag: True,
                "title": "API V2 (Beta)",
                "description": "Нова версія API. Знаходиться в розробці.",
                "version": "2.0.0"
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/",
        'securityDefinitions': {
            'Bearer': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header',
                'description': "Введіть: Bearer <ваш_токен>"
            }
        },
        'security': [{'Bearer': []}]
    }

    template = {
        "swagger": "2.0",
        "info": {
            "title": "Ne Programisty Shop API",
            "description": "Документація для найкращого магазину настільних ігор.",
            "contact": {
                "responsibleOrganization": "Ne Programisty Team",
                "responsibleDeveloper": "Danylo (Team Lead)",
                "email": "danylo@example.com",
            },
            "version": "1.0.0"
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: \"Bearer {token}\""
            }
        },
    }

    Swagger(app, config=swagger_config, template=template)


    with app.app_context():
        db.create_all()
        from app.seed_data import seed_data
        seed_data(db)

    return app


if __name__ == "__main__":
    app = create_app()
    print("-" * 50)
    print("🚀 САЙТ ПРАЦЮЄ ТУТ: http://127.0.0.1")
    print("-" * 50)
    app.run(host="0.0.0.0", port=5000, debug=True)
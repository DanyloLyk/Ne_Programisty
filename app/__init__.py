from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import os
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/images')
    app.config['JWT_SECRET_KEY'] = '7ca594aa165516b25042703fbc5f3f16'
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
    
    from .routes_api import api as api_bp
    # Реєструємо blueprint з API
    app.register_blueprint(api_bp)
    
    from flasgger import Swagger
    
    swagger_config = {
        'title': 'My API',
        'uiversion': 3,
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec_1',
                "route": '/apispec_1.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
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

    Swagger(app, config=swagger_config)


    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
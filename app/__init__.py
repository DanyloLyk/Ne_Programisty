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
    app.config['SECRET_KEY'] = 'your_secret_key_here'
    app.config['SWAGGER'] = {
        'title': 'My API',
        'uiversion': 3,
        # 'openapi': '3.0.2'  # якщо хочеш OpenAPI 3
    }

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
    Swagger(app)


    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
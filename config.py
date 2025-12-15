import os
from pathlib import Path
from dotenv import load_dotenv

# Завантажуємо .env файл
load_dotenv()

# Базова директорія проєкту
BASE_DIR = Path(__file__).resolve().parent.parent

class BaseConfig:
    """Базові налаштування для будь-якого середовища"""
    SECRET_KEY = os.environ.get("SECRET_KEY", "default_secret_key")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "default_jwt_key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app/static/images")
    SWAGGER = {
        'title': 'My API',
        'uiversion': 3,
        'sort_keys': False
    }

class ProductionConfig(BaseConfig):
    """Налаштування для продакшн середовища"""
    DATABASE_PATH = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "instance/mydatabase.db"))
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_PATH}"
    DEBUG = False
    TESTING = False

class TestingConfig(BaseConfig):
    """Налаштування для тестів"""
    # Використовуємо in-memory SQLite для швидких тестів
    DATABASE_PATH = os.environ.get("DATABASE_PATH", ":memory:")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_PATH}"
    DEBUG = True
    TESTING = True
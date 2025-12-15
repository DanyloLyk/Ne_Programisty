import pytest
from app import create_app
from unittest.mock import MagicMock
from app.models.cart import CartItem

@pytest.fixture(scope="session")
def app():
    """Створює Flask додаток для тестів."""
    app = create_app()
    return app

@pytest.fixture
def app_context(app):
    """Контекст додатку для тестів, де потрібна база даних."""
    with app.app_context():
        yield

# Fixtures для mock об'єктів
@pytest.fixture
def mock_cart_item():
    """Повертає mock CartItem з item"""
    item_mock = MagicMock()
    item_mock.id = 1
    item_mock.name = "Тестовий товар"
    item_mock.description = "Опис товару"
    item_mock.price = "100"
    item_mock.image = "image.png"

    cart_item = MagicMock(spec=CartItem)
    cart_item.id = 10
    cart_item.user_id = 1
    cart_item.item_id = 1
    cart_item.quantity = 2
    cart_item.item = item_mock

    return cart_item

@pytest.fixture
def mock_cart_item_no_item():
    """CartItem без item (item=None)"""
    cart_item = MagicMock(spec=CartItem)
    cart_item.id = 11
    cart_item.user_id = 1
    cart_item.item_id = 2
    cart_item.quantity = 1
    cart_item.item = None
    return cart_item

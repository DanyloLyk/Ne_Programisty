import pytest
from app import create_app
from unittest.mock import MagicMock
from app.models.cart import CartItem
from app.models.user import User
from app.models.desktop import Desktop
from app.models.feedback import Feedback
from app.models.news import News, NewsImage
from app.models.order import Order

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

# ===============================================
# CART FIXTURES
# ===============================================

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

# ===============================================
# USER FIXTURES
# ===============================================

@pytest.fixture
def mock_user():
    """Mock користувача з базовим статусом"""
    user = MagicMock(spec=User)
    user.id = 1
    user.nickname = "testuser"
    user.email = "test@example.com"
    user.status = "User"
    user.privilege = "Default"
    user.check_password = MagicMock(return_value=True)
    return user

@pytest.fixture
def mock_admin_user():
    """Mock адміністратора"""
    user = MagicMock(spec=User)
    user.id = 2
    user.nickname = "admin"
    user.email = "admin@example.com"
    user.status = "Admin"
    user.privilege = "VIP"
    user.check_password = MagicMock(return_value=True)
    return user

# ===============================================
# DESKTOP FIXTURES
# ===============================================

@pytest.fixture
def mock_desktop():
    """Mock товару"""
    desktop = MagicMock(spec=Desktop)
    desktop.id = 1
    desktop.name = "Game 1"
    desktop.description = "Опис ігри"
    desktop.price = 500.0
    desktop.image = "game1.png"
    return desktop

@pytest.fixture
def mock_desktop_list():
    """Mock список товарів"""
    desktop1 = MagicMock(spec=Desktop)
    desktop1.id = 1
    desktop1.name = "Game 1"
    desktop1.description = "Опис 1"
    desktop1.price = 500.0
    desktop1.image = "game1.png"
    
    desktop2 = MagicMock(spec=Desktop)
    desktop2.id = 2
    desktop2.name = "Game 2"
    desktop2.description = "Опис 2"
    desktop2.price = 700.0
    desktop2.image = "game2.png"
    
    return [desktop1, desktop2]

# ===============================================
# FEEDBACK FIXTURES
# ===============================================

@pytest.fixture
def mock_feedback():
    """Mock відгуку"""
    feedback = MagicMock(spec=Feedback)
    feedback.id = 1
    feedback.title = "Чудовий товар!"
    feedback.description = "Дуже задоволений покупкою"
    feedback.user_id = 1
    feedback.created_at = "2024-12-01"
    return feedback

@pytest.fixture
def mock_feedback_list():
    """Mock список відгуків"""
    feedback1 = MagicMock(spec=Feedback)
    feedback1.id = 1
    feedback1.title = "Відгук 1"
    feedback1.description = "Опис 1"
    feedback1.user_id = 1
    
    feedback2 = MagicMock(spec=Feedback)
    feedback2.id = 2
    feedback2.title = "Відгук 2"
    feedback2.description = "Опис 2"
    feedback2.user_id = 2
    
    return [feedback1, feedback2]

# ===============================================
# NEWS FIXTURES
# ===============================================

@pytest.fixture
def mock_news():
    """Mock новини"""
    news = MagicMock(spec=News)
    news.id = 1
    news.name = "Нова гра вийшла"
    news.description = "Опис новини"
    news.descriptionSecond = "Деталі"
    news.images = []
    return news

@pytest.fixture
def mock_news_with_images():
    """Mock новини з зображеннями"""
    image1 = MagicMock(spec=NewsImage)
    image1.img_url = "news1.png"
    
    image2 = MagicMock(spec=NewsImage)
    image2.img_url = "news2.png"
    
    news = MagicMock(spec=News)
    news.id = 1
    news.name = "Нова гра"
    news.description = "Опис"
    news.descriptionSecond = "Деталі"
    news.images = [image1, image2]
    
    return news

# ===============================================
# ORDER FIXTURES
# ===============================================

@pytest.fixture
def mock_order():
    """Mock замовлення"""
    user_mock = MagicMock()
    user_mock.id = 1
    user_mock.nickname = "testuser"
    user_mock.email = "test@example.com"
    
    order = MagicMock(spec=Order)
    order.id = 1
    order.user_id = 1
    order.status = "In process"
    order.total_sum = 1000.0
    order.user = user_mock
    order.items = []
    
    return order

@pytest.fixture
def mock_order_shipped():
    """Mock замовлення зі статусом Shipped"""
    user_mock = MagicMock()
    user_mock.id = 1
    user_mock.nickname = "testuser"
    user_mock.email = "test@example.com"
    
    order = MagicMock(spec=Order)
    order.id = 2
    order.user_id = 1
    order.status = "Shipped"
    order.total_sum = 1500.0
    order.user = user_mock
    order.items = []
    
    return order

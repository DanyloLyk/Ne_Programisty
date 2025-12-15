import pytest
from app.models.cart import CartItem
from app.models.desktop import Desktop
from app.domain.cart_rules import get_cart_items_for_user, get_item_in_cart
from app import db
from app.service.cart_service import CartService

@pytest.fixture
def test_item(session):
    """Створює тестовий товар у базі"""
    item = Desktop(name="Тестовий десктоп", description="Опис тестового товару", price=1000, image="img.png")
    session.add(item)
    session.commit()
    return item

@pytest.fixture
def test_cart_item(session, test_item):
    """Створює CartItem для користувача"""
    cart_item = CartItem(user_id=1, item_id=test_item.id, quantity=2)
    session.add(cart_item)
    session.commit()
    return cart_item

def test_get_cart_returns_correct_details(session, test_cart_item):
    """Тестує get_cart: повертає деталі кошика з total"""
    result = CartService.get_cart(user_id=1)
    assert isinstance(result, dict)
    assert result['items'][0]['item_details']['name'] == "Тестовий десктоп"
    assert result['total'] == 2000  # 1000 * 2

def test_add_item_to_cart_new_item(session, test_item):
    """Додає новий товар у кошик"""
    cart_item = CartService.add_item_to_cart(user_id=2, item_id=test_item.id, quantity=3)
    assert cart_item.quantity == 3
    # Перевіряємо базу
    db_item = get_item_in_cart(user_id=2, item_id=test_item.id)
    assert db_item.quantity == 3

def test_add_item_to_cart_existing_item(session, test_cart_item):
    """Додає кількість до існуючого товару"""
    CartService.add_item_to_cart(user_id=1, item_id=test_cart_item.item_id, quantity=1)
    updated_item = get_item_in_cart(user_id=1, item_id=test_cart_item.item_id)
    assert updated_item.quantity == 3  # 2 + 1

def test_remove_item_from_cart(session, test_cart_item):
    """Видаляє товар з кошика"""
    result = CartService.remove_item_from_cart(user_id=1, item_id=test_cart_item.item_id)
    assert result is True
    assert get_item_in_cart(user_id=1, item_id=test_cart_item.item_id) is None

def test_clear_cart(session, test_cart_item):
    """Очищає кошик користувача"""
    CartService.clear_cart(user_id=1)
    assert get_cart_items_for_user(user_id=1) is None

def test_update_item_quantity(session, test_cart_item):
    """Оновлює кількість товару у кошику"""
    result = CartService.update_item_quantity(user_id=1, item_id=test_cart_item.item_id, quantity=5)
    assert result is True
    updated_item = get_item_in_cart(user_id=1, item_id=test_cart_item.item_id)
    assert updated_item.quantity == 5

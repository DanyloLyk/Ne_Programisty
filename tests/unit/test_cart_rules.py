import pytest
from unittest.mock import patch
from app.domain import cart_rules

# ==============================
# Тести для cart_rules
# ==============================

def test_get_cart_items_for_user_returns_items(mock_cart_item, app_context):
    """
    Тестує get_cart_items_for_user, коли є товари в кошику.

    Очікується, що функція поверне список з деталями товарів.
    Given: Існує CartItem з пов'язаним Item
    When: Викликається get_cart_items_for_user
    Then: Повертається список з деталями товарів
    Results:
    - Перевіряється, що повернутий список не порожній
    - Перевіряється, що деталі товару правильні
    - Перевіряється правильність обчислення total_price
    """
    with patch("app.domain.cart_rules.CartItem.query") as mock_query:
        mock_query.filter_by.return_value.all.return_value = [mock_cart_item]
        result = cart_rules.get_cart_items_for_user(user_id=1)
        assert result is not None
        assert isinstance(result, list)
        assert result[0]['item_details']['name'] == "Тестовий товар"
        assert result[0]['item_details']['total_price'] == 200  # 100*2

def test_get_cart_items_for_user_empty(app_context):
    """
    Тестує get_cart_items_for_user, коли кошик порожній.

    Очікується, що функція поверне None.
    Given: Немає CartItem для користувача
    When: Викликається get_cart_items_for_user
    Then: Повертається None
    Results:
    - Перевіряється, що повернене значення є None
    """
    with patch("app.domain.cart_rules.CartItem.query") as mock_query:
        mock_query.filter_by.return_value.all.return_value = []
        result = cart_rules.get_cart_items_for_user(user_id=99)
        assert result is None

def test_get_cart_items_for_user_item_none(mock_cart_item_no_item, app_context):
    """
    Тестує get_cart_items_for_user, коли CartItem має item=None

    Очікується, що деталі товару будуть None.
    Given: Існує CartItem з item=None
    When: Викликається get_cart_items_for_user
    Then: Деталі товару будуть None
    Results:
    - Перевіряється, що item_details є None
    """
    with patch("app.domain.cart_rules.CartItem.query") as mock_query:
        mock_query.filter_by.return_value.all.return_value = [mock_cart_item_no_item]
        result = cart_rules.get_cart_items_for_user(user_id=1)
        assert result[0]['item_details'] is None

def test_get_item_in_cart_found(mock_cart_item, app_context):
    """
    Тестує get_item_in_cart, коли товар знайдено.

    Очікується, що функція поверне відповідний CartItem.
    Given: Існує CartItem для користувача та товару
    When: Викликається get_item_in_cart
    Then: Повертається відповідний CartItem
    Results:
    - Перевіряється, що повернений об'єкт є тим самим CartItem
    """
    with patch("app.domain.cart_rules.CartItem.query") as mock_query:
        mock_query.filter_by.return_value.first.return_value = mock_cart_item
        result = cart_rules.get_item_in_cart(user_id=1, item_id=1)
        assert result == mock_cart_item

def test_get_item_in_cart_not_found(app_context):
    """
    Тестує get_item_in_cart, коли товар не знайдено.

    Очікується, що функція поверне None.
    Given: Немає CartItem для користувача та товару
    When: Викликається get_item_in_cart
    Then: Повертається None
    Results:
    - Перевіряється, що повернене значення є None
    """
    with patch("app.domain.cart_rules.CartItem.query") as mock_query:
        mock_query.filter_by.return_value.first.return_value = None
        result = cart_rules.get_item_in_cart(user_id=1, item_id=999)
        assert result is None
import pytest
from unittest.mock import patch, MagicMock
from app.domain import order_rules

# ==============================
# Тести для order_rules
# ==============================

def test_get_all_orders_returns_list(mock_order, app_context):
    """
    Тестує get_all_orders, коли є замовлення в базі.

    Очікується, що функція поверне список словників замовлень.
    Given: Існує замовлення в базі
    When: Викликається get_all_orders
    Then: Повертається список замовлень
    Results:
    - Перевіряється, що список не порожній
    - Перевіряються дані замовлення
    """
    with patch("app.domain.order_rules.Order.query") as mock_query:
        mock_order.to_dict = MagicMock(return_value={
            "id": 1,
            "user_id": 1,
            "status": "In process",
            "total_sum": 1000.0
        })
        mock_query.options.return_value.order_by.return_value.all.return_value = [mock_order]
        result = order_rules.get_all_orders()
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["id"] == 1

def test_get_all_orders_empty(app_context):
    """
    Тестує get_all_orders, коли замовлень немає.

    Очікується, що функція поверне порожній список.
    Given: Немає замовлень в базі
    When: Викликається get_all_orders
    Then: Повертається порожній список
    Results:
    - Перевіряється, що список є порожнім
    """
    with patch("app.domain.order_rules.Order.query") as mock_query:
        mock_query.options.return_value.order_by.return_value.all.return_value = []
        result = order_rules.get_all_orders()
        assert result == []

def test_get_order_by_id_found(mock_order, app_context):
    """
    Тестує get_order_by_id, коли замовлення знайдено.

    Очікується, що функція поверне замовлення.
    Given: Існує замовлення з ID 1
    When: Викликається get_order_by_id(1)
    Then: Повертається замовлення
    Results:
    - Перевіряється, що повернене замовлення має правильний ID
    - Перевіряються дані замовлення
    """
    with patch("app.domain.order_rules.Order.query") as mock_query:
        mock_query.get.return_value = mock_order
        result = order_rules.get_order_by_id(1)
        assert result is not None
        assert result.id == 1
        assert result.status == "In process"

def test_get_order_by_id_not_found(app_context):
    """
    Тестує get_order_by_id, коли замовлення не знайдено.

    Очікується, що функція поверне None.
    Given: Замовлення з ID 999 не існує
    When: Викликається get_order_by_id(999)
    Then: Повертається None
    Results:
    - Перевіряється, що повернене значення є None
    """
    with patch("app.domain.order_rules.Order.query") as mock_query:
        mock_query.get.return_value = None
        result = order_rules.get_order_by_id(999)
        assert result is None

def test_get_user_orders_found(mock_order, app_context):
    """
    Тестує get_user_orders, коли користувач має замовлення.

    Очікується, що функція поверне список замовлень.
    Given: Користувач з ID 1 має замовлення
    When: Викликається get_user_orders(1)
    Then: Повертається список замовлень
    Results:
    - Перевіряється, що список не порожній
    - Перевіряються дані замовлення
    """
    with patch("app.domain.order_rules.Order.query") as mock_query:
        mock_query.filter_by.return_value.all.return_value = [mock_order]
        result = order_rules.get_user_orders(1)
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].user_id == 1

def test_get_user_orders_empty(app_context):
    """
    Тестує get_user_orders, коли користувач не має замовлень.

    Очікується, що функція поверне порожній список.
    Given: Користувач не має замовлень
    When: Викликається get_user_orders
    Then: Повертається порожній список
    Results:
    - Перевіряється, що список є порожнім
    """
    with patch("app.domain.order_rules.Order.query") as mock_query:
        mock_query.filter_by.return_value.all.return_value = []
        result = order_rules.get_user_orders(999)
        assert result == []

def test_get_user_orders_exception(app_context):
    """
    Тестує get_user_orders при помилці бази даних.

    Очікується, що функція поверне порожній список.
    Given: База даних кидає помилку
    When: Викликається get_user_orders
    Then: Повертається порожній список
    Results:
    - Перевіряється обробка помилки
    """
    with patch("app.domain.order_rules.Order.query") as mock_query:
        mock_query.filter_by.side_effect = Exception("DB Error")
        result = order_rules.get_user_orders(1)
        assert result == []

def test_delete_order_by_id_success(mock_order, app_context):
    """
    Тестує delete_order_by_id для успішного видалення.

    Очікується, що замовлення буде видалено.
    Given: Замовлення існує
    When: Викликається delete_order_by_id
    Then: Замовлення видалено
    Results:
    - Перевіряється, що функція повертає True
    """
    with patch("app.domain.order_rules.Order.query") as mock_query, \
         patch("app.domain.order_rules.db.session") as mock_session:
        
        mock_query.get.return_value = mock_order
        mock_session.delete = MagicMock()
        mock_session.commit = MagicMock()
        
        result = order_rules.delete_order_by_id(1)
        assert result is True

def test_delete_order_by_id_not_found(app_context):
    """
    Тестує delete_order_by_id, коли замовлення не знайдено.

    Очікується, що функція поверне False.
    Given: Замовлення не існує
    When: Викликається delete_order_by_id
    Then: Повертається False
    Results:
    - Перевіряється, що функція повертає False
    """
    with patch("app.domain.order_rules.Order.query") as mock_query:
        mock_query.get.return_value = None
        result = order_rules.delete_order_by_id(999)
        assert result is False

def test_delete_order_by_id_database_error(mock_order, app_context):
    """
    Тестує delete_order_by_id при помилці бази даних.

    Очікується, що функція поверне False.
    Given: База даних кидає помилку
    When: Викликається delete_order_by_id
    Then: Повертається False
    Results:
    - Перевіряється обробка помилки
    """
    with patch("app.domain.order_rules.Order.query") as mock_query, \
         patch("app.domain.order_rules.db.session") as mock_session:
        
        mock_query.get.return_value = mock_order
        mock_session.delete = MagicMock()
        mock_session.commit.side_effect = Exception("DB Error")
        
        result = order_rules.delete_order_by_id(1)
        assert result is False

def test_update_order_status_success(mock_order, app_context):
    """
    Тестує update_order_status для успішного оновлення статусу.

    Очікується, що статус замовлення буде оновлено.
    Given: Замовлення існує
    When: Викликається update_order_status з новим статусом
    Then: Статус оновлено
    Results:
    - Перевіряється, що повернене замовлення має новий статус
    """
    with patch("app.domain.order_rules.Order.query") as mock_query, \
         patch("app.domain.order_rules.db.session") as mock_session:
        
        mock_query.get.return_value = mock_order
        mock_order.status = "Shipped"
        mock_session.commit = MagicMock()
        
        result_order, error = order_rules.update_order_status(1, "Shipped")
        assert result_order is not None
        assert error is None
        assert result_order.status == "Shipped"

def test_update_order_status_not_found(app_context):
    """
    Тестує update_order_status, коли замовлення не знайдено.

    Очікується, що функція поверне помилку.
    Given: Замовлення не існує
    When: Викликається update_order_status
    Then: Повертається помилка
    Results:
    - Перевіряється, що замовлення є None
    - Перевіряється текст помилки
    """
    with patch("app.domain.order_rules.Order.query") as mock_query:
        mock_query.get.return_value = None
        result_order, error = order_rules.update_order_status(999, "Shipped")
        assert result_order is None
        assert error is not None
        assert "не знайдено" in error

def test_update_order_status_database_error(mock_order, app_context):
    """
    Тестує update_order_status при помилці бази даних.

    Очікується, що функція поверне помилку.
    Given: База даних кидає помилку
    When: Викликається update_order_status
    Then: Повертається помилка
    Results:
    - Перевіряється обробка помилки
    """
    with patch("app.domain.order_rules.Order.query") as mock_query, \
         patch("app.domain.order_rules.db.session") as mock_session:
        
        mock_query.get.return_value = mock_order
        mock_session.commit.side_effect = Exception("DB Error")
        
        result_order, error = order_rules.update_order_status(1, "Shipped")
        assert result_order is None
        assert error is not None

def test_create_order_from_cart_success(mock_order, app_context):
    """
    Тестує create_order_from_cart для успішного створення.

    Очікується, що замовлення буде створено з кошика.
    Given: Кошик має товари
    When: Викликається create_order_from_cart
    Then: Замовлення створено
    Results:
    - Перевіряється, що замовлення створено
    """
    with patch("app.domain.order_rules.User.query") as mock_user_query, \
         patch("app.domain.order_rules.CartItem.query") as mock_cart_query, \
         patch("app.domain.order_rules.Order") as MockOrder, \
         patch("app.domain.order_rules.db.session") as mock_session:
        
        mock_user = MagicMock()
        mock_user.discount_multiplier = 1.0
        mock_user_query.get.return_value = mock_user
        
        mock_cart_items = [MagicMock()]
        mock_cart_query.filter_by.return_value.all.return_value = mock_cart_items
        
        mock_new_order = MagicMock()
        mock_new_order.id = 1
        MockOrder.add_order.return_value = mock_new_order
        
        mock_session.add = MagicMock()
        mock_session.delete = MagicMock()
        mock_session.commit = MagicMock()
        
        result_order, error = order_rules.create_order_from_cart(1)
        assert result_order is not None
        assert error is None

def test_create_order_from_cart_user_not_found(app_context):
    """
    Тестує create_order_from_cart, коли користувача не знайдено.

    Очікується, що функція поверне помилку.
    Given: Користувача не існує
    When: Викликається create_order_from_cart
    Then: Повертається помилка
    Results:
    - Перевіряється текст помилки
    """
    with patch("app.domain.order_rules.User.query") as mock_user_query:
        mock_user_query.get.return_value = None
        result_order, error = order_rules.create_order_from_cart(999)
        assert result_order is None
        assert error is not None
        assert "користувача" in error.lower()

def test_create_order_from_cart_empty_cart(app_context):
    """
    Тестує create_order_from_cart, коли кошик порожній.

    Очікується, що функція поверне помилку.
    Given: Кошик без товарів
    When: Викликається create_order_from_cart
    Then: Повертається помилка про порожній кошик
    Results:
    - Перевіряється текст помилки
    """
    with patch("app.domain.order_rules.User.query") as mock_user_query, \
         patch("app.domain.order_rules.CartItem.query") as mock_cart_query:
        
        mock_user = MagicMock()
        mock_user_query.get.return_value = mock_user
        mock_cart_query.filter_by.return_value.all.return_value = []
        
        result_order, error = order_rules.create_order_from_cart(1)
        assert result_order is None
        assert error is not None
        assert "порожній" in error.lower()

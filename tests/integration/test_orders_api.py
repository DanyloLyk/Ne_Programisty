import pytest
from unittest.mock import patch, MagicMock
from app.service.orders_service import OrdersService

# ============================================================
# GET ALL ORDERS
# ============================================================

def test_get_all_orders():
    mock_orders = [MagicMock(id=1), MagicMock(id=2)]
    with patch("app.domain.order_rules.get_all_orders", return_value=mock_orders):
        result = OrdersService.get_all_orders()
        assert result == mock_orders

# ============================================================
# GET ORDER BY ID
# ============================================================

def test_get_order_found():
    order_mock = MagicMock(id=1)
    with patch("app.domain.order_rules.get_order_by_id", return_value=order_mock):
        result = OrdersService.get_order(1)
        assert result == order_mock

def test_get_order_not_found():
    with patch("app.domain.order_rules.get_order_by_id", return_value=None):
        result = OrdersService.get_order(999)
        assert result is None

# ============================================================
# GET ORDERS BY USER
# ============================================================

def test_get_orders_user():
    order1 = MagicMock()
    order1.to_dict.return_value = {"id": 1}
    order2 = MagicMock()
    order2.to_dict.return_value = {"id": 2}
    
    with patch("app.domain.order_rules.get_user_orders", return_value=[order1, order2]):
        result = OrdersService.get_orders(user_id=1)
        assert result == [{"id": 1}, {"id": 2}]

# ============================================================
# ADD ORDER
# ============================================================

def test_add_order():
    mock_order = MagicMock(id=1)
    with patch("app.domain.order_rules.create_order_from_cart", return_value=mock_order):
        result = OrdersService.add_order(user_id=1)
        assert result == mock_order

# ============================================================
# EDIT STATUS ORDER
# ============================================================

def test_edit_status_order_success():
    with patch("app.domain.order_rules.update_order_status", return_value=True):
        result = OrdersService.edit_status_order(order_id=1, status="Completed")
        assert result is True

def test_edit_status_order_empty_status():
    result = OrdersService.edit_status_order(order_id=1, status=None)
    assert result == (None, "Статус не може бути порожнім")

def test_edit_status_order_invalid_status():
    result = OrdersService.edit_status_order(order_id=1, status="Invalid")
    assert "Недопустимий статус" in result[1]

# ============================================================
# DELETE ORDER
# ============================================================

def test_delete_order_success():
    with patch("app.domain.order_rules.delete_order_by_id", return_value=True):
        result = OrdersService.delete_order(order_id=1)
        assert result is True

def test_delete_order_fail():
    with patch("app.domain.order_rules.delete_order_by_id", return_value=False):
        result = OrdersService.delete_order(order_id=999)
        assert result is False

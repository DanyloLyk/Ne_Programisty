import pytest
from unittest.mock import patch, MagicMock
from app.service.desktop_service import DesktopService

# ============================================================
# GET ALL DESKTOPS
# ============================================================

def test_get_all_desktops_service_returns_list():
    mock_desktops = [MagicMock(id=1), MagicMock(id=2)]
    with patch("app.domain.desktop_rules.get_desktops", return_value=mock_desktops):
        result = DesktopService.get_all_desktops_service()
        assert result == mock_desktops

# ============================================================
# GET DESKTOP DETAILS
# ============================================================

def test_get_desktop_details_service_found():
    desktop_mock = MagicMock(id=1, name="Game 1")
    with patch("app.domain.desktop_rules.get_desktop_by_id", return_value=desktop_mock):
        result, error = DesktopService.get_desktop_details_service(1)
        assert result == desktop_mock
        assert error is None

def test_get_desktop_details_service_not_found():
    with patch("app.domain.desktop_rules.get_desktop_by_id", return_value=None):
        result, error = DesktopService.get_desktop_details_service(999)
        assert result is None
        assert error == "Товар не знайдено"

# ============================================================
# CREATE DESKTOP
# ============================================================

def test_create_desktop_service_success():
    data = {"name": "New Game", "description": "Cool game", "price": 1000, "image": None}
    desktop_mock = MagicMock(id=1, **data)
    with patch("app.domain.desktop_rules.add_desktop", return_value=(desktop_mock, None)):
        result, error = DesktopService.create_desktop_service(data)
        assert result == desktop_mock
        assert error is None

def test_create_desktop_service_name_too_short():
    data = {"name": "No", "description": "desc", "price": 100}
    result, error = DesktopService.create_desktop_service(data)
    assert result is None
    assert error.startswith("Назва занадто коротка")

def test_create_desktop_service_invalid_price():
    data = {"name": "Game", "description": "desc", "price": "abc"}
    result, error = DesktopService.create_desktop_service(data)
    assert result is None
    assert error.startswith("Невірний формат ціни")

def test_create_desktop_service_price_zero_or_negative():
    data = {"name": "Game", "description": "desc", "price": 0}
    result, error = DesktopService.create_desktop_service(data)
    assert result is None
    assert error.startswith("Ціна має бути більше 0")

def test_create_desktop_service_image_invalid():
    data = {"name": "Game", "description": "desc", "price": 1000, "image": "bad.png"}
    with patch.object(DesktopService, "_is_image_valid", return_value=False):
        result, error = DesktopService.create_desktop_service(data)
        assert result is None
        assert "не знайдено" in error

# ============================================================
# UPDATE DESKTOP
# ============================================================

def test_update_desktop_service_success():
    data = {"name": "Updated Game", "price": 1500, "image": None}
    desktop_mock = MagicMock(id=1, **data)
    with patch("app.domain.desktop_rules.edit_desktop_by_id", return_value=(desktop_mock, None)):
        result, error = DesktopService.update_desktop_service(1, data)
        assert result == desktop_mock
        assert error is None

def test_update_desktop_service_price_invalid():
    data = {"price": "abc"}
    result, error = DesktopService.update_desktop_service(1, data)
    assert result is None
    assert error.startswith("Невірний формат ціни")

def test_update_desktop_service_image_invalid():
    data = {"image": "bad.png"}
    with patch.object(DesktopService, "_is_image_valid", return_value=False):
        result, error = DesktopService.update_desktop_service(1, data)
        assert result is None
        assert "не знайдено" in error

# ============================================================
# DELETE DESKTOP
# ============================================================

def test_delete_desktop_service_success():
    with patch("app.domain.desktop_rules.delete_desktop_by_id", return_value=True):
        result, msg = DesktopService.delete_desktop_service(1)
        assert result is True
        assert msg == "Товар успішно видалено"

def test_delete_desktop_service_not_found():
    with patch("app.domain.desktop_rules.delete_desktop_by_id", return_value=False):
        result, msg = DesktopService.delete_desktop_service(999)
        assert result is False
        assert msg == "Товар не знайдено"
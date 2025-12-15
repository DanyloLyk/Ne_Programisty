import pytest
from unittest.mock import patch, MagicMock
from app.domain import desktop_rules

# ==============================
# Тести для desktop_rules
# ==============================

def test_get_desktops_returns_list(mock_desktop_list, app_context):
    """
    Тестує get_desktops, коли є товари в базі.

    Очікується, що функція поверне список словників товарів.
    Given: Існує товар в базі
    When: Викликається get_desktops
    Then: Повертається список словників
    Results:
    - Перевіряється, що список не порожній
    - Перевіряється структура даних товару
    """
    with patch("app.domain.desktop_rules.Desktop.query") as mock_query:
        mock_query.all.return_value = mock_desktop_list
        result = desktop_rules.get_desktops()
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 2

def test_get_desktops_empty(app_context):
    """
    Тестує get_desktops, коли в базі немає товарів.

    Очікується, що функція поверне порожній список.
    Given: Немає товарів в базі
    When: Викликається get_desktops
    Then: Повертається порожній список
    Results:
    - Перевіряється, що список є порожнім
    """
    with patch("app.domain.desktop_rules.Desktop.query") as mock_query:
        mock_query.all.return_value = []
        result = desktop_rules.get_desktops()
        assert result == []

def test_get_desktops_exception(app_context):
    """
    Тестує get_desktops при помилці бази даних.

    Очікується, що функція поверне порожній список.
    Given: База даних кидає помилку
    When: Викликається get_desktops
    Then: Повертається порожній список
    Results:
    - Перевіряється, що помилка обробляється корректно
    """
    with patch("app.domain.desktop_rules.Desktop.query") as mock_query:
        mock_query.all.side_effect = Exception("DB Error")
        result = desktop_rules.get_desktops()
        assert result == []

def test_get_desktop_by_id_found(mock_desktop, app_context):
    """
    Тестує get_desktop_by_id, коли товар знайдено.

    Очікується, що функція поверне товар.
    Given: Існує товар з ID 1
    When: Викликається get_desktop_by_id(1)
    Then: Повертається товар
    Results:
    - Перевіряється, що повернений об'єкт має правильний ID
    - Перевіряється дані товару
    """
    with patch("app.domain.desktop_rules.Desktop.query") as mock_query:
        mock_query.get.return_value = mock_desktop
        result = desktop_rules.get_desktop_by_id(1)
        assert result is not None
        assert result.id == 1
        assert result.name == "Game 1"
        assert result.price == 500.0

def test_get_desktop_by_id_not_found(app_context):
    """
    Тестує get_desktop_by_id, коли товар не знайдено.

    Очікується, що функція поверне None.
    Given: Товара з ID 999 не існує
    When: Викликається get_desktop_by_id(999)
    Then: Повертається None
    Results:
    - Перевіряється, що повернене значення є None
    """
    with patch("app.domain.desktop_rules.Desktop.query") as mock_query:
        mock_query.get.return_value = None
        result = desktop_rules.get_desktop_by_id(999)
        assert result is None

def test_add_desktop_success(mock_desktop, app_context):
    """
    Тестує add_desktop для успішного додавання товару.

    Очікується, що новий товар буде створено.
    Given: Валідні дані товару
    When: Викликається add_desktop
    Then: Товар додано до бази
    Results:
    - Перевіряється, що повернений товар не None
    - Перевіряється дані товару
    """
    with patch("app.domain.desktop_rules.Desktop") as MockDesktop, \
         patch("app.domain.desktop_rules.db.session") as mock_session:
        
        mock_new_desktop = MagicMock()
        mock_new_desktop.id = 1
        mock_new_desktop.name = "Game 1"
        mock_new_desktop.description = "Опис ігри"
        mock_new_desktop.price = 500.0
        mock_new_desktop.image = "game1.png"
        
        MockDesktop.return_value = mock_new_desktop
        mock_session.add = MagicMock()
        mock_session.commit = MagicMock()
        
        result_desktop, error = desktop_rules.add_desktop(
            "Game 1", "Опис ігри", 500.0, "game1.png"
        )
        assert result_desktop is not None
        assert error is None
        assert result_desktop.name == "Game 1"

def test_add_desktop_database_error(app_context):
    """
    Тестує add_desktop при помилці бази даних.

    Очікується, що функція поверне помилку.
    Given: База даних кидає помилку
    When: Викликається add_desktop
    Then: Повертається помилка
    Results:
    - Перевіряється, що товар є None
    - Перевіряється, що помилка не порожня
    """
    with patch("app.domain.desktop_rules.Desktop") as MockDesktop, \
         patch("app.domain.desktop_rules.db.session") as mock_session:
        
        MockDesktop.side_effect = Exception("DB Error")
        result_desktop, error = desktop_rules.add_desktop(
            "Game 1", "Опис", 500.0, "game1.png"
        )
        assert result_desktop is None
        assert error is not None

def test_delete_desktop_by_id_success(mock_desktop, app_context):
    """
    Тестує delete_desktop_by_id для успішного видалення.

    Очікується, що товар буде видалено.
    Given: Товар існує
    When: Викликається delete_desktop_by_id
    Then: Товар видалено
    Results:
    - Перевіряється, що функція повертає True
    """
    with patch("app.domain.desktop_rules.Desktop.query") as mock_query, \
         patch("app.domain.desktop_rules.db.session") as mock_session:
        
        mock_query.get.return_value = mock_desktop
        mock_session.delete = MagicMock()
        mock_session.commit = MagicMock()
        
        result = desktop_rules.delete_desktop_by_id(1)
        assert result is True

def test_delete_desktop_by_id_not_found(app_context):
    """
    Тестує delete_desktop_by_id, коли товар не знайдено.

    Очікується, що функція поверне False.
    Given: Товара не існує
    When: Викликається delete_desktop_by_id
    Then: Повертається False
    Results:
    - Перевіряється, що функція повертає False
    """
    with patch("app.domain.desktop_rules.Desktop.query") as mock_query:
        mock_query.get.return_value = None
        result = desktop_rules.delete_desktop_by_id(999)
        assert result is False

def test_delete_desktop_by_id_database_error(mock_desktop, app_context):
    """
    Тестує delete_desktop_by_id при помилці бази даних.

    Очікується, що функція поверне False.
    Given: База даних кидає помилку
    When: Викликається delete_desktop_by_id
    Then: Повертається False
    Results:
    - Перевіряється обробка помилки
    """
    with patch("app.domain.desktop_rules.Desktop.query") as mock_query, \
         patch("app.domain.desktop_rules.db.session") as mock_session:
        
        mock_query.get.return_value = mock_desktop
        mock_session.delete = MagicMock()
        mock_session.commit.side_effect = Exception("DB Error")
        
        result = desktop_rules.delete_desktop_by_id(1)
        assert result is False

def test_edit_desktop_by_id_success(mock_desktop, app_context):
    """
    Тестує edit_desktop_by_id для успішного редагування.

    Очікується, що товар буде оновлено.
    Given: Товар існує
    When: Викликається edit_desktop_by_id з новими даними
    Then: Товар оновлено
    Results:
    - Перевіряється, що повернений товар мав оновлені дані
    """
    with patch("app.domain.desktop_rules.Desktop.query") as mock_query, \
         patch("app.domain.desktop_rules.db.session") as mock_session:
        
        mock_query.get.return_value = mock_desktop
        mock_desktop.name = "Updated Game"
        mock_desktop.price = 600.0
        mock_session.commit = MagicMock()
        
        result_desktop, error = desktop_rules.edit_desktop_by_id(
            1, name="Updated Game", price=600.0
        )
        assert result_desktop is not None
        assert error is None
        assert result_desktop.name == "Updated Game"
        assert result_desktop.price == 600.0

def test_edit_desktop_by_id_not_found(app_context):
    """
    Тестує edit_desktop_by_id, коли товар не знайдено.

    Очікується, що функція поверне помилку.
    Given: Товара не існує
    When: Викликається edit_desktop_by_id
    Then: Повертається помилка
    Results:
    - Перевіряється, що товар є None
    - Перевіряється текст помилки
    """
    with patch("app.domain.desktop_rules.Desktop.query") as mock_query:
        mock_query.get.return_value = None
        result_desktop, error = desktop_rules.edit_desktop_by_id(
            999, name="Updated"
        )
        assert result_desktop is None
        assert error is not None
        assert "не знайдено" in error

def test_edit_desktop_by_id_database_error(mock_desktop, app_context):
    """
    Тестує edit_desktop_by_id при помилці бази даних.

    Очікується, що функція поверне помилку.
    Given: База даних кидає помилку
    When: Викликається edit_desktop_by_id
    Then: Повертається помилка
    Results:
    - Перевіряється обробка помилки
    """
    with patch("app.domain.desktop_rules.Desktop.query") as mock_query, \
         patch("app.domain.desktop_rules.db.session") as mock_session:
        
        mock_query.get.return_value = mock_desktop
        mock_session.commit.side_effect = Exception("DB Error")
        
        result_desktop, error = desktop_rules.edit_desktop_by_id(
            1, name="Updated"
        )
        assert result_desktop is None
        assert error is not None

import pytest
from unittest.mock import patch, MagicMock
from app.domain import feedback_rules

# ==============================
# Тести для feedback_rules
# ==============================

def test_get_feedbacks_returns_list(mock_feedback_list, app_context):
    """
    Тестує get_feedbacks, коли є відгуки в базі.

    Очікується, що функція поверне список відгуків.
    Given: Існує відгук в базі
    When: Викликається get_feedbacks
    Then: Повертається список відгуків
    Results:
    - Перевіряється, що список не порожній
    - Перевіряється дані відгуку
    """
    with patch("app.domain.feedback_rules.Feedback.query") as mock_query:
        mock_query.order_by.return_value.all.return_value = mock_feedback_list
        result = feedback_rules.get_feedbacks()
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0].title == "Відгук 1"

def test_get_feedbacks_empty(app_context):
    """
    Тестує get_feedbacks, коли відгуків немає.

    Очікується, що функція поверне порожній список.
    Given: Немає відгуків в базі
    When: Викликається get_feedbacks
    Then: Повертається порожній список
    Results:
    - Перевіряється, що список є порожнім
    """
    with patch("app.domain.feedback_rules.Feedback.query") as mock_query:
        mock_query.order_by.return_value.all.return_value = []
        result = feedback_rules.get_feedbacks()
        assert result == []

def test_get_feedbacks_exception(app_context):
    """
    Тестує get_feedbacks при помилці бази даних.

    Очікується, що функція поверне порожній список.
    Given: База даних кидає помилку
    When: Викликається get_feedbacks
    Then: Повертається порожній список
    Results:
    - Перевіряється обробка помилки
    """
    with patch("app.domain.feedback_rules.Feedback.query") as mock_query:
        mock_query.order_by.side_effect = Exception("DB Error")
        result = feedback_rules.get_feedbacks()
        assert result == []

def test_get_feedback_by_id_found(mock_feedback, app_context):
    """
    Тестує get_feedback_by_id, коли відгук знайдено.

    Очікується, що функція поверне відгук.
    Given: Існує відгук з ID 1
    When: Викликається get_feedback_by_id(1)
    Then: Повертається відгук
    Results:
    - Перевіряється, що повернений об'єкт має правильний ID
    - Перевіряються дані відгуку
    """
    with patch("app.domain.feedback_rules.Feedback.query") as mock_query:
        mock_query.get.return_value = mock_feedback
        result = feedback_rules.get_feedback_by_id(1)
        assert result is not None
        assert result.id == 1
        assert result.title == "Чудовий товар!"

def test_get_feedback_by_id_not_found(app_context):
    """
    Тестує get_feedback_by_id, коли відгук не знайдено.

    Очікується, що функція поверне None.
    Given: Відгуку з ID 999 не існує
    When: Викликається get_feedback_by_id(999)
    Then: Повертається None
    Results:
    - Перевіряється, що повернене значення є None
    """
    with patch("app.domain.feedback_rules.Feedback.query") as mock_query:
        mock_query.get.return_value = None
        result = feedback_rules.get_feedback_by_id(999)
        assert result is None

def test_add_feedback_success(app_context):
    """
    Тестує add_feedback для успішного додавання відгуку.

    Очікується, що новий відгук буде створено.
    Given: Валідні дані відгуку
    When: Викликається add_feedback
    Then: Відгук додано до бази
    Results:
    - Перевіряється, що повернений відгук не None
    - Перевіряються дані відгуку
    """
    with patch("app.domain.feedback_rules.Feedback") as MockFeedback, \
         patch("app.domain.feedback_rules.db.session") as mock_session:
        
        mock_new_feedback = MagicMock()
        mock_new_feedback.id = 1
        mock_new_feedback.title = "Відгук 1"
        mock_new_feedback.description = "Чудовий товар"
        mock_new_feedback.user_id = 1
        
        MockFeedback.return_value = mock_new_feedback
        mock_session.add = MagicMock()
        mock_session.commit = MagicMock()
        
        result_feedback, error = feedback_rules.add_feedback(
            "Відгук 1", "Чудовий товар", 1
        )
        assert result_feedback is not None
        assert error is None
        assert result_feedback.title == "Відгук 1"

def test_add_feedback_database_error(app_context):
    """
    Тестує add_feedback при помилці бази даних.

    Очікується, що функція поверне помилку.
    Given: База даних кидає помилку
    When: Викликається add_feedback
    Then: Повертається помилка
    Results:
    - Перевіряється, що відгук є None
    - Перевіряється, що помилка не порожня
    """
    with patch("app.domain.feedback_rules.Feedback") as MockFeedback, \
         patch("app.domain.feedback_rules.db.session") as mock_session:
        
        MockFeedback.side_effect = Exception("DB Error")
        result_feedback, error = feedback_rules.add_feedback(
            "Відгук", "Опис", 1
        )
        assert result_feedback is None
        assert error is not None

def test_delete_feedback_by_id_success(mock_feedback, app_context):
    """
    Тестує delete_feedback_by_id для успішного видалення.

    Очікується, що відгук буде видалено.
    Given: Відгук існує
    When: Викликається delete_feedback_by_id
    Then: Відгук видалено
    Results:
    - Перевіряється, що функція повертає True
    """
    with patch("app.domain.feedback_rules.Feedback.query") as mock_query, \
         patch("app.domain.feedback_rules.db.session") as mock_session:
        
        mock_query.get.return_value = mock_feedback
        mock_session.delete = MagicMock()
        mock_session.commit = MagicMock()
        
        result = feedback_rules.delete_feedback_by_id(1)
        assert result is True

def test_delete_feedback_by_id_not_found(app_context):
    """
    Тестує delete_feedback_by_id, коли відгук не знайдено.

    Очікується, що функція поверне False.
    Given: Відгуку не існує
    When: Викликається delete_feedback_by_id
    Then: Повертається False
    Results:
    - Перевіряється, що функція повертає False
    """
    with patch("app.domain.feedback_rules.Feedback.query") as mock_query:
        mock_query.get.return_value = None
        result = feedback_rules.delete_feedback_by_id(999)
        assert result is False

def test_delete_feedback_by_id_database_error(mock_feedback, app_context):
    """
    Тестує delete_feedback_by_id при помилці бази даних.

    Очікується, що функція поверне False.
    Given: База даних кидає помилку
    When: Викликається delete_feedback_by_id
    Then: Повертається False
    Results:
    - Перевіряється обробка помилки
    """
    with patch("app.domain.feedback_rules.Feedback.query") as mock_query, \
         patch("app.domain.feedback_rules.db.session") as mock_session:
        
        mock_query.get.return_value = mock_feedback
        mock_session.delete = MagicMock()
        mock_session.commit.side_effect = Exception("DB Error")
        
        result = feedback_rules.delete_feedback_by_id(1)
        assert result is False

def test_edit_feedback_by_id_success(mock_feedback, app_context):
    """
    Тестує edit_feedback_by_id для успішного редагування.

    Очікується, що відгук буде оновлено.
    Given: Відгук існує
    When: Викликається edit_feedback_by_id з новими даними
    Then: Відгук оновлено
    Results:
    - Перевіряється, що повернений відгук мав оновлені дані
    """
    with patch("app.domain.feedback_rules.Feedback.query") as mock_query, \
         patch("app.domain.feedback_rules.db.session") as mock_session:
        
        mock_query.get.return_value = mock_feedback
        mock_feedback.title = "Оновлений відгук"
        mock_feedback.description = "Оновлений опис"
        mock_session.commit = MagicMock()
        
        result_feedback, error = feedback_rules.edit_feedback_by_id(
            1, title="Оновлений відгук", description="Оновлений опис"
        )
        assert result_feedback is not None
        assert error is None
        assert result_feedback.title == "Оновлений відгук"

def test_edit_feedback_by_id_not_found(app_context):
    """
    Тестує edit_feedback_by_id, коли відгук не знайдено.

    Очікується, що функція поверне помилку.
    Given: Відгуку не існує
    When: Викликається edit_feedback_by_id
    Then: Повертається помилка
    Results:
    - Перевіряється, що відгук є None
    - Перевіряється текст помилки
    """
    with patch("app.domain.feedback_rules.Feedback.query") as mock_query:
        mock_query.get.return_value = None
        result_feedback, error = feedback_rules.edit_feedback_by_id(
            999, title="Updated"
        )
        assert result_feedback is None
        assert error is not None
        assert "не знайдено" in error

def test_edit_feedback_by_id_database_error(mock_feedback, app_context):
    """
    Тестує edit_feedback_by_id при помилці бази даних.

    Очікується, що функція поверне помилку.
    Given: База даних кидає помилку
    When: Викликається edit_feedback_by_id
    Then: Повертається помилка
    Results:
    - Перевіряється обробка помилки
    """
    with patch("app.domain.feedback_rules.Feedback.query") as mock_query, \
         patch("app.domain.feedback_rules.db.session") as mock_session:
        
        mock_query.get.return_value = mock_feedback
        mock_session.commit.side_effect = Exception("DB Error")
        
        result_feedback, error = feedback_rules.edit_feedback_by_id(
            1, title="Updated"
        )
        assert result_feedback is None
        assert error is not None

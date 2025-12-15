import pytest
from unittest.mock import patch, MagicMock
from app.service.feedback_service import FeedbackService

# ============================================================
# GET ALL FEEDBACKS
# ============================================================

def test_get_all_feedbacks_service_returns_list():
    mock_feedbacks = [MagicMock(id=1), MagicMock(id=2)]
    with patch("app.domain.feedback_rules.get_feedbacks", return_value=mock_feedbacks):
        result = FeedbackService.get_all_feedbacks_service()
        assert result == mock_feedbacks

# ============================================================
# GET FEEDBACK BY ID
# ============================================================

def test_get_feedback_by_id_service_found():
    feedback_mock = MagicMock(id=1, title="Test", description="Test desc")
    with patch("app.domain.feedback_rules.get_feedback_by_id", return_value=feedback_mock):
        feedback, error = FeedbackService.get_feedback_by_id_service(1)
        assert feedback == feedback_mock
        assert error is None

def test_get_feedback_by_id_service_not_found():
    with patch("app.domain.feedback_rules.get_feedback_by_id", return_value=None):
        feedback, error = FeedbackService.get_feedback_by_id_service(999)
        assert feedback is None
        assert error == "Feedback not found"

# ============================================================
# CREATE FEEDBACK
# ============================================================

def test_create_feedback_service_success():
    data = {"title": "Great product", "description": "Really liked it"}
    user_id = 1
    mock_feedback = MagicMock(id=1, **data)

    with patch("app.domain.feedback_rules.add_feedback", return_value=(mock_feedback, None)):
        feedback, error = FeedbackService.create_feedback_service(data, user_id)
        assert feedback == mock_feedback
        assert error is None

def test_create_feedback_service_title_too_short():
    data = {"title": "Hi", "description": "Valid description"}
    feedback, error = FeedbackService.create_feedback_service(data, user_id=1)
    assert feedback is None
    assert error.startswith("Заголовок занадто короткий")

def test_create_feedback_service_description_too_short():
    data = {"title": "Valid Title", "description": "123"}
    feedback, error = FeedbackService.create_feedback_service(data, user_id=1)
    assert feedback is None
    assert error.startswith("Текст відгуку занадто короткий")

def test_create_feedback_service_no_user_id():
    data = {"title": "Valid Title", "description": "Valid description"}
    feedback, error = FeedbackService.create_feedback_service(data, user_id=None)
    assert feedback is None
    assert error == "Необхідна авторизація"

# ============================================================
# UPDATE FEEDBACK
# ============================================================

def test_update_feedback_service_success():
    data = {"title": "Updated title", "description": "Updated desc"}
    mock_feedback = MagicMock(id=1, **data)
    with patch("app.domain.feedback_rules.edit_feedback_by_id", return_value=(mock_feedback, None)):
        feedback, error = FeedbackService.update_feedback_service(1, data)
        assert feedback == mock_feedback
        assert error is None

def test_update_feedback_service_title_too_short():
    data = {"title": "Hi"}
    feedback, error = FeedbackService.update_feedback_service(1, data)
    assert feedback is None
    assert error.startswith("Заголовок занадто короткий")

def test_update_feedback_service_description_too_short():
    data = {"description": "123"}
    feedback, error = FeedbackService.update_feedback_service(1, data)
    assert feedback is None
    assert error.startswith("Текст відгуку занадто короткий")

# ============================================================
# DELETE FEEDBACK
# ============================================================

def test_delete_feedback_service_success():
    with patch("app.domain.feedback_rules.delete_feedback_by_id", return_value=True):
        result, msg = FeedbackService.delete_feedback_service(1)
        assert result is True
        assert msg == "Відгук успішно видалено"

def test_delete_feedback_service_not_found():
    with patch("app.domain.feedback_rules.delete_feedback_by_id", return_value=False):
        result, msg = FeedbackService.delete_feedback_service(999)
        assert result is False
        assert msg == "Відгук не знайдено"

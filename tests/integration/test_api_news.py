import pytest
from unittest.mock import patch, MagicMock
from app.service.news_service import NewsService

# ============================================================
# FETCH ALL NEWS
# ============================================================

def test_fetch_all_news_returns_list():
    mock_news = [MagicMock(id=1), MagicMock(id=2)]
    with patch("app.domain.news_rules.get_news", return_value=mock_news):
        result = NewsService.fetch_all_news()
        assert result == mock_news

# ============================================================
# FETCH NEWS BY ID
# ============================================================

def test_fetch_news_by_id_found():
    news_mock = MagicMock(id=1, name="Test News")
    with patch("app.domain.news_rules.get_news_by_id", return_value=news_mock):
        result = NewsService.fetch_news_by_id(1)
        assert result == news_mock

def test_fetch_news_by_id_not_found():
    with patch("app.domain.news_rules.get_news_by_id", return_value=None):
        result = NewsService.fetch_news_by_id(999)
        assert result is None

# ============================================================
# REMOVE NEWS
# ============================================================

def test_remove_news_by_id_success():
    with patch("app.domain.news_rules.delete_news_by_id", return_value=True):
        result = NewsService.remove_news_by_id(1)
        assert result is True

def test_remove_news_by_id_fail():
    with patch("app.domain.news_rules.delete_news_by_id", return_value=False):
        result = NewsService.remove_news_by_id(999)
        assert result is False

# ============================================================
# CREATE NEWS
# ============================================================

def test_create_news_success():
    name = "Title"
    desc = "Desc"
    desc2 = "Desc2"
    images = ["img1.png", "img2.png"]
    news_mock = MagicMock(id=1)
    with patch("app.domain.news_rules.add_news", return_value=(news_mock, None)), \
         patch.object(NewsService, "_is_image_valid", return_value=True):
        result, error = NewsService.create_news(name, desc, desc2, images)
        assert result == news_mock
        assert error is None

def test_create_news_missing_name_or_description():
    result, error = NewsService.create_news("", "", "desc2", None)
    assert result is None
    assert "обов'язковими" in error

def test_create_news_invalid_image():
    with patch.object(NewsService, "_is_image_valid", return_value=False):
        result, error = NewsService.create_news("Title", "Desc", "Desc2", ["bad.png"])
        assert result is None
        assert "не знайдено або недоступне" in error

# ============================================================
# UPDATE NEWS
# ============================================================

def test_update_news_success():
    news_mock = MagicMock(id=1)
    with patch("app.domain.news_rules.edit_news", return_value=(news_mock, None)), \
         patch.object(NewsService, "_is_image_valid", return_value=True):
        result, error = NewsService.update_news(1, "Title", "Desc", "Desc2", ["img1.png"])
        assert result == news_mock
        assert error is None

def test_update_news_invalid_image():
    with patch.object(NewsService, "_is_image_valid", return_value=False):
        result, error = NewsService.update_news(1, "Title", "Desc", "Desc2", ["bad.png"])
        assert result is None
        assert "не знайдено або недоступне" in error
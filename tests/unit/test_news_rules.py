import pytest
from unittest.mock import patch, MagicMock
from app.domain import news_rules

# ==============================
# Тести для news_rules
# ==============================

def test_get_news_returns_list(mock_news_with_images, app_context):
    """
    Тестує get_news, коли є новини в базі.

    Очікується, що функція поверне список словників новин.
    Given: Існує новина в базі
    When: Викликається get_news
    Then: Повертається список словників
    Results:
    - Перевіряється, що список не порожній
    - Перевіряється структура даних новини
    """
    with patch("app.domain.news_rules.News.query") as mock_query:
        mock_query.all.return_value = [mock_news_with_images]
        result = news_rules.get_news()
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 1
        assert "id" in result[0]
        assert "name" in result[0]
        assert "images" in result[0]

def test_get_news_empty(app_context):
    """
    Тестує get_news, коли новин немає.

    Очікується, що функція поверне порожній список.
    Given: Немає новин в базі
    When: Викликається get_news
    Then: Повертається порожній список
    Results:
    - Перевіряється, що список є порожнім
    """
    with patch("app.domain.news_rules.News.query") as mock_query:
        mock_query.all.return_value = []
        result = news_rules.get_news()
        assert result == []

def test_get_news_by_id_found(mock_news_with_images, app_context):
    """
    Тестує get_news_by_id, коли новина знайдена.

    Очікується, що функція поверне новину як словник.
    Given: Існує новина з ID 1
    When: Викликається get_news_by_id(1)
    Then: Повертається словник новини
    Results:
    - Перевіряється, що повернена новина має ID 1
    - Перевіряються дані новини
    """
    with patch("app.domain.news_rules.News.query") as mock_query:
        mock_query.get.return_value = mock_news_with_images
        result = news_rules.get_news_by_id(1)
        assert result is not None
        assert isinstance(result, dict)
        assert result["id"] == 1
        assert result["name"] == "Нова гра"
        assert "images" in result

def test_get_news_by_id_not_found(app_context):
    """
    Тестує get_news_by_id, коли новина не знайдена.

    Очікується, що функція поверне None.
    Given: Новини з ID 999 не існує
    When: Викликається get_news_by_id(999)
    Then: Повертається None
    Results:
    - Перевіряється, що повернене значення є None
    """
    with patch("app.domain.news_rules.News.query") as mock_query:
        mock_query.get.return_value = None
        result = news_rules.get_news_by_id(999)
        assert result is None

def test_delete_news_by_id_success(mock_news, app_context):
    """
    Тестує delete_news_by_id для успішного видалення.

    Очікується, що новина буде видалена.
    Given: Новина існує
    When: Викликається delete_news_by_id
    Then: Новина видалена
    Results:
    - Перевіряється, що функція повертає True
    """
    with patch("app.domain.news_rules.News.query") as mock_query, \
         patch("app.domain.news_rules.db.session") as mock_session:
        
        mock_query.get.return_value = mock_news
        mock_session.delete = MagicMock()
        mock_session.commit = MagicMock()
        
        result = news_rules.delete_news_by_id(1)
        assert result is True

def test_delete_news_by_id_not_found(app_context):
    """
    Тестує delete_news_by_id, коли новина не знайдена.

    Очікується, що функція поверне False.
    Given: Новини не існує
    When: Викликається delete_news_by_id
    Then: Повертається False
    Results:
    - Перевіряється, що функція повертає False
    """
    with patch("app.domain.news_rules.News.query") as mock_query:
        mock_query.get.return_value = None
        result = news_rules.delete_news_by_id(999)
        assert result is False

def test_delete_news_by_id_database_error(mock_news, app_context):
    """
    Тестує delete_news_by_id при помилці бази даних.

    Очікується, що функція поверне False.
    Given: База даних кидає помилку
    When: Викликається delete_news_by_id
    Then: Повертається False
    Results:
    - Перевіряється обробка помилки
    """
    with patch("app.domain.news_rules.News.query") as mock_query, \
         patch("app.domain.news_rules.db.session") as mock_session:
        
        mock_query.get.return_value = mock_news
        mock_session.delete = MagicMock()
        mock_session.commit.side_effect = Exception("DB Error")
        
        result = news_rules.delete_news_by_id(1)
        assert result is False

def test_add_news_success(app_context):
    """
    Тестує add_news для успішного додавання новини.

    Очікується, що нова новина буде створена.
    Given: Валідні дані новини
    When: Викликається add_news
    Then: Новина додана до бази
    Results:
    - Перевіряється, що повернена новина не None
    - Перевіряються дані новини
    """
    with patch("app.domain.news_rules.News") as MockNews, \
         patch("app.domain.news_rules.NewsImage") as MockNewsImage, \
         patch("app.domain.news_rules.db.session") as mock_session:
        
        mock_new_news = MagicMock()
        mock_new_news.id = 1
        mock_new_news.name = "Нова новина"
        mock_new_news.description = "Опис"
        mock_new_news.descriptionSecond = "Деталі"
        
        MockNews.return_value = mock_new_news
        mock_session.add = MagicMock()
        mock_session.commit = MagicMock()
        
        result_news, error = news_rules.add_news(
            "Нова новина", "Опис", "Деталі", ["image1.png", "image2.png"]
        )
        assert result_news is not None
        assert error is None
        assert result_news.name == "Нова новина"

def test_add_news_database_error(app_context):
    """
    Тестує add_news при помилці бази даних.

    Очікується, що функція поверне помилку.
    Given: База даних кидає помилку
    When: Викликається add_news
    Then: Повертається помилка
    Results:
    - Перевіряється, що новина є None
    - Перевіряється, що помилка не порожня
    """
    with patch("app.domain.news_rules.News") as MockNews, \
         patch("app.domain.news_rules.db.session") as mock_session:
        
        MockNews.side_effect = Exception("DB Error")
        result_news, error = news_rules.add_news(
            "Новина", "Опис", "Деталі", ["image.png"]
        )
        assert result_news is None
        assert error is not None

def test_edit_news_success(mock_news, app_context):
    """
    Тестує edit_news для успішного редагування.

    Очікується, що новина буде оновлена.
    Given: Новина існує
    When: Викликається edit_news з новими даними
    Then: Новина оновлена
    Results:
    - Перевіряється, що повернена новина мала оновлені дані
    """
    with patch("app.domain.news_rules.News.query") as mock_query, \
         patch("app.domain.news_rules.NewsImage.query") as mock_image_query, \
         patch("app.domain.news_rules.NewsImage") as MockNewsImage, \
         patch("app.domain.news_rules.db.session") as mock_session:
        
        mock_query.get.return_value = mock_news
        mock_image_query.filter_by.return_value.delete = MagicMock()
        mock_news.name = "Оновлена новина"
        mock_session.add = MagicMock()
        mock_session.commit = MagicMock()
        
        result_news, error = news_rules.edit_news(
            1, "Оновлена новина", "Опис", "Деталі", ["image.png"]
        )
        assert result_news is not None
        assert error is None
        assert result_news.name == "Оновлена новина"

def test_edit_news_not_found(app_context):
    """
    Тестує edit_news, коли новина не знайдена.

    Очікується, що функція поверне помилку.
    Given: Новини не існує
    When: Викликається edit_news
    Then: Повертається помилка
    Results:
    - Перевіряється, що новина є None
    - Перевіряється текст помилки
    """
    with patch("app.domain.news_rules.News.query") as mock_query:
        mock_query.get.return_value = None
        result_news, error = news_rules.edit_news(
            999, "Новина", "Опис", "Деталі", ["image.png"]
        )
        assert result_news is None
        assert error is not None
        assert "не знайдено" in error

def test_edit_news_database_error(mock_news, app_context):
    """
    Тестує edit_news при помилці бази даних.

    Очікується, що функція поверне помилку.
    Given: База даних кидає помилку
    When: Викликається edit_news
    Then: Повертається помилка
    Results:
    - Перевіряється обробка помилки
    """
    with patch("app.domain.news_rules.News.query") as mock_query, \
         patch("app.domain.news_rules.NewsImage.query") as mock_image_query, \
         patch("app.domain.news_rules.db.session") as mock_session:
        
        mock_query.get.return_value = mock_news
        mock_image_query.filter_by.return_value.delete = MagicMock()
        mock_session.commit.side_effect = Exception("DB Error")
        
        result_news, error = news_rules.edit_news(
            1, "Новина", "Опис", "Деталі", ["image.png"]
        )
        assert result_news is None
        assert error is not None

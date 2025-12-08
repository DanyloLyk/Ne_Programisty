from app.domain.news_rules import get_news, add_news, get_news_by_id, delete_news_by_id
from app.models.news import News, NewsImage                     
from .. import db

class NewsService:
    @staticmethod
    def fetch_all_news():
        return get_news()
    

    @staticmethod
    def fetch_news_by_id(news_id):
        return get_news_by_id(news_id)
    @staticmethod
    def remove_news_by_id(news_id):
        return delete_news_by_id(news_id)
    @staticmethod
    def create_news(name, description, descriptionSecond, image_urls):
        return add_news(name, description, descriptionSecond, image_urls)
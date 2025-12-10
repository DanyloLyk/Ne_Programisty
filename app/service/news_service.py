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
    
    @staticmethod
    def update_news(news_id, name, description, descriptionSecond, image_urls):
        from .. import db
        item = News.query.get(news_id)
        if item is None:
            return None

        item.name = name
        item.description = description
        item.descriptionSecond = descriptionSecond

        # Видаляємо існуючі зображення
        NewsImage.query.filter_by(news_id=news_id).delete()

        # Додаємо нові зображення
        for url in image_urls:
            news_image = NewsImage(
                img_url=url,
                news_id=news_id
            )
            db.session.add(news_image)

        db.session.commit()
        return item
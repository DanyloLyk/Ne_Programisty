import os
from requests import get
from flask import current_app
from ..domain import news_rules

class NewsService:
    
    @staticmethod
    def _is_image_valid(image_path):
        """Та сама розумна перевірка"""
        if not image_path: return True
        
        if image_path.startswith(('http://', 'https://')):
            try:
                response = get(image_path, timeout=3)
                return response.status_code == 200
            except:
                return False
        else:
            static_folder = current_app.static_folder 
            full_path = os.path.join(static_folder, image_path)
            return os.path.exists(full_path)

    @staticmethod
    def fetch_all_news():
        return news_rules.get_news()

    @staticmethod
    def fetch_news_by_id(news_id):
        return news_rules.get_news_by_id(news_id)

    @staticmethod
    def remove_news_by_id(news_id):
        return news_rules.delete_news_by_id(news_id)

    @staticmethod
    def create_news(name, description, descriptionSecond, image_urls):
        if not name or not description:
            return None, "Назва та опис є обов'язковими"
            
        # 👇 ПЕРЕВІРЯЄМО КОЖНУ КАРТИНКУ В СПИСКУ
        if image_urls:
            for url in image_urls:
                if not NewsService._is_image_valid(url):
                    return None, f"Зображення '{url}' не знайдено або недоступне"
            
        return news_rules.add_news(name, description, descriptionSecond, image_urls)
    
    @staticmethod
    def update_news(news_id, name, description, descriptionSecond, image_urls):
        # 👇 ПЕРЕВІРКА ПРИ ОНОВЛЕННІ
        if image_urls:
            for url in image_urls:
                if not NewsService._is_image_valid(url):
                    return None, f"Зображення '{url}' не знайдено або недоступне"

        return news_rules.edit_news(news_id, name, description, descriptionSecond, image_urls)
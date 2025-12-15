from app.models.news import News, NewsImage
from .. import db 

def get_news():
    news_items = News.query.all()
    res = []
    for item in news_items:
        res.append({
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "descriptionSecond": item.descriptionSecond,
            "images": [img.img_url for img in item.images]
        })
    return res
    
def get_news_by_id(news_id):
    item = News.query.get(news_id)
    if item is None:
        return None
    return {
        "id": item.id,
        "name": item.name,
        "description": item.description,
        "descriptionSecond": item.descriptionSecond,
        "images": [img.img_url for img in item.images]
    }

def delete_news_by_id(news_id):
    item = News.query.get(news_id)
    if item is None:
        return False
    try:
        db.session.delete(item)
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False

def add_news(name, description, descriptionSecond, image_urls):
    try:
        new_news = News(
            name=name,
            description=description,
            descriptionSecond=descriptionSecond
        )
        db.session.add(new_news)
        db.session.commit() # Комітимо, щоб отримати ID

        for url in image_urls:
            news_image = NewsImage(
                img_url=url,
                news_id=new_news.id
            )
            db.session.add(news_image)

        db.session.commit()
        return new_news, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)

def edit_news(news_id, name, description, descriptionSecond, image_urls):
    news_item = News.query.get(news_id)
    if news_item is None:
        return None, "Новину не знайдено"

    try:
        if name is None:
            name = news_item.name

        if description is None:
            description = news_item.description

        if descriptionSecond is None:
            descriptionSecond = news_item.descriptionSecond

        if image_urls is None or len(image_urls) == 0:
            image_urls = [img.img_url for img in news_item.images]

        news_item.name = name
        news_item.description = description
        news_item.descriptionSecond = descriptionSecond
        
        # Видаляємо старі зображення
        NewsImage.query.filter_by(news_id=news_id).delete()
        
        # Додаємо нові
        for url in image_urls:
            news_image = NewsImage(
                img_url=url,
                news_id=news_id
            )
            db.session.add(news_image)

        db.session.commit()
        return news_item, None # Повертаємо оновлений об'єкт
    except Exception as e:
        db.session.rollback()
        return None, str(e)
from app.models.news import News
from app.models.news import NewsImage  
from .. import db 

def get_news():
    news_items = News.query.all()
    res=[]
    for item in news_items:
        res.append({
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "descriptionSecond": item.descriptionSecond,
            "images": [img.img_url for img in item.images]
        })

    print(res)
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
    db.session.delete(item)
    db.session.commit()
    return True

def add_news(name, description, descriptionSecond, image_urls):
    new_news = News(
        name=name,
        description=description,
        descriptionSecond=descriptionSecond
    )
    db.session.add(new_news)
    db.session.commit()

    for url in image_urls:
        news_image = NewsImage(
            img_url=url,
            news_id=new_news.id
        )
        db.session.add(news_image)

    db.session.commit()
    return new_news

def edit_news(news_id, name, description, descriptionSecond, image_urls):
    news_item = News.query.get(news_id)
    if news_item is None:
        return False

    news_item.name = name
    news_item.description = description
    news_item.descriptionSecond = descriptionSecond

    NewsImage.query.filter_by(news_id=news_id).delete()

    for url in image_urls:
        news_image = NewsImage(
            img_url=url,
            news_id=news_id
        )
        db.session.add(news_image)

    db.session.commit()
    return True

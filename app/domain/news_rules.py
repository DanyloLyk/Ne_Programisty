from app.models.news import News
from app.models.news import NewsImage   

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
    from .. import db
    db.session.delete(item)
    db.session.commit()
    return True

def add_news(name, description, descriptionSecond, image_urls):
    from .. import db
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


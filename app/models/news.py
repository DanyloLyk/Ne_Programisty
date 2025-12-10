from .. import db


class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300), nullable=False)
    descriptionSecond = db.Column(db.String(300), nullable=False)
    images = db.relationship('NewsImage', back_populates='news', lazy=True, cascade="all, delete-orphan")
    def __repr__(self):
        return f'<News {self.name}>'

class NewsImage(db.Model):
    __tablename__ = 'news_image'
    id = db.Column(db.Integer, primary_key=True)
    img_url = db.Column(db.String(255), nullable=False)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'), nullable=False)
    news = db.relationship('News', back_populates='images')

    def __repr__(self):
        return f'<NewsImage {self.img_url}>'
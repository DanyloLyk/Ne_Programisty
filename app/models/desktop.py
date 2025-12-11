from .. import db

class Desktop(db.Model):
    __tablename__ = 'desktop'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(255), nullable=False)
    def to_dict(self):  
        """Перетворює об'єкт у словник для відправки через API"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "image": self.image
        }
    def __repr__(self):
        return f'<Desktop {self.name}>'
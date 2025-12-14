from .. import db


class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    user = db.relationship('User', backref=db.backref('feedback', lazy='dynamic'))
    def to_dict(self):
        """Перетворює відгук у словник для API"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "user_id": self.user_id,
            "user": {
                "id": self.user.id,
                "nickname": self.user.nickname,
                "email": self.user.email
            } if self.user else None,
            # Конвертуємо дату в рядок, щоб JSON не лаявся
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    def __repr__(self):
        return f'<Feedback {self.title}>'
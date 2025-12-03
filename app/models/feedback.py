from .. import db


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    user = db.relationship('User', backref=db.backref('feedbacks', lazy='dynamic'))
    def __repr__(self):
        return f'<Feedback {self.title}>'
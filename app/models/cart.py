from .. import db
from datetime import datetime, timezone

class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)

    #user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_id = db.Column(db.Integer)
    item_id = db.Column(db.Integer, db.ForeignKey('desktop.id'), nullable=False)

    quantity = db.Column(db.Integer, default=1, nullable=False)

    # Relationships (optional but very useful)
    #user = db.relationship('User', backref='cart_items', lazy=True)
    item = db.relationship('Desktop', backref='in_carts', lazy=True)

    def __repr__(self):
        return f'<CartItem user={self.user_id} item={self.item_id} qty={self.quantity}>'
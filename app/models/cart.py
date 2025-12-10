from .. import db


class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('desktop.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)

    user = db.relationship('User', backref='cart_items', lazy='select')
    item = db.relationship('Desktop', backref='in_carts', lazy='select')

    def __repr__(self):
        return f'<CartItem user={self.user_id} item={self.item_id} qty={self.quantity}>'
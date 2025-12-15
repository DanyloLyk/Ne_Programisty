from .. import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'

    PRIVILEGE_TIERS = {
        'Default': {'label': 'Default', 'discount_percent': 0, 'badge_class': 'secondary'},
        'Gold': {'label': 'Gold', 'discount_percent': 5, 'badge_class': 'warning'},
        'Diamond': {'label': 'Diamond', 'discount_percent': 10, 'badge_class': 'info'},
        'VIP': {'label': 'VIP', 'discount_percent': 20, 'badge_class': 'purple'},
    }

    ALLOWED_STATUSES = {'User', 'Admin', 'Moder'}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nickname = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='User')
    privilege = db.Column(db.String(20), default='Default')

    # 👇 ВАЖЛИВО: Каскадне видалення зв'язаних даних 👇
    # Якщо видаляємо User -> видаляємо його Orders, CartItems, Feedbacks
    orders = db.relationship('Order', backref='user', lazy=True, cascade="all, delete-orphan")
    feedbacks = db.relationship('Feedback', backref='user', lazy=True, cascade="all, delete-orphan")
    cart_items = db.relationship('CartItem', backref='user', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nickname': self.nickname,
            'email': self.email,
            'status': self.status,
            'privilege': self.privilege,
            'privilege_label': self.privilege_label,
            'discount_percent': self.discount_percent
        }

    @property
    def privilege_info(self):
        return self.PRIVILEGE_TIERS.get(self.privilege, self.PRIVILEGE_TIERS['Default'])

    @property
    def privilege_label(self):
        return self.privilege_info['label']

    @property
    def discount_percent(self):
        return self.privilege_info['discount_percent']

    @property
    def discount_multiplier(self):
        percent = self.discount_percent
        return round(1 - (percent / 100), 2) if percent else 1.0

    def ensure_valid_levels(self):
        updated = False
        if self.status not in self.ALLOWED_STATUSES:
            self.status = 'User'
            updated = True
        if self.privilege not in self.PRIVILEGE_TIERS:
            self.privilege = 'Default'
            updated = True
        return updated

    def __repr__(self):
        return f"<User {self.nickname}>"
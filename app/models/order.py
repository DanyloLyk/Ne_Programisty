from .. import db
from sqlalchemy.orm import validates

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # <-- тільки один раз
    user = db.relationship("User", backref="orders")  # <-- зв’язок з User
    
    total_amount = db.Column(db.Float, nullable=False)  # Загальна сума замовлення
    status = db.Column(db.String(50), default='In process', nullable=False)  # completed, cancelled, etc.

    def to_dict(self):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'total_amount': self.total_amount,
            'status': self.status,
            'items': self.items, # JSON поле
            'created_at': self.created_at.isoformat() if hasattr(self, 'created_at') else None
        }

        # Додаємо дані про юзера, якщо він є
        if self.user:
            data['user'] = {
                'id': self.user.id,
                'nickname': self.user.nickname,
                'email': self.user.email
            }
        else:
            data['user'] = None
            
        return data
    
    # Список предметів замовлення: [{'item_id': int, 'quantity': int, 'discount': float (0.1-1.0)}]
    items = db.Column(db.JSON, nullable=False, default=list)
    
    @validates('items')
    def validate_items(self, key, items):
        """Валідація списку предметів замовлення"""
        if not isinstance(items, list):
            raise ValueError("items повинен бути списком")
        
        if len(items) == 0:
            raise ValueError("items не може бути порожнім")
        
        required_keys = {'item_id', 'quantity', 'discount'}
        
        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                raise ValueError(f"Елемент {idx} повинен бути словником")
            
            # Перевірка наявності всіх необхідних ключів
            item_keys = set(item.keys())
            if not required_keys.issubset(item_keys):
                missing = required_keys - item_keys
                raise ValueError(f"Елемент {idx} не містить обов'язкових ключів: {missing}")
            
            # Валідація item_id
            if not isinstance(item['item_id'], int) or item['item_id'] <= 0:
                raise ValueError(f"Елемент {idx}: item_id повинен бути додатнім цілим числом")
            
            # Валідація quantity
            if not isinstance(item['quantity'], int) or item['quantity'] <= 0:
                raise ValueError(f"Елемент {idx}: quantity повинен бути додатнім цілим числом")
            
            # Валідація discount
            discount = item['discount']
            if not isinstance(discount, (int, float)):
                raise ValueError(f"Елемент {idx}: discount повинен бути числом")
            
            discount_float = float(discount)
            if not (0.1 <= discount_float <= 1.0):
                raise ValueError(f"Елемент {idx}: discount повинен бути в діапазоні від 0.1 до 1.0")
            
            # Оновлюємо значення discount на float для консистентності
            item['discount'] = discount_float
        
        return items
    
    @staticmethod
    def add_order(user_id, cart_items, discount=1.0):
        """
        Створює замовлення з кошика користувача
        
        Args:
            user_id: ID користувача
            cart_items: Список CartItem об'єктів
            discount: Загальна знижка на замовлення (0.1-1.0), за замовчуванням 1.0 (без знижки)
        
        Returns:
            Order: Створене замовлення
        """
        if not cart_items or len(cart_items) == 0:
            raise ValueError("Кошик порожній, неможливо створити замовлення")
        
        # Валідація discount
        discount_float = float(discount)
        if not (0.1 <= discount_float <= 1.0):
            raise ValueError("discount повинен бути в діапазоні від 0.1 до 1.0")
        
        # Формуємо список items для замовлення
        order_items = []
        total_amount = 0.0
        
        for cart_item in cart_items:
            # Отримуємо товар для отримання поточної ціни
            desktop = cart_item.item
            if not desktop:
                raise ValueError(f"Товар з id={cart_item.item_id} не знайдено")
            
            # Конвертуємо ціну в число, видаляючи пробіли та коми
            price_str = str(desktop.price).replace(' ', '').replace(',', '.')
            price = float(price_str) if price_str else 0.0
            
            # Розраховуємо суму з урахуванням знижки
            item_total = price * cart_item.quantity * discount_float
            
            order_items.append({
                'item_id': cart_item.item_id,
                'quantity': cart_item.quantity,
                'discount': discount_float
            })
            
            total_amount += item_total
        
        # Створюємо замовлення
        order = Order(
            user_id=user_id,
            total_amount=round(total_amount, 2),
            items=order_items,
            status='In process'
        )
        
        return order
    
    def __repr__(self):
        return f'<Order id={self.id} user={self.user_id} total={self.total_amount}>'


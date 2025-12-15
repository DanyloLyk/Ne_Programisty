from .. import db
from sqlalchemy.orm import validates
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    
    # 👇 UNCOMMENTED THIS LINE. This is required for the relationship to work.
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # The backref="orders" is handled by the User model's relationship, so we don't need
    # to define a relationship here unless we want specific loading behavior.
    
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='In process', nullable=False)
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Список предметів: [{'item_id': 1, 'quantity': 2, 'discount': 1.0}]
    items = db.Column(db.JSON, nullable=False, default=list)

    def to_dict(self):
        from app.models.desktop import Desktop 
        
        enriched_items = []
        
        # Перебираємо збережені items (це JSON з бази)
        for item in self.items:
            item_data = item.copy()
            
            # Дістаємо актуальні дані про товар
            product = Desktop.query.get(item['item_id'])
            
            if product:
                item_data['name'] = product.name
                # Оскільки у Desktop price це Float, конвертація str() не обов'язкова, 
                # але для надійності залишимо float()
                price_val = float(product.price)
                item_data['price'] = price_val
                
                # Рахуємо суму: Ціна * Кількість * Знижка
                discount = float(item.get('discount', 1.0))
                quantity = int(item['quantity'])
                
                item_data['sum'] = round(price_val * quantity * discount, 2)
            else:
                # Якщо товар видалили з магазину, щоб історія не ламалась
                item_data['name'] = "Товар видалено"
                item_data['price'] = 0.0
                item_data['sum'] = 0.0
            
            enriched_items.append(item_data)

        data = {
            'id': self.id,
            'user_id': self.user_id,
            'total_amount': self.total_amount,
            'status': self.status,
            'items': enriched_items,
            # Тепер created_at точно існує
            'created_at': self.created_at.isoformat() if self.created_at else datetime.now().isoformat()
        }

        # Додаємо інфо про юзера, якщо є зв'язок
        if hasattr(self, 'user') and self.user:
            data['user'] = {
                'id': self.user.id,
                'nickname': self.user.nickname,
                'email': self.user.email
            }
        else:
            data['user'] = None
            
        return data
    
    @validates('items')
    def validate_items(self, key, items):
        if not isinstance(items, list):
            raise ValueError("items повинен бути списком")
        if len(items) == 0:
            raise ValueError("items не може бути порожнім")
        
        required_keys = {'item_id', 'quantity', 'discount'}
        
        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                raise ValueError(f"Елемент {idx} повинен бути словником")
            
            item_keys = set(item.keys())
            if not required_keys.issubset(item_keys):
                raise ValueError(f"Елемент {idx} не містить ключів: {required_keys - item_keys}")
            
            if not isinstance(item['item_id'], int) or item['item_id'] <= 0:
                raise ValueError(f"Елемент {idx}: item_id має бути > 0")
            
            if not isinstance(item['quantity'], int) or item['quantity'] <= 0:
                raise ValueError(f"Елемент {idx}: quantity має бути > 0")
            
            # Приводимо discount до float
            try:
                discount_float = float(item['discount'])
            except (ValueError, TypeError):
                raise ValueError(f"Елемент {idx}: discount має бути числом")

            if not (0.0 <= discount_float <= 1.0):
                raise ValueError(f"Елемент {idx}: discount має бути від 0.0 до 1.0")
            
            item['discount'] = discount_float
        
        return items
    
    @staticmethod
    def add_order(user_id, cart_items, discount=1.0):
        if not cart_items:
            raise ValueError("Кошик порожній")
        
        discount_float = float(discount)
        order_items = []
        total_amount = 0.0
        
        for cart_item in cart_items:
            desktop = cart_item.item
            if not desktop:
                continue # Або raise error, якщо критично
            
            price = float(desktop.price)
            item_total = price * cart_item.quantity * discount_float
            
            order_items.append({
                'item_id': cart_item.item_id,
                'quantity': cart_item.quantity,
                'discount': discount_float
            })
            
            total_amount += item_total
        
        return Order(
            user_id=user_id,
            total_amount=round(total_amount, 2),
            items=order_items,
            status='In process'
        )
    
    def __repr__(self):
        return f'<Order id={self.id} user={self.user_id}>'
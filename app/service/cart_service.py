from ..domain.cart_rules import get_cart_items_for_user, get_item_in_cart
from ..models.cart import CartItem
from ..models.desktop import Desktop
from .. import db
# Імпорт get_cart_items_for_user був видалений, оскільки він більше не потрібен (ми уніфікували на детальний кошик)

class CartService:
    
    # 1. Уніфікована функція отримання товарів (зроблена приватною)
    @staticmethod
    def __get_cart_items(user_id: int) -> list[dict] | None:
        """
        Повертає детально всі товари в кошику для заданого користувача (уніфіковано).
        Використовує функцію 'get_cart_items_for_user' з домену.
        
        Args:
            user_id: ID користувача
            
        Returns:
            list[dict] | None: Деталізований список товарів або None.
        """
        # Використовуємо функцію з домену, яка повертає деталізований кошик
        items = get_cart_items_for_user(user_id)
        if not items:
            return None
        return items
    
    # 2. Видалено старий get_detailed_cart_items, його функціонал тепер у __get_cart_items
    
    @staticmethod
    def __get_cart_total(user_id: int) -> float:
        """
        Обчислює загальну вартість товарів у кошику користувача.
        
        Args:
            user_id: ID користувача
        
        Returns:
            float: Загальна вартість товарів у кошику
        """
        # Використовуємо уніфікований метод для отримання деталізованих товарів
        items = CartService.__get_cart_items(user_id) 
        if not items:
            return 0.0

        total = 0.0
        for item in items:
            # Припускаємо, що структура тепер має ключ 'item_details' (як ми вирішили раніше)
            # або 'item' (як у вашому старому коді). Я залишаю 'item', як у вашому прикладі.
            if item.get('item') and item['item'].get('total_price') is not None:
                price_for_order = item['item']['total_price']
                total += price_for_order
        return total
    
    @staticmethod
    def get_cart(user_id: int) -> dict:
        """
        Повертає деталі кошика користувача, включаючи ТІЛЬКИ ДЕТАЛІЗОВАНІ товари та загальну вартість.
        
        Args:
            user_id: ID користувача
        Returns:
            dict: Деталі кошика з товарами та загальною вартістю
        """
        # Тепер items завжди повертає деталізований кошик
        items = CartService.__get_cart_items(user_id)
        total = CartService.__get_cart_total(user_id)
        if not items:
            items = []
        return {
            'items': items,
            'total': total
        }
    
    @staticmethod
    def add_item_to_cart(user_id: int, item_id: int, quantity: int = 1) -> CartItem:
        """
        Додає товар до кошика користувача.
        
        Args:
            user_id: ID користувача
            item_id: ID товару
            quantity: Кількість товару, за замовчуванням 1
        
        Returns:
            CartItem: Доданий елемент кошика.
        
        Raises:
            ValueError: Якщо товар з item_id не знайдено.
        """
        # Перевіряємо, чи існує товар (логіка залишилася без змін)
        item = Desktop.query.get(item_id)
        if not item:
            raise ValueError(f"Товар з id={item_id} не знайдено")
        
        # Використовуємо допоміжну функцію get_item_in_cart з домену
        cart_item = get_item_in_cart(user_id, item_id)
        
        if cart_item:
            # Якщо товар уже є, оновлюємо кількість
            CartService.update_item_quantity(user_id, item_id, cart_item.quantity + quantity)
        else:
            # Якщо товару немає, створюємо новий CartItem
            cart_item = CartItem(user_id=user_id, item_id=item_id, quantity=quantity)
            db.session.add(cart_item)
            
        db.session.commit()
        return cart_item

    @staticmethod
    def remove_item_from_cart(user_id: int, item_id: int) -> bool:
        """
        Видаляє товар з кошика користувача.
        
        Args:
            user_id: ID користувача
            item_id: ID товару
        
        Returns:
            bool: True, якщо товар було видалено, інакше False
        """
        # Використовуємо допоміжну функцію get_item_in_cart з домену
        cart_item = get_item_in_cart(user_id, item_id)
        if cart_item:
            db.session.delete(cart_item)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def clear_cart(user_id: int) -> None:
        """
        Очищає кошик користувача.
        
        Args:
            user_id: ID користувача
        """
        # Тут можна використовувати прямий запит до моделі, як було у вас
        CartItem.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        
    @staticmethod
    def update_item_quantity(user_id: int, item_id: int, quantity: int) -> bool:
        """
        Оновлює кількість товару в кошику користувача.
        
        Args:
            user_id: ID користувача
            item_id: ID товару
            quantity: Нова кількість товару
        
        Returns:
            bool: True, якщо кількість було оновлено, інакше False
        """
        # Використовуємо допоміжну функцію get_item_in_cart з домену
        cart_item = get_item_in_cart(user_id, item_id)
        if cart_item:
            cart_item.quantity = quantity
            db.session.commit()
            return True
        return False
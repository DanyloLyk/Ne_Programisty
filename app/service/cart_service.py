from requests import get
from ..domain.cart_rules import get_cart_items_for_user, get_detailed_cart_items_for_user, get_item_in_cart
from ..models.cart import CartItem
from ..models.desktop import Desktop
from .. import db

class CartService:
    @staticmethod
    def __get_cart_items(user_id: int) -> list[dict] | None:
        """
        Повертає всі товари в кошику для заданого користувача.
        
        user_id: ID користувача
        """
        res = get_cart_items_for_user(user_id)
        if not res:
            return None
        return res
    
    def __get_deteailed_cart_items(user_id: int) -> list[CartItem] | None:
        """
        Повертає детально всі товари в кошику для заданого користувача.
        
        user_id: ID користувача
        """
        items = get_detailed_cart_items_for_user(user_id)
        if not items:
            return None
        return items
    
    @staticmethod
    def __get_cart_total(user_id: int) -> float:
        """
        Обчислює загальну вартість товарів у кошику користувача.
        
        Args:
            user_id: ID користувача
        
        Returns:
            float: Загальна вартість товарів у кошику
        """
        items = CartService.__get_cart_items(user_id)
        if not items:
            return 0.0

        total = 0.0
        for item in items:
            if item.get('item') and item['item'].get('price') is not None:
                price = float(str(item['item']['price']).replace(' ', '').replace(',', '.'))
                total += price * item.get('quantity', 0)
        return total
    
    @staticmethod
    def get_cart(user_id: int) -> dict:
        """
        Повертає деталі кошика користувача, включаючи товари та загальну вартість.
        
        Args:
            user_id: ID користувача
        Returns:
            dict: Деталі кошика з товарами та загальною вартістю
        """
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
            CartItem: Доданий елемент кошика
        """
        
            # Перевіряємо, чи існує товар
        item = Desktop.query.get(item_id)
        if not item:
            raise ValueError(f"Товар з id={item_id} не знайдено")
        
        
        cart_item = get_item_in_cart(user_id, item_id)
        if cart_item:
            CartService.update_item_quantity(user_id, item_id, cart_item.quantity + quantity)
        else:
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
        cart_item = get_item_in_cart(user_id, item_id)
        if cart_item:
            cart_item.quantity = quantity
            db.session.commit()
            return True
        return False
from app.models.cart import CartItem
# Припускаємо, що тут також імпортується об'єкт db, якщо він використовується в інших функціях сервісу

def get_cart_items_for_user(user_id: int) -> list[dict] | None:
    """
    Повертає детально всі товари в кошику для заданого користувача.
    (Уніфікована функція, яка завжди повертає деталі товару).

    Args:
        user_id: ID користувача

    Returns:
        list[dict] | None: Список позицій кошика з деталями товару, або None, якщо кошик порожній.
    """
    # 1. Запит до бази даних
    # Завантажуємо всі позиції кошика для користувача
    # Припускаємо, що модель CartItem має зв'язок `item` до моделі Item
    items = CartItem.query.filter_by(user_id=user_id).all()
    
    if not items:
        return None
        
    res = []
    
    # 2. Обробка та форматування даних
    for item in items:
        # Визначаємо ціну та обчислюємо загальну ціну, обробляючи можливі None або неправильний формат
        price = 0.0
        item_details = None
        
        if item.item:
            try:
                # Очищення та конвертація ціни (як у вашому оригінальному коді)
                raw_price = str(item.item.price).replace(' ', '').replace(',', '.')
                price = float(raw_price) if item.item.price is not None else 0.0
            except (ValueError, TypeError):
                # Обробка випадку, коли ціна має непередбачуваний формат
                price = 0.0 
            
            total_price = price * item.quantity
            
            item_details = {
                'id': item.item.id,
                'name': item.item.name,
                'description': item.item.description,
                'price': price,
                'image': item.item.image,
                'total_price': total_price  # Ціна за всю кількість цього товару
            }
        
        # 3. Формування кінцевого об'єкта позиції кошика
        res.append({
            'id': item.id,            # ID самої позиції в кошику (CartItem ID)
            'user_id': item.user_id,
            'item_id': item.item_id,
            'quantity': item.quantity,
            'item_details': item_details # Тепер деталі товару знаходяться в окремому ключі 'item_details'
        })
        
    return res

def get_item_in_cart(user_id: int, item_id: int) -> CartItem | None:
    """
    Повертає об'єкт CartItem у кошику для заданого користувача та товару.
    
    Args:
        user_id: ID користувача
        item_id: ID товару
        
    Returns:
        CartItem | None: Об'єкт CartItem, якщо знайдено, інакше None.
    """
    # Ця функція не змінюється, оскільки вона повертає об'єкт моделі
    item = CartItem.query.filter_by(user_id=user_id, item_id=item_id).first()
    return item
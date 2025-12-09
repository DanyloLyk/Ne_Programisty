from app.models.cart import CartItem

def get_detailed_cart_items_for_user(user_id: int) -> list[dict] | None:
    """
    Повертає детально всі товари в кошику для заданого користувача.
    
    user_id: ID користувача
    """
    items = CartItem.query.filter_by(user_id = user_id).all()
    if not items:
        return None
    res = []
    for item in items:
        res.append({
            'id': item.id,
            'user_id': item.user_id,
            'item_id': item.item_id,
            'quantity': item.quantity,
            'item': {
                'id': item.item.id,
                'name': item.item.name,
                'description': item.item.description,
                'price': float(str(item.item.price).replace(' ', '').replace(',', '.')) if item.item.price is not None else 0.0,
                'image': item.item.image
            } if item.item else None
        })
    return res

def get_cart_items_for_user(user_id: int) -> list[dict] | None:
    """
    Повертає всі товари в кошику для заданого користувача.
    
    user_id: ID користувача
    """
    items = get_detailed_cart_items_for_user(user_id)
    if not items:
        return None
    res = []
    for item in items:
        res.append({
            'id': item['id'],
            'user_id': item['user_id'],
            'item_id': item['item_id'],
            'quantity': item['quantity']
        })
    return res

def get_item_in_cart(user_id: int, item_id: int) -> CartItem | None:
    """
    Повертає товар у кошику для заданого користувача та товару.
    
    user_id: ID користувача
    item_id: ID товару
    """
    item = CartItem.query.filter_by(user_id=user_id, item_id=item_id).first()
    return item
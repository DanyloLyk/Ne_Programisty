from ..domain import order_rules

class OrdersService:
    # Допустимі статуси (краще винести в модель, але можна і тут)
    ALLOWED_STATUSES = {'In process', 'Completed', 'Shipped', 'Cancelled'}

    @staticmethod
    def get_all_orders():
        return order_rules.get_all_orders()

    @staticmethod
    def get_order(order_id):
        return order_rules.get_order_by_id(order_id)
    
    @staticmethod
    def get_orders(user_id):
        # Повертаємо список словників для контролера
        orders = order_rules.get_user_orders(user_id)
        return [order.to_dict() for order in orders]
    
    @staticmethod
    def add_order(user_id):
        return order_rules.create_order_from_cart(user_id)
    
    @staticmethod
    def edit_status_order(order_id, status):
        if not status:
            return None, "Статус не може бути порожнім"
            
        if status not in OrdersService.ALLOWED_STATUSES:
            return None, f"Недопустимий статус: '{status}'. Дозволені: {', '.join(OrdersService.ALLOWED_STATUSES)}"
            
        return order_rules.update_order_status(order_id, status)
    
    @staticmethod
    def delete_order(order_id):
        return order_rules.delete_order_by_id(order_id)
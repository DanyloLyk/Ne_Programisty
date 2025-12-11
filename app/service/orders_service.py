from app.domain.order_rules import get_all_orders, get_orders, add_order, get_order, edit_order, delete_order

class OrdersService:
    @staticmethod
    def get_all_orders():
        return get_all_orders()

    @staticmethod
    def get_order(order_id):
        return get_order(order_id)
    
    @staticmethod
    def get_orders(user_id):
        orders = get_orders(user_id)
        res = []
        for order in orders:
            res.append(order.to_dict())
        return res
    
    @staticmethod
    def add_order(user_id):
        return add_order(user_id)
    
    @staticmethod
    def edit_status_order(order_id, status: str | None = None):
        current_status = get_order(order_id).status
        if status is current_status:
            status = current_status
        if status is "":
            status = None
        if status not in ['In process', 'Going', 'Completed', 'Cancelled'] and status is not None:
            return False, f"Недопустимий статус замовлення: '{status}', допустимі: 'In process', 'Going', 'Completed', 'Cancelled', поточний: {current_status}"
        return edit_order(order_id, status)
    
    @staticmethod
    def delete_order(order_id):
        return delete_order(order_id)
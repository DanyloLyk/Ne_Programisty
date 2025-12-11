from app.domain.order_rules import get_all_orders, get_order, add_order

class OrdersService:
    @staticmethod
    def get_all_orders():
        return get_all_orders()

    @staticmethod
    def get_order(user_id):
        return get_order(user_id)
    
    @staticmethod
    def add_order(user_id):
        return add_order(user_id)
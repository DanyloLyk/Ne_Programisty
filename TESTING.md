# TESTING

## Unit tests
- test_cart_rules.py — перевірка логіки кошика
- test_user_rules.py — валідація користувачів

## Integration tests
- test_api_cart.py — API кошика
- test_api_orders.py — оформлення замовлення

## Run tests
pytest
pytest --cov=app --cov-report=html

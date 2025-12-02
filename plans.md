# ⬇️ **КОПІЮЙ ЦЕ (ЦЕ СИРИЙ MARKDOWN, БЕЗ ЖОДНИХ СТИЛІВ ЧАТУ)**

# 📐 Схематичне представлення архітектури

Ми вводимо три основні рівні, які будуть взаємодіяти між собою:

| Рівень (Layer)         | Компоненти в коді      | Обов'язки                                             | Залежності                          |
|------------------------|-------------------------|--------------------------------------------------------|--------------------------------------|
| **Presentation**       | `app/routes.py`         | Прийом HTTP-запитів, повернення JSON/HTML.            | Залежить від Service Layer          |
| **Service**            | `app/services/`         | Керування транзакціями БД, координація BLL.           | Залежить від BLL та DAL             |
| **Business Logic & DAL** | `app/models/` + `app/domain/` | Бізнес-правила, розрахунки, доступ до БД.              | Не залежить від Presentation/Service |

# 📦 План реструктуризації вашого проекту

Нам потрібно створити дві нові директорії всередині вашої існуючої папки `app/`:

1. `app/domain/` — для чистої бізнес-логіки та правил.  
2. `app/services/` — для сервісних класів, що керують транзакціями.


# 🔧 Крок 1: Оновлення структури файлів

Ваша нова структура проекту буде виглядати так:
```
project/
├── app.py                  # Основний файл запуску Flask
└── app/
├── domain/             # НОВИНКА: Чиста бізнес-логіка/правила
│   ├── cart_rules.py
│   └── order_rules.py
├── models/             # Core Layer / Data Access Layer (DAL)
│   ├── cart.py         # Моделі SQLAlchemy
│   ├── desktop.py
│   └── ... (інші моделі)
├── services/           # НОВИНКА: Сервісний рівень (Transaction Manager)
│   ├── cart_service.py
│   └── order_service.py
├── routes.py           # Presentation Layer (Тонкі маршрути API та HTML)
├── static/
├── templates/
└── utils.py

```

# 🔄 Крок 2: Перенесення логіки в нові рівні

## A. Core Layer (`app/models/`)

Залишається майже без змін.  
Це просто визначення ваших класів SQLAlchemy (`db.Model`).  
Вони є основою для доступу до даних.

## B. Business Logic Layer (`app/domain/`)

Створіть тут функції або класи, які інкапсулюють правила.  
Вони можуть використовувати моделі з `app/models/` для запитів до БД.

### `app/domain/cart_rules.py`:

```python
from app.models.cart import CartItem
from app.models.desktop import Desktop # Товари

def get_detailed_cart_items_for_user(user_id):
    """
    Правило: Отримати всі деталі кошика з бази даних та підготувати їх.
    """
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    
    result = []
    for item in cart_items:
        # Тут ваша оригінальна логіка перетворення в словник
        result.append({
            'item_id': item.item_id,
            'quantity': item.quantity,
            'price': item.item.price # Доступ до пов'язаної моделі Desktop
            # ... інші поля
        })
    return result
````

## C. Service Layer (`app/services/`)

Створіть сервіс, який викликає правила з домену і керує транзакціями.

### `app/services/cart_service.py`:

```python
from app.domain.cart_rules import get_detailed_cart_items_for_user
from app.models.desktop import db # Потрібно для commit/rollback

class CartService:
    def get_cart_data(self, user_id):
        # Сервіс просто викликає логіку з Domain Layer
        data = get_detailed_cart_items_for_user(user_id)
        # Сервіс не робить тут commit, бо це просто GET-запит
        return data

    def add_item_transaction(self, user_id, item_id, quantity):
        """
        Приклад POST-запиту: Сервіс керує транзакцією.
        """
        try:
            # ... викликаємо правила валідації з domain ...
            # ... додаємо запис до БД використовуючи models ...
            db.session.commit() # Фіксація транзакції тут
            return True, "Item added"
        except Exception as e:
            db.session.rollback() # Відкат у разі помилки
            return False, str(e)
```

## D. Presentation Layer (`app/routes.py`)

Маршрути стають "тонкими" — вони просто викликають сервісний рівень.

### `app/routes.py`:

```python
from flask import render_template, jsonify, g, request
from app.services.cart_service import CartService
# ... імпорт інших сервісів ...

cart_service = CartService()

# --- Оригінальний HTML маршрут (все ще працює) ---
@app.route('/cart')
@login_required
def cart_html():
    user_id = g.current_user.id
    # Використовуємо той самий сервіс, що й API!
    cart_data = cart_service.get_cart_data(user_id) 
    # Рендеримо HTML
    return render_template('cart.html', carts=cart_data, ...)


# --- НОВИЙ REST API маршрут ---
@app.route('/api/v1/cart', methods=['GET'])
@login_required
def api_get_cart():
    user_id = g.current_user.id
    # Використовуємо той самий сервіс!
    cart_data = cart_service.get_cart_data(user_id)
    # Повертаємо JSON
    return jsonify(cart_data), 200

@app.route('/api/v1/cart/add', methods=['POST'])
@login_required
def api_add_to_cart():
    data = request.get_json()
    success, message = cart_service.add_item_transaction(g.current_user.id, ...)
    if success:
        return jsonify({'status': 'success', 'message': message}), 201
    else:
        return jsonify({'status': 'error', 'message': message}), 400
```

# 🎯 Переваги для вашої команди

1. **Чистота `routes.py`:**
   Файл маршрутів стає дуже легким для читання. Він займається лише HTTP-протоколом.

2. **Тестування:**
   Ви можете легко тестувати `cart_service.py` та `cart_rules.py` без запуску всього веб-сервера Flask.

3. **Поділ відповідальності:**
   Легко зрозуміти, де знаходяться правила (domain), а де — послідовність дій (services).

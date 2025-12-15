import os
from requests import get
from flask import current_app
from ..domain import desktop_rules

class DesktopService:
    
    @staticmethod
    def _is_image_valid(image_path):
        """
        Універсальна перевірка картинки.
        Розуміє і HTTP посилання, і локальні файли в папці static.
        """
        if not image_path:
            return True # Картинка не обов'язкова, це ок

        # 1. Якщо це зовнішнє посилання (http/https)
        if image_path.startswith(('http://', 'https://')):
            try:
                response = get(image_path, timeout=3)
                return response.status_code == 200
            except:
                return False
        
        # 2. Якщо це локальний шлях (наприклад, images/catalog4.jpg)
        else:
            # Отримуємо повний шлях до папки static на сервері
            static_folder = current_app.static_folder 
            # Склеюємо: /var/www/app/static + images/catalog4.jpg
            full_path = os.path.join(static_folder, image_path)
            
            # Перевіряємо, чи існує файл фізично
            return os.path.exists(full_path)

    @staticmethod
    def get_all_desktops_service():
        return desktop_rules.get_desktops()

    @staticmethod
    def get_desktop_details_service(desktop_id):
        desktop = desktop_rules.get_desktop_by_id(desktop_id)
        if not desktop:
            return None, "Товар не знайдено"
        return desktop, None

    @staticmethod
    def create_desktop_service(data):
        name = data.get('name')
        price = data.get('price')
        image = data.get('image')
        description = data.get('description')

        if not name or len(name) < 3:
            return None, "Назва занадто коротка (мінімум 3 символи)"

        try:
            # Прибираємо пробіли, якщо ціна прийшла рядком "45 000"
            if isinstance(price, str):
                price = float(price.replace(' ', ''))
            elif price is not None:
                price = float(price)
            else:
                return None, "Ціна є обов'язковою"
                
            if price <= 0:
                return None, "Ціна має бути більше 0"
        except (ValueError, TypeError):
            return None, "Невірний формат ціни"

        # 👇 ВИКОРИСТОВУЄМО НОВИЙ ВАЛІДАТОР
        if image and not DesktopService._is_image_valid(image):
             return None, f"Зображення '{image}' не знайдено (перевірте URL або наявність файлу в static)"

        return desktop_rules.add_desktop(name, description, price, image)

    @staticmethod
    def update_desktop_service(desktop_id, data):
        # Валідація ціни
        if 'price' in data:
            try:
                price_val = data['price']
                if isinstance(price_val, str):
                    price_val = float(price_val.replace(' ', ''))
                
                if float(price_val) <= 0:
                    return None, "Ціна має бути більше 0"
                
                # Оновлюємо значення в data, щоб передати чисте число
                data['price'] = price_val 
            except ValueError:
                return None, "Невірний формат ціни"

        # 👇 ВАЛІДАЦІЯ КАРТИНКИ ПРИ ОНОВЛЕННІ
        if 'image' in data:
            image_path = data['image']
            if image_path and not DesktopService._is_image_valid(image_path):
                return None, f"Зображення '{image_path}' не знайдено"

        return desktop_rules.edit_desktop_by_id(
            desktop_id,
            name=data.get('name'),
            description=data.get('description'),
            price=data.get('price'),
            image=data.get('image')
        )

    @staticmethod
    def delete_desktop_service(desktop_id):
        result = desktop_rules.delete_desktop_by_id(desktop_id)
        if result:
            return True, "Товар успішно видалено"
        return False, "Товар не знайдено"
from requests import get
from ..domain.desktop_rules import (get_desktops, get_desktop_by_id, add_desktop,delete_desktop_by_id,edit_desktop_by_id)
from ..models.desktop import Desktop
from .. import db

class DesktopService:
    @staticmethod
    def _is_image_url_valid(url):
        """Перевіряємо, чи посилання на картинку робоче (внутрішній метод)"""
        try:
            response = get(url, timeout=5) 
            return response.status_code == 200
        except:
            return False

    @staticmethod
    def get_all_desktops_service():
        """Просто отримуємо дані через правила"""
        return get_desktops()

    @staticmethod
    def get_desktop_details_service(desktop_id):
        """Отримуємо деталі конкретного товару"""
        desktop = get_desktop_by_id(desktop_id)
        if not desktop:
            return None, "Desktop not found"
        return desktop, None

    @staticmethod
    def create_desktop_service(data):
        """Валідація та створення"""
        name = data.get('name')
        price = data.get('price')
        image = data.get('image')
        description = data.get('description')
        try:
            if price is None:
                 return None, "Price is required"
            price = float(price)
            if price <= 0:
                return None, "Price must be greater than 0"
        except (ValueError, TypeError):
            return None, "Invalid price format"
        if not name or len(name) < 3:
            return None, "Name is too short (min 3 chars)"

        if image and not DesktopService._is_image_url_valid(image):
            return None, "Image URL is not accessible"

        new_desktop = add_desktop(name, description, price, image)
        
        if new_desktop:
            return new_desktop, None
        else:
            return None, "Database error during creation"

    @staticmethod
    def update_desktop_service(desktop_id, data):
        """Оновлення з валідацією"""
        existing = get_desktop_by_id(desktop_id)
        if not existing:
            return None, "Desktop not found"

        if 'price' in data:
            try:
                if float(data['price']) <= 0:
                    return None, "Price must be positive"
            except ValueError:
                return None, "Invalid price"

        updated_desktop = edit_desktop_by_id(
            desktop_id,
            name=data.get('name'),
            description=data.get('description'),
            price=data.get('price'),
            image=data.get('image')
        )
        
        return updated_desktop, None

    @staticmethod
    def delete_desktop_service(desktop_id):
        """Видалення"""
        result = delete_desktop_by_id(desktop_id)
        if result:
            return True, "Deleted successfully"
        return False, "Desktop not found or database error"
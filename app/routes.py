from flask import Blueprint, render_template
from .models.desktop import Desktop
from . import db
from .utils import download_image

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/catalog')
def catalog():
    initial_cards = [
        {"name": "iPad Pro", "description": "Для творчості", "price": 35000, "image": "https://geekach.com.ua/content/uploads/images/nastolnye-strategii.jpg"},
        {"name": "Xiaomi Pad 6", "description": "Баланс потужності", "price": 15000, "image": "https://geekach.com.ua/content/uploads/images/nastolnye-strategii.jpg"},
    ]

    for card in initial_cards:
        exists = Desktop.query.filter_by(name=card["name"]).first()
        if not exists:
            local_image = download_image(card["image"])
            new_desktop = Desktop(
                name=card["name"],
                description=card["description"],
                price=card["price"],
                image=local_image
            )
            db.session.add(new_desktop)

    db.session.commit()
    desktops = Desktop.query.all()
    return render_template("catalog.html", desktops=desktops)
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
    return render_template('catalog.html')

@main.route('/contacts')
def contacts():
    return render_template('contacts.html')

@main.route('/news')
def news():
    return render_template('news.html')
    initial_cards = [
        {"name": "Гра1", "description": "Опис гри 1", "price": 35000, "image": "https://geekach.com.ua/content/uploads/images/nastolnye-strategii.jpg"},
        {"name": "Гра2", "description": "Опис гри 2", "price": 15000, "image": "https://geekach.com.ua/content/uploads/images/nastolnye-strategii.jpg"},
        {"name": "Гра3", "description": "Опис гри 3", "price": 25000, "image": "https://geekach.com.ua/content/uploads/images/nastolnye-strategii.jpg"},
        {"name": "Гра4", "description": "Опис гри 4", "price": 45000, "image": "https://geekach.com.ua/content/uploads/images/nastolnye-strategii.jpg"},
        {"name": "Гра5", "description": "Опис гри 5", "price": 55000, "image": "https://geekach.com.ua/content/uploads/images/nastolnye-strategii.jpg"},
        {"name": "Гра6", "description": "Опис гри 6", "price": 65000, "image": "https://geekach.com.ua/content/uploads/images/nastolnye-strategii.jpg"},
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

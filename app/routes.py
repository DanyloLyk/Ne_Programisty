from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/catalog')
def catalog():
    cards = [
        {
            "image_url": "https://via.placeholder.com/300x200",
            "title": "iPad Pro",
            "description": "Для творчості та навчання",
            "price": "35000 грн"
        },
        {
            "image_url": "https://via.placeholder.com/300x200",
            "title": "Xiaomi Pad 6",
            "description": "Баланс ціни та потужності",
            "price": "15000 грн"
        }
    ]
    return render_template("catalog.html", cards=cards)
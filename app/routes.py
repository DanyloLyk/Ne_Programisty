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

@main.route('/news')
def news():
    return render_template('news.html')

@main.route('/contacts')
def contacts():
    return render_template('contacts.html')

@main.route('/catalog')
def catalog():


    db.session.commit()
    desktops = Desktop.query.all()
    return render_template("catalog.html", desktops=desktops)

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
    return render_template('catalog.html')

@main.route('/contacts')
def contacts():
    return render_template('contacts.html')

@main.route('/news')
def news():
    return render_template('news.html')
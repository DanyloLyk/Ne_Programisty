from flask import Blueprint, render_template
from .models.desktop import Desktop
from flask import request, jsonify
from . import db
from .models.feedback import Feedback
from .models.news import News, NewsImage

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/news')
def news():
    # --- ІНІЦІАЛІЗАЦІЯ ТІЛЬКИ ОДИН РАЗ ---
    #if not News.query.first():
    # --- seed_news_data()


    all_news = News.query.all()
    return render_template('news.html', news=all_news)

def seed_news_data():
    news_data = [
        News(
            name="Новинка: Гра “Стратегія 2025”",
            description="Випробуйте свої стратегічні навички у новій грі! \n Відкрийте для себе світ битв і дипломатії.",
            descriptionSecond=" Відкрийте для себе неймовірний світ “Стратегія 2025”! \n 🏰 Побудуйте власну імперію, використовуючи хитрість, стратегію та дипломатію 🤝. \n Кожна партія – нові виклики ⚔️ і можливість проявити свій стратегічний талант 🧠.",
            images=[
                NewsImage(img_url="images/news1.jpg"),
                NewsImage(img_url="images/news1-2.jpg"),
                NewsImage(img_url="images/news1-3.jpg"),
            ],
        ),
        News(
            name="Акція: -40% на популярні ігри",
            description="  Обмежений час! Знижки на топові \n настільні ігри цього тижня — поповніть колекцію за вигідною ціною.",
            descriptionSecond=" Поповніть колекцію настільних хітів зі знижкою 40% 🎉! \n “Catan”, “Ticket to Ride”, “Carcassonne” та інші стали ще доступнішими 🏷. \n Організовуйте вечори з друзями та сім’єю 👨‍👩‍👧‍👦. ",
            images=[
                NewsImage(img_url="images/news2.jpg"),
                NewsImage(img_url="images/news2-2.jpg"),
                NewsImage(img_url="images/news2-3.jpg"),
            ],
        ),
        News(
            name="Майстер-клас для гравців",
            description="Хочеш грати як професіонал? \n Приходь на наш безкоштовний майстер-клас і навчись новим тактикам!",
            descriptionSecond="Приходьте на живий майстер-клас 🎯. \n Отримайте поради від досвідчених геймерів, спробуйте нестандартні комбінації ходів 🔍 і відкрийте нові способи перемагати 🏆.",
            images=[
                NewsImage(img_url="images/news3.jpg"),
                NewsImage(img_url="images/news3-2.jpg"),
            ],
        ),
        News(
            name="Турнір з настільних ігор",
            description="Перевір свої стратегічні навички та виграй круті призи!",
            descriptionSecond="Щомісячний турнір для фанатів настільних ігор 🎲. \n Переможці отримають призи 🏆, сертифікати 📜 та бонуси 🎁.",
            images=[
                NewsImage(img_url="images/news4.jpg"),
                NewsImage(img_url="images/news4-2.jpg"),
            ],
        ),
        News(
            name="Нові настільні ігри у продажу",
            description="Нові пригоди та квести чекають на тебе!",
            descriptionSecond="Нові пригодницькі квести та кооперативні ігри вже чекають на тебе 🌟. \n Веселі вечори з друзями чи родиною 👨‍👩‍👧‍👦 гарантовані!",
            images=[
                NewsImage(img_url="images/news5.jpg"),
                NewsImage(img_url="images/news5-2.jpg"),
            ],
        ),
        News(
            name="Вечірка для геймерів",
            description="Приходь на тематичну вечірку та грай разом з іншими фанатами настільних ігор!",
            descriptionSecond="Приходь на тематичну вечірку у “Гральну Комору”! 🕹 \n Ігри, конкурси 🏆, призи 🎁 та весела компанія гарантовані 🤗. \n Випробуй свої навички в командних та індивідуальних турнірах ⚔️, отримай подарунки і нові знайомства 🤝.\n Це шанс провести час весело, активно та з користю 🎯, об’єднуючи геймерів у дружню спільноту!",
            images=[
                NewsImage(img_url="images/news6.jpg"),
                NewsImage(img_url="images/news6-2.jpg"),
                NewsImage(img_url="images/news6-3.jpg"),
            ],
        ),
    ]

    db.session.add_all(news_data)
    db.session.commit()
    print("✅ База новин заповнена.")


@main.route('/contacts')
def contacts():
    return render_template('contacts.html')

@main.route('/feedback')
def feedback():
    return render_template('feedback.html')


@main.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    try:
        # 1. Отримуємо JSON-дані, які надіслав JavaScript
        data = request.get_json()

        title = data.get('title')
        description = data.get('description')

        # 2. Валідація на стороні сервера (дуже важливо!)
        if not title or not description:
            # 'jsonify' створює JSON-відповідь, 400 - це код помилки "Bad Request"
            return jsonify({'success': False, 'error': 'Заголовок та опис є обов\'язковими.'}), 400

        if len(title) > 100 or len(description) > 300:
            return jsonify({'success': False, 'error': 'Перевищено ліміт символів.'}), 400

        # 3. Створюємо запис у БД
        new_feedback = Feedback(title=title, description=description)
        db.session.add(new_feedback)
        db.session.commit()

        # 4. Надсилаємо відповідь про успіх
        return jsonify({'success': True, 'message': 'Відгук додано!'}), 201

    except Exception as e:
        db.session.rollback()
        print(f"Помилка при збереженні відгуку: {e}")  # Логування помилки
        return jsonify({'success': False, 'error': 'Внутрішня помилка сервера.'}), 500


@main.route('/catalog')
def catalog():
    db.session.commit()
    desktops = Desktop.query.all()
    return render_template("catalog.html", desktops=desktops)

@main.route('/cart')
def cart():
    return render_template('cart.html', isFooter=False)

from datetime import datetime
from werkzeug.security import generate_password_hash

def seed_data(db):
    # Імпортуємо моделі всередині функції, щоб уникнути циклічних імпортів(Lazy imports)
    from .models.user import User
    from .models.desktop import Desktop
    from .models.feedback import Feedback
    from .models.news import News, NewsImage
    from .models.cart import CartItem
    from .models.order import Order
    
    print("🌱 Seeding database with demo data...")

    if User.query.first() is None:
        users = [
            User(
                nickname="cat",
                email="dann160309@gmail.com",
                password=generate_password_hash("123"),
                status="Admin",
                privilege="VIP"
            ),
            User(
                nickname="sobaka",
                email="sobaka@ukr.net",
                password=generate_password_hash("123"),
                status="Admin",
                privilege="Diamond"
            ),
            User(
                nickname="Ne_Programist1",
                email="ne_programist@gmail.com",
                password=generate_password_hash("Zv*47f0Yf#&FM5?Di-q=OMX@$?n<NC|4NkpIlLAW$x=kI[4\\#b"),
                status="User",
                privilege="Default"
            ),
            User(
                nickname="test_user",
                email="test_user@gmail.com",
                password=generate_password_hash("testpassword"),
                status="User",
                privilege="Default"
            ),
            User(
                nickname="Dima123",
                email="dima123@gmail.com",
                password=generate_password_hash("asdlkasjdkjaskdljlk2j1i3u123jhok_!kkpo"),
                status="Moder",
                privilege="Gold"
            ),
            User(
                nickname="alice",
                email="a123lica@com.ua",
                password=generate_password_hash("alicepassword"),
                status="User",
                privilege="Gold"
            )
        ]

        db.session.add_all(users)
        db.session.commit()

    if Desktop.query.first() is None:
        desktops = [
            Desktop(
                name="🪐 Зоряна Сага",
                description="Велика стратегічна гра з елементами дослідження та будівництва. Досліджуйте галактику, колонізуйте планети та формуйте космічну імперію. Глибокий геймплей і висока реіграбельність.",
                price=35000,
                image="images/star_saga.jpg" 
            ),
            Desktop(
                name="🏕️ Колонізатори Міфічних Земель",
                description="Побудуйте власну імперію на територіях, багатих ресурсами! Змагайтеся за контроль над лісами, горами та ріками. Ідеальна гра для 3–5 гравців.",
                price=15000,
                image="images/catalog2.jpg" 
            ),
            Desktop(
                name="⚔️ Королі та Загарбники",
                description="Станьте правителем королівства або лідером повстанців. Захоплюйте території, укладайте союзи та зраджуйте ворогів. Тактична гра з варіативністю сценаріїв.",
                price=25000,
                image="images/catalog3.jpg" 
            ),
            Desktop(
                name="🧙‍♂️ Гільдії Підземного Міста",
                description="Розвивайте свою гільдію в древньому місті, повному таємниць і магії. Комбінуйте здібності персонажів і відкривайте нові шляхи до перемоги!",
                price=45000,
                image="images/catalog4.jpg" 
            ),
            Desktop(
                name="🛡️ Епоха Героїв",
                description="Фентезійна гра з глибокою бойовою механікою та прокачуванням героїв. Рятуйте королівство від темних сил або станьте їхнім союзником.",
                price=55000,
                image="images/catalog5.jpg" 
            ),
            Desktop(
                name="🚀 Володарі Галактики",
                description="Масштабна космічна стратегія. Створюйте флот, укладайте міжзоряні договори та ведіть битви за ресурси. Підходить для досвідчених гравців.",
                price=65000,
                image="images/images/nastolnye-strategii.jpg" 
            ),
            Desktop(
                name="🐉 Легенди Драконових Печер",
                description="Вирушайте у небезпечну подорож крізь древні підземелля, де сплять дракони і приховані скарби. Збирайте команду героїв — воїнів, магів і шукачів пригод. Перемагайте монстрів, відкривайте таємниці стародавніх руїн і здобувайте легендарні артефакти.",
                price=40000,
                image="images/catalog9.jpg" 
            )
        ]

        db.session.add_all(desktops)
        db.session.commit()
    
    if Feedback.query.first() is None:
        feedbacks = [
            Feedback(
                title="Чудова гра!",
                description="Мені дуже сподобалась ця гра. Матеріал настільних ігор на найвищому рівні, а геймплей захоплюючий.",
                user_id=3,
                created_at=datetime.strptime('2025-01-15 12:30:00', '%Y-%m-%d %H:%M:%S')
            ),
            Feedback(
                title="Захоплюючий сюжет",
                description="Сюжет тримає в напрузі від початку до кінця. Рекомендую всім фанатам жанру.",
                user_id=6,
                created_at=datetime.strptime('2025-03-27 15:14:56', '%Y-%m-%d %H:%M:%S')
            ),
            Feedback(
                title="Відмінний геймплей",
                description="Геймплей дуже різноманітний і цікавий. Є над чим подумати.",
                user_id=4,
                created_at=datetime.strptime('2025-05-10 09:45:23', '%Y-%m-%d %H:%M:%S')
            ),
            Feedback(
                title="Персонал просто супер!",
                description="Чудове обслуговування і дуже уважний персонал. Відчуваєш себе як вдома.",
                user_id=3,
                created_at=datetime.strptime('2025-01-15 12:30:00', '%Y-%m-%d %H:%M:%S')
            ),
            Feedback(
                title="Сайт дуже зручний та інтуїтивний",
                description="Дуже сподобалась навігація по сайту. Легко знайти потрібну інформацію та оформити замовлення.",
                user_id=5,
                created_at=datetime.strptime('2025-03-27 15:14:56', '%Y-%m-%d %H:%M:%S')
            ),
            Feedback(
                title="Всім рекомендую)",
                description="Цей магазин просто знахідка для любителів настільних ігор. Великий вибір і приємні ціни.",
                user_id=2,
                created_at=datetime.strptime('2025-05-10 09:45:23', '%Y-%m-%d %H:%M:%S')
            )
        ]

        db.session.add_all(feedbacks)
        db.session.commit()

    if News.query.first() is None:
        news = [
            News(
                name="Новинка: Гра “Стратегія 2025”",
                description='''Випробуйте свої стратегічні навички у новій грі!" 
"Відкрийте для себе світ битв і дипломатії.
                    ''',
                descriptionSecond = '''Відкрийте для себе неймовірний світ “Стратегія 2025”! 
🏰 Побудуйте власну імперію, використовуючи хитрість, стратегію та дипломатію 🤝. 
Кожна партія – нові виклики ⚔️ і можливість проявити свій стратегічний талант 🧠.
                    ''',
            ),
            News(
                name="Акція: -40% на популярні ігри",
                description='''  Обмежений час! Знижки на топові 
 настільні ігри цього тижня — поповніть колекцію за вигідною ціною.
                    ''',
                descriptionSecond = ''' Поповніть колекцію настільних хітів зі знижкою 40% 🎉! 
 “Catan”, “Ticket to Ride”, “Carcassonne” та інші стали ще доступнішими 🏷. 
 Організовуйте вечори з друзями та сім’єю 👨‍👩‍👧‍👦. 
                    ''',
            ),
            News(
                name="Майстер-клас для гравців",
                description='''Хочеш грати як професіонал? 
 Приходь на наш безкоштовний майстер-клас і навчись новим тактикам!
                    ''',
                descriptionSecond = '''Приходьте на живий майстер-клас 🎯. 
 Отримайте поради від досвідчених геймерів, спробуйте нестандартні комбінації ходів 🔍 і відкрийте нові способи перемагати 🏆.
                    ''',
            ),
            News(
                name="Турнір з настільних ігор",
                description='''Перевір свої стратегічні навички та виграй круті призи! 
                    ''',
                descriptionSecond = '''Щомісячний турнір для фанатів настільних ігор 🎲. 
 Переможці отримають призи 🏆, сертифікати 📜 та бонуси 🎁.
                    ''',
            ),
            News(
                name="Нові настільні ігри у продажу",
                description='''Нові пригоди та квести чекають на тебе!
                    ''',
                descriptionSecond = '''Нові пригодницькі квести та кооперативні ігри вже чекають на тебе 🌟. 
 Веселі вечори з друзями чи родиною 👨‍👩‍👧‍👦 гарантовані!
                    ''',
            ),
            News(
                name="Вечірка для геймерів",
                description='''Приходь на тематичну вечірку та грай разом з іншими фанатами настільних ігор!
                    ''',
                descriptionSecond = '''Приходь на тематичну вечірку у “Гральну Комору”! 🕹 
 Ігри, конкурси 🏆, призи 🎁 та весела компанія гарантовані 🤗. 
 Випробуй свої навички в командних та індивідуальних турнірах ⚔️, отримай подарунки і нові знайомства 🤝.
 Це шанс провести час весело, активно та з користю 🎯, об’єднуючи геймерів у дружню спільноту!
                    ''',
            )
        ]

        db.session.add_all(news)
        db.session.commit()

        news_images = [
            NewsImage(
                img_url="images/news1.jpg",
                news_id=1
            ),
            NewsImage(
                img_url="images/news1-2.jpg",
                news_id=1
            ),
            NewsImage(
                img_url="images/news1-3.jpg",
                news_id=1
            ),
            NewsImage(
                img_url="images/news2.jpg",
                news_id=2
            ),
            NewsImage(
                img_url="images/news2-2.jpg",
                news_id=2
            ),
            NewsImage(
                img_url="images/news2-3.jpg",
                news_id=2
            ),
            NewsImage(
                img_url="images/news3.jpg",
                news_id=3
            ),
            NewsImage(
                img_url="images/news3-2.jpg",
                news_id=3
            ),
            NewsImage(
                img_url="images/news3-3.jpg",
                news_id=3
            ),
            NewsImage(
                img_url="images/news4.jpg",
                news_id=4
            ),
            NewsImage(
                img_url="images/news4-2.jpg",
                news_id=4
            ),
            NewsImage(
                img_url="images/news5.jpg",
                news_id=5
            ),
            NewsImage(
                img_url="images/news5-2.jpg",
                news_id=5
            ),
            NewsImage(
                img_url="images/news6.jpg",
                news_id=6
            ),
            NewsImage(
                img_url="images/news6-2.jpg",
                news_id=6
            ),
            NewsImage(
                img_url="images/news6-3.jpg",
                news_id=6
            )
        ]
        db.session.add_all(news_images)
        db.session.commit()

    if CartItem.query.first() is None:
        cart_items = [
            CartItem(
                user_id=2,
                item_id=5,
                quantity=3
            ),
            CartItem(
                user_id=2,
                item_id=3,
                quantity=23
            ),
            CartItem(
                user_id=4,
                item_id=3,
                quantity=1
            ),
            CartItem(
                user_id=3,
                item_id=1,
                quantity=56
            ),
            CartItem(
                user_id=1,
                item_id=3,
                quantity=2
            ),
            CartItem(
                user_id=2,
                item_id=6,
                quantity=10
            )
        ]

        db.session.add_all(cart_items)
        db.session.commit()

    if Order.query.first() is None:
        orders = [
            Order(
                user_id=1,
                total_amount=70000.0,
                status="In process",
                items = [{"item_id": 1, "quantity": 2, "discount": 1.0}, {"item_id": 4, "quantity": 1, "discount": 1.0}]
            ),
            Order(
                user_id=1,
                total_amount=9853450.4,
                status="Shipped",
                items = [{"item_id": 5, "quantity": 3, "discount": 0.8}, {"item_id": 6, "quantity": 1, "discount": 0.8}]
            ),
            Order(
                user_id=2,
                total_amount=208000,
                status="Completed",
                items = [{"item_id": 3, "quantity": 4, "discount": 0.9}]
            ),
            Order(
                user_id=5,
                total_amount=124000,
                status="Cancelled",
                items = [{"item_id": 4, "quantity": 6, "discount": 0.8}, {"item_id": 9, "quantity": 1, "discount": 0.95}]
            )
        ]

        db.session.add_all(orders)
        db.session.commit() 

    print("✅ Database seeded successfully!")
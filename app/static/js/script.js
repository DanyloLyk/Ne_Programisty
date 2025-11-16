window.onload = function() {
    const loaderWrapper = document.getElementById('loader-wrapper');
    const content = document.getElementById('page-content');
    const masonryGrid = document.querySelector('.row-cols-md-3'); // Елемент сітки Masonry

    if (content) {
        content.style.display = 'block';
    }
    if (masonryGrid && typeof Masonry !== 'undefined') {

        // Ручна ініціалізація Masonry.
        // Це вирішує проблему з "eval" та неправильним розрахунком при завантаженні.
        // Це ПОВИННО бути виконано після того, як контент стане видимим.
        new Masonry(masonryGrid, {
            itemSelector: '.col-md-4', // Селектор для окремих карток
            percentPosition: true,
            gutter: 16 // Проміжок g-4 приблизно дорівнює 16px
        });

        console.log("Masonry successfully initialized.");
    }
    setTimeout(() => {
        if (loaderWrapper) {
            // Клас 'hidden' повинен мати CSS-перехід для плавного зникнення
            loaderWrapper.classList.add('hidden');
        }
    }, 100);
};

document.addEventListener('DOMContentLoaded', function() {

    // Знаходимо кнопку та форму
    const submitBtn = document.getElementById('submit-btn');
    const form = document.getElementById('feedback-form');
    const messageDiv = document.getElementById('form-message');

    // Перевіряємо, чи ми взагалі на сторінці з цією формою
    if (submitBtn && form && messageDiv) {

        // Додаємо слухач події 'click' на кнопку
        submitBtn.addEventListener('click', function() {

            // 1. Збираємо дані з форми
            const titleInput = document.getElementById('title');
            const descriptionInput = document.getElementById('description');

            const title = titleInput.value;
            const description = descriptionInput.value;

            // 2. Проста валідація
            if (!title || !description) {
                messageDiv.textContent = 'Будь ласка, заповніть усі поля.';
                messageDiv.style.color = '#FACC15'; // Жовтий (попередження)
                return;
            }

            // 3. Блокуємо кнопку та показуємо завантаження
            submitBtn.disabled = true;
            submitBtn.textContent = 'Відправка...';
            messageDiv.textContent = '';
            messageDiv.style.color = '#fff';

            // 4. Асинхронний запит (AJAX) за допомогою Fetch API
            fetch('/submit_feedback', { // УВАГА: Це ваш URL у Flask!
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: title,
                    description: description
                })
            })
            .then(response => response.json()) // Очікуємо JSON-відповідь
            .then(data => {
                if (data.success) {
                    // Успіх!
                    messageDiv.textContent = 'Відгук успішно надіслано!';
                    messageDiv.style.color = '#28a745'; // Зелений (успіх)
                    form.reset(); // Очищуємо поля форми
                } else {
                    // Помилка, яку повернув сервер
                    messageDiv.textContent = 'Помилка: ' + (data.error || 'Невідома помилка.');
                    messageDiv.style.color = '#dc3545'; // Червоний (помилка)
                }
            })
            .catch(error => {
                // Помилка мережі (сервер недоступний тощо)
                console.error('Fetch Error:', error);
                messageDiv.textContent = 'Помилка мережі. Спробуйте пізніше.';
                messageDiv.style.color = '#dc3545';
            })
            .finally(() => {
                // Повертаємо кнопку в нормальний стан
                submitBtn.disabled = false;
                submitBtn.textContent = 'Відправити';
            });
        });
    }
});
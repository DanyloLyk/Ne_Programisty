window.onload = function() {
    const loaderWrapper = document.getElementById('loader-wrapper');
    const content = document.getElementById('page-content');
    const masonryGrid = document.querySelector('.row-cols-md-3'); // Елемент сітки Masonry

    if (content) {
        content.style.display = 'block';
    }

    if (masonryGrid && typeof Masonry !== 'undefined') {

        // Ручна ініціаліація Masonry
        new Masonry(masonryGrid, {
            // ВИПРАВЛЕНО: Селектор має бути '.col', оскільки батьківський елемент
            // використовує row-cols-md-3 для керування розміром колонок.
            itemSelector: '.col',
            percentPosition: true
            // gutter не потрібен, оскільки g-4 (gap) з Bootstrap 5
            // вже коректно обробляється Masonry
        });

        console.log("Masonry successfully initialized.");
    }

    // ... (код приховування лоадера) ...
    setTimeout(() => {
        if (loaderWrapper) {
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

            const title = titleInput.value.trim(); // Використовуємо trim() для видалення пробілів
            const description = descriptionInput.value.trim();

            // 2. Проста валідація
            if (!title || !description) {
                messageDiv.textContent = 'Будь ласка, заповніть усі поля.';
                messageDiv.style.color = '#FACC15';
                return;
            }

            // 3. Блокуємо кнопку та показуємо завантаження
            submitBtn.disabled = true;
            submitBtn.textContent = 'Відправка...';
            messageDiv.textContent = '';
            messageDiv.style.color = '#fff';
            fetch('/submit_feedback', { // URL вашого Flask-роуту
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: title,
                    description: description
                })
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(errorData => {
                        throw new Error(errorData.error || 'Помилка на сервері');
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    messageDiv.textContent = '✅ Відгук успішно надіслано!';
                    messageDiv.style.color = '#28a745';
                    form.reset();
                } else {
                    // Цей шлях малоймовірний, якщо сервер правильно використовує статуси HTTP
                    messageDiv.textContent = 'Помилка: ' + (data.error || 'Невідома помилка.');
                    messageDiv.style.color = '#dc3545';
                }
            })
            .catch(error => {
                const errorMessage = error.message || 'Помилка мережі. Спробуйте пізніше.';
                console.error('Fetch Error:', error);
                messageDiv.textContent = `❌ Помилка: ${errorMessage}`;
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
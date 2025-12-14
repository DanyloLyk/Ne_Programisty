// Автоматичний логін тільки для api.html сторінки
async function login() {
    // Перевіряємо чи ми на api.html сторінці
    if (!window.location.pathname.includes('/api')) {
        return Promise.resolve();
    }
    
    try {
        // Перевіряємо чи вже є токен
        if (localStorage.getItem('accessToken')) {
            console.log('Токен вже збережено');
            return Promise.resolve();
        }
        
        const response = await fetch('/api/v1/auth/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 'username': 'cat',
                                    'password': '123' })
            });
    if (!response.ok) {
        throw new Error('Не вдалося увійти користувачу');
    }
    
    const data = await response.json();

    localStorage.setItem('accessToken', data.access_token);
    console.log('Успішний вхід! Токен збережено в localStorage.');
    return Promise.resolve();
    } catch (error) {
        console.error('Помилка під час входу:', error);
        return Promise.reject(error);
    }
}
async function get_token() {
    return localStorage.getItem('accessToken');
}

// Функція для показу красивих повідомлень
// type може бути: 'success' (зелене), 'danger' (червоне), 'warning' (жовте)
window.showToast = function(message, type = 'success') {
const toastEl = document.getElementById('liveToast');
    const toastBody = document.getElementById('toastMessage');
    
    // Встановлюємо текст
    toastBody.textContent = message;
    
    // Скидаємо старі класи кольорів
    toastEl.className = 'toast align-items-center border-0';
    
    // Додаємо колір залежно від типу
    if (type === 'success') {
        toastEl.classList.add('text-bg-success'); // Зелений
    } else if (type === 'danger') {
        toastEl.classList.add('text-bg-danger');  // Червоний
    } else {
        toastEl.classList.add('text-bg-warning'); // Жовтий
    }

    // Показуємо повідомлення (використовуємо Bootstrap API)
    const toast = new bootstrap.Toast(toastEl);
    toast.show();
}
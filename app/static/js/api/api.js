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
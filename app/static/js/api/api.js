async function login() {
    try {
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
    alert('Успішний вхід! Ви - адмін.');
    console.log('Токен збережено в localStorage. Щоб отримати токен, викличте функцію get_token():', data.access_token);
    } catch (error) {
        console.error('Помилка під час входу:', error);
    }
}
async function get_token() {
    return localStorage.getItem('accessToken');
}
// === ВИПРАВЛЕННЯ 1: get_token має бути СИНХРОННИМ (без async) ===
function get_token() {
    return localStorage.getItem('accessToken');
}

// Функція для показу повідомлень (Toast)
window.showToast = function(message, type = 'success') {
    const toastEl = document.getElementById('liveToast');
    const toastBody = document.getElementById('toastMessage');
    
    if (!toastEl || !toastBody) return; // Захист, якщо елементів немає на сторінці

    toastBody.textContent = message;
    toastEl.className = 'toast align-items-center border-0';
    
    if (type === 'success') {
        toastEl.classList.add('text-bg-success');
    } else if (type === 'danger') {
        toastEl.classList.add('text-bg-danger');
    } else {
        toastEl.classList.add('text-bg-warning');
    }

    const toast = new bootstrap.Toast(toastEl);
    toast.show();
}

// Автоматичний логін
async function login() {
    // Логінимось тільки якщо ми на сторінці API
    if (!window.location.pathname.includes('/api')) {
        return Promise.resolve();
    }
    
    try {
        console.log("Спроба автоматичного входу...");
        const response = await fetch('/api/v1/auth/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            // Згідно твого seed_data: nickname="cat", password="123"
            body: JSON.stringify({ 
                'username': 'cat',
                'password': '123' 
            })
        });

        if (!response.ok) {
            const errText = await response.text();
            throw new Error(`Помилка входу: ${response.status} ${errText}`);
        }
        
        const data = await response.json();
        localStorage.setItem('accessToken', data.access_token);
        console.log('✅ Успішний вхід! Токен оновлено.');
        
        return Promise.resolve();
    } catch (error) {
        console.error('❌ Помилка під час входу:', error);
        window.showToast('Не вдалося увійти в систему', 'danger');
        return Promise.reject(error);
    }
}
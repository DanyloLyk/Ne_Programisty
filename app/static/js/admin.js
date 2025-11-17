document.getElementById('addItemForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());

    try {
        const response = await fetch('/add_item', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if(result.success) {
            // Закриваємо модалку
            const addItemModal = bootstrap.Modal.getInstance(document.getElementById('addItemModal'));
            addItemModal.hide();

            // Перезавантажуємо сторінку, щоб оновити список товарів
            location.reload();
        } else {
            alert(result.error || "Помилка при додаванні товару");
        }

    } catch (err) {
        console.error(err);
        alert("Помилка при відправці форми");
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const editForm = document.getElementById('editItemForm');
    if (!editForm) return;

    document.querySelectorAll('.edit-btn').forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.preventDefault();
            const itemId = this.dataset.id;
            const response = await fetch(`/get_item/${itemId}`);
            const data = await response.json();

            if(data.success){
                document.getElementById('editItemId').value = itemId;
                document.getElementById('editItemName').value = data.item.name;
                document.getElementById('editItemDescription').value = data.item.description;
                document.getElementById('editItemPrice').value = data.item.price;
                document.getElementById('editItemImage').value = data.item.image;

                const editModal = new bootstrap.Modal(document.getElementById('editItemModal'));
                editModal.show();
            }
        });
    });

    editForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        const data = Object.fromEntries(formData.entries());

        const response = await fetch(`/edit_item/${data.id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        if(result.success){
            const modal = bootstrap.Modal.getInstance(document.getElementById('editItemModal'));
            modal.hide();
            location.reload();
        } else {
            alert(result.error || "Помилка");
        }
    });
});

document.querySelectorAll('.delete-btn').forEach(btn => {
    btn.addEventListener('click', async function () {

        if (!confirm("Видалити товар?")) return;

        const id = this.dataset.id;

        const response = await fetch(`/delete_item/${id}`, {
            method: 'DELETE',
            headers: {
                "Content-Type": "application/json"
            }
        });

        const result = await response.json();

        if (result.success) {
            this.closest('.col-md-4').remove();
        } else {
            alert(result.error || "Помилка при видаленні!");
        }
    });
});

document.getElementById('addNewsForm')?.addEventListener('submit', async function(e){
    e.preventDefault();

    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());

    data.images = data.images
        ? data.images.split(',').map(x => x.trim())
        : [];

    const response = await fetch('/add_news', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    const result = await response.json();

    if(result.success){
        bootstrap.Modal.getInstance(document.getElementById('addNewsModal')).hide();
        location.reload();
    } else {
        alert("Помилка");
    }
});

document.querySelectorAll('.edit-news-btn').forEach(btn => {
    btn.addEventListener('click', async function(){
        const id = this.dataset.id;

        const response = await fetch(`/get_news/${id}`);
        const result = await response.json();

        if(result.success){
            document.getElementById('editNewsId').value = id;
            document.getElementById('editNewsName').value = result.news.name;
            document.getElementById('editNewsDescription').value = result.news.description;
            document.getElementById('editNewsDescriptionSecond').value = result.news.descriptionSecond;
            document.getElementById('editNewsImages').value = result.news.images.join(', ');

            new bootstrap.Modal(document.getElementById('editNewsModal')).show();
        }
    });
});

document.getElementById('editNewsForm')?.addEventListener('submit', async function(e){
    e.preventDefault();

    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());

    data.images = data.images
        ? data.images.split(',').map(x => x.trim())
        : [];

    const response = await fetch(`/edit_news/${data.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    const result = await response.json();

    if(result.success){
        bootstrap.Modal.getInstance(document.getElementById('editNewsModal')).hide();
        location.reload();
    }
});

document.querySelectorAll('.delete-news-btn').forEach(btn => {
    btn.addEventListener('click', async function(){
        if(!confirm("Видалити новину?")) return;

        const id = this.dataset.id;

        const response = await fetch(`/delete_news/${id}`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if(result.success) {
            const activeTab = localStorage.getItem('activeAdminTab') || '#items';
            location.href = window.location.pathname + activeTab;
        } else {
            alert("Помилка при видаленні");
        }
    });
});
    

document.querySelectorAll('.edit-user-btn').forEach(btn => {
    btn.addEventListener('click', async function() {
        const id = this.dataset.id;
        const res = await fetch(`/get_user/${id}`);
        const data = await res.json();

        if(data.success){
            document.getElementById('editUserId').value = data.user.id;
            document.getElementById('editUserNickname').value = data.user.nickname;
            document.getElementById('editUserEmail').value = data.user.email;
            document.getElementById('editUserStatus').value = data.user.status;
            document.getElementById('editUserPrivilege').value = data.user.privilege;
            document.getElementById('editUserPassword').value = '';

            new bootstrap.Modal(document.getElementById('editUserModal')).show();
        }
    });
});

document.getElementById('editUserForm')?.addEventListener('submit', async function(e){
    e.preventDefault();
    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());

    const res = await fetch(`/edit_user/${data.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    const result = await res.json();
    if(result.success){
        bootstrap.Modal.getInstance(document.getElementById('editUserModal')).hide();
        location.reload();
    } else {
        alert(result.error || "Помилка при редагуванні користувача");
    }
});

document.querySelectorAll('.delete-user-btn').forEach(btn => {
    btn.addEventListener('click', async function(){
        if(!confirm("Видалити користувача?")) return;

        const id = this.dataset.id;
        const res = await fetch(`/delete_user/${id}`, { method: 'DELETE' });
        const result = await res.json();

        if(result.success) location.reload();
        else alert(result.error || "Помилка при видаленні користувача");
    });
});

document.querySelectorAll('.view-order-btn').forEach(btn => {
    btn.addEventListener('click', async function () {
        const id = this.dataset.id;

        const res = await fetch(`/get_order/${id}`);
        const data = await res.json();

        if (!data.success) return alert("Помилка при отриманні замовлення");

        // Основне
        document.getElementById('orderId').textContent = data.order.id;
        document.getElementById('orderStatus').textContent = data.order.status;

        // User
        document.getElementById('orderUserNickname').textContent = data.order.user.nickname;
        document.getElementById('orderUserEmail').textContent = data.order.user.email;

        // Items
        const tbody = document.getElementById('orderItemsTable');
        tbody.innerHTML = "";

        data.order.items.forEach(item => {
            tbody.innerHTML += `
                <tr>
                    <td>${item.name}</td>
                    <td>${item.count}</td>
                    <td>${item.price} грн</td>
                    <td>${item.sum} грн</td>
                </tr>
            `;
        });

        document.getElementById('orderTotal').textContent = data.order.total_sum;

        // Кнопки
        const actions = document.getElementById('orderActions');
        actions.innerHTML = "";

        if (data.order.status === "In process") {
            actions.innerHTML = `
                <button class="btn btn-success" onclick="updateOrderStatus(${id}, 'Going')">Підтвердити</button>
                <button class="btn btn-danger" onclick="updateOrderStatus(${id}, 'Cancelled')">Скасувати</button>
            `;
        }
        else if (data.order.status === "Going") {
            actions.innerHTML = `
                <button class="btn btn-success" onclick="updateOrderStatus(${id}, 'Completed')">Завершити</button>
            `;
        }

        new bootstrap.Modal(document.getElementById('viewOrderModal')).show();
    });
});


async function updateOrderStatus(id, status) {
    const res = await fetch(`/update_order_status/${id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status })
    });

    const data = await res.json();

    if (data.success) location.reload();
    else alert("Помилка при зміні статусу");
}

// Зберігаємо останню активну вкладку адмінки
document.addEventListener('DOMContentLoaded', () => {
    const tabLinks = document.querySelectorAll('#adminTabs .nav-link');

    // Показуємо вкладку, яка збережена у localStorage
    const activeTabId = localStorage.getItem('activeAdminTab');
    if (activeTabId) {
        const tabToShow = document.querySelector(`#adminTabs .nav-link[href="${activeTabId}"]`);
        if (tabToShow) {
            new bootstrap.Tab(tabToShow).show();
        }
    }

    // При кліку на вкладку зберігаємо її в localStorage
    tabLinks.forEach(link => {
        link.addEventListener('shown.bs.tab', (event) => {
            const tabId = event.target.getAttribute('href');
            localStorage.setItem('activeAdminTab', tabId);
        });
    });
});

async function reloadActiveTab() {
    const activeTab = localStorage.getItem('activeAdminTab') || '#items';
    const tabPane = document.querySelector(activeTab);

    if (!tabPane) return;

    try {
        // Отримуємо HTML вкладки з сервера через fetch
        const res = await fetch(window.location.pathname + '?tab=' + activeTab.substring(1));
        const text = await res.text();

        // Створюємо тимчасовий DOM для парсингу
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = text;

        // Заміна контенту поточної вкладки
        const newTabContent = tempDiv.querySelector(activeTab);
        if (newTabContent) {
            tabPane.innerHTML = newTabContent.innerHTML;
        }
    } catch (err) {
        console.error('Помилка при перезавантаженні вкладки', err);
        // Якщо помилка, просто повне перезавантаження
        location.reload();
    }
}

// Управління замовленнями
document.addEventListener("DOMContentLoaded", () => {
    const ordersContainer = document.getElementById("orders-list");
    const viewOrderModal = new bootstrap.Modal(document.getElementById("viewOrderModal"));
    const API_BASE = "/api/v1";

    async function loadOrders() {
        try {
            const headers = window.getAuthHeaders();
            const response = await fetch(`${API_BASE}/orders/`, { headers });
            
            if (!response.ok) {
                if (response.status === 401) {
                    ordersContainer.innerHTML = `<div class="text-muted text-center p-4">Необхідна авторизація для перегляду замовлень</div>`;
                    return;
                }
                throw new Error(`Failed to load orders (${response.status})`);
            }

            const orders = await response.json();
            allOrdersCache = orders; // Зберігаємо в кеш
            renderOrders(orders);
        } catch (err) {
            console.error("Помилка завантаження замовлень:", err);
            ordersContainer.innerHTML = `<div class="text-danger text-center p-4">Помилка завантаження замовлень</div>`;
        }
    }

    function renderOrders(orders) {
        ordersContainer.innerHTML = "";

        if (!orders || orders.length === 0) {
            ordersContainer.innerHTML = `<div class="text-muted text-center p-4">Замовлень немає</div>`;
            return;
        }

        const perSlide = 3;
        for (let i = 0; i < orders.length; i += perSlide) {
            const slideItems = orders.slice(i, i + perSlide);
            const slideDiv = document.createElement("div");
            slideDiv.classList.add("carousel-item");
            if (i === 0) slideDiv.classList.add("active");

            const rowDiv = document.createElement("div");
            rowDiv.classList.add("row", "g-3");

            slideItems.forEach(order => {
                const colDiv = document.createElement("div");
                colDiv.classList.add("col-12", "col-md-4");
                
            const statusBadgeClass = {
                "In process": "bg-warning",
                "Shipped": "bg-info",
                "Completed": "bg-success",
                "Cancelled": "bg-danger"
            }[order.status] || "bg-secondary";

                colDiv.innerHTML = `
                    <div class="card h-100 shadow-sm border border-warning">
                        <div class="card-body d-flex flex-column">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <h5 class="card-title text-warning">Замовлення #${order.id}</h5>
                                <span class="badge ${statusBadgeClass}">${order.status}</span>
                            </div>
                            <p class="text-muted small mb-2">
                                <strong>Користувач:</strong> ${order.user?.nickname || "N/A"}<br>
                                <strong>Email:</strong> ${order.user?.email || "N/A"}
                            </p>
                            <p class="fw-bold text-warning mb-3">Сума: ${order.total_amount || 0} ₴</p>
                            <div class="mt-auto d-flex gap-2">
                                <button class="btn btn-outline-warning btn-sm flex-fill view-order-btn" data-order-id="${order.id}">
                                    <i class="fa-solid fa-eye me-1"></i> Переглянути
                                </button>
                                ${window.isModeratorMode() ? `
                                    <button class="btn btn-outline-danger btn-sm delete-order-btn" data-order-id="${order.id}">
                                        <i class="fa-solid fa-trash"></i>
                                    </button>
                                ` : ""}
                            </div>
                        </div>
                    </div>
                `;
                rowDiv.appendChild(colDiv);
            });

            slideDiv.appendChild(rowDiv);
            ordersContainer.appendChild(slideDiv);
        }

        attachOrderButtons();
    }

    function attachOrderButtons() {
        // Кнопка перегляду
        document.querySelectorAll(".view-order-btn").forEach(btn => {
            btn.addEventListener("click", async () => {
                const orderId = btn.dataset.orderId;
                await viewOrder(orderId);
            });
        });

        // Кнопка видалення
        if (window.isModeratorMode()) {
            document.querySelectorAll(".delete-order-btn").forEach(btn => {
                btn.addEventListener("click", async () => {
                    const orderId = btn.dataset.orderId;
                    if (confirm("Видалити замовлення?")) {
                        await deleteOrder(orderId);
                    }
                });
            });
        }
    }

    let allOrdersCache = [];

    async function viewOrder(orderId) {
        try {
            // 1. Перевіряємо кеш, якщо порожній — вантажимо з сервера
            if (!allOrdersCache || allOrdersCache.length === 0) {
                const headers = window.getAuthHeaders();
                const response = await fetch(`${API_BASE}/orders/`, { headers });
                if (!response.ok) throw new Error("Failed to load orders");
                allOrdersCache = await response.json();
            }

            // 2. ВАЖЛИВО: Знаходимо конкретне замовлення в масиві
            const order = allOrdersCache.find(o => o.id === parseInt(orderId));
            
            if (!order) {
                throw new Error("Замовлення не знайдено в списку");
            }

            // 3. Заповнюємо шапку модалки (Інфо про юзера та статус)
            document.getElementById("orderId").textContent = order.id;
            
            // Фарбуємо статус
            const statusBadge = document.getElementById("orderStatus");
            statusBadge.textContent = order.status;
            statusBadge.className = 'badge ' + ({
                "In process": "bg-warning",
                "Shipped": "bg-info",
                "Completed": "bg-success",
                "Cancelled": "bg-danger"
            }[order.status] || "bg-secondary");

            // Дані юзера (безпечний доступ)
            document.getElementById("orderUserNickname").textContent = order.user?.nickname || "Невідомий";
            document.getElementById("orderUserEmail").textContent = order.user?.email || "N/A";

            // 4. Очищаємо і заповнюємо таблицю товарів
            const tbody = document.getElementById("orderItemsTable");
            tbody.innerHTML = "";

            // Шукаємо items (сумісність з різними версіями API)
            const items = order.items || order.order_items || [];

            if (items.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="4" class="text-center text-muted p-4">
                            Деталі товарів відсутні.<br>
                            <small>Можливо, структура даних змінилася.</small>
                        </td>
                    </tr>
                `;
            } else {
                items.forEach(item => {
                    // Визначаємо змінні (якщо раптом бекенд щось не додав)
                    const itemName = item.name || "Товар видалено/Невідомий";
                    const quantity = item.quantity || item.count || 0;
                    const price = item.price || 0;
                    
                    // Якщо сума прийшла з бекенду (item.sum) — беремо її.
                    // Якщо ні — рахуємо тут (price * quantity * discount).
                    const totalSum = item.sum !== undefined
                        ? item.sum 
                        : (price * quantity * (item.discount || 1.0)).toFixed(2);

                    const row = document.createElement("tr");
                    row.innerHTML = `
                        <td>
                            <span class="fw-bold">${itemName}</span>
                            ${item.discount && item.discount < 1.0 
                                ? `<span class="badge bg-danger ms-1">-${Math.round((1 - item.discount) * 100)}%</span>` 
                                : ''}
                        </td>
                        <td class="text-center">${quantity}</td>
                        <td>${price} ₴</td>
                        <td class="fw-bold text-warning">${totalSum} ₴</td>
                    `;
                    tbody.appendChild(row);
                });
            }

            // 5. Загальна сума
            document.getElementById("orderTotal").textContent = order.total_amount || 0;

            // 6. Кнопки дій (Тільки для модератора)
            const actions = document.getElementById("orderActions");
            actions.innerHTML = ""; // Очищаємо старі кнопки

            if (window.isModeratorMode && window.isModeratorMode()) {
                let buttonsHtml = '';
                
                if (order.status === "In process") {
                    buttonsHtml = `
                        <button class="btn btn-success" onclick="updateOrderStatus(${order.id}, 'Shipped')">
                            <i class="fa-solid fa-truck-fast me-1"></i> Відправити
                        </button>
                        <button class="btn btn-danger" onclick="updateOrderStatus(${order.id}, 'Cancelled')">
                            <i class="fa-solid fa-ban me-1"></i> Скасувати
                        </button>
                    `;
                } else if (order.status === "Shipped") {
                    buttonsHtml = `
                        <button class="btn btn-success" onclick="updateOrderStatus(${order.id}, 'Completed')">
                            <i class="fa-solid fa-check-double me-1"></i> Завершити
                        </button>
                    `;
                }
                // Для Completed/Cancelled кнопок не треба
                actions.innerHTML = buttonsHtml;
            } else {
                // Для звичайного юзера можна додати кнопку "Закрити"
                actions.innerHTML = `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрити</button>`;
            }

            // 7. Відкриваємо модалку
            viewOrderModal.show();

        } catch (err) {
            console.error("Помилка відображення замовлення:", err);
            // Використовуємо твій новий гарний тост, якщо він є, або алерт
            if (window.showToast) {
                window.showToast("Не вдалося відкрити замовлення", 'danger');
            } else {
                alert("Помилка завантаження замовлення");
            }
        }
    }

    window.updateOrderStatus = async function(orderId, status) {
        try {
            const headers = window.getAuthHeaders();
            const response = await fetch(`${API_BASE}/orders/${orderId}`, {
                method: "PATCH",
                headers,
                body: JSON.stringify({ status })
            });

            if (!response.ok) throw new Error("Failed to update order");

            const modal = bootstrap.Modal.getInstance(document.getElementById("viewOrderModal"));
            modal.hide();
            
            allOrdersCache = []; // Очищаємо кеш
            await loadOrders();
            window.showToast("Статус замовлення оновлено", 'success');
        } catch (err) {
            console.error("Помилка оновлення статусу:", err);
            window.showToast("Не вдалося оновити статус замовлення", 'danger');
        }
    };

    async function deleteOrder(orderId) {
        try {
            const headers = window.getAuthHeaders();
            const response = await fetch(`${API_BASE}/orders/${orderId}`, {
                method: "DELETE",
                headers
            });

            if (!response.ok) throw new Error("Failed to delete order");

            allOrdersCache = []; // Очищаємо кеш
            await loadOrders();
            window.showToast("Замовлення видалено", 'success');
        } catch (err) {
            console.error("Помилка видалення замовлення:", err);
            window.showToast("Не вдалося видалити замовлення", 'danger');
        }
    }

    // Експортуємо функцію для використання в інших скриптах
    window.loadOrders = loadOrders;

    // Слухаємо подію створення замовлення
    window.addEventListener("orderCreated", () => {
        loadOrders();
    });

    // Слухаємо зміни режиму модератора
    window.addEventListener("moderatorModeChanged", () => {
        loadOrders();
    });

    // Завантаження при старті
    loadOrders();
});


// Управління замовленнями
document.addEventListener("DOMContentLoaded", () => {
    const ordersContainer = document.getElementById("orders-list");
    const viewOrderModal = new bootstrap.Modal(document.getElementById("viewOrderModal"));
    const confirmDeleteModal = new bootstrap.Modal(document.getElementById("confirmDeleteModal"));
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
                btn.addEventListener("click", () => {
                    const orderId = btn.dataset.orderId;
                    showDeleteConfirmOrder(orderId, "замовлення");
                });
            });
        }
    }

    let allOrdersCache = [];

    async function viewOrder(orderId) {
        try {
            // Використовуємо дані з кешу або завантажуємо знову
            if (allOrdersCache.length === 0) {
                const headers = window.getAuthHeaders();
                const response = await fetch(`${API_BASE}/orders/`, { headers });
                if (!response.ok) throw new Error("Failed to load orders");
                allOrdersCache = await response.json();
            }

            const order = allOrdersCache.find(o => o.id === parseInt(orderId));
            if (!order) {
                throw new Error("Order not found");
            }

            // Заповнюємо модальне вікно
            document.getElementById("orderId").textContent = order.id;
            document.getElementById("orderStatus").textContent = order.status;
            document.getElementById("orderUserNickname").textContent = order.user?.nickname || "N/A";
            document.getElementById("orderUserEmail").textContent = order.user?.email || "N/A";

            // Товари - якщо немає деталей, використовуємо загальну інформацію
            const tbody = document.getElementById("orderItemsTable");
            tbody.innerHTML = "";
            
            const items = order.items || order.order_items || [];
            if (items.length === 0) {
                // Якщо немає деталей товарів, показуємо загальну інформацію
                tbody.innerHTML = `
                    <tr>
                        <td colspan="4" class="text-center text-muted">
                            Деталі товарів недоступні. Загальна сума: ${order.total_amount || 0} ₴
                        </td>
                    </tr>
                `;
            } else {
                items.forEach(item => {
                    const row = document.createElement("tr");
                    row.innerHTML = `
                        <td>${item.name || item.item_name || "N/A"}</td>
                        <td>${item.count || item.quantity || 0}</td>
                        <td>${item.price || 0} ₴</td>
                            <td>${item.sum || (item.price * (item.count || item.quantity || 0))} ₴</td>
                        `;
                        tbody.appendChild(row);
                    });
                }

            document.getElementById("orderTotal").textContent = order.total_amount || order.total_sum || 0;

            // Кнопки дій (тільки для модератора)
            const actions = document.getElementById("orderActions");
            actions.innerHTML = "";

            if (window.isModeratorMode()) {
                if (order.status === "In process") {
                    actions.innerHTML = `
                        <button class="btn btn-success" onclick="updateOrderStatus(${order.id}, 'Shipped')">
                            <i class="fa-solid fa-check me-1"></i> Підтвердити відправку
                        </button>
                        <button class="btn btn-danger" onclick="updateOrderStatus(${order.id}, 'Cancelled')">
                            <i class="fa-solid fa-times me-1"></i> Скасувати
                        </button>
                    `;
                } else if (order.status === "Shipped") {
                    actions.innerHTML = `
                        <button class="btn btn-success" onclick="updateOrderStatus(${order.id}, 'Completed')">
                            <i class="fa-solid fa-check-double me-1"></i> Завершити
                        </button>
                    `;
                }
            }

            viewOrderModal.show();
        } catch (err) {
            console.error("Помилка перегляду замовлення:", err);
            window.showToast("Не вдалося завантажити замовлення", 'danger');
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

    function showDeleteConfirmOrder(orderId, type) {
        document.getElementById("confirmDeleteText").textContent = 
            `Ви впевнені, що хочете видалити це ${type}?`;
        
        const confirmBtn = document.getElementById("confirmDeleteBtn");
        const cancelBtn = document.querySelector("#confirmDeleteModal .btn-secondary");
        const closeBtn = document.querySelector("#confirmDeleteModal .btn-close");
        
        confirmBtn.onclick = async () => {
            try {
                const headers = window.getAuthHeaders();
                const response = await fetch(`${API_BASE}/orders/${orderId}`, {
                    method: "DELETE",
                    headers
                });

                if (!response.ok) throw new Error("Failed to delete order");

                confirmDeleteModal.hide();
                allOrdersCache = []; // Очищаємо кеш
                await loadOrders();
                window.showToast("Замовлення видалено", 'success');
            } catch (err) {
                console.error("Помилка видалення замовлення:", err);
                window.showToast("Не вдалося видалити замовлення", 'danger');
            }
        };
        
        cancelBtn.onclick = () => {
            confirmDeleteModal.hide();
        };
        
        closeBtn.onclick = () => {
            confirmDeleteModal.hide();
        };

        confirmDeleteModal.show();
    }

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

    // Слухаємо зміни режиму модератора
    window.addEventListener("moderatorModeChanged", () => {
        loadOrders();
    });

    // Завантаження при старті
    loadOrders();
});


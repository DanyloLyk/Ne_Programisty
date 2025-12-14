document.addEventListener("DOMContentLoaded", () => {

    const desktopsContainer = document.getElementById("desktop-list");
    const cartItemsContainer = document.getElementById("cart-items");
    const cartTotalField = document.getElementById("cart-total");
    const cartModal = new bootstrap.Modal(document.getElementById("cartModal"));
    const confirmDeleteModal = new bootstrap.Modal(document.getElementById("confirmDeleteModal"));

    const API = "/api/v1";

    function token() {
        return localStorage.getItem("accessToken") || get_token();
    }

    function authHeaders() {
        const tokenValue = token();
        if (!tokenValue) {
            console.warn("Токен не знайдено в localStorage");
            return {
                "Accept": "application/json",
                "Content-Type": "application/json"
            };
        }
        return {
            "Authorization": `Bearer ${tokenValue}`,
            "Accept": "application/json",
            "Content-Type": "application/json"
        };
    }

    // -------------------------
    // Load desktops
    // -------------------------
    async function loadDesktops() {
        try {
            const r = await fetch(`${API}/desktops`);
            if (!r.ok) throw new Error(`Failed to load desktops (${r.status})`);
            const items = await r.json();
            renderDesktops(items);
            attachCartButtons();
        } catch (e) {
            console.error(e);
        }
    }

    // =========================
    // Прив'язка кнопок "До кошика"
    // =========================
    function attachCartButtons() {
        const cartButtons = desktopsContainer.querySelectorAll(".open-cart");
        cartButtons.forEach(btn => {
            btn.addEventListener("click", () => {
                const colDiv = btn.closest(".col-12, .col-md-3");
                if (!colDiv || !colDiv.dataset.itemId) {
                    console.error("Не знайдено item_id на кнопці");
                    return;
                }
                addToCart(colDiv.dataset.itemId);
            });
        });
    }

    // =========================
    // RENDER — десктопи
    // =========================
    function renderDesktops(items) {
        desktopsContainer.innerHTML = "";

        if (!items || items.length === 0) {
            desktopsContainer.innerHTML = `<div class="text-muted">Каталог порожній</div>`;
            return;
        }

        const isModerator = window.isModeratorMode ? window.isModeratorMode() : false;

        const perSlide = 4;
        for (let i = 0; i < items.length; i += perSlide) {
            const slide = document.createElement("div");
            slide.className = "carousel-item" + (i === 0 ? " active" : "");

            const rowDiv = document.createElement("div");
            rowDiv.classList.add("row", "g-3", "justify-content-center");
            const slideItems = items.slice(i, i + perSlide);
            slideItems.forEach(item => {
                const colDiv = document.createElement("div");
                colDiv.classList.add("col-12", "col-md-3");
                colDiv.dataset.itemId = item.id;

                const imagePath = item.image && (item.image.startsWith("http://") || item.image.startsWith("https://"))
                    ? item.image
                    : `/static/${item.image || "images/default.jpg"}`;

                colDiv.innerHTML = `
                    <div class="card h-100 shadow-sm d-flex flex-column border border-warning">
                        <div class="ratio ratio-1x1">
                            <img src="${imagePath}" class="w-100 h-100" alt="${item.name}" style="object-fit: cover;">
                        </div>

                        <div class="card-body d-flex flex-column">
                            <h5 class="card-title text-warning">${item.name}</h5>
                            <p class="card-text text-muted small">${item.description || ""}</p>
                            <div class="mt-auto">
                                <div class="text-center text-warning fw-bold mb-2">${item.price} ₴</div>
                                <div class="d-flex gap-2">
                                    <button class="btn btn-warning flex-fill open-cart">
                                        <i class="fa-solid fa-cart-plus me-1"></i> До кошика
                                    </button>
                                    ${isModerator ? `
                                        <button class="btn btn-outline-warning edit-item-btn" data-item-id="${item.id}">
                                            <i class="fa-solid fa-pencil"></i>
                                        </button>
                                        <button class="btn btn-outline-danger delete-item-btn" data-item-id="${item.id}">
                                            <i class="fa-solid fa-trash"></i>
                                        </button>
                                    ` : ""}
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                rowDiv.appendChild(colDiv);
            });

            slide.appendChild(rowDiv);
            desktopsContainer.appendChild(slide);
        }

        attachCartButtons();
        if (isModerator) {
            attachModeratorButtons();
        }
    }

    function attachModeratorButtons() {
        if (!window.isModeratorMode || !window.isModeratorMode()) return;
        
        // Кнопка редагування товару
        document.querySelectorAll(".edit-item-btn").forEach(btn => {
            btn.addEventListener("click", async () => {
                const itemId = btn.dataset.itemId;
                await editItem(itemId);
            });
        });

        // Кнопка видалення товару
        document.querySelectorAll(".delete-item-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                const itemId = btn.dataset.itemId;
                showDeleteConfirmCatalog(itemId, "товар");
            });
        });
    }

    async function editItem(itemId) {
        if (!window.isModeratorMode || !window.isModeratorMode()) {
            window.showToast("Ця функція доступна тільки в режимі модератора", 'warning');
            return;
        }
        
        try {
            const response = await fetch(`${API}/desktops/${itemId}`);
            if (!response.ok) throw new Error("Failed to load item");

            const item = await response.json();
            
            document.getElementById("editItemId").value = item.id;
            document.getElementById("editItemName").value = item.name;
            document.getElementById("editItemDescription").value = item.description || "";
            document.getElementById("editItemPrice").value = item.price;
            document.getElementById("editItemImage").value = item.image || "";

            const modal = new bootstrap.Modal(document.getElementById("editItemModal"));
            modal.show();
        } catch (err) {
            console.error("Помилка завантаження товару:", err);
            window.showToast("Не вдалося завантажити товар", 'danger');
        }
    }

    async function deleteItem(itemId) {
        if (!window.isModeratorMode || !window.isModeratorMode()) {
            window.showToast("Ця функція доступна тільки в режимі модератора", 'warning');
            return;
        }
        
        try {
            const headers = authHeaders();
            const response = await fetch(`${API}/desktops/${itemId}`, {
                method: "DELETE",
                headers
            });

            if (!response.ok) throw new Error("Failed to delete item");

            await loadDesktops();
            window.showToast("Товар видалено", 'success');
        } catch (err) {
            console.error("Помилка видалення товару:", err);
            window.showToast("Не вдалося видалити товар", 'danger');
        }
    }

    function showDeleteConfirmCatalog(itemId, type) {
        document.getElementById("confirmDeleteText").textContent = 
            `Ви впевнені, що хочете видалити цей ${type}?`;
        
        const confirmBtn = document.getElementById("confirmDeleteBtn");
        const cancelBtn = document.querySelector("#confirmDeleteModal .btn-secondary");
        const closeBtn = document.querySelector("#confirmDeleteModal .btn-close");
        
        confirmBtn.onclick = async () => {
            try {
                const headers = authHeaders();
                const response = await fetch(`${API}/desktops/${itemId}`, {
                    method: "DELETE",
                    headers
                });

                if (!response.ok) throw new Error("Failed to delete item");

                confirmDeleteModal.hide();
                await loadDesktops();
                window.showToast("Товар видалено", 'success');
            } catch (err) {
                console.error("Помилка видалення товару:", err);
                window.showToast("Не вдалося видалити товар", 'danger');
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

    // -------------------------
    // Cart API
    // -------------------------
    async function loadCart() {
        try {
            const r = await fetch(`${API}/cart`, { headers: authHeaders() });
            if (!r.ok) {
                if (r.status === 401) {
                    console.warn("Неавторизований при loadCart");
                    // можна відкрити логін-модал або показати повідомлення
                    cartItemsContainer.innerHTML = `<div class="text-muted">Ви не увійшли в акаунт</div>`;
                    cartTotalField.textContent = `0 ₴`;
                    return;
                }
                throw new Error(`Cart load failed: ${r.status}`);
            }
            const cart = await r.json();
            renderCart(cart);
        } catch (e) {
            console.error(e);
            cartItemsContainer.innerHTML = `<div class="text-danger">Не вдалося завантажити кошик</div>`;
        }
    }

    async function addToCart(itemId, quantity = 1) {
        try {
            const r = await fetch(`${API}/cart`, {
                method: "POST",
                headers: authHeaders(),
                body: JSON.stringify({ item_id: Number(itemId), quantity: Number(quantity) })
            });

            if (!r.ok) {
                const err = await safeParseJSON(r);
                throw new Error(err?.error || `Add failed (${r.status})`);
            }

            await loadCart();
            cartModal.show();
        } catch (e) {
            console.error(e);
            window.showToast(e.message, 'danger');
        }
    }

    // IMPORTANT: server expects absolute quantity (not delta)
    async function updateQuantity(itemId, newQuantity) {
        try {
            if (newQuantity < 1) {
                // якщо нуль або менше — видаляємо позицію
                await removeFromCart(itemId);
                return;
            }

            const r = await fetch(`${API}/cart/quantity`, {
                method: "PUT",
                headers: authHeaders(),
                body: JSON.stringify({ item_id: Number(itemId), quantity: Number(newQuantity) })
            });

            if (!r.ok) {
                const err = await safeParseJSON(r);
                throw new Error(err?.error || `Update quantity failed (${r.status})`);
            }

            await loadCart();
        } catch (e) {
            console.error(e);
            window.showToast(e.message, 'danger');
        }
    }

    async function removeFromCart(itemId) {
        try {
            const r = await fetch(`${API}/cart`, {
                method: "DELETE",
                headers: authHeaders(),
                body: JSON.stringify({ item_id: Number(itemId) })
            });

            if (!r.ok) {
                const err = await safeParseJSON(r);
                throw new Error(err?.error || `Remove failed (${r.status})`);
            }

            await loadCart();
        } catch (e) {
            console.error(e);
            window.showToast(e.message, 'danger');
        }
    }

    // допоміжна: безпечний парсинг JSON з відповіді
    async function safeParseJSON(response) {
        try { return await response.json(); } catch { return null; }
    }

    // -------------------------
    // Render cart — додаємо data-quantity, data-item для span
    // -------------------------
    function renderCart(cart) {
        cartItemsContainer.innerHTML = "";

        if (!cart || !Array.isArray(cart.items) || cart.items.length === 0) {
            cartItemsContainer.innerHTML = `<div class="text-muted">Кошик порожній</div>`;
            cartTotalField.textContent = `0 ₴`;
            return;
        }

        cart.items.forEach(entry => {
            const p = entry.item_details;
            const qty = Number(entry.quantity);

            // зберігаємо quantity в span[data-item-id] для зручності
            cartItemsContainer.innerHTML += `
                <div class="card p-3 shadow-sm" data-item-id="${p.id}">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="d-flex gap-3 align-items-start">
                            <img src="${p.image && (p.image.startsWith('http://')||p.image.startsWith('https://')) ? p.image : `/static/${p.image}`}" width="70" height="70" style="object-fit:cover" alt="${p.name}">
                            <div>
                                <h6 class="m-0">${p.name}</h6>
                                <div class="text-muted small">${p.price} ₴</div>
                                <div class="d-flex align-items-center gap-2 mt-2">
                                    <button class="btn btn-light btn-sm cart-minus" data-item-id="${p.id}">–</button>
                                    <span class="cart-quantity" data-item-id="${p.id}" data-quantity="${qty}">${qty}</span>
                                    <button class="btn btn-light btn-sm cart-plus" data-item-id="${p.id}">+</button>
                                </div>
                            </div>
                        </div>

                        <div class="text-end">
                            <div class="fw-bold">${p.total_price} ₴</div>
                            <button class="btn btn-sm btn-outline-danger mt-2 cart-delete" data-item-id="${p.id}">
                                Видалити
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });
        console.log(cartTotalField.textContent, cart.total);
        
        cartTotalField.textContent = `${cart.total} ₴`;
    }

    // -------------------------
    // Event wiring: делегуємо кліки в контейнері кошика
    // -------------------------
    cartItemsContainer.addEventListener("click", (e) => {
        const plus = e.target.closest(".cart-plus");
        if (plus) {
            const itemId = plus.dataset.itemId;
            // знайдемо поточну кількість із span
            const span = cartItemsContainer.querySelector(`.cart-quantity[data-item-id="${itemId}"]`);
            const current = Number(span?.dataset.quantity ?? span?.textContent ?? 0);
            const newQ = current + 1;
            updateQuantity(itemId, newQ);
            return;
        }

        const minus = e.target.closest(".cart-minus");
        if (minus) {
            const itemId = minus.dataset.itemId;
            const span = cartItemsContainer.querySelector(`.cart-quantity[data-item-id="${itemId}"]`);
            const current = Number(span?.dataset.quantity ?? span?.textContent ?? 0);
            const newQ = current - 1;
            updateQuantity(itemId, newQ);
            return;
        }

        const del = e.target.closest(".cart-delete");
        if (del) {
            const itemId = del.dataset.itemId;
            if (!confirm("Видалити позицію з кошика?")) return;
            removeFromCart(itemId);
            return;
        }
    });

    // -------------------------
    // Attach add-to-cart buttons (on desktop items)
    // -------------------------
    function attachCartButtons() {
        desktopsContainer.querySelectorAll(".open-cart").forEach(btn => {
            btn.onclick = (ev) => {
                const col = btn.closest("[data-item-id]");
                if (!col) { console.error("data-item-id not found"); return; }
                addToCart(col.dataset.itemId, 1);
            };
        });
    }

    document.getElementById("clear-cart")?.addEventListener("click", async () => {
        if (!confirm("Ви дійсно хочете очистити весь кошик?")) return;

        try {
            const r = await fetch(`${API}/cart/clear`, {
                method: "DELETE",
                headers: authHeaders()
            });

            const data = await safeParseJSON(r);

            if (r.ok) {
                window.showToast(data.message || "Ваш кошик успішно очищено.", 'success');
                await loadCart();  // оновлюємо відображення кошика
            } else if (r.status === 401) {
                window.showToast("Користувач не авторизований. Будь ласка, увійдіть.", 'warning');
            } else {
                window.showToast(data?.error || `Не вдалося очистити кошик (${r.status})`, 'danger');
            }
        } catch (e) {
            console.error(e);
            window.showToast("Помилка при очищенні кошика. Перевірте підключення.", 'danger');
        }
    });

    // Додавання товару (тільки для модератора)
    document.getElementById("addItemBtn")?.addEventListener("click", () => {
        if (!window.isModeratorMode || !window.isModeratorMode()) {
            window.showToast("Ця функція доступна тільки в режимі модератора", 'warning');
            return;
        }
        const modal = new bootstrap.Modal(document.getElementById("addItemModal"));
        modal.show();
    });

    document.getElementById("saveItemBtn")?.addEventListener("click", async () => {
        if (!window.isModeratorMode || !window.isModeratorMode()) {
            window.showToast("Ця функція доступна тільки в режимі модератора", 'warning');
            return;
        }
        
        const name = document.getElementById("addItemName").value.trim();
        const description = document.getElementById("addItemDescription").value.trim();
        const price = parseFloat(document.getElementById("addItemPrice").value);
        const image = document.getElementById("addItemImage").value.trim();

        if (!name || !description || !price || !image) {
            window.showToast("Заповніть всі поля", 'warning');
            return;
        }

        try {
            const headers = authHeaders();
            const response = await fetch(`${API}/desktops`, {
                method: "POST",
                headers,
                body: JSON.stringify({ name, description, price, image })
            });

            if (!response.ok) {
                const err = await safeParseJSON(response);
                throw new Error(err?.message || "Failed to create item");
            }

            const modal = bootstrap.Modal.getInstance(document.getElementById("addItemModal"));
            modal.hide();
            
            // Очищаємо форму
            document.getElementById("addItemName").value = "";
            document.getElementById("addItemDescription").value = "";
            document.getElementById("addItemPrice").value = "";
            document.getElementById("addItemImage").value = "";

            await loadDesktops();
            window.showToast("Товар додано", 'success');
        } catch (err) {
            console.error("Помилка додавання товару:", err);
            window.showToast(err.message || "Не вдалося додати товар", 'danger');
        }
    });

    // Оновлення товару
    document.getElementById("updateItemBtn")?.addEventListener("click", async () => {
        if (!window.isModeratorMode || !window.isModeratorMode()) {
            window.showToast("Ця функція доступна тільки в режимі модератора", 'warning');
            return;
        }
        
        const itemId = document.getElementById("editItemId").value;
        const name = document.getElementById("editItemName").value.trim();
        const description = document.getElementById("editItemDescription").value.trim();
        const price = parseFloat(document.getElementById("editItemPrice").value);
        const image = document.getElementById("editItemImage").value.trim();

        if (!name || !description || !price) {
            window.showToast("Заповніть всі обов'язкові поля", 'warning');
            return;
        }

        try {
            const headers = authHeaders();
            const data = { name, description, price };
            if (image) data.image = image;

            const response = await fetch(`${API}/desktops/${itemId}`, {
                method: "PATCH",
                headers,
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                const err = await safeParseJSON(response);
                throw new Error(err?.message || "Failed to update item");
            }

            const modal = bootstrap.Modal.getInstance(document.getElementById("editItemModal"));
            modal.hide();
            
            await loadDesktops();
            window.showToast("Товар оновлено", 'success');
        } catch (err) {
            console.error("Помилка оновлення товару:", err);
            window.showToast(err.message || "Не вдалося оновити товар", 'danger');
        }
    });

    // Слухаємо зміни режиму модератора
    window.addEventListener("moderatorModeChanged", () => {
        loadDesktops();
    });

    // init
    loadDesktops();
    loadCart();
});

document.addEventListener("DOMContentLoaded", () => {

    const desktopsContainer = document.getElementById("desktop-list");
    const cartItemsContainer = document.getElementById("cart-items");
    const cartTotalField = document.getElementById("cart-total");
    const cartModal = new bootstrap.Modal(document.getElementById("cartModal"));

    const API = "/api/v1";

    function token() {
        return localStorage.getItem("accessToken");
    }

    function authHeaders() {
        return {
            "Authorization": `Bearer ${token()}`,
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

    // -------------------------
    // Render desktops (unchanged)
    // -------------------------
    function renderDesktops(items) {
        desktopsContainer.innerHTML = "";
        const perSlide = 4;

        for (let i = 0; i < items.length; i += perSlide) {
            const slide = document.createElement("div");
            slide.className = "carousel-item" + (i === 0 ? " active" : "");

            const row = document.createElement("div");
            row.className = "row g-3 justify-content-center";

            items.slice(i, i + perSlide).forEach(item => {
                const col = document.createElement("div");
                col.className = "col-12 col-md-3";
                col.dataset.itemId = item.id;

                const imagePath = item.image && (item.image.startsWith("http://") || item.image.startsWith("https://"))
                    ? item.image
                    : `/static/${item.image || "images/default.jpg"}`;

                col.innerHTML = `
                    <div class="card h-100 shadow-sm d-flex flex-column">
                        <div class="ratio ratio-1x1">
                            <img src="${imagePath}" class="w-100 h-100" style="object-fit:cover;" alt="${item.name}">
                        </div>
                        <div class="card-body d-flex flex-column">
                            <h5>${item.name}</h5>
                            <p class="text-muted small">${item.description || ""}</p>
                            <div class="mt-auto">
                                <div class="text-warning fw-bold mb-2">${item.price} ₴</div>
                                <button class="btn btn-warning w-100 open-cart">До кошика</button>
                            </div>
                        </div>
                    </div>
                `;
                row.appendChild(col);
            });

            slide.appendChild(row);
            desktopsContainer.appendChild(slide);
        }
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
            alert(e.message);
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
            alert(e.message);
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
            alert(e.message);
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
                alert(data.message || "Ваш кошик успішно очищено.");
                await loadCart();  // оновлюємо відображення кошика
            } else if (r.status === 401) {
                alert("Користувач не авторизований. Будь ласка, увійдіть.");
            } else {
                alert(data?.error || `Не вдалося очистити кошик (${r.status})`);
            }
        } catch (e) {
            console.error(e);
            alert("Помилка при очищенні кошика. Перевірте підключення.");
        }
    });

    // init
    loadDesktops();
    loadCart();
});

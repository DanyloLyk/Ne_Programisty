// =========================
// 1. ЕЛЕМЕНТИ ІНТЕРФЕЙСУ
// =========================

console.log("LIVE!!!");

// Каталог десктопів
const desktopsContainer = document.getElementById("desktop-list");

// Модальне вікно
const cartModal = new bootstrap.Modal(document.getElementById("cartModal"));

// Список товарів у кошику
const cartItemsContainer = document.getElementById("cart-items");

// Поле підсумку
const cartTotalField = document.getElementById("cart-total");

// =========================
// 2. API — ФУНКЦІЇ
// =========================

const API_BASE = "/api/v1";

// =========================
// Завантаження токену
// =========================

function loadToken() {
    const token = localStorage.getItem("accessToken");
    if (!token) throw new Error("AUTH_MISSING_TOKEN");
    return token;
}

// =========================
// Обробка шляху до зображення
// =========================

function getImagePath(image) {
    if (!image) return "/static/images/default.jpg";
    return image.startsWith("http://") || image.startsWith("https://") ? image : `/static/${image}`;
}

// =========================
// GET /desktops
// =========================

async function loadDesktops() {
    try {
        const response = await fetch(`${API_BASE}/desktops`);
        const data = await response.json();
        renderDesktops(data);
        attachCartButtons(); // після рендеру карток прив'язуємо кнопки
    } catch (err) {
        console.error("Помилка завантаження десктопів:", err);
    }
}

// =========================
// GET /cart
// =========================

async function loadCart() {
    try {
        const token = loadToken();
        const response = await fetch(`${API_BASE}/cart`, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Accept": "application/json"
            }
        });
        const data = await response.json();
        renderCart(data);
    } catch (err) {
        console.error("Помилка завантаження кошика:", err);
    }
}

// =========================
// POST /cart — додати товар
// =========================

async function addToCart(itemId, quantity = 1) {
    try {
        const token = loadToken();
        const response = await fetch(`${API_BASE}/cart`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ item_id: itemId, quantity })
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.error || "Помилка при додаванні в кошик");
        }

        const data = await response.json();
        console.log("Додано в кошик:", data);

        loadCart(); // оновлюємо кошик у модалці
        cartModal.show();

    } catch (err) {
        console.error("Помилка при додаванні в кошик:", err);
        alert(err.message);
    }
}

// =========================
// Прив'язка кнопок "До кошика"
// =========================

function attachCartButtons() {
    const cartButtons = document.querySelectorAll(".open-cart");
    cartButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const itemId = btn.closest(".card").parentElement.dataset.itemId;
            console.log(btn.closest(".card"))
            if (!itemId) return console.error("Не знайдено item_id на кнопці");
            addToCart(itemId);
        });
    });
}

// =========================
// RENDER — десктопи
// =========================

function renderDesktops(items) {
    desktopsContainer.innerHTML = "";

    const perSlide = 4; // 4 картки на слайд
    for (let i = 0; i < items.length; i += perSlide) {
        const slideItems = items.slice(i, i + perSlide);
        const slideDiv = document.createElement("div");
        slideDiv.classList.add("carousel-item");
        if (i === 0) slideDiv.classList.add("active");

        const rowDiv = document.createElement("div");
        rowDiv.classList.add("row", "g-3", "justify-content-center");

        slideItems.forEach(item => {
            const colDiv = document.createElement("div");
            colDiv.classList.add("col-12", "col-md-3");
            colDiv.dataset.itemId = item.id;

            const imagePath = getImagePath(item.image);
            colDiv.innerHTML = `
                <div class="card h-100 shadow-sm d-flex flex-column">
                    <div class="ratio ratio-1x1">
                        <img src="${imagePath}" class="w-100 h-100" alt="${item.name}" style="object-fit: cover;">
                    </div>
                    <div class="card-body d-flex flex-column">
                        <h5 class="card-title">${item.name}</h5>
                        <p class="card-text text-muted small">${item.description}</p>
                        <div class="mt-auto">
                            <div class="text-center text-warning fw-bold mb-2">${item.price} ₴</div>
                            <button class="btn btn-warning w-100 open-cart">До кошика</button>
                        </div>
                    </div>
                </div>
            `;
            rowDiv.appendChild(colDiv);
        });

        slideDiv.appendChild(rowDiv);
        desktopsContainer.appendChild(slideDiv);
    }
}

// =========================
// RENDER — кошик
// =========================

function renderCart(cart) {
    cartItemsContainer.innerHTML = "";

    cart.items.forEach(entry => {
        const p = entry.item_details;
        cartItemsContainer.innerHTML += `
            <div class="card p-3 shadow-sm">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h5>${p.name}</h5>
                        <p class="text-muted">${p.price} ₴ × ${entry.quantity}</p>
                    </div>
                    <div class="fw-bold">${p.total_price} ₴</div>
                </div>
            </div>
        `;
    });

    cartTotalField.textContent = `${cart.total} ₴`;
}

// =========================
// СТАРТ
// =========================

loadDesktops();

// =========================
// news.js — повністю
// =========================

document.addEventListener("DOMContentLoaded", () => {

    console.log("NEWS LIVE!!!");

    // Контейнер для новин
    const newsContainer = document.getElementById("news-list");

    if (!newsContainer) {
        console.error("Не знайдено контейнер для новин (#news-list)");
        return;
    }

    const API_BASE = "/api/v1";

    // =========================
    // Обробка шляху до зображення
    // =========================
    function getNewsImagePath(images) {
        if (!images || images.length === 0) return "/static/images/default.jpg";
        const img = images[0];
        return img.startsWith("http://") || img.startsWith("https://") ? img : `/static/${img}`;
    }

    // =========================
    // Завантаження новин
    // =========================
    async function loadNews() {
        try {
            const response = await fetch(`${API_BASE}/news`);
            if (!response.ok) throw new Error(`Помилка завантаження новин: ${response.status}`);
            const data = await response.json();
            renderNews(data);
        } catch (err) {
            console.error("Помилка завантаження новин:", err);
            newsContainer.innerHTML = `<div class="text-danger">Не вдалося завантажити новини</div>`;
        }
    }

    // =========================
    // Рендер новин
    // =========================
    function renderNews(items) {
        newsContainer.innerHTML = ""; // очищаємо контейнер

        if (!items || items.length === 0) {
            newsContainer.innerHTML = `<div class="text-muted">Новини відсутні</div>`;
            return;
        }

        items.forEach(item => {
            const imagePath = getNewsImagePath(item.images);

            const cardDiv = document.createElement("div");
            cardDiv.classList.add("col-12", "col-md-6", "col-lg-4", "mb-4");

            cardDiv.innerHTML = `
                <div class="card h-100 shadow-sm">
                    <div class="ratio ratio-16x9">
                        <img src="${imagePath}" class="card-img-top" alt="${item.name}" style="object-fit: cover;">
                    </div>
                    <div class="card-body d-flex flex-column">
                        <h5 class="card-title">${item.name}</h5>
                        <p class="card-text">${item.description}</p>
                        <div class="mt-auto text-muted small">${item.descriptionSecond || ""}</div>
                    </div>
                </div>
            `;

            newsContainer.appendChild(cardDiv);
        });
    }

    // =========================
    // Старт
    // =========================
    loadNews();

});

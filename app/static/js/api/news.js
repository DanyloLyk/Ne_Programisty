document.addEventListener("DOMContentLoaded", () => {
    console.log("NEWS LIVE!!!");

    const newsContainer = document.getElementById("news-list");
    const newsModal = new bootstrap.Modal(document.getElementById("newsModal"));
    const modalTitle = document.getElementById("newsModalTitle");
    const modalImage = document.getElementById("newsModalImage");
    const modalDescription = document.getElementById("newsModalDescription");
    const modalMore = document.getElementById("newsModalMore");

    // NEW
    const addNewsModal = new bootstrap.Modal(document.getElementById("addNewsModal"));
    const addNewsBtn = document.getElementById("addNewsBtn");
    const saveNewsBtn = document.getElementById("saveNewsBtn");

    const API_BASE = "/api/v1";

    function getImagePath(images) {
        if (!images || images.length === 0) return "/static/images/default.jpg";
        const img = images[0];
        return img.startsWith("http") ? img : `/static/${img}`;
    }

    async function loadNews() {
        try {
            const response = await fetch(`${API_BASE}/news`);
            if (!response.ok) throw new Error("Помилка завантаження новин");
            const data = await response.json();
            renderNews(data);
            attachNewsButtons();
        } catch (err) {
            console.error("Помилка новин:", err);
        }
    }

    function renderNews(items) {
        newsContainer.innerHTML = "";

        const isModerator = window.isModeratorMode ? window.isModeratorMode() : false;

        const perSlide = 3;
        for (let i = 0; i < items.length; i += perSlide) {
            const slideItems = items.slice(i, i + perSlide);

            const slideDiv = document.createElement("div");
            slideDiv.classList.add("carousel-item");
            if (i === 0) slideDiv.classList.add("active");

            const rowDiv = document.createElement("div");
            rowDiv.classList.add("row", "g-3");

            slideItems.forEach(item => {
                const colDiv = document.createElement("div");
                colDiv.classList.add("col-12", "col-md-4");
                colDiv.dataset.newsId = item.id;

                const imagePath = getImagePath(item.images);

                colDiv.innerHTML = `
                    <div class="card h-100 shadow-sm news-card border border-dark">
                        <div class="ratio ratio-16x9">
                            <img src="${imagePath}" class="card-img-top" style="object-fit: cover;">
                        </div>
                        <div class="card-body d-flex flex-column">
                            <h5 class="card-title text-warning">${item.name}</h5>
                            <p class="card-text small">${item.description}</p>
                            <div class="mt-auto d-flex gap-2">
                                <button class="btn btn-warning flex-fill open-news">
                                    <i class="fa-solid fa-info-circle me-1"></i> Детальніше
                                </button>
                                ${isModerator ? `
                                    <button class="btn btn-outline-warning edit-news-btn" data-news-id="${item.id}">
                                        <i class="fa-solid fa-pencil"></i>
                                    </button>
                                    <button class="btn btn-outline-danger delete-news-btn" data-news-id="${item.id}">
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
            newsContainer.appendChild(slideDiv);
        }

        attachNewsButtons();
        if (isModerator) {
            attachModeratorNewsButtons();
        }
    }

    function attachModeratorNewsButtons() {
        if (!window.isModeratorMode || !window.isModeratorMode()) return;
        
        // Кнопка редагування новини
        document.querySelectorAll(".edit-news-btn").forEach(btn => {
            btn.addEventListener("click", async () => {
                const newsId = btn.dataset.newsId;
                await editNews(newsId);
            });
        });

        // Кнопка видалення новини
        document.querySelectorAll(".delete-news-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                const newsId = btn.dataset.newsId;
                if (confirm("Видалити новину?")) {
                    deleteNews(newsId);
                }
            });
        });
    }

    async function editNews(newsId) {
        try {
            const response = await fetch(`${API_BASE}/news/${newsId}`);
            if (!response.ok) throw new Error("Failed to load news");

            const item = await response.json();
            
            document.getElementById("editNewsId").value = item.id;
            document.getElementById("editNewsTitle").value = item.name;
            document.getElementById("editNewsDesc").value = item.description;
            document.getElementById("editNewsDesc2").value = item.descriptionSecond || "";
            document.getElementById("editNewsImage").value = item.images ? item.images.join(", ") : "";

            const modal = new bootstrap.Modal(document.getElementById("editNewsModal"));
            modal.show();
        } catch (err) {
            console.error("Помилка завантаження новини:", err);
            window.showToast("Не вдалося завантажити новину", 'danger');
        }
    }

    async function deleteNews(newsId) {
        try {
            const headers = window.getAuthHeaders ? window.getAuthHeaders() : {};
            const response = await fetch(`${API_BASE}/news/${newsId}`, {
                method: "DELETE",
                headers
            });

            if (!response.ok) throw new Error("Failed to delete news");

            await loadNews();
            window.showToast("Новину видалено", 'success');
        } catch (err) {
            console.error("Помилка видалення новини:", err);
            window.showToast("Не вдалося видалити новину", 'danger');
        }
    }

    function attachNewsButtons() {
        const buttons = document.querySelectorAll(".open-news");
        buttons.forEach(button => {
            button.addEventListener("click", () => {
                const card = button.closest(".col-12, .col-md-4");
                const newsId = card.dataset.newsId;

                openNewsModal(newsId);
            });
        });
    }

    function openNewsModal(id) {
        fetch(`${API_BASE}/news/${id}`)
            .then(res => res.json())
            .then(item => {
                modalTitle.textContent = item.name;
                modalImage.src = getImagePath(item.images);
                modalDescription.textContent = item.description;
                modalMore.textContent = item.descriptionSecond || "";
                newsModal.show();
            })
            .catch(err => console.error("Помилка /news/:id", err));
    }

    // ================================
    // NEW — Відкрити модалку додавання
    // ================================
    addNewsBtn?.addEventListener("click", () => {
        addNewsModal.show();
    });

    // ================================
    // NEW — Створити новину
    // ================================
    saveNewsBtn?.addEventListener("click", async () => {
        const name = document.getElementById("addNewsTitle").value.trim();
        const description = document.getElementById("addNewsDesc").value.trim();
        const descriptionSecond = document.getElementById("addNewsDesc2").value.trim();
        const image = document.getElementById("addNewsImage").value.trim();

        if (!name || !description) {
            window.showToast("Заповніть обов'язкові поля (назва та опис)", 'warning');
            return;
        }

        const payload = {
            name,
            description,
            descriptionSecond,
            image_urls: image ? image.split(",").map(url => url.trim()) : []
        };

        try {
            const headers = window.getAuthHeaders ? window.getAuthHeaders() : {
                "Content-Type": "application/json"
            };
            
            const response = await fetch(`${API_BASE}/news`, {
                method: "POST",
                headers,
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.message || err.error || "Помилка створення новини");
            }

            const modal = bootstrap.Modal.getInstance(document.getElementById("addNewsModal"));
            modal.hide();
            
            // Очищаємо форму
            document.getElementById("addNewsTitle").value = "";
            document.getElementById("addNewsDesc").value = "";
            document.getElementById("addNewsDesc2").value = "";
            document.getElementById("addNewsImage").value = "";

            await loadNews();
            window.showToast("Новину створено", 'success');
        } catch (err) {
            console.error("Помилка додавання:", err);
            window.showToast(err.message, 'danger');
        }
    });

    // Оновлення новини
    document.getElementById("updateNewsBtn")?.addEventListener("click", async () => {
        const newsId = document.getElementById("editNewsId").value;
        const name = document.getElementById("editNewsTitle").value.trim();
        const description = document.getElementById("editNewsDesc").value.trim();
        const descriptionSecond = document.getElementById("editNewsDesc2").value.trim();
        const image = document.getElementById("editNewsImage").value.trim();

        if (!name || !description) {
            window.showToast("Заповніть обов'язкові поля (назва та опис)", 'warning');
            return;
        }

        const payload = {
            name,
            description,
            descriptionSecond,
            image_urls: image ? image.split(",").map(url => url.trim()) : []
        };

        try {
            const headers = window.getAuthHeaders ? window.getAuthHeaders() : {
                "Content-Type": "application/json"
            };
            
            const response = await fetch(`${API_BASE}/news/${newsId}`, {
                method: "PATCH",
                headers,
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.message || err.error || "Помилка оновлення новини");
            }

            const modal = bootstrap.Modal.getInstance(document.getElementById("editNewsModal"));
            modal.hide();
            
            await loadNews();
            window.showToast("Новину оновлено", 'success');
        } catch (err) {
            console.error("Помилка оновлення:", err);
            window.showToast(err.message, 'danger');
        }
    });

    // Слухаємо зміни режиму модератора
    window.addEventListener("moderatorModeChanged", () => {
        loadNews();
    });

    loadNews();
});

document.addEventListener("DOMContentLoaded", () => {
    console.log("NEWS LIVE!!!");

    const newsContainer = document.getElementById("news-list");
    const newsModal = new bootstrap.Modal(document.getElementById("newsModal"));
    const modalTitle = document.getElementById("newsModalTitle");
    const modalImageContainer = document.getElementById("newsModalImages"); // carousel-inner
    const modalDescription = document.getElementById("newsModalDescription");
    const modalMore = document.getElementById("newsModalMore");

    // Модалка додавання новини
    const addNewsModal = new bootstrap.Modal(document.getElementById("addNewsModal"));
    const addNewsBtn = document.getElementById("addNewsBtn");
    const saveNewsBtn = document.getElementById("saveNewsBtn");
    
    // Модалка видалення
    const confirmDeleteModal = new bootstrap.Modal(document.getElementById("confirmDeleteModal"));

    const API_BASE = "/api/v1";

    function getImagePath(images) {
        if (!images || images.length === 0) return "/static/images/default.jpg";
        const img = images[0];
        return img.startsWith("http") ? img : `/static/${img}`;
    }

    // ================================
    // Завантаження та рендер новин
    // ================================
    async function loadNews() {
        try {
            const response = await fetch(`${API_BASE}/news`);
            if (!response.ok) throw new Error("Помилка завантаження новин");
            const data = await response.json();
            renderNews(data);
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
        if (isModerator) attachModeratorNewsButtons();
    }

    // ================================
    // Кнопки модератора
    // ================================
    function attachModeratorNewsButtons() {
        if (!window.isModeratorMode || !window.isModeratorMode()) return;

        document.querySelectorAll(".edit-news-btn").forEach(btn => {
            btn.addEventListener("click", async () => {
                const newsId = btn.dataset.newsId;
                await editNews(newsId);
            });
        });

        document.querySelectorAll(".delete-news-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                const newsId = btn.dataset.newsId;
                showDeleteConfirmNews(newsId, "новину");
            });
        });
    }

    function showDeleteConfirmNews(newsId, type) {
        document.getElementById("confirmDeleteText").textContent = 
            `Ви впевнені, що хочете видалити цю ${type}?`;
        
        const confirmBtn = document.getElementById("confirmDeleteBtn");
        const cancelBtn = document.querySelector("#confirmDeleteModal .btn-secondary");
        const closeBtn = document.querySelector("#confirmDeleteModal .btn-close");
        
        confirmBtn.onclick = async () => {
            try {
                const headers = window.getAuthHeaders ? window.getAuthHeaders() : {};
                const response = await fetch(`${API_BASE}/news/${newsId}`, {
                    method: "DELETE",
                    headers
                });

                if (!response.ok) throw new Error("Failed to delete news");

                confirmDeleteModal.hide();
                await loadNews();
                window.showToast("Новину видалено", 'success');
            } catch (err) {
                console.error("Помилка видалення новини:", err);
                window.showToast("Не вдалося видалити новину", 'danger');
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

    async function editNews(newsId) {
        try {
            const response = await fetch(`${API_BASE}/news/${newsId}`);
            if (!response.ok) throw new Error("Не вдалося завантажити новину");
            const item = await response.json();

            document.getElementById("editNewsId").value = item.id;
            document.getElementById("editNewsTitle").value = item.name;
            document.getElementById("editNewsDesc").value = item.description;
            document.getElementById("editNewsDesc2").value = item.descriptionSecond || "";
            document.getElementById("editNewsImage").value = item.images ? item.images.join(", ") : "";

            const modal = new bootstrap.Modal(document.getElementById("editNewsModal"));
            modal.show();
        } catch (err) {
            console.error(err);
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
            if (!response.ok) throw new Error("Помилка видалення новини");
            await loadNews();
            window.showToast("Новину видалено", 'success');
        } catch (err) {
            console.error(err);
            window.showToast("Не вдалося видалити новину", 'danger');
        }
    }

    // ================================
    // Відкрити модалку новини
    // ================================
    function attachNewsButtons() {
        document.querySelectorAll(".open-news").forEach(button => {
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
            .then(news => {
                modalTitle.textContent = news.name;
                modalDescription.textContent = news.description;
                modalMore.textContent = news.descriptionSecond || "";

                // Очистити попередні фото
                modalImageContainer.innerHTML = "";

                const images = (news.images || []).map(img => img.startsWith('http') ? img : `/static/${img}`);
                if (images.length === 0) images.push('/static/images/default.jpg');

                images.forEach((img, index) => {
                    const div = document.createElement('div');
                    div.classList.add('carousel-item');
                    if (index === 0) div.classList.add('active');

                    const imageEl = document.createElement('img');
                    imageEl.src = img;
                    imageEl.classList.add('d-block', 'w-100');
                    imageEl.style.maxHeight = '300px';
                    imageEl.style.objectFit = 'cover';
                    imageEl.onerror = () => { imageEl.src = 'https://via.placeholder.com/600x400?text=No+Image'; };

                    div.appendChild(imageEl);
                    modalImageContainer.appendChild(div);
                });

                // Ініціалізація каруселі
                new bootstrap.Carousel(document.getElementById('newsModalCarousel'), { interval:3000 });

                newsModal.show();
            })
            .catch(err => console.error("Помилка /news/:id", err));
    }

    // ================================
    // Додати новину
    // ================================
    addNewsBtn?.addEventListener("click", () => addNewsModal.show());

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
            const headers = window.getAuthHeaders ? window.getAuthHeaders() : { "Content-Type": "application/json" };
            const response = await fetch(`${API_BASE}/news`, {
                method: "POST",
                headers,
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.message || err.error || "Помилка створення новини");
            }

            bootstrap.Modal.getInstance(document.getElementById("addNewsModal")).hide();

            // Очистка форми
            document.getElementById("addNewsTitle").value = "";
            document.getElementById("addNewsDesc").value = "";
            document.getElementById("addNewsDesc2").value = "";
            document.getElementById("addNewsImage").value = "";

            await loadNews();
            window.showToast("Новину створено", 'success');
        } catch (err) {
            console.error(err);
            window.showToast(err.message, 'danger');
        }
    });

    // ================================
    // Оновити новину
    // ================================
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
            const headers = window.getAuthHeaders ? window.getAuthHeaders() : { "Content-Type": "application/json" };
            const response = await fetch(`${API_BASE}/news/${newsId}`, {
                method: "PATCH",
                headers,
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.message || err.error || "Помилка оновлення новини");
            }

            bootstrap.Modal.getInstance(document.getElementById("editNewsModal")).hide();
            await loadNews();
            window.showToast("Новину оновлено", 'success');
        } catch (err) {
            console.error(err);
            window.showToast(err.message, 'danger');
        }
    });

    // ================================
    // Слухаємо зміни режиму модератора
    // ================================
    window.addEventListener("moderatorModeChanged", loadNews);

    // Завантаження новин при старті
    loadNews();
});

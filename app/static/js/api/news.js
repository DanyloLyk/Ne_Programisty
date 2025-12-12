document.addEventListener("DOMContentLoaded", () => {
    console.log("NEWS LIVE!!!");

    const newsContainer = document.getElementById("news-list");
    const newsModal = new bootstrap.Modal(document.getElementById("newsModal"));
    const modalTitle = document.getElementById("newsModalTitle");
    const modalImage = document.getElementById("newsModalImage");
    const modalDescription = document.getElementById("newsModalDescription");
    const modalMore = document.getElementById("newsModalMore");

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
                    <div class="card h-100 shadow-sm news-card">
                        <div class="ratio ratio-16x9">
                            <img src="${imagePath}" class="card-img-top" style="object-fit: cover;">
                        </div>
                        <div class="card-body d-flex flex-column">
                            <h5 class="card-title">${item.name}</h5>
                            <p class="card-text small">${item.description}</p>
                            <button class="btn btn-warning mt-auto open-news">Детальніше</button>
                        </div>
                    </div>
                `;
                rowDiv.appendChild(colDiv);
            });

            slideDiv.appendChild(rowDiv);
            newsContainer.appendChild(slideDiv);
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

    loadNews();
});

// Управління відгуками
document.addEventListener("DOMContentLoaded", () => {
    const feedbacksContainer = document.getElementById("feedbacks-list");
    const feedbackForm = document.getElementById("feedback-form");
    const feedbackMessage = document.getElementById("feedback-message");
    const addFeedbackBtn = document.getElementById("addFeedbackBtn");
    const editFeedbackModal = new bootstrap.Modal(document.getElementById("editFeedbackModal"));
    const confirmDeleteModal = new bootstrap.Modal(document.getElementById("confirmDeleteModal"));
    const addFeedbackUserModal = new bootstrap.Modal(document.getElementById("addFeedbackUserModal"));
    const API_BASE = "/api/v1";

    async function loadFeedbacks() {
        try {
            const response = await fetch(`${API_BASE}/feedbacks`);
            if (!response.ok) throw new Error("Failed to load feedbacks");

            const feedbacks = await response.json();
            renderFeedbacks(feedbacks);
        } catch (err) {
            console.error("Помилка завантаження відгуків:", err);
            feedbacksContainer.innerHTML = `<div class="text-danger text-center p-4">Помилка завантаження відгуків</div>`;
        }
    }

    function renderFeedbacks(feedbacks) {
        feedbacksContainer.innerHTML = "";

        if (!feedbacks || feedbacks.length === 0) {
            feedbacksContainer.innerHTML = `<div class="text-muted text-center p-4 col-12">Відгуків поки немає</div>`;
            return;
        }

        feedbacks.forEach(feedback => {
            const colDiv = document.createElement("div");
            colDiv.classList.add("col-12", "col-md-6", "col-lg-4");
            colDiv.id = `feedback-${feedback.id}`;

            const isModerator = window.isModeratorMode();
            
            colDiv.innerHTML = `
                <div class="card h-100 shadow-sm border border-warning">
                    <div class="card-body d-flex flex-column">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h5 class="card-title text-warning">${feedback.title}</h5>
                            ${isModerator ? `
                                <div class="d-flex gap-2">
                                    <button class="btn btn-sm btn-outline-warning edit-feedback-btn" data-feedback-id="${feedback.id}">
                                        <i class="fa-solid fa-pencil"></i>
                                    </button>
                                    <button class="btn btn-sm btn-outline-danger delete-feedback-btn" data-feedback-id="${feedback.id}">
                                        <i class="fa-solid fa-trash"></i>
                                    </button>
                                </div>
                            ` : ""}
                        </div>
                        <p class="card-text text-warning small mb-2">${feedback.description}</p>
                        <div class="mt-auto">
                            <small class="text-warning">
                                <i class="fa-solid fa-user me-1"></i>
                                ${feedback.user?.nickname || "Анонімний користувач"}
                            </small>
                        </div>
                    </div>
                </div>
            `;
            feedbacksContainer.appendChild(colDiv);
        });

        attachFeedbackButtons();
    }

    function attachFeedbackButtons() {
        if (!window.isModeratorMode()) return;

        document.querySelectorAll(".edit-feedback-btn").forEach(btn => {
            btn.addEventListener("click", async () => {
                const feedbackId = btn.dataset.feedbackId;
                await editFeedback(feedbackId);
            });
        });

        document.querySelectorAll(".delete-feedback-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                const feedbackId = btn.dataset.feedbackId;
                showDeleteConfirm(feedbackId, "відгук");
            });
        });
    }

    async function editFeedback(feedbackId) {
        try {
            const response = await fetch(`${API_BASE}/feedbacks/${feedbackId}`);
            if (!response.ok) throw new Error("Failed to load feedback");

            const feedback = await response.json();
            
            document.getElementById("editFeedbackId").value = feedback.id;
            document.getElementById("editFeedbackTitle").value = feedback.title;
            document.getElementById("editFeedbackDescription").value = feedback.description;

            editFeedbackModal.show();
        } catch (err) {
            console.error("Помилка завантаження відгуку:", err);
            window.showToast("Не вдалося завантажити відгук", 'danger');
        }
    }

    // Обробка форми відгуку
    feedbackForm?.addEventListener("submit", async (e) => {
        e.preventDefault();

        const title = document.getElementById("feedback-title").value.trim();
        const description = document.getElementById("feedback-description").value.trim();

        if (!title || !description) {
            feedbackMessage.innerHTML = `<div class="alert alert-warning">Заповніть всі поля</div>`;
            return;
        }

        try {
            const headers = window.getAuthHeaders();
            const response = await fetch(`${API_BASE}/feedbacks`, {
                method: "POST",
                headers,
                body: JSON.stringify({ title, description })
            });

            if (!response.ok) {
                if (response.status === 401) {
                    feedbackMessage.innerHTML = `<div class="alert alert-danger">Необхідна авторизація</div>`;
                    return;
                }
                throw new Error("Failed to create feedback");
            }

            feedbackMessage.innerHTML = `<div class="alert alert-success">Відгук успішно додано!</div>`;
            feedbackForm.reset();
            await loadFeedbacks();

            setTimeout(() => {
                feedbackMessage.innerHTML = "";
            }, 3000);
        } catch (err) {
            console.error("Помилка створення відгуку:", err);
            feedbackMessage.innerHTML = `<div class="alert alert-danger">Помилка при додаванні відгуку</div>`;
        }
    });

    // Оновлення відгуку
    document.getElementById("updateFeedbackBtn")?.addEventListener("click", async () => {
        const feedbackId = document.getElementById("editFeedbackId").value;
        const title = document.getElementById("editFeedbackTitle").value.trim();
        const description = document.getElementById("editFeedbackDescription").value.trim();

        if (!title || !description) {
            window.showToast("Заповніть всі поля", 'warning ');
            return;
        }

        try {
            const headers = window.getAuthHeaders();
            const response = await fetch(`${API_BASE}/feedbacks/${feedbackId}`, {
                method: "PATCH",
                headers,
                body: JSON.stringify({ title, description })
            });

            if (!response.ok) throw new Error("Failed to update feedback");

            editFeedbackModal.hide();
            await loadFeedbacks();
            window.showToast("Відгук оновлено", 'success');
        } catch (err) {
            console.error("Помилка оновлення відгуку:", err);
            window.showToast("Не вдалося оновити відгук", 'danger');
        }
    });

    function showDeleteConfirm(feedbackId, type) {
        document.getElementById("confirmDeleteText").textContent = 
            `Ви впевнені, що хочете видалити цей ${type}?`;
        
        const confirmBtn = document.getElementById("confirmDeleteBtn");
        const cancelBtn = document.querySelector("#confirmDeleteModal .btn-secondary");
        
        confirmBtn.onclick = async () => {
            try {
                const headers = window.getAuthHeaders();
                const response = await fetch(`${API_BASE}/feedbacks/${feedbackId}`, {
                    method: "DELETE",
                    headers
                });

                if (!response.ok) throw new Error("Failed to delete feedback");

                confirmDeleteModal.hide();
                await loadFeedbacks();
                window.showToast("Відгук видалено", 'success');
            } catch (err) {
                console.error("Помилка видалення відгуку:", err);
                window.showToast("Не вдалося видалити відгук", 'danger');
            }
        };
        
        cancelBtn.onclick = () => {
            confirmDeleteModal.hide();
        };

        confirmDeleteModal.show();
    }

    // Додавання відгуку від користувача (для модератора)
    addFeedbackBtn?.addEventListener("click", () => {
        addFeedbackUserModal.show();
    });

    document.getElementById("saveFeedbackUserBtn")?.addEventListener("click", async () => {
        const userId = parseInt(document.getElementById("addFeedbackUserId").value);
        const title = document.getElementById("addFeedbackUserTitle").value.trim();
        const description = document.getElementById("addFeedbackUserDescription").value.trim();

        if (!userId || !title || !description) {
            window.showToast("Заповніть всі поля", 'warning ');
            return;
        }

        try {
            const headers = window.getAuthHeaders();
            const response = await fetch(`${API_BASE}/feedbacks/user/${userId}`, {
                method: "POST",
                headers,
                body: JSON.stringify({ title, description })
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.message || "Failed to create feedback");
            }

            addFeedbackUserModal.hide();
            // Очищаємо форму
            document.getElementById("addFeedbackUserId").value = "";
            document.getElementById("addFeedbackUserTitle").value = "";
            document.getElementById("addFeedbackUserDescription").value = "";
            
            await loadFeedbacks();
            window.showToast("Відгук від користувача створено", 'success');
        } catch (err) {
            console.error("Помилка створення відгуку:", err);
            window.showToast(err.message || "Не вдалося створити відгук", 'danger');
        }
    });

    // Слухаємо зміни режиму модератора
    window.addEventListener("moderatorModeChanged", () => {
        loadFeedbacks();
    });

    // Завантаження при старті
    loadFeedbacks();
});


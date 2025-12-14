// Управління користувачами
document.addEventListener("DOMContentLoaded", () => {
    const usersContainer = document.getElementById("users-list");
    const addUserBtn = document.getElementById("addUserBtn");
    const addUserModal = new bootstrap.Modal(document.getElementById("addUserModal"));
    const editUserModal = new bootstrap.Modal(document.getElementById("editUserModal"));
    const confirmDeleteModal = new bootstrap.Modal(document.getElementById("confirmDeleteModal"));
    const API_BASE = "/api/v1";

    async function loadUsers() {
        try {
            const response = await fetch(`${API_BASE}/users/`);
            if (!response.ok) throw new Error("Failed to load users");

            const users = await response.json();
            renderUsers(users);
        } catch (err) {
            console.error("Помилка завантаження користувачів:", err);
            usersContainer.innerHTML = `<div class="text-danger text-center p-4">Помилка завантаження користувачів</div>`;
        }
    }

    function renderUsers(users) {
        usersContainer.innerHTML = "";

        if (!users || users.length === 0) {
            usersContainer.innerHTML = `<div class="text-muted text-center p-4 col-12">Користувачів немає</div>`;
            return;
        }

        users.forEach(user => {
            const colDiv = document.createElement("div");
            colDiv.classList.add("col-12", "col-md-6", "col-lg-4");
            colDiv.id = `user-${user.id}`;

            const isModerator = window.isModeratorMode();
            
            const statusBadgeClass = {
                "Admin": "bg-danger",
                "Moder": "bg-warning",
                "User": "bg-info"
            }[user.status] || "bg-secondary";

            const privilegeBadgeClass = {
                "VIP": "bg-purple",
                "Diamond": "bg-primary",
                "Gold": "bg-warning",
                "Default": "bg-secondary"
            }[user.privilege] || "bg-secondary";

            colDiv.innerHTML = `
                <div class="card h-100 shadow-sm border border-warning">
                    <div class="card-body d-flex flex-column">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h5 class="card-title text-warning">${user.nickname}</h5>
                            ${isModerator ? `
                                <div class="d-flex gap-2">
                                    <button class="btn btn-sm btn-outline-warning edit-user-btn" data-user-id="${user.id}">
                                        <i class="fa-solid fa-pencil"></i>
                                    </button>
                                    <button class="btn btn-sm btn-outline-danger delete-user-btn" data-user-id="${user.id}">
                                        <i class="fa-solid fa-trash"></i>
                                    </button>
                                </div>
                            ` : ""}
                        </div>
                        <p class="text-muted small mb-2">
                            <i class="fa-solid fa-envelope me-1"></i> ${user.email}
                        </p>
                        <div class="mb-2">
                            <span class="badge ${statusBadgeClass} me-1">${user.status}</span>
                            <span class="badge ${privilegeBadgeClass}">${user.privilege}</span>
                        </div>
                        ${user.discount_percent ? `
                            <p class="text-warning small mb-0">
                                <i class="fa-solid fa-percent me-1"></i> Знижка: ${user.discount_percent}%
                            </p>
                        ` : ""}
                    </div>
                </div>
            `;
            usersContainer.appendChild(colDiv);
        });

        attachUserButtons();
    }

    function attachUserButtons() {
        if (!window.isModeratorMode()) return;

        document.querySelectorAll(".edit-user-btn").forEach(btn => {
            btn.addEventListener("click", async () => {
                const userId = btn.dataset.userId;
                await editUser(userId);
            });
        });

        document.querySelectorAll(".delete-user-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                const userId = btn.dataset.userId;
                showDeleteConfirm(userId, "користувача");
            });
        });
    }

    async function editUser(userId) {
        try {
            const headers = window.getAuthHeaders();
            const response = await fetch(`${API_BASE}/users/${userId}`, { headers });
            if (!response.ok) throw new Error("Failed to load user");

            const user = await response.json();
            
            document.getElementById("editUserId").value = user.id;
            document.getElementById("editUserNickname").value = user.nickname;
            document.getElementById("editUserEmail").value = user.email;
            document.getElementById("editUserStatus").value = user.status;
            document.getElementById("editUserPrivilege").value = user.privilege;
            document.getElementById("editUserPassword").value = "";

            editUserModal.show();
        } catch (err) {
            console.error("Помилка завантаження користувача:", err);
            alert("Не вдалося завантажити користувача");
        }
    }

    // Додавання користувача
    addUserBtn?.addEventListener("click", () => {
        addUserModal.show();
    });

    document.getElementById("saveUserBtn")?.addEventListener("click", async () => {
        const nickname = document.getElementById("addUserNickname").value.trim();
        const email = document.getElementById("addUserEmail").value.trim();
        const password = document.getElementById("addUserPassword").value;
        const passwordConfirm = document.getElementById("addUserPasswordConfirm").value;
        const status = document.getElementById("addUserStatus").value;
        const privilege = document.getElementById("addUserPrivilege").value;

        if (!nickname || !email || !password) {
            alert("Заповніть всі обов'язкові поля");
            return;
        }

        if (password !== passwordConfirm) {
            alert("Паролі не співпадають");
            return;
        }

        try {
            const response = await fetch(`${API_BASE}/register/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    nickname,
                    email,
                    password,
                    password_confirm: passwordConfirm
                })
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.message || "Failed to create user");
            }

            // Після реєстрації оновлюємо користувача через API (якщо є така можливість)
            // Або просто перезавантажуємо список
            addUserModal.hide();
            await loadUsers();
            alert("Користувача створено");
        } catch (err) {
            console.error("Помилка створення користувача:", err);
            alert(err.message || "Не вдалося створити користувача");
        }
    });

    // Оновлення користувача
    document.getElementById("updateUserBtn")?.addEventListener("click", async () => {
        const userId = document.getElementById("editUserId").value;
        const nickname = document.getElementById("editUserNickname").value.trim();
        const email = document.getElementById("editUserEmail").value.trim();
        const status = document.getElementById("editUserStatus").value;
        const privilege = document.getElementById("editUserPrivilege").value;
        const password = document.getElementById("editUserPassword").value;

        const data = { nickname, email, status, privilege };
        if (password) {
            data.password = password;
        }

        try {
            const headers = window.getAuthHeaders();
            const response = await fetch(`${API_BASE}/user/${userId}`, {
                method: "PATCH",
                headers,
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.message || "Failed to update user");
            }

            editUserModal.hide();
            await loadUsers();
            alert("Користувача оновлено");
        } catch (err) {
            console.error("Помилка оновлення користувача:", err);
            alert(err.message || "Не вдалося оновити користувача");
        }
    });

    function showDeleteConfirm(userId, type) {
        document.getElementById("confirmDeleteText").textContent = 
            `Ви впевнені, що хочете видалити цього ${type}?`;
        
        const confirmBtn = document.getElementById("confirmDeleteBtn");
        confirmBtn.onclick = async () => {
            try {
                const headers = window.getAuthHeaders();
                const response = await fetch(`${API_BASE}/user/${userId}`, {
                    method: "DELETE",
                    headers
                });

                if (!response.ok) throw new Error("Failed to delete user");

                confirmDeleteModal.hide();
                await loadUsers();
                alert("Користувача видалено");
            } catch (err) {
                console.error("Помилка видалення користувача:", err);
                alert("Не вдалося видалити користувача");
            }
        };

        confirmDeleteModal.show();
    }

    // Слухаємо зміни режиму модератора
    window.addEventListener("moderatorModeChanged", () => {
        loadUsers();
    });

    // Завантаження при старті
    loadUsers();
});



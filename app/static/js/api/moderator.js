// Режим модератора - перемикання та управління
document.addEventListener("DOMContentLoaded", () => {
    const MODERATOR_MODE_KEY = "moderatorMode";
    let isModeratorMode = localStorage.getItem(MODERATOR_MODE_KEY) === "true";

    const toggleBtn = document.getElementById("moderatorToggleBtn");
    const toggleBtnBottom = document.getElementById("moderatorToggleBtnBottom");
    const toggleText = document.getElementById("moderatorToggleText");
    const toggleTextBottom = document.getElementById("moderatorToggleTextBottom");

    function updateModeratorUI() {
        const moderatorElements = document.querySelectorAll(".moderator-only");
        moderatorElements.forEach(el => {
            el.style.display = isModeratorMode ? "block" : "none";
        });

        const text = isModeratorMode ? "Режим модератора" : "Режим клієнта";
        if (toggleText) toggleText.textContent = text;
        if (toggleTextBottom) toggleTextBottom.textContent = text;

        // Додаємо клас для стилізації
        document.body.classList.toggle("moderator-mode", isModeratorMode);
    }

    function toggleModeratorMode() {
        isModeratorMode = !isModeratorMode;
        localStorage.setItem(MODERATOR_MODE_KEY, isModeratorMode.toString());
        updateModeratorUI();
        
        // Викликаємо подію для інших скриптів
        window.dispatchEvent(new CustomEvent("moderatorModeChanged", { 
            detail: { isModerator: isModeratorMode } 
        }));
    }

    if (toggleBtn) {
        toggleBtn.addEventListener("click", toggleModeratorMode);
    }
    if (toggleBtnBottom) {
        toggleBtnBottom.addEventListener("click", toggleModeratorMode);
    }

    // Ініціалізація
    updateModeratorUI();

    // Експортуємо для використання в інших скриптах
    window.isModeratorMode = () => isModeratorMode;
    window.getAuthHeaders = () => {
        const token = localStorage.getItem("accessToken") || (typeof get_token === 'function' ? get_token() : null);
        if (!token) {
            console.warn("Токен не знайдено в localStorage");
            return {
                "Accept": "application/json",
                "Content-Type": "application/json"
            };
        }
        return {
            "Authorization": `Bearer ${token}`,
            "Accept": "application/json",
            "Content-Type": "application/json"
        };
    };
});


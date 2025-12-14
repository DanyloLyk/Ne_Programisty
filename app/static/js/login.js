document.addEventListener("DOMContentLoaded", function() {
  const loginModal = document.getElementById("login-modal");
  const signupModal = document.getElementById("signup-modal");
  const forgotPasswordModal = document.getElementById("forgot-password-modal");
  const closeLogin = document.getElementById("close-login");
  const closeSignup = document.getElementById("close-signup");
  const closeForgotPassword = document.getElementById("close-forgot-password");
  const openSignup = document.getElementById("open-signup");
  const openLogin = document.getElementById("open-login");
  const openForgotPassword = document.getElementById("open-forgot-password");
  const backToLogin = document.getElementById("back-to-login");
  const backToForgot = document.getElementById("back-to-forgot");
  const loginDesktop = document.getElementById("login-desktop");
  const loginMobile = document.getElementById("login-mobile");
  const forgotPasswordForm = document.getElementById("forgot-password-form");
  const resetPasswordForm = document.getElementById("reset-password-form");
  const forgotMessage = document.getElementById("forgot-message");
  const resetMessage = document.getElementById("reset-message");
  const cartLinks = document.querySelectorAll('[data-cart-link="true"]');
  const isAuthenticated = document.body.dataset.userAuth === "true";

  // Автоматичний вхід для тестування
  const autoLoginForTesting = async () => {
    // Перевіряємо, чи користувач вже авторизований
    if (document.body.dataset.userAuth === "true") {
      console.log("Користувач вже авторизований");
      return;
    }

    console.log("Спроба автоматичного входу для тестування...");

    try {
      const response = await fetch("/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
          email: "dann160309@gmail.com",
          password: "123"
        }),
        redirect: "manual" // Не слідувати за редіректами автоматично
      });

      if (response.status === 302) {
        // Успішний вхід - перезавантажуємо сторінку
        console.log("Автоматичний вхід успішний, перезавантаження сторінки...");
        window.location.reload();
      } else {
        console.log("Автоматичний вхід не вдався, статус:", response.status);
      }
    } catch (error) {
      console.error("Помилка автоматичного входу:", error);
    }
  };

  if (!loginModal && !signupModal && !forgotPasswordModal) return;

  // Overlay для закриття
  const overlay = document.createElement("div");
  overlay.style.cssText = `
    display:none;
    position:fixed;
    top:0;
    left:0;
    width:100%;
    height:100%;
    background:rgba(0,0,0,0.5);
    z-index:10999;
  `;
  document.body.appendChild(overlay);

  const toggleScroll = (disable) => {
    document.body.style.overflow = disable ? "hidden" : "auto";
  };

  const closeAll = () => {
    loginModal?.classList.remove("show");
    signupModal?.classList.remove("show");
    forgotPasswordModal?.classList.remove("show");
    overlay.style.display = "none";
    toggleScroll(false);
    // Сховати форми скидання пароля при закритті
    if (forgotPasswordForm) forgotPasswordForm.style.display = "block";
    if (resetPasswordForm) resetPasswordForm.style.display = "none";
    if (forgotMessage) forgotMessage.innerHTML = "";
    if (resetMessage) resetMessage.innerHTML = "";
  };

  const openModal = (modal) => {
    loginModal?.classList.remove("show");
    signupModal?.classList.remove("show");
    forgotPasswordModal?.classList.remove("show");
    modal?.classList.add("show");
    overlay.style.display = "block";
    toggleScroll(true);
  };

  // Відкриття модалки
  loginDesktop?.addEventListener("click", () => openModal(loginModal));
  loginMobile?.addEventListener("click", () => openModal(loginModal));
  openSignup?.addEventListener("click", (e) => {
    e.preventDefault();
    openModal(signupModal);
  });
  openLogin?.addEventListener("click", (e) => {
    e.preventDefault();
    openModal(loginModal);
  });
  openForgotPassword?.addEventListener("click", (e) => {
    e.preventDefault();
    openModal(forgotPasswordModal);
  });

  // Закриття модалки
  closeLogin?.addEventListener("click", closeAll);
  closeSignup?.addEventListener("click", closeAll);
  closeForgotPassword?.addEventListener("click", closeAll);
  overlay.addEventListener("click", closeAll);

  // Escape key
  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeAll();
  });

  // Обробка форми відновлення пароля
  forgotPasswordForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const email = document.getElementById("forgot-email").value.trim();
    
    if (!email) {
      forgotMessage.innerHTML = '<div class="text-danger">Введіть електронну пошту</div>';
      return;
    }

    try {
      const response = await fetch("/api/v1/auth/forgot-password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (response.ok) {
        forgotMessage.innerHTML = '<div class="text-success">Посилання для скидання пароля відправлено на вашу електронну пошту</div>';
        // Показати форму для введення токена
        forgotPasswordForm.style.display = "none";
        resetPasswordForm.style.display = "block";
        // Показати посилання для розробки
        if (data.reset_link) {
          console.log("Reset link:", data.reset_link);
        }
        if (data.debug_token) {
          console.log("Debug token:", data.debug_token);
        }
      } else {
        forgotMessage.innerHTML = `<div class="text-danger">${data.message || "Помилка при відправці"}</div>`;
      }
    } catch (error) {
      console.error("Помилка:", error);
      forgotMessage.innerHTML = '<div class="text-danger">Помилка мережі. Спробуйте пізніше.</div>';
    }
  });

  // Обробка форми скидання пароля
  resetPasswordForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const token = document.getElementById("reset-token").value.trim();
    const password = document.getElementById("reset-password").value.trim();
    const confirm = document.getElementById("reset-confirm").value.trim();
    
    if (!token || !password || !confirm) {
      resetMessage.innerHTML = '<div class="text-danger">Заповніть всі поля</div>';
      return;
    }

    if (password !== confirm) {
      resetMessage.innerHTML = '<div class="text-danger">Паролі не співпадають</div>';
      return;
    }

    try {
      const response = await fetch("/api/v1/auth/reset-password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          token,
          new_password: password,
          confirm_password: confirm,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        resetMessage.innerHTML = '<div class="text-success">Пароль успішно змінено! Тепер ви можете увійти.</div>';
        // Через 3 секунди закрити модалку і відкрити login
        setTimeout(() => {
          closeAll();
          openModal(loginModal);
        }, 3000);
      } else {
        resetMessage.innerHTML = `<div class="text-danger">${data.message || "Помилка при зміні пароля"}</div>`;
      }
    } catch (error) {
      console.error("Помилка:", error);
      resetMessage.innerHTML = '<div class="text-danger">Помилка мережі. Спробуйте пізніше.</div>';
    }
  });

  // Переключення між формами
  backToLogin?.addEventListener("click", (e) => {
    e.preventDefault();
    closeAll();
    openModal(loginModal);
  });

  backToForgot?.addEventListener("click", (e) => {
    e.preventDefault();
    resetPasswordForm.style.display = "none";
    forgotPasswordForm.style.display = "block";
    forgotMessage.innerHTML = "";
    resetMessage.innerHTML = "";
  });

  // For buttons that require authentication (e.g., add-to-cart on public pages)
  const requireAuthBtns = document.querySelectorAll('.require-auth');
  if (requireAuthBtns.length > 0) {
    requireAuthBtns.forEach(btn => {
      // initialize Bootstrap tooltip
      try {
        new bootstrap.Tooltip(btn);
      } catch (e) {
        // ignore if tooltip init fails
      }

      btn.addEventListener('click', (e) => {
        e.preventDefault();
        // On mobile/tap or desktop click, open login modal
        if (loginModal) openModal(loginModal);
      });
    });
  }

  // Запускаємо автоматичний вхід через 1 секунду після завантаження
  autoLoginForTesting();
});

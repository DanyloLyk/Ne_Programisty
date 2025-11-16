document.addEventListener("DOMContentLoaded", function() {
  const loginModal = document.getElementById("login-modal");
  const signupModal = document.getElementById("signup-modal");
  const closeLogin = document.getElementById("close-login");
  const closeSignup = document.getElementById("close-signup");
  const openSignup = document.getElementById("open-signup");
  const openLogin = document.getElementById("open-login");
  const loginDesktop = document.getElementById("login-desktop");
  const loginMobile = document.getElementById("login-mobile");

  // Створюємо оверлей для блокування всього фону
  const overlay = document.createElement("div");
  overlay.style.cssText = `
    display:none;
    position:fixed;
    top:0;
    left:0;
    width:100%;
    height:100%;
    background:rgba(0,0,0,0.5);
    z-index:9999; /* обов'язково вище всіх кнопок */
  `;
  document.body.appendChild(overlay);

  // Функція відкриття модалки
  const openModal = (modal) => {
    loginModal?.classList.remove("show");
    signupModal?.classList.remove("show");
    modal?.classList.add("show");
    overlay.style.display = "block"; // показати оверлей
  };

  // Функція закриття всіх модалок
  const closeAll = () => {
    loginModal?.classList.remove("show");
    signupModal?.classList.remove("show");
    overlay.style.display = "none"; // ховаємо оверлей
  };

  // Події для кнопок
  loginDesktop?.addEventListener("click", () => openModal(loginModal));
  loginMobile?.addEventListener("click", () => openModal(loginModal));
  closeLogin?.addEventListener("click", closeAll);
  closeSignup?.addEventListener("click", closeAll);
  openSignup?.addEventListener("click", (e) => {
    e.preventDefault();
    openModal(signupModal);
  });
  openLogin?.addEventListener("click", (e) => {
    e.preventDefault();
    openModal(loginModal);
  });

  // Клік на оверлей закриває модалки
  overlay.addEventListener("click", closeAll);

  // Клік поза модалкою закриває модалки
  window.addEventListener("click", (e) => {
    if (e.target === loginModal || e.target === signupModal) closeAll();
  });

  // Додатково: блокуємо прокрутку під час модалки
  const toggleScroll = (disable) => {
    document.body.style.overflow = disable ? "hidden" : "auto";
  };

  const openModalWithScroll = (modal) => {
    openModal(modal);
    toggleScroll(true);
  };

  const closeAllWithScroll = () => {
    closeAll();
    toggleScroll(false);
  };

  // Переприв'язка з блокуванням скролу
  loginDesktop?.addEventListener("click", () => openModalWithScroll(loginModal));
  loginMobile?.addEventListener("click", () => openModalWithScroll(loginModal));
  closeLogin?.addEventListener("click", closeAllWithScroll);
  closeSignup?.addEventListener("click", closeAllWithScroll);
  openSignup?.addEventListener("click", (e) => {
    e.preventDefault();
    openModalWithScroll(signupModal);
  });
  openLogin?.addEventListener("click", (e) => {
    e.preventDefault();
    openModalWithScroll(loginModal);
  });
});
overlay.style.zIndex = 9999; // фон під модалкою
loginModal.style.zIndex = 10000;
signupModal.style.zIndex = 10000;

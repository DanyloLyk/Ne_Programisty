document.addEventListener("DOMContentLoaded", function() {
  const loginModal = document.getElementById("login-modal");
  const signupModal = document.getElementById("signup-modal");
  const closeLogin = document.getElementById("close-login");
  const closeSignup = document.getElementById("close-signup");
  const openSignup = document.getElementById("open-signup");
  const openLogin = document.getElementById("open-login");
  const loginDesktop = document.getElementById("login-desktop");
  const loginMobile = document.getElementById("login-mobile");

  // Відкрити Login
  const openLoginModal = () => {
    signupModal?.classList.remove("show");
    loginModal?.classList.add("show");
  };

  // Відкрити Signup
  const openSignupModal = () => {
    loginModal?.classList.remove("show");
    signupModal?.classList.add("show");
  };

  // Закриття всього
  const closeAll = () => {
    loginModal?.classList.remove("show");
    signupModal?.classList.remove("show");
  };

  // Події
  loginDesktop?.addEventListener("click", openLoginModal);
  loginMobile?.addEventListener("click", openLoginModal);
  closeLogin?.addEventListener("click", closeAll);
  closeSignup?.addEventListener("click", closeAll);
  openSignup?.addEventListener("click", openSignupModal);
  openLogin?.addEventListener("click", openLoginModal);

  // Клік поза модалкою
  window.addEventListener("click", (e) => {
    if (e.target === loginModal || e.target === signupModal) closeAll();
  });
});

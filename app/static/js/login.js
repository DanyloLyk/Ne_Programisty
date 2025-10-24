document.addEventListener("DOMContentLoaded", function() {
  const loginDesktop = document.getElementById("login-desktop");
  const loginMobile = document.getElementById("login-mobile");
  const loginModal = document.getElementById("login-modal");
  const closeModal = document.getElementById("close-login");

  if (!loginModal) return;

  const openModal = () => loginModal.classList.add("show");
  const closeModalFunc = () => loginModal.classList.remove("show");

  if (loginDesktop) loginDesktop.addEventListener("click", openModal);
  if (loginMobile) loginMobile.addEventListener("click", openModal);

  if (closeModal) closeModal.addEventListener("click", closeModalFunc);

  window.addEventListener("click", (e) => {
    if (e.target === loginModal) closeModalFunc();
  });
});

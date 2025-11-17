document.addEventListener("DOMContentLoaded", function() {
  const loginModal = document.getElementById("login-modal");
  const signupModal = document.getElementById("signup-modal");
  const closeLogin = document.getElementById("close-login");
  const closeSignup = document.getElementById("close-signup");
  const openSignup = document.getElementById("open-signup");
  const openLogin = document.getElementById("open-login");
  const loginDesktop = document.getElementById("login-desktop");
  const loginMobile = document.getElementById("login-mobile");
  const cartLinks = document.querySelectorAll('[data-cart-link="true"]');
  const isAuthenticated = document.body.dataset.userAuth === "true";

  if (!loginModal && !signupModal) {
    return;
  }

  const overlay = document.createElement("div");
  overlay.style.cssText = `
    display:none;
    position:fixed;
    top:0;
    left:0;
    width:100%;
    height:100%;
    background:rgba(0,0,0,0.5);
    z-index:9999;
  `;
  document.body.appendChild(overlay);

  const toggleScroll = (disable) => {
    document.body.style.overflow = disable ? "hidden" : "auto";
  };

  const closeAll = () => {
    loginModal?.classList.remove("show");
    signupModal?.classList.remove("show");
    overlay.style.display = "none";
    toggleScroll(false);
  };

  const openModal = (modal) => {
    loginModal?.classList.remove("show");
    signupModal?.classList.remove("show");
    modal?.classList.add("show");
    overlay.style.display = "block";
    toggleScroll(true);
  };

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

  overlay.addEventListener("click", closeAll);
  window.addEventListener("click", (e) => {
    if (e.target === loginModal || e.target === signupModal) closeAll();
  });

  if (!isAuthenticated && cartLinks.length > 0) {
    cartLinks.forEach((link) => {
      link.addEventListener("click", (event) => {
        event.preventDefault();
        alert("Щоб переглянути кошик, будь ласка, увійдіть або зареєструйтесь.");
        if (loginModal) {
          openModal(loginModal);
        }
      });
    });
  }
});

document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("presenter-mode-toggle");
  const slides = Array.from(document.querySelectorAll(".lesson-slide"));
  if (!toggle || slides.length === 0) return;

  let currentSlide = 0;
  let presenterMode = false;

  function fitSlide(slide) {
    slide.style.removeProperty("--presenter-slide-base");
    if (!presenterMode) return;

    let scale = 1;
    while (slide.scrollHeight > slide.clientHeight && scale > 0.72) {
      scale -= 0.04;
      slide.style.setProperty("--presenter-slide-base", `${scale.toFixed(2)}rem`);
    }
  }

  function showSlide(index) {
    currentSlide = Math.max(0, Math.min(index, slides.length - 1));
    slides.forEach((slide, i) => {
      slide.classList.toggle("is-active-slide", i === currentSlide);
    });
    window.requestAnimationFrame(() => fitSlide(slides[currentSlide]));
  }

  function enterPresenterMode() {
    presenterMode = true;
    document.body.classList.add("lesson-presenter-mode");
    toggle.textContent = "Exit presenter mode";
    showSlide(currentSlide);
    slides[currentSlide].scrollIntoView({ behavior: "instant", block: "center" });
  }

  function exitPresenterMode() {
    presenterMode = false;
    document.body.classList.remove("lesson-presenter-mode");
    toggle.textContent = "Enter presenter mode";
    slides.forEach((slide) => slide.classList.remove("is-active-slide"));
  }

  toggle.addEventListener("click", () => {
    if (presenterMode) {
      exitPresenterMode();
    } else {
      enterPresenterMode();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (!presenterMode) return;

    if (event.key === "Escape") {
      exitPresenterMode();
      return;
    }

    if (event.key === "ArrowRight" || event.key === "PageDown" || event.key === " ") {
      event.preventDefault();
      showSlide(currentSlide + 1);
      return;
    }

    if (event.key === "ArrowLeft" || event.key === "PageUp") {
      event.preventDefault();
      showSlide(currentSlide - 1);
    }
  });

  window.addEventListener("resize", () => {
    if (presenterMode) fitSlide(slides[currentSlide]);
  });
});

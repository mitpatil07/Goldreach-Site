/* Vision section:
   1. Draws the gold scribble around "The VISION" as it scrolls into view.
   2. Rotates the scribble as the page scrolls — the circle spins with you. */
(function () {
  var title = document.querySelector('.vision_title[data-vision-title]');
  if (!title) return;
  var scribble = title.querySelector('.vision_scribble');
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* 1. reveal on enter */
  if (reduced || !('IntersectionObserver' in window)) {
    title.classList.add('is-in');
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { title.classList.add('is-in'); io.unobserve(title); }
      });
    }, { threshold: 0.35 });
    io.observe(title);
  }

  /* 2. rotate as you scroll — no rotation while off-screen, one full turn
        over the section's total travel through the viewport. */
  if (reduced || !scribble) return;

  var ticking = false;
  function paint() {
    ticking = false;
    var r = title.getBoundingClientRect();
    var vh = window.innerHeight;
    /* progress: 0 when the title's top hits the bottom of the viewport,
       1 when its bottom leaves the top */
    var span = vh + r.height;
    var p = (vh - r.top) / span;
    if (p < 0) p = 0; else if (p > 1) p = 1;
    /* -12deg (settled/start pose) → +348deg (one full rotation past that) */
    var deg = -12 + p * 360;
    scribble.style.setProperty('--vision-rot', deg.toFixed(2) + 'deg');
  }
  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(paint);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll);
  paint();
})();

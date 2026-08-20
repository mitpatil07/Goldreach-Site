/* Scroll-driven reveal for the "Everything Your Podcast Needs to Win" section.
   The section is 300vh with a sticky 100vh stage (like the orbit it
   replaced), so the page moves slowly through it while the 12 points light
   up one at a time in listed order. Card titles/descriptions fade in as
   soon as the stage is on screen; the background dial spins continuously
   via CSS, independent of scroll. */
(function () {
  var sec = document.querySelector('.cat_scroll');
  if (!sec) return;

  var cards = [].slice.call(document.querySelectorAll('.cat_card'));
  var points = [].slice.call(document.querySelectorAll('.cat_list li'));
  points.sort(function (a, b) { return (+a.dataset.i) - (+b.dataset.i); });

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* card titles/descriptions: simple reveal on entry, staggered by card */
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.classList.add('is-in');
        io.unobserve(en.target);
      });
    }, { threshold: 0.2 });
    cards.forEach(function (c) { io.observe(c); });
  } else {
    cards.forEach(function (c) { c.classList.add('is-in'); });
  }

  if (reduce || !('IntersectionObserver' in window) || window.innerWidth < 1024) {
    points.forEach(function (el) { el.classList.add('is-in'); });
    return;
  }

  var ticking = false;
  function paint() {
    ticking = false;
    var total = sec.offsetHeight - window.innerHeight;
    if (total <= 0) return;
    var p = Math.max(0, Math.min(1, (-sec.getBoundingClientRect().top) / total));
    /* lead-in before the first point, hold after the last */
    var q = Math.max(0, Math.min(1, (p - 0.12) / 0.74));
    var shown = Math.round(q * points.length);
    points.forEach(function (el, i) { el.classList.toggle('is-in', i < shown); });
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

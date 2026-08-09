/* Scroll-driven reveal for the "Everything Your Podcast Needs to Win" section.
   The section is 300vh with a sticky 100vh stage, so the page moves slowly
   through it while the plates appear one at a time in listed order. */
(function () {
  var sec = document.querySelector('.orbit_scroll');
  if (!sec) return;

  var plates = [].slice.call(document.querySelectorAll('.orbit_plate'));
  var mob    = [].slice.call(document.querySelectorAll('.orbit_mplate'));
  plates.sort(function (a, b) { return (+a.dataset.i) - (+b.dataset.i); });

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* stacked list on small screens: simple staggered reveal on entry */
  function revealOnEntry(list) {
    if (!('IntersectionObserver' in window)) {
      list.forEach(function (e) { e.classList.add('is-in'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var el = en.target;
        setTimeout(function () { el.classList.add('is-in'); }, (+el.dataset.i) * 90);
        io.unobserve(el);
      });
    }, { threshold: 0.2 });
    list.forEach(function (e) { io.observe(e); });
  }
  revealOnEntry(mob);

  if (reduce || window.innerWidth < 1024) {
    plates.forEach(function (e) { e.classList.add('is-in'); });
    return;
  }

  var ticking = false;
  function paint() {
    ticking = false;
    var total = sec.offsetHeight - window.innerHeight;
    if (total <= 0) return;
    var p = Math.max(0, Math.min(1, (-sec.getBoundingClientRect().top) / total));
    /* lead-in before the first plate, hold after the last */
    var q = Math.max(0, Math.min(1, (p - 0.12) / 0.74));
    var shown = Math.round(q * plates.length);
    plates.forEach(function (el, i) { el.classList.toggle('is-in', i < shown); });
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

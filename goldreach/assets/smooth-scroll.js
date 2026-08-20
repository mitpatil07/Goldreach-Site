/* Eased scroll for wheel/trackpad input, plus smooth anchor-link jumps.
   Self-contained (no CDN library), so the offline gate still passes.

   Design:
   - Only wheel input is intercepted and eased. Keyboard scrolling and
     scrollbar dragging are left completely native — smoothing only those
     two paths would need hijacking every input method (effectively a full
     virtual-scroll rewrite), which isn't worth the risk to sticky-positioned
     sections elsewhere on the page. Leaving them native means there's
     nothing to break there.
   - Every wheel event resyncs the animation's target to the page's actual
     current scrollY first. Without that, if the user scrolls with the
     keyboard or the scrollbar between wheel gestures, the next wheel tick
     would resume from a stale target and the page would jump.
   - prefers-reduced-motion disables this entirely; scrolling stays native. */
(function () {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  var current = window.scrollY;
  var target = current;
  var raf = null;

  // Lower = slower/heavier. 0.07 lands close to a ~1s ease per wheel gesture.
  var EASE = 0.07;
  // <1 slows the effective scroll distance per wheel notch.
  var WHEEL_MULT = 0.6;

  function maxScroll() {
    return document.documentElement.scrollHeight - window.innerHeight;
  }

  function loop() {
    var diff = target - current;
    if (Math.abs(diff) < 0.5) {
      current = target;
      window.scrollTo(0, current);
      raf = null;
      return;
    }
    current += diff * EASE;
    window.scrollTo(0, current);
    raf = requestAnimationFrame(loop);
  }

  function start() {
    if (!raf) raf = requestAnimationFrame(loop);
  }

  window.addEventListener('wheel', function (e) {
    // vertical wheel only; let horizontal gestures pass through untouched
    if (Math.abs(e.deltaX) > Math.abs(e.deltaY)) return;
    e.preventDefault();

    if (!raf) { current = window.scrollY; target = current; }

    target += e.deltaY * WHEEL_MULT;
    target = Math.max(0, Math.min(maxScroll(), target));
    start();
  }, { passive: false });

  // smooth anchor-link navigation (nav + footer links), same easing engine.
  // The nav is a fixed floating pill (see theme-light.css §22), so jump
  // targets are offset by its live rendered height + a gap — matching the
  // section's `scroll-margin-top`, which covers non-JS anchor jumps.
  var navEl = document.querySelector('.navbar1_component');
  function navOffset() {
    return navEl ? navEl.getBoundingClientRect().height + 34 : 0;
  }

  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href^="#"]');
    if (!a) return;
    var id = a.getAttribute('href');
    if (id.length < 2) return;
    var el = document.querySelector(id);
    if (!el) return;
    e.preventDefault();
    current = window.scrollY;
    target = Math.max(0, Math.min(maxScroll(),
      el.getBoundingClientRect().top + window.scrollY - navOffset()));
    start();
  });

  window.addEventListener('resize', function () {
    target = Math.min(target, maxScroll());
  });
})();

/* The clip marquee has 32 looping videos (16 clips x 2, doubled for the
   seamless scroll). Autoplaying all 32 at once was the main cause of the
   lag reported on Windows and mobile — 32 concurrent video decodes is
   heavy even on capable hardware. This lazy-loads each clip's src only
   once it's near the viewport, and pauses (without dropping the loaded
   src) once it scrolls back out, so only the handful of cards actually
   visible at any moment are ever decoding. */
(function () {
  var videos = [].slice.call(document.querySelectorAll('.clip-video'));
  if (!videos.length) return;

  function load(v) {
    if (!v.src && v.dataset.src) v.src = v.dataset.src;
  }

  if (!('IntersectionObserver' in window)) {
    videos.forEach(function (v) { load(v); v.play().catch(function () {}); });
    return;
  }

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      var v = en.target;
      if (en.isIntersecting) {
        load(v);
        v.play().catch(function () {});
      } else {
        v.pause();
      }
    });
  }, { rootMargin: '400px 200px' });

  videos.forEach(function (v) { io.observe(v); });
})();

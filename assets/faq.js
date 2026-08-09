/* Custom FAQ accordion.
   The original 3 questions opened via Webflow's compiled IX2 interactions,
   which are baked into webflow.schunk.*.js as a JSON config keyed to those
   exact 3 data-w-id values. New questions added outside the Webflow
   designer have no matching entry in that config, so clicking them does
   nothing. This drives all items with plain JS instead, independent of IX2. */
(function () {
  var items = [].slice.call(document.querySelectorAll('.faq6_accordion'));
  items.forEach(function (item) {
    var q = item.querySelector('.faq6_question');
    var a = item.querySelector('.faq6_answer');
    if (!q || !a) return;
    a.style.transition = 'height .3s ease';
    q.addEventListener('click', function () {
      var open = item.classList.contains('is-open');
      if (open) {
        a.style.height = a.scrollHeight + 'px';
        requestAnimationFrame(function () { a.style.height = '0px'; });
        item.classList.remove('is-open');
      } else {
        a.style.height = a.scrollHeight + 'px';
        item.classList.add('is-open');
        a.addEventListener('transitionend', function clear() {
          if (item.classList.contains('is-open')) a.style.height = 'auto';
          a.removeEventListener('transitionend', clear);
        });
      }
    });
  });
})();

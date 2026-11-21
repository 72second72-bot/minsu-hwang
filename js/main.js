(function () {
  var root = document.documentElement;

  // 밝게 / 어둡게
  var btn = document.querySelector('.theme-btn');
  btn.addEventListener('click', function () {
    var cur = root.dataset.theme || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    var next = cur === 'dark' ? 'light' : 'dark';
    root.dataset.theme = next;
    try { localStorage.setItem('theme', next); } catch (e) {}
  });

  // 스크롤하면 나타나기
  var items = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    items.forEach(function (el) { io.observe(el); });
  } else {
    items.forEach(function (el) { el.classList.add('in'); });
  }

  // 지금 보는 단락을 위 막대에 표시
  var links = Array.prototype.slice.call(document.querySelectorAll('.nav a'));
  var map = { about: 'about', projects: 'projects', works: 'works', research: 'research', skills: 'research', contact: 'contact' };
  if ('IntersectionObserver' in window) {
    var so = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        var id = map[e.target.id];
        links.forEach(function (a) { a.classList.toggle('on', a.getAttribute('href') === '#' + id); });
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    Object.keys(map).forEach(function (id) { var s = document.getElementById(id); if (s) so.observe(s); });
  }

  // 그림 크게 보기
  var dlg = document.querySelector('.lightbox');
  var big = dlg.querySelector('img');
  document.querySelectorAll('.zoom').forEach(function (b) {
    b.addEventListener('click', function () {
      big.src = b.dataset.full;
      var im = b.querySelector('img');
      big.alt = im ? im.alt : b.textContent.trim();
      if (dlg.showModal) dlg.showModal(); else window.open(b.dataset.full, '_blank');
    });
  });
  dlg.addEventListener('click', function (e) { if (e.target === dlg || e.target.classList.contains('lb-close')) dlg.close(); });
})();

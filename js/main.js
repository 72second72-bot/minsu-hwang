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

  // ───────── 자세히 보기 창 ─────────
  var W = window.WORKS || {};
  var KIND = { panel: '판넬', slides: '장' };

  // 카드에 장수 표시
  document.querySelectorAll('[data-badge]').forEach(function (el) {
    var w = W[el.dataset.badge]; if (!w) { el.remove(); return; }
    el.textContent = w.sets.map(function (s) { return s.name + ' ' + s.items.length; }).join(' · ');
  });

  var dlg = document.querySelector('.viewer');
  if (!dlg) return;
  var q = function (s) { return dlg.querySelector(s); };
  var elTitle = q('.vw-title'), elTabs = q('.vw-tabs'), elCount = q('.vw-count'), elZoom = q('.vw-zoom');
  var stage = q('.vw-stage'), img = q('.vw-img'), strip = q('.vw-strip'), cap = q('.vw-cap');
  var cur = { work: null, set: 0, i: 0, zoom: false };

  function setItems() { return W[cur.work].sets[cur.set].items; }

  function buildTabs() {
    var sets = W[cur.work].sets;
    elTabs.innerHTML = '';
    if (sets.length < 2) { elTabs.hidden = true; return; }
    elTabs.hidden = false;
    sets.forEach(function (s, k) {
      var b = document.createElement('button');
      b.type = 'button'; b.setAttribute('role', 'tab');
      b.textContent = s.name + ' ' + s.items.length;
      b.setAttribute('aria-selected', k === cur.set ? 'true' : 'false');
      b.addEventListener('click', function () { cur.set = k; cur.i = 0; buildTabs(); buildStrip(); show(); });
      elTabs.appendChild(b);
    });
  }

  function buildStrip() {
    strip.innerHTML = '';
    var its = setItems();
    strip.classList.toggle('portrait', its[0] && its[0].h > its[0].w);
    its.forEach(function (it, k) {
      var b = document.createElement('button');
      b.type = 'button'; b.setAttribute('aria-label', (k + 1) + '번째 보기');
      var t = document.createElement('img'); t.src = it.t; t.alt = ''; t.loading = 'lazy';
      t.width = 240; t.height = Math.round(240 * it.h / it.w); // 불러오기 전에도 자리를 잡아 둔다
      b.appendChild(t);
      b.addEventListener('click', function () { cur.i = k; show(); });
      strip.appendChild(b);
    });
  }

  function setZoom(on, cx, cy) {
    if (on && img.classList.contains('loading')) return;
    // 맞춤 크기와 누른 자리는 확대 모드로 바꾸기 전에 잰다.
    // (예전엔 바꾼 뒤에 재서 원본 크기의 2배, 판넬은 화면 맞춤의 10배 가까이 커졌다 — 11-21 민수님 '너무 심하다')
    var fitW = img.clientWidth, fitH = img.clientHeight, rect = img.getBoundingClientRect();
    cur.zoom = on;
    dlg.classList.toggle('zoomed', on);
    elZoom.setAttribute('aria-pressed', on ? 'true' : 'false');
    elZoom.querySelector('span').textContent = on ? '맞춤' : '확대';
    if (!on) { img.style.width = ''; img.style.height = ''; stage.scrollTo(0, 0); return; }
    var it = setItems()[cur.i];
    var rx = cx == null ? 0.5 : (cx - rect.left) / rect.width;
    var ry = cy == null ? 0.5 : (cy - rect.top) / rect.height;
    // 화면 맞춤의 1.5~2.5배. 원본 해상도를 넘기지 않되, 너무 덜 커지지 않게 1.5배는 보장한다.
    var scale = Math.max(1.5, Math.min(2.5, it.w / fitW));
    var w = Math.round(fitW * scale), h = Math.round(fitH * scale);
    img.style.width = w + 'px'; img.style.height = h + 'px';
    requestAnimationFrame(function () {
      stage.scrollLeft = rx * w - stage.clientWidth / 2;
      stage.scrollTop = ry * h - stage.clientHeight / 2;
    });
  }

  function show() {
    var its = setItems(), it = its[cur.i];
    if (cur.zoom) setZoom(false);
    if (img.getAttribute('src') !== it.src) { img.classList.add('loading'); img.src = it.src; }
    img.alt = W[cur.work].title + ' ' + (cur.i + 1) + '쪽';
    elCount.textContent = (cur.i + 1) + ' / ' + its.length;
    cap.textContent = it.cap || '';
    cap.hidden = !it.cap;
    q('.vw-prev').disabled = cur.i === 0;
    q('.vw-next').disabled = cur.i === its.length - 1;
    Array.prototype.forEach.call(strip.children, function (b, k) {
      b.classList.toggle('on', k === cur.i);
      if (k === cur.i) b.scrollIntoView({ block: 'nearest', inline: 'center' });
    });
    [cur.i + 1, cur.i - 1].forEach(function (k) { if (its[k]) { var p = new Image(); p.src = its[k].src; } });
  }

  function go(d) {
    var n = cur.i + d, its = setItems();
    if (n < 0 || n >= its.length) return;
    cur.i = n; show();
  }

  function open(key) {
    if (!W[key]) return;
    cur = { work: key, set: 0, i: 0, zoom: false };
    elTitle.textContent = W[key].title;
    buildTabs(); buildStrip();
    if (dlg.showModal) dlg.showModal(); else dlg.setAttribute('open', '');
    document.body.classList.add('noscroll');
    show();
  }

  function close() { setZoom(false); dlg.close(); }
  // 닫힘 알림은 한 박자 늦게 오므로, 그새 다시 열렸으면 그림을 지우지 않는다
  dlg.addEventListener('close', function () { if (dlg.open) return; document.body.classList.remove('noscroll'); img.removeAttribute('src'); });
  img.addEventListener('load', function () { img.classList.remove('loading'); });
  img.addEventListener('error', function () { img.classList.remove('loading'); });

  document.querySelectorAll('[data-open]').forEach(function (b) {
    b.addEventListener('click', function () { open(b.dataset.open); });
  });
  q('.vw-prev').addEventListener('click', function () { go(-1); });
  q('.vw-next').addEventListener('click', function () { go(1); });
  q('.vw-close').addEventListener('click', close);
  elZoom.addEventListener('click', function () { setZoom(!cur.zoom); });

  // 탭을 누르면 단추가 새로 그려져 초점이 창 밖으로 나가므로, 문서 전체에서 키를 받는다.
  document.addEventListener('keydown', function (e) {
    if (!dlg.open) return;
    if (e.key === 'ArrowRight') { e.preventDefault(); go(1); }
    else if (e.key === 'ArrowLeft') { e.preventDefault(); go(-1); }
    else if (e.key === '+' || e.key === '=' || e.key === 'z') { setZoom(!cur.zoom); }
  });

  // 그림을 누르면 그 자리로 확대 / 다시 누르면 맞춤. 확대 중에는 끌어서 움직인다.
  var drag = null, moved = false;
  img.addEventListener('pointerdown', function (e) {
    if (e.pointerType !== 'mouse') return;
    moved = false;
    if (cur.zoom) { drag = { x: e.clientX, y: e.clientY, l: stage.scrollLeft, t: stage.scrollTop }; img.setPointerCapture(e.pointerId); e.preventDefault(); }
  });
  img.addEventListener('pointermove', function (e) {
    if (!drag) return;
    var dx = e.clientX - drag.x, dy = e.clientY - drag.y;
    if (Math.abs(dx) + Math.abs(dy) > 4) moved = true;
    stage.scrollLeft = drag.l - dx; stage.scrollTop = drag.t - dy;
  });
  img.addEventListener('pointerup', function () { drag = null; });
  img.addEventListener('click', function (e) {
    if (moved) { moved = false; return; }
    setZoom(!cur.zoom, e.clientX, e.clientY);
  });

  // 손가락으로 옆으로 밀면 넘기기 (맞춤 상태에서만)
  var tx = null, ty = null;
  stage.addEventListener('touchstart', function (e) { if (cur.zoom || e.touches.length > 1) { tx = null; return; } tx = e.touches[0].clientX; ty = e.touches[0].clientY; }, { passive: true });
  stage.addEventListener('touchend', function (e) {
    if (tx == null) return;
    var dx = e.changedTouches[0].clientX - tx, dy = e.changedTouches[0].clientY - ty;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.5) go(dx < 0 ? 1 : -1);
    tx = null;
  });
})();

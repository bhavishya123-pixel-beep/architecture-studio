/* ===== RAIN EFFECT ===== */
(function () {
  const canvas = document.getElementById('rain');
  const ctx = canvas.getContext('2d');
  let W, H, drops = [];

  function resize() {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }

  function Drop() { this.reset(); }
  Drop.prototype.reset = function () {
    this.x = Math.random() * W;
    this.y = Math.random() * H - H;
    this.len = Math.random() * 18 + 8;
    this.speed = Math.random() * 6 + 4;
    this.alpha = Math.random() * 0.4 + 0.05;
    this.color = Math.random() > 0.6 ? '#ff0080' : '#00f5ff';
  };
  Drop.prototype.update = function () { this.y += this.speed; if (this.y > H) this.reset(); };
  Drop.prototype.draw = function () {
    ctx.beginPath();
    ctx.moveTo(this.x, this.y);
    ctx.lineTo(this.x, this.y + this.len);
    ctx.strokeStyle = this.color.replace(')', `,${this.alpha})`).replace('rgb', 'rgba').replace('#ff0080', `rgba(255,0,128,${this.alpha})`).replace('#00f5ff', `rgba(0,245,255,${this.alpha})`);
    ctx.lineWidth = 1;
    ctx.stroke();
  };

  function init() {
    resize();
    drops = Array.from({ length: 180 }, () => new Drop());
  }

  function animate() {
    ctx.clearRect(0, 0, W, H);
    drops.forEach(d => { d.update(); d.draw(); });
    requestAnimationFrame(animate);
  }

  window.addEventListener('resize', resize);
  init();
  animate();
})();

/* ===== CUSTOM CURSOR ===== */
(function () {
  const dot = document.createElement('div');
  const ring = document.createElement('div');
  dot.className = 'cdot'; ring.className = 'cring';
  document.body.append(dot, ring);
  let mx = 0, my = 0, rx = 0, ry = 0;
  document.addEventListener('mousemove', e => {
    mx = e.clientX; my = e.clientY;
    dot.style.left = mx + 'px'; dot.style.top = my + 'px';
  });
  (function loop() {
    rx += (mx - rx) * 0.12; ry += (my - ry) * 0.12;
    ring.style.left = rx + 'px'; ring.style.top = ry + 'px';
    requestAnimationFrame(loop);
  })();
  document.querySelectorAll('a,button,.pcard,.ccard').forEach(el => {
    el.addEventListener('mouseenter', () => { ring.style.width = '52px'; ring.style.height = '52px'; dot.style.transform = 'translate(-50%,-50%) scale(0)'; });
    el.addEventListener('mouseleave', () => { ring.style.width = '30px'; ring.style.height = '30px'; dot.style.transform = 'translate(-50%,-50%) scale(1)'; });
  });
})();

/* ===== STATUS TEXT ===== */
(function () {
  const msgs = ['SYS_ONLINE', 'CATALOG_LOADED', 'NIGHT_CITY_UPLINK', 'SECURE_CHANNEL', 'NEXFORM_v7.7', 'READY'];
  let i = 0;
  const el = document.getElementById('sysMsg');
  el.style.transition = 'opacity 0.3s';
  setInterval(() => {
    i = (i + 1) % msgs.length;
    el.style.opacity = '0';
    setTimeout(() => { el.textContent = msgs[i]; el.style.opacity = '1'; }, 300);
  }, 2500);
})();

/* ===== COUNTER ANIMATION ===== */
function animateCount(el) {
  const target = +el.dataset.t;
  const dur = 1600;
  const t0 = performance.now();
  (function step(now) {
    const p = Math.min((now - t0) / dur, 1);
    const e = 1 - Math.pow(1 - p, 3);
    el.textContent = Math.floor(e * target).toString().padStart(el.dataset.t.length, '0');
    if (p < 1) requestAnimationFrame(step);
  })(t0);
}

/* ===== SCROLL REVEAL ===== */
(function () {
  const io = new IntersectionObserver(entries => {
    entries.forEach(en => {
      if (en.isIntersecting) {
        en.target.classList.add('visible');
        if (en.target.classList.contains('hnum')) animateCount(en.target);
        io.unobserve(en.target);
      }
    });
  }, { threshold: 0.08 });

  document.querySelectorAll('.pcard,.ccard,.pstep,.tcard,.hnum,.sec-head,.contact-wrap').forEach(el => {
    el.classList.add('reveal');
    io.observe(el);
  });
})();

/* ===== FILTER ===== */
(function () {
  const btns = document.querySelectorAll('.filt');
  const cards = document.querySelectorAll('.pcard');
  btns.forEach(btn => {
    btn.addEventListener('click', () => {
      btns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const f = btn.dataset.f;
      cards.forEach(card => {
        if (f === 'all' || card.dataset.c === f) {
          card.classList.remove('hidden');
        } else {
          card.classList.add('hidden');
        }
      });
    });
  });
})();

/* ===== ADD FEEDBACK ===== */
document.querySelectorAll('.btn-add').forEach(btn => {
  btn.addEventListener('click', function () {
    const orig = this.textContent;
    this.textContent = '✓ ADDED';
    this.style.background = 'var(--pink)';
    this.style.color = '#fff';
    setTimeout(() => {
      this.textContent = orig;
      this.style.background = '';
      this.style.color = '';
    }, 1400);
  });
});

/* ===== FORM SUBMIT ===== */
document.getElementById('contactForm').addEventListener('submit', function (e) {
  e.preventDefault();
  const btn = this.querySelector('button[type=submit]');
  btn.textContent = '✓ TRANSMISSION RECEIVED';
  btn.style.background = 'var(--green)';
  btn.style.borderColor = 'var(--green)';
  btn.style.color = '#000';
  setTimeout(() => {
    btn.textContent = '▶ TRANSMIT REQUEST';
    btn.style.background = '';
    btn.style.borderColor = '';
    btn.style.color = '';
  }, 3000);
});

/* ===== NAV SCROLL ===== */
(function () {
  const nav = document.querySelector('.nav');
  window.addEventListener('scroll', () => {
    nav.style.borderBottomColor = window.scrollY > 60
      ? 'rgba(255,0,128,0.45)'
      : 'rgba(255,0,128,0.25)';
  });
})();

/* ===== HOLOGRAPHIC TILT ===== */
document.querySelectorAll('.pcard,.ccard').forEach(card => {
  card.addEventListener('mousemove', e => {
    const r = card.getBoundingClientRect();
    const x = (e.clientX - r.left) / r.width - 0.5;
    const y = (e.clientY - r.top) / r.height - 0.5;
    card.style.transform = `translateY(-5px) rotateX(${-y * 5}deg) rotateY(${x * 5}deg)`;
    card.style.boxShadow = `${-x * 12}px ${-y * 12}px 28px rgba(255,0,128,0.15)`;
  });
  card.addEventListener('mouseleave', () => {
    card.style.transform = '';
    card.style.boxShadow = '';
    card.style.transition = 'transform 0.4s, box-shadow 0.4s, border-color 0.3s';
  });
  card.addEventListener('mouseenter', () => {
    card.style.transition = 'border-color 0.2s';
  });
});

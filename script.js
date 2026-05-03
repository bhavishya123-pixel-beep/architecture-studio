/* ===== PARTICLE CANVAS ===== */
(function () {
  const canvas = document.getElementById('particles');
  const ctx = canvas.getContext('2d');
  let w, h, particles;

  function resize() {
    w = canvas.width = window.innerWidth;
    h = canvas.height = window.innerHeight;
  }

  function Particle() {
    this.reset();
  }
  Particle.prototype.reset = function () {
    this.x = Math.random() * w;
    this.y = Math.random() * h;
    this.vx = (Math.random() - 0.5) * 0.3;
    this.vy = (Math.random() - 0.5) * 0.3;
    this.alpha = Math.random() * 0.6 + 0.1;
    this.size = Math.random() * 1.5 + 0.5;
    this.color = Math.random() > 0.5 ? '0,245,255' : '191,0,255';
  };
  Particle.prototype.update = function () {
    this.x += this.vx;
    this.y += this.vy;
    if (this.x < 0 || this.x > w || this.y < 0 || this.y > h) this.reset();
  };
  Particle.prototype.draw = function () {
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(${this.color},${this.alpha})`;
    ctx.fill();
  };

  function init() {
    resize();
    particles = Array.from({ length: 120 }, () => new Particle());
  }

  function drawConnections() {
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 120) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(0,245,255,${0.06 * (1 - dist / 120)})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }
  }

  function animate() {
    ctx.clearRect(0, 0, w, h);
    drawConnections();
    particles.forEach(p => { p.update(); p.draw(); });
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
  dot.className = 'cursor-dot';
  ring.className = 'cursor-ring';
  document.body.append(dot, ring);

  let mx = 0, my = 0, rx = 0, ry = 0;
  document.addEventListener('mousemove', e => {
    mx = e.clientX; my = e.clientY;
    dot.style.left = mx + 'px';
    dot.style.top  = my + 'px';
  });

  function animateRing() {
    rx += (mx - rx) * 0.12;
    ry += (my - ry) * 0.12;
    ring.style.left = rx + 'px';
    ring.style.top  = ry + 'px';
    requestAnimationFrame(animateRing);
  }
  animateRing();

  document.querySelectorAll('a, button, .product-card, .collection-card').forEach(el => {
    el.addEventListener('mouseenter', () => {
      ring.style.width = '56px';
      ring.style.height = '56px';
      dot.style.transform = 'translate(-50%,-50%) scale(0)';
    });
    el.addEventListener('mouseleave', () => {
      ring.style.width = '32px';
      ring.style.height = '32px';
      dot.style.transform = 'translate(-50%,-50%) scale(1)';
    });
  });
})();

/* ===== STATUS TEXT CYCLING ===== */
(function () {
  const msgs = [
    'SYSTEM ONLINE', 'LOADING CATALOG...', 'ALL SYSTEMS GO',
    'SECURE CONNECTION', 'NEXFORM v4.2', 'READY FOR INPUT'
  ];
  let i = 0;
  const el = document.getElementById('statusText');
  setInterval(() => {
    i = (i + 1) % msgs.length;
    el.style.opacity = '0';
    setTimeout(() => { el.textContent = msgs[i]; el.style.opacity = '1'; }, 300);
  }, 3000);
  el.style.transition = 'opacity 0.3s';
})();

/* ===== COUNTER ANIMATION ===== */
function animateCounter(el) {
  const target = parseInt(el.dataset.target);
  const duration = 1800;
  const start = performance.now();
  function step(now) {
    const progress = Math.min((now - start) / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.floor(ease * target).toString().padStart(el.dataset.target.length, '0');
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

/* ===== SCROLL REVEAL ===== */
(function () {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('visible');
        if (e.target.classList.contains('stat-num')) animateCounter(e.target);
        observer.unobserve(e.target);
      }
    });
  }, { threshold: 0.15 });

  document.querySelectorAll(
    '.product-card, .collection-card, .step, .testimonial-card, .stat-num, .section-header, .contact-inner'
  ).forEach(el => {
    el.classList.add('reveal');
    observer.observe(el);
  });
})();

/* ===== PRODUCT FILTER ===== */
(function () {
  const btns = document.querySelectorAll('.filter-btn');
  const cards = document.querySelectorAll('.product-card');
  btns.forEach(btn => {
    btn.addEventListener('click', () => {
      btns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const filter = btn.dataset.filter;
      cards.forEach(card => {
        const show = filter === 'all' || card.dataset.cat === filter;
        card.style.opacity = show ? '1' : '0';
        card.style.transform = show ? '' : 'scale(0.9)';
        card.style.pointerEvents = show ? '' : 'none';
        card.style.transition = 'opacity 0.35s, transform 0.35s';
      });
    });
  });
})();

/* ===== GLITCH RANDOM TRIGGER ===== */
(function () {
  const glitches = document.querySelectorAll('.glitch');
  setInterval(() => {
    const el = glitches[Math.floor(Math.random() * glitches.length)];
    el.style.animation = 'none';
    requestAnimationFrame(() => {
      el.style.animation = '';
    });
  }, 4000);
})();

/* ===== ADD TO CART FEEDBACK ===== */
document.querySelectorAll('.btn-add').forEach(btn => {
  btn.addEventListener('click', function () {
    const orig = this.textContent;
    this.textContent = 'ADDED ✓';
    this.style.background = 'var(--cyan)';
    this.style.color = 'var(--bg)';
    setTimeout(() => {
      this.textContent = orig;
      this.style.background = '';
      this.style.color = '';
    }, 1500);
  });
});

/* ===== FORM SUBMIT ===== */
document.getElementById('contactForm').addEventListener('submit', function (e) {
  e.preventDefault();
  const btn = this.querySelector('button[type=submit]');
  btn.textContent = '✓ TRANSMISSION RECEIVED';
  btn.style.borderColor = 'var(--green)';
  btn.style.color = 'var(--green)';
  setTimeout(() => {
    btn.innerHTML = '<span class="btn-icon">&#9654;</span> TRANSMIT REQUEST';
    btn.style.borderColor = '';
    btn.style.color = '';
  }, 3000);
});

/* ===== SMOOTH SCROLL ===== */
window.scrollTo = function (selector) {
  const el = document.querySelector(selector);
  if (el) el.scrollIntoView({ behavior: 'smooth' });
};
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    e.preventDefault();
    const target = document.querySelector(a.getAttribute('href'));
    if (target) target.scrollIntoView({ behavior: 'smooth' });
  });
});

/* ===== NAV BACKGROUND ON SCROLL ===== */
(function () {
  const nav = document.querySelector('.nav');
  window.addEventListener('scroll', () => {
    if (window.scrollY > 80) {
      nav.style.background = 'rgba(5,5,8,0.97)';
      nav.style.borderBottomColor = 'rgba(0,245,255,0.3)';
    } else {
      nav.style.background = 'rgba(5,5,8,0.85)';
      nav.style.borderBottomColor = 'rgba(0,245,255,0.2)';
    }
  });
})();

/* ===== HOLOGRAPHIC TILT ON PRODUCT CARDS ===== */
document.querySelectorAll('.product-card, .collection-card').forEach(card => {
  card.addEventListener('mousemove', e => {
    const rect = card.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width - 0.5;
    const y = (e.clientY - rect.top) / rect.height - 0.5;
    card.style.transform = `translateY(-6px) rotateX(${-y * 6}deg) rotateY(${x * 6}deg)`;
    card.style.boxShadow = `${-x * 10}px ${-y * 10}px 30px rgba(0,245,255,0.1)`;
  });
  card.addEventListener('mouseleave', () => {
    card.style.transform = '';
    card.style.boxShadow = '';
    card.style.transition = 'transform 0.4s, box-shadow 0.4s';
  });
  card.addEventListener('mouseenter', () => {
    card.style.transition = 'border-color 0.3s, background 0.3s';
  });
});

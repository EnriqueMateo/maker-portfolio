// Theme toggle, project filters, photo lightbox and the contact form.
(function () {
  const root = document.documentElement;

  // ---- Theme ----
  const toggle = document.querySelector('[data-theme-toggle]');
  if (toggle) {
    toggle.addEventListener('click', () => {
      const dark = root.dataset.theme
        ? root.dataset.theme === 'dark'
        : matchMedia('(prefers-color-scheme: dark)').matches;
      root.dataset.theme = dark ? 'light' : 'dark';
      try { localStorage.setItem('theme', root.dataset.theme); } catch (e) {}
    });
  }

  // ---- Project filters ----
  const filters = document.querySelectorAll('[data-filter]');
  filters.forEach((btn) =>
    btn.addEventListener('click', () => {
      filters.forEach((b) => b.classList.toggle('active', b === btn));
      const f = btn.dataset.filter;
      document.querySelectorAll('.card').forEach((card) => {
        card.hidden = Boolean(f) && !card.dataset.domains.split('|').includes(f);
      });
    })
  );

  // ---- Lightbox ----
  const lb = document.querySelector('[data-lightbox]');
  const imgs = Array.from(document.querySelectorAll('.prose img, .gallery img'));
  if (lb && imgs.length) {
    const lbImg = lb.querySelector('img');
    const lbCap = lb.querySelector('figcaption');
    let current = 0;

    const captionFor = (img) => {
      const td = img.closest('td');
      const sub = td && td.querySelector('sub');
      if (sub) return sub.textContent;
      const em = img.parentElement && img.parentElement.nextElementSibling;
      if (em && em.tagName === 'P' && em.firstElementChild && em.firstElementChild.tagName === 'EM') return em.textContent;
      return img.alt || '';
    };
    const show = (i) => {
      current = (i + imgs.length) % imgs.length;
      const img = imgs[current];
      lbImg.src = img.dataset.full || img.currentSrc || img.src;
      lbImg.alt = img.alt;
      lbCap.textContent = captionFor(img);
      lb.hidden = false;
      document.body.style.overflow = 'hidden';
    };
    const close = () => {
      lb.hidden = true;
      document.body.style.overflow = '';
    };

    imgs.forEach((img, i) =>
      img.addEventListener('click', (e) => {
        e.preventDefault();
        show(i);
      })
    );
    lb.querySelector('.lb-close').addEventListener('click', close);
    lb.querySelector('.lb-prev').addEventListener('click', () => show(current - 1));
    lb.querySelector('.lb-next').addEventListener('click', () => show(current + 1));
    lb.addEventListener('click', (e) => { if (e.target === lb) close(); });
    document.addEventListener('keydown', (e) => {
      if (lb.hidden) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') show(current - 1);
      if (e.key === 'ArrowRight') show(current + 1);
    });
  }

  // ---- Contact form ----
  const form = document.querySelector('[data-contact]');
  if (form) {
    const status = form.querySelector('.form-status');
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = form.querySelector('button[type=submit]');
      btn.disabled = true;
      status.className = 'form-status';
      status.textContent = 'Sending…';
      try {
        const res = await fetch('/api/contact', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(Object.fromEntries(new FormData(form))),
        });
        const json = await res.json().catch(() => ({}));
        if (!res.ok || !json.ok) throw new Error(json.error || 'Could not send the message.');
        form.reset();
        status.classList.add('ok');
        status.textContent = 'Thanks! Your message is on its way.';
      } catch (err) {
        status.classList.add('err');
        status.textContent = err.message;
      } finally {
        btn.disabled = false;
      }
    });
  }
})();

// Photo lightbox and the contact form.
(function () {
  // ---- Lightbox ----
  // Story photos open at full size; [data-lb] links (hero, gallery) open their href.
  const lb = document.querySelector('[data-lightbox]');
  const items = Array.from(document.querySelectorAll('[data-lb], .prose img')).filter(
    (el) => !(el.tagName === 'IMG' && el.closest('[data-lb]'))
  );
  if (lb && items.length) {
    const lbImg = lb.querySelector('img');
    const lbCap = lb.querySelector('figcaption');
    let current = 0;

    const imgOf = (el) => (el.tagName === 'IMG' ? el : el.querySelector('img'));
    const captionFor = (el) => {
      const img = imgOf(el);
      const sub = el.closest('td') && el.closest('td').querySelector('sub');
      if (sub) return sub.textContent;
      const em = img.parentElement && img.parentElement.querySelector(':scope > em');
      if (em) return em.textContent;
      return img.alt || '';
    };
    const show = (i) => {
      current = (i + items.length) % items.length;
      const el = items[current];
      const img = imgOf(el);
      lbImg.src = el.tagName === 'A' ? el.href : img.currentSrc || img.src;
      lbImg.alt = img.alt;
      lbCap.textContent = captionFor(el);
      lb.hidden = false;
      document.body.style.overflow = 'hidden';
      lb.querySelector('.lb-close').focus();
    };
    const close = () => {
      lb.hidden = true;
      document.body.style.overflow = '';
      const el = items[current];
      if (el && el.focus) el.focus({ preventScroll: true });
    };

    items.forEach((el, i) =>
      el.addEventListener('click', (e) => {
        e.preventDefault();
        show(i);
      })
    );
    lb.querySelector('.lb-close').addEventListener('click', close);
    lb.querySelector('.lb-prev').addEventListener('click', () => show(current - 1));
    lb.querySelector('.lb-next').addEventListener('click', () => show(current + 1));
    lb.addEventListener('click', (e) => { if (e.target === lb || e.target.tagName === 'FIGURE') close(); });
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
      if (window.STATIC_PREVIEW) {
        status.className = 'form-status';
        status.textContent = 'This is a static preview. The form sends messages once the site is deployed on Railway.';
        return;
      }
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

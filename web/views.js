// Server-rendered HTML templates (no build step, good for SEO and link previews).
//
// Visual language: an engineering drawing set. Each project is a numbered
// "sheet", key facts sit in a title block, and figures are numbered.

const { marked } = require('marked');

const esc = (s) =>
  String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);

const pad = (n) => String(n).padStart(2, '0');
const sheet = (i, total) => `Sheet ${pad(i + 1)} / ${pad(total)}`;
const dims = (m) => (m && m.width && m.height ? ` width="${m.width}" height="${m.height}"` : '');

const THEME_ICON = `<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><circle cx="12" cy="12" r="8.5" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M12 3.5a8.5 8.5 0 0 1 0 17z" fill="currentColor"/></svg>`;

function layout({ site, title, description, image, body, baseUrl, path, bodyClass = '' }) {
  const fullTitle = title ? `${title} — ${site.name}` : `${site.name} — Maker Portfolio`;
  const abs = (u) => (u && u.startsWith('/') && baseUrl ? baseUrl + u : u);
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>${esc(fullTitle)}</title>
<meta name="description" content="${esc(description)}">
<meta property="og:title" content="${esc(fullTitle)}">
<meta property="og:description" content="${esc(description)}">
<meta property="og:type" content="website">
${baseUrl ? `<meta property="og:url" content="${esc(baseUrl + path)}">` : ''}
${image ? `<meta property="og:image" content="${esc(abs(image))}">` : ''}
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..800&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/styles.css">
<script>try{var t=localStorage.getItem('theme');if(t)document.documentElement.dataset.theme=t}catch(e){}</script>
</head>
<body class="${bodyClass}">
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="/" aria-label="${esc(site.name)}, home">
      <span class="brand-mark" aria-hidden="true">EMC</span>
      <span class="brand-name">${esc(site.name)}</span>
    </a>
    <nav class="nav" aria-label="Main">
      <a href="/#projects">Projects</a>
      <a href="/#process">Process</a>
      <a href="/#contact">Contact</a>
      <a href="${esc(site.github)}" target="_blank" rel="noopener">GitHub</a>
      <button class="theme-toggle" type="button" aria-label="Toggle dark mode" data-theme-toggle>${THEME_ICON}</button>
    </nav>
  </div>
</header>
<main>
${body}
</main>
<footer class="site-footer">
  <div class="wrap footer-inner">
    <span>${esc(site.name)} · ${esc(site.location)} · ${new Date().getFullYear()}</span>
    <a class="mono" href="${esc(site.github)}/maker-portfolio" target="_blank" rel="noopener">Source of this site ↗</a>
  </div>
</footer>
<div class="lightbox" hidden data-lightbox role="dialog" aria-modal="true" aria-label="Photo viewer">
  <button class="lb-close" type="button" aria-label="Close">×</button>
  <button class="lb-prev" type="button" aria-label="Previous photo">‹</button>
  <figure><img alt=""><figcaption></figcaption></figure>
  <button class="lb-next" type="button" aria-label="Next photo">›</button>
</div>
<script src="/assets/app.js" defer></script>
</body>
</html>`;
}

function facts(list, cls = '') {
  if (!list || !list.length) return '';
  return `<dl class="facts ${cls}">${list.map((f) => `<div><dt>${esc(f.label)}</dt><dd>${esc(f.value)}</dd></div>`).join('')}</dl>`;
}

// Up to three app screenshots in phone frames, middle one in front.
function phones(p, cls = '') {
  const shots = p.media.filter((m) => m.kind === 'image').slice(0, 3);
  return `<div class="phones ${cls}">${shots
    .map((m) => `<img class="phone" src="${esc(m.thumb_url || m.url)}"${dims(m)} alt="${esc(m.caption || p.title)}" loading="lazy">`)
    .join('')}</div>`;
}

function projectRow(p, i, total) {
  const device = p.media_style === 'device';
  const visual = device
    ? phones(p)
    : `<img src="${esc(p.cover_url)}" alt="${esc(p.short_title || p.title)}" loading="${i === 0 ? 'eager' : 'lazy'}">`;
  return `<article class="row${i % 2 ? ' row--flip' : ''}" id="p-${esc(p.slug)}">
  <a class="row-media${device ? ' row-media--device' : ''}" href="/projects/${esc(p.slug)}" tabindex="-1" aria-hidden="true">
    ${visual}
    <span class="crop tl"></span><span class="crop tr"></span><span class="crop bl"></span><span class="crop br"></span>
  </a>
  <div class="row-copy">
    <p class="sheet mono">${sheet(i, total)}</p>
    <h3><a href="/projects/${esc(p.slug)}">${esc(p.short_title || p.title)}</a></h3>
    <p class="row-summary">${esc(p.summary)}</p>
    ${facts(p.facts)}
    <p class="domains mono">${p.domains.map(esc).join(' · ')}</p>
    <a class="arrow-link" href="/projects/${esc(p.slug)}">Read the build log <span aria-hidden="true">→</span></a>
  </div>
</article>`;
}

function home({ site, projects, baseUrl }) {
  const h = site.hero;
  const body = `
<section class="hero">
  <div class="wrap hero-grid">
    <div class="hero-copy">
      <p class="kicker"><span class="kicker-name">${esc(site.name)}</span><span class="mono">${esc(site.role)}</span></p>
      <h1>${esc(site.headline)}</h1>
      <p class="lead">${esc(site.intro)}</p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="#projects">See the projects</a>
        <a class="btn" href="#contact">Get in touch</a>
      </div>
    </div>
    <figure class="hero-visual" aria-label="From sketch to finished machine">
      <a class="hv hv-sketch" href="${esc(h.sketch.full)}" data-lb><img src="${esc(h.sketch.src)}" alt="${esc(h.sketch.alt)}"><span class="hv-label mono">A · ${esc(h.sketch.label)}</span></a>
      <a class="hv hv-built" href="${esc(h.built.full)}" data-lb><img src="${esc(h.built.src)}" alt="${esc(h.built.alt)}"><span class="hv-label mono">B · ${esc(h.built.label)}</span></a>
      <svg class="hv-arrow" viewBox="0 0 120 60" aria-hidden="true"><path d="M6 50 C 40 50, 70 40, 108 12" fill="none" stroke="currentColor" stroke-width="1.5" stroke-dasharray="4 4"/><path d="M98 10 L110 11 L104 22" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>
    </figure>
  </div>
  <div class="wrap">
    <dl class="title-block">
      ${site.titleBlock.map((c) => `<div><dt class="mono">${esc(c.label)}</dt><dd>${esc(c.value)}</dd></div>`).join('')}
    </dl>
  </div>
</section>

<section id="projects" class="section">
  <div class="wrap">
    <header class="section-head">
      <p class="mono section-label">Drawing set · ${pad(projects.length)} sheets</p>
      <h2>Projects</h2>
    </header>
    <div class="rows">
      ${projects.map((p, i) => projectRow(p, i, projects.length)).join('\n')}
    </div>
  </div>
</section>

<section id="process" class="section section--tint">
  <div class="wrap">
    <header class="section-head">
      <p class="mono section-label">How I work</p>
      <h2>Same loop, every build</h2>
    </header>
    <ol class="process">
      ${site.process.map((s) => `<li><h3>${esc(s.step)}</h3><p>${esc(s.text)}</p></li>`).join('')}
    </ol>
    <div class="principles">
      ${site.principles.map((pr) => `<article><h3>${esc(pr.title)}</h3><p>${esc(pr.text)}</p></article>`).join('')}
    </div>
  </div>
</section>

<section id="contact" class="section">
  <div class="wrap contact">
    <div class="contact-copy">
      <p class="mono section-label">Contact</p>
      <h2>Have something that needs building?</h2>
      <p class="lead">Internships, working-student roles, collaborations, or a question about one of the builds. Send a message and I'll reply by email.</p>
      <p class="mono"><a href="${esc(site.github)}" target="_blank" rel="noopener">${esc(site.github.replace('https://', ''))} ↗</a></p>
    </div>
    <form class="contact-form" data-contact novalidate>
      <div class="field"><label for="cf-name">Name</label><input id="cf-name" name="name" required maxlength="120" autocomplete="name"></div>
      <div class="field"><label for="cf-email">Email</label><input id="cf-email" name="email" type="email" required maxlength="200" autocomplete="email"></div>
      <div class="field"><label for="cf-message">Message</label><textarea id="cf-message" name="message" required maxlength="4000" rows="5"></textarea></div>
      <div class="hp" aria-hidden="true"><label for="cf-website">Website</label><input id="cf-website" name="website" tabindex="-1" autocomplete="off"></div>
      <button class="btn btn-primary" type="submit">Send message</button>
      <p class="form-status" role="status"></p>
    </form>
  </div>
</section>`;
  return layout({
    site,
    baseUrl,
    path: '/',
    description: `${site.name}, ${site.role}. ${site.intro}`,
    image: h.built.full,
    body,
    bodyClass: 'page-home',
  });
}

function project({ site, project: p, index, total, next, baseUrl }) {
  const extras = p.media.filter((m) => m.kind === 'extra');
  const device = p.media_style === 'device';
  const body = `
<article class="project${device ? ' project--device' : ''}">
  <header class="project-head">
    <div class="wrap project-head-grid">
      <div class="project-head-copy">
        <a class="back mono" href="/#p-${esc(p.slug)}">← All projects</a>
        <p class="sheet mono">${sheet(index, total)} · ${p.domains.map(esc).join(' · ')}</p>
        <h1>${esc(p.title)}</h1>
        ${p.tagline ? `<p class="lead">${marked.parseInline(p.tagline)}</p>` : ''}
        ${p.links.length ? `<p class="links">${p.links.map((l) => `<a class="btn btn-small" href="${esc(l.url)}" target="_blank" rel="noopener">${esc(l.label)} ↗</a>`).join(' ')}</p>` : ''}
      </div>
      ${facts(p.facts, 'facts--block')}
    </div>
  </header>
  <div class="prose">
    ${marked.parse(p.body_md || '')}
    ${
      extras.length
        ? `<section class="more-photos"><h2>More photos</h2><div class="gallery">${extras
            .map((m) => `<a href="${esc(m.url)}" class="gallery-item" data-lb><img src="${esc(m.thumb_url || m.url)}"${dims(m)} alt="${esc(m.caption || p.title)}" loading="lazy"></a>`)
            .join('')}</div></section>`
        : ''
    }
  </div>
  ${
    next
      ? `<a class="next-project${next.media_style === 'device' ? ' next-project--device' : ''}" href="/projects/${esc(next.slug)}">
    <div class="wrap next-inner">
      <div>
        <p class="mono">Next · ${sheet(index + 1 === total ? 0 : index + 1, total)}</p>
        <p class="next-title">${esc(next.short_title || next.title)} <span aria-hidden="true">→</span></p>
        <p class="next-summary">${esc(next.summary)}</p>
      </div>
      ${next.media_style === 'device' ? phones(next, 'phones--small') : `<img src="${esc(next.cover_thumb_url || next.cover_url)}" alt="" loading="lazy">`}
    </div>
  </a>`
      : ''
  }
</article>`;
  return layout({
    site,
    baseUrl,
    path: `/projects/${p.slug}`,
    title: p.short_title || p.title,
    description: p.summary || p.tagline,
    image: p.cover_url,
    body,
    bodyClass: 'page-project',
  });
}

function notFound({ site }) {
  return layout({
    site,
    path: '/404',
    title: 'Not found',
    description: 'Page not found',
    body: `<section class="hero"><div class="wrap"><p class="mono section-label">Error 404 · sheet missing</p><h1>This drawing isn't in the set.</h1><p class="lead">The page you're looking for doesn't exist.</p><p><a class="btn btn-primary" href="/">Back to the projects</a></p></div></section>`,
  });
}

module.exports = { home, project, notFound, esc };

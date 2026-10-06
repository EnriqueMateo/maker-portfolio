// Server-rendered HTML templates (no build step, good for SEO and link previews).

const { marked } = require('marked');

const esc = (s) =>
  String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);

function layout({ site, title, description, image, body, baseUrl, path }) {
  const fullTitle = title ? `${title} — ${site.name}` : `${site.name} — Maker Portfolio`;
  const abs = (u) => (u && u.startsWith('/') && baseUrl ? baseUrl + u : u);
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
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
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/styles.css">
<script>try{var t=localStorage.getItem('theme');if(t)document.documentElement.dataset.theme=t}catch(e){}</script>
</head>
<body>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="/"><span class="brand-mark">EMC</span><span class="brand-name">${esc(site.name)}</span></a>
    <nav class="nav">
      <a href="/#projects">Projects</a>
      <a href="/#about">About</a>
      <a href="/#contact">Contact</a>
      <a href="${esc(site.github)}" target="_blank" rel="noopener">GitHub</a>
      <button class="theme-toggle" type="button" aria-label="Toggle dark mode" data-theme-toggle>◐</button>
    </nav>
  </div>
</header>
<main>
${body}
</main>
<footer class="site-footer">
  <div class="wrap footer-inner">
    <span>© ${new Date().getFullYear()} ${esc(site.name)} · ${esc(site.location)}</span>
    <span class="mono">Built with Express · Supabase · Railway</span>
  </div>
</footer>
<div class="lightbox" hidden data-lightbox>
  <button class="lb-close" type="button" aria-label="Close">×</button>
  <button class="lb-prev" type="button" aria-label="Previous">‹</button>
  <figure><img alt=""><figcaption></figcaption></figure>
  <button class="lb-next" type="button" aria-label="Next">›</button>
</div>
<script src="/assets/app.js" defer></script>
</body>
</html>`;
}

function projectCard(p) {
  return `<a class="card" href="/projects/${esc(p.slug)}" data-domains="${esc(p.domains.join('|'))}">
  <div class="card-media">${p.cover_thumb_url || p.cover_url ? `<img src="${esc(p.cover_thumb_url || p.cover_url)}" alt="${esc(p.short_title || p.title)}" loading="lazy">` : ''}</div>
  <div class="card-body">
    <h3>${p.emoji ? `<span class="emoji">${esc(p.emoji)}</span> ` : ''}${esc(p.short_title || p.title)}</h3>
    <p>${esc(p.summary)}</p>
    <ul class="chips">${p.domains.map((d) => `<li>${esc(d)}</li>`).join('')}</ul>
  </div>
</a>`;
}

function home({ site, projects, baseUrl }) {
  const domains = [...new Set(projects.flatMap((p) => p.domains))];
  const body = `
<section class="hero wrap">
  <p class="eyebrow mono">${esc(site.role)}</p>
  <h1>${esc(site.name)}</h1>
  <p class="lead">${esc(site.headline)}</p>
  <p class="sub">${esc(site.intro)}</p>
  <div class="hero-actions">
    <a class="btn primary" href="#projects">See the projects</a>
    <a class="btn" href="#contact">Get in touch</a>
  </div>
  <dl class="stats">
    ${site.stats.map((s) => `<div><dt>${esc(s.value)}</dt><dd>${esc(s.label)}</dd></div>`).join('')}
  </dl>
</section>

<section id="projects" class="section wrap">
  <div class="section-head">
    <h2>Projects</h2>
    <div class="filters" role="group" aria-label="Filter by domain">
      <button type="button" class="filter active" data-filter="">All</button>
      ${domains.map((d) => `<button type="button" class="filter" data-filter="${esc(d)}">${esc(d)}</button>`).join('')}
    </div>
  </div>
  <div class="grid">
    ${projects.map(projectCard).join('\n')}
  </div>
</section>

<section id="about" class="section wrap">
  <h2>How I work</h2>
  <div class="principles">
    ${site.howIWork.map((h, i) => `<article><span class="mono idx">0${i + 1}</span><h3>${esc(h.title)}</h3><p>${esc(h.text)}</p></article>`).join('')}
  </div>
</section>

<section id="contact" class="section wrap">
  <div class="contact">
    <div>
      <h2>Let's build something</h2>
      <p class="sub">Internships, working student positions, collaborations or just a question about a build — drop me a message.</p>
      <p><a href="${esc(site.github)}" target="_blank" rel="noopener">${esc(site.github.replace('https://', ''))}</a></p>
    </div>
    <form class="contact-form" data-contact>
      <label>Name<input name="name" required maxlength="120" autocomplete="name"></label>
      <label>Email<input name="email" type="email" required maxlength="200" autocomplete="email"></label>
      <label>Message<textarea name="message" required maxlength="4000" rows="5"></textarea></label>
      <label class="hp" aria-hidden="true">Website<input name="website" tabindex="-1" autocomplete="off"></label>
      <button class="btn primary" type="submit">Send message</button>
      <p class="form-status" role="status"></p>
    </form>
  </div>
</section>`;
  return layout({
    site,
    baseUrl,
    path: '/',
    description: `${site.role}. ${site.headline}`,
    image: projects[0]?.cover_url,
    body,
  });
}

function project({ site, project: p, prev, next, baseUrl }) {
  const extras = p.media.filter((m) => m.kind === 'extra');
  const body = `
<article class="project wrap">
  <a class="back mono" href="/#projects">← All projects</a>
  <header class="project-head">
    <ul class="chips">${p.domains.map((d) => `<li>${esc(d)}</li>`).join('')}</ul>
    <h1>${esc(p.title)}</h1>
    ${p.tagline ? `<p class="lead">${marked.parseInline(p.tagline)}</p>` : ''}
    ${p.links.length ? `<p class="links">${p.links.map((l) => `<a class="btn small" href="${esc(l.url)}" target="_blank" rel="noopener">${esc(l.label)} ↗</a>`).join(' ')}</p>` : ''}
  </header>
  <div class="prose">
    ${marked.parse(p.body_md || '')}
  </div>
  ${
    extras.length
      ? `<section class="more-photos"><h2>More photos</h2><div class="gallery">${extras
          .map((m) => `<a href="${esc(m.url)}" class="gallery-item"><img src="${esc(m.thumb_url || m.url)}" data-full="${esc(m.url)}" alt="${esc(m.caption || p.title)}" loading="lazy"></a>`)
          .join('')}</div></section>`
      : ''
  }
  <nav class="pager">
    ${prev ? `<a href="/projects/${esc(prev.slug)}"><span class="mono">← Previous</span>${esc(prev.short_title || prev.title)}</a>` : '<span></span>'}
    ${next ? `<a class="next" href="/projects/${esc(next.slug)}"><span class="mono">Next →</span>${esc(next.short_title || next.title)}</a>` : '<span></span>'}
  </nav>
</article>`;
  return layout({
    site,
    baseUrl,
    path: `/projects/${p.slug}`,
    title: p.short_title || p.title,
    description: p.summary || p.tagline,
    image: p.cover_url,
    body,
  });
}

function notFound({ site }) {
  return layout({
    site,
    path: '/404',
    title: 'Not found',
    description: 'Page not found',
    body: `<section class="hero wrap"><p class="eyebrow mono">404</p><h1>Nothing printed here.</h1><p class="lead">That page doesn't exist.</p><a class="btn primary" href="/">Back home</a></section>`,
  });
}

module.exports = { home, project, notFound, esc };

// Server-rendered HTML templates (no build step, good for SEO and link previews).

const { marked } = require('marked');

const esc = (s) =>
  String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);

const dims = (m) => (m && m.width && m.height ? ` width="${m.width}" height="${m.height}"` : '');

function layout({ site, title, description, image, body, baseUrl, path }) {
  const fullTitle = title ? `${title} — ${site.name}` : `${site.name} — Portfolio`;
  const abs = (u) => (u && u.startsWith('/') && baseUrl ? baseUrl + u : u);
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>${esc(fullTitle)}</title>
<meta name="description" content="${esc(description)}">
<meta name="color-scheme" content="light">
<meta property="og:title" content="${esc(fullTitle)}">
<meta property="og:description" content="${esc(description)}">
<meta property="og:type" content="website">
${baseUrl ? `<meta property="og:url" content="${esc(baseUrl + path)}">` : ''}
${image ? `<meta property="og:image" content="${esc(abs(image))}">` : ''}
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/styles.css">
</head>
<body>
<header class="site-header">
  <div class="container header-inner">
    <a class="brand" href="/">${esc(site.name)}</a>
    <nav class="nav" aria-label="Main">
      <a href="/#projects">Projects</a>
      <a href="/#about">About</a>
      <a href="/#contact">Contact</a>
    </nav>
  </div>
</header>
<main>
${body}
</main>
<footer class="site-footer">
  <div class="container footer-inner">
    <span>© ${new Date().getFullYear()} ${esc(site.name)} · ${esc(site.location)}</span>
    <a href="${esc(site.github)}" target="_blank" rel="noopener">GitHub ↗</a>
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

function facts(list, limit) {
  const items = (list || []).slice(0, limit || undefined);
  if (!items.length) return '';
  return `<dl class="facts">${items.map((f) => `<div><dt>${esc(f.label)}</dt><dd>${esc(f.value)}</dd></div>`).join('')}</dl>`;
}

// App screenshots: three phones side by side, same size, never cropped.
function phones(p) {
  const shots = p.media.filter((m) => m.kind === 'image').slice(0, 3);
  return `<div class="phones">${shots
    .map((m) => `<img class="phone" src="${esc(m.thumb_url || m.url)}"${dims(m)} alt="${esc(m.caption || p.title)}" loading="lazy">`)
    .join('')}</div>`;
}

function projectCard(p) {
  const device = p.media_style === 'device';
  return `<article class="card">
  <a class="card-media${device ? ' card-media--device' : ''}" href="/projects/${esc(p.slug)}" tabindex="-1" aria-hidden="true">
    ${device ? phones(p) : `<img src="${esc(p.cover_url)}" alt="" loading="lazy">`}
  </a>
  <div class="card-body">
    <p class="eyebrow">${p.domains.slice(0, 3).map(esc).join(' · ')}</p>
    <h3><a href="/projects/${esc(p.slug)}">${esc(p.short_title || p.title)}</a></h3>
    <p class="card-summary">${esc(p.summary)}</p>
    ${facts(p.facts, 2)}
    <a class="text-link" href="/projects/${esc(p.slug)}">View project <span aria-hidden="true">→</span></a>
  </div>
</article>`;
}

function home({ site, projects, baseUrl }) {
  const body = `
<section class="hero">
  <div class="container hero-grid">
    <div class="hero-copy">
      <p class="eyebrow">${esc(site.role)}</p>
      <h1>${esc(site.name)}</h1>
      <p class="hero-headline">${esc(site.headline)}</p>
      <p class="lead">${esc(site.intro)}</p>
      <div class="actions">
        <a class="btn btn-primary" href="#projects">View projects</a>
        <a class="btn" href="#contact">Contact me</a>
      </div>
    </div>
    <figure class="hero-media">
      <img src="${esc(site.heroImage.src)}" alt="${esc(site.heroImage.alt)}" width="1600" height="900">
      <figcaption>${esc(site.heroCaption)}</figcaption>
    </figure>
  </div>
  <div class="container">
    <dl class="stats">
      ${site.stats.map((s) => `<div><dt>${esc(s.label)}</dt><dd>${esc(s.value)}</dd></div>`).join('')}
    </dl>
  </div>
</section>

<section id="projects" class="section">
  <div class="container">
    <div class="section-head">
      <h2>Projects</h2>
      <p>Hardware and software I designed and built myself.</p>
    </div>
    <div class="cards">
      ${projects.map(projectCard).join('\n')}
    </div>
  </div>
</section>

<section id="about" class="section section--alt">
  <div class="container about">
    <div class="section-head">
      <h2>About</h2>
    </div>
    <div class="about-body">
      ${site.about.map((t) => `<p>${esc(t)}</p>`).join('')}
      <div class="skills">
        ${site.skills.map((s) => `<div><h3>${esc(s.area)}</h3><ul>${s.items.map((i) => `<li>${esc(i)}</li>`).join('')}</ul></div>`).join('')}
      </div>
      <p class="languages"><strong>Languages</strong> ${esc(site.languages)}</p>
    </div>
  </div>
</section>

<section id="contact" class="section">
  <div class="container contact">
    <div class="section-head">
      <h2>Contact</h2>
      <p>Internships, working-student roles, collaborations or questions about a build. I reply by email.</p>
      <p><a class="text-link" href="${esc(site.github)}" target="_blank" rel="noopener">${esc(site.github.replace('https://', ''))} ↗</a></p>
    </div>
    <form class="contact-form" data-contact novalidate>
      <div class="field-row">
        <div class="field"><label for="cf-name">Name</label><input id="cf-name" name="name" required maxlength="120" autocomplete="name"></div>
        <div class="field"><label for="cf-email">Email</label><input id="cf-email" name="email" type="email" required maxlength="200" autocomplete="email"></div>
      </div>
      <div class="field"><label for="cf-message">Message</label><textarea id="cf-message" name="message" required maxlength="4000" rows="5"></textarea></div>
      <div class="hp" aria-hidden="true"><label for="cf-website">Website</label><input id="cf-website" name="website" tabindex="-1" autocomplete="off"></div>
      <div class="form-foot">
        <button class="btn btn-primary" type="submit">Send message</button>
        <p class="form-status" role="status"></p>
      </div>
    </form>
  </div>
</section>`;
  return layout({
    site,
    baseUrl,
    path: '/',
    description: `${site.name}, ${site.role}. ${site.intro}`,
    image: site.heroImage.src,
    body,
  });
}

function project({ site, project: p, next, baseUrl }) {
  const extras = p.media.filter((m) => m.kind === 'extra');
  const device = p.media_style === 'device';
  const body = `
<article class="project${device ? ' project--device' : ''}">
  <header class="project-head container">
    <a class="back" href="/#projects">← All projects</a>
    <p class="eyebrow">${p.domains.map(esc).join(' · ')}</p>
    <h1>${esc(p.title)}</h1>
    ${p.tagline ? `<p class="lead">${marked.parseInline(p.tagline)}</p>` : ''}
    ${facts(p.facts)}
    ${p.links.length ? `<p class="links">${p.links.map((l) => `<a class="text-link" href="${esc(l.url)}" target="_blank" rel="noopener">${esc(l.label)} ↗</a>`).join(' ')}</p>` : ''}
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
      ? `<nav class="container next" aria-label="Next project">
    <a href="/projects/${esc(next.slug)}">
      <span class="eyebrow">Next project</span>
      <span class="next-title">${esc(next.short_title || next.title)} <span aria-hidden="true">→</span></span>
    </a>
  </nav>`
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
  });
}

function notFound({ site }) {
  return layout({
    site,
    path: '/404',
    title: 'Not found',
    description: 'Page not found',
    body: `<section class="hero"><div class="container"><p class="eyebrow">404</p><h1>Page not found</h1><p class="lead">The page you're looking for doesn't exist.</p><div class="actions"><a class="btn btn-primary" href="/">Back to home</a></div></div></section>`,
  });
}

module.exports = { home, project, notFound, esc };

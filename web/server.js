const path = require('path');

try { process.loadEnvFile(path.join(__dirname, '..', '.env')); } catch {}

const express = require('express');
const data = require('./lib/data');
const views = require('./views');
const site = require('../content/site.json');

const app = express();
const PORT = process.env.PORT || 3000;
// Railway exposes the public domain; used for absolute og:image / og:url.
const BASE_URL = (process.env.PUBLIC_URL || (process.env.RAILWAY_PUBLIC_DOMAIN ? `https://${process.env.RAILWAY_PUBLIC_DOMAIN}` : '')).replace(/\/$/, '');

app.set('trust proxy', 1);
app.disable('x-powered-by');
app.use((req, res, next) => {
  res.set('X-Content-Type-Options', 'nosniff');
  res.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  next();
});

app.use('/assets', express.static(path.join(__dirname, 'public'), { maxAge: '1h' }));
app.use('/media', express.static(path.join(__dirname, '..', '.cache', 'media'), { maxAge: '30d', immutable: true }));

const wrap = (fn) => (req, res, next) => fn(req, res, next).catch(next);

// ---- Pages ---------------------------------------------------------------

app.get('/', wrap(async (req, res) => {
  const projects = await data.listProjects();
  res.send(views.home({ site, projects, baseUrl: BASE_URL }));
}));

app.get('/projects/:slug', wrap(async (req, res) => {
  const projects = await data.listProjects();
  const i = projects.findIndex((p) => p.slug === req.params.slug);
  if (i === -1) return res.status(404).send(views.notFound({ site }));
  res.send(views.project({ site, project: projects[i], prev: projects[i - 1], next: projects[i + 1], baseUrl: BASE_URL }));
}));

// ---- API -----------------------------------------------------------------

app.get('/api/health', (req, res) => res.json({ ok: true, ...data.status() }));

app.get('/api/projects', wrap(async (req, res) => {
  const projects = await data.listProjects();
  res.json(projects.map(({ body_md, media, ...p }) => p));
}));

app.get('/api/projects/:slug', wrap(async (req, res) => {
  const p = await data.getProject(req.params.slug);
  if (!p) return res.status(404).json({ error: 'not_found' });
  res.json(p);
}));

// Tiny in-memory rate limit: 5 messages per IP per hour.
const hits = new Map();
function rateLimited(ip) {
  const now = Date.now();
  const recent = (hits.get(ip) || []).filter((t) => now - t < 3600_000);
  recent.push(now);
  hits.set(ip, recent);
  return recent.length > 5;
}

app.post('/api/contact', express.json({ limit: '16kb' }), wrap(async (req, res) => {
  const { name, email, message, website } = req.body || {};
  if (website) return res.json({ ok: true }); // honeypot: silently drop bots
  const clean = (s, max) => (typeof s === 'string' ? s.trim().slice(0, max) : '');
  const msg = { name: clean(name, 120), email: clean(email, 200), message: clean(message, 4000) };
  if (!msg.name || !msg.message || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(msg.email)) {
    return res.status(400).json({ ok: false, error: 'Please fill in your name, a valid email and a message.' });
  }
  if (rateLimited(req.ip)) return res.status(429).json({ ok: false, error: 'Too many messages — try again later.' });
  const result = await data.saveContactMessage(msg);
  if (!result.ok) {
    const error = result.reason === 'not_configured' ? 'The contact form is not connected yet.' : 'Could not send right now — please try again later.';
    return res.status(503).json({ ok: false, error });
  }
  res.json({ ok: true });
}));

// ---- Fallbacks -----------------------------------------------------------

app.use((req, res) => res.status(404).send(views.notFound({ site })));
app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).send('Something went wrong.');
});

if (require.main === module) {
  app.listen(PORT, () => {
    const s = data.status();
    console.log(`Portfolio listening on :${PORT} (supabase read: ${s.supabaseRead}, write: ${s.supabaseWrite})`);
  });
}

module.exports = app;

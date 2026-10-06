const { test, before, after } = require('node:test');
const assert = require('node:assert');

process.env.SUPABASE_URL = ''; // always test the local-content path (an existing .env won't override this)
const app = require('../web/server');
const projects = require('../content/projects.json');

let server, base;
before(() => new Promise((r) => { server = app.listen(0, () => { base = `http://127.0.0.1:${server.address().port}`; r(); }); }));
after(() => server.close());

test('content was parsed from the READMEs', () => {
  assert.deepStrictEqual(projects.map((p) => p.slug), ['3d-printer', 'rc-car', 'filament-recycler', 'shapio']);
  for (const p of projects) {
    assert.ok(p.title && p.summary && p.domains.length && p.cover_url, p.slug);
    assert.ok(!p.body_md.includes('src="./'), `${p.slug} has unrewritten image paths`);
  }
});

test('home lists every project', async () => {
  const html = await (await fetch(base + '/')).text();
  for (const p of projects) assert.ok(html.includes(`/projects/${p.slug}`), p.slug);
});

test('project page renders the story', async () => {
  const res = await fetch(base + '/projects/3d-printer');
  assert.strictEqual(res.status, 200);
  const html = await res.text();
  assert.ok(html.includes('KMI 2.0'));
  assert.ok(html.includes('class="media-grid"'));
});

test('unknown project is a 404', async () => {
  assert.strictEqual((await fetch(base + '/projects/nope')).status, 404);
});

test('api returns projects and health', async () => {
  const list = await (await fetch(base + '/api/projects')).json();
  assert.strictEqual(list.length, projects.length);
  const health = await (await fetch(base + '/api/health')).json();
  assert.deepStrictEqual([health.ok, health.source], [true, 'local']);
});

test('contact validates input and reports when not connected', async () => {
  const post = (body) => fetch(base + '/api/contact', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  assert.strictEqual((await post({ name: 'A', email: 'bad', message: 'hi' })).status, 400);
  assert.strictEqual((await post({ name: 'A', email: 'a@b.co', message: 'hi' })).status, 503);
});

#!/usr/bin/env node
// Parses the repo READMEs into content/projects.json — the local source of
// truth the site falls back to, and what `npm run seed` imports into Supabase.
//
// Image paths are rewritten to /media/<slug>/<name>.webp; build-media.js
// produces those files and seed-supabase.js uploads them to Storage.

const fs = require('fs');
const path = require('path');
const { mediaName, IMAGE_EXT } = require('./lib/media-names');

const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'content', 'projects.json');
// Card/preview image when the first photo in the README isn't the best one.
const COVER_OVERRIDES = { '3d-printer': 'DSC04210.JPG' };

function parseRootTable(md) {
  // | 🖨️ [**Title**](./slug) | What it is | Domains |
  const rows = [];
  const re = /^\|\s*(\S+)\s+\[\*\*(.+?)\*\*\]\(\.\/([\w-]+)\)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*$/gm;
  let m;
  while ((m = re.exec(md))) {
    rows.push({
      emoji: m[1],
      shortTitle: m[2],
      slug: m[3],
      summary: m[4].replace(/\*\*/g, ''),
      domains: m[5].split('·').map((d) => d.trim()).filter(Boolean),
    });
  }
  return rows;
}

function parseProjectReadme(slug, md) {
  const lines = md.split('\n');
  const titleIdx = lines.findIndex((l) => l.startsWith('# '));
  const title = lines[titleIdx].slice(2).trim();

  let i = titleIdx + 1;
  while (i < lines.length && !lines[i].trim()) i++;
  const taglineLines = [];
  while (i < lines.length && lines[i].startsWith('>')) {
    taglineLines.push(lines[i].replace(/^>\s?/, ''));
    i++;
  }
  const tagline = taglineLines.join(' ').trim();

  let body = lines.slice(i).join('\n');
  // The trailing "## Media" section only describes the repo folder.
  body = body.replace(/\n## Media\b[\s\S]*$/, '\n').trim();
  return { title, tagline, body };
}

function collectMedia(slug, body) {
  const dir = path.join(ROOT, slug);
  const used = [];
  const seen = new Set();
  const add = (file, caption) => {
    if (seen.has(file)) return;
    seen.add(file);
    used.push({ file, caption: caption || null });
  };

  // <img src="./X" ...><br><sub>caption</sub>
  const htmlRe = /<img\s+src="\.\/([^"]+)"[^>]*>(?:<br>\s*<sub>([\s\S]*?)<\/sub>)?/g;
  // ![alt](./X)\n*caption*
  const mdRe = /!\[([^\]]*)\]\(\.\/([^)]+)\)(?:\n\*(.+?)\*\s*$)?/gm;
  const matches = [];
  let m;
  while ((m = htmlRe.exec(body))) matches.push({ at: m.index, file: decodeURIComponent(m[1]), caption: m[2] });
  while ((m = mdRe.exec(body))) matches.push({ at: m.index, file: decodeURIComponent(m[2]), caption: m[3] || m[1] });
  matches.sort((a, b) => a.at - b.at).forEach((x) => add(x.file, stripMd(x.caption)));

  const inBody = new Set(used.map((u) => u.file));
  const extra = fs
    .readdirSync(dir)
    .filter((f) => IMAGE_EXT.test(f) && !inBody.has(f))
    .sort()
    .map((file) => ({ file, caption: null }));

  return { used, extra };
}

function stripMd(s) {
  if (!s) return s;
  return s.replace(/<[^>]+>/g, '').replace(/\*\*/g, '').replace(/\s+/g, ' ').trim();
}

function rewriteBody(slug, body) {
  const url = (file) => `/media/${slug}/${mediaName(decodeURIComponent(file))}`;
  return body
    .replace(/src="\.\/([^"]+)"/g, (_, f) => `src="${url(f)}" loading="lazy"`)
    .replace(/(!\[[^\]]*\]\()\.\/([^)]+)\)/g, (_, pre, f) => `${pre}${url(f)})`)
    // Raw HTML photo tables become responsive grids; markdown tables (specs) stay tables.
    .replace(/<table>/g, '<table class="media-grid">')
    .replace(/\s(width|height)="\d+"/g, '');
}

function main() {
  const rootMd = fs.readFileSync(path.join(ROOT, 'README.md'), 'utf8');
  const rows = parseRootTable(rootMd);
  if (!rows.length) throw new Error('Could not parse the projects table in README.md');

  const projects = rows.map((row, idx) => {
    const md = fs.readFileSync(path.join(ROOT, row.slug, 'README.md'), 'utf8');
    const { title, tagline, body } = parseProjectReadme(row.slug, md);
    const { used, extra } = collectMedia(row.slug, body);
    const toMedia = (kind) => (x, i) => ({
      url: `/media/${row.slug}/${mediaName(x.file)}`,
      thumb_url: `/media/${row.slug}/${mediaName(x.file, 'sm')}`,
      caption: x.caption,
      kind,
      sort_order: i,
    });
    const media = [...used.map(toMedia('image')), ...extra.map((x, i) => toMedia('extra')(x, used.length + i))];
    const coverFile = COVER_OVERRIDES[row.slug];
    const cover = (coverFile && media.find((m) => m.url.endsWith(`/${mediaName(coverFile)}`))) || media[0];
    return {
      slug: row.slug,
      emoji: row.emoji,
      title,
      short_title: row.shortTitle,
      tagline,
      summary: row.summary,
      domains: row.domains,
      body_md: rewriteBody(row.slug, body),
      cover_url: cover ? cover.url : null,
      cover_thumb_url: cover ? cover.thumb_url : null,
      links: [{ label: 'Source on GitHub', url: `https://github.com/EnriqueMateo/maker-portfolio/tree/main/${row.slug}` }],
      sort_order: idx,
      published: true,
      media,
    };
  });

  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  fs.writeFileSync(OUT, JSON.stringify(projects, null, 2) + '\n');
  console.log(`Wrote ${projects.length} projects → ${path.relative(ROOT, OUT)}`);
  for (const p of projects) console.log(`  ${p.slug}: ${p.media.length} images`);
}

if (require.main === module) main();
module.exports = { parseRootTable, parseProjectReadme, rewriteBody };

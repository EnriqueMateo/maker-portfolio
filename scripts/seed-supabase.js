#!/usr/bin/env node
// Imports content/projects.json into Supabase and uploads the optimized
// photos (.cache/media, from `npm run build`) to the public "portfolio" bucket.
//
//   SUPABASE_URL=... SUPABASE_SERVICE_ROLE_KEY=... npm run seed
//
// Safe to re-run: projects are upserted by slug and their media rows replaced.
// Projects you created only in Supabase are left alone.

const fs = require('fs');
const path = require('path');
const { createClient } = require('@supabase/supabase-js');

try { process.loadEnvFile(path.resolve(__dirname, '..', '.env')); } catch {}

const ROOT = path.resolve(__dirname, '..');
const MEDIA_DIR = path.join(ROOT, '.cache', 'media');
const BUCKET = process.env.SUPABASE_BUCKET || 'portfolio';

const { SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY } = process.env;
if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
  console.error('Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (in .env or the environment).');
  process.exit(1);
}
const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, { auth: { persistSession: false } });
const publicBase = `${SUPABASE_URL.replace(/\/$/, '')}/storage/v1/object/public/${BUCKET}/`;
const toPublic = (s) => (typeof s === 'string' ? s.split('/media/').join(publicBase) : s);

function walk(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) =>
    e.isDirectory() ? walk(path.join(dir, e.name)) : [path.join(dir, e.name)]
  );
}

async function uploadMedia() {
  if (!fs.existsSync(MEDIA_DIR)) throw new Error('No .cache/media — run `npm run build` first.');
  const files = walk(MEDIA_DIR);
  let done = 0;
  for (const file of files) {
    const key = path.relative(MEDIA_DIR, file).split(path.sep).join('/');
    const { error } = await supabase.storage.from(BUCKET).upload(key, fs.readFileSync(file), {
      contentType: 'image/webp',
      cacheControl: '31536000',
      upsert: true,
    });
    if (error) throw new Error(`upload ${key}: ${error.message}`);
    if (++done % 20 === 0) console.log(`  uploaded ${done}/${files.length}`);
  }
  console.log(`Uploaded ${files.length} files to bucket "${BUCKET}"`);
}

async function upsertProjects() {
  const projects = JSON.parse(fs.readFileSync(path.join(ROOT, 'content', 'projects.json'), 'utf8'));
  for (const { media, ...p } of projects) {
    const row = { ...p, body_md: toPublic(p.body_md), cover_url: toPublic(p.cover_url), cover_thumb_url: toPublic(p.cover_thumb_url) };
    const { data, error } = await supabase.from('projects').upsert(row, { onConflict: 'slug' }).select('id').single();
    if (error) throw new Error(`project ${p.slug}: ${error.message}`);

    const del = await supabase.from('project_media').delete().eq('project_id', data.id);
    if (del.error) throw new Error(`media ${p.slug}: ${del.error.message}`);
    const rows = media.map((m) => ({ ...m, url: toPublic(m.url), thumb_url: toPublic(m.thumb_url), project_id: data.id }));
    const ins = await supabase.from('project_media').insert(rows);
    if (ins.error) throw new Error(`media ${p.slug}: ${ins.error.message}`);
    console.log(`  ${p.slug}: ${rows.length} media`);
  }
  console.log(`Upserted ${projects.length} projects`);
}

(async () => {
  await uploadMedia();
  await upsertProjects();
  console.log('Done. Your site now reads from Supabase.');
})().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});

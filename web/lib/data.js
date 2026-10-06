// Project data access. Reads from Supabase when SUPABASE_URL + SUPABASE_ANON_KEY
// are set; otherwise (or if Supabase errors / is still empty) falls back to the
// bundled content/projects.json so the site always renders.

const path = require('path');
const { createClient } = require('@supabase/supabase-js');

const LOCAL = require(path.join(__dirname, '..', '..', 'content', 'projects.json'));
const CACHE_MS = Number(process.env.CACHE_SECONDS ?? 60) * 1000;

const { SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY } = process.env;
const opts = { auth: { persistSession: false } };
const reader = SUPABASE_URL && SUPABASE_ANON_KEY ? createClient(SUPABASE_URL, SUPABASE_ANON_KEY, opts) : null;
const writer = SUPABASE_URL && SUPABASE_SERVICE_ROLE_KEY ? createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, opts) : null;

let cache = { at: 0, projects: null, source: 'local' };

function normalize(p) {
  const media = [...(p.media || p.project_media || [])].sort((a, b) => a.sort_order - b.sort_order);
  const { project_media, ...rest } = p;
  return { ...rest, domains: p.domains || [], links: p.links || [], media };
}

async function fetchFromSupabase() {
  const { data, error } = await reader
    .from('projects')
    .select('*, project_media(url, thumb_url, caption, kind, sort_order)')
    .eq('published', true)
    .order('sort_order', { ascending: true });
  if (error) throw error;
  return data;
}

async function listProjects() {
  if (cache.projects && Date.now() - cache.at < CACHE_MS) return cache.projects;
  let projects = LOCAL;
  let source = 'local';
  if (reader) {
    try {
      const rows = await fetchFromSupabase();
      if (rows.length) {
        projects = rows;
        source = 'supabase';
      } else {
        console.warn('[data] Supabase has no published projects yet — serving local content (run `npm run seed`).');
      }
    } catch (err) {
      console.error('[data] Supabase read failed, serving local content:', err.message);
      // Keep the last good Supabase copy if we have one.
      if (cache.source === 'supabase' && cache.projects) return cache.projects;
    }
  }
  cache = { at: Date.now(), projects: projects.filter((p) => p.published !== false).map(normalize), source };
  return cache.projects;
}

async function getProject(slug) {
  return (await listProjects()).find((p) => p.slug === slug) || null;
}

async function saveContactMessage(msg) {
  if (!writer) return { ok: false, reason: 'not_configured' };
  const { error } = await writer.from('contact_messages').insert(msg);
  if (error) {
    console.error('[contact] insert failed:', error.message);
    return { ok: false, reason: 'db_error' };
  }
  return { ok: true };
}

const status = () => ({
  source: cache.source,
  supabaseRead: Boolean(reader),
  supabaseWrite: Boolean(writer),
});

module.exports = { listProjects, getProject, saveContactMessage, status };

# Portfolio website

A server-rendered portfolio site for the projects in this repo.

- **Railway** hosts the Node/Express server (`web/`).
- **Supabase** stores the projects (Postgres), the photos (Storage) and contact-form messages.
- The project READMEs are the initial content. `npm run content` parses them into `content/projects.json`. The site **falls back to that file** whenever Supabase isn't configured or is still empty, so it works on day one.

```
README.md files ──npm run content──▶ content/projects.json ──npm run seed──▶ Supabase (tables + Storage)
                                              │                                   │
                                              └──────── fallback ◀── web/server.js ┘  (Railway)
```

## Run locally

```bash
npm install
npm run build      # converts the photos to web-sized WebP in .cache/media (≈30 s the first time)
npm run dev        # http://localhost:3000
npm test
```

## 1. Set up Supabase

1. Create a project at [supabase.com](https://supabase.com).
2. Open the **SQL Editor**, run the files in [`supabase/migrations/`](supabase/migrations/) in order (`0001_init.sql`, then `0002_facts_and_media_style.sql`). This creates the `projects`, `project_media` and `contact_messages` tables, the RLS policies and the public `portfolio` storage bucket.
3. In **Project Settings → API**, copy the project URL, the `anon` key and the `service_role` key.
4. Import the projects and photos:
   ```bash
   cp .env.example .env   # fill in the three values
   npm run build
   npm run seed
   ```
   You can re-run `seed` safely. It upserts by `slug`, so projects you create directly in Supabase are left alone.

## 2. Deploy on Railway

1. **New Project → Deploy from GitHub repo** → pick `maker-portfolio`. Railway reads `railway.json`, which sets the build (`npm run build`), start (`npm start`) and health check (`/api/health`).
2. In the service's **Variables**, add `SUPABASE_URL`, `SUPABASE_ANON_KEY` and `SUPABASE_SERVICE_ROLE_KEY`.
3. Go to **Settings → Networking → Generate Domain**, or attach your own domain.
4. Open `https://<your-domain>/api/health`. `"source": "supabase"` means the site is reading from the database.

## Adding or editing projects

Once the projects are seeded, Supabase is the source of truth. In the **Table Editor**:

- **`projects`**: one row per project. `body_md` is the story in Markdown (HTML is allowed). `facts` is a list of `{label, value}` pairs shown on the card and in the page header, `media_style` is `photo` or `device` (`device` shows screenshots in phone frames, uncropped), `sort_order` sets the order and `published` hides or shows a project.
- **`project_media`**: photos. Rows with `kind = image` appear in the story; rows with `kind = extra` appear in the "More photos" gallery.
- Upload new photos to the `portfolio` bucket and paste their public URLs.

Changes appear on the site within `CACHE_SECONDS` (60 s by default).

To keep the repo as the source instead, edit the READMEs, then run `npm run content && npm run build && npm run seed`.

## Contact form

Messages are saved to the `contact_messages` table (Supabase → Table Editor). The form needs `SUPABASE_SERVICE_ROLE_KEY` on the server. It has a honeypot field and a limit of 5 messages per IP per hour.

## Layout

| Path | What it is |
|---|---|
| `web/server.js` | Express app: pages, `/api/projects`, `/api/contact`, `/api/health` |
| `web/views.js` | HTML templates (server-rendered, with Open Graph tags for link previews) |
| `web/lib/data.js` | Supabase reads and writes, with a cache and a local fallback |
| `web/public/` | CSS, the small client script (filters, lightbox, form) and the favicon |
| `content/` | `projects.json` (generated) and `site.json` (hero, title block, process, principles) |
| `scripts/` | `build-content`, `build-media`, `seed-supabase` |
| `supabase/migrations/` | Database schema |

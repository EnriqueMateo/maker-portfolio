-- Maker portfolio schema. Run in the Supabase SQL editor (or `supabase db push`).

create extension if not exists pgcrypto;

create table if not exists public.projects (
  id              uuid primary key default gen_random_uuid(),
  slug            text not null unique,
  emoji           text,
  title           text not null,
  short_title     text,
  tagline         text,
  summary         text,
  domains         text[] not null default '{}',
  body_md         text,
  cover_url       text,
  cover_thumb_url text,
  links           jsonb not null default '[]'::jsonb,
  sort_order      int not null default 0,
  published       boolean not null default true,
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now()
);

create table if not exists public.project_media (
  id          uuid primary key default gen_random_uuid(),
  project_id  uuid not null references public.projects(id) on delete cascade,
  url         text not null,
  thumb_url   text,
  caption     text,
  -- 'image' = shown inside the story, 'extra' = only in the "More photos" gallery
  kind        text not null default 'image' check (kind in ('image', 'extra')),
  sort_order  int not null default 0,
  created_at  timestamptz not null default now()
);
create index if not exists project_media_project_idx on public.project_media (project_id, sort_order);

create table if not exists public.contact_messages (
  id          uuid primary key default gen_random_uuid(),
  name        text not null,
  email       text not null,
  message     text not null,
  created_at  timestamptz not null default now()
);

create or replace function public.touch_updated_at() returns trigger
language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end $$;

drop trigger if exists projects_touch on public.projects;
create trigger projects_touch before update on public.projects
  for each row execute function public.touch_updated_at();

-- Row level security: the public (anon key) can only read published projects.
-- Writes and contact messages go through the server with the service-role key.
alter table public.projects         enable row level security;
alter table public.project_media    enable row level security;
alter table public.contact_messages enable row level security;

drop policy if exists "public read published projects" on public.projects;
create policy "public read published projects" on public.projects
  for select using (published);

drop policy if exists "public read media of published projects" on public.project_media;
create policy "public read media of published projects" on public.project_media
  for select using (
    exists (select 1 from public.projects p where p.id = project_id and p.published)
  );

-- Public storage bucket for the optimized photos.
insert into storage.buckets (id, name, public)
values ('portfolio', 'portfolio', true)
on conflict (id) do nothing;

-- Key facts for project cards/headers, presentation style, and image sizes.
alter table public.projects
  add column if not exists facts jsonb not null default '[]'::jsonb,
  add column if not exists media_style text not null default 'photo';

alter table public.projects drop constraint if exists projects_media_style_check;
alter table public.projects add constraint projects_media_style_check check (media_style in ('photo', 'device'));

alter table public.project_media
  add column if not exists width int,
  add column if not exists height int;

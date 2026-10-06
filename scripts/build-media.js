#!/usr/bin/env node
// Converts the full-resolution photos in each project folder into web-sized
// WebP files under .cache/media/<slug>/ (1600px + 640px thumbnails).
// Runs as `npm run build` on Railway; existing outputs are skipped.

const fs = require('fs');
const path = require('path');
const sharp = require('sharp');
const { IMAGE_EXT, mediaName } = require('./lib/media-names');

const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, '.cache', 'media');
const projects = require(path.join(ROOT, 'content', 'projects.json'));

const SIZES = [
  { variant: null, width: 1600, quality: 80 },
  { variant: 'sm', width: 640, quality: 72 },
];

async function main() {
  if (process.env.SKIP_MEDIA_BUILD === '1') {
    console.log('SKIP_MEDIA_BUILD=1 — skipping image optimisation');
    return;
  }
  let made = 0;
  for (const { slug } of projects) {
    const src = path.join(ROOT, slug);
    const dst = path.join(OUT, slug);
    fs.mkdirSync(dst, { recursive: true });
    for (const file of fs.readdirSync(src).filter((f) => IMAGE_EXT.test(f))) {
      for (const s of SIZES) {
        const out = path.join(dst, mediaName(file, s.variant));
        if (fs.existsSync(out)) continue;
        await sharp(path.join(src, file))
          .rotate() // honour EXIF orientation from phone photos
          .resize({ width: s.width, withoutEnlargement: true })
          .webp({ quality: s.quality })
          .toFile(out);
        made++;
      }
    }
  }
  console.log(`Media ready in ${path.relative(ROOT, OUT)} (${made} new files)`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});

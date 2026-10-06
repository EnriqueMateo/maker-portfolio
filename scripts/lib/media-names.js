// Shared naming convention for optimized media: "My Photo.JPEG" → "my-photo.webp"
// (and "my-photo-sm.webp" for the thumbnail variant).

const IMAGE_EXT = /\.(jpe?g|png|webp)$/i;

function mediaBase(file) {
  return file
    .replace(/\.[^.]+$/, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
}

function mediaName(file, variant) {
  return `${mediaBase(file)}${variant ? `-${variant}` : ''}.webp`;
}

module.exports = { IMAGE_EXT, mediaBase, mediaName };

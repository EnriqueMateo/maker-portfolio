// Shared naming convention for optimized media: "My Photo.JPEG" → "my-photo.webp"
// (and "my-photo-sm.webp" for the thumbnail variant).

const IMAGE_EXT = /\.(jpe?g|png|webp)$/i;

// Photos stored sideways without an EXIF orientation flag: extra clockwise
// rotation in degrees, keyed by "<project folder>/<file>".
const ROTATE = {
  '3d-printer/1000012381.JPEG': 270,
};

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

module.exports = { IMAGE_EXT, ROTATE, mediaBase, mediaName };

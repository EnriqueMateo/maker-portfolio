# Contorno oscuro tipo pegatina alrededor de un recorte: python outline.py in.webp out.webp [grosor]
import sys, cv2, numpy as np
src, out = sys.argv[1], sys.argv[2]; t = int(sys.argv[3]) if len(sys.argv) > 3 else 9
im = cv2.imread(src, cv2.IMREAD_UNCHANGED); pad = t + 4
im = cv2.copyMakeBorder(im, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(0, 0, 0, 0))
a = im[:, :, 3].astype(np.float32) / 255
k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * t + 1, 2 * t + 1))
ring = cv2.GaussianBlur(cv2.dilate((a > .5).astype(np.uint8), k).astype(np.float32), (5, 5), 0)
ink = np.array([40, 18, 22], np.float32)  # azul-marrón muy oscuro (BGR)
out_rgb = im[:, :, :3].astype(np.float32) * a[:, :, None] + ink * (1 - a[:, :, None])
out_a = np.maximum(a, ring)
res = np.dstack([np.clip(out_rgb / np.maximum(out_a[:, :, None], 1e-4), 0, 255).astype(np.uint8), (out_a * 255).astype(np.uint8)])
cv2.imwrite(out, res, [cv2.IMWRITE_WEBP_QUALITY, 92]); print(out, res.shape)

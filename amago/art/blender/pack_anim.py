# Empaqueta los fotogramas de anim_sprites.py en tiras webp (una por vista y animación) con contorno oscuro.
# Uso: python pack_anim.py <dir_fotogramas> <heroe> <dir_salida>   → imprime la entrada de ANIM3D para index.html
import sys, os, glob, json, cv2, numpy as np
src, hero, out = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out, exist_ok=True)
frames = {}
for f in sorted(glob.glob(os.path.join(src, '*.png'))):
    vw, an, i = os.path.basename(f)[:-4].split('_')
    frames.setdefault((vw, an), []).append(cv2.imread(f, cv2.IMREAD_UNCHANGED))
# una sola caja para todo el héroe: misma escala y mismos pies en todas las animaciones
ys, xs = [], []
for fl in frames.values():
    for im in fl:
        yy, xx = np.nonzero(im[:, :, 3] > 10)
        if len(yy): ys += [yy.min(), yy.max()]; xs += [xx.min(), xx.max()]
S = next(iter(frames.values()))[0].shape[0]; T = max(3, round(3 * S / 256))  # contorno proporcional a la resolución
y0, y1, x0, x1 = max(0, min(ys) - T - 1), min(S - 1, max(ys) + T + 1), max(0, min(xs) - T - 1), min(S - 1, max(xs) + T + 1)
fh, fw = y1 - y0 + 1, x1 - x0 + 1
def outline(im):
    a = im[:, :, 3].astype(np.float32) / 255
    ring = cv2.GaussianBlur(cv2.dilate((a > .4).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * T + 1, 2 * T + 1))).astype(np.float32), (2 * (T // 3) + 1, 2 * (T // 3) + 1), 0)
    ink = np.array([34, 14, 16], np.float32)
    rgb = im[:, :, :3].astype(np.float32) * a[:, :, None] + ink * (1 - a[:, :, None]); oa = np.maximum(a, ring)
    return np.dstack([np.clip(rgb / np.maximum(oa[:, :, None], 1e-4), 0, 255).astype(np.uint8), (oa * 255).astype(np.uint8)])
n = {}
for (vw, an), fl in frames.items():
    strip = np.concatenate([outline(im[y0:y1 + 1, x0:x1 + 1]) for im in fl], axis=1)
    cv2.imwrite(os.path.join(out, f'{hero}_{vw}_{an}.webp'), strip, [cv2.IMWRITE_WEBP_QUALITY, int(os.environ.get('Q', 88))]); n[an] = len(fl)
idle = frames[('f', 'idle')][0][y0:y1 + 1, x0:x1 + 1, 3]; yy, _ = np.nonzero(idle > 10)
ih = (yy.max() - yy.min() + 1) / fh; foot = (fh - 1 - yy.max()) / fh
print(json.dumps({hero: {"fw": int(fw), "fh": int(fh), "ih": round(float(ih), 3), "foot": round(float(foot), 3), "n": n}}))

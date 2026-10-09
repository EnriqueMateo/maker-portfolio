# Pasa los renders de icons.py a webp para la interfaz: recorta, añade contorno oscuro y reduce.
# python ui_icons.py <dir_renders> <dir_salida>
import sys, os, glob, cv2, numpy as np
src, out = sys.argv[1], sys.argv[2]
SIZE = {'chest': 320}
for f in sorted(glob.glob(os.path.join(src, '*.png'))):
    name = os.path.splitext(os.path.basename(f))[0]
    if name.startswith('sheet'): continue
    im = cv2.imread(f, cv2.IMREAD_UNCHANGED)
    a = im[:, :, 3]; ys, xs = np.nonzero(a > 8)
    im = im[max(0, ys.min() - 2):ys.max() + 3, max(0, xs.min() - 2):xs.max() + 3]
    target = SIZE['chest'] if name.startswith('chest') else 160
    k = target / max(im.shape[:2]); im = cv2.resize(im, (int(im.shape[1] * k), int(im.shape[0] * k)), interpolation=cv2.INTER_AREA)
    t = max(3, target // 40); pad = t + 3
    im = cv2.copyMakeBorder(im, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(0, 0, 0, 0))
    al = im[:, :, 3].astype(np.float32) / 255
    ring = cv2.GaussianBlur(cv2.dilate((al > .4).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * t + 1, 2 * t + 1))).astype(np.float32), (3, 3), 0)
    ink = np.array([31, 10, 11], np.float32)  # tinta azul muy oscura (BGR)
    rgb = im[:, :, :3].astype(np.float32) * al[:, :, None] + ink * (1 - al[:, :, None])
    oa = np.maximum(al, ring)
    res = np.dstack([np.clip(rgb / np.maximum(oa[:, :, None], 1e-4), 0, 255).astype(np.uint8), (oa * 255).astype(np.uint8)])
    cv2.imwrite(os.path.join(out, name + '.webp'), res, [cv2.IMWRITE_WEBP_QUALITY, 90]); print(name, res.shape)

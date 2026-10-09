# Recorta un personaje sobre fondo blanco liso: python cutout.py in.jpg out.webp [alto]
import sys, cv2, numpy as np
src, out = sys.argv[1], sys.argv[2]; H = int(sys.argv[3]) if len(sys.argv) > 3 else 640
im = cv2.imread(src, cv2.IMREAD_UNCHANGED)
if im.shape[2] == 4:  # ya trae transparencia
    a = im[:, :, 3]; bgr = im[:, :, :3]
else:
    bgr = im; h, w = bgr.shape[:2]
    # fondo = lo conectado con el borde y casi blanco/gris claro y poco saturado
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    light = ((hsv[:, :, 2] > 215) & (hsv[:, :, 1] < 28)).astype(np.uint8)
    n, lab = cv2.connectedComponents(light)
    border = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])) - {0}
    bg = np.isin(lab, list(border)).astype(np.uint8)
    # quitar sombras suaves del suelo: gris muy claro bajo el personaje también es fondo
    bg = cv2.morphologyEx(bg, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    fg = 1 - bg
    # quedarse con la pieza principal (y las que estén cerca)
    n2, lab2, st, _ = cv2.connectedComponentsWithStats(fg)
    keep = [i for i in range(1, n2) if st[i, cv2.CC_STAT_AREA] > 0.002 * h * w]
    fg = np.isin(lab2, keep).astype(np.uint8)
    a = cv2.GaussianBlur((fg * 255).astype(np.uint8), (3, 3), 0)
    # descontaminar el borde blanco
    al = a.astype(np.float32)[:, :, None] / 255
    bgr = np.clip((bgr.astype(np.float32) - (1 - al) * 248) / np.maximum(al, .05), 0, 255).astype(np.uint8)
ys, xs = np.nonzero(a > 10); y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
rgba = np.dstack([bgr, a])[max(0, y0 - 4):y1 + 5, max(0, x0 - 4):x1 + 5]
k = H / rgba.shape[0]; rgba = cv2.resize(rgba, (int(rgba.shape[1] * k), H), interpolation=cv2.INTER_AREA)
cv2.imwrite(out, rgba, [cv2.IMWRITE_WEBP_QUALITY, 92]); print(out, rgba.shape)

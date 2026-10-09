# Recorte con IA (rembg, isnet-general-use): python cutout_ai.py in out.webp [alto]
import sys, numpy as np, cv2
from rembg import remove, new_session
from PIL import Image
src, out = sys.argv[1], sys.argv[2]; H = int(sys.argv[3]) if len(sys.argv) > 3 else 640
im = Image.open(src).convert('RGB')
cut = remove(im, session=new_session('isnet-general-use'))
a = np.array(cut); a[:, :, :3] = np.array(im)  # color original, solo usamos la máscara de la IA
al = a[:, :, 3]
# quitar motas sueltas: quedarse con piezas grandes
n, lab, st, _ = cv2.connectedComponentsWithStats((al > 40).astype(np.uint8))
keep = [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > 0.0015 * al.size]
mask = np.isin(lab, keep)
# rellenar huecos interiores y hacer opaco el interior (sin transparencias raras en zonas oscuras o blancas)
solid = mask.astype(np.uint8); ff = solid.copy(); h_, w_ = ff.shape; m2 = np.zeros((h_ + 2, w_ + 2), np.uint8); cv2.floodFill(ff, m2, (0, 0), 1)
solid = solid | (1 - ff)
inner = cv2.erode(solid, np.ones((7, 7), np.uint8)).astype(bool); al[inner] = 255; al[~cv2.dilate(solid, np.ones((5, 5), np.uint8)).astype(bool)] = 0; a[:, :, 3] = al
ys, xs = np.nonzero(al > 10); a = a[max(0, ys.min() - 4):ys.max() + 5, max(0, xs.min() - 4):xs.max() + 5]
img = Image.fromarray(a); k = H / img.height; img = img.resize((int(img.width * k), H), Image.LANCZOS)
img.save(out, quality=92, method=6); print(out, img.size)

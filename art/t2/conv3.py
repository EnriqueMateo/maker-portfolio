# Convierte un modelo TRELLIS (art/t2/<id>.glb) al formato del juego SIN rehacer la textura:
# conserva la malla, las UV y la textura originales (2048 px) y solo lleva el modelo a las coordenadas de la carta 2D.
# conv2.py repintaba la textura muestreando puntos y la filtraba: caras, guantes y detalles salían borrosos.
import sys, os, numpy as np, trimesh
from PIL import Image
i = sys.argv[1]; G = sys.argv[2]; D = os.path.dirname(os.path.abspath(__file__))
src = trimesh.load(f'{D}/{i}.glb', force='mesh', process=False)
tex = src.visual.material.baseColorTexture.convert('RGB')
V = np.asarray(src.vertices, np.float64); F = np.asarray(src.faces); UV = np.asarray(src.visual.uv, np.float64)
MAXF = int(os.environ.get('MAXF', '45000'))
if len(F) > MAXF:
    # reducción que respeta las UV (la textura original sigue valiendo)
    import pymeshlab, tempfile
    td = tempfile.mkdtemp(); ob = f'{td}/m.obj'
    m0 = trimesh.Trimesh(V, F, process=False); m0.visual = trimesh.visual.TextureVisuals(uv=UV, image=tex); m0.export(ob)
    ms = pymeshlab.MeshSet(); ms.load_new_mesh(ob)
    ms.meshing_decimation_quadric_edge_collapse_with_texture(targetfacenum=MAXF, preserveboundary=True, preservenormal=True, qualitythr=.5)
    ms.save_current_mesh(f'{td}/d.obj')
    d = trimesh.load(f'{td}/d.obj', force='mesh', process=False)
    V = np.asarray(d.vertices, np.float64); F = np.asarray(d.faces); UV = np.asarray(d.visual.uv, np.float64)
    print('reducido a', len(F), flush=True)
# modelos que el generador deja mirando hacia otro lado: se giran (eje Y) antes de todo para que el frente sea +Z
ROTS = {'bum': np.pi, 'flecha': -np.pi / 2, 'rey': np.pi, 'brasa': np.pi, 'arana': -np.pi * .75}
r = float(os.environ.get('ROT', ROTS.get(i, 0)))
if r:
    c_, s_ = np.cos(r), np.sin(r); V = np.stack([V[:, 0] * c_ + V[:, 2] * s_, V[:, 1], -V[:, 0] * s_ + V[:, 2] * c_], 1)
# normales suaves que no se cortan en las costuras de UV: se promedian por posición
key = np.round(V / 1e-5).astype(np.int64)
_, inv = np.unique(key, axis=0, return_inverse=True); inv = inv.reshape(-1)
fn = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]])
acc = np.zeros((inv.max() + 1, 3))
for k in range(3): np.add.at(acc, inv[F[:, k]], fn)
N = acc[inv]; N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-12
# misma caja que la ilustración (alto de la imagen = 1)
if i.startswith('sk_'): spath = f'{D}/../../amago/skins/{i[3:]}.webp'
elif i.startswith('pr_'): spath = f'{D}/../../amago/props/{i[3:]}.webp'
elif os.environ.get('REF'): spath = os.environ['REF']
else: spath = f'{D}/../../amago/sprites/{i}.webp'
sp = Image.open(spath).convert('RGBA'); bx = sp.getbbox(); Ws, Hs = sp.size
b0, b1 = V.min(0), V.max(0)
sx = (bx[2] - bx[0]) / (b1[0] - b0[0]); sy = (bx[3] - bx[1]) / (b1[1] - b0[1])
if os.environ.get('UNI') == '1' or not .8 < sx / sy < 1.25: sx = sy
px = (bx[0] + bx[2]) / 2 + (V[:, 0] - (b0[0] + b1[0]) / 2) * sx; py = bx[3] - (V[:, 1] - b0[1]) * sy
C = np.stack([(px / Ws - .5) * Ws / Hs, 1 - py / Hs, (V[:, 2] - np.median(V[:, 2])) * (sx + sy) / 2 / Hs], 1)
# PROYECCIÓN: la parte delantera del modelo se pinta con la propia ilustración (cara, ojos y detalles nítidos como en el dibujo).
# El modelo está colocado exactamente sobre la ilustración, así que cada punto visible de frente tiene su píxel en el dibujo.
# revisado a ojo: en estos el modelo no coincide con el dibujo (pose distinta) y la proyección deja caras dobles
PROJ_OFF = {'brasa', 'mira', 'mina', 'salto', 'savia', 'rey', 'topo', 'arana', 'ojo', 'truco', 'muro', 'coloso'}
if os.environ.get('PROJ', '0' if (i.startswith('pr_') or i.startswith('sk_') or i in PROJ_OFF) else '1') == '1':
    import cv2
    spa = np.asarray(sp, np.float32); sal = spa[..., 3]
    inner = cv2.erode((sal > 250).astype(np.uint8), np.ones((9, 9), np.uint8)) > 0   # sin el contorno negro del borde
    Z = V[:, 2]; zr = (b1 - b0).max()
    # z-buffer en el plano del dibujo (lo más cercano a la cámara frontal)
    zb = np.full((Hs, Ws), -1e9, np.float32); Mimg = np.zeros((Hs, Ws, 3), np.float32); Mm = np.zeros((Hs, Ws), bool)
    P2 = np.stack([px, py], 1); T0 = np.asarray(tex, np.float32); TH0, TW0 = T0.shape[:2]
    Uv = np.stack([UV[:, 0] * (TW0 - 1), (1 - UV[:, 1]) * (TH0 - 1)], 1)
    for f in F[np.argsort(Z[F].mean(1))]:
        t = P2[f]; mn = np.floor(t.min(0)).astype(int); mx = np.ceil(t.max(0)).astype(int)
        mn = np.clip(mn, 0, [Ws - 1, Hs - 1]); mx = np.clip(mx, 0, [Ws - 1, Hs - 1])
        if (mx - mn).min() < 0: continue
        gx, gy = np.meshgrid(np.arange(mn[0], mx[0] + 1) + .5, np.arange(mn[1], mx[1] + 1) + .5)
        d = (t[1, 1] - t[2, 1]) * (t[0, 0] - t[2, 0]) + (t[2, 0] - t[1, 0]) * (t[0, 1] - t[2, 1])
        if abs(d) < 1e-9: continue
        w0 = ((t[1, 1] - t[2, 1]) * (gx - t[2, 0]) + (t[2, 0] - t[1, 0]) * (gy - t[2, 1])) / d
        w1 = ((t[2, 1] - t[0, 1]) * (gx - t[2, 0]) + (t[0, 0] - t[2, 0]) * (gy - t[2, 1])) / d; w2 = 1 - w0 - w1
        ok = (w0 >= -.01) & (w1 >= -.01) & (w2 >= -.01)
        if not ok.any(): continue
        z = w0 * Z[f[0]] + w1 * Z[f[1]] + w2 * Z[f[2]]
        iy = (gy[ok] - .5).astype(int); ix = (gx[ok] - .5).astype(int); zz = z[ok]
        uu = w0[ok] * Uv[f[0], 0] + w1[ok] * Uv[f[1], 0] + w2[ok] * Uv[f[2], 0]; vv = w0[ok] * Uv[f[0], 1] + w1[ok] * Uv[f[1], 1] + w2[ok] * Uv[f[2], 1]
        zb[iy, ix] = zz; Mimg[iy, ix] = T0[np.clip(vv.astype(int), 0, TH0 - 1), np.clip(uu.astype(int), 0, TW0 - 1)]; Mm[iy, ix] = True
    # alinear el dibujo con el modelo (desplazamiento, escala y giro) y decidir si la proyección encaja
    g1 = cv2.cvtColor(Mimg.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32); g2 = cv2.cvtColor(spa[..., :3].astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    g1 = cv2.GaussianBlur(g1, (0, 0), 2); g2 = cv2.GaussianBlur(g2, (0, 0), 2)
    msk = (Mm & inner).astype(np.uint8)
    def ncc(W):
        w2 = cv2.warpAffine(g2, W, (Ws, Hs), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP); m = msk > 0
        a_, b_ = g1[m] - g1[m].mean(), w2[m] - w2[m].mean(); return float((a_ * b_).sum() / (np.sqrt((a_ * a_).sum() * (b_ * b_).sum()) + 1e-6))
    I0 = np.eye(2, 3, dtype=np.float32); cc0 = ncc(I0); Wp = I0; cc = cc0
    try:
        _, W1 = cv2.findTransformECC(g1, g2, I0.copy(), cv2.MOTION_AFFINE, (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-5), msk, 5)
        cc1 = ncc(W1)
        if os.environ.get('ALIGN') == '1' and cc1 > cc0 + .04 and abs(W1[:, 2]).max() < 40: Wp, cc = W1, cc1
    except cv2.error: pass
    print('encaje', round(cc0, 3), '->', round(cc, 3), 'desplazamiento', Wp[:, 2].round(1), flush=True)
    if cc < float(os.environ.get('CCMIN', '-1')): print('no encaja: sin proyección', flush=True); inner[:] = False
    # recorrer la textura: posición, normal y profundidad de cada texel
    T = np.asarray(tex, np.float32); TH, TW = T.shape[:2]
    U = np.stack([UV[:, 0] * TW, (1 - UV[:, 1]) * TH], 1)
    out = T.copy(); hits = 0
    for f in F:
        nz = (N[f, 2]).mean()
        if nz < .2: continue
        t = U[f]; mn = np.clip(np.floor(t.min(0)).astype(int), 0, [TW - 1, TH - 1]); mx = np.clip(np.ceil(t.max(0)).astype(int), 0, [TW - 1, TH - 1])
        gx, gy = np.meshgrid(np.arange(mn[0], mx[0] + 1) + .5, np.arange(mn[1], mx[1] + 1) + .5)
        d = (t[1, 1] - t[2, 1]) * (t[0, 0] - t[2, 0]) + (t[2, 0] - t[1, 0]) * (t[0, 1] - t[2, 1])
        if abs(d) < 1e-12: continue
        w0 = ((t[1, 1] - t[2, 1]) * (gx - t[2, 0]) + (t[2, 0] - t[1, 0]) * (gy - t[2, 1])) / d
        w1 = ((t[2, 1] - t[0, 1]) * (gx - t[2, 0]) + (t[0, 0] - t[2, 0]) * (gy - t[2, 1])) / d; w2 = 1 - w0 - w1
        ok = (w0 >= -.02) & (w1 >= -.02) & (w2 >= -.02)
        if not ok.any(): continue
        w0, w1, w2 = w0[ok], w1[ok], w2[ok]
        X = w0 * px[f[0]] + w1 * px[f[1]] + w2 * px[f[2]]; Y = w0 * py[f[0]] + w1 * py[f[1]] + w2 * py[f[2]]; Zt = w0 * Z[f[0]] + w1 * Z[f[1]] + w2 * Z[f[2]]
        xi = np.clip(X.astype(int), 0, Ws - 1); yi = np.clip(Y.astype(int), 0, Hs - 1)
        Xs = Wp[0, 0] * X + Wp[0, 1] * Y + Wp[0, 2]; Ys = Wp[1, 0] * X + Wp[1, 1] * Y + Wp[1, 2]
        xs = np.clip(Xs.astype(int), 0, Ws - 1); ys = np.clip(Ys.astype(int), 0, Hs - 1)
        vis = (Zt >= zb[yi, xi] - zr * .012) & inner[ys, xs] & (sal[ys, xs] > 250)
        if not vis.any(): continue
        wt = np.clip((nz - .2) / .35, 0, 1)
        ty = (gy[ok] - .5).astype(int)[vis]; tx = (gx[ok] - .5).astype(int)[vis]
        out[ty, tx] = out[ty, tx] * (1 - wt) + spa[ys[vis], xs[vis], :3] * wt; hits += vis.sum()
    tex = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)); print('proyectados', hits, flush=True)
g = trimesh.Trimesh(vertices=C, faces=F, vertex_normals=N, process=False); g.visual = trimesh.visual.TextureVisuals(uv=UV)
os.makedirs(G, exist_ok=True); g.export(f'{G}/{i}.glb'); tex.save(f'{G}/{i}.webp', quality=92, method=6)
print('ok', i, len(F), len(C), 'ratio xy', round(sx / sy, 3), C.min(0).round(2), C.max(0).round(2))

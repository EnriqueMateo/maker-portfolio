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
g = trimesh.Trimesh(vertices=C, faces=F, vertex_normals=N, process=False); g.visual = trimesh.visual.TextureVisuals(uv=UV)
os.makedirs(G, exist_ok=True); g.export(f'{G}/{i}.glb'); tex.save(f'{G}/{i}.webp', quality=92, method=6)
print('ok', i, len(F), len(C), 'ratio xy', round(sx / sy, 3), C.min(0).round(2), C.max(0).round(2))

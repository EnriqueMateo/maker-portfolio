# Repinta manchas (y opcionalmente quita astillas: ... xcut zcut) oscuras de la textura en una zona (p. ej. zapatilla): python tex_fix.py -- in.glb out.glb xmin xmax zmax valmax
import sys, os, bpy, numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import reset
a = sys.argv[sys.argv.index('--') + 1:]
src, out, x0, x1, zmax, vmax = a[0], a[1], float(a[2]), float(a[3]), float(a[4]), float(a[5])
reset(); bpy.ops.import_scene.gltf(filepath=src)
o = [o for o in bpy.data.objects if o.type == 'MESH'][0]; me = o.data
V = np.array([tuple(o.matrix_world @ v.co) for v in me.vertices]); mn, mx = V.min(0), V.max(0); k = 2 / (mx[2] - mn[2])
x = (V[:, 0] - (mn[0] + mx[0]) / 2) * k; z = (V[:, 2] - mn[2]) * k
img = [i for i in bpy.data.images if i.size[0] > 0][0]; W, H = img.size
px = np.array(img.pixels[:], dtype=np.float32).reshape(H, W, 4)
lay = me.uv_layers.active.data; mask = np.zeros((H, W), np.uint8)
for poly in me.polygons:
    vs = list(poly.vertices)
    if not all(x0 < x[v] < x1 and z[v] < zmax for v in vs): continue
    uv = np.array([tuple(lay[li].uv) for li in poly.loop_indices]); pts = np.stack([uv[:, 0] * W, uv[:, 1] * H], 1).astype(np.int32)
    tri = np.zeros((H, W), np.uint8); cv2.fillPoly(tri, [pts], 255)
    mask |= tri
dark = (px[:, :, :3].max(2) < vmax).astype(np.uint8) * 255
m = cv2.dilate(mask & dark, np.ones((5, 5), np.uint8))
print('px repintados', int((m > 0).sum()))
rgb = (np.clip(px[:, :, :3], 0, 1) ** (1 / 2.2) * 255).astype(np.uint8)
fix = cv2.inpaint(rgb, m, 7, cv2.INPAINT_TELEA).astype(np.float32) / 255
px[:, :, :3] = np.where(m[:, :, None] > 0, fix ** 2.2, px[:, :, :3])
img.pixels[:] = px.ravel(); img.update(); img.pack()
# opcional: borrar astillas sueltas más allá de un límite (xcut zcut)
if len(a) > 7:
    import bmesh
    xc, zc = float(a[6]), float(a[7]); bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
    kill = [bm.verts[i] for i in range(len(bm.verts)) if x[i] < xc and z[i] < zc]
    bmesh.ops.delete(bm, geom=kill, context='VERTS'); bm.to_mesh(me); bm.free(); print('astillas', len(kill))
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_image_format='JPEG', export_jpeg_quality=90)

# Esqueleto automático para un héroe de AMAGO (figura de una pieza hecha por IA).
# Uso: python rig.py -- in.glb out.glb juntas.json [pose.png]
# juntas.json da las alturas y anchuras clave en unidades normalizadas (altura total = 2, pies en z = 0, frente hacia -Y):
#   {"hip": .52, "chest": 1.0, "neck": 1.1, "top": 1.9, "leg_x": .09, "knee": .26,
#    "shoulder": [.2, .95], "elbow": [.31, .78], "hand": [.38, .58], "arm_gate": .24, "head_rigid": 1.12}
# Los pesos se calculan por distancia a cada hueso, con reglas por zonas para que la cabeza sea rígida
# y lo que está fuera del tronco (manos, arco, armas) siga al brazo de su lado.
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import reset, apply_mods
import bpy
import numpy as np
from mathutils import Vector

a = sys.argv[sys.argv.index('--') + 1:]
SRC, OUT, J = a[0], a[1], json.load(open(a[2]))
POSE = a[3] if len(a) > 3 else None

reset()
bpy.ops.import_scene.gltf(filepath=SRC)
mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]
for o in bpy.context.selected_objects: o.select_set(False)
mesh.select_set(True); bpy.context.view_layer.objects.active = mesh
bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
# normalizar: altura 2, pies en 0, centrado
V = np.array([tuple(v.co) for v in mesh.data.vertices])
mn, mx = V.min(0), V.max(0); k = 2.0 / (mx[2] - mn[2])
c = Vector(((mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2, mn[2]))
for v in mesh.data.vertices: v.co = (v.co - c) * k
mesh.data.update()
V = np.array([tuple(v.co) for v in mesh.data.vertices])
# objetos sujetos (arco, bastón...): se detectan por el color de la textura y la zona, y van 100% con el antebrazo
import colorsys
def tex_hsv():
    me = mesh.data; img = [i for i in bpy.data.images if i.size[0] > 0][0]
    Wd, Ht = img.size; px = np.array(img.pixels[:]).reshape(Ht, Wd, 4)[:, :, :3]
    uv = np.zeros((len(me.vertices), 2)); lay = me.uv_layers.active.data
    for l in me.loops: uv[l.vertex_index] = lay[l.index].uv
    col = px[np.clip((uv[:, 1] * Ht).astype(int), 0, Ht - 1), np.clip((uv[:, 0] * Wd).astype(int), 0, Wd - 1)]
    col = np.where(col <= .0031308, col * 12.92, 1.055 * np.clip(col, 0, None) ** (1 / 2.4) - .055)
    return np.array([colorsys.rgb_to_hsv(*c) for c in col])
def find_prop(pr, HSV):
    if True:
        sgn = 1 if pr['side'] == 'L' else -1
        h = HSV[:, 0] * 360
        m = (h >= pr['hue'][0]) & (h <= pr['hue'][1]) & (HSV[:, 1] >= pr['sat'][0]) & (HSV[:, 1] <= pr['sat'][1]) \
            & (HSV[:, 2] >= pr['val'][0]) & (HSV[:, 2] <= pr['val'][1]) & (sgn * x > pr['xmin']) & (z < pr.get('zmax', 9))
        notHead = ~((z > J['head_rigid'] - .05) & (np.abs(x) < pr.get('head_w', .52)))  # el pelo naranja se parece al arco
        m &= notHead
        # agrupar por cercanía (la malla viene cortada por las costuras de la textura) y quedarse con el grupo mayor
        cell = .035; P_ = np.nonzero(m)[0]; keys = {}
        for vi in P_: keys.setdefault(tuple((V[vi] / cell).astype(int)), []).append(vi)
        seen = set(); best = []
        for k0 in keys:
            if k0 in seen: continue
            comp = []; st = [k0]; seen.add(k0)
            while st:
                kk = st.pop(); comp += keys[kk]
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        for dz in (-1, 0, 1):
                            nk = (kk[0] + dx, kk[1] + dy, kk[2] + dz)
                            if nk in keys and nk not in seen: seen.add(nk); st.append(nk)
            if len(comp) > len(best): best = comp
        pm = np.zeros(len(V), bool); pm[best] = True
        # engordar: vértices a menos de 3 cm del grupo y en su lado (bordes con otro color, costuras)
        C_ = V[pm]; grid = {}
        for vi in np.nonzero(pm)[0]: grid.setdefault(tuple((V[vi] / .03).astype(int)), []).append(vi)
        cand = np.nonzero((sgn * x > pr['xmin'] - .05) & ~pm & notHead)[0]
        for vi in cand:
            kk = tuple((V[vi] / .03).astype(int))
            if any((kk[0] + dx, kk[1] + dy, kk[2] + dz) in grid for dx in (-1, 0, 1) for dy in (-1, 0, 1) for dz in (-1, 0, 1)): pm[vi] = True
        print('prop', pr['side'], int(pm.sum()), 'verts, z', round(float(z[pm].min()), 2), round(float(z[pm].max()), 2))
        return pm

x, z = V[:, 0], V[:, 2]
NEWPROPS = []  # objetos modelados aparte que sustituyen al original
if J.get('props'):
    HSV = tex_hsv()
    for pr in J['props']:
        if not pr.get('replace'): continue
        pm = find_prop(pr, HSV)
        for bx in pr.get('boxes', []):  # zonas donde el objeto toca la cara o el cuerpo: lo de su color también fuera
            (x0, x1), (y0, y1), (z0, z1) = bx
            h = HSV[:, 0] * 360
            pm |= (x > x0) & (x < x1) & (V[:, 1] > y0) & (V[:, 1] < y1) & (z > z0) & (z < z1) & (h > pr['hue'][0]) & (h < pr['hue'][1]) & (HSV[:, 1] < pr.get('box_sat', .62)) & (HSV[:, 2] > pr['val'][0])
        grip = V[pm & (np.abs(z - J['hand'][1]) < .12)].mean(0) if (pm & (np.abs(z - J['hand'][1]) < .12)).any() else V[pm].mean(0)
        span = (float(z[pm].min()), float(z[pm].max()))
        print('replace prop', pr['side'], int(pm.sum()), 'verts, grip', grip.round(2), 'span', [round(v, 2) for v in span])
        import bmesh
        bm = bmesh.new(); bm.from_mesh(mesh.data); bm.verts.ensure_lookup_table()
        bmesh.ops.delete(bm, geom=[bm.verts[i] for i in np.nonzero(pm)[0]], context='VERTS')
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
        bnd = [e for e in bm.edges if e.is_boundary]
        bmesh.ops.holes_fill(bm, edges=bnd, sides=60)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        # quitar restos sueltos del objeto original
        bm.verts.ensure_lookup_table(); seen = set(); small = []
        for v0 in bm.verts:
            if v0.index in seen: continue
            comp = []; st = [v0]; seen.add(v0.index)
            while st:
                a_ = st.pop(); comp.append(a_)
                for e in a_.link_edges:
                    b_ = e.other_vert(a_)
                    if b_.index not in seen: seen.add(b_.index); st.append(b_)
            if len(comp) < 300: small += comp
        if small: bmesh.ops.delete(bm, geom=small, context='VERTS')
        print('restos quitados', len(small))
        bm.to_mesh(mesh.data); bm.free(); mesh.data.update()
        Vn = np.array([tuple(v.co) for v in mesh.data.vertices]); sg = 1 if pr['side'] == 'L' else -1
        hp = np.array([sg * J['hand'][0], 0, J['hand'][1]]); near = Vn[(np.linalg.norm(Vn - hp, axis=1) < .2) & (sg * Vn[:, 0] > J['arm_gate'])]
        if len(near): grip = np.array([near[:, 0].mean(), near[:, 1].mean(), near[:, 2].mean()])
        print('agarre', grip.round(2))
        NEWPROPS.append((pr, grip, span))
    V = np.array([tuple(v.co) for v in mesh.data.vertices]); x, z = V[:, 0], V[:, 2]

# ---------- huesos ----------
arm = bpy.data.armatures.new('rig'); rig = bpy.data.objects.new('rig', arm)
bpy.context.scene.collection.objects.link(rig)
bpy.context.view_layer.objects.active = rig; bpy.ops.object.mode_set(mode='EDIT')
E = arm.edit_bones
def bone(name, h, t, parent=None):
    b = E.new(name); b.head = h; b.tail = t
    if parent: b.parent = E[parent]; b.use_connect = False
    b.align_roll(Vector((0, -1, 0)))  # eje Z local hacia delante: girar en X local = adelante/atrás
    return b
hip, chest, neck, top = J['hip'], J['chest'], J['neck'], J['top']
bone('root', (0, 0, 0), (0, 0, .15))
bone('hips', (0, 0, hip), (0, 0, hip + .12), 'root')
bone('spine', (0, 0, hip + .12), (0, 0, chest), 'hips')
bone('head', (0, 0, neck), (0, 0, top), 'spine')
for s, side in ((1, 'L'), (-1, 'R')):  # L = +X (izquierda del personaje mirando a -Y)
    sh, el, ha = J['shoulder'], J['elbow'], J['hand']
    bone(f'arm.{side}', (s * sh[0], 0, sh[1]), (s * el[0], 0, el[1]), 'spine')
    bone(f'fore.{side}', (s * el[0], 0, el[1]), (s * ha[0], 0, ha[1]), f'arm.{side}')
    lx = J['leg_x']
    bone(f'thigh.{side}', (s * lx, 0, hip), (s * lx, 0, J['knee']), 'hips')
    bone(f'shin.{side}', (s * lx, 0, J['knee']), (s * lx, 0, .02), f'thigh.{side}')
bpy.ops.object.mode_set(mode='OBJECT')

# ---------- pesos ----------
def seg_dist(P, a, b):
    a, b = np.array(a), np.array(b); ab = b - a
    t = np.clip(((P - a) @ ab) / (ab @ ab), 0, 1)
    return np.linalg.norm(P - (a + t[:, None] * ab), axis=1)
bones = {b.name: (np.array(b.head_local), np.array(b.tail_local)) for b in arm.bones}
names = [n for n in bones if n != 'root']
D = np.stack([seg_dist(V, *bones[n]) for n in names], 1)
x, z = V[:, 0], V[:, 2]
allow = np.ones_like(D, dtype=bool)
idx = {n: i for i, n in enumerate(names)}
gate = J['arm_gate']
for i, n in enumerate(names):
    if n.startswith(('arm', 'fore')):
        s = 1 if n.endswith('L') else -1
        allow[:, i] = (s * x > gate * .7) & (z < J['shoulder'][1] + .15) & (V[:, 1] < .25)  # nada de la espalda (carcaj, capa)
    if n.startswith(('thigh', 'shin')):
        s = 1 if n.endswith('L') else -1
        allow[:, i] = (s * x > -.02) & (z < hip + .08) & (np.abs(x) < gate)
    if n == 'head': allow[:, i] = z > J['head_rigid'] - .08
    if n in ('spine', 'hips'): allow[:, i] = (np.abs(x) < gate + .06) | (z > J['shoulder'][1])
# fuera del tronco y por debajo del hombro: siempre brazo
out = np.abs(x) > gate
for n in names:
    if not n.startswith(('arm', 'fore')): allow[out & (z < J['shoulder'][1]), idx[n]] = False
W = np.where(allow, 1.0 / np.maximum(D, .015) ** 4, 0)
W[z > J['head_rigid'] + .06] = 0; W[z > J['head_rigid'] + .06, idx['head']] = 1  # cabeza rígida
# manos y lo que sujetan (arco, armas): rígidos con el antebrazo de su lado
# ("prop": lados que llevan un objeto largo, como el arco, que sube por encima del hombro)
for s_, side in ((1, 'L'), (-1, 'R')):
    top_ = J['shoulder'][1] + .1
    m_ = (s_ * x > gate) & (z < top_) & (V[:, 1] < .25)
    W[m_] = 0; W[m_, idx[f'fore.{side}']] = 1
W = W / np.maximum(W.sum(1, keepdims=True), 1e-9)
# quedarse con los 2 huesos más fuertes por vértice
order = np.argsort(-W, 1)
for vi in range(len(V)):
    keep = order[vi, :2]; m = np.zeros(len(names)); m[keep] = W[vi, keep]; W[vi] = m / m.sum()
groups = {n: mesh.vertex_groups.new(name=n) for n in names}
for i, n in enumerate(names):
    nz = np.nonzero(W[:, i] > .01)[0]
    for vi in nz: groups[n].add([int(vi)], float(W[vi, i]), 'REPLACE')

# ---------- objetos nuevos (arco) pegados al antebrazo ----------
def make_bow(grip, span, side):
    import bmesh
    wood = bpy.data.materials.new('bow_wood'); wood.use_nodes = True
    bs = wood.node_tree.nodes['Principled BSDF']; bs.inputs['Base Color'].default_value = (0.45, 0.2, 0.05, 1); bs.inputs['Roughness'].default_value = .45
    dark = bpy.data.materials.new('bow_grip'); dark.use_nodes = True
    dk = dark.node_tree.nodes['Principled BSDF']; dk.inputs['Base Color'].default_value = (0.16, 0.07, 0.03, 1); dk.inputs['Roughness'].default_value = .6
    gold = bpy.data.materials.new('bow_gold'); gold.use_nodes = True
    gd = gold.node_tree.nodes['Principled BSDF']; gd.inputs['Base Color'].default_value = (1.0, 0.7, 0.15, 1); gd.inputs['Metallic'].default_value = .7; gd.inputs['Roughness'].default_value = .3
    string = bpy.data.materials.new('bow_string'); string.use_nodes = True
    string.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.95, 0.92, 0.85, 1)
    H = (span[1] - span[0]) / 2 * .95; g = Vector(grip)
    # palas: arco que se curva hacia delante (-Y) con las puntas vueltas hacia atrás
    pts = []
    for i in range(-10, 11):
        t = i / 10; zz = t * H
        yy = -.12 * (1 - t * t) + .07 * max(0, abs(t) - .8) / .2 + .12
        pts.append((g.x, g.y + yy, g.z + zz))
    objs = []
    from lib import tube, sphere
    objs.append(tube('bowU', [Vector(p) for p in pts[10:]], .062, .032, m=wood, res=4))
    objs.append(tube('bowD', [Vector(p) for p in pts[10::-1]], .062, .032, m=wood, res=4))
    objs.append(tube('grip', [Vector((g.x, g.y, g.z - .12)), Vector((g.x, g.y, g.z + .12))], .072, m=dark))
    for sgn in (-1, 1):
        objs.append(sphere('tip', (g.x, g.y + .19, g.z + sgn * H), .045, m=gold, seg=16))
    objs.append(tube('string', [Vector((g.x, g.y + .19, g.z - H)), Vector((g.x, g.y + .19, g.z + H))], .008, m=string))
    for o2 in bpy.context.selected_objects: o2.select_set(False)
    for o2 in objs: o2.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.join(); b = bpy.context.view_layer.objects.active; b.name = 'bow'
    # unirlo a la malla con peso 100% en el antebrazo (más fiable que colgarlo del hueso al exportar)
    vg = b.vertex_groups.new(name='fore.' + side); vg.add(list(range(len(b.data.vertices))), 1.0, 'REPLACE')
    for o2 in bpy.context.selected_objects: o2.select_set(False)
    b.select_set(True); mesh.select_set(True); bpy.context.view_layer.objects.active = mesh; bpy.ops.object.join()
    return mesh
for pr, grip, span in NEWPROPS: make_bow(grip, span, pr['side'])
mesh.parent = rig
md = mesh.modifiers.new('arm', 'ARMATURE'); md.object = rig
lowz = z < .4
print('low verts weights', {n: round(float(W[lowz, i].sum()), 1) for i, n in enumerate(names)})
print('weights ok', {n: int((W[:, i] > .5).sum()) for i, n in enumerate(names)})

if POSE:
    # pose de prueba: paso adelante, brazo derecho arriba, cabeza girada
    pb = rig.pose.bones
    for b in pb: b.rotation_mode = 'XYZ'
    POSES = {'rest': {}, 'thigh': {'thigh.L': (35, 0, 0)}, 'arm': {'arm.R': (60, 0, 0)}, 'head': {'head': (0, 25, 0)}, 'win': {'arm.L': (0, 0, 140), 'arm.R': (0, 0, -140)}, 'atk': {'arm.L': (80, 0, 0), 'fore.R': (70, 0, 0)}}
    pose = POSES[os.environ.get('POSE', 'rest')]
    for n, (rx, ry, rz) in pose.items(): pb[n].rotation_euler = (math.radians(rx), math.radians(ry), math.radians(rz))
    print('axes', {b.name: [tuple(round(c, 2) for c in b.matrix_local.to_3x3().col[i]) for i in range(3)] for b in rig.data.bones if b.name in ('thigh.L', 'arm.R', 'head')})
    s = bpy.context.scene
    s.render.engine = 'CYCLES'; s.cycles.device = 'CPU'; s.cycles.samples = 24; s.cycles.use_denoising = True
    s.render.resolution_x = 520; s.render.resolution_y = 600
    w = bpy.data.worlds.new('w'); s.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[1].default_value = 3.0
    s.view_settings.view_transform = 'Standard'
    for name, ang in (('a', -35), ('b', 60)):
        bpy.ops.object.camera_add(location=(4.4 * math.sin(math.radians(ang)), -4.4 * math.cos(math.radians(ang)), 1.2))
        cam = bpy.context.object; cam.rotation_euler = (Vector((0, 0, 1.0)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
        s.camera = cam; s.render.filepath = POSE.replace('.png', f'_{name}.png'); bpy.ops.render.render(write_still=True)
    for b in pb: b.rotation_euler = (0, 0, 0)

for o in list(bpy.data.objects):
    if o.type not in ('MESH', 'ARMATURE'): bpy.data.objects.remove(o, do_unlink=True)
for o in bpy.context.selected_objects: o.select_set(False)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', export_skins=True, export_animations=False, export_image_format='JPEG', export_jpeg_quality=88)
print('OK', OUT, os.path.getsize(OUT))

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
    top_ = 1.45 if side in J.get('prop', []) else J['shoulder'][1] + .1
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

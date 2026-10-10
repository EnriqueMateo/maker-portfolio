# Prueba de sprites pre-renderizados (técnica de Clash Royale): anima el héroe 3D con su esqueleto
# y renderiza cada fotograma desde el ángulo de la cámara del juego.
# Uso: python anim_sprites.py -- in.glb out_dir [anim]   (anim: walk | attack | idle)
import sys, os, math, bpy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from mathutils import Vector, Euler
a = sys.argv[sys.argv.index('--') + 1:]
src, out = a[0], a[1]; ANIM = a[2] if len(a) > 2 else 'walk'
os.makedirs(out, exist_ok=True)
reset()
bpy.ops.import_scene.gltf(filepath=src)
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
arm = next((o for o in bpy.data.objects if o.type == 'ARMATURE'), None)
pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
root = empty('ROOT')
for o in bpy.data.objects:
    if o.parent is None and o != root: o.parent = root
k = 2.0 / (mx.z - mn.z); root.scale = (k, k, k)
root.location = (-(mn.x + mx.x) / 2 * k, -(mn.y + mx.y) / 2 * k, -mn.z * k)
print('BONES', [b.name for b in arm.pose.bones] if arm else None)
studio(res=(320, 320), samples=24)
v = bpy.context.scene.view_settings; v.view_transform = 'Standard'; v.look = 'None'; v.exposure = 0
# cámara del juego: unos 50° por encima, el héroe en 3/4 de frente
r = 7.0; el = math.radians(42); az = math.radians(-28)
bpy.context.view_layer.update()
pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
cx = sum(p.x for p in pts) / len(pts); cy = sum(p.y for p in pts) / len(pts); top = max(p.z for p in pts)
print('BBOX2', cx, cy, top)
tgt = Vector((cx, cy, top * .48))
camera((tgt.x + r * math.cos(el) * math.sin(az), tgt.y - r * math.cos(el) * math.cos(az), tgt.z + r * math.sin(el)), tuple(tgt), lens=100 * top / 2)
P = arm.pose.bones if arm else {}
def rot(name, x=0, y=0, z=0):
    b = P.get(name) if arm else None
    if b: b.rotation_mode = 'XYZ'; b.rotation_euler = Euler((x, y, z))
def reset_pose():
    for b in (arm.pose.bones if arm else []): b.rotation_mode = 'XYZ'; b.rotation_euler = Euler((0, 0, 0)); b.location = (0, 0, 0)
N = {'walk': 10, 'attack': 10, 'idle': 8}[ANIM]
for f in range(N):
    t = f / N; reset_pose(); w = math.sin(t * 2 * math.pi)
    if ANIM == 'walk':
        rot('thigh.L', .55 * w); rot('thigh.R', -.55 * w)
        rot('shin.L', .5 * max(0, -w)); rot('shin.R', .5 * max(0, w))
        rot('arm.L', -.45 * w); rot('arm.R', .45 * w)
        rot('spine', .08, 0, .06 * w); rot('head', -.04, 0, -.05 * w)
        root.location.z = -mn.z * k + abs(w) * .06
    elif ANIM == 'attack':
        p = -math.sin(t / .35 * math.pi / 2) if t < .35 else (-1 + 2.3 * math.sin((t - .35) / .15 * math.pi / 2) if t < .5 else 1.3 * (1 - (t - .5) / .5))
        rot('arm.R', -1.2 * p, 0, 0); rot('fore.R', -.6 * max(0, -p)); rot('arm.L', .4 * p)
        rot('spine', .15 * p, 0, -.1 * p); rot('head', -.1 * p)
    else:
        b = math.sin(t * 2 * math.pi); rot('spine', .03 * b); rot('head', .04 * b, .06 * b); rot('arm.L', .05 * b); rot('arm.R', -.05 * b)
    bpy.context.view_layer.update()
    render(os.path.join(out, f'{ANIM}_{f:02d}.png'))
print('OK', N)

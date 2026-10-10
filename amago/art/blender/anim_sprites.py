# Sprites pre-renderizados (técnica de Clash Royale): anima el héroe 3D con su esqueleto y renderiza cada
# fotograma desde el ángulo de la cámara del juego, de frente (f) o de espaldas (b).
# Uso: python anim_sprites.py -- in.glb out_dir vista [anims] [estilo]
#   vista: f | b; anims: idle,walk,attack,hit,ko,win; estilo de ataque: breath | swing | stomp | cast
import sys, os, math, json, bpy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from mathutils import Vector, Euler
a = sys.argv[sys.argv.index('--') + 1:]
src, out, VIEW = a[0], a[1], a[2]
ANIMS = a[3].split(',') if len(a) > 3 and a[3] else ['idle', 'walk', 'attack', 'hit', 'ko', 'win']
STYLE = a[4] if len(a) > 4 else 'breath'
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
base = Vector((-(mn.x + mx.x) / 2 * k, -(mn.y + mx.y) / 2 * k, -mn.z * k)); root.location = base
studio(res=(256, 256), samples=20)
v = bpy.context.scene.view_settings; v.view_transform = 'Standard'; v.look = 'None'; v.exposure = 0
# cámara del juego: ~42° de elevación; de frente en 3/4, o de espaldas
r = 9.0; el = math.radians(42); az = math.radians(-28 if VIEW == 'f' else 180 - 28)
tgt = Vector((0, 0, 1.05))
camera((tgt.x + r * math.cos(el) * math.sin(az), tgt.y - r * math.cos(el) * math.cos(az), tgt.z + r * math.sin(el)), tuple(tgt), lens=float(os.environ.get('LENS', 118)))
P = arm.pose.bones
def rot(name, x=0, y=0, z=0):
    b = P.get(name)
    if b: b.rotation_mode = 'XYZ'; e = b.rotation_euler; b.rotation_euler = Euler((e.x + x, e.y + y, e.z + z))
def reset_pose():
    for b in P: b.rotation_mode = 'XYZ'; b.rotation_euler = Euler((0, 0, 0)); b.location = (0, 0, 0)
    root.location = base; root.rotation_euler = (0, 0, 0)
def ease(t): return t * t * (3 - 2 * t)
N = {'idle': 8, 'walk': 10, 'attack': 10, 'hit': 6, 'ko': 8, 'win': 10}
meta = {}
for an in ANIMS:
    for f in range(N[an]):
        t = f / N[an]; reset_pose(); w = math.sin(t * 2 * math.pi)
        if an == 'idle':
            rot('spine', .03 * w); rot('head', .04 * w, .05 * math.sin(t * 2 * math.pi + 1)); rot('arm.L', .06 * w); rot('arm.R', -.06 * w)
            root.location.z = base.z + .01 * w
        elif an == 'walk':
            rot('thigh.L', .42 * w); rot('thigh.R', -.42 * w)
            rot('shin.L', .45 * max(0, -w)); rot('shin.R', .45 * max(0, w))
            rot('arm.L', -.4 * w); rot('arm.R', .4 * w)
            rot('spine', .06, 0, .05 * w); rot('head', -.03, 0, -.04 * w)
            root.location.z = base.z + abs(w) * .07
        elif an == 'attack':
            # carga hacia atrás y golpe hacia delante (el frente del modelo mira a -Y)
            p = -ease(t / .35) if t < .35 else (-1 + 2.3 * ease((t - .35) / .15) if t < .5 else 1.3 * (1 - ease((t - .5) / .5)))
            if STYLE == 'breath':
                rot('head', .35 * p); rot('spine', .18 * p); rot('arm.L', -.3 * max(0, -p)); rot('arm.R', -.3 * max(0, -p))
            elif STYLE == 'stomp':
                # pisotón: brazos arriba en la carga y golpe al suelo con los dos
                rot('arm.L', -1.3 * max(0, -p) + .5 * max(0, p)); rot('arm.R', -1.3 * max(0, -p) + .5 * max(0, p))
                rot('spine', -.15 * max(0, -p) + .3 * max(0, p)); rot('thigh.L', -.4 * max(0, -p))
                root.location.z = base.z + .25 * max(0, -p)
            elif STYLE == 'cast':
                # conjuro: los dos brazos al frente y hacia arriba
                rot('arm.L', -1.4 * p); rot('arm.R', -1.4 * p); rot('head', -.2 * p); rot('spine', .12 * p)
            else:
                rot('arm.R', -1.1 * p); rot('fore.R', -.5 * max(0, -p)); rot('arm.L', .35 * p); rot('spine', .15 * p, 0, -.1 * p)
            root.location.y = base.y - .12 * max(0, p)
        elif an == 'hit':
            e = math.sin(min(1, t * 1.6) * math.pi)
            rot('spine', -.32 * e); rot('head', -.3 * e); rot('arm.L', 0, 0, .5 * e); rot('arm.R', 0, 0, -.5 * e)
            root.location.y = base.y + .15 * e
        elif an == 'ko':
            kk = min(1, t * 1.4); b = 1 - abs(math.cos(kk * math.pi * 1.5)) * (1 - kk) * .15
            root.rotation_euler = (-1.45 * ease(kk) * b, 0, 0); rot('arm.L', 0, 0, .6 * kk); rot('arm.R', 0, 0, -.6 * kk); rot('head', -.3 * kk)
            root.location.y = base.y + .25 * kk
        elif an == 'win':
            j = abs(math.sin(t * 2 * math.pi)); rot('arm.L', 0, 0, 1.0 + .2 * w); rot('arm.R', 0, 0, -1.0 + .2 * w); rot('head', -.15, .15 * w)
            rot('thigh.L', -.2 * j); rot('thigh.R', -.2 * j); root.location.z = base.z + .35 * j
        bpy.context.view_layer.update()
        render(os.path.join(out, f'{VIEW}_{an}_{f:02d}.png'))
    meta[an] = N[an]
json.dump(meta, open(os.path.join(out, f'meta_{VIEW}.json'), 'w'))
print('OK', meta)

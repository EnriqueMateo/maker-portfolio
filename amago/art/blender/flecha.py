import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
OUT = os.path.dirname(os.path.abspath(__file__))
POSE = (sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv else 'hero')

reset()
SKIN = mat('skin', hexc('#ffb98a'), rough=.42, sss=.35, sss_r=(1, .38, .22))
INNER = mat('mouth', hexc('#6e0f20'), rough=.5)
TEETH = mat('teeth', hexc('#fffaf0'), rough=.18, coat=.6)
TONGUE = mat('tongue', hexc('#ff5470'), rough=.35, sss=.2)
EYEW = mat('eyew', hexc('#ffffff'), rough=.05, coat=1, coat_r=.02)
IRIS = mat('iris', hexc('#1fa83c'), rough=.08, coat=1, coat_r=.02)
PUPIL = mat('pupil', hexc('#0c0a12'), rough=.05, coat=1)
SPARK = mat('spark', (1, 1, 1), emit=6)
HAIR = mat('hair', hexc('#ff4a0a'), rough=.35, sss=.1, coat=.35)
HOOD = mat('hood', hexc('#14b347'), rough=.55, sheen=.5, coat=.15)
TUNIC = mat('tunic', hexc('#0e9a3a'), rough=.6, sheen=.6)
LEATHER = mat('leather', hexc('#7a3e14'), rough=.42, coat=.35)
LEATHER2 = mat('leather2', hexc('#4e2508'), rough=.5, coat=.2)
GOLD = mat('gold', hexc('#ffc21a'), rough=.22, metal=1)
WOOD = mat('wood', hexc('#9c5a22'), rough=.4, coat=.5)
STRING = mat('string', hexc('#fff3d6'), rough=.4)
RED = mat('feather', hexc('#ff2d4b'), rough=.4, sheen=.5)
PANTS = mat('pants', hexc('#6b3b16'), rough=.65, sheen=.4)

root = empty('root')
body = empty('body', (0, 0, .62), root)
head = empty('head', (0, 0, 1.12), body)
armL = empty('armL', (.36, 0, 1.0), body); armR = empty('armR', (-.36, 0, 1.0), body)
legL = empty('legL', (.15, 0, .6), root); legR = empty('legR', (-.15, 0, .6), root)

H = Vector((0, 0, 1.45))
# ---------------- cabeza ----------------
b = Blob('Head')
b.ell(H, .45, (1.0, .96, 1.0))
b.ell(H + Vector((0, -.05, -.17)), .36, (1.02, .95, .88))
for s in (-1, 1):
    b.ball(H + Vector((s * .22, -.29, -.13)), .13)
    b.ell(H + Vector((s * .44, .02, -.03)), .09, (.6, .9, 1.25))
b.ball(H + Vector((0, -.27, -.29)), .15)
b.ell(H + Vector((0, -.45, -.04)), .062, (1, 1, .95))
for x in (-.19, -.14, -.09, -.045, 0, .045, .09, .14, .19):
    z = -.215 + 3.2 * x * x
    b.ell(H + Vector((x, -.46 + abs(x) * .35, z)), .055 - abs(x) * .12, (1.15, 1, .62), neg=True)
hd = b.mesh('head', voxel=.0065, smooth=6, m=SKIN, fillet=3)
reparent(hd, head)
sphere('mouthIn', H + Vector((0, -.32, -.19)), .2, scale=(1.05, .75, .5), m=INNER, parent=head)
for x in (-.12, -.06, 0, .06, .12):
    rbox(f'tooth{x}', H + Vector((x, -.432 + abs(x) * .34, -.196 + 3.2 * x * x)), (.058, .045, .042), bevel=.016, rot=(0, 0, x * 1.6), m=TEETH, parent=head)
sphere('tongue', H + Vector((0, -.38, -.245)), .08, scale=(1.4, .8, .32), m=TONGUE, parent=head)
for x, z in [(-.24, -.05), (-.2, -.08), (-.27, -.1), (.24, -.05), (.2, -.08), (.27, -.1)]:
    sphere(f'freckle{x}{z}', H + Vector((x, -.39 + abs(x) * .25, z)), .012, m=mat('freckle', hexc('#e07a4a'), rough=.5), parent=head)
for s in (-1, 1):
    c = H + Vector((s * .165, -.345, .05))
    sphere(f'eye{s}', c, .125, scale=(.95, .7, 1.12), m=EYEW, parent=head)
    fwd = Vector((s * .05 - .03, -1, .0)).normalized()
    ic = c + fwd * .083
    sphere(f'iris{s}', ic, .074, scale=(1, .35, 1.08), m=IRIS, parent=head)
    sphere(f'pupil{s}', ic + fwd * .012, .043, scale=(1, .3, 1.1), m=PUPIL, parent=head)
    sphere(f'spark{s}', ic + fwd * .02 + Vector((-.024, 0, .032)), .017, m=SPARK, parent=head)
    sphere(f'sparkb{s}', ic + fwd * .02 + Vector((.02, 0, -.028)), .008, m=SPARK, parent=head)
    lid = sphere(f'lid{s}', c, .137, scale=(.98, .74, 1.14), m=SKIN)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    shell_cut(lid, plane_co=c + Vector((0, 0, .045)), plane_no=Vector((-s * .75, 0, 1)).normalized(), thick=.014)
    reparent(lid, head)
    br = Blob(f'Brow{s}'); br.cap(c + Vector((-s * .07, -.1, .16)), c + Vector((s * .1, -.07, .23)), .032, r2=.022)
    reparent(br.mesh(f'brow{s}', voxel=.005, smooth=4, m=HAIR, fillet=2), head)
hb = Blob('Hair')
for x, z, r in [(-.24, .2, .1), (-.11, .29, .11), (.05, .3, .1), (.2, .24, .09)]:
    hb.ell(H + Vector((x, -.34, z)), r, (1.15, .6, .75), rot=(0, x * 1.4, 0))
reparent(hb.mesh('hair', voxel=.006, smooth=5, m=HAIR, fillet=2), head)
k = Blob('Hood')
k.ell(H + Vector((0, .05, .05)), .56, (1.0, 1.0, 1.03))
k.cap(H + Vector((0, .15, .42)), H + Vector((0, .5, .62)), .15, r2=.09)
k.cap(H + Vector((0, .5, .62)), H + Vector((.04, .8, .62)), .09, r2=.035)
k.ell(H + Vector((0, .05, .05)), .5, (1.0, 1.0, 1.03), neg=True)
k.ell(H + Vector((0, -.48, -.1)), .46, (.88, .9, .9), neg=True)
k.ell(H + Vector((0, 0, -.62)), .6, (1.2, 1.2, .6), neg=True)
reparent(k.mesh('hood', voxel=.009, smooth=6, m=HOOD, fillet=3), head)
fe = Blob('Feather'); fe.ell(H + Vector((.38, .25, .38)), .1, (.35, .25, 1.4), rot=(.3, .5, -.6))
reparent(fe.mesh('feather', voxel=.006, smooth=4, m=RED, fillet=2), head)

# ---------------- cuerpo ----------------
t = Blob('Torso')
t.ell((0, 0, .86), .36, (1.0, .82, .95))
t.ell((0, -.02, .66), .37, (1.03, .85, .7))
t.cap((0, 0, 1.0), (0, 0, 1.12), .13)
reparent(t.mesh('tunic', voxel=.008, smooth=6, m=TUNIC, fillet=3), body)
cape = Blob('Collar')
cape.ell((0, .02, 1.04), .34, (1.15, 1.0, .32))
cape.ell((0, .02, 1.04), .2, (1.1, 1.1, 2), neg=True)
reparent(cape.mesh('collar', voxel=.008, smooth=5, m=HOOD, fillet=3), body)
belt = torus('belt', (0, -.01, .6), .345, .045, m=LEATHER, scale=(1.04, .86, 1)); reparent(belt, body)
rbox('buckle', (0, -.32, .6), (.14, .05, .12), bevel=.03, m=GOLD, parent=body)
sphere('gem', (0, -.35, .6), .026, scale=(1, .5, 1), m=mat('gemg', hexc('#3cff8a'), rough=.05, coat=1, emit=.6), parent=body)
strap = tube('strap', [(-.3, -.22, 1.02), (-.05, -.33, .82), (.25, -.27, .64), (.34, -.05, .6)], .03, m=LEATHER2); reparent(strap, body)
q = Blob('Quiver'); q.cap((.16, .3, .62), (-.12, .34, 1.12), .095, r2=.1)
reparent(q.mesh('quiver', voxel=.007, smooth=4, m=LEATHER, fillet=2), body)
torus('quiverRim', (-.12, .34, 1.12), .1, .022, rot=(0, .52, 0), m=GOLD, parent=body)
for i, dx in enumerate((-.05, 0, .05)):
    a = Vector((-.12 + dx, .34, 1.1)); d = Vector((-.5, .05, .86)).normalized()
    tube(f'arrow{i}', [a, a + d * .22], .008, m=WOOD, parent=body)
    fb = Blob(f'Fl{i}'); fb.ell(a + d * .22, .045, (.35, 1, 1.3), rot=(0, .52, 0)); reparent(fb.mesh(f'fletch{i}', voxel=.004, smooth=3, m=RED, fillet=1), body)

# ---------------- brazos y manos con dedos ----------------
def arm(side, grp):
    s = 1 if side == 'L' else -1
    sh = Vector((s * .36, 0, 1.0)); el = sh + Vector((s * .1, 0, -.22)); wr = el + Vector((s * .02, -.02, -.2))
    sl = Blob(f'Sleeve{side}'); sl.cap(sh, el, .1, r2=.09); sl.cap(el, wr + Vector((0, 0, .05)), .09, r2=.08)
    reparent(sl.mesh(f'sleeve{side}', voxel=.007, smooth=4, m=TUNIC, fillet=2), grp)
    g = Blob(f'Glove{side}')
    pc = wr + Vector((0, 0, -.1))
    g.ell(pc, .1, (.9, .62, 1.0))
    g.cap(wr + Vector((0, 0, .06)), pc, .085, r2=.08)
    for i, fx in enumerate((-.055, -.018, .018, .055)):
        base = pc + Vector((fx, -.005, -.07)); tip = base + Vector((fx * .2, -.05, -.09 + abs(fx) * .25))
        g.cap(base, tip, .03, r2=.028)
    g.cap(pc + Vector((-s * .07, -.04, .0)), pc + Vector((-s * .1, -.09, -.06)), .032, r2=.03)
    reparent(g.mesh(f'glove{side}', voxel=.005, smooth=4, m=LEATHER, fillet=2), grp)
    cu = torus(f'cuff{side}', wr + Vector((0, 0, .04)), .095, .03, m=LEATHER2); reparent(cu, grp)
    return pc
pL = arm('L', armL); pR = arm('R', armR)
# arco en la mano izquierda
bow = empty('bow', pL + Vector((0, -.05, -.06)), armL)
pts = [Vector((0, -math.cos(a) * .5 + .32, math.sin(a) * .52)) for a in [-1.05 + i * 2.1 / 8 for i in range(9)]]
bw = tube('bowWood', [bow.location + p for p in pts], .022, .018, m=WOOD); reparent(bw, armL)
tube('bowString', [bow.location + pts[0], bow.location + Vector((0, .02, 0)), bow.location + pts[-1]], .005, m=STRING, parent=armL)
torus('grip', bow.location + Vector((0, -.18, 0)), .03, .016, m=LEATHER2, parent=armL)

# ---------------- piernas y botas ----------------
for side, grp in (('L', legL), ('R', legR)):
    s = 1 if side == 'L' else -1
    hp = Vector((s * .15, 0, .6))
    lg = Blob(f'Leg{side}'); lg.cap(hp, hp + Vector((s * .02, 0, -.32)), .1, r2=.085)
    reparent(lg.mesh(f'leg{side}', voxel=.007, smooth=4, m=PANTS, fillet=2), grp)
    bt = Blob(f'Boot{side}')
    bt.ell(hp + Vector((s * .02, -.06, -.5)), .14, (1.0, 1.55, .72))
    bt.cap(hp + Vector((s * .02, 0, -.28)), hp + Vector((s * .02, -.01, -.46)), .11)
    bt.ell(hp + Vector((s * .02, -.06, -.66)), .2, (1, 1.6, .5), neg=True)
    reparent(bt.mesh(f'boot{side}', voxel=.007, smooth=4, m=LEATHER, fillet=3), grp)
    so = Blob(f'Sole{side}'); so.ell(hp + Vector((s * .02, -.06, -.565)), .145, (1.02, 1.58, .2)); reparent(so.mesh(f'sole{side}', voxel=.006, smooth=3, m=LEATHER2, fillet=2), grp)
    torus(f'bootCuff{side}', hp + Vector((s * .02, 0, -.27)), .115, .035, m=LEATHER2, parent=grp)

# ---------------- pose ----------------
if POSE == 'hero':
    root.rotation_euler = (0, 0, math.radians(-18))
    armL.rotation_euler = (math.radians(-25), math.radians(0), math.radians(18))
    armR.rotation_euler = (math.radians(-10), 0, math.radians(-30))
    head.rotation_euler = (math.radians(4), 0, math.radians(8))
    body.rotation_euler = (0, math.radians(-4), 0)
    legL.rotation_euler = (math.radians(8), 0, math.radians(4)); legR.rotation_euler = (math.radians(-6), 0, math.radians(-3))

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'flecha.blend'))
if '--norender' in sys.argv: sys.exit(0)
studio(bg=hexc('#ffa94d'), transparent=False)
vs = bpy.context.scene.view_settings; vs.view_transform = 'Standard'
try: vs.look = 'Medium High Contrast'
except Exception as e: print('look', e)
vs.exposure = -.35
camera((1.1, -5.6, 1.35), (0, 0, 1.0), lens=50)
bpy.context.scene.render.resolution_x = 900; bpy.context.scene.render.resolution_y = 1100
render(os.path.join(OUT, f'flecha_{POSE}.png'))

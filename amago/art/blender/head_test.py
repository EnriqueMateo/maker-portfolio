import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from lib import *

reset()
SKIN = mat('skin', hexc('#ffc49a'), rough=.42, sss=.35, sss_r=(1, .38, .22))
INNER = mat('mouth', hexc('#7a1424'), rough=.5)
TEETH = mat('teeth', hexc('#fffaf0'), rough=.18, coat=.6)
TONGUE = mat('tongue', hexc('#ff6a7a'), rough=.35, sss=.2)
EYEW = mat('eyew', hexc('#ffffff'), rough=.05, coat=1, coat_r=.02)
IRIS = mat('iris', hexc('#2fb84a'), rough=.08, coat=1, coat_r=.02)
PUPIL = mat('pupil', hexc('#0c0a12'), rough=.05, coat=1)
SPARK = mat('spark', (1, 1, 1), emit=6)
HAIR = mat('hair', hexc('#e8541c'), rough=.38, sss=.1, coat=.3)
HOOD = mat('hood', hexc('#1fae4a'), rough=.62, sheen=.6)
HOODIN = mat('hoodin', hexc('#0e6b2c'), rough=.7, sheen=.4)

H = Vector((0, 0, 1.45))
# --- cabeza: cráneo, mejillas, barbilla, nariz y orejas fundidos ---
b = Blob('Head')
b.ell(H, .46, (1.0, .95, 1.02))
b.ell(H + Vector((0, -.06, -.16)), .36, (1.05, .95, .9))
for s in (-1, 1):
    b.ball(H + Vector((s * .24, -.3, -.12)), .17)
    b.ell(H + Vector((s * .47, .02, -.02)), .1, (.55, .9, 1.3))
b.ball(H + Vector((0, -.28, -.3)), .16)
b.ball(H + Vector((0, -.47, -.04)), .085, stiff=3)
head = b.mesh('head', voxel=.007, smooth=8, m=SKIN)
# --- boca abierta: hueco con dientes y lengua ---
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=H + Vector((0, -.46, -.2)), segments=48, ring_count=24)
cut = bpy.context.object; cut.scale = (.16, .14, .085); cut.rotation_euler = (0, 0, 0)
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
mw = cut.matrix_world
boolean(head, cut)
finish(head, voxel=0, smooth=3)
sphere('mouthIn', H + Vector((0, -.34, -.2)), .15, scale=(1, .8, .7), m=INNER)
rbox('teethTop', H + Vector((0, -.43, -.155)), (.2, .06, .04), bevel=.018, m=TEETH)
sphere('tongue', H + Vector((0, -.41, -.255)), .09, scale=(1.1, .8, .45), m=TONGUE)
# --- ojos grandes con iris, pupila, brillos y párpados ---
for s in (-1, 1):
    c = H + Vector((s * .17, -.36, .06))
    sphere(f'eye{s}', c, .13, scale=(.95, .7, 1.12), m=EYEW)
    fwd = Vector((s * .06, -1, .02)).normalized()
    ic = c + fwd * .088
    sphere(f'iris{s}', ic, .078, scale=(1, .35, 1.08), rot=(0, 0, s * .06), m=IRIS)
    sphere(f'pupil{s}', ic + fwd * .012, .046, scale=(1, .3, 1.1), m=PUPIL)
    sphere(f'spark{s}', ic + fwd * .02 + Vector((-.025, 0, .035)), .018, m=SPARK)
    sphere(f'spark2{s}', ic + fwd * .02 + Vector((.02, 0, -.03)), .009, m=SPARK)
    lid = sphere(f'lid{s}', c, .142, scale=(.98, .74, 1.14), m=SKIN)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    shell_cut(lid, plane_co=c + Vector((0, 0, .055)), plane_no=Vector((s * -.35, 0, 1)).normalized(), thick=.012)
    # ceja gruesa
    br = Blob(f'Brow{s}'); br.cap(c + Vector((s * -.08, -.12, .17)), c + Vector((s * .1, -.1, .2)), .03)
    br.mesh(f'brow{s}', voxel=.005, smooth=4, m=HAIR)
# --- pelo y capucha con punta ---
hb = Blob('Hair')
for x, z in [(-.25, .22), (-.1, .3), (.08, .3), (.24, .2)]:
    hb.ell(H + Vector((x, -.36, z)), .1, (1.1, .6, .8), rot=(0, 0, x))
hb.mesh('hair', voxel=.006, smooth=6, m=HAIR)
hd = Blob('Hood', res=.015)
hd.ell(H + Vector((0, .04, .04)), .6, (1.0, 1.0, 1.04))
hd.ell(H + Vector((0, .04, .04)), .53, (1.0, 1.0, 1.04), neg=True)
hd.ell(H + Vector((0, -.5, -.08)), .5, (.82, .9, .92), neg=True)
hd.cap(H + Vector((0, .1, .5)), H + Vector((0, .42, .78)), .14)
hd.cap(H + Vector((0, .42, .78)), H + Vector((.05, .78, .86)), .08)
hood = hd.mesh('hood', voxel=.009, smooth=8, m=HOOD)

studio(transparent=False)
camera(H + Vector((.9, -3.2, .25)), H + Vector((0, 0, -.02)), lens=85)
bpy.context.scene.render.resolution_x = 800; bpy.context.scene.render.resolution_y = 800
render(os.path.join(os.path.dirname(__file__), 'head.png'))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(os.path.dirname(__file__), 'head.blend'))

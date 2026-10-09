# Renderiza un .blend con una iluminación y cámara de estudio: python shoot.py -- archivo.blend salida.png variante
import sys, os, math, bpy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
a = sys.argv[sys.argv.index('--') + 1:]
blend, out, var = a[0], a[1], (a[2] if len(a) > 2 else 'a')
res = int(a[3]) if len(a) > 3 else 700
bpy.ops.wm.open_mainfile(filepath=blend)
for o in list(bpy.data.objects):
    if o.type in ('LIGHT', 'CAMERA') or o.name.startswith('Plane'): bpy.data.objects.remove(o, do_unlink=True)
s = bpy.context.scene
s.render.engine = 'CYCLES'; s.cycles.device = 'CPU'; s.cycles.samples = 80; s.cycles.use_denoising = True
s.render.resolution_x = res; s.render.resolution_y = int(res * 1.15); s.render.film_transparent = var.endswith('t')
w = bpy.data.worlds.new('w2'); s.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[0].default_value = (1, .92, .85, 1); w.node_tree.nodes['Background'].inputs[1].default_value = .35
def area(loc, e, size, col, tgt=(0, 0, 1)):
    bpy.ops.object.light_add(type='AREA', location=loc); l = bpy.context.object; l.data.energy = e; l.data.size = size; l.data.color = col
    l.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
area((-2.4, -3.8, 3.4), 520, 3.2, (1, .95, .88))
area((3.4, -2.6, 1.4), 160, 4, (.85, .92, 1))
area((1.6, 3.0, 3.0), 650, 1.8, (.9, .96, 1))
area((-2.6, 2.6, 2.0), 320, 1.6, (1, .92, .82))
if not var.endswith('t'):
    bg = hexc('#ff9d2e')
    bpy.ops.mesh.primitive_plane_add(size=60); assign(bpy.context.object, mat('bgf', bg, rough=.85, spec=.2))
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 9, 12), rotation=(math.pi / 2, 0, 0)); assign(bpy.context.object, mat('bgw', bg, rough=.85, spec=.2))
vs = s.view_settings
if var.startswith('agx'): vs.view_transform = 'AgX'; vs.look = 'AgX - Punchy'; vs.exposure = 0
elif var.startswith('fil'): vs.view_transform = 'Filmic'; vs.look = 'Filmic - Medium High Contrast'; vs.exposure = 0
else: vs.view_transform = 'Standard'; vs.look = 'None'; vs.exposure = -.4
camera((1.0, -4.4, 1.25), (0, 0, 1.02), lens=55)
render(out)

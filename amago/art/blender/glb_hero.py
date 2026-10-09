# Render promocional de un modelo normalizado (.blend de glb_view): python glb_hero.py -- in.blend out.png color angulo [t]
import sys, os, math, bpy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from mathutils import Vector
a = sys.argv[sys.argv.index('--') + 1:]
blend, out, col, ang = a[0], a[1], a[2], float(a[3])
transp = len(a) > 4 and a[4] == 't'
bpy.ops.wm.open_mainfile(filepath=blend)
for o in list(bpy.data.objects):
    if o.type in ('LIGHT', 'CAMERA'): bpy.data.objects.remove(o, do_unlink=True)
for m in bpy.data.materials:
    bs = m.node_tree.nodes.get('Principled BSDF') if m.use_nodes else None
    if bs:
        bs.inputs['Coat Weight'].default_value = .15; bs.inputs['Coat Roughness'].default_value = .25
        # un pelín más de saturación sobre la textura
        nt = m.node_tree; l = [l for l in nt.links if l.to_socket == bs.inputs['Base Color']]
        if l:
            hsv = nt.nodes.new('ShaderNodeHueSaturation'); hsv.inputs['Saturation'].default_value = 1.15; hsv.inputs['Value'].default_value = 1.0
            fs = l[0].from_socket; nt.links.remove(l[0]); nt.links.new(fs, hsv.inputs['Color']); nt.links.new(hsv.outputs['Color'], bs.inputs['Base Color'])
s = bpy.context.scene
s.render.engine = 'CYCLES'; s.cycles.device = 'CPU'; s.cycles.samples = 96; s.cycles.use_denoising = True
s.render.resolution_x = 900; s.render.resolution_y = 1100; s.render.film_transparent = transp
w = bpy.data.worlds.new('w'); s.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = (1, .97, .94, 1); w.node_tree.nodes['Background'].inputs[1].default_value = .6
s.view_settings.view_transform = 'Standard'; s.view_settings.look = 'Medium Contrast'; s.view_settings.exposure = -.65
def area(loc, e, size, c, tgt=(0, 0, 1.1)):
    bpy.ops.object.light_add(type='AREA', location=loc); l = bpy.context.object; l.data.energy = e; l.data.size = size; l.data.color = c
    l.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
area((-2.5, -3.5, 3.4), 600, 3, (1, .96, .9))
area((3.2, -2.8, 1.5), 220, 4, (.9, .95, 1))
area((2.0, 3.0, 3.0), 900, 1.6, (.8, .9, 1))
area((-2.4, 2.6, 2.2), 600, 1.6, (1, .9, .75))
if not transp:
    c = hexc(col)
    bpy.ops.mesh.primitive_plane_add(size=60); assign(bpy.context.object, mat('bgf', c, rough=.8, spec=.15))
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 7, 10), rotation=(math.pi / 2, 0, 0)); assign(bpy.context.object, mat('bgw', tuple(min(1, v * 1.25) for v in c), rough=.9, spec=.1))
t = math.radians(ang); r = 4.1
camera((r * math.sin(t), -r * math.cos(t), 1.25), (0, 0, 1.02), lens=50)
render(out)

# Importa un GLB, lo normaliza (pies en z=0, altura 2) y renderiza vistas: python glb_view.py -- in.glb outprefix
import sys, os, math, bpy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from mathutils import Vector
a = sys.argv[sys.argv.index('--') + 1:]
src, out = a[0], a[1]
reset()
bpy.ops.import_scene.gltf(filepath=src)
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
for o in meshes:
    me = o.data
    print('MESH', o.name, 'verts', len(me.vertices), 'faces', len(me.polygons), 'mats', [m.name for m in me.materials])
for im in bpy.data.images: print('IMG', im.name, im.size[:])
for m in bpy.data.materials:
    if m.use_nodes:
        bs = m.node_tree.nodes.get('Principled BSDF')
        if bs: print('MAT', m.name, 'metal', bs.inputs['Metallic'].default_value, 'rough', bs.inputs['Roughness'].default_value, [l.to_socket.name for l in m.node_tree.links if l.to_node == bs])
pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
print('BBOX', mn, mx)
root = empty('ROOT')
for o in bpy.data.objects:
    if o.parent is None and o != root: o.parent = root
k = 2.0 / (mx.z - mn.z)
root.scale = (k, k, k)
root.location = (-(mn.x + mx.x) / 2 * k, -(mn.y + mx.y) / 2 * k, -mn.z * k)
bpy.context.view_layer.update()
s = bpy.context.scene
s.render.engine = 'CYCLES'; s.cycles.device = 'CPU'; s.cycles.samples = 48; s.cycles.use_denoising = True
s.render.resolution_x = 560; s.render.resolution_y = 640; s.render.film_transparent = False
w = bpy.data.worlds.new('w'); s.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = (1, 1, 1, 1); w.node_tree.nodes['Background'].inputs[1].default_value = .9
s.view_settings.view_transform = 'Standard'; s.view_settings.look = 'None'
for name, ang in [('front', 0), ('q', 35), ('side', 90), ('back', 180)]:
    r = 5.2; t = math.radians(ang)
    camera((r * math.sin(t), -r * math.cos(t), 1.1), (0, 0, 1.0), lens=50)
    render(f'{out}_{name}.png')
bpy.ops.wm.save_as_mainfile(filepath=out + '.blend')

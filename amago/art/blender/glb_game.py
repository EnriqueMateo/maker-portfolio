# Versión ligera para el juego: python glb_game.py -- in.glb out.glb caras texsize
import sys, os, bpy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import reset
a = sys.argv[sys.argv.index('--') + 1:]
src, out, faces, tex = a[0], a[1], int(a[2]), int(a[3])
reset()
bpy.ops.import_scene.gltf(filepath=src)
for o in [o for o in bpy.data.objects if o.type == 'MESH']:
    bpy.context.view_layer.objects.active = o; o.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.remove_doubles(threshold=1e-5); bpy.ops.object.mode_set(mode='OBJECT')
    n = len(o.data.polygons)
    m = o.modifiers.new('dec', 'DECIMATE'); m.ratio = min(1, faces / n)
    bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier='dec')
    o.select_set(True); bpy.ops.object.shade_smooth()
    wn = o.modifiers.new('wn', 'WEIGHTED_NORMAL'); wn.keep_sharp = False; bpy.ops.object.modifier_apply(modifier='wn')
    print('faces', n, '->', len(o.data.polygons))
for im in bpy.data.images:
    if im.size[0] > tex: im.scale(tex, tex)
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_image_format='JPEG', export_jpeg_quality=88)

# Gira un GLB sobre el eje vertical (para los modelos que la IA genera mirando hacia atrás): python glb_turn.py -- in.glb out.glb grados
import sys, os, math, bpy
from mathutils import Matrix
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import reset
a = sys.argv[sys.argv.index('--') + 1:]
reset(); bpy.ops.import_scene.gltf(filepath=a[0])
for o in bpy.data.objects:
    if o.type == 'MESH':
        for o2 in bpy.context.selected_objects: o2.select_set(False)
        o.select_set(True); bpy.context.view_layer.objects.active = o
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        o.data.transform(Matrix.Rotation(math.radians(float(a[2])), 4, 'Z'))  # el importador usa cuaterniones: girar la malla directamente
bpy.ops.export_scene.gltf(filepath=a[1], export_format='GLB', export_image_format='AUTO')

# Arena de AMAGO: diorama de arcilla con la luz horneada en colores de vértice.
# Uso: python arena.py -- <tema> <salida.glb> [preview.png]
# Coordenadas de Blender (z arriba). En el juego (y arriba): x igual, z_juego = -y.
# Tablero del jugador: y en [-5.3, -1.3]; tablero rival: y en [1.3, 5.3]; parte de arriba de las casillas en z = 0.
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
import bpy, bmesh
from mathutils import Vector, noise

a = sys.argv[sys.argv.index('--') + 1:]
THEME, OUT = a[0], a[1]
PREVIEW = a[2] if len(a) > 2 else None
# AMAGO_BARE=1: solo islas, colinas y flores; árboles, rocas, puente y banderas los pone el juego como ilustraciones
BARE = os.environ.get('AMAGO_BARE') == '1'

TH = {
    'pradera': dict(grass='#7ccf34', grass2='#55ad26', rock='#e8cf9c', rock2='#c9a571', water='#38c3ff', leaf='#5ccc3c', leaf2='#a5e04a',
                    trunk='#93603a', path='#f3e2b6', props='tree', flowers=['#ffd23a', '#ff7ab8', '#ffffff'], sky='#bfe9ff', ground='#2a9be0'),
    'bosque':  dict(grass='#4fae3f', grass2='#2f8a34', rock='#9fb08a', rock2='#738a66', water='#2fb5a8', leaf='#2c9b4a', leaf2='#55c25a',
                    trunk='#6e4a2f', path='#d9c79a', props='pine', flowers=['#ff5a4f', '#ffffff', '#ffd23a'], sky='#c9f0d8', ground='#1f8a7e'),
    'volcan':  dict(grass='#6b5a5e', grass2='#4e4247', rock='#3d3440', rock2='#2a2330', water='#ff6a1f', leaf='#ff9a2e', leaf2='#ffd04a',
                    trunk='#3a2c2c', path='#8a7a78', props='crystal', flowers=['#ff7a2a', '#ffcf3a', '#ff4a2a'], sky='#ffb48a', ground='#ff5a14'),
    'trono':   dict(grass='#8b6fd6', grass2='#6c52bd', rock='#b9b2d6', rock2='#8e86b4', water='#5a3fd0', leaf='#c78bff', leaf2='#ff9ae0',
                    trunk='#5a3f7a', path='#e7e0ff', props='tower', flowers=['#ffd23a', '#ffffff', '#ff9ae0'], sky='#d9c9ff', ground='#4a2fb8'),
    'olimpo':  dict(grass='#f3efe4', grass2='#e2dccb', rock='#fff8ea', rock2='#e8dcc0', water='#ffffff', leaf='#ffd34a', leaf2='#fff08a',
                    trunk='#c99a2e', path='#ffffff', props='column', flowers=['#ffd23a', '#ffffff', '#8fd8ff'], sky='#fff3cf', ground='#ffffff'),
}[THEME]
random.seed(7)
reset()

def nmat(name, c1, c2, scale=3.0, rough=.9, emit=0):
    """material mate con manchas suaves entre dos tonos (se hornea en los vértices)"""
    m = mat(name, hexc(c1), rough=rough, spec=.2)
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tex = nt.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value = scale; tex.inputs['Detail'].default_value = 1.5
    ramp = nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position = .42; ramp.color_ramp.elements[1].position = .62
    ramp.color_ramp.elements[0].color = hexc(c1) + (1,); ramp.color_ramp.elements[1].color = hexc(c2) + (1,)
    nt.links.new(tex.outputs['Fac'], ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    if emit:
        nt.links.new(ramp.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = emit
    return m

def bands(name, c1, c2):
    """roca por capas horizontales, como acantilado"""
    m = mat(name, hexc(c1), rough=.95, spec=.15)
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 1.2
    mul = nt.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY_ADD'; mul.inputs[1].default_value = .25
    wave = nt.nodes.new('ShaderNodeMath'); wave.operation = 'SINE'
    sc = nt.nodes.new('ShaderNodeMath'); sc.operation = 'MULTIPLY'; sc.inputs[1].default_value = 7.0
    ramp = nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position = .35; ramp.color_ramp.elements[1].position = .65
    ramp.color_ramp.elements[0].color = hexc(c2) + (1,); ramp.color_ramp.elements[1].color = hexc(c1) + (1,)
    nt.links.new(tc.outputs['Object'], sep.inputs[0]); nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    nt.links.new(nz.outputs['Fac'], mul.inputs[0]); nt.links.new(sep.outputs['Z'], mul.inputs[2])
    nt.links.new(mul.outputs[0], sc.inputs[0]); nt.links.new(sc.outputs[0], wave.inputs[0])
    nt.links.new(wave.outputs[0], ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    return m

GRASS = nmat('grass', TH['grass'], TH['grass2'], 2.2)
ROCK = bands('rock', TH['rock'], TH['rock2'])
LEAF = nmat('leaf', TH['leaf'], TH['leaf2'], 4.0, emit=(.25 if THEME == 'volcan' else 0))
TRUNK = nmat('trunk', TH['trunk'], TH['trunk'], 2)
PATH = nmat('path', TH['path'], TH['rock'], 5)
WOOD = nmat('wood', '#b9824e', '#9a6a3c', 6)
BLUE = mat('blue', hexc('#2f8cff'), rough=.6, spec=.3)
RED = mat('red', hexc('#ff4a5a'), rough=.6, spec=.3)
GOLD = mat('gold', hexc('#ffc93a'), rough=.35, metal=.6)
WHITE = mat('white', hexc('#ffffff'), rough=.6)
FLOWERS = [mat(f'fl{i}', hexc(c), rough=.6) for i, c in enumerate(TH['flowers'])]

objs = []
def keep(o):
    objs.append(o); return o

def cube(co, size):
    bpy.ops.mesh.primitive_cube_add(size=1, location=co); o = bpy.context.object; o.scale = size; return o

# ---------- mesetas: tapa de hierba plana y acantilado de roca blandito ----------
def plateau(cy, sign):
    b = Blob('plat')
    W, D = 7.0, 5.4
    b.pos.append(cube((0, cy, -.75), (W - 1.0, D - 1.0, 1.3)))
    for i in range(34):
        t = i / 34
        per = 2 * (W + D); s = t * per
        if s < W: x, y = -W / 2 + s, -D / 2
        elif s < W + D: x, y = W / 2, -D / 2 + (s - W)
        elif s < 2 * W + D: x, y = W / 2 - (s - W - D), D / 2
        else: x, y = -W / 2, D / 2 - (s - 2 * W - D)
        r = random.uniform(.5, .66)
        b.ell((x * .88, cy + y * .86, -.55 - random.uniform(0, .35)), r, (1, 1, random.uniform(1.1, 1.5)))
        b.ell((x * .85, cy + y * .82, -1.25), r * .9, (1, 1, .9))
    o = b.mesh('plateau', voxel=.07, smooth=4, fillet=3)
    # corta la parte de arriba para dejarla plana a la altura del suelo
    top = cube((0, cy, 1.0 - .16), (20, 20, 2)); boolean(o, top)
    # hierba en las caras que miran hacia arriba, roca en el resto
    o.data.materials.append(GRASS); o.data.materials.append(ROCK)
    for p in o.data.polygons:
        p.material_index = 0 if (p.normal.z > .55 and p.center.z > -.45) else 1
    for p in o.data.polygons: p.use_smooth = True
    # borde del tablero: bordillo pintado del color del equipo
    team = BLUE if sign < 0 else RED
    for (x, y, sx, sy) in [(0, cy - 2.62, 5.4, .22), (0, cy + 2.62, 5.4, .22), (-2.62, cy, .22, 5.0), (2.62, cy, .22, 5.0)]:
        keep(rbox('curb', (x, y, -.1), (sx, sy, .16), bevel=.06, m=team))
    return keep(o)

plateau(-3.35, -1); plateau(3.35, 1)

# ---------- puente de madera en el centro ----------
for i in range(0 if BARE else 6):
    keep(rbox('plank', (random.uniform(-.03, .03), -1.25 + i * .5, -.2), (1.05, .4, .09), bevel=.035, rot=(0, 0, random.uniform(-.05, .05)), m=WOOD))
for sx in (() if BARE else (-1, 1)):
    for y in (-1.3, 1.3):
        keep(rbox('post', (sx * .6, y, -.02), (.12, .12, .45), bevel=.04, m=WOOD))
    keep(tube('rope', [(sx * .6, -1.3, .18), (sx * .6, 0, .05), (sx * .6, 1.3, .18)], .025, m=TRUNK))

# ---------- accesorios ----------
def tree(x, y, s=1.0):
    keep(tube('trunk', [(x, y, -.15), (x + .05 * s, y, .45 * s), (x - .03 * s, y, .8 * s)], .13 * s, .08 * s, m=TRUNK))
    b = Blob('canopy')
    for (dx, dy, dz, r) in [(0, 0, 1.15, .55), (.35, .1, .95, .38), (-.32, -.05, .98, .4), (.05, .2, 1.45, .36), (.0, -.3, 1.0, .35)]:
        b.ball((x + dx * s, y + dy * s, dz * s), r * s)
    keep(b.mesh('canopy', voxel=.035, smooth=3, m=LEAF, fillet=2))

def pine(x, y, s=1.0):
    keep(tube('trunk', [(x, y, -.15), (x, y, .45 * s)], .1 * s, .08 * s, m=TRUNK))
    b = Blob('pine')
    for i, (z, r) in enumerate([(.45, .6), (.85, .47), (1.2, .33)]):
        b.cap((x, y, z * s), (x, y, (z + .55) * s), r * s, r2=.05 * s)
    keep(b.mesh('pine', voxel=.035, smooth=3, m=LEAF, fillet=2))

def crystal(x, y, s=1.0):
    for i in range(3):
        a = random.uniform(0, 6.28); h = random.uniform(.5, 1.0) * s
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=.16 * s, radius2=.02, depth=h, location=(x + math.cos(a) * .12 * s, y + math.sin(a) * .12 * s, h / 2 - .1),
                                        rotation=(random.uniform(-.35, .35), random.uniform(-.35, .35), 0))
        o = bpy.context.object; md = o.modifiers.new('bv', 'BEVEL'); md.width = .02; md.segments = 2; apply_mods(o); assign(o, LEAF); keep(o)
    rock(x, y, .6 * s)

def tower(x, y, s=1.0):
    keep(rbox('tw', (x, y, .35 * s), (.7 * s, .7 * s, 1.0 * s), bevel=.08, m=ROCK))
    for dx in (-.25, 0, .25):
        for dy in (-.25, .25):
            keep(rbox('mer', (x + dx * s, y + dy * s, .95 * s), (.18 * s, .18 * s, .22 * s), bevel=.04, m=ROCK))
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=.5 * s, depth=.7 * s, location=(x, y, 1.35 * s)); o = bpy.context.object; bpy.ops.object.shade_smooth(); assign(o, LEAF); keep(o)

def column(x, y, s=1.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=.2 * s, depth=1.3 * s, location=(x, y, .5 * s)); o = bpy.context.object
    md = o.modifiers.new('bv', 'BEVEL'); md.width = .03; md.segments = 3; apply_mods(o); bpy.ops.object.shade_smooth(); assign(o, ROCK); keep(o)
    keep(rbox('cap', (x, y, 1.2 * s), (.55 * s, .55 * s, .14 * s), bevel=.04, m=GOLD))
    keep(rbox('base', (x, y, -.08), (.55 * s, .55 * s, .14 * s), bevel=.04, m=ROCK))

def rock(x, y, s=1.0, z=-.12):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=.3 * s, location=(x, y, z))
    o = bpy.context.object; o.scale = (1, random.uniform(.8, 1.1), random.uniform(.6, .8))
    for v in o.data.vertices: v.co *= 1 + .18 * noise.noise(v.co * 3 + Vector((x, y, 0)))
    md = o.modifiers.new('sub', 'SUBSURF'); md.levels = 1; apply_mods(o); bpy.ops.object.shade_smooth()
    o.rotation_euler = (0, 0, random.uniform(0, 6.28)); assign(o, ROCK); return keep(o)

def bush(x, y, s=1.0):
    b = Blob('bush')
    for (dx, dy, dz, r) in [(0, 0, .1, .32), (.25, .05, .05, .24), (-.24, .0, .05, .25)]:
        b.ball((x + dx * s, y + dy * s, dz * s - .1), r * s)
    keep(b.mesh('bush', voxel=.03, smooth=3, m=LEAF, fillet=2))

def flowers(x, y, n=6):
    for i in range(n):
        keep(sphere('fl', (x + random.uniform(-.35, .35), y + random.uniform(-.35, .35), -.1), .06, scale=(1, 1, .6), m=random.choice(FLOWERS), seg=12))

def banner(x, y, team):
    keep(tube('pole', [(x, y, -.15), (x, y, 1.25)], .04, m=WOOD))
    keep(sphere('knob', (x, y, 1.3), .07, m=GOLD, seg=16))
    keep(rbox('flag', (x + .22, y, 1.0), (.4, .04, .5), bevel=.03, m=team))

BIG = {'tree': tree, 'pine': pine, 'crystal': crystal, 'tower': tower, 'column': column}[TH['props']]
for sign in (-1, 1):
    cy = 3.3 * sign
    team = BLUE if sign < 0 else RED
    if not BARE: banner(-2.95, cy + 2.75 * sign, team); banner(2.95, cy + 2.75 * sign, team)
    for x in (-3.15, 3.15):
        if not BARE: bush(x, cy - .9, .55); bush(x, cy + 1.1, .5); rock(x + random.uniform(-.1, .1), cy + .2, .55)
        if THEME in ('pradera', 'bosque', 'trono'): flowers(x, cy - 2.0, 5); flowers(x, cy + 2.1, 4)

# colinas de fondo (detrás del rival) y de delante (delante del jugador), con la vegetación grande
def hill(cy, w, n):
    b = Blob('hill')
    b.pos.append(cube((0, cy, -.8), (w, 2.4, 1.2)))
    for i in range(n):
        x = -w / 2 + w * i / (n - 1)
        b.ell((x, cy + random.uniform(-.6, .6), -.5), random.uniform(.8, 1.1), (1, 1, 1.2))
    o = b.mesh('hill', voxel=.05, smooth=4, fillet=3)
    top = cube((0, cy, 1.0 - .05), (40, 6, 2)); boolean(o, top)
    o.data.materials.append(GRASS); o.data.materials.append(ROCK)
    for p in o.data.polygons: p.material_index = 0 if (p.normal.z > .55 and p.center.z > -.4) else 1
    for p in o.data.polygons: p.use_smooth = True
    return keep(o)
hill(8.0, 13, 9); hill(-8.1, 13, 9)
for i, x in enumerate([-5.2, -3.4, -1.3, .9, 3.0, 5.0]):
    if BARE: continue
    BIG(x + random.uniform(-.3, .3), 8.1 + random.uniform(-.5, .5), random.uniform(.9, 1.2))
    if i % 2 == 0: bush(x + .9, 7.2, .7)
for x in ([] if BARE else [-4.6, -2.0, 2.3, 4.7]):
    BIG(x, -8.3 + random.uniform(-.3, .3), random.uniform(.8, 1.0))
for x in [-3.4, 3.4]:
    if not BARE: rock(x, 6.9, .9)
    flowers(x + .6, 7.0, 5) if THEME in ('pradera', 'bosque', 'trono') else None

# ---------- luz y horneado ----------
s = bpy.context.scene
s.render.engine = 'CYCLES'; s.cycles.device = 'CPU'; s.cycles.samples = 48
w = bpy.data.worlds.new('w'); s.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = hexc(TH['sky']) + (1,); w.node_tree.nodes['Background'].inputs[1].default_value = .32
bpy.ops.object.light_add(type='SUN', location=(0, 0, 10)); sun = bpy.context.object
sun.data.energy = 3.4; sun.data.angle = math.radians(12); sun.rotation_euler = (math.radians(38), math.radians(-18), math.radians(-30))
sun.data.color = (1, .96, .9)
# agua provisional para que rebote su color en la luz (no se exporta)
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, -.9)); wat = bpy.context.object
assign(wat, mat('water', hexc(TH['water']), rough=.3, emit=(1.5 if THEME == 'volcan' else 0), emit_c=hexc(TH['water'])))

def merged():
    for o in bpy.context.selected_objects: o.select_set(False)
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.join(); o = bpy.context.view_layer.objects.active; o.name = 'arena'
    return o

arena = merged()
print('verts', len(arena.data.vertices), 'faces', len(arena.data.polygons))

if PREVIEW:
    cam_t = Vector((0, .15, 0)); d = Vector((0, -.82, 1)).normalized()
    bpy.ops.object.camera_add(location=(0, -17.76, 21.84)); c = bpy.context.object
    c.rotation_euler = (cam_t - c.location).to_track_quat('-Z', 'Y').to_euler(); c.data.angle_y = math.radians(40); c.data.sensor_fit = 'VERTICAL'
    s.camera = c; s.render.resolution_x = 450; s.render.resolution_y = 975
    s.view_settings.view_transform = 'Standard'; s.view_settings.look = 'None'
    s.cycles.samples = 24; s.render.filepath = PREVIEW; bpy.ops.render.render(write_still=True)

# hornear luz + color en los vértices
ca = arena.data.color_attributes.new('Col', 'FLOAT_COLOR', 'POINT'); arena.data.color_attributes.active_color = ca
for o in bpy.context.selected_objects: o.select_set(False)
arena.select_set(True); bpy.context.view_layer.objects.active = arena
s.cycles.samples = 64
s.render.bake.target = 'VERTEX_COLORS'
bpy.ops.object.bake(type='COMBINED')
# reducir la malla manteniendo los colores
md = arena.modifiers.new('dec', 'DECIMATE'); md.ratio = min(1, 90000 / max(1, len(arena.data.polygons))); apply_mods(arena)
print('faces final', len(arena.data.polygons))
# material simple que usa los colores horneados (en el juego se pinta sin luz)
arena.data.materials.clear(); vm = bpy.data.materials.new('baked'); vm.use_nodes = True
nt = vm.node_tree; ca_n = nt.nodes.new('ShaderNodeVertexColor'); ca_n.layer_name = 'Col'
nt.links.new(ca_n.outputs['Color'], nt.nodes['Principled BSDF'].inputs['Base Color']); arena.data.materials.append(vm)
bpy.data.objects.remove(wat, do_unlink=True)
for o in list(bpy.data.objects):
    if o.type != 'MESH': bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', export_normals=False, export_vertex_color='ACTIVE', export_materials='EXPORT', export_yup=True)
print('OK', OUT, os.path.getsize(OUT))

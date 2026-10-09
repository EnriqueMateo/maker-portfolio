# Utilidades de modelado y render en Blender para los héroes de AMAGO
import bpy, bmesh, math
from mathutils import Vector, Quaternion, Euler

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def link(o, parent=None):
    bpy.context.scene.collection.objects.link(o)
    if parent: o.parent = parent
    return o

def empty(name, loc=(0,0,0), parent=None):
    e = bpy.data.objects.new(name, None); e.location = loc
    return link(e, parent)

# ---------- materiales ----------
_M = {}
def mat(name, color, rough=.4, sss=0, sss_r=(1,.35,.2), coat=0, coat_r=.08, metal=0, sheen=0, emit=0, emit_c=None, spec=.5):
    if name in _M: return _M[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    c = tuple(color) + (1,) if len(color) == 3 else color
    b.inputs['Base Color'].default_value = c
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    b.inputs['Subsurface Weight'].default_value = sss
    b.inputs['Subsurface Radius'].default_value = sss_r
    b.inputs['Subsurface Scale'].default_value = .04
    b.inputs['Coat Weight'].default_value = coat
    b.inputs['Coat Roughness'].default_value = coat_r
    b.inputs['Sheen Weight'].default_value = sheen
    b.inputs['Specular IOR Level'].default_value = spec
    if emit:
        b.inputs['Emission Color'].default_value = tuple(emit_c or color) + (1,)
        b.inputs['Emission Strength'].default_value = emit
    _M[name] = m
    return m

def hexc(h):
    h = h.lstrip('#'); r, g, b = (int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4
    return (f(r), f(g), f(b))

def assign(o, m):
    o.data.materials.clear(); o.data.materials.append(m); return o

# ---------- arcilla: piezas exactas fundidas en una sola malla ----------
class Blob:
    """añade volúmenes (positivos o negativos); mesh() los une con remallado en vóxeles y suaviza las uniones"""
    def __init__(self, name, res=None):
        self.name = name; self.pos = []; self.neg = []
    def _ell(self, co, r, size=(1,1,1), rot=(0,0,0), neg=False, seg=48):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=seg, ring_count=seg // 2, location=co, rotation=rot)
        o = bpy.context.object; o.scale = size
        (self.neg if neg else self.pos).append(o); return o
    def ball(self, co, r, neg=False, stiff=None):
        return self._ell(co, r, neg=neg)
    def ell(self, co, r, size, rot=(0,0,0), neg=False, stiff=None):
        return self._ell(co, r, size, rot, neg)
    def cap(self, a, b, r, neg=False, stiff=None, r2=None):
        a, b = Vector(a), Vector(b); d = b - a; r2 = r if r2 is None else r2
        q = Vector((0, 0, 1)).rotation_difference(d.normalized())
        bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=r, radius2=r2, depth=d.length, location=(a + b) / 2, rotation=q.to_euler())
        c = bpy.context.object; (self.neg if neg else self.pos).append(c)
        self._ell(a, r, neg=neg); self._ell(b, r2, neg=neg); return c
    def mesh(self, name, voxel=.008, smooth=6, m=None, fillet=4):
        for o in bpy.context.selected_objects: o.select_set(False)
        for o in self.pos: o.select_set(True)
        bpy.context.view_layer.objects.active = self.pos[0]
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        if len(self.pos) > 1: bpy.ops.object.join()
        o = bpy.context.view_layer.objects.active; o.name = name
        md = o.modifiers.new('rm', 'REMESH'); md.mode = 'VOXEL'; md.voxel_size = voxel; apply_mods(o)
        for n in self.neg:
            for o2 in bpy.context.selected_objects: o2.select_set(False)
            n.select_set(True); bpy.context.view_layer.objects.active = n
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
            boolean(o, n)
        if fillet:
            md = o.modifiers.new('rm2', 'REMESH'); md.mode = 'VOXEL'; md.voxel_size = voxel; apply_mods(o)
            md = o.modifiers.new('lap', 'LAPLACIANSMOOTH'); md.lambda_factor = .9; md.iterations = fillet; md.use_volume_preserve = True; apply_mods(o)
        finish(o, 0, smooth)
        if m: assign(o, m)
        return o

def finish(o, voxel=.008, smooth=6):
    if voxel:
        md = o.modifiers.new('rm', 'REMESH'); md.mode = 'VOXEL'; md.voxel_size = voxel; md.use_smooth_shade = True
        apply_mods(o)
    if smooth:
        md = o.modifiers.new('sm', 'CORRECTIVE_SMOOTH'); md.factor = .5; md.iterations = smooth; md.smooth_type = 'SIMPLE'; md.use_only_smooth = True
        apply_mods(o)
    for p in o.data.polygons: p.use_smooth = True
    return o

def apply_mods(o):
    for o2 in bpy.context.selected_objects: o2.select_set(False)
    o.select_set(True); bpy.context.view_layer.objects.active = o
    for md in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=md.name)

def boolean(o, cutter, op='DIFFERENCE', keep=False):
    md = o.modifiers.new('b', 'BOOLEAN'); md.operation = op; md.object = cutter; md.solver = 'EXACT'
    apply_mods(o)
    if not keep: bpy.data.objects.remove(cutter, do_unlink=True)
    return o

# ---------- primitivas lisas ----------
def sphere(name, loc, r, scale=(1,1,1), rot=(0,0,0), m=None, seg=64, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=seg, ring_count=seg // 2, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; o.scale = scale
    bpy.ops.object.shade_smooth()
    if m: assign(o, m)
    if parent: reparent(o, parent)
    return o

def rbox(name, loc, size, bevel=.02, rot=(0,0,0), m=None, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    md = o.modifiers.new('bv', 'BEVEL'); md.width = bevel; md.segments = 6; md.limit_method = 'NONE'
    apply_mods(o); bpy.ops.object.shade_smooth()
    if m: assign(o, m)
    if parent: reparent(o, parent)
    return o

def torus(name, loc, R, r, rot=(0,0,0), m=None, parent=None, scale=(1,1,1)):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=72, minor_segments=24, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; o.scale = scale; bpy.ops.object.shade_smooth()
    if m: assign(o, m)
    if parent: reparent(o, parent)
    return o

def tube(name, pts, r0, r1=None, m=None, parent=None, res=24):
    """tubo suave a lo largo de una curva, con grosor que se afina"""
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 1; cu.bevel_resolution = 8; cu.resolution_u = res; cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    r1 = r0 if r1 is None else r1
    for i, (p, bp) in enumerate(zip(pts, sp.bezier_points)):
        bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'; bp.radius = r0 + (r1 - r0) * i / max(1, len(pts) - 1)
    o = link(bpy.data.objects.new(name, cu))
    for o2 in bpy.context.selected_objects: o2.select_set(False)
    o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.object.convert(target='MESH'); o = bpy.context.object
    for p in o.data.polygons: p.use_smooth = True
    if m: assign(o, m)
    if parent: reparent(o, parent)
    return o

def reparent(o, parent):
    mw = o.matrix_world.copy(); o.parent = parent; o.matrix_world = mw; return o

def shell_cut(o, plane_co, plane_no, thick=.012):
    """deja solo la parte de la malla delante de un plano y le da grosor (párpados, viseras)"""
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=plane_co, plane_no=plane_no, clear_inner=True)
    bm.to_mesh(o.data); bm.free()
    md = o.modifiers.new('so', 'SOLIDIFY'); md.thickness = thick; md.offset = 1
    apply_mods(o); return o

# ---------- estudio de render ----------
def studio(bg=None, transparent=True, res=(900, 900), samples=96, look='AgX - Punchy'):
    s = bpy.context.scene
    s.render.engine = 'CYCLES'; s.cycles.device = 'CPU'; s.cycles.samples = samples; s.cycles.use_denoising = True
    s.render.resolution_x, s.render.resolution_y = res; s.render.film_transparent = transparent
    s.view_settings.view_transform = 'AgX'
    try: s.view_settings.look = look
    except Exception: pass
    s.view_settings.exposure = .25
    w = bpy.data.worlds.new('w'); s.world = w; w.use_nodes = True
    nt = w.node_tree; bgn = nt.nodes['Background']
    grad = nt.nodes.new('ShaderNodeTexGradient'); grad.gradient_type = 'LINEAR'
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Rotation'].default_value = (0, -math.pi / 2, 0)
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (1.0, .78, .55, 1); ramp.color_ramp.elements[1].color = (.55, .78, 1.0, 1)
    nt.links.new(tc.outputs['Generated'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], grad.inputs['Vector'])
    nt.links.new(grad.outputs['Color'], ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'], bgn.inputs['Color'])
    bgn.inputs['Strength'].default_value = .55
    def area(name, loc, energy, size, color, target=(0, 0, 1)):
        bpy.ops.object.light_add(type='AREA', location=loc); l = bpy.context.object; l.name = name
        l.data.energy = energy; l.data.size = size; l.data.color = color
        d = Vector(target) - Vector(loc); l.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler(); return l
    area('key', (-2.6, -3.4, 3.6), 900, 2.6, (1, .93, .84))
    area('fill', (3.2, -2.6, 1.6), 260, 3.5, (.8, .9, 1))
    area('rim', (1.8, 3.2, 3.2), 1100, 1.6, (.85, .93, 1))
    area('rim2', (-2.5, 2.8, 2.2), 500, 1.4, (1, .9, .8))
    if bg:
        bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0)); fl = bpy.context.object
        assign(fl, mat('floor', bg, rough=.6))
        bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 8, 10), rotation=(math.pi / 2, 0, 0)); wl = bpy.context.object
        assign(wl, mat('wall', bg, rough=.6))

def camera(loc, target, lens=70):
    bpy.ops.object.camera_add(location=loc); c = bpy.context.object; c.data.lens = lens
    d = Vector(target) - Vector(loc); c.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = c; return c

def render(path):
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)

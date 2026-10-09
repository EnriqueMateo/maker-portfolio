# Iconos y cofres de AMAGO renderizados en 3D (estilo Supercell): python icons.py -- <pieza> <salida_dir>
# piezas: coin, power, trophy, key, star, chest1, chest2, chest3 (los cofres salen cerrados y abiertos)
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
import bpy, bmesh
from mathutils import Vector

a = sys.argv[sys.argv.index('--') + 1:]
ITEM, OUT = a[0], a[1]
reset()

GOLD = mat('gold', hexc('#ffd43a'), rough=.3, metal=.55, coat=.5)
GOLD2 = mat('gold2', hexc('#f0a010'), rough=.35, metal=.5)
DARK = mat('dark', hexc('#3a1f0e'), rough=.6)

def star_mesh(name, r_out, r_in, depth, m, loc=(0, 0, 0), rot=(0, 0, 0), bevel=.03, pts=5):
    bm = bmesh.new()
    vs = []
    for i in range(pts * 2):
        r = r_out if i % 2 == 0 else r_in; ang = math.pi / 2 + i * math.pi / pts
        vs.append(bm.verts.new((math.cos(ang) * r, math.sin(ang) * r, 0)))
    f = bm.faces.new(vs)
    ext = bmesh.ops.extrude_face_region(bm, geom=[f]); top = [v for v in ext['geom'] if isinstance(v, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0, 0, depth), verts=top)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); o = link(bpy.data.objects.new(name, me))
    o.location = loc; o.rotation_euler = rot
    for o2 in bpy.context.selected_objects: o2.select_set(False)
    o.select_set(True); bpy.context.view_layer.objects.active = o
    md = o.modifiers.new('bv', 'BEVEL'); md.width = bevel; md.segments = 5; md.limit_method = 'NONE'; apply_mods(o)
    bpy.ops.object.shade_smooth(); assign(o, m); return o

def cyl(name, loc, r, depth, m, rot=(0, 0, 0), bevel=.04, verts=96):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name
    md = o.modifiers.new('bv', 'BEVEL'); md.width = bevel; md.segments = 6; md.limit_method = 'NONE'; apply_mods(o)
    bpy.ops.object.shade_smooth(); assign(o, m); return o

def lathe(name, prof, m, loc=(0, 0, 0), seg=96):
    bm = bmesh.new(); prev = None; first = None
    vs = [bm.verts.new((r, 0, z)) for r, z in prof]
    for i in range(len(vs) - 1): bm.edges.new((vs[i], vs[i + 1]))
    bmesh.ops.spin(bm, geom=bm.verts[:] + bm.edges[:], cent=(0, 0, 0), axis=(0, 0, 1), steps=seg, angle=2 * math.pi)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); o = link(bpy.data.objects.new(name, me)); o.location = loc
    for p in o.data.polygons: p.use_smooth = True
    md = o.modifiers.new('sub', 'SUBSURF'); md.levels = 2; md.render_levels = 2
    assign(o, m); return o

def vt():
    # color 'Standard' para que los colores salgan saturados como en los juegos de Supercell
    v = bpy.context.scene.view_settings; v.view_transform = 'Standard'; v.look = 'None'; v.exposure = -.15

def orbit(deg, dist, z):
    # cámara girada alrededor del objeto (en vez de girar las piezas)
    a = math.radians(deg); return (math.sin(-a) * dist, -math.cos(a) * dist, z)

def shot(name, res, cam_loc, target, lens):
    studio(res=(res, res), samples=64); vt()
    camera(cam_loc, target, lens)
    render(os.path.join(OUT, name + '.png'))

if ITEM == 'coin':
    c = cyl('coin', (0, 0, 0), 1, .26, GOLD, rot=(math.radians(90), 0, 0), bevel=.08)
    cyl('rim', (0, -.135, 0), .8, .02, GOLD2, rot=(math.radians(90), 0, 0), bevel=.01)
    star_mesh('st', .58, .25, .1, GOLD, loc=(0, -.13, 0), rot=(math.radians(90), 0, 0))
    shot('coin', 256, orbit(-18, 6, .9), (0, 0, 0), 50)

elif ITEM == 'power':
    # punto de poder: cristal morado tallado con un rayo dorado
    PUR = mat('pur', hexc('#a64dff'), rough=.12, coat=1, sss=.2, emit=.35, emit_c=hexc('#7a2bff'))
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1, location=(0, 0, 0)); g = bpy.context.object
    g.scale = (.8, .55, 1.15); bpy.ops.object.transform_apply(scale=True)
    md = g.modifiers.new('bv', 'BEVEL'); md.width = .05; md.segments = 3; md.limit_method = 'NONE'; apply_mods(g); assign(g, PUR)
    bolt = [(-.05, .55), (.28, .55), (.06, .12), (.3, .12), (-.22, -.6), (-.04, -.05), (-.28, -.05)]
    bm = bmesh.new(); vs = [bm.verts.new((x, 0, y)) for x, y in bolt]; f = bm.faces.new(vs)
    ext = bmesh.ops.extrude_face_region(bm, geom=[f]); bmesh.ops.translate(bm, vec=(0, -.12, 0), verts=[v for v in ext['geom'] if isinstance(v, bmesh.types.BMVert)])
    me = bpy.data.meshes.new('bolt'); bm.to_mesh(me); b = link(bpy.data.objects.new('bolt', me)); b.location = (0, -.5, 0)
    for o2 in bpy.context.selected_objects: o2.select_set(False)
    b.select_set(True); bpy.context.view_layer.objects.active = b
    md = b.modifiers.new('bv', 'BEVEL'); md.width = .025; md.segments = 4; md.limit_method = 'NONE'; apply_mods(b); assign(b, GOLD)
    shot('power', 256, orbit(-15, 6, 1.2), (0, 0, 0), 46)

elif ITEM == 'trophy':
    lathe('cup', [(0, 1.15), (.72, 1.15), (.78, 1.12), (.7, .75), (.5, .42), (.2, .2), (.13, .0), (.16, -.25), (.42, -.42), (.5, -.55), (0, -.55)], GOLD)
    lathe('in', [(0, 1.0), (.62, 1.08), (.0, 1.08)], GOLD2)
    for sx in (-1, 1):
        bpy.ops.mesh.primitive_torus_add(major_radius=.28, minor_radius=.07, location=(sx * .78, 0, .72), rotation=(math.radians(90), 0, 0))
        h = bpy.context.object; h.scale = (1, 1.25, 1); bpy.ops.object.shade_smooth(); assign(h, GOLD)
    rbox('base', (0, 0, -.7), (1.0, .7, .3), bevel=.08, m=mat('wood', hexc('#7a3b1b'), rough=.5, coat=.5))
    star_mesh('st', .2, .09, .05, mat('red', hexc('#ff3a4a'), rough=.25, coat=1), loc=(0, -.62, .65), rot=(math.radians(90), 0, 0), bevel=.015)
    shot('trophy', 256, orbit(-14, 6, 1.6), (0, 0, .25), 42)

elif ITEM == 'key':
    bpy.ops.mesh.primitive_torus_add(major_radius=.42, minor_radius=.13, location=(0, 0, .55), rotation=(math.radians(90), 0, 0)); r = bpy.context.object; bpy.ops.object.shade_smooth(); assign(r, GOLD)
    sphere('gem', (0, -.05, .55), .16, scale=(1, .6, 1), m=mat('gemr', hexc('#ff3a5a'), rough=.1, coat=1))
    tube('shaft', [(0, 0, .14), (0, 0, -.9)], .1, m=GOLD)
    rbox('t1', (.17, 0, -.75), (.22, .16, .1), bevel=.03, m=GOLD); rbox('t2', (.14, 0, -.52), (.16, .16, .09), bevel=.03, m=GOLD)
    for o in bpy.data.objects:
        if o.parent is None: o.location.rotate(__import__('mathutils').Euler((0, math.radians(-35), 0))); o.rotation_euler.y += math.radians(-35)
    shot('key', 256, orbit(-10, 6, .5), (0, 0, 0), 46)

elif ITEM == 'star':
    # ficha del pase: estrella gorda azul y oro
    star_mesh('st', 1.0, .5, .32, mat('bl', hexc('#2fb8ff'), rough=.2, coat=1), loc=(0, .16, 0), rot=(math.radians(90), 0, 0), bevel=.12)
    star_mesh('st2', .55, .27, .1, GOLD, loc=(0, -.2, 0), rot=(math.radians(90), 0, 0), bevel=.05)
    shot('star', 256, orbit(-15, 6, .9), (0, 0, 0), 46)

elif ITEM == 'mission':
    # misiones: medalla verde con una marca de hecho
    cyl('disc', (0, 0, 0), 1, .28, mat('grn', hexc('#2fd36a'), rough=.25, coat=.8), rot=(math.radians(90), 0, 0), bevel=.1)
    cyl('rim', (0, -.145, 0), .82, .02, mat('grn2', hexc('#1a9e4a'), rough=.3), rot=(math.radians(90), 0, 0), bevel=.01)
    pts = [(-.5, .05), (-.32, .23), (-.12, .02), (.38, .5), (.56, .32), (-.12, -.36)]
    bm = bmesh.new(); vs = [bm.verts.new((x, 0, y)) for x, y in pts]; f = bm.faces.new(vs)
    ext = bmesh.ops.extrude_face_region(bm, geom=[f]); bmesh.ops.translate(bm, vec=(0, -.14, 0), verts=[v for v in ext['geom'] if isinstance(v, bmesh.types.BMVert)])
    me = bpy.data.meshes.new('tick'); bm.to_mesh(me); t = link(bpy.data.objects.new('tick', me)); t.location = (0, -.13, 0)
    for o2 in bpy.context.selected_objects: o2.select_set(False)
    t.select_set(True); bpy.context.view_layer.objects.active = t
    md = t.modifiers.new('bv', 'BEVEL'); md.width = .03; md.segments = 4; md.limit_method = 'NONE'; apply_mods(t); assign(t, mat('wh', hexc('#ffffff'), rough=.3, coat=.5))
    shot('mission', 256, orbit(-18, 6, .9), (0, 0, 0), 50)

elif ITEM.startswith('chest'):
    tier = int(ITEM[-1])
    body_c, band_m, sz = {1: ('#c46a2b', GOLD, 1.0), 2: ('#2f7cff', GOLD, 1.0), 3: ('#8a3cff', GOLD, 1.0)}[tier]
    BODY = mat('body', hexc(body_c), rough=.55, coat=.25)
    BODY2 = mat('body2', tuple(c * .7 for c in hexc(body_c)), rough=.55, coat=.3)
    W, D, H = 1.6, 1.05, .78
    rbox('body', (0, 0, H / 2), (W, D, H), bevel=.07, m=BODY)
    for zz in (.26, .52): rbox('groove', (0, -D / 2 - .002, zz), (W - .1, .02, .035), bevel=.01, m=BODY2)
    for sx in (-1, 1):
        rbox('band', (sx * (W / 2 - .2), 0, H / 2), (.2, D + .06, H + .04), bevel=.05, m=band_m)
        rbox('corner', (sx * (W / 2 - .02), -D / 2 + .02, .06), (.16, .16, .14), bevel=.04, m=band_m)
    rbox('rimb', (0, 0, H - .03), (W + .05, D + .05, .09), bevel=.035, m=band_m)
    # tapa redondeada (media cápsula) con bisagra atrás
    lid = empty('lid', (0, D / 2, H))
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=D / 2, depth=W, location=(0, 0, 0), rotation=(0, math.radians(90), 0)); cy = bpy.context.object
    bm = bmesh.new(); bm.from_mesh(cy.data)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, 0), plane_no=(-1, 0, 0), clear_inner=True)
    bmesh.ops.holes_fill(bm, edges=bm.edges[:]); bm.to_mesh(cy.data)
    cy.scale = (.82, 1, 1); bpy.ops.object.transform_apply(scale=True)
    md = cy.modifiers.new('bv', 'BEVEL'); md.width = .06; md.segments = 6; md.limit_method = 'ANGLE'; apply_mods(cy); bpy.ops.object.shade_smooth()
    assign(cy, BODY); cy.location = (0, 0, H); bpy.context.view_layer.update()
    # bandas doradas de la tapa: copias finas de la propia tapa, un poco más gruesas
    bands = []
    for sx in (-1, 1):
        bnd = cy.copy(); bnd.data = cy.data.copy(); bpy.context.collection.objects.link(bnd)
        bnd.data.materials.clear(); bnd.data.materials.append(band_m)
        bnd.scale = (.2 / W, 1.07, 1.07); bnd.location = (sx * (W / 2 - .2), 0, H - .01); bands.append(bnd)
    bpy.context.view_layer.update()
    for o in [cy] + bands: reparent(o, lid)
    # cerradura
    rbox('lock', (0, -D / 2 - .06, H - .02), (.36, .1, .42), bevel=.06, m=band_m)
    sphere('hole', (0, -D / 2 - .115, H - .04), .055, scale=(1, .4, 1), m=DARK, seg=24)
    if tier == 3:
        sphere('gem', (0, -D / 2 - .13, H + .12), .1, scale=(1, .6, 1), m=mat('gemg', hexc('#3cff9a'), rough=.08, coat=1, emit=.4, emit_c=hexc('#1fe07a')), seg=32)
    if tier >= 2:
        st = star_mesh('lst', .2, .09, .05, GOLD, loc=(0, -.4, H + .26), rot=(math.radians(64), 0, 0), bevel=.02); bpy.context.view_layer.update(); reparent(st, lid)
    # brillo dentro (solo se ve abierto)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, H - .05)); gl = bpy.context.object; gl.scale = (W - .15, D - .15, 1)
    assign(gl, mat('glow', hexc('#fff2a0'), emit=18, emit_c=hexc('#ffe27a')))
    studio(res=(720, 720), samples=72); vt()
    camera(orbit(-22, 6.2, 3.6), (0, 0, .75), 62)
    lid.rotation_euler.x = 0; gl.hide_render = True
    render(os.path.join(OUT, f'{ITEM}.png'))
    lid.rotation_euler.x = math.radians(-115); gl.hide_render = False
    bpy.ops.object.light_add(type='POINT', location=(0, 0, H + .4)); pl = bpy.context.object; pl.data.energy = 250; pl.data.color = (1, .85, .4)
    render(os.path.join(OUT, f'{ITEM}_open.png'))
print('OK', ITEM)

import bpy
import math
from math import sin, cos, pi
from mathutils import Vector

# ============================================================
# Hilbert-Bloch Visual Scene for Blender
# ------------------------------------------------------------
# Builds a glowing 3D scene inspired by:
# - global Hilbert-Bloch network sphere
# - exponential multi-qubit state-space sphere
# - infographic-like display panels in the viewport
# ------------------------------------------------------------
# Usage:
# 1. Open Blender
# 2. Switch to the Scripting workspace
# 3. Open this file and run it
# ============================================================

# ------------------------------
# Helpers
# ------------------------------

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    for block in list(bpy.data.meshes):
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in list(bpy.data.curves):
        if block.users == 0:
            bpy.data.curves.remove(block)
    for block in list(bpy.data.materials):
        if block.users == 0:
            bpy.data.materials.remove(block)
    for block in list(bpy.data.images):
        if block.users == 0:
            bpy.data.images.remove(block)


def ensure_world():
    world = bpy.data.worlds.get("World")
    if not world:
        world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    bg = nt.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.005, 0.008, 0.02, 1.0)
        bg.inputs[1].default_value = 0.2


def set_renderer():
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    if hasattr(scene, 'eevee'):
        if hasattr(scene.eevee, 'use_bloom'):
            scene.eevee.use_bloom = True
            scene.eevee.bloom_intensity = 0.08
            scene.eevee.bloom_radius = 6.0
            scene.eevee.bloom_threshold = 0.45
        scene.eevee.taa_samples = 64
        scene.eevee.taa_render_samples = 64
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.fps = 24
    scene.frame_start = 1
    scene.frame_end = 360


def make_emission_principled(name, color=(1,1,1,1), emission_strength=5.0, metallic=0.0, roughness=0.15, alpha=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.blend_method = 'BLEND' if alpha < 1.0 else 'OPAQUE'
    mat.shadow_method = 'NONE'
    nt = mat.node_tree
    for n in nt.nodes:
        nt.nodes.remove(n)

    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')

    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Emission Color'].default_value = color
    bsdf.inputs['Emission Strength'].default_value = emission_strength
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    if 'Alpha' in bsdf.inputs:
        bsdf.inputs['Alpha'].default_value = alpha

    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat


def make_glass_emission(name, color=(0.5,0.8,1,1), strength=1.5):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.blend_method = 'BLEND'
    nt = mat.node_tree
    for n in nt.nodes:
        nt.nodes.remove(n)

    out = nt.nodes.new('ShaderNodeOutputMaterial')
    add = nt.nodes.new('ShaderNodeAddShader')
    glass = nt.nodes.new('ShaderNodeBsdfGlass')
    emis = nt.nodes.new('ShaderNodeEmission')

    glass.inputs['Color'].default_value = color
    glass.inputs['Roughness'].default_value = 0.02
    glass.inputs['IOR'].default_value = 1.45
    emis.inputs['Color'].default_value = color
    emis.inputs['Strength'].default_value = strength

    nt.links.new(glass.outputs['BSDF'], add.inputs[0])
    nt.links.new(emis.outputs['Emission'], add.inputs[1])
    nt.links.new(add.outputs['Shader'], out.inputs['Surface'])
    return mat


def add_uv_sphere(name, location=(0,0,0), radius=0.2, material=None, segments=48, rings=24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, radius=radius, location=location)
    obj = bpy.context.active_object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    return obj


def add_ico_sphere(name, location=(0,0,0), radius=0.2, subdivisions=3, material=None):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=radius, location=location)
    obj = bpy.context.active_object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    return obj


def add_curve(name, points, bevel=0.015, material=None, cyclic=False):
    crv = bpy.data.curves.new(name + '_curve', 'CURVE')
    crv.dimensions = '3D'
    crv.resolution_u = 24
    crv.bevel_depth = bevel
    crv.bevel_resolution = 5
    spline = crv.splines.new('NURBS')
    spline.points.add(len(points)-1)
    for i, p in enumerate(points):
        spline.points[i].co = (p[0], p[1], p[2], 1.0)
    spline.use_endpoint_u = True
    spline.use_cyclic_u = cyclic
    obj = bpy.data.objects.new(name, crv)
    bpy.context.collection.objects.link(obj)
    if material:
        obj.data.materials.append(material)
    return obj


def animate(obj, data_path, key_values, interpolation='BEZIER'):
    for frame, val in key_values:
        set_attr(obj, data_path, val)
        obj.keyframe_insert(data_path=data_path, frame=frame)
    if obj.animation_data and obj.animation_data.action:
        for fc in obj.animation_data.action.fcurves:
            if fc.data_path == data_path:
                for kp in fc.keyframe_points:
                    kp.interpolation = interpolation


def set_attr(obj, data_path, val):
    parts = data_path.split('.')
    target = obj
    for p in parts[:-1]:
        target = getattr(target, p)
    setattr(target, parts[-1], val)


def add_text(name, text, location=(0,0,0), rotation=(math.radians(90), 0, 0), size=0.35, material=None, align='CENTER'):
    bpy.ops.object.text_add(location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.body = text
    obj.data.size = size
    obj.data.align_x = align
    obj.data.extrude = 0.015
    obj.data.bevel_depth = 0.003
    if material:
        obj.data.materials.append(material)
    return obj


def add_panel(name, location=(0,0,0), size=(3, 2), rotation=(math.radians(90), 0, 0), material=None):
    bpy.ops.mesh.primitive_plane_add(size=1, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size[0], size[1], 1)
    if material:
        obj.data.materials.append(material)
    return obj

# ------------------------------
# Scene setup
# ------------------------------
clear_scene()
ensure_world()
set_renderer()

scene = bpy.context.scene

# Camera
bpy.ops.object.camera_add(location=(0, -18, 8), rotation=(math.radians(67), 0, 0))
cam = bpy.context.active_object
cam.name = 'Camera'
cam.data.lens = 42
scene.camera = cam
animate(cam, 'location', [(1,(0,-18,8)), (180,(1.1,-17.4,8.5)), (360,(0,-18,8))])
animate(cam, 'rotation_euler', [(1,(math.radians(67), 0, 0)), (180,(math.radians(64), 0, math.radians(3))), (360,(math.radians(67), 0, 0))])

# Lights
bpy.ops.object.light_add(type='AREA', location=(0, -10, 9))
light = bpy.context.active_object
light.data.energy = 4500
light.data.size = 8
light.rotation_euler = (math.radians(55), 0, 0)

bpy.ops.object.light_add(type='POINT', location=(6, 3, 5))
light2 = bpy.context.active_object
light2.data.energy = 1500
light2.data.color = (0.35, 0.6, 1.0)

bpy.ops.object.light_add(type='POINT', location=(-6, 3, 5))
light3 = bpy.context.active_object
light3.data.energy = 1500
light3.data.color = (1.0, 0.45, 0.8)

# Ground / base
bpy.ops.mesh.primitive_plane_add(size=50, location=(0, 0, -5.5))
ground = bpy.context.active_object
ground_mat = make_emission_principled('GroundMat', (0.012, 0.018, 0.04, 1), 0.0, 0.0, 0.9)
ground.data.materials.append(ground_mat)

# Materials
mat_core = make_emission_principled('Core', (1.0, 0.8, 0.35, 1), 22.0, 0.0, 0.05)
mat_blue = make_emission_principled('Blue', (0.33, 0.72, 1.0, 1), 7.5, 0.05, 0.18)
mat_cyan = make_emission_principled('Cyan', (0.4, 1.0, 0.95, 1), 7.2, 0.05, 0.18)
mat_magenta = make_emission_principled('Magenta', (1.0, 0.45, 0.85, 1), 7.2, 0.05, 0.18)
mat_green = make_emission_principled('Green', (0.62, 1.0, 0.68, 1), 6.8, 0.05, 0.18)
mat_orange = make_emission_principled('Orange', (1.0, 0.68, 0.35, 1), 7.2, 0.05, 0.18)
mat_violet = make_emission_principled('Violet', (0.7, 0.6, 1.0, 1), 7.0, 0.05, 0.18)
mat_white = make_emission_principled('White', (0.95, 0.98, 1.0, 1), 6.0, 0.0, 0.12)
mat_shell = make_glass_emission('Shell', (0.35, 0.5, 1.0, 1), 0.7)
mat_goldline = make_emission_principled('GoldLine', (1.0, 0.68, 0.3, 1), 8.0, 0.0, 0.1)
mat_panel = make_emission_principled('Panel', (0.05, 0.08, 0.15, 1), 0.2, 0.0, 0.5, alpha=0.92)
mat_panel_line = make_emission_principled('PanelLine', (0.75, 0.86, 1.0, 1), 3.0, 0.0, 0.3)

# Main shell
shell = add_uv_sphere('GlobalShell', location=(0,0,0), radius=6.6, material=mat_shell, segments=64, rings=32)
animate(shell, 'rotation_euler', [(1,(0,0,0)), (360,(0,0,2*pi))], interpolation='LINEAR')

# Central core + radiant axis
core = add_uv_sphere('CentralCore', location=(0,0,0), radius=0.46, material=mat_core)
animate(core, 'scale', [(1,(0.85,0.85,0.85)), (90,(1.2,1.2,1.2)), (180,(1.0,1.0,1.0)), (270,(1.18,1.18,1.18)), (360,(0.95,0.95,0.95))])

# Vertical luminous column
bpy.ops.mesh.primitive_cylinder_add(radius=0.16, depth=11.0, location=(0,0,0), rotation=(0,0,0))
axis_col = bpy.context.active_object
axis_col.name = 'AxisColumn'
axis_col.data.materials.append(mat_blue)
axis_col.scale = (1,1,1)
animate(axis_col, 'scale', [(1,(0.65,0.65,1.0)), (120,(1.0,1.0,1.0)), (240,(0.8,0.8,1.0)), (360,(0.95,0.95,1.0))])
animate(axis_col, 'rotation_euler', [(1,(0,0,0)), (360,(0,0,2*pi))], interpolation='LINEAR')

# Horizontal and circular rings around the center
for i, rot in enumerate([(0,0,0), (math.radians(90),0,0), (0,math.radians(90),0)]):
    bpy.ops.mesh.primitive_torus_add(major_radius=3.9, minor_radius=0.035, location=(0,0,0), rotation=rot)
    tor = bpy.context.active_object
    tor.name = f'MainRing_{i+1}'
    tor.data.materials.append([mat_goldline, mat_magenta, mat_blue][i])
    animate(tor, 'rotation_euler', [(1,rot), (360,(rot[0]+2*pi, rot[1]+2*pi, rot[2]+2*pi))], interpolation='LINEAR')

# Nested center rings (radiant geometry)
for i in range(7):
    r = 0.8 + i * 0.28
    bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=0.012, location=(0,0,0), rotation=(math.radians(90),0,0))
    tor = bpy.context.active_object
    tor.name = f'InnerTorus_{i+1}'
    tor.data.materials.append(mat_goldline)

# Local qubit-like spheres
node_data = [
    ((0,0,4.9), 0.44, mat_blue),
    ((0,0,-4.9), 0.44, mat_magenta),
    ((-4.9,0,0), 0.50, mat_violet),
    ((4.9,0,0), 0.50, mat_magenta),
    ((-2.4,2.8,0.9), 0.45, mat_blue),
    ((2.4,2.8,0.9), 0.45, mat_green),
    ((-2.4,-2.8,-0.9), 0.45, mat_cyan),
    ((2.4,-2.8,-0.9), 0.45, mat_blue),
    ((-4.3,2.4,2.2), 0.22, mat_orange),
    ((4.3,2.4,2.2), 0.22, mat_violet),
    ((-3.2,-4.1,-1.7), 0.20, mat_green),
    ((3.2,-4.1,-1.7), 0.20, mat_orange),
    ((-4.3,-2.9,-3.5), 0.26, mat_magenta),
    ((4.3,-2.9,-3.5), 0.26, mat_blue),
]

nodes = []
for idx, (loc, rad, mat) in enumerate(node_data):
    n = add_uv_sphere(f'Node_{idx+1}', location=loc, radius=rad, material=mat)
    nodes.append(n)
    x,y,z = loc
    animate(n, 'location', [
        (1, loc),
        (120, (x*0.98, y*0.98, z + 0.18*sin(idx))),
        (240, (x*1.02, y*1.02, z - 0.15*cos(idx))),
        (360, loc),
    ])

    # local wire ring for mini-Bloch feel
    bpy.ops.mesh.primitive_torus_add(major_radius=rad*1.35, minor_radius=0.008, location=loc, rotation=(0,0,0))
    tr = bpy.context.active_object
    tr.name = f'NodeRing_{idx+1}'
    tr.data.materials.append(mat_white)
    animate(tr, 'rotation_euler', [(1,(0,0,0)), (360,(2*pi, 2*pi, 2*pi))], interpolation='LINEAR')

# Connection curves בין nodes to core and between selected nodes
for idx, n in enumerate(nodes):
    p1 = n.location.copy()
    mid = (p1 + Vector((0,0,0))) * 0.5 + Vector((0, 0, 0.6 * sin(idx)))
    c = add_curve(f'CoreLink_{idx+1}', [p1, mid, (0,0,0)], bevel=0.012, material=mat_white)
    animate(c, 'rotation_euler', [(1,(0,0,0)), (360,(0,0,2*pi))], interpolation='LINEAR')

# Orbital arcs / network loops
pairs = [(0,4), (0,5), (2,4), (3,5), (6,7), (8,2), (9,3), (10,6), (11,7), (12,13)]
for i,(a,b) in enumerate(pairs):
    pa = nodes[a].location.copy()
    pb = nodes[b].location.copy()
    mid = (pa + pb) / 2 + Vector((0, 0, 1.0 + 0.4*sin(i)))
    mat = mat_goldline if i % 2 == 0 else mat_magenta
    crv = add_curve(f'PairArc_{i+1}', [pa, mid, pb], bevel=0.014, material=mat)
    animate(crv, 'rotation_euler', [(1,(0,0,0)), (360,(2*pi*0.4, 2*pi*0.2, 2*pi*0.75))], interpolation='LINEAR')

# Great-circle style arcs around the shell
for i in range(8):
    pts = []
    for j in range(120):
        t = 2*pi*j/119.0
        r = 6.0
        x = r * cos(t)
        y = r * sin(t) * cos(i*pi/8.0)
        z = r * sin(t) * sin(i*pi/8.0)
        pts.append((x,y,z))
    mat = mat_blue if i % 2 == 0 else mat_white
    c = add_curve(f'GreatArc_{i+1}', pts, bevel=0.008, material=mat, cyclic=True)
    animate(c, 'rotation_euler', [(1,(0,0,0)), (360,(2*pi*(0.12*i), 2*pi*(0.08*i), 2*pi*(0.16*i+0.12)))], interpolation='LINEAR')

# Exponential qubit sphere on the left side as a second object
exp_sphere = add_ico_sphere('ExponentialStateSphere', location=(-10.5, 0.2, 0.4), radius=2.2, subdivisions=5, material=make_glass_emission('ExpGlass', (0.6, 0.4, 1.0, 1), 0.45))
animate(exp_sphere, 'rotation_euler', [(1,(0,0,0)), (360,(2*pi, 2*pi*0.35, 2*pi*0.8))], interpolation='LINEAR')

# Sprinkle many tiny state points on/within the sphere
for i in range(260):
    phi = (i * 0.6180339887 * 2*pi) % (2*pi)
    z = 1 - 2*(i+0.5)/260
    r = math.sqrt(max(0.0, 1-z*z))
    jitter = 0.2 * sin(i*1.37)
    x = (2.0 + 0.18*jitter) * r * cos(phi) - 10.5
    y = (2.0 + 0.18*jitter) * r * sin(phi) + 0.2
    zz = (2.0 + 0.18*jitter) * z + 0.4
    m = [mat_magenta, mat_blue, mat_green, mat_orange, mat_violet][i % 5]
    s = add_uv_sphere(f'ExpPoint_{i+1}', location=(x,y,zz), radius=0.045, material=m, segments=16, rings=8)
    animate(s, 'scale', [(1,(0.8,0.8,0.8)), (180,(1.2,1.2,1.2)), (360,(0.85,0.85,0.85))])

# Central burst inside exponential sphere
exp_core = add_uv_sphere('ExpCore', location=(-10.5,0.2,0.4), radius=0.17, material=mat_core)
animate(exp_core, 'scale', [(1,(0.9,0.9,0.9)), (120,(1.5,1.5,1.5)), (240,(1.1,1.1,1.1)), (360,(1.35,1.35,1.35))])

# Left info panel - simplified "NOCH MEHR QUBITS"
panel_left = add_panel('PanelLeft', location=(-10.5, 4.9, 3.0), size=(2.8, 2.25), rotation=(math.radians(90), 0, 0), material=mat_panel)
add_text('TitleLeft', 'NOCH MEHR QUBITS ...', location=(-10.5, 4.83, 4.65), size=0.28, material=mat_panel_line)
add_text('SubLeft', 'Dimension: 2^n wächst exponentiell', location=(-10.5, 4.83, 4.15), size=0.18, material=mat_panel_line)
add_text('BodyLeft', 'Bereits kleine Erhöhungen\nvon n führen zu\nsehr großen Zustandsräumen.', location=(-10.5, 4.83, 1.8), size=0.15, material=mat_panel_line)

# Right infographic wall panel
panel_right = add_panel('PanelRight', location=(10.2, 5.1, 2.4), size=(4.2, 2.65), rotation=(math.radians(90), 0, 0), material=mat_panel)
add_text('PanelRightTitle', 'ZUSTANDSRAUM IN HÖHEREN DIMENSIONEN', location=(10.2, 5.03, 4.6), size=0.18, material=mat_panel_line)
add_text('PanelRightSub', 'verschränkte Paare / Dimension 2^n / Projektionen', location=(10.2, 5.03, 4.28), size=0.11, material=mat_panel_line)

# Small diagram spheres on right panel
small_centers = [
    (8.2, 5.02, 3.55), (10.0, 5.02, 3.55), (11.8, 5.02, 3.55),
    (8.2, 5.02, 2.4), (10.0, 5.02, 2.4), (11.8, 5.02, 2.4),
]
small_mats = [mat_blue, mat_magenta, mat_green, mat_orange, mat_violet, mat_cyan]
for i, c in enumerate(small_centers):
    s = add_uv_sphere(f'PanelSphere_{i+1}', location=c, radius=0.22, material=small_mats[i])
    bpy.ops.mesh.primitive_torus_add(major_radius=0.28, minor_radius=0.008, location=c, rotation=(0,0,0))
    tr = bpy.context.active_object
    tr.data.materials.append(mat_white)

# Table lines on the right panel
for i in range(5):
    z = 1.2 + i * 0.25
    pts = [(7.2, 5.01, z), (13.2, 5.01, z)]
    add_curve(f'PanelLineH_{i+1}', pts, bevel=0.004, material=mat_panel_line)
for i in range(4):
    x = 8.0 + i * 1.65
    pts = [(x, 5.01, 1.15), (x, 5.01, 2.15)]
    add_curve(f'PanelLineV_{i+1}', pts, bevel=0.004, material=mat_panel_line)

# Labels around central system
label_mat = mat_panel_line
add_text('LabelA', 'Hilbert-Bloch Netzwerk', location=(0, -6.9, 6.1), rotation=(math.radians(90), 0, 0), size=0.22, material=label_mat)
add_text('LabelB', 'globale Kopplung / lokaler Bloch-Zustand', location=(0, -6.9, 5.7), rotation=(math.radians(90), 0, 0), size=0.12, material=label_mat)

# A few star particles around the whole scene
for i in range(100):
    x = -15 + (i * 1.731) % 30
    y = 1.5 + ((i * 2.177) % 10)
    z = -1 + ((i * 3.119) % 12)
    s = add_uv_sphere(f'Star_{i+1}', location=(x, y, z), radius=0.03 + 0.02*((i % 3)/3), material=mat_white, segments=10, rings=6)

# Set viewport shading if possible
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'MATERIAL'
                space.shading.use_scene_lights = True
                space.shading.use_scene_world = True
                break

print('Fertig: Hilbert-Bloch Blender Szene erstellt.')

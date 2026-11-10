"""
delta_orbital_blender.py
Conceptual Blender script for a Delta-Orbital model.

Run inside Blender:
- Open Blender
- Go to Scripting
- Open this file
- Run Script
"""

import bpy
import math
from math import sin, cos, pi, sqrt, exp
from mathutils import Vector

EXTENT = 4.5
GRID_N = 22
THRESH_DELTA = 0.18
THRESH_PSI = 0.22
THRESH_ETA = 0.16
FRAME_START = 1
FRAME_END = 120
A = 1.35
POINT_RADIUS = 0.055
FPS = 24


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


def ensure_collection(name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


def make_material(name, color, emission=0.0, alpha=1.0):
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    for node in list(nodes):
        nodes.remove(node)
    out = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.35
    bsdf.inputs["Alpha"].default_value = alpha
    bsdf.inputs["Emission Color"].default_value = (*color, 1.0)
    bsdf.inputs["Emission Strength"].default_value = emission
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    if alpha < 1.0:
        mat.blend_method = 'BLEND'
        mat.shadow_method = 'HASHED'
    return mat


def create_base_instance(name, radius, material):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=(0, 0, 0))
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(material)
    obj.hide_render = True
    obj.hide_viewport = True
    return obj


def create_mesh_object(name, collection):
    mesh = bpy.data.meshes.new(name + "_mesh")
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def set_points_as_vertices(obj, points):
    mesh = obj.data
    mesh.clear_geometry()
    mesh.from_pydata(points if points else [(0.0, 0.0, 0.0)], [], [])
    mesh.update()


def set_geometry_nodes_instancing(obj, instance_obj):
    mod = obj.modifiers.new(name="GN", type='NODES')
    ng = bpy.data.node_groups.new(obj.name + "_GN", 'GeometryNodeTree')
    mod.node_group = ng
    nodes = ng.nodes
    links = ng.links

    group_in = nodes.new("NodeGroupInput")
    group_out = nodes.new("NodeGroupOutput")
    ng.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    ng.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

    inst = nodes.new("GeometryNodeInstanceOnPoints")
    obj_info = nodes.new("GeometryNodeObjectInfo")
    obj_info.transform_space = 'RELATIVE'
    obj_info.inputs["Object"].default_value = instance_obj

    links.new(group_in.outputs["Geometry"], inst.inputs["Points"])
    links.new(obj_info.outputs["Geometry"], inst.inputs["Instance"])
    links.new(inst.outputs["Instances"], group_out.inputs["Geometry"])


def add_text(text, location, size=0.42):
    bpy.ops.object.text_add(location=location)
    obj = bpy.context.active_object
    obj.data.body = text
    obj.data.size = size
    obj.rotation_euler = (math.radians(90), 0, 0)
    return obj


def add_camera_and_lights():
    bpy.ops.object.camera_add(location=(12, -12, 8), rotation=(math.radians(62), 0, math.radians(42)))
    cam = bpy.context.active_object
    bpy.context.scene.camera = cam

    bpy.ops.object.light_add(type='AREA', location=(6, -6, 10))
    light1 = bpy.context.active_object
    light1.data.energy = 3000
    light1.data.size = 8

    bpy.ops.object.light_add(type='POINT', location=(-6, 4, 5))
    light2 = bpy.context.active_object
    light2.data.energy = 1200
    return cam


def delta_field(x, y, t):
    dx = cos(t)
    dy = sin(t)
    strength = 0.15 + 0.85 * (0.5 * (1 + sin(t - pi / 3)))
    return strength * (dx * x + dy * y) * exp(-sqrt(x * x + y * y) / (1.6 * A))


def psi_s(r):
    return exp(-r / A)


def psi_px(x, r):
    return (x / A) * exp(-r / (2 * A))


def psi_py(y, r):
    return (y / A) * exp(-r / (2 * A))


def psi_d(x, y, r):
    return ((x * x - y * y) / (A * A)) * exp(-r / (2.4 * A))


def sample_model(t):
    pts_delta = []
    pts_psi_pos = []
    pts_psi_neg = []
    pts_eta = []

    dx = cos(t)
    dy = sin(t)
    strength = 0.15 + 0.85 * (0.5 * (1 + sin(t - pi / 3)))
    info_mix = 0.25 * (0.5 * (1 + sin(2 * t - 0.7)))

    for iy in range(GRID_N):
        y = -EXTENT + 2 * EXTENT * iy / (GRID_N - 1)
        for ix in range(GRID_N):
            x = -EXTENT + 2 * EXTENT * ix / (GRID_N - 1)
            r = sqrt(x * x + y * y) + 1e-9

            d = delta_field(x, y, t)
            psi = ((1 - 0.75 * strength) * psi_s(r)
                   + strength * (dx * psi_px(x, r) + dy * psi_py(y, r))
                   + info_mix * psi_d(x, y, r))
            eta = exp(-r / (1.8 * A)) * (0.55 + 0.45 * (psi * psi))

            if abs(d) > THRESH_DELTA:
                pts_delta.append((x - 6.5, y, 0.35 * d))
            if psi > THRESH_PSI:
                pts_psi_pos.append((x, y, 0.65 * psi + 0.2))
            elif psi < -THRESH_PSI:
                pts_psi_neg.append((x, y, 0.65 * psi - 0.2))
            if eta > THRESH_ETA:
                pts_eta.append((x + 6.5, y, 1.2 * eta - 0.4))

    return pts_delta, pts_psi_pos, pts_psi_neg, pts_eta


clear_scene()

scene = bpy.context.scene
scene.frame_start = FRAME_START
scene.frame_end = FRAME_END
scene.render.fps = FPS

try:
    scene.render.engine = 'BLENDER_EEVEE'
except Exception:
    pass

if scene.world and scene.world.use_nodes:
    bg = scene.world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.02, 0.02, 0.025, 1.0)
        bg.inputs[1].default_value = 0.35

col = ensure_collection("DeltaOrbital")

mat_delta = make_material("MatDelta", (0.2, 0.7, 1.0), emission=1.5, alpha=0.85)
mat_psi_pos = make_material("MatPsiPos", (1.0, 0.35, 0.35), emission=1.2, alpha=0.9)
mat_psi_neg = make_material("MatPsiNeg", (0.3, 0.45, 1.0), emission=1.2, alpha=0.9)
mat_eta = make_material("MatEta", (1.0, 0.75, 0.2), emission=0.8, alpha=0.8)

inst_delta = create_base_instance("DeltaPoint", POINT_RADIUS, mat_delta)
inst_psi_pos = create_base_instance("PsiPosPoint", POINT_RADIUS, mat_psi_pos)
inst_psi_neg = create_base_instance("PsiNegPoint", POINT_RADIUS, mat_psi_neg)
inst_eta = create_base_instance("EtaPoint", POINT_RADIUS, mat_eta)

obj_delta = create_mesh_object("DeltaCloud", col)
obj_psi_pos = create_mesh_object("PsiPosCloud", col)
obj_psi_neg = create_mesh_object("PsiNegCloud", col)
obj_eta = create_mesh_object("EtaCloud", col)

set_geometry_nodes_instancing(obj_delta, inst_delta)
set_geometry_nodes_instancing(obj_psi_pos, inst_psi_pos)
set_geometry_nodes_instancing(obj_psi_neg, inst_psi_neg)
set_geometry_nodes_instancing(obj_eta, inst_eta)

p_delta, p_psi_pos, p_psi_neg, p_eta = sample_model(0.0)
set_points_as_vertices(obj_delta, p_delta)
set_points_as_vertices(obj_psi_pos, p_psi_pos)
set_points_as_vertices(obj_psi_neg, p_psi_neg)
set_points_as_vertices(obj_eta, p_eta)

add_text("Δ first difference", (-8.7, -4.7, 0))
add_text("ψ wave structure", (-1.9, -4.7, 0))
add_text("η + |ψ|² emergent form", (4.0, -4.7, 0))

cam = add_camera_and_lights()

bpy.ops.mesh.primitive_plane_add(size=28, location=(0, 0, -1.1))
floor = bpy.context.active_object
floor.data.materials.append(make_material("FloorMat", (0.06, 0.06, 0.08), alpha=1.0))

def update_frame(scene):
    frame = scene.frame_current
    t = 2 * pi * (frame - FRAME_START) / max(1, (FRAME_END - FRAME_START))
    p_delta, p_psi_pos, p_psi_neg, p_eta = sample_model(t)
    set_points_as_vertices(obj_delta, p_delta)
    set_points_as_vertices(obj_psi_pos, p_psi_pos)
    set_points_as_vertices(obj_psi_neg, p_psi_neg)
    set_points_as_vertices(obj_eta, p_eta)

    radius = 17.0
    ang = 0.35 + 0.6 * t / (2 * pi)
    cam.location = Vector((radius * cos(ang), -radius * sin(ang), 8.0))
    direction = Vector((0, 0, 0)) - cam.location
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

for h in list(bpy.app.handlers.frame_change_pre):
    if getattr(h, "__name__", "") == "update_frame":
        bpy.app.handlers.frame_change_pre.remove(h)

bpy.app.handlers.frame_change_pre.append(update_frame)
scene.frame_set(FRAME_START)

print("Delta-Orbital Blender scene created. Play the timeline.")

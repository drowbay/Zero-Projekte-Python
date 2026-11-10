# ============================================================
# Zustands-Energie Visualraum fuer Blender
# Erstellt eine animierte 3D-Szene direkt im Blender-Viewport.
# Nutzung in Blender:
#   1. Blender oeffnen
#   2. Scripting > Text > Open > diese Datei laden
#   3. Run Script klicken
#   4. Space/Play druecken oder Timeline abspielen
#
# Getestet fuer Blender 3.x/4.x API-Style.
# Keine externen Assets, keine PNGs, alles wird in Blender erzeugt.
# ============================================================

import bpy
import math
import random
from mathutils import Vector

# ----------------------------
# Szene leeren
# ----------------------------
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 240
scene.frame_set(1)
scene.render.fps = 24

# Eevee/Cycles Setup
scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in [i.identifier for i in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
try:
    scene.eevee.taa_render_samples = 64
except Exception:
    pass

# Units / Kamera
scene.unit_settings.system = 'METRIC'

# ----------------------------
# Materialien
# ----------------------------
def make_mat(name, color, emission=None, strength=1.0, alpha=1.0, blend=False):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        try:
            bsdf.inputs['Base Color'].default_value = color
        except Exception:
            pass
        try:
            bsdf.inputs['Alpha'].default_value = alpha
        except Exception:
            pass
        if emission is not None:
            # Blender 4 uses inputs by name. Guard for older versions.
            if 'Emission Color' in bsdf.inputs:
                bsdf.inputs['Emission Color'].default_value = emission
            if 'Emission Strength' in bsdf.inputs:
                bsdf.inputs['Emission Strength'].default_value = strength
            elif 'Emission' in bsdf.inputs:
                bsdf.inputs['Emission'].default_value = emission
    if blend or alpha < 1:
        mat.blend_method = 'BLEND'
        mat.use_screen_refraction = True
        mat.show_transparent_back = True
    return mat

mat_core = make_mat('Goldener Energiekern', (1.0, 0.62, 0.10, 1), (1.0, 0.55, 0.08, 1), 5.0)
mat_blue = make_mat('Cyan-Blau Feldlicht', (0.05, 0.45, 1.0, 1), (0.0, 0.6, 1.0, 1), 3.5)
mat_magenta = make_mat('Magenta Feldlicht', (1.0, 0.05, 0.8, 1), (1.0, 0.0, 0.7, 1), 3.5)
mat_gold_line = make_mat('Goldene Linien', (1.0, 0.65, 0.12, 1), (1.0, 0.5, 0.08, 1), 2.5)
mat_white = make_mat('Weisses Leuchten', (0.8, 0.95, 1.0, 1), (0.65, 0.9, 1.0, 1), 1.8)
mat_hull = make_mat('Transparente Zustandsraum-Huelle', (0.1, 0.45, 1.0, 0.13), (0.0, 0.25, 0.65, 1), 0.3, alpha=0.13, blend=True)
mat_dark = make_mat('Dunkler Panelstoff', (0.01, 0.015, 0.03, 1), None, 0.0)
mat_grid = make_mat('Gitter Cyan', (0.1, 0.75, 1.0, 1), (0.0, 0.4, 1.0, 1), 1.2)
mat_red = make_mat('Rot Konfinement', (1.0, 0.08, 0.05, 1), (1.0, 0.03, 0.02, 1), 2.8)
mat_green = make_mat('Gruen Kollektivmodus', (0.35, 1.0, 0.45, 1), (0.15, 1.0, 0.3, 1), 2.1)

# ----------------------------
# Helfer: Objekte
# ----------------------------
def add_uv_sphere(name, loc, scale, mat, segments=64, rings=32):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, radius=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    if mat:
        obj.data.materials.append(mat)
    return obj

def add_curve_polyline(name, points, mat, bevel=0.025, cyclic=False):
    curve = bpy.data.curves.new(name, type='CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 16
    curve.bevel_depth = bevel
    curve.bevel_resolution = 4
    poly = curve.splines.new('POLY')
    poly.points.add(len(points) - 1)
    for p, co in zip(poly.points, points):
        p.co = (co[0], co[1], co[2], 1)
    poly.use_cyclic_u = cyclic
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    if mat:
        obj.data.materials.append(mat)
    return obj

def add_torus(name, loc, major, minor, mat, seg=160, minseg=16):
    bpy.ops.mesh.primitive_torus_add(major_segments=seg, minor_segments=minseg, location=loc, major_radius=major, minor_radius=minor)
    obj = bpy.context.object
    obj.name = name
    if mat:
        obj.data.materials.append(mat)
    return obj

def add_text(name, text, loc, size, mat, align='CENTER'):
    bpy.ops.object.text_add(location=loc, rotation=(math.radians(65), 0, 0))
    obj = bpy.context.object
    obj.name = name
    obj.data.body = text
    obj.data.align_x = align
    obj.data.align_y = 'CENTER'
    obj.data.size = size
    obj.data.extrude = 0.01
    if mat:
        obj.data.materials.append(mat)
    return obj

# ----------------------------
# Hauptobjekte
# ----------------------------
core = add_uv_sphere('Stern: S* gespeicherter Zwischenzustand', (0, 0, 0), (0.38, 0.38, 0.38), mat_core)
core.keyframe_insert('scale', frame=1)
core.scale = (0.65, 0.65, 0.65)
core.keyframe_insert('scale', frame=120)
core.scale = (0.48, 0.48, 0.48)
core.keyframe_insert('scale', frame=240)

hull = add_uv_sphere('Hilbert-/Zustandsraum-Huelle', (0, 0, 0), (5.0, 5.0, 5.0), mat_hull, 96, 48)
hull.display_type = 'TEXTURED'
hull.keyframe_insert('rotation_euler', frame=1)
hull.rotation_euler[2] = math.radians(360)
hull.keyframe_insert('rotation_euler', frame=240)

# Elektronen / Teilchen links-rechts
e_left = add_uv_sphere('e- links: Eingang', (-6.2, 0, 0), (0.34,0.34,0.34), mat_blue)
e_right = add_uv_sphere('e- rechts: Eingang', (6.2, 0, 0), (0.34,0.34,0.34), mat_magenta)
for obj, x_start, x_end in [(e_left, -6.2, -2.0), (e_right, 6.2, 2.0)]:
    obj.keyframe_insert('location', frame=1)
    obj.location.x = x_end
    obj.keyframe_insert('location', frame=70)
    obj.location.x = x_start * 0.55
    obj.keyframe_insert('location', frame=240)

add_text('Label e links', 'e-', (-6.2, -0.05, 0.45), 0.32, mat_white)
add_text('Label e rechts', 'e-', (6.2, -0.05, 0.45), 0.32, mat_white)

# Achsen / Energiekanal
add_curve_polyline('Vertikale Energieachse blau', [(0,0,-5.2),(0,0,5.2)], mat_blue, bevel=0.035)
add_curve_polyline('Vertikale Energieachse gold', [(0.08,0,-5.2),(0.08,0,5.2)], mat_gold_line, bevel=0.018)
add_curve_polyline('Horizontale Kopplungsachse', [(-6.5,0,0),(6.5,0,0)], mat_magenta, bevel=0.025)

# Wellenfronten / Interferenzringe
for r in [0.8, 1.25, 1.7, 2.2, 2.8, 3.4, 4.1]:
    tor = add_torus(f'Interferenzring r={r}', (0,0,0), r, 0.008, mat_gold_line, seg=180, minseg=8)
    tor.rotation_euler[0] = math.radians(90)
    tor.keyframe_insert('scale', frame=1)
    tor.scale = (1.08, 1.08, 1.08)
    tor.keyframe_insert('scale', frame=120)
    tor.scale = (0.98, 0.98, 0.98)
    tor.keyframe_insert('scale', frame=240)

# Orbitale / spirographische Feldlinien
random.seed(4)
for i in range(18):
    pts = []
    phase = 2*math.pi*i/18
    for s in range(600):
        a = 2*math.pi*s/600
        Rr = 2.2 + 1.35*math.sin(3*a + phase)
        x = Rr*math.cos(a + 0.35*math.sin(phase))
        y = 0.75*Rr*math.sin(2*a + phase)
        z = 1.1*math.sin(a*2 + phase)
        # rotate around z
        rot = phase
        xr = x*math.cos(rot)-y*math.sin(rot)
        yr = x*math.sin(rot)+y*math.cos(rot)
        pts.append((xr, yr, z))
    mat = [mat_blue, mat_magenta, mat_gold_line, mat_green][i % 4]
    line = add_curve_polyline(f'Orbitale Feldlinie {i+1}', pts, mat, bevel=0.012, cyclic=True)
    line.keyframe_insert('rotation_euler', frame=1)
    line.rotation_euler[2] += math.radians(120 + i*8)
    line.rotation_euler[0] += math.radians(30*math.sin(i))
    line.keyframe_insert('rotation_euler', frame=240)

# Zustandsraum-Knoten auf Kugel
node_objs = []
for i in range(16):
    theta = math.acos(1 - 2*(i+0.5)/16)
    phi = math.pi * (1 + 5**0.5) * i
    radius = 4.35
    loc = (radius*math.sin(theta)*math.cos(phi), radius*math.sin(theta)*math.sin(phi), radius*math.cos(theta))
    mat = [mat_blue, mat_magenta, mat_gold_line, mat_green][i % 4]
    node = add_uv_sphere(f'Zustandsknoten {i+1}', loc, (0.08,0.08,0.08), mat, 24, 12)
    node_objs.append(node)

# Verbindungsnetz zwischen Knoten
for i in range(len(node_objs)):
    for j in [(i+3)%16, (i+5)%16]:
        p1 = node_objs[i].location
        p2 = node_objs[j].location
        add_curve_polyline(f'Verschraenkung {i+1}-{j+1}', [p1, p2], mat_grid, bevel=0.006)

# Konfinement / Energiespeicher-Torus als reife Phase
for i in range(6):
    tor = add_torus(f'Konfinement-Spule {i+1}', (0,0,0), 3.05, 0.055, mat_red if i % 2 == 0 else mat_blue, 180, 16)
    tor.rotation_euler[0] = math.radians(90)
    tor.rotation_euler[1] = math.radians(i*30)
    tor.rotation_euler[2] = math.radians(i*18)
    tor.keyframe_insert('rotation_euler', frame=1)
    tor.rotation_euler[2] += math.radians(240)
    tor.keyframe_insert('rotation_euler', frame=240)

# Auskopplungswellen rechts
for k in range(5):
    pts = []
    for s in range(220):
        x = 3.5 + s*0.025
        y = -1.2 + k*0.6 + 0.18*math.sin(s*0.2)
        z = -2.7 + 0.12*math.cos(s*0.18 + k)
        pts.append((x,y,z))
    add_curve_polyline(f'Energieauskopplung Welle {k+1}', pts, mat_gold_line, bevel=0.015)

# ----------------------------
# HUD Panels als einfache 3D-Tafeln
# ----------------------------
def add_panel(name, loc, scale, title, lines):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    panel = bpy.context.object
    panel.name = name
    panel.scale = (scale[0], 0.03, scale[1])
    panel.data.materials.append(mat_dark)
    add_text(name+'_title', title, (loc[0], loc[1]-0.08, loc[2]+scale[1]*0.78), 0.18, mat_grid)
    for idx, ln in enumerate(lines):
        add_text(name+f'_line_{idx}', ln, (loc[0]-scale[0]*0.75, loc[1]-0.09, loc[2]+scale[1]*0.35-idx*0.28), 0.11, mat_white, align='LEFT')
    return panel

add_panel('Panel Spektrum', (-5.7, 2.85, 3.4), (1.25,0.75), 'SPEKTROGRAMM', ['Energieband', 'Moden h1..h4'])
add_panel('Panel Zustand', (5.7, 2.85, 3.4), (1.25,0.75), 'ZUSTANDSRAUM', ['Dimension ~ 2^n', 'Knoten = Moden'])
add_panel('Panel Speicher', (5.7, 2.85, -3.25), (1.25,0.9), 'ENERGIESPEICHER', ['S0 + Ein -> S*', 'S* -> S0 + Eout', 'eta = Eout / Ein'])
add_panel('Panel Modell', (-5.7, 2.85, -3.25), (1.25,0.9), 'MODELLKERN', ['Feld + Geometrie', 'Zwischenzustand Z', 'Messung M = Pi[Z]'])

# Beschriftungen unten / Phasenmarken
phase_label = add_text('Phasenlabel', 'Phase 1-4: Kopplung -> Interferenz -> Zustandsraum -> Konfinement', (0, -5.45, -4.5), 0.22, mat_white)
project_label = add_text('Projektlabel', 'ZES-Modell: zustandsbasierte Energiespeicher / Visualraum', (0, -5.45, -5.0), 0.16, mat_grid)

# ----------------------------
# Licht & Welt
# ----------------------------
bpy.ops.object.light_add(type='POINT', location=(0, -3, 3))
light = bpy.context.object
light.name = 'Hauptlicht Kernreflex'
light.data.energy = 650
light.data.color = (0.5, 0.8, 1.0)

bpy.ops.object.light_add(type='POINT', location=(0, 0, 0))
cl = bpy.context.object
cl.name = 'Zentrales Energielicht'
cl.data.energy = 1200
cl.data.color = (1.0, 0.55, 0.15)

bpy.ops.object.camera_add(location=(0, -12.5, 6.1), rotation=(math.radians(62), 0, 0))
cam = bpy.context.object
scene.camera = cam
cam.name = 'Kamera Visualisierungsraum'
try:
    cam.data.lens = 28
except Exception:
    pass

# Bloom / Color Management
try:
    scene.eevee.use_bloom = True
    scene.eevee.bloom_intensity = 0.18
    scene.eevee.bloom_radius = 6.0
except Exception:
    pass

scene.view_settings.view_transform = 'Filmic'
scene.view_settings.look = 'High Contrast'
scene.view_settings.exposure = 0
scene.view_settings.gamma = 1

# Dunkle Welt
bpy.context.scene.world = bpy.data.worlds.new('Dunkler Visualraum') if bpy.context.scene.world is None else bpy.context.scene.world
bpy.context.scene.world.color = (0,0,0)

# ----------------------------
# Animation: Sichtbarkeit/Skalierung nach Phasen
# ----------------------------
# Gruppen grob anhand Namen einfaden
for obj in bpy.context.scene.objects:
    if obj.type in {'CURVE','MESH','FONT'}:
        # keyframes fuer Rotation vieler Objekte, leichte organische Bewegung
        if obj.name.startswith('Zustandsknoten'):
            obj.keyframe_insert('scale', frame=1)
            obj.scale *= 1.35
            obj.keyframe_insert('scale', frame=150)
            obj.scale *= 0.9
            obj.keyframe_insert('scale', frame=240)

# Kamerafahrt leicht hinein
cam.keyframe_insert('location', frame=1)
cam.location = (0, -10.8, 5.2)
cam.keyframe_insert('location', frame=240)

# Datei speichern, wenn moeglich im gleichen Pfad wie Script oder Home
# Hinweis: Dieser Save funktioniert nur, wenn Script innerhalb Blender ausgefuehrt wird.
try:
    bpy.ops.wm.save_as_mainfile(filepath='zustands_energie_visualraum.blend')
except Exception as exc:
    print('Hinweis: .blend konnte nicht automatisch gespeichert werden:', exc)

print('\nFertig: Zustands-Energie Visualraum wurde in der aktuellen Blender-Szene erstellt.')
print('Timeline abspielen: Leertaste oder Play in der Timeline.')
print('Optional speichern: File > Save As > zustands_energie_visualraum.blend')

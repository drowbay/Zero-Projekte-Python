# Phasenherz-Kern / Zustandsspeicher - Blender Python Script
# Erstellt ein stilisiertes 3D-Gerät inspiriert vom hochgeladenen Bild.
# Nutzung: Blender öffnen -> Scripting -> New -> Script einfügen -> Run Script
# Getestet für Blender 3.x/4.x Grundfunktionen.

import bpy
import math
from mathutils import Vector

# -----------------------------
# Szene leeren
# -----------------------------
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# -----------------------------
# Hilfsfunktionen
# -----------------------------
def mat(name, color, metallic=0.0, roughness=0.35, emission=False, strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        if emission:
            try:
                bsdf.inputs['Base Color'].default_value = color
                bsdf.inputs['Emission Color'].default_value = color
                bsdf.inputs['Emission Strength'].default_value = strength
            except Exception:
                pass
        else:
            bsdf.inputs['Base Color'].default_value = color
        if 'Metallic' in bsdf.inputs:
            bsdf.inputs['Metallic'].default_value = metallic
        if 'Roughness' in bsdf.inputs:
            bsdf.inputs['Roughness'].default_value = roughness
    return m

mat_dark = mat('Dunkles Titan-Gehäuse', (0.035, 0.038, 0.042, 1), 0.75, 0.22)
mat_edge = mat('Anthrazit Kantenpanzer', (0.10, 0.105, 0.11, 1), 0.85, 0.18)
mat_plate = mat('Graphit Innenplatten', (0.055, 0.060, 0.067, 1), 0.65, 0.30)
mat_copper = mat('Kupferleitungen / Spulen', (0.78, 0.33, 0.10, 1), 0.95, 0.20)
mat_glow = mat('Phasenherz Orange Glow', (1.0, 0.35, 0.02, 1), 0.0, 0.10, True, 6.0)
mat_glow2 = mat('Sanfter Sekundär-Glow', (1.0, 0.58, 0.12, 1), 0.0, 0.15, True, 2.5)
mat_label = mat('Beschriftung Hellgrau', (0.82, 0.82, 0.78, 1), 0.0, 0.65)


def bevel(obj, amount=0.04, segments=2):
    mod = obj.modifiers.new('weiche Fasen', 'BEVEL')
    mod.width = amount
    mod.segments = segments
    mod.affect = 'EDGES'
    obj.modifiers.new('gewichtete Normalen', 'WEIGHTED_NORMAL')
    return obj


def cube(name, loc, scale, material):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        o.data.materials.append(material)
    return bevel(o, 0.035, 2)


def cyl(name, loc, radius, depth, material, vertices=64, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    if material:
        o.data.materials.append(material)
    return bevel(o, 0.015, 2)


def torus(name, loc, major, minor, material, rot=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_segments=128, minor_segments=16, major_radius=major, minor_radius=minor, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    if material:
        o.data.materials.append(material)
    return o


def add_text(name, text, loc, size=0.12, rot=(math.radians(90),0,0), material=mat_label, align='CENTER'):
    bpy.ops.object.text_add(location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.data.body = text
    o.data.align_x = align
    o.data.align_y = 'CENTER'
    o.data.size = size
    o.data.extrude = 0.002
    if material:
        o.data.materials.append(material)
    return o

# -----------------------------
# Grundplatte / Panzergehäuse
# -----------------------------
base = cube('Schutzgehäuse - schwere Außenplatte', (0,0,0), (5.0, 0.30, 7.0), mat_dark)

# Octagonaler Look durch Eckpanzer
for sx in [-1, 1]:
    for sz in [-1, 1]:
        corner = cube('abgeschrägte Eckpanzerung', (sx*2.18, -0.02, sz*3.05), (0.95,0.38,0.65), mat_edge)
        corner.rotation_euler[1] = math.radians(0)
        corner.rotation_euler[2] = math.radians(0)
        corner.rotation_euler[1] = math.radians(0)

# Seitenrahmen
cube('linker Stützrahmen', (-2.55,-0.08,0), (0.36,0.42,5.45), mat_edge)
cube('rechter Stützrahmen', (2.55,-0.08,0), (0.36,0.42,5.45), mat_edge)
cube('oberer Halterahmen', (0,-0.08,3.45), (3.65,0.42,0.34), mat_edge)
cube('unterer Halterahmen', (0,-0.08,-3.45), (3.65,0.42,0.34), mat_edge)

# Innenplatten und Layer
for i, s in enumerate([4.05, 3.35, 2.65]):
    cube(f'Innenplatte Layer {i+1}', (0, -0.20-i*0.015, 0), (s,0.18, s*1.18), mat_plate)

# -----------------------------
# Phasenherz-Kern
# -----------------------------
torus('Metamaterial-Hülle Ring außen', (0,-0.48,0), 1.25, 0.075, mat_copper, (math.radians(90),0,0))
torus('Isolationsverbund Ring innen', (0,-0.50,0), 0.92, 0.045, mat_edge, (math.radians(90),0,0))
torus('Emissionsfeld Resonanzring', (0,-0.55,0), 0.72, 0.025, mat_glow2, (math.radians(90),0,0))

# Leuchtender Kristall / Zustandkern
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.62, location=(0,-0.72,0))
core = bpy.context.object
core.name = 'Zustandskern S* - leuchtender Phasenkristall'
core.scale.z = 1.18
core.rotation_euler[1] = math.radians(15)
core.data.materials.append(mat_glow)
bevel(core, 0.01, 1)

# Innere diagonale Lichtlamellen
for angle in [-38, -19, 0, 19, 38]:
    strip = cube('diagonale Energielamelle im Kern', (0,-0.93,0), (0.08,0.035,1.32), mat_glow2)
    strip.rotation_euler[1] = math.radians(angle)
    strip.rotation_euler[2] = math.radians(34)

# Kleine Halteklammern um Kern
for a in range(0,360,45):
    r = 1.18
    x = math.cos(math.radians(a))*r
    z = math.sin(math.radians(a))*r
    clamp = cube('Kern-Halteklammer', (x,-0.62,z), (0.34,0.28,0.16), mat_edge)
    clamp.rotation_euler[1] = -math.radians(a)

# -----------------------------
# Primär-/Sekundärspulen oben/unten
# -----------------------------
for z in [1.95, -1.95]:
    cyl('Kupfer-Hochfrequenzspule', (0,-0.63,z), 0.33, 0.75, mat_copper, 64, (math.radians(90),0,0))
    for offset in [-0.28,-0.14,0,0.14,0.28]:
        torus('sichtbare Spulenwicklung', (0,-0.99+offset*0.05,z), 0.34+abs(offset)*0.05, 0.018, mat_copper, (math.radians(90),0,0))
    cube('Spulenhalter links/rechts', (-0.56,-0.55,z), (0.22,0.33,0.80), mat_edge)
    cube('Spulenhalter links/rechts', (0.56,-0.55,z), (0.22,0.33,0.80), mat_edge)

# -----------------------------
# Leitungen: Kupferbahnen und Feldkäfig
# -----------------------------
for sx in [-1,1]:
    # vertikale Leitungssegmente
    cube('Kupfer Energiebus vertikal', (sx*1.82,-0.58,0), (0.09,0.12,4.15), mat_copper)
    cube('Kupfer Energiebus oben', (sx*1.10,-0.58,2.25), (1.45,0.12,0.09), mat_copper)
    cube('Kupfer Energiebus unten', (sx*1.10,-0.58,-2.25), (1.45,0.12,0.09), mat_copper)
    # dunkle Schutzleisten daneben
    cube('Feldkäfig Schutzkanal', (sx*2.05,-0.52,0), (0.16,0.18,4.65), mat_edge)

# Symmetrische Tech-Kacheln
for sx in [-1,1]:
    for z in [-2.7,-1.35,1.35,2.7]:
        cube('modulare Strukturmatrix-Kachel', (sx*1.35,-0.67,z), (0.52,0.20,0.22), mat_plate)
        cube('orange Statusmarker', (sx*1.35,-0.82,z), (0.23,0.035,0.055), mat_glow2)

# Schrauben / Nieten
for sx in [-1,1]:
    for z in [-3.1,-2.1,-1.05,1.05,2.1,3.1]:
        cyl('Stahlbolzen', (sx*2.25,-0.34,z), 0.07, 0.035, mat_edge, 32, (math.radians(90),0,0))
for x in [-1.7,-0.85,0.85,1.7]:
    for z in [-3.05,3.05]:
        cyl('Rahmenbolzen', (x,-0.34,z), 0.06, 0.035, mat_edge, 32, (math.radians(90),0,0))

# -----------------------------
# Beschriftungen direkt am Modell
# -----------------------------
add_text('Titel', 'PHASENHERZ-KERN', (-2.35,-1.03,3.95), 0.22, align='LEFT')
add_text('Untertitel', 'vergrößerter Querschnitt / Zustandskern', (-2.35,-1.03,3.62), 0.10, align='LEFT')

labels_left = [
    ('SCHUTZGEHÄUSE', -2.95, 2.65),
    ('FELDKÄFIG', -2.95, 1.75),
    ('PRIMÄRSPULE', -2.95, 0.85),
    ('ISOLATIONSVERBUND', -2.95, 0.05),
    ('SEKUNDÄRSPULE', -2.95, -0.85),
    ('KÜHLRING', -2.95, -1.75),
    ('STÜTZRAHMEN', -2.95, -2.65),
]
for text, x, z in labels_left:
    add_text('Label '+text, text, (x,-1.02,z), 0.075, align='LEFT')
    cube('feine Callout Linie', (x+0.88,-1.00,z), (1.15,0.01,0.012), mat_label)

labels_right = [
    ('INDUKTIVE KOPPLUNG', 1.85, 2.45),
    ('METAMATERIAL-HÜLLE', 1.85, 1.45),
    ('ZUSTANDSKERN S*', 1.85, 0.45),
    ('QUANTENBINDUNG', 1.85, -0.45),
    ('EMISSIONSFELD', 1.85, -1.45),
    ('UNTERER HALTERAHMEN', 1.85, -2.45),
]
for text, x, z in labels_right:
    add_text('Label '+text, text, (x,-1.02,z), 0.075, align='LEFT')
    cube('feine Callout Linie', (x-0.58,-1.00,z), (0.95,0.01,0.012), mat_label)

# Zustandsdiagramm klein rechts unten im Raum
add_text('Zustandsdiagramm', 'S0  ⇄  S*', (2.95,-1.02,-3.45), 0.13)
add_text('Energiehinweis', 'Aktivierung / Deaktivierung\nkontrollierte Abstrahlung', (2.95,-1.02,-3.72), 0.065)

# -----------------------------
# Licht, Kamera, Glow
# -----------------------------
bpy.ops.object.light_add(type='AREA', location=(0,-4,4))
l = bpy.context.object
l.name = 'große Softbox'
l.data.energy = 450
l.data.size = 5

bpy.ops.object.light_add(type='POINT', location=(0,-1.8,0))
pl = bpy.context.object
pl.name = 'oranger Kernschein'
pl.data.color = (1.0,0.45,0.12)
pl.data.energy = 800
pl.data.shadow_soft_size = 4

bpy.ops.object.camera_add(location=(0,-10,0.35), rotation=(math.radians(88),0,0))
bpy.context.scene.camera = bpy.context.object

# Render-Einstellungen
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 96
bpy.context.scene.view_settings.view_transform = 'Filmic'
bpy.context.scene.view_settings.look = 'Medium High Contrast'
bpy.context.scene.eevee.taa_render_samples = 64 if hasattr(bpy.context.scene, 'eevee') else 16

# Bloom für Eevee, falls verfügbar
if hasattr(bpy.context.scene, 'eevee'):
    try:
        bpy.context.scene.eevee.use_bloom = True
        bpy.context.scene.eevee.bloom_intensity = 0.18
        bpy.context.scene.eevee.bloom_radius = 6.0
    except Exception:
        pass

# Kamera auf orthografisch wie technischer Blueprint
bpy.context.scene.camera.data.type = 'ORTHO'
bpy.context.scene.camera.data.ortho_scale = 8.8
bpy.context.scene.render.resolution_x = 1600
bpy.context.scene.render.resolution_y = 2200

# Ursprung sauber setzen
for obj in bpy.context.scene.objects:
    obj.select_set(False)

print('Fertig: Phasenherz-Kern Modell erzeugt. Tipp: Für mehr Glow in Eevee Bloom aktivieren oder in Cycles mit Compositor Glare nutzen.')

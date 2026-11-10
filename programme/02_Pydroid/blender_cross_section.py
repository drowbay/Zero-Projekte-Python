
import bpy
import math

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Materials
def make_mat(name, color):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    return mat

mat_plasma = make_mat("Plasma", (0.2, 0.6, 1.0))
mat_carbon = make_mat("Carbon", (0.05, 0.05, 0.05))
mat_copper = make_mat("Copper", (0.8, 0.4, 0.2))
mat_tungsten = make_mat("Tungsten", (0.7, 0.7, 0.7))

# Create rings (cross-section layers)
def create_ring(radius, thickness, mat):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=radius,
        minor_radius=thickness,
        location=(0,0,0)
    )
    obj = bpy.context.object
    obj.data.materials.append(mat)
    return obj

# Plasma core
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.8, location=(0,0,0))
plasma = bpy.context.object
plasma.data.materials.append(mat_plasma)

# Layers
carbon = create_ring(1.2, 0.1, mat_carbon)
copper = create_ring(1.5, 0.15, mat_copper)
tungsten = create_ring(1.9, 0.1, mat_tungsten)

# Add spikes (simplified)
for i in range(20):
    angle = i * (2*math.pi/20)
    x = math.cos(angle)*2.1
    y = math.sin(angle)*2.1
    
    bpy.ops.mesh.primitive_cone_add(radius1=0.05, depth=0.3, location=(x,y,0))
    spike = bpy.context.object
    spike.rotation_euler[1] = math.pi/2
    spike.rotation_euler[2] = angle
    spike.data.materials.append(mat_tungsten)

# Camera
bpy.ops.object.camera_add(location=(4, -4, 3), rotation=(1.1, 0, 0.8))

# Light
bpy.ops.object.light_add(type='POINT', location=(2, -2, 3))

print("Cross-section scene created")

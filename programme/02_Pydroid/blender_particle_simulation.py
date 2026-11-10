
import bpy
import random
import math

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

PARTICLE_COUNT = 35
WIDTH = 10
HEIGHT = 10

ATTRACTION_RADIUS = 3.0
REPULSION_RADIUS = 0.8
DANGER_RADIUS = 0.35

ATTRACTION_FORCE = 0.02
REPULSION_FORCE = 0.2
FRICTION = 0.96

particles = []
velocities = []

# Create particles (spheres)
for i in range(PARTICLE_COUNT):
    x = random.random() * WIDTH - WIDTH/2
    y = random.random() * HEIGHT - HEIGHT/2
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(x, y, 0))
    obj = bpy.context.object
    obj.name = f"Particle_{i}"
    
    particles.append(obj)
    velocities.append([random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1)])

def distance(a, b):
    dx = a.x - b.x
    dy = a.y - b.y
    return math.sqrt(dx*dx + dy*dy)

# Animate
for frame in range(1, 200):
    forces = [[0,0] for _ in range(PARTICLE_COUNT)]
    
    for i in range(PARTICLE_COUNT):
        for j in range(i+1, PARTICLE_COUNT):
            p1 = particles[i].location
            p2 = particles[j].location
            
            dx = p2.x - p1.x
            dy = p2.y - p1.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist == 0:
                continue
            
            dirx = dx / dist
            diry = dy / dist
            
            if dist < REPULSION_RADIUS:
                strength = REPULSION_FORCE * (REPULSION_RADIUS - dist)
                forces[i][0] -= dirx * strength
                forces[i][1] -= diry * strength
                forces[j][0] += dirx * strength
                forces[j][1] += diry * strength
                
            elif dist < ATTRACTION_RADIUS:
                strength = ATTRACTION_FORCE * (ATTRACTION_RADIUS - dist)
                forces[i][0] += dirx * strength
                forces[i][1] += diry * strength
                forces[j][0] -= dirx * strength
                forces[j][1] -= diry * strength
    
    # Apply movement
    for i in range(PARTICLE_COUNT):
        velocities[i][0] += forces[i][0]
        velocities[i][1] += forces[i][1]
        
        velocities[i][0] *= FRICTION
        velocities[i][1] *= FRICTION
        
        loc = particles[i].location
        loc.x += velocities[i][0]
        loc.y += velocities[i][1]
        
        # Bounce walls
        if loc.x < -WIDTH/2 or loc.x > WIDTH/2:
            velocities[i][0] *= -1
        if loc.y < -HEIGHT/2 or loc.y > HEIGHT/2:
            velocities[i][1] *= -1
        
        particles[i].keyframe_insert(data_path="location", frame=frame)

print("Simulation baked!")

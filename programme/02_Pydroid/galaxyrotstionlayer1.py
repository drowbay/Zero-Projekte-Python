import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# -----------------------------
# PARAMETER
# -----------------------------
G = 1.0                 # vereinfachte Gravitationskonstante
M = 500.0               # zentrale Masse der Galaxie
grid_size = 120         # Auflösung der Karte
space_size = 20.0       # Größe des Raums [-space_size, +space_size]
num_particles = 80      # Anzahl der Testteilchen
dt = 0.03               # Zeitschritt
softening = 0.8         # vermeidet Singularität im Zentrum

# -----------------------------
# GRID (RAUMKARTE)
# -----------------------------
x = np.linspace(-space_size, space_size, grid_size)
y = np.linspace(-space_size, space_size, grid_size)
X, Y = np.meshgrid(x, y)

R = np.sqrt(X**2 + Y**2 + softening**2)

# -----------------------------
# GRAVITATIONSFELD
# -----------------------------
# Potential grob: -GM/r
potential = -G * M / R

# Feldstärke grob: GM/r^2
gravity_strength = G * M / (R**2)

# -----------------------------
# ROTATIONSFELD
# -----------------------------
# Tangentiale Geschwindigkeit für eine grobe Galaxienrotation:
# v ~ sqrt(GM/r)
v_mag = np.sqrt(G * M / R)

# Tangentialrichtung:
# (vx, vy) = (-y/r, x/r) * v
VX = -Y / R * v_mag
VY =  X / R * v_mag

# Für schönere Pfeile ausdünnen
step = 8
Xq = X[::step, ::step]
Yq = Y[::step, ::step]
VXq = VX[::step, ::step]
VYq = VY[::step, ::step]

# -----------------------------
# TESTTEILCHEN
# -----------------------------
# Zufällige Startwinkel und Radien
angles = np.random.uniform(0, 2*np.pi, num_particles)
radii = np.random.uniform(3.0, 14.0, num_particles)

px = radii * np.cos(angles)
py = radii * np.sin(angles)

# Anfangsgeschwindigkeit tangential
pr = np.sqrt(px**2 + py**2 + softening**2)
pv_mag = np.sqrt(G * M / pr)

pvx = -py / pr * pv_mag
pvy =  px / pr * pv_mag

# -----------------------------
# FIGURE
# -----------------------------
fig, ax = plt.subplots(figsize=(8, 8), facecolor='black')
ax.set_facecolor('black')

# Heatmap
im = ax.imshow(
    gravity_strength,
    extent=[-space_size, space_size, -space_size, space_size],
    origin='lower',
    cmap='inferno'
)

# Pfeile
quiv = ax.quiver(
    Xq, Yq, VXq, VYq,
    color='cyan',
    alpha=0.7,
    scale=120
)

# Zentrum
ax.scatter(0, 0, s=120, c='white', marker='o', label='Galaxienzentrum')

# Testteilchen
particles = ax.scatter(px, py, s=10, c='white', alpha=0.9)

ax.set_title("MS Space Field Viewer v1\nGravitation + Rotation", color='white')
ax.set_xlim(-space_size, space_size)
ax.set_ylim(-space_size, space_size)
ax.tick_params(colors='white')

# -----------------------------
# UPDATE
# -----------------------------
def update(frame):
    global px, py, pvx, pvy

    # Abstand zum Zentrum
    r = np.sqrt(px**2 + py**2 + softening**2)

    # Gravitationsbeschleunigung zum Zentrum
    ax_grav = -G * M * px / (r**3)
    ay_grav = -G * M * py / (r**3)

    # Euler-Integration
    pvx += ax_grav * dt
    pvy += ay_grav * dt

    px += pvx * dt
    py += pvy * dt

    # Positionen aktualisieren
    particles.set_offsets(np.column_stack([px, py]))

    return [particles]

# -----------------------------
# START
# -----------------------------
ani = animation.FuncAnimation(
    fig, update, frames=400, interval=30, blit=True
)

plt.tight_layout()
plt.show()
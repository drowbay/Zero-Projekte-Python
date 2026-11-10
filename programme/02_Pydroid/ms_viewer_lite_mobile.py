
# MS Viewer v5.5 LITE — Mobile Friendly Version
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

np.random.seed(7)

G = 1.0
M = 200.0
grid_size = 80
space_size = 12.0
num_particles = 60
dt = 0.03
softening = 1.0
frames = 120

x = np.linspace(-space_size, space_size, grid_size)
y = np.linspace(-space_size, space_size, grid_size)
X, Y = np.meshgrid(x, y)
R = np.sqrt(X**2 + Y**2 + softening**2)

def normalize(arr):
    arr = arr - np.min(arr)
    return arr / (np.max(arr) + 1e-9)

potential = -G * M / R
energy_field = normalize(G * M / (R**2))

angles = np.random.uniform(0, 2*np.pi, num_particles)
radii = np.random.uniform(2.0, 8.0, num_particles)

px = radii * np.cos(angles)
py = radii * np.sin(angles)

pr = np.sqrt(px**2 + py**2 + softening**2)
pv = np.sqrt(G * M / pr)

pvx = -py / pr * pv
pvy =  px / pr * pv

fig, ax = plt.subplots(figsize=(6,6))
ax.set_facecolor("black")
ax.axis("off")

im = ax.imshow(energy_field, extent=[-space_size, space_size, -space_size, space_size], cmap="inferno", alpha=0.6)
particles = ax.scatter(px, py, s=6, c="white")

def update(frame):
    global px, py, pvx, pvy

    r = np.sqrt(px**2 + py**2 + softening**2)
    ax_g = -G * M * px / (r**3)
    ay_g = -G * M * py / (r**3)

    pvx += ax_g * dt
    pvy += ay_g * dt

    px += pvx * dt
    py += pvy * dt

    particles.set_offsets(np.column_stack([px, py]))
    return particles,

ani = animation.FuncAnimation(fig, update, frames=frames, interval=40)

plt.show()

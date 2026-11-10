import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

np.random.seed(7)

# -----------------------------
# PARAMETER
# -----------------------------
G = 1.0
WIDTH = HEIGHT = 48.0
space_size = 24.0

num_particles = 120
dt = 0.018
softening = 0.9
frames = 900

# Nähe-Zonen
ATTRACTION_RADIUS = 7.0
REPULSION_RADIUS = 2.2
DANGER_RADIUS = 0.9

ATTRACTION_FORCE = 0.006
REPULSION_FORCE = 0.055
FRICTION = 0.985

dark_energy_strength = 0.006

cores = [
    (0.0, 0.0, 520.0),
    (-8.0, 6.0, 120.0),
    (9.0, -7.0, 105.0),
]

# -----------------------------
# PARTICLES
# -----------------------------
angles = np.random.uniform(0, 2*np.pi, num_particles)
radii = np.random.uniform(4.0, 18.0, num_particles)

positions = np.column_stack([
    radii * np.cos(angles),
    0.72 * radii * np.sin(angles)
])

velocities = np.zeros_like(positions)

for i in range(num_particles):
    x, y = positions[i]
    r = np.sqrt(x*x + y*y + softening**2)
    v = np.sqrt(G * 520.0 / r)
    velocities[i] = [-y / r * v, x / r * v]

velocities += np.random.normal(0, 0.03, velocities.shape)

# -----------------------------
# FIELD BACKGROUND
# -----------------------------
grid_size = 140
x = np.linspace(-space_size, space_size, grid_size)
y = np.linspace(-space_size, space_size, grid_size)
X, Y = np.meshgrid(x, y)

def normalize(arr):
    arr = np.array(arr, dtype=float)
    arr = arr - np.min(arr)
    return arr / (np.max(arr) + 1e-9)

potential = np.zeros_like(X)
gravity_strength = np.zeros_like(X)

for cx, cy, mass in cores:
    dx = X - cx
    dy = Y - cy
    R = np.sqrt(dx**2 + dy**2 + softening**2)

    potential += -G * mass / R
    gravity_strength += G * mass / (R**2)

cmb_noise = normalize(np.random.normal(0, 1, (grid_size, grid_size)))

cosmic_field = normalize(
    0.65 * normalize(gravity_strength) +
    0.20 * normalize(np.abs(potential)) +
    0.15 * cmb_noise
)

# -----------------------------
# FIGURE
# -----------------------------
fig, ax = plt.subplots(figsize=(9, 9), facecolor="black")
ax.set_facecolor("black")

im = ax.imshow(
    cosmic_field,
    extent=[-space_size, space_size, -space_size, space_size],
    origin="lower",
    cmap="magma",
    alpha=0.55
)

danger_text = ax.text(
    -23, 22,
    "",
    color="white",
    fontsize=10,
    va="top",
    bbox=dict(facecolor="black", alpha=0.55)
)

# -----------------------------
# HELPERS
# -----------------------------
def distance(a, b):
    return np.linalg.norm(a - b)

# -----------------------------
# UPDATE
# -----------------------------
def update(frame):
    global positions, velocities

    forces = np.zeros_like(positions)
    danger_events = []
    repulsion_events = []
    attraction_events = []

    # Gravitation durch Kerne
    for i in range(num_particles):
        x, y = positions[i]

        ax_g = 0.0
        ay_g = 0.0

        for cx, cy, mass in cores:
            dx = x - cx
            dy = y - cy
            r = np.sqrt(dx*dx + dy*dy + softening**2)

            ax_g += -G * mass * dx / (r**3)
            ay_g += -G * mass * dy / (r**3)

        # Dark Energy Drift nach außen
        r0 = np.sqrt(x*x + y*y + softening**2)
        ax_g += dark_energy_strength * x / r0
        ay_g += dark_energy_strength * y / r0

        forces[i] += np.array([ax_g, ay_g]) * 0.045

    # Näheanalyse zwischen Teilchen
    for i in range(num_particles):
        for j in range(i + 1, num_particles):
            delta = positions[j] - positions[i]
            dist = np.linalg.norm(delta)

            if dist == 0:
                continue

            direction = delta / dist

            if dist < REPULSION_RADIUS:
                strength = REPULSION_FORCE * (REPULSION_RADIUS - dist)
                forces[i] -= direction * strength
                forces[j] += direction * strength
                repulsion_events.append((i, j, dist))

            elif dist < ATTRACTION_RADIUS:
                strength = ATTRACTION_FORCE * (ATTRACTION_RADIUS - dist)
                forces[i] += direction * strength
                forces[j] -= direction * strength
                attraction_events.append((i, j, dist))

            if dist < DANGER_RADIUS:
                danger_events.append((i, j, dist))

    velocities += forces
    velocities *= FRICTION
    positions += velocities * dt * 10.0

    # Grenzen / Reset
    r_out = np.sqrt(positions[:, 0]**2 + positions[:, 1]**2)
    reset = r_out > 23.0

    if np.any(reset):
        new_angles = np.random.uniform(0, 2*np.pi, np.sum(reset))
        new_radii = np.random.uniform(8.0, 18.0, np.sum(reset))
        positions[reset, 0] = new_radii * np.cos(new_angles)
        positions[reset, 1] = 0.72 * new_radii * np.sin(new_angles)
        velocities[reset] *= 0.0

    # Zeichnen
    ax.clear()
    ax.set_facecolor("black")
    ax.set_xlim(-space_size, space_size)
    ax.set_ylim(-space_size, space_size)
    ax.set_aspect("equal")
    ax.axis("off")

    ax.imshow(
        cosmic_field,
        extent=[-space_size, space_size, -space_size, space_size],
        origin="lower",
        cmap="magma",
        alpha=0.55
    )

    # Kerne
    for cx, cy, mass in cores:
        ax.scatter(cx, cy, s=80 + mass * 0.12, c="white", alpha=0.95)

    # Fokus-Teilchen
    focus = 0
    fx, fy = positions[focus]

    attraction_circle = plt.Circle(
        (fx, fy), ATTRACTION_RADIUS,
        fill=False, linestyle="--", linewidth=1.0,
        color="deepskyblue", alpha=0.75
    )
    repulsion_circle = plt.Circle(
        (fx, fy), REPULSION_RADIUS,
        fill=False, linestyle="-", linewidth=2.0,
        color="orange", alpha=0.85
    )
    danger_circle = plt.Circle(
        (fx, fy), DANGER_RADIUS,
        fill=False, linestyle="-", linewidth=3.0,
        color="red", alpha=0.95
    )

    ax.add_patch(attraction_circle)
    ax.add_patch(repulsion_circle)
    ax.add_patch(danger_circle)

    # Verbindungslinien
    for i in range(num_particles):
        for j in range(i + 1, num_particles):
            dist = distance(positions[i], positions[j])

            if dist < DANGER_RADIUS:
                ax.plot(
                    [positions[i, 0], positions[j, 0]],
                    [positions[i, 1], positions[j, 1]],
                    color="red",
                    linewidth=2.0,
                    alpha=0.9
                )
            elif dist < REPULSION_RADIUS:
                ax.plot(
                    [positions[i, 0], positions[j, 0]],
                    [positions[i, 1], positions[j, 1]],
                    color="orange",
                    linewidth=1.1,
                    alpha=0.65
                )
            elif dist < ATTRACTION_RADIUS:
                ax.plot(
                    [positions[i, 0], positions[j, 0]],
                    [positions[i, 1], positions[j, 1]],
                    color="deepskyblue",
                    linewidth=0.45,
                    linestyle="--",
                    alpha=0.35
                )

    # Teilchen
    ax.scatter(positions[:, 0], positions[:, 1], s=22, c="white", alpha=0.86)

    # Fokus hervorheben
    ax.scatter([fx], [fy], s=130, c="cyan", alpha=0.95)

    ax.set_title(
        "MS Cosmic Näheanalyse | Gravitation + Dark Energy + CMB + Kontaktzonen\n"
        f"Anziehung: {len(attraction_events)} | Abstoßung: {len(repulsion_events)} | Kritisch: {len(danger_events)}",
        color="white",
        fontsize=12
    )

    ax.text(
        -23.2,
        22.6,
        "Fokus-Zonen:\n"
        "-- blau = Anziehung / Resonanz\n"
        "orange = Abstoßung / Druck\n"
        "rot = kritische Nähe\n\n"
        "Magma = kosmisches Feld\n"
        "weiß = sichtbare Teilchen\n"
        "cyan = Fokus-Teilchen",
        fontsize=9,
        color="white",
        va="top",
        bbox=dict(facecolor="black", alpha=0.55, edgecolor="gray")
    )

ani = animation.FuncAnimation(fig, update, frames=frames, interval=30)
plt.show()
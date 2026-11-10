import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# -----------------------------
# PARAMETER
# -----------------------------
size = 10
dt = 0.1

# Drift (Flussrichtung)
vx, vy, vz = 0.5, 0.2, 0.0

# kleine Unruhe (natürliches Verhalten)
noise_strength = 0.05

# -----------------------------
# GITTER ERZEUGEN
# -----------------------------
x, y, z = np.meshgrid(
    np.arange(size),
    np.arange(size),
    np.arange(size),
    indexing='ij'
)

# in float konvertieren (für Bewegung)
x = x.astype(float)
y = y.astype(float)
z = z.astype(float)

# -----------------------------
# FIGURE
# -----------------------------
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# -----------------------------
# UPDATE
# -----------------------------
def update(frame):
    global x, y, z

    ax.clear()

    # Drift (dein Fluss)
    x += vx * dt
    y += vy * dt
    z += vz * dt

    # kleine zufällige Bewegung (realistisch)
    x += noise_strength * (np.random.rand(*x.shape) - 0.5)
    y += noise_strength * (np.random.rand(*y.shape) - 0.5)
    z += noise_strength * (np.random.rand(*z.shape) - 0.5)

    # Grenzen (Loop → wie Raum ohne Rand)
    x %= size
    y %= size
    z %= size

    # Plot
    ax.scatter(x.flatten(), y.flatten(), z.flatten(),
               color='olive', alpha=0.7, s=10)

    # Gitterlinien (Struktur sichtbar)
    for i in range(size):
        ax.plot([0, size], [i, i], [0, 0], color='gray', alpha=0.2)
        ax.plot([i, i], [0, size], [0, 0], color='gray', alpha=0.2)

    ax.set_xlim(0, size)
    ax.set_ylim(0, size)
    ax.set_zlim(0, size)

    ax.set_title("Cosmic Drift Grid (dein Modell)")

# -----------------------------
# START
# -----------------------------
ani = animation.FuncAnimation(fig, update, frames=200, interval=60)

plt.show()
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# ============================================================
# 3 ECHTE MODELLE:
# 1 = PEAK (Verdichtung)
# 2 = CRACK (Δ-Riss)
# 3 = VORTEX (Phase/Wirbel)
# ============================================================

np.random.seed(2)

# ------------------------------------------------------------
# SETTINGS
# ------------------------------------------------------------
GRID = 70
SPACE = 15
FRAMES = 500

MODE = 1  # Startmodus

x = np.linspace(-SPACE, SPACE, GRID)
y = np.linspace(-SPACE, SPACE, GRID)
X, Y = np.meshgrid(x, y)

# ------------------------------------------------------------
# BASISFELDER
# ------------------------------------------------------------
def normalize(a):
    a = a - np.min(a)
    return a / (np.max(a) + 1e-9)

def make_base_field(t):
    f = np.zeros_like(X)

    sources = [
        (0, 0, 300),
        (-6, 5, 120),
        (6, -4, 100)
    ]

    for cx, cy, m in sources:
        dx = X - cx
        dy = Y - cy
        r = np.sqrt(dx**2 + dy**2 + 1.2)
        f += m / r

    f += 0.2*np.sin(0.4*X + 0.3*Y - t)
    f += 0.15*np.cos(0.5*np.sqrt(X**2+Y**2) - t)

    return normalize(f)

def make_delta(f):
    gx, gy = np.gradient(f)
    return normalize(np.sqrt(gx**2 + gy**2))

def make_vorticity(t):
    vx = -Y
    vy = X
    rot = np.gradient(vy, axis=1) - np.gradient(vx, axis=0)
    return normalize(np.abs(rot + 0.5*np.sin(t)))

# ------------------------------------------------------------
# GEOMETRIE
# ------------------------------------------------------------
def triangle(center, size=1.0, rot=0):
    pts = np.array([
        [0, 1, 0],
        [-0.8, -0.6, 0],
        [0.8, -0.6, 0]
    ]) * size

    R = np.array([
        [np.cos(rot), -np.sin(rot), 0],
        [np.sin(rot),  np.cos(rot), 0],
        [0, 0, 1]
    ])

    return pts @ R.T + center

# ------------------------------------------------------------
# FIGURE
# ------------------------------------------------------------
fig = plt.figure(figsize=(10,8))
ax = fig.add_subplot(111, projection='3d')
fig.patch.set_facecolor("black")
ax.set_facecolor("black")

surface = None
objects = []

# ------------------------------------------------------------
# UPDATE
# ------------------------------------------------------------
def update(frame):
    global surface, objects, MODE

    ax.cla()

    t = frame * 0.05

    base = make_base_field(t)
    delta = make_delta(base)
    vortex = make_vorticity(t)

    # --------------------------------
    # MODE A: PEAK (Verdichtung)
    # --------------------------------
    if MODE == 1:
        field = base
        cmap = "inferno"

        peaks = np.argsort(field.ravel())[::-1][:5]

        for p in peaks:
            iy, ix = np.unravel_index(p, field.shape)
            z = field[iy, ix]*4

            tri = triangle([x[ix], y[iy], z+2], size=0.6+field[iy,ix])

            poly = Poly3DCollection([tri], color="cyan", alpha=0.9)
            ax.add_collection3d(poly)

    # --------------------------------
    # MODE B: CRACK (Δ-Riss)
    # --------------------------------
    elif MODE == 2:
        field = delta
        cmap = "cool"

        mask = delta > 0.6
        iy, ix = np.where(mask)

        for i in range(min(150, len(ix))):
            px = x[ix[i]]
            py = y[iy[i]]
            z = field[iy[i], ix[i]]*3

            ax.plot([px, px+0.5], [py, py+0.5], [z, z],
                    color="red", alpha=0.8, linewidth=1)

    # --------------------------------
    # MODE C: VORTEX (Wirbel)
    # --------------------------------
    elif MODE == 3:
        field = vortex
        cmap = "viridis"

        for angle in np.linspace(0, 2*np.pi, 12):
            cx = 5*np.cos(angle + t)
            cy = 5*np.sin(angle + t)

            tri = triangle([cx, cy, 2], size=0.8, rot=angle+t)

            poly = Poly3DCollection([tri], color="lime", alpha=0.85)
            ax.add_collection3d(poly)

    # --------------------------------
    # SURFACE
    # --------------------------------
    Z = field*2 - 1
    surface = ax.plot_surface(X, Y, Z, cmap=cmap, alpha=0.85)

    # STYLE
    ax.set_xlim(-SPACE, SPACE)
    ax.set_ylim(-SPACE, SPACE)
    ax.set_zlim(-2, 6)

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])

    titles = {
        1: "MODE A — PEAK / VERDICHTUNG",
        2: "MODE B — CRACK / Δ-RISS",
        3: "MODE C — VORTEX / WIRBEL"
    }

    ax.set_title(titles[MODE], color="white")

    ax.view_init(elev=30, azim=frame*0.4)

# ------------------------------------------------------------
# KEY CONTROL
# ------------------------------------------------------------
def on_key(event):
    global MODE

    if event.key == "1":
        MODE = 1
    elif event.key == "2":
        MODE = 2
    elif event.key == "3":
        MODE = 3

fig.canvas.mpl_connect('key_press_event', on_key)

# ------------------------------------------------------------
# RUN
# ------------------------------------------------------------
ani = FuncAnimation(fig, update, frames=FRAMES, interval=40)
plt.show()
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# ============================================================
# ABES – Triple Slice Visualization
# XY / XZ / YZ cuts through a dynamic 3D field
# ============================================================

# -----------------------------
# CONFIG
# -----------------------------
GRID_SIZE = 90
SPACE_SIZE = 10.0
FRAMES = 260
INTERVAL = 45
USE_DARK_LAYER = True

# -----------------------------
# 3D GRID
# -----------------------------
x = np.linspace(-SPACE_SIZE, SPACE_SIZE, GRID_SIZE)
y = np.linspace(-SPACE_SIZE, SPACE_SIZE, GRID_SIZE)
z = np.linspace(-SPACE_SIZE, SPACE_SIZE, GRID_SIZE)

X, Y, Z = np.meshgrid(x, y, z, indexing="ij")

# -----------------------------
# HELPERS
# -----------------------------
def normalize(a):
    a = a - np.min(a)
    m = np.max(a)
    if m < 1e-12:
        return np.zeros_like(a)
    return a / m

def gaussian3d(xv, yv, zv, x0, y0, z0, sigma, amp=1.0):
    return amp * np.exp(
        -(
            ((xv - x0) ** 2 + (yv - y0) ** 2 + (zv - z0) ** 2)
            / (2 * sigma ** 2)
        )
    )

def source_list(t):
    """
    Verteilte 3D-Quellen ohne globales Zentrum.
    """
    return [
        (-4.8 + 0.8 * np.sin(0.45 * t),  2.8,  1.5 * np.cos(0.25 * t), 1.15, 1.7),
        ( 4.2, -3.5 + 0.7 * np.cos(0.38 * t), -2.6, 0.95, 1.5),
        ( 2.0 * np.cos(0.18 * t),  5.0,  3.0 * np.sin(0.22 * t), 0.85, 1.3),
        (-5.5, -4.2,  2.4, 0.90, 1.6),
        ( 5.8 * np.sin(0.11 * t), -1.8, -4.5 + 0.9 * np.sin(0.31 * t), 0.78, 1.9),
    ]

def make_field_3d(t, obs_x=0.0, obs_y=0.0, obs_z=0.0):
    """
    Beobachter-relatives 3D-Feld.
    Kein absoluter Mittelpunkt.
    """
    Xr = X - obs_x
    Yr = Y - obs_y
    Zr = Z - obs_z

    f = np.zeros_like(X)

    for sx, sy, sz, amp, sig in source_list(t):
        f += gaussian3d(Xr, Yr, Zr, sx, sy, sz, sig, amp)

    # Zusätzliche Wellen-/Interferenzstruktur
    R = np.sqrt(Xr**2 + Yr**2 + Zr**2 + 0.6)
    f += 0.14 * np.sin(0.35 * Xr + 0.28 * Yr - 0.25 * Zr - 0.9 * t)
    f += 0.11 * np.cos(0.22 * Xr * Yr / (SPACE_SIZE + 1.0) - 0.5 * t)
    f += 0.09 * np.sin(0.18 * Yr * Zr / (SPACE_SIZE + 1.0) + 0.7 * t)
    f += 0.10 * np.cos(0.55 * R - 0.6 * t)

    return normalize(f)

def make_dark_layer_3d(t, obs_x=0.0, obs_y=0.0, obs_z=0.0):
    """
    Verborgener Einfluss im 3D-Raum.
    """
    Xr = X - obs_x
    Yr = Y - obs_y
    Zr = Z - obs_z

    d = np.zeros_like(X)

    d += gaussian3d(
        Xr, Yr, Zr,
        2.2 * np.cos(0.23 * t),
        1.7 * np.sin(0.27 * t),
        2.8 * np.cos(0.19 * t),
        2.6,
        0.85
    )

    d += gaussian3d(
        Xr, Yr, Zr,
        -4.5 + 0.9 * np.sin(0.17 * t),
        4.2 * np.cos(0.15 * t),
        -3.0 + 0.8 * np.sin(0.13 * t),
        3.0,
        0.60
    )

    R2 = np.sqrt((Xr + 1.5)**2 + (Yr - 2.0)**2 + (Zr + 1.0)**2 + 0.8)
    d += 0.18 / (R2 + 0.9)

    d += 0.08 * np.sin(0.08 * Xr * Yr * Zr / (SPACE_SIZE + 1.0) - 0.7 * t)

    return normalize(d)

def get_slices(field3d, ix, iy, iz):
    """
    Gibt die drei orthogonalen Schnitte zurück:
    XY bei z = iz
    XZ bei y = iy
    YZ bei x = ix
    """
    xy = field3d[:, :, iz]
    xz = field3d[:, iy, :]
    yz = field3d[ix, :, :]

    return xy, xz, yz

# -----------------------------
# FIGURE
# -----------------------------
fig, axes = plt.subplots(1, 3, figsize=(16, 5.6))
fig.patch.set_facecolor("black")

for ax in axes:
    ax.set_facecolor("black")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

axXY, axXZ, axYZ = axes

# -----------------------------
# INITIAL FRAME
# -----------------------------
t0 = 0.0

# Bewegter Beobachter im 3D-Raum
obs_x0 = 1.8 * np.cos(0.17 * t0)
obs_y0 = 1.3 * np.sin(0.21 * t0)
obs_z0 = 1.5 * np.cos(0.14 * t0)

F0 = make_field_3d(t0, obs_x0, obs_y0, obs_z0)

if USE_DARK_LAYER:
    D0 = make_dark_layer_3d(t0, obs_x0, obs_y0, obs_z0)
    F0 = normalize(0.86 * F0 + 0.22 * D0)

# Wir nehmen die mittleren Schnitte
ix0 = GRID_SIZE // 2
iy0 = GRID_SIZE // 2
iz0 = GRID_SIZE // 2

xy0, xz0, yz0 = get_slices(F0, ix0, iy0, iz0)

imXY = axXY.imshow(
    xy0.T,
    extent=[-SPACE_SIZE, SPACE_SIZE, -SPACE_SIZE, SPACE_SIZE],
    origin="lower",
    cmap="inferno",
    animated=True,
    aspect="auto"
)

imXZ = axXZ.imshow(
    xz0.T,
    extent=[-SPACE_SIZE, SPACE_SIZE, -SPACE_SIZE, SPACE_SIZE],
    origin="lower",
    cmap="viridis",
    animated=True,
    aspect="auto"
)

imYZ = axYZ.imshow(
    yz0.T,
    extent=[-SPACE_SIZE, SPACE_SIZE, -SPACE_SIZE, SPACE_SIZE],
    origin="lower",
    cmap="cool",
    animated=True,
    aspect="auto"
)

axXY.set_title("XY-Schnitt", color="white", fontsize=13)
axXZ.set_title("XZ-Schnitt", color="white", fontsize=13)
axYZ.set_title("YZ-Schnitt", color="white", fontsize=13)

title = fig.text(
    0.5, 0.965,
    "ABES – Triple Slice Visualization",
    ha="center", va="center",
    color="white", fontsize=15
)

subtitle = fig.text(
    0.5, 0.03,
    "Three orthogonal cuts through one dynamic 3D field | observer-relative, no fixed global center",
    ha="center", va="center",
    color="lightgray", fontsize=10
)

# -----------------------------
# ANIMATION
# -----------------------------
def update(frame):
    t = frame * 0.055

    # Beobachter bewegt sich im Raum
    obs_x = 1.8 * np.cos(0.17 * t)
    obs_y = 1.3 * np.sin(0.21 * t)
    obs_z = 1.5 * np.cos(0.14 * t)

    F = make_field_3d(t, obs_x, obs_y, obs_z)

    if USE_DARK_LAYER:
        D = make_dark_layer_3d(t, obs_x, obs_y, obs_z)
        F = normalize(0.86 * F + 0.22 * D)

    # Schnittpositionen dürfen sich leicht bewegen
    ix = int((GRID_SIZE / 2) + 10 * np.sin(0.19 * t))
    iy = int((GRID_SIZE / 2) + 9 * np.cos(0.16 * t))
    iz = int((GRID_SIZE / 2) + 11 * np.sin(0.13 * t))

    ix = np.clip(ix, 0, GRID_SIZE - 1)
    iy = np.clip(iy, 0, GRID_SIZE - 1)
    iz = np.clip(iz, 0, GRID_SIZE - 1)

    xy, xz, yz = get_slices(F, ix, iy, iz)

    imXY.set_array(xy.T)
    imXZ.set_array(xz.T)
    imYZ.set_array(yz.T)

    axXY.set_title(f"XY-Schnitt  |  z = {z[iz]:.2f}", color="white", fontsize=13)
    axXZ.set_title(f"XZ-Schnitt  |  y = {y[iy]:.2f}", color="white", fontsize=13)
    axYZ.set_title(f"YZ-Schnitt  |  x = {x[ix]:.2f}", color="white", fontsize=13)

    return [imXY, imXZ, imYZ]

ani = animation.FuncAnimation(
    fig,
    update,
    frames=FRAMES,
    interval=INTERVAL,
    blit=True
)

plt.tight_layout(rect=[0, 0.06, 1, 0.94])
plt.show()
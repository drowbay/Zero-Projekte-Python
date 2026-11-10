import random
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

# =========================================================
# PYDROID COMBO LIVING FIELD
# ---------------------------------------------------------
# Ein stabiles, statisches Sammelscript für Pydroid 3.
#
# Modi:
#   "freefield"   -> freies 3D Living Field
#   "breathing"   -> atmendes 3D Feld
#   "blackhole"   -> vereinfachtes Black-Hole-Feld
#   "peak"        -> Peak / Verdichtung
#   "crack"       -> Δ-Riss
#   "vortex"      -> Wirbel / Phasenfeld
#   "spinfoam"    -> statische 3D Sinnform
#   "kern"        -> PNNA / Energieausdruck
# =========================================================

MODE = "freefield"   # freefield, breathing, blackhole, peak, crack, vortex, spinfoam, kern

# ---------- gemeinsame Settings ----------
DARK_BG = "#06070a"
TEXT = "#f2f5f7"
SUBTEXT = "#c2cbd2"
GRID_COLOR = "#1a1d22"

# ---------- pydroid-sichere Größen ----------
STEPS = 1800
SPACE_RADIUS = 90
POINT_SIZE = 5
VOXEL_SIZE = 10

# ---------- kern / pnna ----------
EXPRESSION = "1 : ~0"   # z.B. "1 : ~0" oder "1 => -1"

ENERGY_MAP = {
    "1": 1,
    "0": 0,
    "-1": -1,
    "~0": 0.5,
}


# =========================================================
# HELPERS
# =========================================================
def style_3d_axes(ax):
    ax.set_facecolor(DARK_BG)
    try:
        ax.xaxis.set_pane_color((0.03, 0.04, 0.05, 1.0))
        ax.yaxis.set_pane_color((0.03, 0.04, 0.05, 1.0))
        ax.zaxis.set_pane_color((0.03, 0.04, 0.05, 1.0))
    except Exception:
        pass
    ax.tick_params(colors=SUBTEXT)
    ax.set_xlabel("X", color=TEXT)
    ax.set_ylabel("Y", color=TEXT)
    ax.set_zlabel("Z", color=TEXT)


def style_2d_axes(ax):
    ax.set_facecolor(DARK_BG)
    ax.tick_params(colors=SUBTEXT)
    for spine in ax.spines.values():
        spine.set_color("#22262d")


def energy_metric(x, y, z):
    return math.sqrt(x * x + y * y + z * z)


def voxel_index(x, y, z, voxel_size):
    return (int(x // voxel_size), int(y // voxel_size), int(z // voxel_size))


def random_spherical_point(radius):
    theta = random.uniform(0, 2 * math.pi)
    phi = math.acos(random.uniform(-1, 1))
    r = radius * (random.random() ** (1 / 3))
    x = r * math.sin(phi) * math.cos(theta)
    y = r * math.sin(phi) * math.sin(theta)
    z = r * math.cos(phi)
    return x, y, z


def random_stretched_point(radius, stretch=(1.8, 1.4, 1.2)):
    x, y, z = random_spherical_point(radius)
    return x * stretch[0], y * stretch[1], z * stretch[2]


def soft_rgba(state, z, energy):
    s = (state + 1.0) * 0.5
    depth = max(0.0, min(1.0, (z + 120.0) / 240.0))
    glow = max(0.0, min(1.0, energy / 120.0))
    r = 0.20 + 0.65 * s + 0.10 * glow
    g = 0.30 + 0.40 * (1 - abs(s - 0.5) * 2) + 0.10 * depth
    b = 0.45 + 0.36 * (1 - s) + 0.08 * (1 - depth)
    a = 0.35 + 0.45 * glow
    return (min(r, 1), min(g, 1), min(b, 1), min(a, 0.95))


def normalize(a):
    a = np.array(a, dtype=float)
    a = a - np.min(a)
    return a / (np.max(a) + 1e-9)


# =========================================================
# PEAKWEDGE / SPINFOAM HELPERS
# =========================================================
def rot_z(a):
    return np.array([
        [np.cos(a), -np.sin(a), 0],
        [np.sin(a),  np.cos(a), 0],
        [0, 0, 1]
    ])


def rot_y(a):
    return np.array([
        [ np.cos(a), 0, np.sin(a)],
        [0, 1, 0],
        [-np.sin(a), 0, np.cos(a)]
    ])


def triangle(center, size=1.0, rot=0.0):
    pts = np.array([
        [0.0, 1.0, 0.0],
        [-0.8, -0.6, 0.0],
        [0.8, -0.6, 0.0]
    ]) * size
    R = np.array([
        [np.cos(rot), -np.sin(rot), 0.0],
        [np.sin(rot),  np.cos(rot), 0.0],
        [0.0, 0.0, 1.0]
    ])
    return pts @ R.T + np.array(center)


def make_triangle(center, size=0.4, yaw=0.0, tilt=0.0):
    base = np.array([
        [0.0,  1.0, 0.0],
        [-0.85, -0.75, 0.0],
        [0.85, -0.75, 0.0]
    ]) * size
    R = rot_z(yaw) @ rot_y(tilt)
    pts = base @ R.T
    pts += np.array(center)
    return pts


def make_wire_triangle(center, size=0.7, yaw=0.0, tilt=0.0):
    pts = make_triangle(center, size=size, yaw=yaw, tilt=tilt)
    return np.vstack([pts, pts[0]])


def cloud_points(n, xlim, ylim, zlim, seed=7):
    rng = np.random.default_rng(seed)
    xs = rng.uniform(xlim[0], xlim[1], n)
    ys = rng.uniform(ylim[0], ylim[1], n)
    zs = rng.uniform(zlim[0], zlim[1], n)
    return np.column_stack([xs, ys, zs])


# =========================================================
# PNNA / KERN
# =========================================================
def combine(a, b):
    return ENERGY_MAP[a] + ENERGY_MAP[b]


def transition(a, b):
    return f"{a} -> {b}"


def evaluate(expression):
    tokens = expression.split()
    if ":" in tokens:
        i = tokens.index(":")
        result = combine(tokens[i - 1], tokens[i + 1])
        return f"Kombinierte Energie: {result}"
    if "=>" in tokens:
        i = tokens.index("=>")
        return transition(tokens[i - 1], tokens[i + 1])
    return "Unbekannter Ausdruck"


# =========================================================
# FREEFIELD
# =========================================================
def build_freefield():
    x = y = z = 0.0
    xs, ys, zs, colors = [], [], [], []
    occupied_voxels = set()
    energy_values = []

    for i in range(STEPS):
        g = 0.2 + 0.8 * (i / STEPS)
        radius = SPACE_RADIUS * g

        targets = []
        for _ in range(3):
            targets.append((0.0, 0.0, 0.0, "#FFFFFF"))
        for _ in range(2):
            targets.append((55.0 * g, -35.0 * g, 30.0 * g, "#FFD700"))
        for _ in range(6):
            px, py, pz = random_stretched_point(radius)
            targets.append((px, py, pz, "#00E5FF"))
        for _ in range(4):
            px, py, pz = random_stretched_point(radius * 1.2)
            targets.append((px, py, pz, "#1E88E5"))
        for _ in range(2):
            targets.append((
                random.uniform(-15, 15) * g,
                random.uniform(-15, 15) * g,
                random.uniform(-15, 15) * g,
                "#EC407A"
            ))

        px, py, pz, color = random.choice(targets)
        factor = random.choice([1.55, 1.7, 1.85, 2.0])

        x = (x + px) / factor
        y = (y + py) / factor
        z = (z + pz) / factor

        x *= 1.0015
        y *= 1.0012
        z *= 1.0010

        xs.append(x); ys.append(y); zs.append(z); colors.append(color)
        occupied_voxels.add(voxel_index(x, y, z, VOXEL_SIZE))
        energy_values.append(energy_metric(x, y, z))

    return xs, ys, zs, colors, occupied_voxels, energy_values


# =========================================================
# BREATHING
# =========================================================
def build_breathing():
    x = y = z = 0.0
    xs, ys, zs, colors = [], [], [], []
    occupied_voxels = set()
    energy_values = []

    for i in range(STEPS):
        t = i * 0.01
        t2 = i * 0.003
        pulse = math.sin(t) + 0.5 * math.sin(t2)
        pulse = max(-1.0, min(1.0, pulse))

        radius = SPACE_RADIUS * (1.0 + pulse * 0.4)
        px, py, pz = random_spherical_point(radius)
        factor = 1.6 + (pulse + 1.0) * 0.5

        x = (x + px) / factor
        y = (y + py) / factor
        z = (z + pz) / factor

        drift = 1.0 + pulse * 0.002
        x *= drift; y *= drift; z *= drift

        e = energy_metric(x, y, z)
        xs.append(x); ys.append(y); zs.append(z)
        colors.append(soft_rgba(pulse, z, e))
        occupied_voxels.add(voxel_index(x, y, z, VOXEL_SIZE))
        energy_values.append(e)

    return xs, ys, zs, colors, occupied_voxels, energy_values


# =========================================================
# BLACK HOLE
# =========================================================
def build_blackhole():
    x, y, z = random_spherical_point(SPACE_RADIUS * 0.8)
    vx, vy, vz = 0.0, 0.8, 0.0
    xs, ys, zs, colors = [], [], [], []
    occupied_voxels = set()
    energy_values = []
    captured = 0

    CORE_MASS = 1800.0
    SOFTENING = 8.0
    EVENT_HORIZON = 16.0
    CAPTURE_RADIUS = 6.0
    RING_RADIUS = 65.0
    RING_THICKNESS = 14.0
    DT = 0.05
    DRAG = 0.996
    SWIRL = 0.08

    def ring_point(radius, thickness):
        angle = random.uniform(0, 2 * math.pi)
        rr = radius + random.uniform(-thickness, thickness)
        return (
            rr * math.cos(angle),
            rr * math.sin(angle),
            random.uniform(-thickness * 0.2, thickness * 0.2),
        )

    for i in range(STEPS):
        dx = -x; dy = -y; dz = -z
        r2 = dx * dx + dy * dy + dz * dz + SOFTENING ** 2
        r = math.sqrt(r2)
        a = CORE_MASS / r2

        ax_g = a * dx / r
        ay_g = a * dy / r
        az_g = a * dz / r
        swirl_x = -y * (SWIRL / max(r, 1.0))
        swirl_y =  x * (SWIRL / max(r, 1.0))

        vx = (vx + (ax_g + swirl_x) * DT) * DRAG
        vy = (vy + (ay_g + swirl_y) * DT) * DRAG
        vz = (vz + az_g * DT) * DRAG

        x += vx * DT * 18
        y += vy * DT * 18
        z += vz * DT * 18

        e = 0.5 * (vx * vx + vy * vy + vz * vz)

        if r < CAPTURE_RADIUS:
            captured += 1
            x, y, z = ring_point(RING_RADIUS, RING_THICKNESS)
            vx, vy, vz = 0.0, 0.03, 0.0
            color = "#111111"
        elif r < EVENT_HORIZON:
            color = "#7A00FF"
        else:
            color = "#7FDBFF"

        xs.append(x); ys.append(y); zs.append(z); colors.append(color)
        occupied_voxels.add(voxel_index(x, y, z, VOXEL_SIZE))
        energy_values.append(e)

    return xs, ys, zs, colors, occupied_voxels, energy_values, captured


# =========================================================
# PEAK / CRACK / VORTEX
# =========================================================
def build_peak_crack_vortex(mode_name):
    GRID = 70
    SPACE = 15
    x = np.linspace(-SPACE, SPACE, GRID)
    y = np.linspace(-SPACE, SPACE, GRID)
    X, Y = np.meshgrid(x, y)
    t = 1.8

    def make_base_field(tt):
        f = np.zeros_like(X)
        sources = [(0, 0, 300), (-6, 5, 120), (6, -4, 100)]
        for cx, cy, m in sources:
            dx = X - cx
            dy = Y - cy
            r = np.sqrt(dx ** 2 + dy ** 2 + 1.2)
            f += m / r
        f += 0.2 * np.sin(0.4 * X + 0.3 * Y - tt)
        f += 0.15 * np.cos(0.5 * np.sqrt(X ** 2 + Y ** 2) - tt)
        return normalize(f)

    def make_delta(f):
        gx, gy = np.gradient(f)
        return normalize(np.sqrt(gx ** 2 + gy ** 2))

    def make_vorticity(tt):
        vx = -Y
        vy = X
        rot = np.gradient(vy, axis=1) - np.gradient(vx, axis=0)
        return normalize(np.abs(rot + 0.5 * np.sin(tt)))

    base = make_base_field(t)
    delta = make_delta(base)
    vortex = make_vorticity(t)

    return X, Y, base, delta, vortex


# =========================================================
# SPINFOAM STATIC
# =========================================================
def build_spinfoam_static():
    vertex = np.array([0.0, 0.0, 0.0])
    g1 = np.array([0.35, 0.95, 0.55])
    g2 = np.array([0.45, -0.75, -0.35])

    eta_points = cloud_points(
        180,
        xlim=(-2.5, 8.0),
        ylim=(-1.6, 5.2),
        zlim=(-1.8, 3.8),
        seed=7
    )

    face_top = np.array([
        [1.2, 3.7, 2.2],
        [6.8, 4.4, 2.9],
        [7.7, 2.2, 1.2],
        [3.0, 1.5, 0.9],
        [0.9, 2.4, 1.4]
    ])

    face_mid = np.array([
        [0.7, 1.0, 0.4],
        [5.8, 1.6, 1.0],
        [6.8, 0.2, 0.1],
        [3.6, -0.7, -0.6],
        [1.2, -0.1, -0.2]
    ])

    t = 2.3
    drift = np.array([0.8, 0.0, 0.0])

    centers = [
        np.array([2.2 + 0.35*np.sin(1.2*t),  2.2 + 0.15*np.cos(t),     1.3 + 0.25*np.sin(0.8*t)]),
        np.array([2.8 + 0.30*np.cos(0.9*t),  0.2 + 0.22*np.sin(1.1*t), 0.2 + 0.18*np.cos(1.3*t)]),
        np.array([6.6 + 0.18*np.sin(1.0*t), -1.1 + 0.18*np.cos(0.7*t), -0.8 + 0.20*np.sin(0.9*t)]),
        np.array([6.5 + 0.25*np.cos(0.8*t),  3.7 + 0.20*np.sin(0.9*t),  2.7 + 0.15*np.cos(1.0*t)]),
    ]

    yaws = [
        -0.55 + 0.30*np.sin(t),
        -0.35 + 0.25*np.cos(1.2*t),
         0.95 + 0.25*np.sin(0.9*t),
         0.75 + 0.22*np.cos(1.1*t),
    ]

    tilts = [
        0.35*np.sin(0.7*t),
        0.25*np.cos(0.9*t),
        0.40*np.sin(0.8*t),
        0.28*np.cos(0.85*t),
    ]

    sizes = [
        0.42 + 0.05*np.sin(t),
        0.48 + 0.05*np.cos(1.1*t),
        0.54 + 0.04*np.sin(0.8*t),
        0.52 + 0.04*np.cos(0.9*t),
    ]

    wedges = []
    wires = []
    for i in range(4):
        c = centers[i] + drift * 0.02
        tri = make_triangle(c, size=sizes[i], yaw=yaws[i], tilt=tilts[i])
        wire = make_wire_triangle(c, size=(sizes[i] + 0.28), yaw=yaws[i], tilt=tilts[i])
        wedges.append(tri)
        wires.append(wire)

    link_targets = [
        centers[1] + np.array([-0.35, 0.1, 0.0]),
        centers[0] + np.array([-0.25, -0.1, 0.0]),
        centers[2] + np.array([-0.45, 0.0, 0.1]),
    ]

    starts = [vertex, g1, g2]
    links = []
    for i in range(3):
        p0 = starts[i]
        p1 = link_targets[i] + drift * 0.02
        links.append((p0, p1))

    return vertex, g1, g2, eta_points, face_top, face_mid, wedges, wires, links


# =========================================================
# DRAW MODES
# =========================================================
def draw_freefield():
    xs, ys, zs, colors, occupied_voxels, energy_values = build_freefield()
    avg_energy = float(np.mean(energy_values)) if energy_values else 0.0
    density = len(xs) / max(len(occupied_voxels), 1)

    fig = plt.figure(figsize=(9, 9))
    fig.patch.set_facecolor(DARK_BG)
    ax = fig.add_subplot(111, projection="3d")
    style_3d_axes(ax)

    ax.scatter(xs, ys, zs, s=POINT_SIZE, c=colors)
    limit = 180
    ax.set_xlim(-limit, limit); ax.set_ylim(-limit, limit); ax.set_zlim(-limit, limit)
    ax.set_box_aspect((1, 1, 1))
    ax.set_title("Living Field Static", color=TEXT, pad=14)
    ax.view_init(elev=24, azim=35)

    fig.text(
        0.03, 0.95,
        "Living Field Static\n"
        "-------------------\n"
        f"mode        : freefield\n"
        f"points      : {len(xs):6d}\n"
        f"energy(avg) : {avg_energy:6.2f}\n"
        f"density     : {density:6.2f}\n"
        f"voxels      : {len(occupied_voxels):6d}",
        color=TEXT, fontsize=10, family="monospace", va="top"
    )
    plt.show()


def draw_breathing():
    xs, ys, zs, colors, occupied_voxels, energy_values = build_breathing()
    avg_energy = float(np.mean(energy_values)) if energy_values else 0.0
    density = len(xs) / max(len(occupied_voxels), 1)

    fig = plt.figure(figsize=(9, 9))
    fig.patch.set_facecolor(DARK_BG)
    ax = fig.add_subplot(111, projection="3d")
    style_3d_axes(ax)

    ax.scatter(xs, ys, zs, s=POINT_SIZE, c=colors)
    limit = 180
    ax.set_xlim(-limit, limit); ax.set_ylim(-limit, limit); ax.set_zlim(-limit, limit)
    ax.set_box_aspect((1, 1, 1))
    ax.set_title("Living Breathing Static", color=TEXT, pad=14)
    ax.view_init(elev=24, azim=35)

    fig.text(
        0.03, 0.95,
        "Living Breathing Static\n"
        "-----------------------\n"
        f"mode        : breathing\n"
        f"points      : {len(xs):6d}\n"
        f"energy(avg) : {avg_energy:6.2f}\n"
        f"density     : {density:6.2f}\n"
        f"voxels      : {len(occupied_voxels):6d}",
        color=TEXT, fontsize=10, family="monospace", va="top"
    )
    plt.show()


def draw_blackhole():
    xs, ys, zs, colors, occupied_voxels, energy_values, captured = build_blackhole()
    avg_energy = float(np.mean(energy_values)) if energy_values else 0.0
    density = len(xs) / max(len(occupied_voxels), 1)

    fig = plt.figure(figsize=(9, 9))
    fig.patch.set_facecolor(DARK_BG)
    ax = fig.add_subplot(111, projection="3d")
    style_3d_axes(ax)

    ax.scatter(xs, ys, zs, s=POINT_SIZE, c=colors)
    limit = 180
    ax.set_xlim(-limit, limit); ax.set_ylim(-limit, limit); ax.set_zlim(-limit, limit)
    ax.set_box_aspect((1, 1, 1))
    ax.set_title("Living Black Hole Static", color=TEXT, pad=14)
    ax.view_init(elev=24, azim=35)

    fig.text(
        0.03, 0.95,
        "Living Black Hole Static\n"
        "------------------------\n"
        f"mode        : blackhole\n"
        f"points      : {len(xs):6d}\n"
        f"energy(avg) : {avg_energy:6.2f}\n"
        f"density     : {density:6.2f}\n"
        f"voxels      : {len(occupied_voxels):6d}\n"
        f"captured    : {captured:6d}",
        color=TEXT, fontsize=10, family="monospace", va="top"
    )
    plt.show()


def draw_peak_crack_vortex(mode_name):
    X, Y, base, delta, vortex = build_peak_crack_vortex(mode_name)

    fig = plt.figure(figsize=(10, 8))
    fig.patch.set_facecolor(DARK_BG)
    ax = fig.add_subplot(111, projection="3d")
    style_3d_axes(ax)

    if mode_name == "peak":
        field = base
        cmap = "inferno"
        peaks = np.argsort(field.ravel())[::-1][:6]
        for p in peaks:
            iy, ix = np.unravel_index(p, field.shape)
            z = field[iy, ix] * 4
            tri = triangle([X[iy, ix], Y[iy, ix], z + 2], size=0.6 + field[iy, ix], rot=0.3)
            poly = Poly3DCollection([tri], color="cyan", alpha=0.9)
            ax.add_collection3d(poly)
        title = "MODE A — PEAK / VERDICHTUNG"

    elif mode_name == "crack":
        field = delta
        cmap = "cool"
        mask = delta > 0.6
        iy, ix = np.where(mask)
        for i in range(min(150, len(ix))):
            px = X[iy[i], ix[i]]
            py = Y[iy[i], ix[i]]
            z = field[iy[i], ix[i]] * 3
            ax.plot([px, px + 0.5], [py, py + 0.5], [z, z], color="red", alpha=0.8, linewidth=1)
        title = "MODE B — CRACK / Δ-RISS"

    else:
        field = vortex
        cmap = "viridis"
        t = 1.8
        for angle in np.linspace(0, 2 * np.pi, 12):
            cx = 5 * np.cos(angle + t)
            cy = 5 * np.sin(angle + t)
            tri = triangle([cx, cy, 2], size=0.8, rot=angle + t)
            poly = Poly3DCollection([tri], color="lime", alpha=0.85)
            ax.add_collection3d(poly)
        title = "MODE C — VORTEX / WIRBEL"

    Z = field * 2 - 1
    ax.plot_surface(X, Y, Z, cmap=cmap, alpha=0.88, linewidth=0, antialiased=True)
    ax.set_xlim(-15, 15); ax.set_ylim(-15, 15); ax.set_zlim(-2, 6)
    ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])
    ax.set_title(title, color=TEXT, pad=14)
    ax.view_init(elev=30, azim=28)
    plt.show()


def draw_spinfoam():
    vertex, g1, g2, eta_points, face_top, face_mid, wedges, wires, links = build_spinfoam_static()

    fig = plt.figure(figsize=(8.6, 8.8))
    fig.patch.set_facecolor(DARK_BG)
    ax = fig.add_subplot(111, projection="3d")
    style_3d_axes(ax)

    poly_top = Poly3DCollection([face_top], facecolors=(0.95, 0.95, 0.98, 0.16), edgecolors="#d8dee6", linewidths=1.3, alpha=0.55)
    poly_mid = Poly3DCollection([face_mid], facecolors=(0.70, 0.75, 0.82, 0.18), edgecolors="#cbd3dc", linewidths=1.2, alpha=0.48)
    ax.add_collection3d(poly_top)
    ax.add_collection3d(poly_mid)

    ax.scatter(
        eta_points[:, 0], eta_points[:, 1], eta_points[:, 2],
        s=14, facecolors="none", edgecolors="#7d8b9a", linewidths=0.7, alpha=0.75
    )

    ax.scatter([vertex[0]], [vertex[1]], [vertex[2]], s=40, color="#ffffff")
    ax.scatter([g1[0], g2[0]], [g1[1], g2[1]], [g1[2], g2[2]], s=18, color="#ffd166")
    ax.plot([vertex[0], g1[0]], [vertex[1], g1[1]], [vertex[2], g1[2]], color="#d8dee6", lw=1.2)
    ax.plot([vertex[0], g2[0]], [vertex[1], g2[1]], [vertex[2], g2[2]], color="#d8dee6", lw=1.2)

    wedge_cols = ["#7ee7ff", "#ffb347", "#ff6b9a", "#9cffc8"]
    for i, tri in enumerate(wedges):
        poly = Poly3DCollection([tri], facecolors=wedge_cols[i], edgecolors="#111111", linewidths=0.9, alpha=0.82)
        ax.add_collection3d(poly)

    for wire in wires:
        ax.plot(wire[:, 0], wire[:, 1], wire[:, 2], color="#8e9aa8", lw=1.0, alpha=0.75)

    for p0, p1 in links:
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], [p0[2], p1[2]], color="#c084fc", lw=1.4, alpha=0.82)

    ax.text(7.0, 3.2, 2.5, "spin foam face", fontsize=10, color=TEXT)
    ax.text(3.7, 0.6, 0.4, "wedge", fontsize=10, color=TEXT)
    ax.text(-0.55, 0.0, 0.0, "vertex", fontsize=10, color=TEXT)

    ax.set_xlim(-1.2, 8.4)
    ax.set_ylim(-2.2, 5.3)
    ax.set_zlim(-2.2, 4.0)
    ax.set_title("MS / MSM – 3D Sinnform Static", color=TEXT, pad=14)
    ax.view_init(elev=24, azim=-58)

    fig.text(
        0.03, 0.95,
        "Spinfoam Static\n"
        "---------------\n"
        "eta cloud  : Hintergrundpunkte\n"
        "psi wedges : 4 dynamische Dreiecke\n"
        "delta links: Vertex -> Wedge\n"
        "look       : dunkler, ruhiger, cleaner",
        color=TEXT, fontsize=10, family="monospace", va="top"
    )
    plt.tight_layout()
    plt.show()


def draw_kern():
    result = evaluate(EXPRESSION)

    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor(DARK_BG)
    style_2d_axes(ax)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlim(0, 10); ax.set_ylim(0, 10)

    ax.text(0.7, 8.8, "Kern / PNNA Energieausdruck", color=TEXT, fontsize=16, weight="bold")
    ax.text(0.7, 7.4, f"Ausdruck: {EXPRESSION}", color="#7ee7ff", fontsize=14, family="monospace")
    ax.text(0.7, 6.0, f"Ergebnis: {result}", color="#ffd166", fontsize=14, family="monospace")

    ax.text(
        0.7, 3.7,
        "ENERGY_MAP\n"
        "----------\n"
        "1   ->  1\n"
        "0   ->  0\n"
        "-1  -> -1\n"
        "~0  ->  0.5",
        color=SUBTEXT, fontsize=13, family="monospace",
        bbox=dict(facecolor="#101319", edgecolor="#303844", boxstyle="round,pad=0.6")
    )

    ax.text(
        6.0, 3.7,
        "Syntax\n"
        "------\n"
        "a : b   -> Energie kombinieren\n"
        "a => b  -> Transition anzeigen",
        color=SUBTEXT, fontsize=12, family="monospace",
        bbox=dict(facecolor="#101319", edgecolor="#303844", boxstyle="round,pad=0.6")
    )

    plt.show()


# =========================================================
# MAIN
# =========================================================
if MODE == "freefield":
    draw_freefield()
elif MODE == "breathing":
    draw_breathing()
elif MODE == "blackhole":
    draw_blackhole()
elif MODE == "peak":
    draw_peak_crack_vortex("peak")
elif MODE == "crack":
    draw_peak_crack_vortex("crack")
elif MODE == "vortex":
    draw_peak_crack_vortex("vortex")
elif MODE == "spinfoam":
    draw_spinfoam()
elif MODE == "kern":
    draw_kern()
else:
    raise ValueError("MODE muss freefield, breathing, blackhole, peak, crack, vortex, spinfoam oder kern sein")

input("Enter drücken zum Beenden...")

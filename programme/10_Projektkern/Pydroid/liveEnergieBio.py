import random
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

# =========================================================
# CONFIG
# =========================================================
SEED = 42

NX, NY, NZ = 5, 4, 3          # 60 Zellen
CELL_SIZE = 26

PARTICLES_PER_CELL = 10       # 60 * 10 = 600 Partikel
TOTAL_PARTICLES = NX * NY * NZ * PARTICLES_PER_CELL

FRAMES = 700
STEPS_PER_FRAME = 2
DT = 0.11
DRAG = 0.975

POINT_SIZE = 7
SHOW_CELL_CENTERS = True
SHOW_BOX_FLOORS = True
AUTO_ROTATE = True

EDGE_BLEND = 0.20

FIELD_TYPES = [
    "energy",
    "bio",
    "signal",
    "memory",
    "shadow",
    "drift",
]

FIELD_COLORS = {
    "energy": "#FFD700",
    "bio": "#7CFFB2",
    "signal": "#7FDBFF",
    "memory": "#C084FC",
    "shadow": "#5C6BC0",
    "drift": "#26A69A",
}

random.seed(SEED)
np.random.seed(SEED)

# =========================================================
# HELPERS
# =========================================================
def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def vlen3(x, y, z):
    return math.sqrt(x * x + y * y + z * z) + 1e-9

def cell_index_from_pos(px, py, pz):
    ix = clamp(int(px // CELL_SIZE), 0, NX - 1)
    iy = clamp(int(py // CELL_SIZE), 0, NY - 1)
    iz = clamp(int(pz // CELL_SIZE), 0, NZ - 1)
    return iz * (NX * NY) + iy * NX + ix

# =========================================================
# CELLS
# =========================================================
def make_cells():
    cells = []
    num_cells = NX * NY * NZ

    kinds = (FIELD_TYPES * ((num_cells // len(FIELD_TYPES)) + 1))[:num_cells]
    random.shuffle(kinds)

    idx = 0
    for iz in range(NZ):
        for iy in range(NY):
            for ix in range(NX):
                x0 = ix * CELL_SIZE
                y0 = iy * CELL_SIZE
                z0 = iz * CELL_SIZE

                x1 = x0 + CELL_SIZE
                y1 = y0 + CELL_SIZE
                z1 = z0 + CELL_SIZE

                cx = x0 + CELL_SIZE / 2
                cy = y0 + CELL_SIZE / 2
                cz = z0 + CELL_SIZE / 2

                a1 = random.uniform(0, 2 * math.pi)
                a2 = random.uniform(0, 2 * math.pi)

                dirx = math.cos(a1) * math.cos(a2)
                diry = math.sin(a1) * math.cos(a2)
                dirz = math.sin(a2)

                ftype = kinds[idx]

                cells.append({
                    "id": idx,
                    "ix": ix,
                    "iy": iy,
                    "iz": iz,
                    "x0": x0, "y0": y0, "z0": z0,
                    "x1": x1, "y1": y1, "z1": z1,
                    "cx": cx, "cy": cy, "cz": cz,
                    "type": ftype,
                    "color": FIELD_COLORS[ftype],
                    "strength": random.uniform(0.7, 1.8),
                    "phase": random.uniform(0, 2 * math.pi),
                    "dirx": dirx, "diry": diry, "dirz": dirz,
                })
                idx += 1
    return cells

cells = make_cells()

# =========================================================
# PARTICLES
# =========================================================
pos = np.zeros((TOTAL_PARTICLES, 3), dtype=float)
vel = np.zeros((TOTAL_PARTICLES, 3), dtype=float)
particle_cell = np.zeros(TOTAL_PARTICLES, dtype=int)
particle_color = np.empty(TOTAL_PARTICLES, dtype=object)

k = 0
for cell in cells:
    for _ in range(PARTICLES_PER_CELL):
        px = random.uniform(cell["x0"] + 2, cell["x1"] - 2)
        py = random.uniform(cell["y0"] + 2, cell["y1"] - 2)
        pz = random.uniform(cell["z0"] + 2, cell["z1"] - 2)

        pos[k] = [px, py, pz]
        vel[k] = [
            random.uniform(-0.6, 0.6),
            random.uniform(-0.6, 0.6),
            random.uniform(-0.6, 0.6),
        ]
        particle_cell[k] = cell["id"]
        particle_color[k] = cell["color"]
        k += 1

# =========================================================
# FORCES
# =========================================================
def single_cell_force(cell, px, py, pz, vx, vy, vz, frame):
    dx = cell["cx"] - px
    dy = cell["cy"] - py
    dz = cell["cz"] - pz

    dist = vlen3(dx, dy, dz)
    ndx = dx / dist
    ndy = dy / dist
    ndz = dz / dist

    pulse = 0.5 + 0.5 * math.sin(frame * 0.04 + cell["phase"])
    s = cell["strength"]
    t = cell["type"]

    fx = fy = fz = 0.0

    if t == "energy":
        fx = ndx * s * 0.45 + 0.10 * cell["dirx"]
        fy = ndy * s * 0.45 + 0.10 * cell["diry"]
        fz = ndz * s * 0.45 + 0.20 * pulse

    elif t == "bio":
        fx = ndx * s * 0.65 - vx * 0.08
        fy = ndy * s * 0.65 - vy * 0.08
        fz = ndz * s * 0.65 - vz * 0.08

    elif t == "signal":
        fx = ndx * s * 0.30 + cell["dirx"] * 0.28 * pulse
        fy = ndy * s * 0.30 + cell["diry"] * 0.28 * pulse
        fz = ndz * s * 0.30 + cell["dirz"] * 0.28 * pulse

    elif t == "memory":
        fx = ndx * s * 0.50 - vx * 0.16
        fy = ndy * s * 0.50 - vy * 0.16
        fz = ndz * s * 0.50 - vz * 0.16

    elif t == "shadow":
        fx = -ndx * s * 0.85
        fy = -ndy * s * 0.85
        fz = -ndz * s * 0.85

    elif t == "drift":
        fx = cell["dirx"] * s * 0.75 + ndx * 0.08
        fy = cell["diry"] * s * 0.75 + ndy * 0.08
        fz = cell["dirz"] * s * 0.75 + ndz * 0.08

    return fx, fy, fz


def blended_force(px, py, pz, vx, vy, vz, frame):
    idx = cell_index_from_pos(px, py, pz)
    cell = cells[idx]

    fx, fy, fz = single_cell_force(cell, px, py, pz, vx, vy, vz, frame)
    total_w = 1.0

    u = (px - cell["x0"]) / CELL_SIZE
    v = (py - cell["y0"]) / CELL_SIZE
    w = (pz - cell["z0"]) / CELL_SIZE

    ix = cell["ix"]
    iy = cell["iy"]
    iz = cell["iz"]

    # x-Nachbarn
    if u < EDGE_BLEND and ix > 0:
        nb = cells[idx - 1]
        bw = (EDGE_BLEND - u) / EDGE_BLEND
        nfx, nfy, nfz = single_cell_force(nb, px, py, pz, vx, vy, vz, frame)
        fx += nfx * bw; fy += nfy * bw; fz += nfz * bw; total_w += bw

    if u > 1.0 - EDGE_BLEND and ix < NX - 1:
        nb = cells[idx + 1]
        bw = (u - (1.0 - EDGE_BLEND)) / EDGE_BLEND
        nfx, nfy, nfz = single_cell_force(nb, px, py, pz, vx, vy, vz, frame)
        fx += nfx * bw; fy += nfy * bw; fz += nfz * bw; total_w += bw

    # y-Nachbarn
    if v < EDGE_BLEND and iy > 0:
        nb = cells[idx - NX]
        bw = (EDGE_BLEND - v) / EDGE_BLEND
        nfx, nfy, nfz = single_cell_force(nb, px, py, pz, vx, vy, vz, frame)
        fx += nfx * bw; fy += nfy * bw; fz += nfz * bw; total_w += bw

    if v > 1.0 - EDGE_BLEND and iy < NY - 1:
        nb = cells[idx + NX]
        bw = (v - (1.0 - EDGE_BLEND)) / EDGE_BLEND
        nfx, nfy, nfz = single_cell_force(nb, px, py, pz, vx, vy, vz, frame)
        fx += nfx * bw; fy += nfy * bw; fz += nfz * bw; total_w += bw

    # z-Nachbarn
    layer = NX * NY
    if w < EDGE_BLEND and iz > 0:
        nb = cells[idx - layer]
        bw = (EDGE_BLEND - w) / EDGE_BLEND
        nfx, nfy, nfz = single_cell_force(nb, px, py, pz, vx, vy, vz, frame)
        fx += nfx * bw; fy += nfy * bw; fz += nfz * bw; total_w += bw

    if w > 1.0 - EDGE_BLEND and iz < NZ - 1:
        nb = cells[idx + layer]
        bw = (w - (1.0 - EDGE_BLEND)) / EDGE_BLEND
        nfx, nfy, nfz = single_cell_force(nb, px, py, pz, vx, vy, vz, frame)
        fx += nfx * bw; fy += nfy * bw; fz += nfz * bw; total_w += bw

    return fx / total_w, fy / total_w, fz / total_w


# =========================================================
# WORLD
# =========================================================
WORLD_X = NX * CELL_SIZE
WORLD_Y = NY * CELL_SIZE
WORLD_Z = NZ * CELL_SIZE

transition_count = 0

def step_world(frame):
    global transition_count

    for i in range(TOTAL_PARTICLES):
        px, py, pz = pos[i]
        vx, vy, vz = vel[i]
        old_cell = particle_cell[i]

        fx, fy, fz = blended_force(px, py, pz, vx, vy, vz, frame)

        vx = (vx + fx * DT) * DRAG
        vy = (vy + fy * DT) * DRAG
        vz = (vz + fz * DT) * DRAG

        px += vx
        py += vy
        pz += vz

        bounce = 0.72

        if px < 0:
            px = 0; vx *= -bounce
        elif px > WORLD_X:
            px = WORLD_X; vx *= -bounce

        if py < 0:
            py = 0; vy *= -bounce
        elif py > WORLD_Y:
            py = WORLD_Y; vy *= -bounce

        if pz < 0:
            pz = 0; vz *= -bounce
        elif pz > WORLD_Z:
            pz = WORLD_Z; vz *= -bounce

        new_cell = cell_index_from_pos(px, py, pz)
        if new_cell != old_cell:
            transition_count += 1

        pos[i] = [px, py, pz]
        vel[i] = [vx, vy, vz]
        particle_cell[i] = new_cell
        particle_color[i] = cells[new_cell]["color"]


# =========================================================
# FIGURE
# =========================================================
fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection="3d")

fig.patch.set_facecolor("#05070a")
ax.set_facecolor("#05070a")
ax.tick_params(colors="white")
ax.set_xlabel("X", color="white")
ax.set_ylabel("Y", color="white")
ax.set_zlabel("Z", color="white")

if SHOW_BOX_FLOORS:
    for c in cells:
        xs = [c["x0"], c["x1"], c["x1"], c["x0"], c["x0"]]
        ys = [c["y0"], c["y0"], c["y1"], c["y1"], c["y0"]]
        zs = [c["z0"]] * 5
        ax.plot(xs, ys, zs, color=c["color"], alpha=0.10, linewidth=0.6)

if SHOW_CELL_CENTERS:
    cx = [c["cx"] for c in cells]
    cy = [c["cy"] for c in cells]
    cz = [c["cz"] for c in cells]
    cc = [c["color"] for c in cells]
    ax.scatter(cx, cy, cz, s=28, c=cc, marker="x", alpha=0.8)

scatter = ax.scatter(
    pos[:, 0],
    pos[:, 1],
    pos[:, 2],
    s=POINT_SIZE,
    c=particle_color,
    alpha=0.88
)

info_text = fig.text(
    0.02, 0.97, "",
    color="white",
    fontsize=10,
    family="monospace",
    va="top"
)

ax.set_xlim(0, WORLD_X)
ax.set_ylim(0, WORLD_Y)
ax.set_zlim(0, WORLD_Z)
ax.set_box_aspect((NX, NY, NZ))
ax.set_title("Live 3D — Energie + Bio + Signal", color="white", pad=14)

field_stats = {name: 0 for name in FIELD_TYPES}
for c in cells:
    field_stats[c["type"]] += 1

def update(frame):
    for _ in range(STEPS_PER_FRAME):
        step_world(frame)

    scatter._offsets3d = (pos[:, 0], pos[:, 1], pos[:, 2])
    scatter.set_color(particle_color)

    speeds = np.sqrt(vel[:, 0] ** 2 + vel[:, 1] ** 2 + vel[:, 2] ** 2)
    avg_speed = float(np.mean(speeds))

    dists = []
    for i in range(TOTAL_PARTICLES):
        c = cells[particle_cell[i]]
        dx = pos[i, 0] - c["cx"]
        dy = pos[i, 1] - c["cy"]
        dz = pos[i, 2] - c["cz"]
        dists.append(math.sqrt(dx * dx + dy * dy + dz * dz))
    avg_dist = float(np.mean(dists))

    info_text.set_text(
        "Live 3D\n"
        "-------\n"
        f"Zellen           : {NX*NY*NZ:4d}\n"
        f"Partikel         : {TOTAL_PARTICLES:4d}\n"
        f"Frame            : {frame:4d}\n"
        f"Transitions      : {transition_count:6d}\n"
        f"Ø Geschwindigkeit: {avg_speed:7.3f}\n"
        f"Ø Zentrumdistanz : {avg_dist:7.3f}\n"
        "\n"
        "Feldtypen:\n"
        f"energy : {field_stats['energy']:3d}\n"
        f"bio    : {field_stats['bio']:3d}\n"
        f"signal : {field_stats['signal']:3d}\n"
        f"memory : {field_stats['memory']:3d}\n"
        f"shadow : {field_stats['shadow']:3d}\n"
        f"drift  : {field_stats['drift']:3d}"
    )

    if AUTO_ROTATE:
        ax.view_init(elev=28 + 3 * math.sin(frame * 0.03), azim=35 + frame * 0.45)

    return scatter, info_text

anim = FuncAnimation(
    fig,
    update,
    frames=FRAMES,
    interval=35,
    blit=False,
    cache_frame_data=False
)

plt.show()
import random
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle

# =========================================================
# CONFIG
# =========================================================
SEED = 42

ROWS = 20
COLS = 20
NUM_BOXES = ROWS * COLS

BOX_W = 12
BOX_H = 12

WORLD_W = COLS * BOX_W
WORLD_H = ROWS * BOX_H

# Für Pydroid besser moderat halten:
PARTICLES_PER_BOX = 3   # 400 * 3 = 1200 Partikel
TOTAL_PARTICLES = NUM_BOXES * PARTICLES_PER_BOX

DT = 0.16
DRAG = 0.972
FRAMES = 900
INTERVAL = 35
POINT_SIZE = 8

# sanfte Kästchenmischung an Kanten
EDGE_BLEND = 0.22

SHOW_GRID = True
SHOW_BOX_COLORS = True

FIELD_TYPES = [
    "gravity",
    "energy",
    "quantum",
    "plasma",
    "noise",
    "memory",
    "shadow",
    "drift",
]

FIELD_COLORS = {
    "gravity": "#7FDBFF",   # hellblau
    "energy":  "#FFD700",   # gold
    "quantum": "#EC407A",   # pink
    "plasma":  "#FF7043",   # orange
    "noise":   "#BDBDBD",   # grau
    "memory":  "#AB47BC",   # violett
    "shadow":  "#5C6BC0",   # indigo
    "drift":   "#26A69A",   # türkis
}

random.seed(SEED)
np.random.seed(SEED)

# =========================================================
# HELPERS
# =========================================================
def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def vlen(x, y):
    return math.sqrt(x * x + y * y) + 1e-9

def box_index_from_pos(px, py):
    col = int(px // BOX_W)
    row = int(py // BOX_H)

    col = clamp(col, 0, COLS - 1)
    row = clamp(row, 0, ROWS - 1)

    return row * COLS + col

def rgba_from_hex(hex_color, alpha=0.10):
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    return (r, g, b, alpha)

# =========================================================
# BOXES
# =========================================================
def make_boxes():
    boxes = []

    types = (FIELD_TYPES * ((NUM_BOXES // len(FIELD_TYPES)) + 1))[:NUM_BOXES]
    random.shuffle(types)

    idx = 0
    for row in range(ROWS):
        for col in range(COLS):
            x0 = col * BOX_W
            y0 = row * BOX_H
            x1 = x0 + BOX_W
            y1 = y0 + BOX_H
            cx = x0 + BOX_W / 2
            cy = y0 + BOX_H / 2

            angle = random.uniform(0, 2 * math.pi)
            dirx = math.cos(angle)
            diry = math.sin(angle)

            field_type = types[idx]
            boxes.append({
                "id": idx,
                "row": row,
                "col": col,
                "x0": x0,
                "y0": y0,
                "x1": x1,
                "y1": y1,
                "cx": cx,
                "cy": cy,
                "type": field_type,
                "color": FIELD_COLORS[field_type],
                "strength": random.uniform(0.75, 1.85),
                "phase": random.uniform(0, 2 * math.pi),
                "dirx": dirx,
                "diry": diry,
            })
            idx += 1

    return boxes

boxes = make_boxes()

# =========================================================
# PARTICLES
# =========================================================
pos = np.zeros((TOTAL_PARTICLES, 2), dtype=float)
vel = np.zeros((TOTAL_PARTICLES, 2), dtype=float)
particle_box = np.zeros(TOTAL_PARTICLES, dtype=int)
particle_color = np.empty(TOTAL_PARTICLES, dtype=object)

k = 0
for box in boxes:
    for _ in range(PARTICLES_PER_BOX):
        px = random.uniform(box["x0"] + 1.5, box["x1"] - 1.5)
        py = random.uniform(box["y0"] + 1.5, box["y1"] - 1.5)

        pos[k] = [px, py]
        vel[k] = [random.uniform(-0.6, 0.6), random.uniform(-0.6, 0.6)]
        particle_box[k] = box["id"]
        particle_color[k] = box["color"]
        k += 1

# =========================================================
# FIELD FORCE
# =========================================================
def single_box_force(box, px, py, vx, vy, frame):
    dx = box["cx"] - px
    dy = box["cy"] - py
    dist = vlen(dx, dy)

    ndx = dx / dist
    ndy = dy / dist

    pulse = 0.5 + 0.5 * math.sin(frame * 0.03 + box["phase"])
    s = box["strength"]
    t = box["type"]

    fx = 0.0
    fy = 0.0

    if t == "gravity":
        fx = ndx * s * 0.95
        fy = ndy * s * 0.95

    elif t == "energy":
        fx = ndx * s * 0.45 + box["dirx"] * 0.10
        fy = ndy * s * 0.45 + box["diry"] * 0.10 + 0.20 * pulse

    elif t == "quantum":
        fx = ndx * s * 0.18 + random.uniform(-1, 1) * 0.85
        fy = ndy * s * 0.18 + random.uniform(-1, 1) * 0.85

    elif t == "plasma":
        tx = -ndy
        ty = ndx
        fx = tx * s * 1.10 + ndx * 0.10
        fy = ty * s * 1.10 + ndy * 0.10

    elif t == "noise":
        fx = random.uniform(-1, 1) * s * 1.15
        fy = random.uniform(-1, 1) * s * 1.15

    elif t == "memory":
        fx = ndx * s * 0.50 - vx * 0.18
        fy = ndy * s * 0.50 - vy * 0.18

    elif t == "shadow":
        fx = -ndx * s * 0.90
        fy = -ndy * s * 0.90

    elif t == "drift":
        fx = box["dirx"] * s * 0.85 + ndx * 0.08
        fy = box["diry"] * s * 0.85 + ndy * 0.08

    return fx, fy

def blended_force(px, py, vx, vy, frame):
    idx = box_index_from_pos(px, py)
    box = boxes[idx]

    fx, fy = single_box_force(box, px, py, vx, vy, frame)
    total_w = 1.0

    u = (px - box["x0"]) / BOX_W
    v = (py - box["y0"]) / BOX_H

    row = box["row"]
    col = box["col"]

    # linker Nachbar
    if u < EDGE_BLEND and col > 0:
        w = (EDGE_BLEND - u) / EDGE_BLEND
        nb = boxes[idx - 1]
        nfx, nfy = single_box_force(nb, px, py, vx, vy, frame)
        fx += nfx * w
        fy += nfy * w
        total_w += w

    # rechter Nachbar
    if u > 1.0 - EDGE_BLEND and col < COLS - 1:
        w = (u - (1.0 - EDGE_BLEND)) / EDGE_BLEND
        nb = boxes[idx + 1]
        nfx, nfy = single_box_force(nb, px, py, vx, vy, frame)
        fx += nfx * w
        fy += nfy * w
        total_w += w

    # unterer Nachbar
    if v < EDGE_BLEND and row > 0:
        w = (EDGE_BLEND - v) / EDGE_BLEND
        nb = boxes[idx - COLS]
        nfx, nfy = single_box_force(nb, px, py, vx, vy, frame)
        fx += nfx * w
        fy += nfy * w
        total_w += w

    # oberer Nachbar
    if v > 1.0 - EDGE_BLEND and row < ROWS - 1:
        w = (v - (1.0 - EDGE_BLEND)) / EDGE_BLEND
        nb = boxes[idx + COLS]
        nfx, nfy = single_box_force(nb, px, py, vx, vy, frame)
        fx += nfx * w
        fy += nfy * w
        total_w += w

    return fx / total_w, fy / total_w, idx

# =========================================================
# WORLD BOUNDS
# =========================================================
def apply_world_bounds(px, py, vx, vy):
    bounce = 0.72

    if px < 0:
        px = 0
        vx *= -bounce
    elif px > WORLD_W:
        px = WORLD_W
        vx *= -bounce

    if py < 0:
        py = 0
        vy *= -bounce
    elif py > WORLD_H:
        py = WORLD_H
        vy *= -bounce

    return px, py, vx, vy

# =========================================================
# FIGURE
# =========================================================
fig, ax = plt.subplots(figsize=(12, 12))
fig.patch.set_facecolor("#05070a")
ax.set_facecolor("#05070a")

ax.set_xlim(0, WORLD_W)
ax.set_ylim(0, WORLD_H)
ax.set_aspect("equal")
ax.set_xticks([])
ax.set_yticks([])

# Kästchen
if SHOW_GRID:
    for box in boxes:
        face = rgba_from_hex(box["color"], alpha=0.10) if SHOW_BOX_COLORS else (0, 0, 0, 0)
        rect = Rectangle(
            (box["x0"], box["y0"]),
            BOX_W,
            BOX_H,
            facecolor=face,
            edgecolor="#202631",
            linewidth=0.45
        )
        ax.add_patch(rect)

scatter = ax.scatter(
    pos[:, 0],
    pos[:, 1],
    s=POINT_SIZE,
    c=particle_color,
    alpha=0.92,
    linewidths=0
)

info_text = fig.text(
    0.015, 0.985, "",
    color="white",
    fontsize=10,
    family="monospace",
    va="top"
)

ax.set_title("20 x 20 Kästchen-Cluster | Cross-Dance", color="white", pad=12)

# =========================================================
# STATS
# =========================================================
field_stats = {name: 0 for name in FIELD_TYPES}
for b in boxes:
    field_stats[b["type"]] += 1

transition_count = 0

# =========================================================
# UPDATE
# =========================================================
def update(frame):
    global pos, vel, particle_box, particle_color, transition_count

    for i in range(TOTAL_PARTICLES):
        px, py = pos[i]
        vx, vy = vel[i]

        old_box = particle_box[i]

        fx, fy, current_idx = blended_force(px, py, vx, vy, frame)

        vx = (vx + fx * DT) * DRAG
        vy = (vy + fy * DT) * DRAG

        px += vx
        py += vy

        px, py, vx, vy = apply_world_bounds(px, py, vx, vy)

        new_box = box_index_from_pos(px, py)

        if new_box != old_box:
            transition_count += 1

        particle_box[i] = new_box
        particle_color[i] = boxes[new_box]["color"]

        pos[i] = [px, py]
        vel[i] = [vx, vy]

    scatter.set_offsets(pos)
    scatter.set_color(particle_color)

    speeds = np.sqrt(vel[:, 0] ** 2 + vel[:, 1] ** 2)
    avg_speed = float(np.mean(speeds))

    # mittlere Distanz zum Zentrum des aktuellen Kästchens
    dists = []
    for i in range(TOTAL_PARTICLES):
        b = boxes[particle_box[i]]
        dx = pos[i, 0] - b["cx"]
        dy = pos[i, 1] - b["cy"]
        dists.append(math.sqrt(dx * dx + dy * dy))
    avg_dist = float(np.mean(dists))

    info_text.set_text(
        "20x20 Cross-Dance Cluster\n"
        "-------------------------\n"
        f"Kästchen         : {NUM_BOXES:4d}\n"
        f"Partikel         : {TOTAL_PARTICLES:4d}\n"
        f"Frame            : {frame:4d}\n"
        f"Ø Geschwindigkeit: {avg_speed:7.3f}\n"
        f"Ø Zentrumdistanz : {avg_dist:7.3f}\n"
        f"Wechsel gesamt   : {transition_count:6d}\n"
        "\n"
        "Feldtypen:\n"
        f"gravity : {field_stats['gravity']:3d}\n"
        f"energy  : {field_stats['energy']:3d}\n"
        f"quantum : {field_stats['quantum']:3d}\n"
        f"plasma  : {field_stats['plasma']:3d}\n"
        f"noise   : {field_stats['noise']:3d}\n"
        f"memory  : {field_stats['memory']:3d}\n"
        f"shadow  : {field_stats['shadow']:3d}\n"
        f"drift   : {field_stats['drift']:3d}"
    )

    return scatter, info_text

anim = FuncAnimation(
    fig,
    update,
    frames=FRAMES,
    interval=INTERVAL,
    blit=False,
    cache_frame_data=False
)

plt.tight_layout(rect=[0.15, 0.0, 1.0, 1.0])
plt.show()
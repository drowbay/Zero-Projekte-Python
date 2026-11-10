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

ROWS = 4
COLS = 5
NUM_BOXES = ROWS * COLS

BOX_W = 38
BOX_H = 38

WORLD_W = COLS * BOX_W
WORLD_H = ROWS * BOX_H

PARTICLES_PER_BOX = 45
TOTAL_PARTICLES = NUM_BOXES * PARTICLES_PER_BOX

DT = 0.16
DRAG = 0.968
FRAMES = 650
INTERVAL = 40
POINT_SIZE = 9

SHOW_LABELS = True
SHOW_CENTERS = True

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
    "gravity": "#7FDBFF",
    "energy": "#FFD700",
    "quantum": "#EC407A",
    "plasma": "#FF7043",
    "noise": "#BDBDBD",
    "memory": "#AB47BC",
    "shadow": "#5C6BC0",
    "drift": "#26A69A",
}

random.seed(SEED)
np.random.seed(SEED)

# =========================================================
# HELPERS
# =========================================================
def vlen(x, y):
    return np.sqrt(x * x + y * y) + 1e-9


def make_boxes():
    boxes = []
    kinds = (FIELD_TYPES * ((NUM_BOXES // len(FIELD_TYPES)) + 1))[:NUM_BOXES]
    random.shuffle(kinds)

    idx = 0
    for r in range(ROWS):
        for c in range(COLS):
            x0 = c * BOX_W
            y0 = r * BOX_H
            x1 = x0 + BOX_W
            y1 = y0 + BOX_H
            cx = x0 + BOX_W / 2
            cy = y0 + BOX_H / 2

            boxes.append({
                "id": idx,
                "type": kinds[idx],
                "color": FIELD_COLORS[kinds[idx]],
                "x0": x0,
                "y0": y0,
                "x1": x1,
                "y1": y1,
                "cx": cx,
                "cy": cy,
                "strength": random.uniform(0.7, 1.8),
                "phase": random.uniform(0, 2 * math.pi),
            })
            idx += 1
    return boxes


def force_for_box(box, px, py, vx, vy, frame):
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
        fx = ndx * s * 0.85
        fy = ndy * s * 0.85

    elif t == "energy":
        fx = ndx * s * 0.55
        fy = ndy * s * 0.55 + 0.22 * pulse

    elif t == "quantum":
        fx = ndx * s * 0.22 + random.uniform(-1, 1) * 0.75
        fy = ndy * s * 0.22 + random.uniform(-1, 1) * 0.75

    elif t == "plasma":
        tx = -ndy
        ty = ndx
        fx = tx * s * 1.05 + ndx * 0.15
        fy = ty * s * 1.05 + ndy * 0.15

    elif t == "noise":
        fx = random.uniform(-1, 1) * s * 1.15
        fy = random.uniform(-1, 1) * s * 1.15

    elif t == "memory":
        fx = ndx * s * 0.48 - vx * 0.12
        fy = ndy * s * 0.48 - vy * 0.12

    elif t == "shadow":
        fx = -ndx * s * 0.95
        fy = -ndy * s * 0.95

    elif t == "drift":
        drift_x = 0.95
        drift_y = 0.30 * math.sin(frame * 0.02 + box["phase"])
        fx = drift_x * s * 0.65 + ndx * 0.06
        fy = drift_y * s * 0.65 + ndy * 0.06

    return fx, fy


def apply_box_limits(box, px, py, vx, vy):
    margin = 2.0
    bounce = 0.62

    if px < box["x0"] + margin:
        px = box["x0"] + margin
        vx *= -bounce
    elif px > box["x1"] - margin:
        px = box["x1"] - margin
        vx *= -bounce

    if py < box["y0"] + margin:
        py = box["y0"] + margin
        vy *= -bounce
    elif py > box["y1"] - margin:
        py = box["y1"] - margin
        vy *= -bounce

    return px, py, vx, vy


# =========================================================
# BOXES / PARTICLES
# =========================================================
boxes = make_boxes()

pos = np.zeros((TOTAL_PARTICLES, 2), dtype=float)
vel = np.zeros((TOTAL_PARTICLES, 2), dtype=float)
particle_box = np.zeros(TOTAL_PARTICLES, dtype=int)
particle_color = np.empty(TOTAL_PARTICLES, dtype=object)

k = 0
for box in boxes:
    for _ in range(PARTICLES_PER_BOX):
        px = random.uniform(box["x0"] + 4, box["x1"] - 4)
        py = random.uniform(box["y0"] + 4, box["y1"] - 4)

        pos[k] = [px, py]
        vel[k] = [random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)]
        particle_box[k] = box["id"]
        particle_color[k] = box["color"]
        k += 1


# =========================================================
# FIGURE
# =========================================================
fig, ax = plt.subplots(figsize=(14, 10))
fig.patch.set_facecolor("#05070a")
ax.set_facecolor("#05070a")

ax.set_xlim(0, WORLD_W)
ax.set_ylim(0, WORLD_H)
ax.set_aspect("equal")
ax.set_xticks([])
ax.set_yticks([])

# Kästchen zeichnen
for box in boxes:
    rect = Rectangle(
        (box["x0"], box["y0"]),
        BOX_W,
        BOX_H,
        fill=False,
        edgecolor="#39414c",
        linewidth=1.2
    )
    ax.add_patch(rect)

    if SHOW_CENTERS:
        ax.scatter(
            [box["cx"]],
            [box["cy"]],
            s=35,
            c=box["color"],
            marker="x",
            alpha=0.85
        )

    if SHOW_LABELS:
        ax.text(
            box["x0"] + 2,
            box["y1"] - 3,
            f"{box['id']:02d} {box['type']}",
            color=box["color"],
            fontsize=8,
            ha="left",
            va="top"
        )

scatter = ax.scatter(
    pos[:, 0],
    pos[:, 1],
    s=POINT_SIZE,
    c=particle_color,
    alpha=0.82
)

info_text = fig.text(
    0.015, 0.97, "",
    color="white",
    fontsize=10,
    family="monospace",
    va="top"
)

ax.set_title("Cluster mit 20 Kästchen", color="white", pad=14)


# =========================================================
# STATS
# =========================================================
def build_stats():
    stats = {name: 0 for name in FIELD_TYPES}
    for box in boxes:
        stats[box["type"]] += 1
    return stats

box_type_stats = build_stats()


# =========================================================
# UPDATE
# =========================================================
def update(frame):
    global pos, vel

    for i in range(TOTAL_PARTICLES):
        box = boxes[particle_box[i]]

        px, py = pos[i]
        vx, vy = vel[i]

        fx, fy = force_for_box(box, px, py, vx, vy, frame)

        vx = (vx + fx * DT) * DRAG
        vy = (vy + fy * DT) * DRAG

        px += vx
        py += vy

        px, py, vx, vy = apply_box_limits(box, px, py, vx, vy)

        pos[i] = [px, py]
        vel[i] = [vx, vy]

    scatter.set_offsets(pos)

    speeds = np.sqrt(vel[:, 0] ** 2 + vel[:, 1] ** 2)
    avg_speed = float(np.mean(speeds))

    dists = []
    for i in range(TOTAL_PARTICLES):
        box = boxes[particle_box[i]]
        dx = pos[i, 0] - box["cx"]
        dy = pos[i, 1] - box["cy"]
        dists.append(math.sqrt(dx * dx + dy * dy))
    avg_dist = float(np.mean(dists))

    info_text.set_text(
        "20 Kästchen Cluster\n"
        "-------------------\n"
        f"Frame          : {frame:4d}\n"
        f"Kästchen       : {NUM_BOXES:4d}\n"
        f"Partikel       : {TOTAL_PARTICLES:4d}\n"
        f"Ø Geschwindigkeit: {avg_speed:7.3f}\n"
        f"Ø Distanz Kern : {avg_dist:7.3f}\n"
        "\n"
        "Feldtypen:\n"
        f"gravity : {box_type_stats['gravity']:2d}\n"
        f"energy  : {box_type_stats['energy']:2d}\n"
        f"quantum : {box_type_stats['quantum']:2d}\n"
        f"plasma  : {box_type_stats['plasma']:2d}\n"
        f"noise   : {box_type_stats['noise']:2d}\n"
        f"memory  : {box_type_stats['memory']:2d}\n"
        f"shadow  : {box_type_stats['shadow']:2d}\n"
        f"drift   : {box_type_stats['drift']:2d}"
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

plt.tight_layout(rect=[0.12, 0.0, 1.0, 1.0])
plt.show()
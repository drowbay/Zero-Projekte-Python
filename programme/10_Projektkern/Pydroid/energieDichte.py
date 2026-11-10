import random
import math
from collections import deque

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401


# =========================================================
# KONFIGURATION
# =========================================================
SEED = 42

NX, NY, NZ = 5, 4, 3          # 60 Zellen
CELL_SIZE = 24

PARTICLES_PER_CELL = 8
TOTAL_PARTICLES = NX * NY * NZ * PARTICLES_PER_CELL

FRAMES = 900
STEPS_PER_FRAME = 2

DT = 0.11
POINT_SIZE = 8
EDGE_BLEND = 0.22
AUTO_ROTATE = True

ANALYSIS_WINDOW = 60
ANALYZE_EVERY = 1

FIELD_TYPES = ["energy", "bio", "signal", "memory", "shadow", "drift"]

FIELD_COLORS = {
    "energy": "#FFD700",   # gold
    "bio": "#7CFFB2",      # grün
    "signal": "#7FDBFF",   # hellblau
    "memory": "#C084FC",   # violett
    "shadow": "#5C6BC0",   # indigo
    "drift": "#26A69A",    # türkis
}

random.seed(SEED)
np.random.seed(SEED)


# =========================================================
# HILFSFUNKTIONEN
# =========================================================
def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def vlen3(x, y, z):
    return math.sqrt(x * x + y * y + z * z) + 1e-9


def arrow_from_change(delta, eps=0.01):
    if delta > eps:
        return "↑"
    if delta < -eps:
        return "↓"
    return "→"


def normalize(v):
    n = np.linalg.norm(v) + 1e-9
    return v / n


# =========================================================
# SIMULATIONSKLASSE
# =========================================================
class FieldSimulation:
    def __init__(self, style="ordered"):
        self.style = style
        self.prev_order_score = None
        self.prev_disorder_score = None
        self.reset(style)

    # -----------------------------------------------------
    # Zellindex aus Position
    # -----------------------------------------------------
    def cell_index_from_pos(self, px, py, pz):
        ix = clamp(int(px // CELL_SIZE), 0, NX - 1)
        iy = clamp(int(py // CELL_SIZE), 0, NY - 1)
        iz = clamp(int(pz // CELL_SIZE), 0, NZ - 1)
        return iz * (NX * NY) + iy * NX + ix

    # -----------------------------------------------------
    # Zellen aufbauen
    # -----------------------------------------------------
    def build_cells(self):
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

                    if self.style == "ordered":
                        strength = random.uniform(0.7, 1.4)
                    else:
                        strength = random.uniform(0.5, 2.2)

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
                        "strength": strength,
                        "phase": random.uniform(0, 2 * math.pi),
                        "dirx": dirx,
                        "diry": diry,
                        "dirz": dirz,
                    })
                    idx += 1
        return cells

    # -----------------------------------------------------
    # Reset
    # -----------------------------------------------------
    def reset(self, style=None):
        if style is not None:
            self.style = style

        self.cells = self.build_cells()

        self.world_x = NX * CELL_SIZE
        self.world_y = NY * CELL_SIZE
        self.world_z = NZ * CELL_SIZE

        self.pos = np.zeros((TOTAL_PARTICLES, 3), dtype=float)
        self.vel = np.zeros((TOTAL_PARTICLES, 3), dtype=float)
        self.particle_cell = np.zeros(TOTAL_PARTICLES, dtype=int)
        self.particle_color = np.empty(TOTAL_PARTICLES, dtype=object)

        k = 0
        for cell in self.cells:
            for _ in range(PARTICLES_PER_CELL):
                px = random.uniform(cell["x0"] + 2, cell["x1"] - 2)
                py = random.uniform(cell["y0"] + 2, cell["y1"] - 2)
                pz = random.uniform(cell["z0"] + 2, cell["z1"] - 2)

                self.pos[k] = [px, py, pz]

                if self.style == "ordered":
                    self.vel[k] = [
                        random.uniform(-0.35, 0.35),
                        random.uniform(-0.35, 0.35),
                        random.uniform(-0.35, 0.35),
                    ]
                else:
                    self.vel[k] = [
                        random.uniform(-0.9, 0.9),
                        random.uniform(-0.9, 0.9),
                        random.uniform(-0.9, 0.9),
                    ]

                self.particle_cell[k] = cell["id"]
                self.particle_color[k] = cell["color"]
                k += 1

        self.frame_counter = 0
        self.total_transitions = 0
        self.transition_window = deque(maxlen=ANALYSIS_WINDOW)
        self.cell_exit_window = deque(maxlen=ANALYSIS_WINDOW)

        self.last_analysis = {
            "order_score": 0.0,
            "disorder_score": 0.0,
            "cluster_count": 0,
            "avg_center_dist": 0.0,
            "transition_rate": 0.0,
            "top_cells": [],
            "avg_speed": 0.0,
            "occupied_microcells": 0,
        }

    # -----------------------------------------------------
    # Kraft einer einzelnen Zelle
    # -----------------------------------------------------
    def single_cell_force(self, cell, px, py, pz, vx, vy, vz, frame):
        dx = cell["cx"] - px
        dy = cell["cy"] - py
        dz = cell["cz"] - pz

        dist = vlen3(dx, dy, dz)
        ndx = dx / dist
        ndy = dy / dist
        ndz = dz / dist

        pulse = 0.5 + 0.5 * math.sin(frame * 0.05 + cell["phase"])
        s = cell["strength"]
        t = cell["type"]

        # Style-Faktoren
        if self.style == "ordered":
            center_gain = 1.0
            drift_gain = 0.75
            shadow_gain = 0.85
        else:
            center_gain = 0.55
            drift_gain = 1.25
            shadow_gain = 1.35

        fx = fy = fz = 0.0

        if t == "energy":
            fx = ndx * s * 0.40 * center_gain + 0.10 * cell["dirx"]
            fy = ndy * s * 0.40 * center_gain + 0.10 * cell["diry"]
            fz = ndz * s * 0.40 * center_gain + 0.18 * pulse

        elif t == "bio":
            fx = ndx * s * 0.65 * center_gain - vx * 0.10
            fy = ndy * s * 0.65 * center_gain - vy * 0.10
            fz = ndz * s * 0.65 * center_gain - vz * 0.10

        elif t == "signal":
            fx = ndx * s * 0.25 * center_gain + cell["dirx"] * 0.32 * pulse
            fy = ndy * s * 0.25 * center_gain + cell["diry"] * 0.32 * pulse
            fz = ndz * s * 0.25 * center_gain + cell["dirz"] * 0.32 * pulse

        elif t == "memory":
            fx = ndx * s * 0.55 * center_gain - vx * 0.18
            fy = ndy * s * 0.55 * center_gain - vy * 0.18
            fz = ndz * s * 0.55 * center_gain - vz * 0.18

        elif t == "shadow":
            fx = -ndx * s * 0.75 * shadow_gain
            fy = -ndy * s * 0.75 * shadow_gain
            fz = -ndz * s * 0.75 * shadow_gain

        elif t == "drift":
            fx = cell["dirx"] * s * 0.70 * drift_gain + ndx * 0.06
            fy = cell["diry"] * s * 0.70 * drift_gain + ndy * 0.06
            fz = cell["dirz"] * s * 0.70 * drift_gain + ndz * 0.06

        return fx, fy, fz

    # -----------------------------------------------------
    # Nachbar-Mischung an Zellgrenzen
    # -----------------------------------------------------
    def blended_force(self, px, py, pz, vx, vy, vz, frame):
        idx = self.cell_index_from_pos(px, py, pz)
        cell = self.cells[idx]

        fx, fy, fz = self.single_cell_force(cell, px, py, pz, vx, vy, vz, frame)
        total_w = 1.0

        u = (px - cell["x0"]) / CELL_SIZE
        v = (py - cell["y0"]) / CELL_SIZE
        w = (pz - cell["z0"]) / CELL_SIZE

        ix, iy, iz = cell["ix"], cell["iy"], cell["iz"]
        layer = NX * NY

        if u < EDGE_BLEND and ix > 0:
            nb = self.cells[idx - 1]
            bw = (EDGE_BLEND - u) / EDGE_BLEND
            nfx, nfy, nfz = self.single_cell_force(nb, px, py, pz, vx, vy, vz, frame)
            fx += nfx * bw
            fy += nfy * bw
            fz += nfz * bw
            total_w += bw

        if u > 1.0 - EDGE_BLEND and ix < NX - 1:
            nb = self.cells[idx + 1]
            bw = (u - (1.0 - EDGE_BLEND)) / EDGE_BLEND
            nfx, nfy, nfz = self.single_cell_force(nb, px, py, pz, vx, vy, vz, frame)
            fx += nfx * bw
            fy += nfy * bw
            fz += nfz * bw
            total_w += bw

        if v < EDGE_BLEND and iy > 0:
            nb = self.cells[idx - NX]
            bw = (EDGE_BLEND - v) / EDGE_BLEND
            nfx, nfy, nfz = self.single_cell_force(nb, px, py, pz, vx, vy, vz, frame)
            fx += nfx * bw
            fy += nfy * bw
            fz += nfz * bw
            total_w += bw

        if v > 1.0 - EDGE_BLEND and iy < NY - 1:
            nb = self.cells[idx + NX]
            bw = (v - (1.0 - EDGE_BLEND)) / EDGE_BLEND
            nfx, nfy, nfz = self.single_cell_force(nb, px, py, pz, vx, vy, vz, frame)
            fx += nfx * bw
            fy += nfy * bw
            fz += nfz * bw
            total_w += bw

        if w < EDGE_BLEND and iz > 0:
            nb = self.cells[idx - layer]
            bw = (EDGE_BLEND - w) / EDGE_BLEND
            nfx, nfy, nfz = self.single_cell_force(nb, px, py, pz, vx, vy, vz, frame)
            fx += nfx * bw
            fy += nfy * bw
            fz += nfz * bw
            total_w += bw

        if w > 1.0 - EDGE_BLEND and iz < NZ - 1:
            nb = self.cells[idx + layer]
            bw = (w - (1.0 - EDGE_BLEND)) / EDGE_BLEND
            nfx, nfy, nfz = self.single_cell_force(nb, px, py, pz, vx, vy, vz, frame)
            fx += nfx * bw
            fy += nfy * bw
            fz += nfz * bw
            total_w += bw

        return fx / total_w, fy / total_w, fz / total_w

    # -----------------------------------------------------
    # Simulationsschritt
    # -----------------------------------------------------
    def step(self, frame):
        transitions_this_step = 0
        cell_exits_this_step = np.zeros(len(self.cells), dtype=int)

        if self.style == "ordered":
            drag = 0.978
            noise_strength = 0.025
            impulse_chance = 0.0
        else:
            drag = 0.945
            noise_strength = 0.20
            impulse_chance = 0.025

        for i in range(TOTAL_PARTICLES):
            px, py, pz = self.pos[i]
            vx, vy, vz = self.vel[i]

            old_cell = self.particle_cell[i]

            fx, fy, fz = self.blended_force(px, py, pz, vx, vy, vz, frame)

            # Stilbedingte Zusatz-Unruhe
            fx += random.uniform(-1, 1) * noise_strength
            fy += random.uniform(-1, 1) * noise_strength
            fz += random.uniform(-1, 1) * noise_strength

            if self.style == "disordered" and random.random() < impulse_chance:
                vx += random.uniform(-1.0, 1.0)
                vy += random.uniform(-1.0, 1.0)
                vz += random.uniform(-1.0, 1.0)

            vx = (vx + fx * DT) * drag
            vy = (vy + fy * DT) * drag
            vz = (vz + fz * DT) * drag

            px += vx
            py += vy
            pz += vz

            bounce = 0.70 if self.style == "ordered" else 0.90

            if px < 0:
                px = 0
                vx *= -bounce
            elif px > self.world_x:
                px = self.world_x
                vx *= -bounce

            if py < 0:
                py = 0
                vy *= -bounce
            elif py > self.world_y:
                py = self.world_y
                vy *= -bounce

            if pz < 0:
                pz = 0
                vz *= -bounce
            elif pz > self.world_z:
                pz = self.world_z
                vz *= -bounce

            new_cell = self.cell_index_from_pos(px, py, pz)

            if new_cell != old_cell:
                transitions_this_step += 1
                cell_exits_this_step[old_cell] += 1
                self.total_transitions += 1

            self.pos[i] = [px, py, pz]
            self.vel[i] = [vx, vy, vz]
            self.particle_cell[i] = new_cell
            self.particle_color[i] = self.cells[new_cell]["color"]

        self.transition_window.append(transitions_this_step)
        self.cell_exit_window.append(cell_exits_this_step)
        self.frame_counter += 1

    # -----------------------------------------------------
    # Clusterzahl grob bestimmen
    # -----------------------------------------------------
    def compute_cluster_count(self):
        micro = CELL_SIZE / 2.0
        occ = {}

        for p in self.pos:
            key = (
                int(p[0] // micro),
                int(p[1] // micro),
                int(p[2] // micro),
            )
            occ[key] = occ.get(key, 0) + 1

        active = {k for k, v in occ.items() if v >= 3}
        visited = set()
        clusters = 0

        neighbors = [
            (1, 0, 0), (-1, 0, 0),
            (0, 1, 0), (0, -1, 0),
            (0, 0, 1), (0, 0, -1),
        ]

        for start in active:
            if start in visited:
                continue

            clusters += 1
            stack = [start]
            visited.add(start)

            while stack:
                cx, cy, cz = stack.pop()
                for dx, dy, dz in neighbors:
                    nb = (cx + dx, cy + dy, cz + dz)
                    if nb in active and nb not in visited:
                        visited.add(nb)
                        stack.append(nb)

        return clusters, len(active)

    # -----------------------------------------------------
    # Stabilisierende Zellen bestimmen
    # -----------------------------------------------------
    def compute_cell_stability(self):
        counts = np.zeros(len(self.cells), dtype=int)
        dist_sum = np.zeros(len(self.cells), dtype=float)
        speed_sum = np.zeros(len(self.cells), dtype=float)

        recent_exits = np.zeros(len(self.cells), dtype=int)
        for arr in self.cell_exit_window:
            recent_exits += arr

        for i in range(TOTAL_PARTICLES):
            cid = self.particle_cell[i]
            cell = self.cells[cid]

            counts[cid] += 1

            dx = self.pos[i, 0] - cell["cx"]
            dy = self.pos[i, 1] - cell["cy"]
            dz = self.pos[i, 2] - cell["cz"]
            dist = math.sqrt(dx * dx + dy * dy + dz * dz)

            speed = math.sqrt(
                self.vel[i, 0] ** 2 + self.vel[i, 1] ** 2 + self.vel[i, 2] ** 2
            )

            dist_sum[cid] += dist
            speed_sum[cid] += speed

        ranking = []
        ref_dist = CELL_SIZE * 0.80
        ref_speed = 1.8

        for cid, cell in enumerate(self.cells):
            n = counts[cid]
            if n == 0:
                score = 0.0
                avg_dist = 0.0
                avg_speed = 0.0
            else:
                avg_dist = dist_sum[cid] / n
                avg_speed = speed_sum[cid] / n

                dist_score = clamp(1.0 - avg_dist / ref_dist, 0.0, 1.0)
                speed_score = clamp(1.0 - avg_speed / ref_speed, 0.0, 1.0)
                exit_score = clamp(1.0 - recent_exits[cid] / max(1, n * 0.8), 0.0, 1.0)

                score = 0.45 * dist_score + 0.30 * speed_score + 0.25 * exit_score

            ranking.append({
                "cell_id": cid,
                "type": cell["type"],
                "score": score,
                "count": int(n),
                "avg_dist": avg_dist,
                "avg_speed": avg_speed,
                "exits": int(recent_exits[cid]),
            })

        ranking.sort(key=lambda x: x["score"], reverse=True)
        return ranking

    # -----------------------------------------------------
    # Analyse
    # -----------------------------------------------------
    def analyze(self):
        speeds = np.sqrt(
            self.vel[:, 0] ** 2 + self.vel[:, 1] ** 2 + self.vel[:, 2] ** 2
        )
        avg_speed = float(np.mean(speeds))

        center_dists = []
        for i in range(TOTAL_PARTICLES):
            c = self.cells[self.particle_cell[i]]
            dx = self.pos[i, 0] - c["cx"]
            dy = self.pos[i, 1] - c["cy"]
            dz = self.pos[i, 2] - c["cz"]
            center_dists.append(math.sqrt(dx * dx + dy * dy + dz * dz))

        avg_center_dist = float(np.mean(center_dists))

        transitions_recent = sum(self.transition_window)
        window_steps = max(len(self.transition_window), 1)
        transition_rate = transitions_recent / (TOTAL_PARTICLES * window_steps)

        cluster_count, occupied_microcells = self.compute_cluster_count()
        ranking = self.compute_cell_stability()

        top3_mean = 0.0
        if ranking:
            top3 = ranking[:3]
            top3_mean = float(np.mean([r["score"] for r in top3]))

        # Ordnungskomponenten
        center_order = clamp(1.0 - avg_center_dist / (CELL_SIZE * 0.85), 0.0, 1.0)
        transition_order = clamp(1.0 - transition_rate / 0.22, 0.0, 1.0)
        cluster_order = clamp(1.0 - max(cluster_count - 4, 0) / 16.0, 0.0, 1.0)
        stability_order = clamp(top3_mean, 0.0, 1.0)

        order_score = (
            0.35 * center_order
            + 0.25 * transition_order
            + 0.15 * cluster_order
            + 0.25 * stability_order
        )

        disorder_score = (
            0.35 * (1.0 - center_order)
            + 0.25 * (1.0 - transition_order)
            + 0.15 * (1.0 - cluster_order)
            + 0.25 * (1.0 - stability_order)
        )

        self.last_analysis = {
            "order_score": order_score,
            "disorder_score": disorder_score,
            "cluster_count": cluster_count,
            "avg_center_dist": avg_center_dist,
            "transition_rate": transition_rate,
            "top_cells": ranking[:5],
            "avg_speed": avg_speed,
            "occupied_microcells": occupied_microcells,
        }

        return self.last_analysis


# =========================================================
# SIMULATION START
# =========================================================
sim = FieldSimulation(style="ordered")


# =========================================================
# FIGUR
# =========================================================
fig = plt.figure(figsize=(13, 10))
ax = fig.add_subplot(111, projection="3d")

fig.patch.set_facecolor("#05070a")
ax.set_facecolor("#05070a")
ax.tick_params(colors="white")
ax.set_xlabel("X", color="white")
ax.set_ylabel("Y", color="white")
ax.set_zlabel("Z", color="white")

ax.set_xlim(0, sim.world_x)
ax.set_ylim(0, sim.world_y)
ax.set_zlim(0, sim.world_z)
ax.set_box_aspect((NX, NY, NZ))

# Zellzentren sichtbar machen
cx = [c["cx"] for c in sim.cells]
cy = [c["cy"] for c in sim.cells]
cz = [c["cz"] for c in sim.cells]
cc = [c["color"] for c in sim.cells]
centers = ax.scatter(cx, cy, cz, s=30, c=cc, marker="x", alpha=0.8)

# Gitterboden andeuten
for c in sim.cells:
    xs = [c["x0"], c["x1"], c["x1"], c["x0"], c["x0"]]
    ys = [c["y0"], c["y0"], c["y1"], c["y1"], c["y0"]]
    zs = [c["z0"]] * 5
    ax.plot(xs, ys, zs, color=c["color"], alpha=0.08, linewidth=0.7)

scatter = ax.scatter(
    sim.pos[:, 0],
    sim.pos[:, 1],
    sim.pos[:, 2],
    s=POINT_SIZE,
    c=sim.particle_color,
    alpha=0.88
)

info_text = fig.text(
    0.02, 0.97,
    "",
    color="white",
    fontsize=10,
    family="monospace",
    va="top"
)

help_text = fig.text(
    0.72, 0.97,
    "Tasten:\nM = ordered/disordered\nR = reset",
    color="white",
    fontsize=10,
    family="monospace",
    va="top"
)


# =========================================================
# KEY EVENTS
# =========================================================
def on_key(event):
    global sim

    if event.key == "m":
        new_style = "disordered" if sim.style == "ordered" else "ordered"
        sim.reset(new_style)
        refresh_centers()
    elif event.key == "r":
        sim.reset(sim.style)
        refresh_centers()


fig.canvas.mpl_connect("key_press_event", on_key)


def refresh_centers():
    global centers
    centers.remove()

    cx = [c["cx"] for c in sim.cells]
    cy = [c["cy"] for c in sim.cells]
    cz = [c["cz"] for c in sim.cells]
    cc = [c["color"] for c in sim.cells]

    centers = ax.scatter(cx, cy, cz, s=30, c=cc, marker="x", alpha=0.8)


# =========================================================
# UPDATE
# =========================================================
def update(frame):
    for _ in range(STEPS_PER_FRAME):
        sim.step(frame)

    if frame % ANALYZE_EVERY == 0:
        data = sim.analyze()
    else:
        data = sim.last_analysis

    scatter._offsets3d = (sim.pos[:, 0], sim.pos[:, 1], sim.pos[:, 2])
    scatter.set_color(sim.particle_color.tolist())

    order_score = data["order_score"]
    disorder_score = data["disorder_score"]

    if sim.prev_order_score is None:
        order_arrow = "→"
        disorder_arrow = "→"
    else:
        order_arrow = arrow_from_change(order_score - sim.prev_order_score)
        disorder_arrow = arrow_from_change(disorder_score - sim.prev_disorder_score)

    sim.prev_order_score = order_score
    sim.prev_disorder_score = disorder_score

    top_lines = []
    for rank, item in enumerate(data["top_cells"], start=1):
        top_lines.append(
            f"{rank}. Z{item['cell_id']:02d} {item['type']:<7} "
            f"S={item['score']:.2f} N={item['count']:2d}"
        )

    style_label = "ORDERED" if sim.style == "ordered" else "DISORDERED"

    info_text.set_text(
        f"Live 3D Analyzer [{style_label}]\n"
        f"---------------------------------\n"
        f"Ordnung       : {order_score*100:6.2f}% {order_arrow}\n"
        f"Unordnung     : {disorder_score*100:6.2f}% {disorder_arrow}\n"
        f"Clusterzahl   : {data['cluster_count']:6d}\n"
        f"Zentrumsdist. : {data['avg_center_dist']:6.2f}\n"
        f"Übergangsrate : {data['transition_rate']:6.3f}\n"
        f"Ø Tempo       : {data['avg_speed']:6.3f}\n"
        f"Micro-Zellen  : {data['occupied_microcells']:6d}\n"
        f"Transitions   : {sim.total_transitions:6d}\n"
        f"\n"
        f"Top stabilisierende Zellen:\n"
        + ("\n".join(top_lines) if top_lines else "keine")
    )

    ax.set_title(
        f"Energie + Bio + Signal | {style_label} | Frame {frame}",
        color="white",
        pad=14
    )

    if AUTO_ROTATE:
        ax.view_init(
            elev=28 + 3 * math.sin(frame * 0.03),
            azim=35 + frame * 0.42
        )

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
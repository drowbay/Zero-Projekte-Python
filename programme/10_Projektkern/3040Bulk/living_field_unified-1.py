
"""
living_field_unified.py

Ein einziges sauberes Script als "Living Field" Sammeldatei.
Es vereint mehrere Ideen aus:
- Stern + Wedges + Wachstum
- Partikel-Universum
- freies Feld mit Fixpunkten
- Breathing Field
- Black-Hole / Warped / Raytracing-Lite

Start:
    python3 living_field_unified.py

Modus oben bei MODE wählen:
    "living_star"
    "living_universe"
    "living_freefield"
    "living_breathing"
    "living_blackhole"
    "living_warped"
    "living_ray2d"
"""

import random
import math
from dataclasses import dataclass
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401


# =========================================================
# Globale Wahl
# =========================================================
MODE = "living_field"  # Alias -> living_freefield
# Andere Modi:
# MODE = "living_star"
# MODE = "living_universe"
# MODE = "living_freefield"
# MODE = "living_breathing"
# MODE = "living_blackhole"
# MODE = "living_warped"
# MODE = "living_ray2d"


# =========================================================
# Gemeinsame Hilfsfunktionen
# =========================================================
def growth_factor(step, max_steps, start=0.15, end=1.0):
    t = min(step / max_steps, 1.0)
    return start + (end - start) * (1 - math.exp(-5 * t)) / (1 - math.exp(-5))


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


def random_stretched_point(radius, stretch=(1.6, 1.2, 1.0)):
    x, y, z = random_spherical_point(radius)
    return x * stretch[0], y * stretch[1], z * stretch[2]


def random_point(radius):
    return random_spherical_point(radius)


def soft_rgba(state, z, energy):
    s = (state + 1) * 0.5
    depth = max(0.0, min(1.0, (z + 140) / 280))
    glow = max(0.0, min(1.0, energy / 160))
    r = 0.20 + 0.65 * s + 0.10 * glow
    g = 0.30 + 0.40 * (1 - abs(s - 0.5) * 2) + 0.12 * depth
    b = 0.45 + 0.36 * (1 - s) + 0.08 * (1 - depth)
    a = 0.18 + 0.58 * glow
    return (min(r, 1), min(g, 1), min(b, 1), min(a, 0.95))


# =========================================================
# Stern-Geometrie
# =========================================================
def star_points_2d(outer_radius=100, inner_radius=40):
    pts = []
    for i in range(10):
        angle_deg = 90 + i * 36
        angle_rad = math.radians(angle_deg)
        r = outer_radius if i % 2 == 0 else inner_radius
        x = r * math.cos(angle_rad)
        y = r * math.sin(angle_rad)
        pts.append((x, y))
    return pts


def make_peak_wedges(base_points, wedge_length=18, wedge_width=10, z_lift=8):
    wedges = []
    for i in range(0, 10, 2):
        x, y = base_points[i]
        length = math.hypot(x, y)
        if length == 0:
            continue
        ux, uy = x / length, y / length
        px, py = -uy, ux
        tip = (x + ux * wedge_length, y + uy * wedge_length, z_lift)
        left = (
            x + ux * (wedge_length * 0.5) + px * wedge_width,
            y + uy * (wedge_length * 0.5) + py * wedge_width,
            z_lift * 0.6,
        )
        right = (
            x + ux * (wedge_length * 0.5) - px * wedge_width,
            y + uy * (wedge_length * 0.5) - py * wedge_width,
            z_lift * 0.6,
        )
        wedges.extend([tip, left, right])
    return wedges


def make_inner_ring_particles(base_points, ring_scale=0.55, z_lift=15):
    return [(x * ring_scale, y * ring_scale, z_lift) for x, y in base_points]


# =========================================================
# Farben
# =========================================================
STAR_PARTICLE_COLORS = {
    "core": "#FFD700",
    "source": "#FFFFFF",
    "outer_peak": "#FF2D55",
    "inner_peak": "#FF9500",
    "wedge_tip": "#00E5FF",
    "wedge_left": "#00C853",
    "wedge_right": "#7C4DFF",
    "ring": "#1E88E5",
    "field": "#8D6E63",
    "quantum": "#EC407A",
    "echo": "#26A69A",
    "shadow": "#5C6BC0",
    "plasma": "#FFEB3B",
    "gravity": "#455A64",
    "memory": "#AB47BC",
    "noise": "#BDBDBD",
}

FREEFIELD_COLORS = {
    "anchor_1": "#FFFFFF",
    "anchor_2": "#FFD700",
    "field": "#00E5FF",
    "drift": "#1E88E5",
    "quantum": "#EC407A",
    "plasma": "#FF7043",
    "memory": "#AB47BC",
    "echo": "#26A69A",
    "noise": "#BDBDBD",
    "shadow": "#5C6BC0",
}


# =========================================================
# 3D Living Star
# =========================================================
def run_living_star():
    TOTAL_STEPS = 60000
    OUTER_RADIUS = 100
    INNER_RADIUS = 40
    TOP_HEIGHT = 120
    DRAW_EVERY = 400
    VOXEL_SIZE = 8
    POINT_SIZE = 2
    WEDGE_WEIGHT = 3
    SOURCE_WEIGHT = 2
    RING_WEIGHT = 2
    FIELD_WEIGHT = 1
    QUANTUM_WEIGHT = 1
    MEMORY_WEIGHT = 1
    FACTOR_CHOICES = [2, 2, 2.15, 2.3, 2.5]

    fig = plt.figure(figsize=(13, 9))
    ax = fig.add_subplot(111, projection="3d")
    ax.set_xlim(-145, 145); ax.set_ylim(-145, 145); ax.set_zlim(-30, 170)
    ax.set_box_aspect((1, 1, 1))
    ax.set_facecolor("#07080a")
    fig.patch.set_facecolor("#07080a")
    ax.tick_params(colors="white")
    ax.set_xlabel("X", color="white"); ax.set_ylabel("Y", color="white"); ax.set_zlabel("Z", color="white")
    ax.set_title("Living Star Field", color="white", pad=14)

    scatter = ax.scatter([], [], [], s=POINT_SIZE)
    target_scatter = ax.scatter([], [], [], s=26, alpha=0.85)
    info = fig.text(0.015, 0.96, "", fontsize=10, family="monospace", color="white", va="top")

    legend_handles = [
        Line2D([0], [0], marker='o', color='w', label=name, markerfacecolor=color, markersize=7)
        for name, color in STAR_PARTICLE_COLORS.items()
    ]
    ax.legend(handles=legend_handles, loc="upper right", bbox_to_anchor=(1.28, 1.0), title="Teilchen")

    x = y = z = 0.0
    xs, ys, zs = [], [], []
    point_colors = []
    occupied_voxels = set()
    field_counter = {}
    particle_counter = {name: 0 for name in STAR_PARTICLE_COLORS}
    energy_values = []
    history_points = []

    def build_targets(g):
        base_points = star_points_2d(OUTER_RADIUS * g, INNER_RADIUS * g)
        targets = []
        O = (0, 0, TOP_HEIGHT * g)
        for _ in range(SOURCE_WEIGHT):
            targets.append((O[0], O[1], O[2], "source"))
        for idx, (bx, by) in enumerate(base_points):
            ptype = "outer_peak" if idx % 2 == 0 else "inner_peak"
            targets.append((bx, by, 0, ptype))
        targets.append((0, 0, 0, "core"))

        wedges = make_peak_wedges(base_points, 18 * g, 10 * g, 10 * g)
        wedge_points = []
        for i in range(0, len(wedges), 3):
            tip, left, right = wedges[i:i+3]
            wedge_points.extend([
                (tip[0], tip[1], tip[2], "wedge_tip"),
                (left[0], left[1], left[2], "wedge_left"),
                (right[0], right[1], right[2], "wedge_right"),
            ])
        targets.extend(wedge_points * WEDGE_WEIGHT)

        ring = make_inner_ring_particles(base_points, 0.55, 15 * g)
        targets.extend([(p[0], p[1], p[2], "ring") for p in ring] * RING_WEIGHT)

        for bx, by in base_points:
            targets.append((bx * 0.5, by * 0.5, TOP_HEIGHT * g * 0.35, "field"))

        for _ in range(8):
            qx = random.uniform(-12, 12) * g
            qy = random.uniform(-12, 12) * g
            qz = TOP_HEIGHT * g + random.uniform(-8, 8) * g
            targets.append((qx, qy, qz, "quantum"))

        if len(history_points) > 50:
            for hx, hy, hz in random.sample(history_points, min(6, len(history_points))):
                targets.append((hx, hy, hz, "memory"))

        targets.extend([
            (0, 0, -10 * g, "shadow"),
            (0, 0, TOP_HEIGHT * g * 0.5, "plasma"),
            (0, 0, TOP_HEIGHT * g * 0.25, "gravity"),
            (random.uniform(-30, 30) * g, random.uniform(-30, 30) * g, random.uniform(0, 25) * g, "noise"),
            (random.uniform(-20, 20) * g, random.uniform(-20, 20) * g, random.uniform(10, 35) * g, "echo"),
        ])

        seen = set()
        visible = []
        for t in targets:
            key = (round(t[0], 4), round(t[1], 4), round(t[2], 4), t[3])
            if key not in seen:
                visible.append(t)
                seen.add(key)
        return targets, visible

    def update(frame):
        nonlocal x, y, z
        g = growth_factor(frame, TOTAL_STEPS, 0.20, 1.0)
        targets, visible_targets = build_targets(g)

        for _ in range(6):
            px, py, pz, particle_type = random.choice(targets)
            factor = random.choice(FACTOR_CHOICES)
            x = (x + px) / factor
            y = (y + py) / factor
            z = (z + pz) / factor

            xs.append(x); ys.append(y); zs.append(z)
            point_colors.append(STAR_PARTICLE_COLORS[particle_type])
            particle_counter[particle_type] += 1
            e = energy_metric(x, y, z)
            energy_values.append(e)

            vox = voxel_index(x, y, z, VOXEL_SIZE)
            occupied_voxels.add(vox)
            field_counter[vox] = field_counter.get(vox, 0) + 1

        if frame % 2 == 0:
            history_points.append((x, y, z))
            if len(history_points) > 500:
                history_points.pop(0)

        scatter._offsets3d = (xs, ys, zs)
        scatter.set_color(point_colors)

        tx = [p[0] for p in visible_targets]
        ty = [p[1] for p in visible_targets]
        tz = [p[2] for p in visible_targets]
        tc = [STAR_PARTICLE_COLORS[p[3]] for p in visible_targets]
        target_scatter._offsets3d = (tx, ty, tz)
        target_scatter.set_color(tc)

        avg_energy = float(np.mean(energy_values[-1000:])) if energy_values else 0.0
        density = len(xs) / max(len(occupied_voxels), 1)
        dominant_voxel = max(field_counter, key=field_counter.get) if field_counter else None
        dominant_particle = max(particle_counter, key=particle_counter.get)

        info.set_text(
            "Living Star\n"
            "-----------\n"
            f"Energie     : {avg_energy:8.2f}\n"
            f"Lage        : ({x:7.2f}, {y:7.2f}, {z:7.2f})\n"
            f"Feld        : {len(occupied_voxels):8d} Voxel\n"
            f"Ordnung     : {density:8.2f}\n"
            f"Wachstum    : {g:8.2f}\n"
            f"DominantVox : {dominant_voxel}\n"
            f"TopPartikel : {dominant_particle}"
        )
        ax.view_init(elev=22 + 4 * math.sin(frame * 0.02), azim=(frame * 0.4) % 360)
        return scatter, target_scatter

    FuncAnimation(fig, update, frames=TOTAL_STEPS, interval=30, blit=False, cache_frame_data=False)
    plt.show()


# =========================================================
# 3D Living Universe / Freefield
# =========================================================
def run_living_freefield(universe=False):
    TOTAL_STEPS = 80000 if universe else 70000
    SPACE_RADIUS = 120
    STRETCH = (1.8, 1.4, 1.2)
    DRAW_EVERY = 1
    VOXEL_SIZE = 10
    POINT_SIZE = 3 if universe else 2
    FACTOR_CHOICES = [1.55, 1.7, 1.85, 2.0] if not universe else [1.9, 2.0, 2.15, 2.3]
    ANCHOR_1 = (0, 0, 0)
    ANCHOR_2 = (55, -35, 30)
    USE_SECOND_ANCHOR = True

    fig = plt.figure(figsize=(13, 9))
    ax = fig.add_subplot(111, projection="3d")
    scatter = ax.scatter([], [], [], s=POINT_SIZE)
    target_scatter = ax.scatter([], [], [], s=40, alpha=0.95)

    limit = SPACE_RADIUS * max(STRETCH) * 1.2
    ax.set_xlim(-limit, limit); ax.set_ylim(-limit, limit); ax.set_zlim(-limit, limit)
    ax.set_box_aspect((1, 1, 1))
    ax.set_facecolor("#06070a"); fig.patch.set_facecolor("#06070a")
    ax.tick_params(colors="white")
    ax.set_xlabel("X", color="white"); ax.set_ylabel("Y", color="white"); ax.set_zlabel("Z", color="white")
    ax.set_title("Living Field" if not universe else "Living Universe", color="white")

    legend_handles = [
        Line2D([0], [0], marker='o', color='w', label=name, markerfacecolor=color, markersize=8)
        for name, color in FREEFIELD_COLORS.items()
    ]
    ax.legend(handles=legend_handles, loc="upper right", bbox_to_anchor=(1.22, 1.0), title="Teilchen")
    info = fig.text(0.015, 0.96, "", fontsize=10, verticalalignment="top", family="monospace", color="white")

    x = y = z = 0.0
    xs, ys, zs = [], [], []
    point_colors = []
    occupied_voxels = set()
    field_counter = {}
    particle_counter = {name: 0 for name in FREEFIELD_COLORS}
    energy_values = []
    history_points = []

    def build_targets(g):
        radius = SPACE_RADIUS * g
        targets = []
        for _ in range(3):
            targets.append((*ANCHOR_1, "anchor_1"))
        if USE_SECOND_ANCHOR:
            scaled_anchor_2 = tuple(a * g for a in ANCHOR_2)
            for _ in range(2):
                targets.append((*scaled_anchor_2, "anchor_2"))

        for _ in range(6 if not universe else 8):
            targets.append((*random_stretched_point(radius, STRETCH), "field"))
        for _ in range(4 if not universe else 6):
            targets.append((*random_stretched_point(radius * 1.25, STRETCH), "drift"))
        for _ in range(2 if not universe else 4):
            q = random.uniform(-15, 15) * g
            targets.append((q, random.uniform(-15, 15) * g, random.uniform(-15, 15) * g, "quantum"))

        if len(history_points) > 30:
            for hx, hy, hz in random.sample(history_points, min(8, len(history_points))):
                targets.append((hx, hy, hz, "memory"))

        targets.extend([
            (*random_stretched_point(radius * 0.7, STRETCH), "echo"),
            (*random_stretched_point(radius * 0.4, (2.0, 2.0, 0.8)), "noise"),
        ])
        sx, sy, sz = random_stretched_point(radius * 0.5, (1.2, 1.2, 0.5))
        targets.append((sx, sy, -abs(sz), "shadow"))
        targets.append((*random_stretched_point(radius * 0.9, (1.0, 1.0, 1.6)), "plasma"))

        seen = set()
        visible = []
        for t in targets:
            key = (round(t[0], 3), round(t[1], 3), round(t[2], 3), t[3])
            if key not in seen:
                visible.append(t)
                seen.add(key)
        return targets, visible

    def update(frame):
        nonlocal x, y, z
        g = growth_factor(frame, TOTAL_STEPS) if not universe else growth_factor(frame, TOTAL_STEPS, 0.10, 1.0)
        targets, visible_targets = build_targets(g)

        for _ in range(6 if not universe else 8):
            px, py, pz, particle_type = random.choice(targets)
            factor = random.choice(FACTOR_CHOICES)
            x = (x + px) / factor
            y = (y + py) / factor
            z = (z + pz) / factor

            pulse = math.sin(frame * 0.02) if universe else 0.0
            x *= 1.0015 + 0.0004 * pulse
            y *= 1.0012 + 0.0003 * pulse
            z *= 1.0010 + 0.0002 * pulse

            xs.append(x); ys.append(y); zs.append(z)
            point_colors.append(FREEFIELD_COLORS[particle_type])
            particle_counter[particle_type] += 1

            e = energy_metric(x, y, z)
            energy_values.append(e)
            vox = voxel_index(x, y, z, VOXEL_SIZE)
            occupied_voxels.add(vox)
            field_counter[vox] = field_counter.get(vox, 0) + 1

        if frame % 2 == 0:
            history_points.append((x, y, z))
            if len(history_points) > 600:
                history_points.pop(0)

        scatter._offsets3d = (xs, ys, zs)
        scatter.set_color(point_colors)
        tx = [p[0] for p in visible_targets]; ty = [p[1] for p in visible_targets]; tz = [p[2] for p in visible_targets]
        tc = [FREEFIELD_COLORS[p[3]] for p in visible_targets]
        target_scatter._offsets3d = (tx, ty, tz); target_scatter.set_color(tc)

        avg_energy = float(np.mean(energy_values[-1000:])) if energy_values else 0.0
        density = len(xs) / max(len(occupied_voxels), 1)
        dominant_voxel = max(field_counter, key=field_counter.get) if field_counter else None
        dominant_particle = max(particle_counter, key=particle_counter.get)

        title = "Living Field" if not universe else "Living Universe"
        info.set_text(
            f"{title}\n"
            "-----------\n"
            f"Energie     : {avg_energy:8.2f}\n"
            f"Lage        : ({x:7.2f}, {y:7.2f}, {z:7.2f})\n"
            f"Feld        : {len(occupied_voxels):8d} Voxel\n"
            f"Ordnung     : {density:8.2f}\n"
            f"Wachstum    : {g:8.2f}\n"
            f"TopPartikel : {dominant_particle}\n"
            f"DominantVox : {dominant_voxel}"
        )
        ax.view_init(elev=22 + 5 * math.sin(frame * 0.014), azim=(frame * 0.5) % 360)
        return scatter, target_scatter

    FuncAnimation(fig, update, frames=TOTAL_STEPS, interval=30, blit=False, cache_frame_data=False)
    plt.show()


# =========================================================
# 3D Living Breathing
# =========================================================
def run_living_breathing():
    TOTAL_STEPS = 100000
    BASE_RADIUS = 120
    PULSE_SPEED = 0.002
    SECOND_PULSE = 0.0007
    DRIFT_STRENGTH = 0.002
    FACTOR_BASE = 1.6
    FACTOR_VARIATION = 0.6
    POINT_SIZE = 2

    fig = plt.figure(figsize=(11, 9))
    ax = fig.add_subplot(111, projection='3d')
    scatter = ax.scatter([], [], [], s=POINT_SIZE)
    limit = BASE_RADIUS * 1.8
    ax.set_xlim(-limit, limit); ax.set_ylim(-limit, limit); ax.set_zlim(-limit, limit)
    ax.set_box_aspect((1, 1, 1))
    ax.set_facecolor("#06070a"); fig.patch.set_facecolor("#06070a")
    ax.tick_params(colors="white")
    ax.set_title("Living Breathing Field", color="white")
    info_text = fig.text(0.02, 0.95, "", fontsize=10, family="monospace", verticalalignment="top", color="white")

    x = y = z = 0.0
    xs, ys, zs = [], [], []
    colors = []
    energy_values = []

    def update(frame):
        nonlocal x, y, z
        t = frame * PULSE_SPEED
        t2 = frame * SECOND_PULSE
        state = math.sin(t) + 0.5 * math.sin(t2)
        state = max(-1, min(1, state))
        radius = BASE_RADIUS * (1 + state * 0.5)
        factor = FACTOR_BASE + (state + 1) * FACTOR_VARIATION

        for _ in range(5):
            px, py, pz = random_point(radius)
            x = (x + px) / factor
            y = (y + py) / factor
            z = (z + pz) / factor

            drift = 1 + state * DRIFT_STRENGTH
            x *= drift; y *= drift; z *= drift
            xs.append(x); ys.append(y); zs.append(z)

            e = energy_metric(x, y, z)
            energy_values.append(e)
            colors.append(soft_rgba(state, z, e))

        scatter._offsets3d = (xs, ys, zs)
        scatter.set_color(colors)
        avg_e = float(np.mean(energy_values[-1000:])) if energy_values else 0.0
        info_text.set_text(
            "Living Breathing\n"
            "----------------\n"
            f"State       : {state:8.3f}\n"
            f"Radius      : {radius:8.2f}\n"
            f"Energy(avg) : {avg_e:8.2f}\n"
            f"Points      : {len(xs):8d}"
        )
        ax.view_init(elev=22 + 4 * math.sin(frame * 0.015), azim=(frame * 0.55) % 360)
        return scatter,

    FuncAnimation(fig, update, frames=TOTAL_STEPS, interval=30, blit=False, cache_frame_data=False)
    plt.show()


# =========================================================
# 3D Living Black Hole
# =========================================================
def run_living_blackhole(warped=False):
    TOTAL_STEPS = 60000
    DRAW_EVERY = 1
    POINT_SIZE = 2
    SPACE_RADIUS = 220
    CORE_MASS = 2600.0 if not warped else 4000.0
    EVENT_HORIZON = 18.0 if not warped else 25.0
    CAPTURE_RADIUS = 6.0
    SOFTENING = 8.0
    RING_RADIUS = 85.0 if not warped else 90.0
    RING_THICKNESS = 18.0 if not warped else 20.0
    DT = 0.06 if not warped else 0.05
    DRAG = 0.996 if not warped else 0.995
    SWIRL_STRENGTH = 0.09
    RADIAL_PUSH = 0.015
    WARP_STRENGTH = 300
    TIME_SLOW = 2.5

    colors_map = {
        "field": "#7FDBFF",
        "ring": "#FFB000",
        "noise": "#C0C0C0",
        "jet": "#FF4D6D",
        "captured": "#111111",
        "core": "#FFFFFF",
        "horizon": "#7A00FF",
    }

    def random_ball_point(radius):
        return random_spherical_point(radius)

    def ring_point(radius, thickness):
        angle = random.uniform(0, 2 * math.pi)
        rr = radius + random.uniform(-thickness, thickness)
        return rr * math.cos(angle), rr * math.sin(angle), random.uniform(-thickness * 0.2, thickness * 0.2)

    def acceleration_to_mass(px, py, pz, cx, cy, cz, mass):
        dx = cx - px; dy = cy - py; dz = cz - pz
        r2 = dx * dx + dy * dy + dz * dz + SOFTENING**2
        r = math.sqrt(r2)
        a = mass / r2
        return a * dx / r, a * dy / r, a * dz / r, math.sqrt(dx * dx + dy * dy + dz * dz)

    def tangential_xy(x, y, strength):
        return -y * strength, x * strength, 0.0

    def build_target_pool():
        targets = []
        for _ in range(5):
            targets.append((*random_ball_point(SPACE_RADIUS), "field"))
        for _ in range(6):
            targets.append((*ring_point(RING_RADIUS, RING_THICKNESS), "ring"))
        for _ in range(2):
            targets.append((*random_ball_point(SPACE_RADIUS * 0.35), "noise"))
        sign = random.choice([-1, 1])
        targets.append((random.uniform(-10, 10), random.uniform(-10, 10), sign * random.uniform(120, 190), "jet"))
        return targets

    def warp_space(x, y, z):
        r = math.sqrt(x*x + y*y + z*z) + 1e-5
        warp = 1 / (1 + WARP_STRENGTH / r)
        return x * warp, y * warp, z * warp

    def time_dilation(r):
        return r / (r + EVENT_HORIZON * TIME_SLOW)

    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection="3d")
    plt.ion()
    scatter = ax.scatter([], [], [], s=POINT_SIZE)
    target_scatter = ax.scatter([], [], [], s=20, alpha=0.7)

    limit = SPACE_RADIUS * 1.1
    ax.set_xlim(-limit, limit); ax.set_ylim(-limit, limit); ax.set_zlim(-limit, limit)
    ax.set_box_aspect((1, 1, 1))
    ax.set_facecolor("#050609"); fig.patch.set_facecolor("#050609")
    ax.tick_params(colors="white")
    ax.set_xlabel("X", color="white"); ax.set_ylabel("Y", color="white"); ax.set_zlabel("Z", color="white")
    ax.set_title("Living Black Hole" if not warped else "Living Warped Black Hole", color="white")
    info_text = fig.text(0.02, 0.95, "", fontsize=10, family="monospace", verticalalignment="top", color="white")

    x, y, z = random_ball_point(SPACE_RADIUS * 0.8)
    vx, vy, vz = 0.0, 0.9 if not warped else 1.2, 0.0
    xs, ys, zs, colors = [], [], [], []
    captured_count = 0
    energy_values = []

    def update(frame):
        nonlocal x, y, z, vx, vy, vz, captured_count
        targets = build_target_pool()
        tx, ty, tz, ptype = random.choice(targets)
        ax1, ay1, az1, dist1 = acceleration_to_mass(x, y, z, 0.0, 0.0, 0.0, CORE_MASS)
        ax_total, ay_total, az_total = ax1, ay1, az1

        tax, tay, taz = tangential_xy(x, y, SWIRL_STRENGTH / max(dist1, 1))
        ax_total += tax; ay_total += tay; az_total += taz
        dx = tx - x; dy = ty - y; dz = tz - z
        ax_total += dx * RADIAL_PUSH * 0.002
        ay_total += dy * RADIAL_PUSH * 0.002
        az_total += dz * RADIAL_PUSH * 0.002

        dt_factor = time_dilation(dist1) if warped else 1.0
        vx = (vx + ax_total * DT * dt_factor) * DRAG
        vy = (vy + ay_total * DT * dt_factor) * DRAG
        vz = (vz + az_total * DT * dt_factor) * DRAG

        x += vx * DT * 18
        y += vy * DT * 18
        z += vz * DT * 18

        speed2 = vx * vx + vy * vy + vz * vz
        specific_energy = 0.5 * speed2 - CORE_MASS / max(dist1, 1.0)
        energy_values.append(specific_energy)

        if dist1 < CAPTURE_RADIUS:
            captured_count += 1
            x, y, z = ring_point(RING_RADIUS + random.uniform(5, 25), RING_THICKNESS * 1.5)
            vx, vy, vz = tangential_xy(x, y, 0.04)
            xs.append(x); ys.append(y); zs.append(z)
            colors.append(colors_map["captured"])
        else:
            wx, wy, wz = warp_space(x, y, z) if warped else (x, y, z)
            xs.append(wx); ys.append(wy); zs.append(wz)
            colors.append(colors_map["horizon"] if dist1 < EVENT_HORIZON else colors_map.get(ptype, "#FFFFFF"))

        scatter._offsets3d = (xs, ys, zs)
        scatter.set_color(colors)
        visible_targets = [(0.0, 0.0, 0.0, "core")] + build_target_pool()[:20]
        txs = [p[0] for p in visible_targets]; tys = [p[1] for p in visible_targets]; tzs = [p[2] for p in visible_targets]
        tcs = [colors_map.get(p[3], "#FFFFFF") for p in visible_targets]
        target_scatter._offsets3d = (txs, tys, tzs); target_scatter.set_color(tcs)

        avg_energy = float(np.mean(energy_values[-1000:])) if energy_values else 0.0
        info_text.set_text(
            ("Living Warped BH\n" if warped else "Living Black Hole\n") +
            "-----------------\n"
            f"distance     : {dist1:8.2f}\n"
            f"speed        : {math.sqrt(speed2):8.3f}\n"
            f"energy(avg)  : {avg_energy:8.3f}\n"
            f"captured     : {captured_count:8d}\n"
            f"points       : {len(xs):8d}\n"
            f"horizon      : {EVENT_HORIZON:8.2f}"
        )
        ax.view_init(elev=20 + 3 * math.sin(frame * 0.02), azim=(frame * 0.5) % 360)
        return scatter, target_scatter

    FuncAnimation(fig, update, frames=TOTAL_STEPS, interval=30, blit=False, cache_frame_data=False)
    plt.show()


# =========================================================
# 2D Living Raytracing
# =========================================================
def run_living_ray2d():
    WIDTH = 12.0
    HEIGHT = 8.0
    CENTER = np.array([0.0, 0.0])
    BLACK_HOLE_RADIUS = 0.65
    PHOTON_RING_RADIUS = 1.05
    ACCRETION_RING_INNER = 1.35
    ACCRETION_RING_OUTER = 2.25
    LENSING_STRENGTH = 0.12
    SOFTENING = 0.18
    CAPTURE_RADIUS = 0.72
    DT = 0.03
    MAX_STEPS = 650
    NUM_RAYS = 180
    ANIMATION_INTERVAL = 35
    DRAW_RAY_HEADS = True

    class Ray:
        def __init__(self, y0):
            self.pos = np.array([WIDTH / 2 - 0.3, y0], dtype=float)
            self.vel = np.array([-1.0, 0.0], dtype=float)
            self.path_x = [self.pos[0]]
            self.path_y = [self.pos[1]]
            self.captured = False
            self.finished = False
            self.hit_ring = False

        def step(self):
            if self.captured or self.finished:
                return
            rel = CENTER - self.pos
            r = np.linalg.norm(rel) + 1e-9
            direction = rel / r
            accel_mag = LENSING_STRENGTH / ((r + SOFTENING) ** 2)
            accel = direction * accel_mag
            self.vel += accel * DT
            speed = np.linalg.norm(self.vel) + 1e-9
            self.vel = self.vel / speed
            self.pos += self.vel * DT * 1.25
            self.path_x.append(self.pos[0]); self.path_y.append(self.pos[1])
            if r < CAPTURE_RADIUS:
                self.captured = True
                return
            if ACCRETION_RING_INNER <= r <= ACCRETION_RING_OUTER:
                self.hit_ring = True
            if self.pos[0] < -WIDTH / 2 or abs(self.pos[1]) > HEIGHT / 2:
                self.finished = True

    def make_rays():
        ys = np.linspace(-HEIGHT / 2 + 0.25, HEIGHT / 2 - 0.25, NUM_RAYS)
        return [Ray(y) for y in ys]

    def circle_xy(radius, n=400):
        t = np.linspace(0, 2 * np.pi, n)
        return radius * np.cos(t), radius * np.sin(t)

    def draw_static_scene(ax):
        bx, by = circle_xy(BLACK_HOLE_RADIUS)
        ax.fill(bx, by, color="black", zorder=8)
        px, py = circle_xy(PHOTON_RING_RADIUS)
        ax.plot(px, py, color="#8fd3ff", lw=2.2, alpha=0.9, zorder=7)
        outer_x, outer_y = circle_xy(ACCRETION_RING_OUTER)
        inner_x, inner_y = circle_xy(ACCRETION_RING_INNER)
        ax.fill(outer_x, outer_y, color="#ff6a00", alpha=0.22, zorder=2)
        ax.fill(inner_x, inner_y, color="white", zorder=3)
        ax.fill(inner_x, inner_y, color="black", zorder=4)
        hot_x, hot_y = circle_xy((ACCRETION_RING_INNER + ACCRETION_RING_OUTER) * 0.5)
        ax.plot(hot_x, hot_y, color="#ffd166", lw=2, alpha=0.85, zorder=5)

    rays = make_rays()
    fig, ax = plt.subplots(figsize=(11, 8), facecolor="black")
    ax.set_facecolor("black")
    ax.set_xlim(-WIDTH / 2, WIDTH / 2); ax.set_ylim(-HEIGHT / 2, HEIGHT / 2)
    ax.set_aspect("equal"); ax.axis("off")
    info = fig.text(0.02, 0.95, "", color="white", fontsize=11, family="monospace", verticalalignment="top")
    ray_lines, ray_heads = [], []
    for _ in rays:
        line, = ax.plot([], [], lw=1.0, color="#6ee7ff", alpha=0.72, zorder=1)
        ray_lines.append(line)
        if DRAW_RAY_HEADS:
            head, = ax.plot([], [], marker="o", ms=2.2, color="#ffffff", alpha=0.75, zorder=9)
        else:
            head, = ax.plot([], [], alpha=0.0)
        ray_heads.append(head)
    center_glow = [ax.plot([], [], lw=1.6, color="#ffd166", alpha=0.0, zorder=6)[0] for _ in rays]

    def init():
        draw_static_scene(ax)
        ax.set_title("Living Ray Field", color="white", fontsize=20, pad=16)
        return ray_lines + ray_heads + center_glow

    def update(frame):
        active = captured = ring_hits = 0
        for i, ray in enumerate(rays):
            if not ray.finished and not ray.captured:
                ray.step()
            x = ray.path_x; y = ray.path_y
            ray_lines[i].set_data(x, y)
            if DRAW_RAY_HEADS and x and y and not ray.captured:
                ray_heads[i].set_data([x[-1]], [y[-1]])
            else:
                ray_heads[i].set_data([], [])

            if len(x) > 2:
                dist_now = math.sqrt(ray.pos[0] ** 2 + ray.pos[1] ** 2)
                if dist_now < ACCRETION_RING_OUTER * 1.4 or ray.hit_ring:
                    center_glow[i].set_alpha(0.75)
                    center_glow[i].set_data(x, y)
                else:
                    center_glow[i].set_alpha(0.0)
                    center_glow[i].set_data([], [])

            if not ray.finished and not ray.captured: active += 1
            if ray.captured: captured += 1
            if ray.hit_ring: ring_hits += 1
            if ray.captured:
                ray_lines[i].set_color("#2b0a3d")
                ray_lines[i].set_alpha(0.35)
                center_glow[i].set_alpha(0.0)
                ray_heads[i].set_data([], [])

        info.set_text(
            "Living Ray Field\n"
            "----------------\n"
            f"Rays active   : {active:3d}\n"
            f"Rays captured : {captured:3d}\n"
            f"Ring contacts : {ring_hits:3d}\n"
            f"Lensing       : {LENSING_STRENGTH:.3f}\n"
            f"Horizon-ish   : {CAPTURE_RADIUS:.2f}"
        )
        return ray_lines + ray_heads + center_glow

    FuncAnimation(fig, update, init_func=init, frames=MAX_STEPS, interval=ANIMATION_INTERVAL,
                  blit=False, repeat=False, cache_frame_data=False)
    plt.show()


# =========================================================
# Start
# =========================================================
if __name__ == "__main__":
    if MODE == "living_star":
        run_living_star()
    elif MODE == "living_universe":
        run_living_freefield(universe=True)
    elif MODE in ("living_freefield", "living_field"):
        run_living_freefield(universe=False)
    elif MODE == "living_breathing":
        run_living_breathing()
    elif MODE == "living_blackhole":
        run_living_blackhole(warped=False)
    elif MODE == "living_warped":
        run_living_blackhole(warped=True)
    elif MODE == "living_ray2d":
        run_living_ray2d()
    else:
        raise ValueError(f"Unbekannter MODE: {MODE}")

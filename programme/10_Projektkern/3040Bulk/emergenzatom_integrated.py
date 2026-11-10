
import argparse
import math
import random

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401


# =========================================================
# GEMEINSAME HILFSFUNKTIONEN
# =========================================================
def growth_factor(step, max_steps, start=0.15, end=1.0):
    """Sanftes Wachstum des verfügbaren Raums."""
    t = min(step / max_steps, 1.0)
    return start + (end - start) * (1 - math.exp(-5 * t)) / (1 - math.exp(-5))


def energy_metric(x, y, z):
    """Spielerische Energie-Metrik = Abstand vom Ursprung."""
    return math.sqrt(x * x + y * y + z * z)


def voxel_index(x, y, z, voxel_size):
    return (
        int(x // voxel_size),
        int(y // voxel_size),
        int(z // voxel_size),
    )


def random_spherical_point(radius):
    """Zufälliger Punkt in alle Richtungen, ungefähr kugelförmig."""
    theta = random.uniform(0, 2 * math.pi)
    phi = math.acos(random.uniform(-1, 1))
    r = radius * (random.random() ** (1 / 3))
    x = r * math.sin(phi) * math.cos(theta)
    y = r * math.sin(phi) * math.sin(theta)
    z = r * math.cos(phi)
    return x, y, z


def random_stretched_point(radius, stretch=(1.6, 1.2, 1.0)):
    """Zufälliger Punkt in alle Richtungen, aber gedehnt."""
    x, y, z = random_spherical_point(radius)
    return x * stretch[0], y * stretch[1], z * stretch[2]


# =========================================================
# MODUS 1: FREIES 3D-FELD (aus emergenzatom weitergebaut)
# =========================================================
PARTICLE_COLORS = {
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
PARTICLE_ORDER = list(PARTICLE_COLORS.keys())

TOTAL_STEPS_3D = 100000
SPACE_RADIUS = 120
USE_GROWTH = True
STRETCH = (1.8, 1.4, 1.2)
USE_SECOND_ANCHOR = True
ANCHOR_1 = (0, 0, 0)
ANCHOR_2 = (55, -35, 30)
ANCHOR_WEIGHT_1 = 3
ANCHOR_WEIGHT_2 = 2
FIELD_WEIGHT = 6
DRIFT_WEIGHT = 4
QUANTUM_WEIGHT = 2
MEMORY_WEIGHT = 2
FACTOR_CHOICES = [1.55, 1.7, 1.85, 2.0]
VOXEL_SIZE = 10
DRAW_EVERY_3D = 300
POINT_SIZE_3D = 2


def build_targets(g, history_points):
    radius = SPACE_RADIUS * g
    targets = []

    for _ in range(ANCHOR_WEIGHT_1):
        targets.append((*ANCHOR_1, "anchor_1"))

    if USE_SECOND_ANCHOR:
        scaled_anchor_2 = tuple(a * g for a in ANCHOR_2)
        for _ in range(ANCHOR_WEIGHT_2):
            targets.append((*scaled_anchor_2, "anchor_2"))

    for _ in range(FIELD_WEIGHT):
        targets.append((*random_stretched_point(radius, stretch=STRETCH), "field"))

    for _ in range(DRIFT_WEIGHT):
        targets.append((*random_stretched_point(radius * 1.25, stretch=STRETCH), "drift"))

    for _ in range(QUANTUM_WEIGHT):
        qx = random.uniform(-15, 15) * g
        qy = random.uniform(-15, 15) * g
        qz = random.uniform(-15, 15) * g
        targets.append((qx, qy, qz, "quantum"))

    if len(history_points) > 30:
        sample_count = min(8, len(history_points))
        for hx, hy, hz in random.sample(history_points, sample_count):
            targets.append((hx, hy, hz, "memory"))

    targets.append((*random_stretched_point(radius * 0.7, stretch=STRETCH), "echo"))
    targets.append((*random_stretched_point(radius * 0.4, stretch=(2.0, 2.0, 0.8)), "noise"))

    sx, sy, sz = random_stretched_point(radius * 0.5, stretch=(1.2, 1.2, 0.5))
    targets.append((sx, sy, -abs(sz), "shadow"))
    targets.append((*random_stretched_point(radius * 0.9, stretch=(1.0, 1.0, 1.6)), "plasma"))

    visible_targets = []
    seen = set()
    for t in targets:
        key = (round(t[0], 3), round(t[1], 3), round(t[2], 3), t[3])
        if key not in seen:
            visible_targets.append(t)
            seen.add(key)

    return targets, visible_targets


def run_field_3d():
    plt.ion()
    fig = plt.figure(figsize=(13, 9))
    ax = fig.add_subplot(111, projection="3d")

    scatter = ax.scatter([], [], [], s=POINT_SIZE_3D)
    target_scatter = ax.scatter([], [], [], s=40, alpha=0.95)

    limit = SPACE_RADIUS * max(STRETCH) * 1.2
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.set_zlim(-limit, limit)
    ax.set_box_aspect((1, 1, 1))
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title("Freies 3D-Feld mit Fixpunkten")

    theory_text = fig.text(
        0.015, 0.96, "", fontsize=10, verticalalignment="top", family="monospace"
    )

    legend_handles = [
        Line2D([0], [0], marker='o', color='w', label=name,
               markerfacecolor=color, markersize=8)
        for name, color in PARTICLE_COLORS.items()
    ]
    ax.legend(handles=legend_handles, loc="upper right", bbox_to_anchor=(1.22, 1.0), title="Teilchentypen")

    x = y = z = 0.0
    xs, ys, zs = [], [], []
    point_colors = []

    occupied_voxels = set()
    field_counter = {}
    particle_counter = {name: 0 for name in PARTICLE_ORDER}
    energy_values = []
    history_points = []

    print("Freies Feld mit 1–2 Fixpunkten läuft ... STRG+C zum Beenden")

    try:
        for i in range(TOTAL_STEPS_3D):
            g = growth_factor(i, TOTAL_STEPS_3D) if USE_GROWTH else 1.0
            targets, visible_targets = build_targets(g, history_points)

            px, py, pz, particle_type = random.choice(targets)
            factor = random.choice(FACTOR_CHOICES)

            x = (x + px) / factor
            y = (y + py) / factor
            z = (z + pz) / factor

            x *= 1.0015
            y *= 1.0012
            z *= 1.0010

            xs.append(x)
            ys.append(y)
            zs.append(z)
            point_colors.append(PARTICLE_COLORS[particle_type])
            particle_counter[particle_type] += 1

            energy_values.append(energy_metric(x, y, z))

            vox = voxel_index(x, y, z, VOXEL_SIZE)
            occupied_voxels.add(vox)
            field_counter[vox] = field_counter.get(vox, 0) + 1

            if i % 150 == 0:
                history_points.append((x, y, z))
                if len(history_points) > 600:
                    history_points.pop(0)

            if i % DRAW_EVERY_3D == 0 and i > 0:
                scatter._offsets3d = (xs, ys, zs)
                scatter.set_color(point_colors)

                tx = [p[0] for p in visible_targets]
                ty = [p[1] for p in visible_targets]
                tz = [p[2] for p in visible_targets]
                tc = [PARTICLE_COLORS[p[3]] for p in visible_targets]
                target_scatter._offsets3d = (tx, ty, tz)
                target_scatter.set_color(tc)

                avg_energy = float(np.mean(energy_values[-1000:])) if energy_values else 0.0
                density = len(xs) / max(len(occupied_voxels), 1)
                dominant_voxel = max(field_counter, key=field_counter.get)
                dominant_particle = max(particle_counter, key=particle_counter.get)

                theory_text.set_text(
                    "Freies Feld\n"
                    "-----------\n"
                    f"Energie     : {avg_energy:8.2f}\n"
                    f"Lage        : ({x:7.2f}, {y:7.2f}, {z:7.2f})\n"
                    f"Feld        : {len(occupied_voxels):8d} Voxel\n"
                    f"Emergenz    : Expansion / Cluster / Drift\n"
                    f"Information : {len(occupied_voxels):8d}\n"
                    f"Ordnung     : {density:8.2f}\n"
                    f"Wachstum    : {g:8.2f}\n"
                    f"TopPartikel : {dominant_particle}\n"
                    f"DominantVox : {dominant_voxel}"
                )

                ax.set_title(
                    f"Freies 3D-Feld | Schritt {i} | Wachstum {g:.2f} | Ordnung {density:.2f}"
                )
                plt.draw()
                plt.pause(0.001)

    except KeyboardInterrupt:
        print("\nBeendet 👋")

    avg_energy_total = float(np.mean(energy_values)) if energy_values else 0.0
    density_final = len(xs) / max(len(occupied_voxels), 1)
    dominant_voxel = max(field_counter, key=field_counter.get) if field_counter else None

    print("\n--- Abschlussanalyse ---")
    print(f"Gesamtpunkte : {len(xs)}")
    print(f"Belegte Voxel: {len(occupied_voxels)}")
    print(f"Ordnung      : {density_final:.2f}")
    print(f"Energie Ø    : {avg_energy_total:.2f}")
    print(f"Dominant Vox : {dominant_voxel}")
    print("\n--- Teilchenzählung ---")
    for name in PARTICLE_ORDER:
        print(f"{name:>10}: {particle_counter[name]}")

    plt.ioff()
    plt.show()


# =========================================================
# MODUS 2: BLACK-HOLE MINI-ENGINE (dein 2D-Ray-System)
# =========================================================
class BHConfig:
    WIDTH = 10
    HEIGHT = 6
    DT = 0.03
    STEPS = 600
    NUM_RAYS = 180
    RAY_SPEED = 1.0
    START_X = 4.5
    BLACK_HOLE_RADIUS = 0.5
    PHOTON_RING_RADIUS = 0.9
    LENSING = 0.15
    INTERVAL = 30
    BG_COLOR = "black"
    RAY_COLOR = "cyan"
    CAPTURED_COLOR = "purple"
    RING_COLOR = "orange"


class Ray:
    def __init__(self, y):
        self.pos = np.array([BHConfig.START_X, y], dtype=float)
        self.vel = np.array([-BHConfig.RAY_SPEED, 0.0], dtype=float)
        self.path_x = [self.pos[0]]
        self.path_y = [self.pos[1]]
        self.captured = False
        self.active = True

    def step(self, center):
        if not self.active or self.captured:
            return

        rel = center - self.pos
        dist = np.linalg.norm(rel) + 1e-9
        direction = rel / dist

        accel = direction * (BHConfig.LENSING / (dist ** 2))
        self.vel += accel * BHConfig.DT

        speed = np.linalg.norm(self.vel) + 1e-9
        self.vel = self.vel / speed * BHConfig.RAY_SPEED
        self.pos += self.vel * BHConfig.DT

        self.path_x.append(self.pos[0])
        self.path_y.append(self.pos[1])

        if dist < BHConfig.BLACK_HOLE_RADIUS:
            self.captured = True
            self.active = False
            return

        if (
            self.pos[0] < -BHConfig.WIDTH / 2
            or self.pos[0] > BHConfig.WIDTH / 2
            or self.pos[1] < -BHConfig.HEIGHT / 2
            or self.pos[1] > BHConfig.HEIGHT / 2
        ):
            self.active = False


class World:
    def __init__(self):
        self.center = np.array([0.0, 0.0], dtype=float)
        self.rays = []
        self.frame = 0

    def reset(self):
        self.rays.clear()
        ys = np.linspace(-BHConfig.HEIGHT / 2, BHConfig.HEIGHT / 2, BHConfig.NUM_RAYS)
        for y in ys:
            self.rays.append(Ray(float(y)))
        self.frame = 0


class Engine:
    def __init__(self, world):
        self.world = world

    def step(self):
        for ray in self.world.rays:
            ray.step(self.world.center)
        self.world.frame += 1


class Renderer:
    def __init__(self, engine):
        self.engine = engine
        self.world = engine.world

        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.ax.set_facecolor(BHConfig.BG_COLOR)
        self.ax.set_xlim(-BHConfig.WIDTH / 2, BHConfig.WIDTH / 2)
        self.ax.set_ylim(-BHConfig.HEIGHT / 2, BHConfig.HEIGHT / 2)
        self.ax.set_aspect("equal")
        self.ax.axis("off")

        self.info = self.fig.text(
            0.02, 0.95, "", color="white", fontsize=10, family="monospace",
            verticalalignment="top"
        )

        self.lines = []
        for _ in self.world.rays:
            line, = self.ax.plot([], [], color=BHConfig.RAY_COLOR, linewidth=1)
            self.lines.append(line)

        self._draw_static_scene()

    def _draw_static_scene(self):
        circle = plt.Circle((0, 0), BHConfig.BLACK_HOLE_RADIUS, color="black", zorder=5)
        self.ax.add_patch(circle)

        ring = plt.Circle(
            (0, 0),
            BHConfig.PHOTON_RING_RADIUS,
            color=BHConfig.RING_COLOR,
            fill=False,
            linewidth=2,
            zorder=4,
        )
        self.ax.add_patch(ring)

        self.ax.set_title("Mini Engine Black Hole", color="white", pad=14)

    def active_count(self):
        return sum(1 for r in self.world.rays if r.active)

    def captured_count(self):
        return sum(1 for r in self.world.rays if r.captured)

    def update(self, frame):
        self.engine.step()

        for i, ray in enumerate(self.world.rays):
            self.lines[i].set_data(ray.path_x, ray.path_y)
            if ray.captured:
                self.lines[i].set_color(BHConfig.CAPTURED_COLOR)
            else:
                self.lines[i].set_color(BHConfig.RAY_COLOR)

        self.info.set_text(
            "Mini Engine\n"
            "-----------\n"
            f"Frame      : {self.world.frame:4d}\n"
            f"Active Rays: {self.active_count():4d}\n"
            f"Captured   : {self.captured_count():4d}\n"
            f"Lensing    : {BHConfig.LENSING:4.2f}\n"
            f"BH Radius  : {BHConfig.BLACK_HOLE_RADIUS:4.2f}"
        )
        return self.lines

    def run(self):
        self.anim = FuncAnimation(
            self.fig,
            self.update,
            frames=BHConfig.STEPS,
            interval=BHConfig.INTERVAL,
            blit=False,
            cache_frame_data=False,
        )
        plt.show()


def run_black_hole_2d():
    world = World()
    world.reset()
    engine = Engine(world)
    renderer = Renderer(engine)
    renderer.run()


# =========================================================
# MAIN
# =========================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Kombinierte Datei: freies 3D-Feld oder Black-Hole-Mini-Engine"
    )
    parser.add_argument(
        "--mode",
        choices=["field3d", "blackhole2d"],
        default="field3d",
        help="Welcher Modus gestartet werden soll.",
    )
    args = parser.parse_args()

    if args.mode == "blackhole2d":
        run_black_hole_2d()
    else:
        run_field_3d()

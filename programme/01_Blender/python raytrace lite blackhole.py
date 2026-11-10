import math import numpy as np import matplotlib.pyplot as plt from matplotlib.animation import FuncAnimation

=========================================================

Black Hole Ray Tracing Lite

---------------------------------------------------------

Nicht volle Allgemeine Relativität.

Aber: bildlich brauchbare, physikalisch inspirierte Light-Ray-

Krümmung um ein zentrales Objekt mit Akkretionsring.



Idee:

- viele Lichtstrahlen starten rechts beim Beobachter

- sie laufen nach links durchs Bild

- nahe dem Zentrum werden sie radial abgelenkt

- ein leuchtender Ring gibt Orientierung

- Strahlen, die zu nah kommen, gelten als "eingefangen"

=========================================================

-----------------------------

Szene-Parameter

-----------------------------

WIDTH = 12.0 HEIGHT = 8.0

CENTER = np.array([0.0, 0.0]) BLACK_HOLE_RADIUS = 0.65 PHOTON_RING_RADIUS = 1.05 ACCRETION_RING_INNER = 1.35 ACCRETION_RING_OUTER = 2.25

Krümmungs-Stärke (rein visuell / inspiriert)

LENSING_STRENGTH = 0.12 SOFTENING = 0.18 CAPTURE_RADIUS = 0.72

Integrations-Parameter

DT = 0.03 MAX_STEPS = 650 NUM_RAYS = 180

Animation

ANIMATE = True ANIMATION_INTERVAL = 35 DRAW_RAY_HEADS = True

-----------------------------

Lichtstrahl-Klasse

-----------------------------

class Ray: def init(self, y0: float): self.pos = np.array([WIDTH / 2 - 0.3, y0], dtype=float) self.vel = np.array([-1.0, 0.0], dtype=float) self.path_x = [self.pos[0]] self.path_y = [self.pos[1]] self.captured = False self.finished = False self.hit_ring = False

def step(self):
    if self.captured or self.finished:
        return

    rel = CENTER - self.pos
    r = np.linalg.norm(rel) + 1e-9
    direction = rel / r

    # "Lensing": stärkere Krümmung nahe am Zentrum
    accel_mag = LENSING_STRENGTH / ((r + SOFTENING) ** 2)
    accel = direction * accel_mag

    # Geschwindigkeit leicht normieren, damit es wie Lichtbahnen wirkt
    self.vel += accel * DT
    speed = np.linalg.norm(self.vel) + 1e-9
    self.vel = self.vel / speed

    self.pos += self.vel * DT * 1.25
    self.path_x.append(self.pos[0])
    self.path_y.append(self.pos[1])

    # Capture / Horizon-artige Zone
    if r < CAPTURE_RADIUS:
        self.captured = True
        return

    # Akkretionsring getroffen?
    if ACCRETION_RING_INNER <= r <= ACCRETION_RING_OUTER:
        self.hit_ring = True

    # Bild verlassen?
    if self.pos[0] < -WIDTH / 2 or abs(self.pos[1]) > HEIGHT / 2:
        self.finished = True

-----------------------------

Hilfsfunktionen

-----------------------------

def make_rays() -> list[Ray]: ys = np.linspace(-HEIGHT / 2 + 0.25, HEIGHT / 2 - 0.25, NUM_RAYS) return [Ray(y) for y in ys]

def circle_xy(radius: float, n: int = 400): t = np.linspace(0, 2 * np.pi, n) return radius * np.cos(t), radius * np.sin(t)

def draw_static_scene(ax): # schwarzes Loch bx, by = circle_xy(BLACK_HOLE_RADIUS) ax.fill(bx, by, color="black", zorder=8)

# Photon-Ring
px, py = circle_xy(PHOTON_RING_RADIUS)
ax.plot(px, py, color="#8fd3ff", lw=2.2, alpha=0.9, zorder=7)

# Akkretionsscheibe (vereinfacht als Ring)
outer_x, outer_y = circle_xy(ACCRETION_RING_OUTER)
inner_x, inner_y = circle_xy(ACCRETION_RING_INNER)

ax.fill(outer_x, outer_y, color="#ff6a00", alpha=0.22, zorder=2)
ax.fill(inner_x, inner_y, color="white", zorder=3)
ax.fill(inner_x, inner_y, color="black", zorder=4)

# zusätzlicher heißer innerer Ring
hot_x, hot_y = circle_xy((ACCRETION_RING_INNER + ACCRETION_RING_OUTER) * 0.5)
ax.plot(hot_x, hot_y, color="#ffd166", lw=2, alpha=0.85, zorder=5)

-----------------------------

Simulation vorbereiten

-----------------------------

rays = make_rays()

fig, ax = plt.subplots(figsize=(11, 8), facecolor="black") ax.set_facecolor("black") ax.set_xlim(-WIDTH / 2, WIDTH / 2) ax.set_ylim(-HEIGHT / 2, HEIGHT / 2) ax.set_aspect("equal") ax.axis("off")

info = fig.text( 0.02, 0.95, "", color="white", fontsize=11, family="monospace", verticalalignment="top", )

Linienobjekte pro Ray

ray_lines = [] ray_heads = [] for _ in rays: line, = ax.plot([], [], lw=1.0, color="#6ee7ff", alpha=0.72, zorder=1) ray_lines.append(line) if DRAW_RAY_HEADS: head, = ax.plot([], [], marker="o", ms=2.2, color="#ffffff", alpha=0.75, zorder=9) else: head, = ax.plot([], [], alpha=0.0) ray_heads.append(head)

Farbigere Strahlen nahe der Mitte

CENTER_GLOW = [ ax.plot([], [], lw=1.6, color="#ffd166", alpha=0.0, zorder=6)[0] for _ in rays ]

def init(): draw_static_scene(ax) title = "Black Hole Ray Tracing Lite" ax.set_title(title, color="white", fontsize=20, pad=16) return ray_lines + ray_heads + CENTER_GLOW

def update(frame): active = 0 captured = 0 ring_hits = 0

for i, ray in enumerate(rays):
    if not ray.finished and not ray.captured:
        ray.step()

    x = ray.path_x
    y = ray.path_y
    ray_lines[i].set_data(x, y)

    if DRAW_RAY_HEADS and x and y and not ray.captured:
        ray_heads[i].set_data([x[-1]], [y[-1]])
    else:
        ray_heads[i].set_data([], [])

    # Highlight für ringnahe / stark gebogene Strahlen
    if len(x) > 2:
        dist_now = math.sqrt(ray.pos[0] ** 2 + ray.pos[1] ** 2)
        if dist_now < ACCRETION_RING_OUTER * 1.4 or ray.hit_ring:
            CENTER_GLOW[i].set_alpha(0.75)
            CENTER_GLOW[i].set_data(x, y)
        else:
            CENTER_GLOW[i].set_alpha(0.0)
            CENTER_GLOW[i].set_data([], [])

    if not ray.finished and not ray.captured:
        active += 1
    if ray.captured:
        captured += 1
    if ray.hit_ring:
        ring_hits += 1

    # Eingefangene Strahlen abdunkeln
    if ray.captured:
        ray_lines[i].set_color("#2b0a3d")
        ray_lines[i].set_alpha(0.35)
        CENTER_GLOW[i].set_alpha(0.0)
        ray_heads[i].set_data([], [])

info.set_text(
    "Physikalisch inspiriert, nicht exakte GR\n"
    f"Rays active   : {active:3d}\n"
    f"Rays captured : {captured:3d}\n"
    f"Ring contacts : {ring_hits:3d}\n"
    f"Lensing       : {LENSING_STRENGTH:.3f}\n"
    f"Horizon-ish   : {CAPTURE_RADIUS:.2f}"
)

return ray_lines + ray_heads + CENTER_GLOW

if name == "main": if ANIMATE: anim = FuncAnimation( fig, update, init_func=init, frames=MAX_STEPS, interval=ANIMATION_INTERVAL, blit=False, repeat=False, cache_frame_data=False, ) plt.show() else: init() for _ in range(MAX_STEPS): update(0) plt.show()
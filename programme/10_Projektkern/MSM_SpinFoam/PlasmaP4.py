import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ============================================================
# Zero-Lumi Plasma P4 Visualizer
# PyDroid-kompatible Magazin-Version
# ============================================================

np.random.seed(42)

NUM_STREAMS = 45
POINTS_PER_STREAM = 90
NUM_PARTICLES = 180
FRAMES = 360

TAIL_LENGTH = 22.0
HEAD_RADIUS = 2.0

X_MIN, X_MAX = -24, 6
Y_MIN, Y_MAX = -8, 8
Z_MIN, Z_MAX = -6, 6


def normalize(v):
    v = np.asarray(v, dtype=float)
    return (v - v.min()) / (v.max() - v.min() + 1e-9)


def state_lambda(x, y, z, t):
    r = np.sqrt(x*x + y*y + z*z)
    return np.sin(0.45 * r - 0.06 * t) + 0.35 * np.cos(0.9 * y + 0.04 * t)


def plasma_head(theta, phi, pulse):
    r = HEAD_RADIUS * (1.0 + 0.07 * np.sin(4 * theta + pulse))
    x = r * np.cos(theta) * np.sin(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(phi)
    return x, y, z


# ------------------------------------------------------------
# Schweiflinien
# ------------------------------------------------------------
streams = []

for i in range(NUM_STREAMS):
    s = np.linspace(0, 1, POINTS_PER_STREAM)

    angle = np.random.uniform(0, 2 * np.pi)
    radius = np.random.uniform(0.1, 1.8)

    y0 = radius * np.cos(angle)
    z0 = radius * np.sin(angle)

    x = -TAIL_LENGTH * s

    swirl = 1.0 + 2.8 * s
    phase = np.random.uniform(0, 2 * np.pi)

    y = y0 + 0.9 * s * np.sin(5.5 * s + phase)
    y += 0.18 * swirl * np.sin(14 * s + phase)

    z = z0 + 0.7 * s * np.cos(4.8 * s + phase)
    z += 0.14 * swirl * np.cos(11 * s + phase)

    y += np.random.normal(0, 0.15, POINTS_PER_STREAM) * s
    z += np.random.normal(0, 0.15, POINTS_PER_STREAM) * s

    streams.append((x, y, z, phase))


# ------------------------------------------------------------
# Partikel
# ------------------------------------------------------------
particle_s = np.random.rand(NUM_PARTICLES)
particle_phase = np.random.uniform(0, 2 * np.pi, NUM_PARTICLES)
particle_offset_y = np.random.normal(0, 1.8, NUM_PARTICLES)
particle_offset_z = np.random.normal(0, 1.4, NUM_PARTICLES)


# ------------------------------------------------------------
# Plot
# ------------------------------------------------------------
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection="3d")

fig.patch.set_facecolor("black")
ax.set_facecolor("black")

ax.set_xlim(X_MIN, X_MAX)
ax.set_ylim(Y_MIN, Y_MAX)
ax.set_zlim(Z_MIN, Z_MAX)

ax.set_xlabel("x Raumachse", color="white")
ax.set_ylabel("y Raumachse", color="white")
ax.set_zlabel("z Raumachse", color="white")

ax.set_title(
    "Zero-Lumi Plasma P4 Magazin Visualizer",
    color="white",
    pad=18
)

ax.tick_params(colors="white")
ax.grid(True)

# Linien
stream_lines = []
for _ in streams:
    line, = ax.plot([], [], [], linewidth=0.8, alpha=0.75)
    stream_lines.append(line)

# Partikel
particles = ax.scatter([], [], [], s=8, alpha=0.8)

# Kopf
theta = np.linspace(0, 2 * np.pi, 36)
phi = np.linspace(0, np.pi, 18)
TH, PH = np.meshgrid(theta, phi)
head_surface = [None]

# P4 Marker
p4_point = ax.scatter([], [], [], s=90, marker="o")

p4_text = ax.text(
    0, 0, 0,
    "",
    color="white",
    fontsize=9
)

info_text = ax.text2D(
    0.03,
    0.04,
    "",
    transform=ax.transAxes,
    color="white",
    fontsize=8
)


def update(frame):
    global particles

    ax.view_init(
        elev=18 + 5 * np.sin(frame * 0.015),
        azim=-68 + frame * 0.12
    )

    # Kopf neu zeichnen
    if head_surface[0] is not None:
        head_surface[0].remove()

    pulse = frame * 0.08
    hx, hy, hz = plasma_head(TH, PH, pulse)

    head_surface[0] = ax.plot_surface(
        hx, hy, hz,
        alpha=0.24,
        linewidth=0,
        shade=True
    )

    # Schweiflinien
    for idx, (x, y, z, phase) in enumerate(streams):
        yy = y + 0.25 * np.sin(0.4 * x + frame * 0.08 + phase)
        zz = z + 0.20 * np.cos(0.4 * x + frame * 0.07 + phase)

        lam = state_lambda(x, yy, zz, frame)
        c = plt.cm.plasma(np.mean(normalize(lam)))

        stream_lines[idx].set_data(x, yy)
        stream_lines[idx].set_3d_properties(zz)
        stream_lines[idx].set_color(c)

    # Partikel
    s = (particle_s + frame * 0.004) % 1.0

    px = -TAIL_LENGTH * s
    py = particle_offset_y * s
    py += 0.7 * s * np.sin(8 * s + particle_phase + frame * 0.045)

    pz = particle_offset_z * s
    pz += 0.6 * s * np.cos(7 * s + particle_phase + frame * 0.04)

    lam_p = state_lambda(px, py, pz, frame)

    particles.remove()
    particles = ax.scatter(
        px, py, pz,
        s=8 + 14 * normalize(lam_p),
        c=plt.cm.cool(normalize(lam_p)),
        alpha=0.75
    )

    # P4 Marker
    p4_x = -1.6 + 0.5 * np.sin(frame * 0.025)
    p4_y = 1.2 * np.cos(frame * 0.035)
    p4_z = 0.9 * np.sin(frame * 0.04)

    p4_lambda = state_lambda(p4_x, p4_y, p4_z, frame)

    p4_point._offsets3d = ([p4_x], [p4_y], [p4_z])
    p4_point.set_color([plt.cm.spring(normalize(np.array([p4_lambda, -1, 1]))[0])])

    p4_text.set_position((p4_x, p4_y))
    p4_text.set_3d_properties(p4_z + 0.6)
    p4_text.set_text(
        "P4 = (x,y,z,λ)\n"
        f"x={p4_x:.2f}\n"
        f"y={p4_y:.2f}\n"
        f"z={p4_z:.2f}\n"
        f"λ={p4_lambda:.2f}"
    )

    info_text.set_text(
        "3D sichtbar: x, y, z\n"
        "λ = verborgener Zustandswert\n"
        "Deutung: Phase / Energie / ψ / ΔS / Feldkopplung\n"
        "Die Szene ist eine Projektion eines P4-Zustandsraums."
    )

    return stream_lines + [particles, p4_point, p4_text, info_text]


ani = FuncAnimation(
    fig,
    update,
    frames=FRAMES,
    interval=33,
    blit=False
)

plt.tight_layout()
plt.show()
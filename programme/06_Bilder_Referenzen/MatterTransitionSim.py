import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ============================================================
# Zero-Lumi Matter Transition Simulation
# ------------------------------------------------------------
# Idee:
# t0: Körper ist stabil links
# t1: Oberfläche löst sich auf
# t2: Struktur zerfällt in Partikel
# t3: Transit / Zeitversatz
# t4: Partikel sammeln sich rechts
# t5: Körper ist wieder stabil rechts
#
# Keine echte Physik-Teleportation,
# sondern eine visuelle Zustands-Simulation.
# ============================================================

np.random.seed(7)

# -----------------------------
# Grundeinstellungen
# -----------------------------
N_BODY = 1300          # Anzahl Körperpunkte
N_TRAIL = 600          # zusätzliche Transit-Partikel
FRAMES = 360           # Animationslänge
FPS = 30

LEFT_X = -4.0
RIGHT_X = 4.0

SAVE_GIF = False       # True = speichert GIF
GIF_NAME = "matter_transition.gif"


# -----------------------------
# Hilfsfunktionen
# -----------------------------
def smoothstep(edge0, edge1, x):
    """Weicher Übergang von 0 nach 1."""
    x = np.clip((x - edge0) / (edge1 - edge0), 0, 1)
    return x * x * (3 - 2 * x)


def make_human_points(n=1000, x_offset=0.0):
    """
    Erzeugt eine einfache menschliche Silhouette als Punktwolke.
    Kopf, Körper, Arme, Beine.
    """
    pts = []

    # Kopf: Kreis
    n_head = n // 6
    theta = np.random.rand(n_head) * 2 * np.pi
    r = 0.35 * np.sqrt(np.random.rand(n_head))
    x = x_offset + r * np.cos(theta)
    y = 1.65 + r * np.sin(theta)
    pts.append(np.column_stack([x, y]))

    # Torso: Ellipse/Rechteckmischung
    n_torso = n // 3
    y = np.random.uniform(0.2, 1.35, n_torso)
    width = 0.45 - 0.12 * (y - 0.2) / 1.15
    x = x_offset + np.random.uniform(-1, 1, n_torso) * width
    pts.append(np.column_stack([x, y]))

    # Arme
    n_arms = n // 5
    side = np.random.choice([-1, 1], n_arms)
    t = np.random.rand(n_arms)
    x = x_offset + side * (0.35 + 0.55 * t)
    y = 1.15 - 0.8 * t + np.random.normal(0, 0.05, n_arms)
    pts.append(np.column_stack([x, y]))

    # Beine
    n_legs = n - n_head - n_torso - n_arms
    side = np.random.choice([-1, 1], n_legs)
    t = np.random.rand(n_legs)
    x = x_offset + side * (0.13 + 0.22 * t) + np.random.normal(0, 0.04, n_legs)
    y = 0.2 - 1.2 * t
    pts.append(np.column_stack([x, y]))

    return np.vstack(pts)


# -----------------------------
# Start- und Zielkörper
# -----------------------------
body_left = make_human_points(N_BODY, LEFT_X)
body_right = make_human_points(N_BODY, RIGHT_X)

# Jede Materieeinheit bekommt ein zufälliges "Chaos-Ziel" im Transitbereich
chaos = np.column_stack([
    np.random.uniform(-1.2, 1.2, N_BODY),
    np.random.uniform(-1.4, 1.8, N_BODY)
])

# Zusätzliche Transit-Partikel
trail_x = np.random.uniform(LEFT_X, RIGHT_X, N_TRAIL)
trail_y = np.random.normal(0.25, 0.65, N_TRAIL)
trail_phase = np.random.rand(N_TRAIL) * 2 * np.pi


# -----------------------------
# Figure
# -----------------------------
fig, ax = plt.subplots(figsize=(14, 7))
fig.patch.set_facecolor("black")
ax.set_facecolor("#02040a")

ax.set_xlim(-6, 6)
ax.set_ylim(-1.5, 2.4)
ax.axis("off")

# Hauptpartikel
scatter_body = ax.scatter([], [], s=[], c=[], alpha=0.9)

# Transit-Schweif
scatter_trail = ax.scatter([], [], s=[], c=[], alpha=0.35)

# Text
title = ax.text(
    0, 2.15, "",
    color="white",
    ha="center",
    va="center",
    fontsize=16,
    fontweight="bold"
)

subtitle = ax.text(
    0, 1.95, "",
    color="#9fdcff",
    ha="center",
    va="center",
    fontsize=10
)

# Zeitlinie unten
ax.plot([-5.2, 5.2], [-1.25, -1.25], color="#4f7890", lw=1, alpha=0.5)

stage_positions = np.linspace(-5.0, 5.0, 6)
stage_labels = ["t0", "t1", "t2", "t3", "t4", "t5"]
stage_names = [
    "stabil",
    "auflösen",
    "zerfallen",
    "delay",
    "sammeln",
    "restauriert"
]

stage_texts = []

for sx, lab, name in zip(stage_positions, stage_labels, stage_names):
    ax.scatter([sx], [-1.25], s=35, edgecolor="#9fdcff", facecolor="black", lw=1)
    txt = ax.text(
        sx, -1.38,
        f"{lab}\n{name}",
        color="#bdeaff",
        ha="center",
        va="top",
        fontsize=8
    )
    stage_texts.append(txt)


# -----------------------------
# Animationslogik
# -----------------------------
def interpolate(a, b, t):
    return a * (1 - t) + b * t


def get_state(frame):
    """
    Erzeugt aktuellen Zustand der Partikel.
    """
    u = frame / (FRAMES - 1)

    # Phasen:
    # 0.00 - 0.20: stabil links
    # 0.20 - 0.42: Zerfall
    # 0.42 - 0.60: Transit / Delay
    # 0.60 - 0.82: Zusammenbau rechts
    # 0.82 - 1.00: stabil rechts

    dissolve = smoothstep(0.18, 0.42, u)
    reassemble = smoothstep(0.60, 0.82, u)

    # Erst von links nach Chaos
    pos_dis = interpolate(body_left, chaos, dissolve)

    # Dann von Chaos nach rechts
    pos_final = interpolate(pos_dis, body_right, reassemble)

    # Transitbewegung im Mittel
    drift = smoothstep(0.35, 0.70, u)
    pos_final[:, 0] += drift * 0.35 * np.sin(8 * u + np.arange(N_BODY) * 0.01)

    # Flimmern / Quanten-artige Unruhe während Zerfall und Aufbau
    chaos_strength = np.sin(np.pi * np.clip((u - 0.18) / 0.64, 0, 1))
    jitter = np.random.normal(0, 0.025 + 0.12 * chaos_strength, pos_final.shape)
    pos_final += jitter

    # Partikelgröße
    base_size = 8
    sizes = base_size + 18 * chaos_strength * np.random.rand(N_BODY)

    # Farben über Phasen
    colors = []

    for i in range(N_BODY):
        # außenliegende Partikel reagieren früher
        dist = np.linalg.norm(body_left[i] - np.array([LEFT_X, 0.5]))
        edge_factor = np.clip(dist / 1.4, 0, 1)

        glow = np.clip(dissolve + reassemble + edge_factor * dissolve, 0, 1)

        if u < 0.2:
            colors.append((0.75, 0.9, 1.0, 0.75))
        elif u < 0.6:
            colors.append((0.3 + 0.5 * glow, 0.75, 1.0, 0.75))
        elif u < 0.84:
            colors.append((0.6, 0.95, 1.0, 0.8))
        else:
            colors.append((0.8, 0.9, 1.0, 0.75))

    return pos_final, sizes, colors, u, chaos_strength


def update(frame):
    pos, sizes, colors, u, chaos_strength = get_state(frame)

    scatter_body.set_offsets(pos)
    scatter_body.set_sizes(sizes)
    scatter_body.set_color(colors)

    # Transit-Schweif sichtbar besonders in der Mitte
    transit_visibility = np.sin(np.pi * smoothstep(0.28, 0.75, u))
    transit_visibility *= 1 - smoothstep(0.78, 0.95, u)

    moving_trail_x = trail_x + 0.25 * np.sin(6 * u + trail_phase)
    moving_trail_y = trail_y + 0.18 * np.sin(10 * u + trail_phase * 1.7)

    trail_offsets = np.column_stack([moving_trail_x, moving_trail_y])
    trail_sizes = 2 + 18 * np.random.rand(N_TRAIL) * transit_visibility

    trail_colors = np.zeros((N_TRAIL, 4))
    trail_colors[:, 0] = 0.35
    trail_colors[:, 1] = 0.75
    trail_colors[:, 2] = 1.0
    trail_colors[:, 3] = 0.04 + 0.32 * transit_visibility * np.random.rand(N_TRAIL)

    scatter_trail.set_offsets(trail_offsets)
    scatter_trail.set_sizes(trail_sizes)
    scatter_trail.set_color(trail_colors)

    # Titel je nach Phase
    if u < 0.18:
        title.set_text("t0 — Materie stabil lokalisiert")
        subtitle.set_text("kohärente Körperstruktur")
    elif u < 0.42:
        title.set_text("t1 / t2 — Oberfläche löst sich auf")
        subtitle.set_text("Struktur zerfällt von außen nach innen in Partikel")
    elif u < 0.60:
        title.set_text("t3 — Transit mit Zeitversatz")
        subtitle.set_text("sichtbar bleibt nur ein Übergangsfeld / Partikelstrom")
    elif u < 0.82:
        title.set_text("t4 — Reassemblierung beginnt")
        subtitle.set_text("Partikel richten sich neu aus und bauen die Form zurück")
    else:
        title.set_text("t5 — Kohärenz wiederhergestellt")
        subtitle.set_text("die Struktur erscheint rechts erneut")

    return scatter_body, scatter_trail, title, subtitle


ani = FuncAnimation(
    fig,
    update,
    frames=FRAMES,
    interval=1000 / FPS,
    blit=False
)

plt.tight_layout()

if SAVE_GIF:
    ani.save(GIF_NAME, writer="pillow", fps=FPS)
    print(f"GIF gespeichert als: {GIF_NAME}")

plt.show()
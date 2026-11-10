import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ============================================================
# Zero-Lumi Plasma P4 Visualizer
# ------------------------------------------------------------
# Idee:
# - 3D-Plasma/Kometen-Schweif
# - Partikel bewegen sich vom "Kopf" in den Schweif
# - P4 ist ein zusätzlicher Zustandsmarker:
#       P4 = (x, y, z, lambda)
#
# Dabei ist lambda NICHT zwingend echte Zeit,
# sondern kann eine verborgene Zustandsdimension sein:
# Energie, Phase, Teilchenzustand, Feldkopplung, psi, DeltaS usw.
# ============================================================


# -----------------------------
# Grundeinstellungen
# -----------------------------
np.random.seed(42)

NUM_STREAMS = 90          # Anzahl der Schweiflinien
POINTS_PER_STREAM = 120   # Punkte pro Linie
NUM_PARTICLES = 450       # leuchtende Partikelpunkte
FRAMES = 360              # Animationslänge
TAIL_LENGTH = 22.0        # Länge des Schweifs
HEAD_RADIUS = 2.0         # Radius des Plasma-Kopfes

# Bildbereich
X_MIN, X_MAX = -24, 6
Y_MIN, Y_MAX = -8, 8
Z_MIN, Z_MAX = -6, 6


# -----------------------------
# Hilfsfunktionen
# -----------------------------
def normalize(v):
    v = np.asarray(v)
    return (v - v.min()) / (v.max() - v.min() + 1e-9)


def state_lambda(x, y, z, t):
    """
    Verborgene 4D-/Zustandskomponente.

    Das kann man interpretieren als:
    - lambda = Quantenphase
    - lambda = Feldkopplung
    - lambda = Energiezustand
    - lambda = DeltaS
    - lambda = psi-Zustand

    Hier als schöne, bewegte Wellenfunktion gebaut.
    """
    r = np.sqrt(x*x + y*y + z*z)
    lam = np.sin(0.45 * r - 0.06 * t) + 0.35 * np.cos(0.9 * y + 0.04 * t)
    return lam


def plasma_head(theta, phi, pulse):
    """
    Erzeugt Oberfläche eines Plasma-Kopfes.
    """
    r = HEAD_RADIUS * (1.0 + 0.07 * np.sin(4 * theta + pulse))
    x = r * np.cos(theta) * np.sin(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(phi)
    return x, y, z


# -----------------------------
# Schweiflinien generieren
# -----------------------------
streams = []

for i in range(NUM_STREAMS):
    s = np.linspace(0, 1, POINTS_PER_STREAM)

    # Start nahe am Kopf
    angle = np.random.uniform(0, 2 * np.pi)
    radius = np.random.uniform(0.1, 1.8)

    y0 = radius * np.cos(angle)
    z0 = radius * np.sin(angle)

    # Schweif läuft nach links in negative x-Richtung
    x = -TAIL_LENGTH * s

    # Wirbel/Schwingung
    swirl = 1.0 + 2.8 * s
    phase = np.random.uniform(0, 2 * np.pi)

    y = y0 + 0.9 * s * np.sin(5.5 * s + phase) + 0.18 * swirl * np.sin(14 * s + phase)
    z = z0 + 0.7 * s * np.cos(4.8 * s + phase) + 0.14 * swirl * np.cos(11 * s + phase)

    # Schweif breitet sich leicht aus
    y += np.random.normal(0, 0.15, POINTS_PER_STREAM) * s
    z += np.random.normal(0, 0.15, POINTS_PER_STREAM) * s

    streams.append((x, y, z, phase))


# -----------------------------
# Partikel erzeugen
# -----------------------------
particle_s = np.random.rand(NUM_PARTICLES)
particle_phase = np.random.uniform(0, 2 * np.pi, NUM_PARTICLES)
particle_offset_y = np.random.normal(0, 1.8, NUM_PARTICLES)
particle_offset_z = np.random.normal(0, 1.4, NUM_PARTICLES)


# -----------------------------
# Plot vorbereiten
# -----------------------------
fig = plt.figure(figsize=(13, 8))
ax = fig.add_subplot(111, projection="3d")

fig.patch.set_facecolor("black")
ax.set_facecolor("black")

ax.set_xlim(X_MIN, X_MAX)
ax.set_ylim(Y_MIN, Y_MAX)
ax.set_zlim(Z_MIN, Z_MAX)

ax.set_xlabel("x / Raumachse")
ax.set_ylabel("y / Raumachse")
ax.set_zlabel("z / Raumachse")

ax.set_title(
    "Zero-Lumi Plasma-Schweif mit P4-Zustandsmarker",
    color="white",
    pad=18
)

# Achsenfarben etwas heller
ax.tick_params(colors="white")
ax.xaxis.label.set_color("white")
ax.yaxis.label.set_color("white")
ax.zaxis.label.set_color("white")

# Gitternetz dunkler machen
ax.grid(True)

# -----------------------------
# Künstlerobjekte
# -----------------------------
stream_lines = []
for _ in streams:
    line, = ax.plot([], [], [], linewidth=0.8, alpha=0.65)
    stream_lines.append(line)

particles = ax.scatter([], [], [], s=6, alpha=0.85)

# Plasma-Kopf
theta = np.linspace(0, 2 * np.pi, 48)
phi = np.linspace(0, np.pi, 24)
TH, PH = np.meshgrid(theta, phi)

head_surface = [None]

# P4 Punkt
p4_point = ax.scatter([], [], [], s=90, marker="o")
p4_text = ax.text(
    0, 0, 0,
    "",
    color="white",
    fontsize=10
)

# Info-Text links unten
info_text = ax.text2D(
    0.03, 0.04,
    "",
    transform=ax.transAxes,
    color="white",
    fontsize=9
)


# -----------------------------
# Animation
# -----------------------------
def update(frame):
    global particles

    t = frame

    # Kamera langsam drehen
    ax.view_init(elev=18 + 5 * np.sin(frame * 0.015), azim=-68 + frame * 0.12)

    # Alte Kopfoberfläche entfernen
    if head_surface[0] is not None:
        head_surface[0].remove()

    # Plasma-Kopf leicht pulsierend
    pulse = frame * 0.08
    hx, hy, hz = plasma_head(TH, PH, pulse)

    # Kopf sitzt bei x = 0
    head_color_value = 0.5 + 0.5 * np.sin(frame * 0.04)

    head_surface[0] = ax.plot_surface(
        hx,
        hy,
        hz,
        rstride=1,
        cstride=1,
        alpha=0.22,
        linewidth=0,
        shade=True
    )

    # Schweiflinien animieren
    for idx, (x, y, z, phase) in enumerate(streams):
        wave = 0.25 * np.sin(0.4 * x + frame * 0.08 + phase)

        yy = y + wave
        zz = z + 0.20 * np.cos(0.4 * x + frame * 0.07 + phase)

        lam = state_lambda(x, yy, zz, frame)
        color_strength = normalize(lam)

        # Matplotlib-Linien können nur eine Farbe pro Linie:
        # daher nehmen wir mittleren lambda-Wert.
        c = plt.cm.plasma(np.mean(color_strength))

        stream_lines[idx].set_data(x, yy)
        stream_lines[idx].set_3d_properties(zz)
        stream_lines[idx].set_color(c)

    # Partikel bewegen sich entlang des Schweifs
    s = (particle_s + frame * 0.004) % 1.0

    px = -TAIL_LENGTH * s

    swirl = 1.0 + 2.8 * s
    py = particle_offset_y * s + 0.7 * s * np.sin(8 * s + particle_phase + frame * 0.045)
    pz = particle_offset_z * s + 0.6 * s * np.cos(7 * s + particle_phase + frame * 0.04)

    lam_p = state_lambda(px, py, pz, frame)
    colors = plt.cm.cool(normalize(lam_p))

    # Scatter erneuern
    particles.remove()
    particles = ax.scatter(
        px,
        py,
        pz,
        s=8 + 16 * normalize(lam_p),
        c=colors,
        alpha=0.75
    )

    # -----------------------------
    # P4-Zustandsmarker
    # -----------------------------
    # P4 bewegt sich nahe am Kopf und zeigt eine verborgene Zustandsachse lambda
    p4_x = -1.6 + 0.5 * np.sin(frame * 0.025)
    p4_y = 1.2 * np.cos(frame * 0.035)
    p4_z = 0.9 * np.sin(frame * 0.04)

    p4_lambda = state_lambda(p4_x, p4_y, p4_z, frame)

    p4_point._offsets3d = ([p4_x], [p4_y], [p4_z])
    p4_point.set_color([plt.cm.spring(normalize(np.array([p4_lambda, -1, 1]))[0])])

    p4_text.set_position((p4_x, p4_y))
    p4_text.set_3d_properties(p4_z + 0.6)
    p4_text.set_text(
        f"P4 = (x,y,z,λ)\n"
        f"x={p4_x: .2f}\n"
        f"y={p4_y: .2f}\n"
        f"z={p4_z: .2f}\n"
        f"λ={p4_lambda: .2f}"
    )

    info_text.set_text(
        "Modell:\n"
        "3D sichtbar: x,y,z\n"
        "4D/Zustand: λ\n"
        "λ kann ψ, ΔS, Energie, Phase oder Feldkopplung darstellen.\n"
        "Die sichtbare Struktur ist eine Projektion verborgener Zustandsachsen."
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


# ============================================================
# Optional speichern:
# Dafür brauchst du ffmpeg.
#
# Linux:
# sudo apt install ffmpeg
#
# Dann unten aktivieren:
#
# ani.save("zero_plasma_p4_visualizer.mp4", fps=30, dpi=160)
# ============================================================
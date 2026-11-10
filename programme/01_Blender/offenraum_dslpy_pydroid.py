"""
Offenraum DSL-PY Mobile / Pydroid
=================================

Pydroid-Version ohne Blender/bpy.
Sie zeigt als 2D-Animation:
- Hilbert-Bloch-Zustandsnetz
- Plasma-/Material-Querschnitt
- Interferenzfeld
- Zustandsbasierter Energiespeicher

Installation in Pydroid:
    pip install numpy matplotlib

Start:
    Script in Pydroid öffnen und Play drücken.

Optional GIF speichern:
    pip install pillow
    Unten save_gif = True setzen.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from math import sin, cos, pi

# ==========================================================
# Einstellungen
# ==========================================================

N = 360                 # Auflösung. Für schwache Geräte: 240 oder 300
EXTENT = 7.5            # Sichtbarer Bereich
FRAMES = 240            # Länge der Animation
INTERVAL = 45           # Millisekunden pro Frame
SAVE_GIF = False        # True = GIF nach Download speichern
GIF_PATH = "/sdcard/Download/offenraum_dslpy_pydroid.gif"

# Raster
x = np.linspace(-EXTENT, EXTENT, N)
y = np.linspace(-EXTENT, EXTENT, N)
X, Y = np.meshgrid(x, y)

# ==========================================================
# Mathe-Helfer
# ==========================================================

def normalize(a):
    a = a - np.min(a)
    return a / (np.max(a) + 1e-9)


def gaussian(x0, y0, sx, sy=None, Xgrid=None, Ygrid=None):
    if Xgrid is None:
        Xgrid = X
    if Ygrid is None:
        Ygrid = Y
    if sy is None:
        sy = sx
    return np.exp(-(((Xgrid - x0) ** 2) / (2 * sx ** 2) + ((Ygrid - y0) ** 2) / (2 * sy ** 2)))


def ring_field(radius, width, Xgrid=None, Ygrid=None):
    if Xgrid is None:
        Xgrid = X
    if Ygrid is None:
        Ygrid = Y
    r = np.sqrt(Xgrid ** 2 + Ygrid ** 2)
    return np.exp(-((r - radius) ** 2) / (2 * width ** 2))


def wave_source(x0, y0, k, t, decay=0.16):
    r = np.sqrt((X - x0) ** 2 + (Y - y0) ** 2)
    return np.cos(k * r - t) * np.exp(-decay * r)


def soft_line(x1, y1, x2, y2, width=0.055, samples=40):
    out = np.zeros_like(X)
    for s in np.linspace(0.0, 1.0, samples):
        px = (1 - s) * x1 + s * x2
        py = (1 - s) * y1 + s * y2
        out += gaussian(px, py, width)
    return out / samples

# ==========================================================
# DSL-artige Zeichenmaschine
# ==========================================================

class PydroidDSL:
    def __init__(self):
        self.layers = []

    def add(self, name, field, weight=1.0):
        self.layers.append((name, field, weight))

    def render(self):
        field = np.zeros_like(X)
        for _name, layer, weight in self.layers:
            field += weight * layer
        return normalize(field)

# ==========================================================
# Bausteine
# ==========================================================

def cross_section_field(t, cx=-5.0, cy=-2.2, scale=0.65):
    """Plasma-Kern + Materialringe + Wolframspitzen."""
    Xs = (X - cx) / scale
    Ys = (Y - cy) / scale

    core = 2.3 * gaussian(0, 0, 0.55, Xgrid=Xs, Ygrid=Ys)
    carbon = 0.65 * ring_field(1.15, 0.08, Xs, Ys)
    copper = 0.95 * ring_field(1.55, 0.11, Xs, Ys)
    tungsten = 0.85 * ring_field(1.95, 0.08, Xs, Ys)

    spikes = np.zeros_like(X)
    for i in range(32):
        a = i * 2 * pi / 32
        rr = 2.20 + 0.06 * sin(t + i)
        x0 = rr * cos(a)
        y0 = rr * sin(a)
        spikes += 0.20 * gaussian(x0, y0, 0.07, 0.15, Xs, Ys)

    pulse = 1.0 + 0.14 * sin(2.6 * t)
    return pulse * (core + carbon + copper + tungsten + spikes)


def hilbert_bloch_field(t):
    """Globale Hülle, Zustandsknoten und Kopplungen."""
    R = np.sqrt(X ** 2 + Y ** 2)
    TH = np.arctan2(Y, X)

    shell = 0.65 * np.exp(-((R - (4.9 + 0.10 * sin(0.7 * t))) ** 2) / (2 * 0.06 ** 2))
    center = 2.2 * gaussian(0, 0, 0.35)

    # Achsen im Zustandsraum
    horizontal = 0.50 * np.exp(-(Y ** 2) / (2 * 0.035 ** 2)) * np.exp(-(X ** 2) / 22)
    vertical = 0.50 * np.exp(-(X ** 2) / (2 * 0.035 ** 2)) * np.exp(-(Y ** 2) / 22)

    # Zustandsknoten
    count = 12
    nodes = np.zeros_like(X)
    links = np.zeros_like(X)
    positions = []

    for i in range(count):
        a = 2 * pi * i / count + 0.18 * sin(0.7 * t)
        rad = 3.75 + 0.22 * sin(t + i)
        px = rad * cos(a)
        py = rad * sin(a)
        positions.append((px, py))
        nodes += 1.18 * gaussian(px, py, 0.16)
        nodes += 0.35 * ring_field(0.33, 0.025, (X - px), (Y - py))

    # Links vom Zentrum zu den Zustandsknoten
    for px, py in positions:
        links += 1.3 * soft_line(px, py, 0, 0, width=0.045, samples=28)

    # Kopplungsbögen als Linien mit kleiner Wölbung
    for i in range(count):
        x1, y1 = positions[i]
        x2, y2 = positions[(i + 4) % count]
        for s in np.linspace(0, 1, 36):
            bx = (1 - s) * x1 + s * x2
            by = (1 - s) * y1 + s * y2
            curve = 0.32 * sin(pi * s) * sin(t + i)
            links += 0.030 * gaussian(bx, by + curve, 0.05)

    # Orbitale / Spirographisches Feld
    orbit = np.sin(5 * TH + 1.2 * sin(t)) * np.cos(2.3 * R - 1.4 * t) * np.exp(-0.045 * R ** 2)
    orbit = 0.55 * np.abs(orbit)

    return shell + center + horizontal + vertical + nodes + links + orbit


def interference_field(t):
    """Zwei Quellen -> Interferenzmuster."""
    w1 = wave_source(-1.0, 0.0, 8.2, 2.2 * t)
    w2 = wave_source(1.0, 0.0, 8.2, 2.2 * t)
    return ((w1 + w2) ** 2) * np.exp(-0.04 * (X ** 2 + Y ** 2))


def energy_storage_field(t):
    """S0 + E_in -> S* -> E_out, als visuelle Speicher-/Auskopplungsschicht."""
    charge_ring = 1.05 * ring_field(2.85 + 0.16 * sin(t), 0.14)
    inner = 1.45 * gaussian(0, 0, 0.72) * (1.0 + 0.25 * sin(3 * t))
    output_beam = np.exp(-(Y ** 2) / (2 * 0.12 ** 2)) * np.exp(-((X - 2.3) ** 2) / 8.0)
    input_beam = np.exp(-(Y ** 2) / (2 * 0.14 ** 2)) * np.exp(-((X + 2.6) ** 2) / 8.5)
    return charge_ring + inner + 0.45 * output_beam + 0.30 * input_beam


def z_echo_field(current, previous):
    """Z-Echo: Veränderung zwischen zwei Mustern."""
    if previous is None:
        return np.zeros_like(current)
    return normalize(np.abs(current - previous))


def build_frame(t, previous_base=None):
    dsl = PydroidDSL()
    base = (
        1.00 * hilbert_bloch_field(t)
        + 0.40 * interference_field(t)
        + 0.35 * energy_storage_field(t)
        + 0.90 * cross_section_field(t)
    )
    echo = z_echo_field(base, previous_base)
    dsl.add("base", base, 1.0)
    dsl.add("z_echo", echo, 0.18)
    return dsl.render(), base

# ==========================================================
# Animation
# ==========================================================

plt.style.use("dark_background")
fig, ax = plt.subplots(figsize=(7.2, 7.2))
fig.patch.set_facecolor("black")
ax.set_facecolor("black")

img = ax.imshow(
    np.zeros_like(X),
    extent=[-EXTENT, EXTENT, -EXTENT, EXTENT],
    origin="lower",
    cmap="turbo",
    interpolation="bilinear",
    vmin=0,
    vmax=1,
)

ax.set_xlim(-EXTENT, EXTENT)
ax.set_ylim(-EXTENT, EXTENT)
ax.set_aspect("equal")
ax.axis("off")

title = ax.text(0, 7.05, "Offenraum DSL-PY Mobile", ha="center", va="center", fontsize=14, color="#bfe8ff")
formula = ax.text(0, -7.10, "S_in -> G -> Z -> M    |    S0 + E_in -> S* -> E_out    |    Z_echo = ΔM", ha="center", va="center", fontsize=8.5, color="#cfefff")
phase_text = ax.text(-7.20, -6.62, "", ha="left", va="center", fontsize=8.5, color="#ffffff")

previous = {"base": None}


def phase_name(u):
    if u < 0.25:
        return "Phase 1: Kopplung + Interferenz"
    if u < 0.50:
        return "Phase 2: Hilbert-Bloch Zustandsnetz"
    if u < 0.75:
        return "Phase 3: Material-/Plasma-Querschnitt"
    return "Phase 4: Zustandsbasierter Energiespeicher + Z-Echo"


def update(frame):
    t = frame * 0.075
    u = frame / max(1, FRAMES - 1)
    m, base = build_frame(t, previous["base"])
    previous["base"] = base

    img.set_array(m ** 0.85)
    phase_text.set_text(phase_name(u))
    return img, title, formula, phase_text

ani = FuncAnimation(fig, update, frames=FRAMES, interval=INTERVAL, blit=False)

if SAVE_GIF:
    ani.save(GIF_PATH, writer="pillow", fps=20)
    print("GIF gespeichert:", GIF_PATH)
else:
    plt.show()

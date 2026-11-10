import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ============================================================
# TIRXY Cross-Section + Brane View Simulation
# ------------------------------------------------------------
# Zero-Lumi Modell:
#
# TIRXY =
# T = Trägerraum / Topologie
# I = Information / Zustand
# R = Regeln / Relaxation
# X = Kreuzung / Kopplung / Kollision
# Y = sichtbare Ergebnisachse / Emergenz
#
# Idee:
# - Bulk erzeugt unsichtbare Schwingungen
# - Brane ist die sichtbare Schnittfläche
# - String-artige Impulse laufen/fallen ins Feld
# - Defekte/Lücken speichern "Gedächtnis" des Systems
# - Relaxation glättet extreme Zustände
# ============================================================


# -----------------------------
# Grundeinstellungen
# -----------------------------
np.random.seed(7)

GRID_X = 140
GRID_Y = 90
FRAMES = 500

# Stärke der Effekte
BULK_WAVE_STRENGTH = 0.55
STRING_STRENGTH = 1.45
DEFECT_STRENGTH = -1.2
RELAXATION = 0.965
DIFFUSION = 0.045

# Anzahl sichtbarer String-/Formimpulse
NUM_STRINGS = 9

# Anzahl Defekte / Lücken
NUM_DEFECTS = 16


# -----------------------------
# Koordinatenfeld
# -----------------------------
x = np.linspace(-4.0, 4.0, GRID_X)
y = np.linspace(-2.6, 2.6, GRID_Y)
X, Y = np.meshgrid(x, y)

field = np.zeros((GRID_Y, GRID_X))


# -----------------------------
# Defekte/Lücken erzeugen
# -----------------------------
defects = []

for _ in range(NUM_DEFECTS):
    dx = np.random.uniform(-3.5, 3.5)
    dy = np.random.uniform(-2.2, 2.2)
    radius = np.random.uniform(0.10, 0.28)
    depth = np.random.uniform(0.45, 1.0)
    defects.append((dx, dy, radius, depth))


# -----------------------------
# String-Impulse erzeugen
# -----------------------------
strings = []

for i in range(NUM_STRINGS):
    sx = np.random.uniform(-3.7, 3.7)
    sy = np.random.uniform(-2.5, 2.5)
    speed = np.random.uniform(0.012, 0.035)
    phase = np.random.uniform(0, 2 * np.pi)
    width = np.random.uniform(0.16, 0.34)
    strength = np.random.uniform(0.7, 1.3)
    strings.append({
        "x": sx,
        "y": sy,
        "speed": speed,
        "phase": phase,
        "width": width,
        "strength": strength
    })


# -----------------------------
# Hilfsfunktionen
# -----------------------------
def gaussian_2d(cx, cy, width):
    return np.exp(-((X - cx) ** 2 + (Y - cy) ** 2) / (2 * width ** 2))


def laplacian(Z):
    """
    Einfache 2D-Diffusion.
    Das ist keine echte Quantenfeldrechnung,
    sondern ein stabiles Toy-Modell für Feldrelaxation.
    """
    return (
        np.roll(Z, 1, axis=0)
        + np.roll(Z, -1, axis=0)
        + np.roll(Z, 1, axis=1)
        + np.roll(Z, -1, axis=1)
        - 4 * Z
    )


def normalize(Z):
    Z = np.array(Z, dtype=float)
    return Z / (np.max(np.abs(Z)) + 1e-9)


def compute_bulk_wave(t):
    """
    Unsichtbare Hintergrundschwingung.
    Im TIRXY-Bild: Bulk -> Brane-Projektion.
    """
    wave1 = np.sin(2.2 * X + 0.055 * t)
    wave2 = np.cos(2.8 * Y - 0.040 * t)
    wave3 = np.sin(1.3 * X + 1.6 * Y + 0.030 * t)
    return BULK_WAVE_STRENGTH * (wave1 + wave2 + wave3) / 3.0


def compute_string_layer(t):
    """
    Bewegte, string-artige Energieformen.
    Sie sind nicht "echte Strings",
    sondern sichtbare Muster für Form + Rotation + Kopplung.
    """
    layer = np.zeros_like(field)

    for s in strings:
        # Bewegung mit leichter Kreis-/Wellenbahn
        cx = s["x"] + 0.55 * np.sin(0.025 * t + s["phase"])
        cy = s["y"] + 0.35 * np.cos(0.018 * t + s["phase"])

        # langsames Driften nach unten und Zurückspringen
        cy = ((cy - s["speed"] * t + 2.6) % 5.2) - 2.6

        core = gaussian_2d(cx, cy, s["width"])

        # kleine "String-Schwanz"-Struktur
        tail = gaussian_2d(
            cx - 0.35 * np.sin(0.04 * t + s["phase"]),
            cy + 0.42,
            s["width"] * 1.65
        )

        layer += s["strength"] * core
        layer += 0.38 * s["strength"] * tail

    return STRING_STRENGTH * layer


def compute_defect_layer(t):
    """
    Defekte/Lücken.
    Im Tetris-Bild: leere Räume.
    Im Feldbild: Symmetriebruch, Störung, ΔS.
    """
    layer = np.zeros_like(field)

    for dx, dy, radius, depth in defects:
        pulse = 0.75 + 0.25 * np.sin(0.025 * t + dx * 2.0)
        layer += DEFECT_STRENGTH * depth * pulse * gaussian_2d(dx, dy, radius)

    return layer


def line_relaxation_layer(Z):
    """
    Tetris-artige 'Linienlogik':
    Wenn in einer horizontalen Zone sehr viel Ordnung/Energie liegt,
    wird sie leicht geglättet.
    Das ist unsere symbolische Relaxation.
    """
    row_energy = np.mean(np.abs(Z), axis=1)
    threshold = np.percentile(row_energy, 88)

    relaxed = Z.copy()

    for row_index, energy in enumerate(row_energy):
        if energy > threshold:
            relaxed[row_index, :] *= 0.72

            if row_index > 0:
                relaxed[row_index - 1, :] += 0.08 * Z[row_index, :]

            if row_index < Z.shape[0] - 1:
                relaxed[row_index + 1, :] += 0.08 * Z[row_index, :]

    return relaxed


# -----------------------------
# Plot vorbereiten
# -----------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6))

fig.suptitle(
    "TIRXY Simulation: Querschnitt + Brane-Ansicht",
    fontsize=15
)

# Linke Ansicht: Querschnitt
img1 = ax1.imshow(
    field,
    extent=[x.min(), x.max(), y.min(), y.max()],
    origin="lower",
    cmap="inferno",
    vmin=-1,
    vmax=1,
    interpolation="bilinear"
)

ax1.set_title("Querschnitt: Bulk → Brane → Feld")
ax1.set_xlabel("X / Brane-Achse")
ax1.set_ylabel("Y / Tiefe-Zustand")

# Rechte Ansicht: Draufsicht / Brane-Projektion
img2 = ax2.imshow(
    field,
    extent=[x.min(), x.max(), y.min(), y.max()],
    origin="lower",
    cmap="viridis",
    vmin=-1,
    vmax=1,
    interpolation="bilinear"
)

ax2.set_title("Ansicht: sichtbare Feldstruktur")
ax2.set_xlabel("X / sichtbares Raster")
ax2.set_ylabel("Y / sichtbares Raster")

# Farbleisten
cbar1 = plt.colorbar(img1, ax=ax1, fraction=0.046, pad=0.04)
cbar1.set_label("Zustandsenergie / ΔS")

cbar2 = plt.colorbar(img2, ax=ax2, fraction=0.046, pad=0.04)
cbar2.set_label("sichtbare Projektion")

# Textbox
info_text = fig.text(
    0.5,
    0.02,
    "",
    ha="center",
    fontsize=10
)


# -----------------------------
# Animation
# -----------------------------
def update(frame):
    global field

    bulk = compute_bulk_wave(frame)
    strings_layer = compute_string_layer(frame)
    defect_layer = compute_defect_layer(frame)

    # Gesamtantrieb
    drive = bulk + strings_layer + defect_layer

    # Feld-Update:
    # alter Zustand bleibt teilweise erhalten,
    # neue Projektion kommt hinzu,
    # Diffusion verteilt Energie,
    # Relaxation beruhigt das System.
    field = RELAXATION * field
    field += 0.080 * drive
    field += DIFFUSION * laplacian(field)

    # symbolische Linien-/Ordnungsrelaxation
    field = line_relaxation_layer(field)

    # Normalisierung für stabile Darstellung
    visible = normalize(field)

    # Querschnitt stärker kontrastiert
    cross_section = np.tanh(1.75 * visible)

    # Draufsicht weicher
    brane_view = np.tanh(1.15 * (visible + 0.25 * bulk))

    img1.set_data(cross_section)
    img2.set_data(brane_view)

    # Diagnosewerte
    mean_energy = np.mean(np.abs(field))
    defect_value = np.mean(np.abs(defect_layer))
    order_value = 1.0 / (1.0 + mean_energy + defect_value)

    info_text.set_text(
        f"Frame {frame:03d}   |   "
        f"mittlere Feldenergie: {mean_energy:.3f}   |   "
        f"ΔS/Defektstärke: {defect_value:.3f}   |   "
        f"Ordnungsschätzer: {order_value:.3f}"
    )

    return img1, img2, info_text


ani = FuncAnimation(
    fig,
    update,
    frames=FRAMES,
    interval=35,
    blit=False
)

plt.tight_layout(rect=[0, 0.05, 1, 0.95])
plt.show()